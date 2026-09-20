"""Sentiment analysis: HF transformer primary, classical ML fallback.

Primary model (documented): distilbert-base-uncased-finetuned-sst-2-english
(SST-2: POSITIVE/NEGATIVE) mapped to positive/negative/neutral via thresholds.
Fallback: TF-IDF + LogisticRegression trained on the synthetic tickets, saved
as models/sentiment.joblib, so the app works fully offline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

HF_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
LABELS = ["negative", "neutral", "positive"]

_pipe = None  # lazy HF pipeline cache


def _hf_pipe(model_name: str = HF_MODEL):
    global _pipe
    if _pipe is None:
        from transformers import pipeline  # lazy import (heavy dep)

        _pipe = pipeline("sentiment-analysis", model=model_name)
    return _pipe


def hf_predict(text: str, model_name: str = HF_MODEL) -> Tuple[str, float]:
    """Predict with the HF model. Raises if model unavailable (offline)."""
    pipe = _hf_pipe(model_name)
    r = pipe(text[:512])[0]
    raw, score = str(r["label"]).upper(), float(r["score"])
    if raw == "POSITIVE":
        # Low-confidence positives near 0.5 become neutral.
        return ("positive", score) if score >= 0.65 else ("neutral", score)
    return ("negative", score) if score >= 0.65 else ("neutral", score)


def train_fallback(texts: list[str], labels: list[str], out_path: str | Path) -> Pipeline:
    """Train TF-IDF+LogReg fallback and persist it."""
    m = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=6000, ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    m.fit(texts, labels)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(m, out_path)
    return m


def fallback_predict(model: Pipeline, text: str) -> Tuple[str, float]:
    """Predict with fallback model; confidence = max class probability."""
    import numpy as np

    proba = model.predict_proba([text])[0]
    idx = int(np.argmax(proba))
    return str(model.classes_[idx]), float(proba[idx])


class SentimentAnalyzer:
    """Unified interface: tries HF, falls back to local joblib model."""

    def __init__(self, fallback_path: str | Path | None = None, hf_model: str = HF_MODEL):
        """Load fallback model eagerly if present."""
        self.hf_model = hf_model
        self.fallback = None
        if fallback_path and Path(fallback_path).exists():
            self.fallback = joblib.load(fallback_path)

    def predict(self, text: str) -> Dict[str, object]:
        """Return {sentiment_label, sentiment_score, provider}.

        Order: local fallback model first (fast, offline, deterministic);
        HF transformer only when no fallback exists. This keeps the API
        responsive without large downloads.
        """
        if self.fallback is not None:
            try:
                label, score = fallback_predict(self.fallback, text)
                return {"sentiment_label": label, "sentiment_score": round(score, 4), "provider": "fallback-ml"}
            except Exception:
                pass
        try:
            label, score = hf_predict(text, self.hf_model)
            return {"sentiment_label": label, "sentiment_score": round(score, 4), "provider": "huggingface"}
        except Exception:
            label, score = heuristic(text)
            return {"sentiment_label": label, "sentiment_score": round(score, 4), "provider": "heuristic"}


NEG_WORDS = {"delay", "delayed", "cancelled", "angry", "furious", "unacceptable", "terrible", "awful",
             "worst", "complaint", "dispute", "breach", "failed", "failure", "broken", "missing",
             "poor", "bad", "escalate", "urgent", "aog", "grounded"}
POS_WORDS = {"thank", "thanks", "great", "excellent", "appreciate", "satisfied", "good", "prompt",
             "quick", "helpful", "resolved", "pleased"}


def heuristic(text: str) -> Tuple[str, float]:
    """Tiny lexical sentiment used only when no model is available."""
    t = text.lower()
    neg = sum(1 for w in NEG_WORDS if w in t)
    pos = sum(1 for w in POS_WORDS if w in t)
    if neg > pos:
        return "negative", min(0.95, 0.6 + 0.1 * (neg - pos))
    if pos > neg:
        return "positive", min(0.95, 0.6 + 0.1 * (pos - neg))
    return "neutral", 0.55

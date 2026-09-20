"""Unified case-analysis pipeline: classify -> sentiment -> severity -> escalate -> RAG."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from src.data.preprocessing import normalize_text
from src.models import escalation as esc_mod
from src.models import sentiment as sent_mod
from src.models import severity as sev_mod
from src.models import explain as explain_mod
from src.models import classifier as clf_mod
from src.utils.config import get_settings, model_dir

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def _load_all():
    s = get_settings()
    md = model_dir()
    classifier = clf_mod.load_model(md / "classifier.joblib")
    esc_bundle = esc_mod.load_bundle(md / "escalation.joblib")
    analyzer = sent_mod.SentimentAnalyzer(md / "sentiment.joblib", hf_model=s.hf_sentiment_model)
    try:
        from src.rag.retriever import Retriever

        retriever = Retriever()
    except Exception:
        retriever = None
    return classifier, esc_bundle, analyzer, retriever


def analyze_case(message: str, delay_hours: float = 0.0, previous_complaints: int = 0,
                 customer_priority: str = "standard", aircraft_type: str = "A320neo") -> dict:
    """Run the full pipeline and return a JSON-serialisable dict."""
    classifier, esc_bundle, analyzer, retriever = _load_all()

    cat = clf_mod.predict(classifier, [message])[0]
    sent = analyzer.predict(message)
    severity, _ = sev_mod.estimate_severity(message, delay_hours, previous_complaints, cat["category"])

    row = pd.DataFrame([{
        "delay_hours": delay_hours, "previous_complaints": previous_complaints,
        "severity": severity, "customer_priority": customer_priority,
        "sentiment": sent["sentiment_label"], "category": cat["category"],
        "aircraft_type": aircraft_type, "clean_text": normalize_text(message),
        "severity_code": {"low": 0, "medium": 1, "high": 2}.get(severity, 1),
        "priority_code": {"standard": 0, "silver": 1, "gold": 2, "platinum": 3}.get(customer_priority, 0),
        "sentiment_code": {"negative": 0, "neutral": 1, "positive": 2}.get(sent["sentiment_label"], 1),
        "is_negative": 1 if sent["sentiment_label"] == "negative" else 0,
        "is_high_severity": 1 if severity == "high" else 0,
    }])
    import numpy as np

    row["log_delay"] = np.log1p(max(0.0, delay_hours))
    row["msg_len"] = len(row.loc[0, "clean_text"])
    row["msg_words"] = len(row.loc[0, "clean_text"].split())
    row["complaint_x_delay"] = previous_complaints * float(row.loc[0, "log_delay"])

    esc_p = esc_mod.predict_proba(esc_bundle, row)[0]
    risk = sev_mod.risk_level(esc_p, severity)
    factors = explain_mod.explain(esc_bundle, row)

    retrieved: list[dict] = []
    grounded = False
    if retriever is not None:
        try:
            gate = retriever.search_gated(message, top_k=4)
            retrieved, grounded = gate["hits"], gate["grounded"]
        except Exception:
            retrieved, grounded = [], False
    from src.rag import generator as gen

    # Relevance gate: ungrounded queries abstain WITHOUT calling the LLM,
    # so out-of-domain questions never get aviation answers. ML outputs
    # (category/sentiment/severity/escalation) are unaffected.
    gen_out = gen.generate(message, retrieved) if grounded else gen.abstain_response()

    return {
        "category": cat["category"], "category_confidence": round(float(cat["confidence"]), 4),
        "sentiment": sent["sentiment_label"], "sentiment_score": float(sent["sentiment_score"]),
        "severity": severity, "escalation_probability": round(float(esc_p), 4),
        "risk_level": risk,
        "recommended_action": sev_mod.recommended_action(cat["category"], risk, severity),
        "generated_response": gen_out["answer"], "sources": gen_out["sources"],
        "important_factors": factors,
    }

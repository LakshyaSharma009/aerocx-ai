"""Embedding backend: SentenceTransformers primary, TF-IDF fallback (offline-safe)."""

from __future__ import annotations

from pathlib import Path
from typing import List

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class EmbeddingModel:
    """Unified embedding interface with .encode() and persistence."""

    backend: str = "tfidf"

    def encode(self, texts: List[str]) -> np.ndarray:
        """Return L2-normalised embedding matrix."""
        raise NotImplementedError

    def save(self, path: str | Path) -> None:
        """Persist backend state."""
        raise NotImplementedError


class STEmbedding(EmbeddingModel):
    """Sentence-Transformers backend."""

    backend = "sentence-transformers"

    def __init__(self, model_name: str):
        """Load transformer model (downloads weights on first use)."""
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode + L2-normalise."""
        vecs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return normalize(np.asarray(vecs, dtype=float))

    def save(self, path: str | Path) -> None:
        """Persist model name (weights stay in HF cache)."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"backend": self.backend, "model_name": self.model_name}, path)


class TfidfEmbedding(EmbeddingModel):
    """TF-IDF fallback backend (no downloads, fully local).

    English stop words are removed so that generic words ("the", "who", "and")
    cannot create spurious cross-domain similarity between out-of-domain
    queries and aviation documents (see docs/architecture.md, RAG gate).
    """

    backend = "tfidf"

    def __init__(self, max_features: int = 2048):
        """Create unfitted vectoriser."""
        self.vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2),
                                          sublinear_tf=True, stop_words="english")

    def fit(self, texts: List[str]) -> "TfidfEmbedding":
        """Fit vectoriser on corpus."""
        self.vectorizer.fit(texts)
        return self

    def encode(self, texts: List[str]) -> np.ndarray:
        """Transform + L2-normalise."""
        return normalize(self.vectorizer.transform(texts).toarray())

    def save(self, path: str | Path) -> None:
        """Persist fitted vectoriser."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"backend": self.backend, "vectorizer": self.vectorizer}, path)


def load_embedding(path: str | Path, model_name: str = "") -> EmbeddingModel:
    """Load persisted embedding backend."""
    state = joblib.load(path)
    if state.get("backend") == "sentence-transformers":
        return STEmbedding(state.get("model_name") or model_name)
    emb = TfidfEmbedding()
    emb.vectorizer = state["vectorizer"]
    return emb


def get_embedding(model_name: str, texts: List[str] | None = None) -> EmbeddingModel:
    """Try SentenceTransformers; fall back to TF-IDF on any failure (offline)."""
    try:
        emb = STEmbedding(model_name)
        if texts is not None:  # warm-up to surface download errors early
            emb.encode(texts[:2])
        return emb
    except Exception:
        fb = TfidfEmbedding()
        if texts is not None:
            fb.fit(texts)
        return fb

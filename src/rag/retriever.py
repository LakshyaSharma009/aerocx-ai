"""Retriever: cosine similarity over the local chunk index, with relevance gating.

pgvector path: src/db/database.py mirrors these chunks into PostgreSQL+pgvector;
this local retriever keeps dev/test offline-friendly with identical ranking math.

Relevance gate: `search_gated()` drops hits below `RAG_MIN_SIMILARITY` so that
out-of-domain queries (e.g. history questions) abstain instead of answering
from unrelated aviation documents. Threshold comes from settings (env
RAG_MIN_SIMILARITY), calibrated on the TF-IDF backend — see docs/architecture.md.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.rag.embeddings import load_embedding
from src.utils.config import get_settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Retriever:
    """Top-k similarity search over ingested chunks."""

    def __init__(self, index_dir: str | Path | None = None):
        """Load chunks, vectors, embedding backend."""
        settings = get_settings()
        idx = Path(index_dir) if index_dir else PROJECT_ROOT / "models" / "rag_index"
        chunks_pq, vecs_np, emb_jl = idx / "chunks.parquet", idx / "vectors.npy", idx / "embeddings.joblib"
        if not (chunks_pq.exists() and vecs_np.exists()):
            raise FileNotFoundError(
                f"RAG index not found in {idx}. Run: python -m src.rag.ingest")
        self.chunks = pd.read_parquet(chunks_pq)
        self.vectors = np.load(vecs_np)
        self.embedding = load_embedding(emb_jl, settings.embedding_model) if emb_jl.exists() else None

    def _ranked(self, query: str) -> list[dict]:
        """All chunks scored, best chunk per document only (dedupes overlap fragments)."""
        if self.embedding is None:
            raise RuntimeError("Embedding backend missing from index.")
        q = self.embedding.encode([query])[0]
        scores = self.vectors @ q  # both L2-normalised => cosine
        best: dict[str, dict] = {}
        for i in range(len(self.chunks)):
            doc = str(self.chunks.iloc[i]["doc_name"])
            s = float(scores[i])
            if doc not in best or s > best[doc]["score"]:
                best[doc] = {"doc_name": doc,
                             "chunk_id": str(self.chunks.iloc[i]["chunk_id"]),
                             "text": str(self.chunks.iloc[i]["text"]),
                             "score": s}
        return sorted(best.values(), key=lambda h: h["score"], reverse=True)

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        """Return top-k {doc_name, chunk_id, text, score} (one hit per document)."""
        return self._ranked(query)[: max(1, top_k)]

    def search_gated(self, query: str, top_k: int = 4,
                     min_score: float | None = None) -> dict:
        """Gated retrieval: keep hits with score >= threshold.

        Returns {"hits", "grounded", "top_score", "threshold"}. `grounded` is
        False when no chunk clears the threshold — callers must then abstain
        WITHOUT invoking the LLM generator.
        """
        threshold = get_settings().rag_min_similarity if min_score is None else float(min_score)
        ranked = self._ranked(query)
        top_score = ranked[0]["score"] if ranked else 0.0
        hits = [h for h in ranked[: max(1, top_k)] if h["score"] >= threshold]
        return {"hits": hits, "grounded": bool(hits),
                "top_score": float(top_score), "threshold": float(threshold)}

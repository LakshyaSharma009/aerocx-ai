"""Ingest: markdown docs -> chunks -> embeddings -> local index (+ pgvector-ready rows)."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.rag.embeddings import get_embedding
from src.utils.config import get_settings
from src.utils.logging import get_logger

log = get_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def chunk_text(text: str, doc_name: str, chunk_size: int = 600, overlap: int = 120) -> list[dict]:
    """Character-window chunking with overlap; keeps doc provenance."""
    text = " ".join(text.split())
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append({"doc_name": doc_name, "chunk_id": f"{doc_name}::chunk-{len(chunks)}",
                       "text": text[start:end]})
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest(kb_dir: str | Path | None = None, out_dir: str | Path | None = None) -> dict:
    """Build chunk index from data/kb/*.md. Returns stats."""
    settings = get_settings()
    kb = Path(kb_dir) if kb_dir else PROJECT_ROOT / "data" / "kb"
    out = Path(out_dir) if out_dir else PROJECT_ROOT / "models" / "rag_index"
    out.mkdir(parents=True, exist_ok=True)

    docs = sorted(kb.glob("*.md"))
    if not docs:
        raise FileNotFoundError(f"No markdown docs in {kb}")
    all_chunks: list[dict] = []
    for d in docs:
        all_chunks.extend(chunk_text(d.read_text(encoding="utf-8"), d.name))
    texts = [c["text"] for c in all_chunks]

    emb = get_embedding(settings.embedding_model, texts)
    vecs = emb.encode(texts)
    emb.save(out / "embeddings.joblib")
    joblib.dump([{"backend": emb.backend}], out / "backend.joblib")
    np.save(out / "vectors.npy", np.asarray(vecs, dtype=np.float32))
    pd.DataFrame(all_chunks).to_parquet(out / "chunks.parquet", index=False)
    log.info("Ingested %d chunks from %d docs (backend=%s)", len(all_chunks), len(docs), emb.backend)
    return {"n_docs": len(docs), "n_chunks": len(all_chunks), "backend": emb.backend,
            "index_dir": str(out)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-dir", default=None)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()
    print(ingest(args.kb_dir, args.out_dir))

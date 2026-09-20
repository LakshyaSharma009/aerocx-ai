"""FastAPI backend for AeroCX AI."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api import analysis as pipeline
from src.api import schemas as S
from src.data.preprocessing import normalize_text
from src.models import escalation as esc_mod
import pandas as pd
from src.utils.config import model_dir
from src.utils.logging import get_logger

log = get_logger(__name__)
app = FastAPI(title="AeroCX AI", version="1.0.0",
              description="Aviation Customer Experience Intelligence Platform (synthetic-data demo).")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _classifier():
    return pipeline._load_all()[0]


def _esc_bundle():
    return pipeline._load_all()[1]


def _analyzer():
    return pipeline._load_all()[2]


def _retriever():
    return pipeline._load_all()[3]


@app.get("/health", response_model=S.HealthResponse)
def health() -> S.HealthResponse:
    """Liveness + artefact presence."""
    md = model_dir()
    loaded = {n: (md / n).exists() for n in ["classifier.joblib", "sentiment.joblib", "escalation.joblib"]}
    rag_ready = (md / "rag_index" / "chunks.parquet").exists()
    return S.HealthResponse(status="ok", models_loaded=loaded, rag_ready=rag_ready)


@app.post("/predict/category", response_model=S.CategoryResponse)
def predict_category(req: S.CategoryRequest) -> S.CategoryResponse:
    """Classify the customer issue."""
    try:
        from src.models import classifier as clf_mod

        out = clf_mod.predict(_classifier(), [req.message])[0]
        return S.CategoryResponse(category=out["category"], confidence=float(out["confidence"]))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not trained: {e}")
    except Exception as e:  # pragma: no cover
        log.exception("category failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/sentiment", response_model=S.SentimentResponse)
def predict_sentiment(req: S.SentimentRequest) -> S.SentimentResponse:
    """Sentiment label + score."""
    try:
        r = _analyzer().predict(req.message)
        return S.SentimentResponse(sentiment_label=str(r["sentiment_label"]),
                                   sentiment_score=float(r["sentiment_score"]),
                                   provider=str(r.get("provider", "unknown")))
    except Exception as e:  # pragma: no cover
        log.exception("sentiment failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/escalation", response_model=S.EscalationResponse)
def predict_escalation(req: S.EscalationRequest) -> S.EscalationResponse:
    """Escalation probability from structured features."""
    try:
        import numpy as np

        from src.models import explain as explain_mod
        from src.models import severity as sev_mod

        bundle = _esc_bundle()
        row = pd.DataFrame([{
            "delay_hours": req.delay_hours, "previous_complaints": req.previous_complaints,
            "severity": req.severity, "customer_priority": req.customer_priority,
            "sentiment": req.sentiment, "category": req.category,
            "aircraft_type": req.aircraft_type, "clean_text": normalize_text(req.message),
            "severity_code": {"low": 0, "medium": 1, "high": 2}.get(req.severity, 1),
            "priority_code": {"standard": 0, "silver": 1, "gold": 2, "platinum": 3}.get(req.customer_priority, 0),
            "sentiment_code": {"negative": 0, "neutral": 1, "positive": 2}.get(req.sentiment, 1),
            "is_negative": 1 if req.sentiment == "negative" else 0,
            "is_high_severity": 1 if req.severity == "high" else 0,
            "log_delay": float(np.log1p(max(0.0, req.delay_hours))),
            "msg_len": len(req.message), "msg_words": len(req.message.split()),
            "complaint_x_delay": req.previous_complaints * float(np.log1p(max(0.0, req.delay_hours))),
        }])
        p = esc_mod.predict_proba(bundle, row)[0]
        return S.EscalationResponse(escalation_probability=round(float(p), 4),
                                    risk_level=sev_mod.risk_level(p, req.severity),
                                    important_factors=explain_mod.explain(bundle, row))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not trained: {e}")
    except Exception as e:  # pragma: no cover
        log.exception("escalation failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=S.AnalyzeResponse)
def analyze(req: S.AnalyzeRequest) -> S.AnalyzeResponse:
    """Unified case analysis (classification + sentiment + severity + escalation + RAG)."""
    try:
        return S.AnalyzeResponse(**pipeline.analyze_case(
            req.message, req.delay_hours, req.previous_complaints,
            req.customer_priority, req.aircraft_type))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not trained: {e}")
    except Exception as e:  # pragma: no cover
        log.exception("analyze failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/query", response_model=S.RagQueryResponse)
def rag_query(req: S.RagQueryRequest) -> S.RagQueryResponse:
    """Grounded knowledge-base Q&A."""
    try:
        from src.rag import generator as gen

        ret = _retriever()
        if ret is None:
            raise HTTPException(status_code=503, detail="RAG index not built. Run: python -m src.rag.ingest")
        gate = ret.search_gated(req.query, top_k=req.top_k)
        if not gate["grounded"]:
            # Below relevance threshold: abstain WITHOUT calling the LLM.
            out = gen.abstain_response()
            return S.RagQueryResponse(answer=out["answer"], sources=out["sources"],
                                      provider=out["provider"], retrieved=[])
        hits = gate["hits"]
        out = gen.generate(req.query, hits)
        return S.RagQueryResponse(answer=out["answer"], sources=out["sources"],
                                  provider=out["provider"],
                                  retrieved=[S.SourceRef(doc_name=h["doc_name"],
                                                         chunk_id=h["chunk_id"],
                                                         score=h["score"]) for h in hits])
    except HTTPException:
        raise
    except Exception as e:  # pragma: no cover
        log.exception("rag failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics() -> dict:
    """Training metrics written by scripts/train.py (real numbers only)."""
    p = model_dir() / "metrics.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="metrics.json not found. Run scripts/train.py first.")
    return json.loads(p.read_text(encoding="utf-8"))

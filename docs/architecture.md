# System Architecture

## Overview
```
customer message
  → FastAPI (/analyze) ─→ src/api/analysis.py
        ├─ classifier.joblib (TF-IDF + LogReg) → category
        ├─ sentiment.joblib (TF-IDF + LogReg fallback; HF distilbert optional) → sentiment
        ├─ severity rules → severity → risk_level + recommended_action
        ├─ escalation.joblib (XGBoost + one-hot) → P(escalation) + SHAP/feature-importance factors
        └─ RAG: Retriever (local cosine index) → generator (LLM_PROVIDER) → grounded answer + sources
```

## Components
- **Data**: `src/data/generate_synthetic.py` (seed 42, 5 000 rows) → `src/data/preprocessing.py`
  (validate → clean → normalize → features → stratified 70/15/15 split).
- **ML**: `src/models/{classifier,escalation,sentiment,severity,explain}.py`; artefacts in `models/`.
- **RAG**: `src/rag/{ingest,embeddings,retriever,generator}.py`; KB in `data/kb/*.md`
  (synthetic); index in `models/rag_index/`; embeddings = sentence-transformers
  with TF-IDF fallback so the project runs offline. The TF-IDF fallback drops
  English stop words (generic words otherwise caused spurious cross-domain matches).
  `Retriever.search_gated()` enforces `RAG_MIN_SIMILARITY` (default 0.10, env-tunable):
  below-threshold queries abstain WITHOUT calling any LLM (provider `abstention`,
  empty sources). Retrieval returns one best chunk per document (dedupes overlap fragments).
  Calibrated on the TF-IDF backend: 8 aviation probes (incl. paraphrases) scored
  top-1 0.136–0.344; 6 out-of-domain probes scored exactly 0.0; 0.10 sits in the gap.
- **API**: `src/api/main.py` (FastAPI, auto-docs at `/docs`); schemas in `src/api/schemas.py`.
- **Dashboard**: `app/streamlit_app.py` (5 pages; calls API, falls back to local pipeline).
- **DB**: `src/db/database.py` (SQLAlchemy; cases/predictions/documents/chunks/analyses;
  pgvector extension enabled when Postgres is available; local file index otherwise).
- **Infra**: `Dockerfile` (API), `docker-compose.yml` (pgvector Postgres + API).

## Key design decisions
1. **No target leakage**: `resolution_time_hours` is excluded from escalation features.
2. **Imbalance**: `class_weight="balanced"` (classifier), `scale_pos_weight` (XGBoost, ≈2.70).
3. **Offline-first**: every heavy dependency (HF models, OpenAI, Postgres, SHAP) has a
   documented local fallback; the default `LLM_PROVIDER=mock` needs no keys.
4. **Reproducibility**: fixed seeds (42), pinned splits, metrics written by training code only.

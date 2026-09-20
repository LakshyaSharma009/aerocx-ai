# AeroCX AI — Aviation Customer Experience Intelligence Platform

> **Synthetic-data portfolio project.** All tickets and knowledge-base documents are
> **synthetically generated** for engineering demonstration. No proprietary data, no GE
> Aerospace internal systems, documents, or APIs are used or claimed.

## 1. Project overview
AeroCX AI ingests aviation customer-service interactions and returns: issue category,
sentiment, severity, escalation probability (with explanations), relevant knowledge-base
passages, a grounded GenAI response with sources, and a recommended action — via a
FastAPI backend, a Streamlit dashboard, and a Postgres+pgvector store.

## 2. Problem statement
Airline/MRO/OEM support teams triage high-volume, high-stakes cases (AOG parts,
maintenance delays, billing disputes). Slow or inconsistent triage causes misconnections,
SLA breaches, and churn. AeroCX AI automates triage + drafting while keeping every
claim cited to retrievable sources.

## 3. Architecture
See `docs/architecture.md`. Flow:
`message → classify → sentiment → severity → escalate → retrieve → generate → recommend`.
UI: Streamlit (5 pages). API: FastAPI (`/docs`). DB: PostgreSQL+pgvector. LLM: provider
abstraction (`LLM_PROVIDER`: `mock` | `openai` | `huggingface`, default `mock`).

## 4. Data pipeline
`src/data/generate_synthetic.py` (seed 42, 5 000 rows, 9 imbalanced categories) →
`src/data/preprocessing.py` (schema validation, dedupe, median imputation, text
normalisation, engineered features, stratified 70/15/15 split). `resolution_time_hours`
is analytics-only (excluded from escalation features to prevent leakage).

## 5. ML pipeline
- **Classification** (`src/models/classifier.py`): TF-IDF + LogReg vs TF-IDF + LinearSVC,
  best by val macro-F1, persisted with joblib.
- **Escalation** (`src/models/escalation.py`): XGBoost, `scale_pos_weight≈2.70`.
- **Sentiment** (`src/models/sentiment.py`): documented HF primary
  (`distilbert-base-uncased-finetuned-sst-2-english`); shipped TF-IDF+LogReg fallback
  (default, offline); lexical heuristic last resort. Provider reported per response.
- **Severity** (`src/models/severity.py`): deterministic rules + risk mapping + actions.
- **Explainability** (`src/models/explain.py`): SHAP with gain-weighted fallback.

## 6. RAG architecture
`data/kb/*.md` (6 synthetic docs) → `src/rag/ingest.py` (overlap chunking) →
`src/rag/embeddings.py` (sentence-transformers, TF-IDF fallback) → local cosine index
(`models/rag_index/`) mirrorable to pgvector → `src/rag/retriever.py` (top-k) →
`src/rag/generator.py` (grounding system prompt, source citations, FACT vs
RECOMMENDATION split, explicit "don't know" behaviour).

## 7. API documentation
See `docs/api.md` and live Swagger at `/docs`. Endpoints: `GET /health`, `POST
/predict/category`, `POST /predict/sentiment`, `POST /predict/escalation`,
`POST /analyze`, `POST /rag/query`, `GET /metrics`.

## 8. Installation
```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env
```

## 9. Environment variables
| var | default | purpose |
|---|---|---|
| `LLM_PROVIDER` | `mock` | `mock` \| `openai` \| `huggingface` |
| `LLM_API_KEY` | — | provider key (never hard-code) |
| `LLM_MODEL` | `gpt-4o-mini` | provider model id |
| `DATABASE_URL` | local postgres | SQLAlchemy URL |
| `MODEL_PATH` | `models` | artefact dir |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | RAG encoder |
| `HF_SENTIMENT_MODEL` | `distilbert-...-sst-2-english` | optional HF sentiment |

## 10. Training instructions
```bash
$env:PYTHONPATH="."
python -m src.data.generate_synthetic --n 5000 --seed 42 --out data/raw/tickets.csv
python scripts/train.py --n 5000 --seed 42     # writes models/*.joblib + models/metrics.json
python -m src.rag.ingest                        # builds models/rag_index/
```

## 11. Running locally
```bash
$env:PYTHONPATH="."
uvicorn src.api.main:app --reload --port 8000        # API + /docs
streamlit run app/streamlit_app.py                   # dashboard (API_URL env optional)
python -m pytest tests/ -q                           # 24 tests
```

## 12. Docker instructions
```bash
docker compose up --build        # Postgres+pgvector (db) + API on :8000
python scripts/init_db.py        # create extension + tables (needs DATABASE_URL reachable)
streamlit run app/streamlit_app.py   # Streamlit runs separately (uses API_URL)
```

## 13. Evaluation methodology
Seeded stratified splits; vectorisers fit on train only; classification compared on
macro-F1 with confusion matrices; escalation judged on precision/recall/F1/ROC-AUC/PR-AUC
(recall favoured for triage); sentiment ships a fallback so results are reproducible
offline; RAG checked for citations and abstention. Full numbers: `docs/model_evaluation.md`.

## 14. Results (measured, val split, seed 42)
- **Classification**: LogReg and LinearSVC both macro-F1 **1.000** (synthetic templates
  are near-separable — see limitations).
- **Escalation (XGBoost)**: precision **0.726**, recall **0.847**, F1 **0.782**,
  ROC-AUC **0.946**, PR-AUC **0.875**; confusion `[[482, 65], [31, 172]]`.
- **Tests**: 24/24 passing. **RAG**: grounded answers with source lists; mock provider
  by default (no keys needed).

## 15. Limitations
1. Synthetic text flatters the classifier (F1 1.0); real-world copy would score lower.
2. Default embeddings are TF-IDF unless `sentence-transformers` weights are downloaded.
3. Default LLM is a template (`mock`) — fluent generation needs `openai`/`huggingface` keys.
4. pgvector mirroring requires a running Postgres; otherwise the local index is used.
5. SHAP explanations need the optional `shap` package; otherwise gain-weighted fallback.

## 16. Future improvements
Real (licensed) data + cross-validation, calibrated probabilities, encoder-based
sentiment by default, hybrid (dense+sparse) retrieval with evals (faithfulness,
citation precision), auth/rate-limits, Alembic migrations, CI, Kubernetes manifests,
drift monitoring.

## Project tree
```
src/{data,models,rag,api,db,utils}/  app/streamlit_app.py  scripts/{train,init_db}.py
tests/  docs/  data/{raw,processed,kb}/  models/  Dockerfile  docker-compose.yml
```



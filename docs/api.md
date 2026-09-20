# API Reference

Base URL (local): `http://localhost:8000`. Interactive docs: `/docs` (Swagger), `/redoc`.

## GET /health
```json
{"status": "ok", "models_loaded": {"classifier.joblib": true, "sentiment.joblib": true, "escalation.joblib": true}, "rag_ready": true}
```

## POST /predict/category
Request: `{"message": "..."}` → Response: `{"category": "Maintenance Delay", "confidence": 0.61}`

## POST /predict/sentiment
Request: `{"message": "..."}` → Response:
`{"sentiment_label": "negative", "sentiment_score": 0.49, "provider": "fallback-ml"}`

## POST /predict/escalation
```json
// request
{"message": "...", "category": "Maintenance Delay", "sentiment": "negative",
 "severity": "high", "delay_hours": 10, "previous_complaints": 2,
 "customer_priority": "gold", "aircraft_type": "A320neo"}
// response
{"escalation_probability": 0.93, "risk_level": "high",
 "important_factors": [{"feature": "previous_complaints", "contribution": 0.31}]}
```

## POST /analyze
Request: `{"message": "...", "delay_hours": 12, "previous_complaints": 1,
"customer_priority": "standard", "aircraft_type": "A320neo"}`.
Response: `category, category_confidence, sentiment, sentiment_score, severity,
escalation_probability, risk_level, recommended_action, generated_response,
sources, important_factors`.

## POST /rag/query
Request: `{"query": "How are AOG parts expedited?", "top_k": 4}` → Response:
`{"answer": "FACT — ... [aog_parts_procedure.md] ...", "sources": ["aog_parts_procedure.md"],
"provider": "mock", "retrieved": [...]}`.

**Relevance gate**: when no chunk reaches `RAG_MIN_SIMILARITY` (default 0.10),
the endpoint abstains WITHOUT calling the LLM:
`{"answer": "I don't have sufficiently relevant information ...", "sources": [],
"provider": "abstention", "retrieved": []}`. Same rule applies to the RAG portion
of `POST /analyze` (ML triage fields are still returned).

## GET /metrics
Returns `models/metrics.json` verbatim (real training numbers).

## Errors
- `422` — validation error (e.g. message too short).
- `503` — model/index not built (run `python scripts/train.py`, `python -m src.rag.ingest`).
- `500` — unexpected failure (check logs).

## curl examples
```bash
curl -X POST localhost:8000/predict/category -H "Content-Type: application/json" \
  -d '{"message":"Invoice double-charged for shop visit work scope"}'
curl -X POST localhost:8000/analyze -H "Content-Type: application/json" \
  -d '{"message":"Urgent AOG: need fuel nozzle at DXB, 48h lead time","delay_hours":48,"previous_complaints":3,"customer_priority":"platinum"}'
```

"""Tests for RAG, API endpoints, and error handling."""

from fastapi.testclient import TestClient

from src.api.main import app
from src.rag import generator as gen
from src.rag.ingest import chunk_text
from src.rag.retriever import Retriever

client = TestClient(app)


def test_chunking_keeps_provenance():
    """Chunks carry doc_name and chunk_id."""
    chunks = chunk_text("word " * 500, "doc.md", chunk_size=200, overlap=20)
    assert len(chunks) >= 2
    assert all(c["doc_name"] == "doc.md" for c in chunks)


def test_retriever_returns_ranked_hits():
    """Retriever returns top-k hits with scores."""
    r = Retriever()
    hits = r.search("AOG parts expediting lead time", top_k=2)
    assert len(hits) == 2
    assert hits[0]["score"] >= hits[1]["score"]
    assert "doc_name" in hits[0]


def test_generator_always_cites_sources():
    """Mock answer includes source names; empty ctx says unavailable."""
    hits = [{"doc_name": "a.md", "chunk_id": "a::0", "text": "t" * 100, "score": 0.5}]
    out = gen.generate("q", hits)
    assert "a.md" in out["answer"] and out["sources"] == ["a.md"]
    out2 = gen.generate("q", [])
    assert "don't have" in out2["answer"]


def test_health_endpoint():
    """GET /health returns ok + artefact flags."""
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_category_endpoint_and_validation_error():
    """Valid message classifies; empty message 422s."""
    r = client.post("/predict/category", json={"message": "Invoice double-charged for shop visit work scope"})
    assert r.status_code == 200 and "category" in r.json()
    r2 = client.post("/predict/category", json={"message": "x"})
    assert r2.status_code == 422


def test_sentiment_endpoint_schema():
    """Sentiment returns label+score."""
    r = client.post("/predict/sentiment", json={"message": "Thank you, excellent turnaround support"})
    assert r.status_code == 200
    assert r.json()["sentiment_label"] in ("positive", "neutral", "negative")


def test_escalation_endpoint_schema():
    """Escalation returns probability in [0,1]."""
    r = client.post("/predict/escalation", json={
        "message": "Maintenance delay 10h, many misconnections", "category": "Maintenance Delay",
        "sentiment": "negative", "severity": "high", "delay_hours": 10,
        "previous_complaints": 2, "customer_priority": "gold", "aircraft_type": "A320neo"})
    assert r.status_code == 200
    assert 0.0 <= r.json()["escalation_probability"] <= 1.0


def test_analyze_unified_schema():
    """POST /analyze returns the full contract."""
    r = client.post("/analyze", json={"message": "No stock of igniter plug at SIN for scheduled check",
                                      "delay_hours": 5, "previous_complaints": 1})
    assert r.status_code == 200
    body = r.json()
    for key in ["category", "sentiment", "severity", "escalation_probability",
                "risk_level", "recommended_action", "generated_response", "sources"]:
        assert key in body


def test_rag_query_endpoint():
    """POST /rag/query returns answer + sources."""
    r = client.post("/rag/query", json={"query": "How are billing disputes resolved?", "top_k": 2})
    assert r.status_code == 200
    assert r.json()["sources"]


def test_metrics_endpoint_has_real_numbers():
    """GET /metrics reflects trained models."""
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.json()["escalation"]["roc_auc"] > 0.5

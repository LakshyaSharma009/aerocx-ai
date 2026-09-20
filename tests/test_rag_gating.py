"""RAG relevance-gate tests: grounded aviation queries answer, off-domain abstains."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.rag import generator as gen
from src.rag.retriever import Retriever

client = TestClient(app)

AOG_QUERY = ("Urgent AOG: we need a replacement fuel nozzle and the aircraft "
             "has been grounded for 48 hours")
MAINT_QUERY = ("Our A320neo departure from JFK delayed 8h due to fuel nozzle "
               "maintenance, passengers misconnecting")
ROMAN_QUERY = "What is the history of the Roman Empire and who was Julius Caesar?"
CAKE_QUERY = "How do I make chocolate cake?"


def test_relevant_aog_query_grounded():
    """Test 1: AOG query retrieves aviation sources, no abstention."""
    r = Retriever().search_gated(AOG_QUERY)
    assert r["grounded"] is True
    assert r["top_score"] >= 0.10
    assert any("aog_parts" in h["doc_name"] for h in r["hits"])
    out = gen.generate(AOG_QUERY, r["hits"])
    assert out["provider"] != "abstention"
    assert "aog_parts_procedure.md" in out["sources"]


def test_relevant_maintenance_query_grounded():
    """Test 2: maintenance/delay query retrieves docs, no abstention."""
    r = Retriever().search_gated(MAINT_QUERY)
    assert r["grounded"] is True
    assert any("maintenance_delay_policy.md" == h["doc_name"] for h in r["hits"])


def test_roman_query_abstains_and_skips_generator(monkeypatch):
    """Test 3: Roman Empire query abstains; generator/LLM is NOT called."""
    called = []

    def _boom(query, contexts):
        called.append((query, contexts))
        raise AssertionError("generate() must not be called for ungrounded queries")

    monkeypatch.setattr("src.rag.generator.generate", _boom)
    resp = client.post("/rag/query", json={"query": ROMAN_QUERY, "top_k": 4})
    assert resp.status_code == 200
    body = resp.json()
    assert body["sources"] == [] and body["retrieved"] == []
    assert body["provider"] == "abstention"
    assert "sufficiently relevant" in body["answer"]
    assert "fuel nozzle" not in body["answer"].lower()
    assert called == []


def test_cake_query_abstains_no_aviation_answer():
    """Test 4: chocolate-cake query abstains with no hallucinated aviation answer."""
    resp = client.post("/rag/query", json={"query": CAKE_QUERY, "top_k": 4})
    assert resp.status_code == 200
    body = resp.json()
    assert body["sources"] == []
    assert "sufficiently relevant" in body["answer"]
    for banned in ["aog", "fuel nozzle", "mel", "rebook"]:
        assert banned not in body["answer"].lower()


def test_analyze_aog_regression():
    """Regression: /analyze ML outputs preserved; RAG portion grounded for AOG."""
    resp = client.post("/analyze", json={
        "message": "Urgent AOG: need fuel nozzle for B737 MAX 8 at DXB, quoted lead time 48h",
        "delay_hours": 48, "previous_complaints": 3, "customer_priority": "platinum"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["category"] == "Parts Availability"
    assert body["severity"] == "high" and body["risk_level"] == "high"
    assert body["escalation_probability"] > 0.9
    assert body["sources"], "AOG case must still retrieve AOG documentation"
    assert any("aog_parts" in s for s in body["sources"])
    assert "sufficiently relevant" not in body["generated_response"]


def test_analyze_roman_abstains_rag_only():
    """Out-of-domain /analyze: ML triage still runs, RAG portion abstains."""
    resp = client.post("/analyze", json={"message": ROMAN_QUERY})
    assert resp.status_code == 200
    body = resp.json()
    assert body["sources"] == []
    assert "sufficiently relevant" in body["generated_response"]
    # ML pipeline untouched: still returns category/sentiment/severity/escalation.
    for key in ["category", "sentiment", "severity", "escalation_probability", "risk_level"]:
        assert key in body


def test_generate_safety_net_on_low_scores():
    """Direct generate() with sub-threshold scored contexts abstains w/o provider."""
    out = gen.generate("anything", [{"doc_name": "x.md", "chunk_id": "x::0",
                                     "text": "unrelated", "score": 0.01}])
    assert out == {"answer": gen.ABSTAIN_MESSAGE, "sources": [], "provider": "abstention"}

"""Tests for models: classifier, sentiment, severity, escalation, explain."""

import pandas as pd

from src.data.generate_synthetic import generate
from src.data.preprocessing import add_features, clean_data
from src.models import escalation as esc_mod
from src.models import explain as explain_mod
from src.models import sentiment as sent_mod
from src.models import severity as sev_mod
from src.models.classifier import build_baseline, evaluate


def _small_frames():
    df = add_features(clean_data(generate(n=400, seed=11)))
    return df.iloc[:300], df.iloc[300:350]


def test_classifier_trains_and_predicts():
    """Baseline fits and emits category+confidence."""
    tr, va = _small_frames()
    m = build_baseline()
    m.fit(tr["clean_text"], tr["category"])
    metrics = evaluate(m, va["clean_text"], va["category"])
    assert metrics["f1_macro"] > 0.5
    assert "confusion_matrix" in metrics


def test_sentiment_heuristic_negative():
    """Heuristic flags angry delay text as negative."""
    label, score = sent_mod.heuristic("This delay is unacceptable, furious about the terrible service")
    assert label == "negative" and score > 0.5


def test_sentiment_analyzer_uses_fallback(tmp_path):
    """Analyzer prefers local fallback model when present."""
    tr, _ = _small_frames()
    p = tmp_path / "sent.joblib"
    sent_mod.train_fallback(tr["clean_text"].tolist()[:200], tr["sentiment"].tolist()[:200], p)
    az = sent_mod.SentimentAnalyzer(p)
    r = az.predict("Thank you, great prompt service")
    assert r["sentiment_label"] in ("positive", "neutral", "negative")
    assert r["provider"] == "fallback-ml"


def test_severity_high_on_aog():
    """AOG language yields high severity."""
    sev, conf = sev_mod.estimate_severity("Urgent AOG grounded aircraft, need part now", 30, 6)
    assert sev == "high"


def test_risk_level_mapping():
    """High prob or high severity maps to high risk."""
    assert sev_mod.risk_level(0.9, "low") == "high"
    assert sev_mod.risk_level(0.1, "low") == "low"


def test_escalation_trains_and_explains(tmp_path):
    """XGBoost trains on synthetic data; explain returns top features."""
    tr, va = _small_frames()
    m = esc_mod.train(tr, va, tmp_path)
    assert m["roc_auc"] > 0.7
    bundle = esc_mod.load_bundle(tmp_path / "escalation.joblib")
    row = va.iloc[[0]]
    assert len(esc_mod.predict_proba(bundle, row)) == 1
    factors = explain_mod.explain(bundle, row)
    assert 1 <= len(factors) <= 4 and "feature" in factors[0]

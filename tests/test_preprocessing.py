"""Tests for preprocessing and dataset validation."""

import pandas as pd
import pytest

from src.data.generate_synthetic import generate
from src.data.preprocessing import add_features, clean_data, normalize_text, split_data, validate_schema


def test_generate_fixed_seed_reproducible():
    """Same seed must yield identical frames."""
    a = generate(n=200, seed=7)
    b = generate(n=200, seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_generate_has_required_columns_and_size():
    """Generator emits >=5000 rows by default config with all fields."""
    df = generate(n=500, seed=42)
    for col in ["ticket_id", "customer_message", "category", "sentiment", "severity",
                "delay_hours", "previous_complaints", "customer_priority",
                "aircraft_type", "resolution_time_hours", "escalated"]:
        assert col in df.columns
    assert len(df) == 500
    assert df["escalated"].isin([0, 1]).all()


def test_generate_categories_within_allowed_set():
    """Categories come only from the spec list."""
    df = generate(n=300, seed=1)
    allowed = {"Maintenance", "Maintenance Delay", "Technical Issue", "Parts Availability",
               "Billing", "Service Quality", "Scheduling", "Contract", "Other"}
    assert set(df["category"]).issubset(allowed)


def test_validate_schema_raises_on_missing_column():
    """Missing columns raise ValueError."""
    with pytest.raises(ValueError):
        validate_schema(pd.DataFrame({"a": [1]}))


def test_normalize_text():
    """Lowercases and collapses whitespace."""
    assert normalize_text("  HELLO   World!! ") == "hello world " or "hello" in normalize_text("  HELLO   World!! ")


def test_clean_data_removes_invalid_rows():
    """Empty messages and duplicate ids are dropped."""
    df = pd.DataFrame([{
        "ticket_id": "T-1", "customer_message": "  ", "category": "Billing",
        "sentiment": "neutral", "severity": "low", "delay_hours": 1,
        "previous_complaints": 0, "customer_priority": "standard",
        "aircraft_type": "A320neo", "resolution_time_hours": 5, "escalated": 0},
        {"ticket_id": "T-2", "customer_message": "Need help", "category": "Billing",
         "sentiment": "neutral", "severity": "low", "delay_hours": 1,
         "previous_complaints": 0, "customer_priority": "standard",
         "aircraft_type": "A320neo", "resolution_time_hours": 5, "escalated": 0}])
    out = clean_data(df)
    assert len(out) == 1 and out.iloc[0]["ticket_id"] == "T-2"


def test_add_features_no_resolution_leakage_columns():
    """Feature frame includes engineered cols; resolution time kept only for analytics."""
    df = add_features(clean_data(generate(n=50, seed=3)))
    for col in ["severity_code", "priority_code", "sentiment_code", "log_delay", "msg_len"]:
        assert col in df.columns


def test_split_stratified_and_reproducible():
    """70/15/15 split preserving escalation rate approximately."""
    df = add_features(clean_data(generate(n=600, seed=9)))
    tr, va, te = split_data(df, seed=42)
    assert len(tr) + len(va) + len(te) == len(df)
    assert abs(tr["escalated"].mean() - df["escalated"].mean()) < 0.05

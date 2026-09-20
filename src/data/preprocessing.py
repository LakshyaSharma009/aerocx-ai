"""Preprocessing: validation, cleaning, text normalisation, features, splits."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

EXPECTED_COLUMNS = [
    "ticket_id", "customer_message", "category", "sentiment", "severity",
    "delay_hours", "previous_complaints", "customer_priority", "aircraft_type",
    "resolution_time_hours", "escalated",
]

CATEGORIES = [
    "Maintenance", "Maintenance Delay", "Technical Issue", "Parts Availability",
    "Billing", "Service Quality", "Scheduling", "Contract", "Other",
]
SENTIMENTS = ["positive", "neutral", "negative"]
SEVERITIES = ["low", "medium", "high"]
PRIORITIES = ["standard", "silver", "gold", "platinum"]

SEVERITY_MAP = {"low": 0, "medium": 1, "high": 2}
PRIORITY_MAP = {"standard": 0, "silver": 1, "gold": 2, "platinum": 3}
SENTIMENT_MAP = {"negative": 0, "neutral": 1, "positive": 2}


def normalize_text(text: str) -> str:
    """Lowercase, strip, collapse whitespace, drop non-informative chars."""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\-.,;:']", " ", text)
    return re.sub(r"\s+", " ", text)


def load_data(path: str | Path) -> pd.DataFrame:
    """Load tickets CSV."""
    return pd.read_csv(path)


def validate_schema(df: pd.DataFrame) -> None:
    """Raise ValueError if required columns are missing."""
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove invalid rows, impute numerics, normalise text. Returns new frame."""
    validate_schema(df)
    df = df.copy()
    # Drop rows with missing id/message.
    df = df.dropna(subset=["ticket_id", "customer_message"])
    df = df[df["customer_message"].astype(str).str.strip().str.len() > 0]
    df = df.drop_duplicates(subset=["ticket_id"], keep="first")
    # Impute numerics with median (fit on this frame; splits impute from train later).
    for col in ["delay_hours", "previous_complaints", "resolution_time_hours"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].fillna(df[col].median())
    # Categorical fallbacks.
    df["category"] = df["category"].where(df["category"].isin(CATEGORIES), "Other")
    df["sentiment"] = df["sentiment"].where(df["sentiment"].isin(SENTIMENTS), "neutral")
    df["severity"] = df["severity"].where(df["severity"].isin(SEVERITIES), "medium")
    df["customer_priority"] = df["customer_priority"].where(df["customer_priority"].isin(PRIORITIES), "standard")
    df["clean_text"] = df["customer_message"].astype(str).map(normalize_text)
    df["escalated"] = pd.to_numeric(df["escalated"], errors="coerce").fillna(0).astype(int).clip(0, 1)
    # Clip implausible values.
    df["delay_hours"] = df["delay_hours"].clip(0, 500)
    df["previous_complaints"] = df["previous_complaints"].clip(0, 50)
    return df.reset_index(drop=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add model-ready numeric features (no target leakage).

    Note: resolution_time_hours is an *outcome* observed after handling, so it
    is excluded from escalation features to avoid leakage. It is kept in the
    frame for analytics only.
    """
    df = df.copy()
    df["severity_code"] = df["severity"].map(SEVERITY_MAP).fillna(1).astype(int)
    df["priority_code"] = df["customer_priority"].map(PRIORITY_MAP).fillna(0).astype(int)
    df["sentiment_code"] = df["sentiment"].map(SENTIMENT_MAP).fillna(1).astype(int)
    df["is_negative"] = (df["sentiment"] == "negative").astype(int)
    df["is_high_severity"] = (df["severity"] == "high").astype(int)
    df["log_delay"] = np_log1p(df["delay_hours"].astype(float))
    df["msg_len"] = df["clean_text"].str.len().clip(0, 5000)
    df["msg_words"] = df["clean_text"].str.split().str.len().clip(0, 1000)
    df["complaint_x_delay"] = df["previous_complaints"].astype(float) * df["log_delay"]
    return df


def np_log1p(s: pd.Series) -> pd.Series:
    """log1p that tolerates NaN."""
    import numpy as np

    return np.log1p(s.fillna(0).clip(lower=0))


def split_data(
    df: pd.DataFrame, test_size: float = 0.15, val_size: float = 0.15, seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reproducible stratified (on escalated) train/val/test split."""
    train_val, test = train_test_split(df, test_size=test_size, random_state=seed, stratify=df["escalated"])
    val_rel = val_size / (1 - test_size)
    train, val = train_test_split(train_val, test_size=val_rel, random_state=seed, stratify=train_val["escalated"])
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)


def prepare(input_csv: str | Path, out_dir: str | Path, seed: int = 42) -> dict:
    """Full pipeline: load -> clean -> features -> split -> save. Returns paths + shapes."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = add_features(clean_data(load_data(input_csv)))
    train, val, test = split_data(df, seed=seed)
    paths = {}
    for name, frame in [("train", train), ("val", val), ("test", test)]:
        p = out / f"{name}.csv"
        frame.to_csv(p, index=False)
        paths[name] = str(p)
    paths["full"] = str(out / "full.csv")
    df.to_csv(paths["full"], index=False)
    return {"paths": paths, "shapes": {k: list(v.shape) for k, v in [("train", train), ("val", val), ("test", test)]}}

"""Escalation prediction with XGBoost (no target leakage)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.preprocessing import OneHotEncoder

from src.utils.logging import get_logger

log = get_logger(__name__)

# resolution_time_hours deliberately EXCLUDED (observed only after handling = leakage).
NUMERIC_FEATURES = ["delay_hours", "previous_complaints", "severity_code",
                    "priority_code", "sentiment_code", "is_negative",
                    "is_high_severity", "log_delay", "msg_len", "msg_words",
                    "complaint_x_delay"]
CATEGORICAL_FEATURES = ["category", "customer_priority", "aircraft_type"]


def _encoder() -> OneHotEncoder:
    return OneHotEncoder(handle_unknown="ignore", sparse_output=False)


def build_matrix(df: pd.DataFrame, encoder: OneHotEncoder | None = None):
    """Return (X, feature_names, fitted_encoder)."""
    df = df.copy()
    for c in NUMERIC_FEATURES:
        if c not in df.columns:
            df[c] = 0
    X_num = df[NUMERIC_FEATURES].fillna(0).to_numpy()
    num_names = list(NUMERIC_FEATURES)
    cat_df = df[CATEGORICAL_FEATURES].fillna("unknown").astype(str)
    if encoder is None:
        encoder = _encoder().fit(cat_df)
    X_cat = encoder.transform(cat_df)
    cat_names = list(encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    import numpy as np

    X = np.hstack([X_num, X_cat])
    return X, num_names + cat_names, encoder


def train(df_train: pd.DataFrame, df_val: pd.DataFrame, out_dir: str | Path) -> Dict:
    """Train XGBoost classifier with scale_pos_weight; persist bundle."""
    from xgboost import XGBClassifier

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    X_train, names, enc = build_matrix(df_train)
    X_val, _, _ = build_matrix(df_val, enc)
    y_train = df_train["escalated"].astype(int).to_numpy()
    y_val = df_val["escalated"].astype(int).to_numpy()

    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    spw = float(neg / max(pos, 1))
    clf = XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
        scale_pos_weight=spw, eval_metric="logloss",
        n_jobs=-1, random_state=42, tree_method="hist",
    )
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_val)[:, 1]
    pred = (proba >= 0.5).astype(int)
    metrics = {
        "precision": float(precision_score(y_val, pred, zero_division=0)),
        "recall": float(recall_score(y_val, pred, zero_division=0)),
        "f1": float(f1_score(y_val, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_val, proba)),
        "pr_auc": float(average_precision_score(y_val, proba)),
        "confusion_matrix": confusion_matrix(y_val, pred).tolist(),
        "scale_pos_weight": spw,
        "feature_names": names,
    }
    joblib.dump({"model": clf, "encoder": enc, "feature_names": names,
                 "numeric": NUMERIC_FEATURES, "categorical": CATEGORICAL_FEATURES}, out / "escalation.joblib")
    log.info("Saved escalation model (F1=%.4f ROC-AUC=%.4f)", metrics["f1"], metrics["roc_auc"])
    return metrics


def load_bundle(path: str | Path) -> Dict:
    """Load persisted escalation bundle."""
    return joblib.load(path)


def predict_proba(bundle: Dict, df: pd.DataFrame) -> List[float]:
    """Escalation probabilities for rows of df."""
    X, _, _ = build_matrix(df, bundle["encoder"])
    return [float(p) for p in bundle["model"].predict_proba(X)[:, 1]]

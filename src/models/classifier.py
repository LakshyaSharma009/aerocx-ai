"""Issue classification: TF-IDF + LogisticRegression baseline vs LinearSVC."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.utils.logging import get_logger

log = get_logger(__name__)


def build_baseline() -> Pipeline:
    """TF-IDF + Logistic Regression pipeline."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(max_features=8000, ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", n_jobs=None)),
    ])


def build_svm() -> Pipeline:
    """TF-IDF + Linear SVM pipeline."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(max_features=8000, ngram_range=(1, 2), sublinear_tf=True)),
        ("clf", LinearSVC(class_weight="balanced")),
    ])


def evaluate(model: Pipeline, X_test, y_test) -> Dict:
    """Return accuracy/precision/recall/F1 + confusion matrix + report."""
    pred = model.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision_macro": float(precision_score(y_test, pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, pred, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "labels": sorted(list(map(str, model.classes_))),
        "report": classification_report(y_test, pred, output_dict=True, zero_division=0),
    }


def train_and_compare(X_train, y_train, X_val, y_val, out_dir: str | Path) -> Dict:
    """Train both candidates, pick best by val macro-F1, persist with joblib."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    results: Dict = {}
    for name, builder in [("logreg", build_baseline), ("svm", build_svm)]:
        m = builder()
        m.fit(X_train, y_train)
        metrics = evaluate(m, X_val, y_val)
        results[name] = metrics
        log.info("%s val macro-F1=%.4f", name, metrics["f1_macro"])
    best_name = max(results, key=lambda k: results[k]["f1_macro"])
    best = {"logreg": build_baseline(), "svm": build_svm()}[best_name]
    best.fit(list(X_train) + list(X_val), list(y_train) + list(y_val))
    joblib.dump(best, out / "classifier.joblib")
    log.info("Saved best classifier (%s) -> %s", best_name, out / "classifier.joblib")
    return {"best": best_name, "metrics": results}


def load_model(path: str | Path) -> Pipeline:
    """Load persisted classifier."""
    return joblib.load(path)


def predict(model: Pipeline, texts: list[str]) -> list[Dict]:
    """Predict category + confidence (softmax for logreg; decision scores for SVM)."""
    import numpy as np

    preds = model.predict(texts)
    out = []
    if hasattr(model.named_steps["clf"], "predict_proba"):
        proba = model.predict_proba(texts)
        for label, row in zip(preds, proba):
            out.append({"category": str(label), "confidence": float(np.max(row))})
    else:  # LinearSVC: softmax over decision_function
        scores = model.decision_function(texts)
        scores = np.atleast_2d(scores)
        e = np.exp(scores - scores.max(axis=1, keepdims=True))
        probs = e / e.sum(axis=1, keepdims=True)
        for label, row in zip(preds, probs):
            out.append({"category": str(label), "confidence": float(np.max(row))})
    return out

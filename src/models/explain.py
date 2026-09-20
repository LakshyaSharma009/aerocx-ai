"""SHAP explainability for the escalation model, with feature-importance fallback."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from src.models import escalation as esc


def explain(bundle: Dict, row: pd.DataFrame, top_k: int = 4) -> List[Dict]:
    """Return top-k contributing features for a single-row prediction.

    Tries SHAP TreeExplainer; falls back to gain-based feature importance with
    per-row value weighting. Never raises: returns [] explanation on failure.
    """
    try:
        import shap  # type: ignore

        X, _, _ = esc.build_matrix(row, bundle["encoder"])
        explainer = shap.TreeExplainer(bundle["model"])
        vals = explainer.shap_values(X)
        import numpy as np

        if isinstance(vals, list):
            vals = vals[0]
        vals = np.asarray(vals).reshape(-1)
        names: List[str] = bundle["feature_names"]
        order = sorted(range(len(names)), key=lambda i: abs(float(vals[i])), reverse=True)[:top_k]
        return [{"feature": names[i], "contribution": float(vals[i])} for i in order]
    except Exception:
        pass
    # Fallback: global gain importance mapped to present feature values.
    try:
        import numpy as np

        model = bundle["model"]
        names: List[str] = bundle["feature_names"]
        imp = np.asarray(model.feature_importances_, dtype=float)
        X, _, _ = esc.build_matrix(row, bundle["encoder"])
        x = np.asarray(X).reshape(-1)
        # Weight importance by standardised magnitude so the explanation varies per case.
        score = imp * (np.abs(x) / (np.abs(x).mean() + 1e-9))
        order = list(np.argsort(score)[::-1][:top_k])
        total = float(score.sum()) or 1.0
        return [{"feature": names[i], "contribution": float(score[i] / total)} for i in order]
    except Exception:
        return []

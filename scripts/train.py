"""Train all ML models and write metrics JSON (no invented numbers)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data.preprocessing import prepare
from src.models import classifier as clf_mod
from src.models import escalation as esc_mod
from src.models import sentiment as sent_mod
from src.utils.config import get_settings
from src.utils.logging import get_logger

log = get_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main(n: int = 5000, seed: int = 42) -> dict:
    """Run full training; returns metrics dict and writes models/metrics.json."""
    settings = get_settings()
    raw = PROJECT_ROOT / "data" / "raw" / "tickets.csv"
    if not raw.exists():
        from src.data.generate_synthetic import generate

        raw.parent.mkdir(parents=True, exist_ok=True)
        generate(n=n, seed=seed).to_csv(raw, index=False)
        log.info("Generated synthetic data -> %s", raw)

    prep = prepare(raw, PROJECT_ROOT / "data" / "processed", seed=seed)
    import pandas as pd

    train = pd.read_csv(prep["paths"]["train"])
    val = pd.read_csv(prep["paths"]["val"])

    model_dir = PROJECT_ROOT / settings.model_path
    model_dir.mkdir(parents=True, exist_ok=True)

    clf_res = clf_mod.train_and_compare(
        train["clean_text"].tolist(), train["category"].tolist(),
        val["clean_text"].tolist(), val["category"].tolist(), model_dir,
    )
    sent_mod.train_fallback(train["clean_text"].tolist(), train["sentiment"].tolist(),
                            model_dir / "sentiment.joblib")
    esc_metrics = esc_mod.train(train, val, model_dir)

    metrics = {"classifier": clf_res, "escalation": esc_metrics,
               "shapes": prep["shapes"], "seed": seed, "n_synthetic": len(train) + len(val)}
    with open(model_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    log.info("Wrote %s", model_dir / "metrics.json")
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    m = main(n=args.n, seed=args.seed)
    print(json.dumps({k: (v if k != "classifier" else {kk: vv.get("f1_macro") if isinstance(vv, dict) else vv for kk, vv in v["metrics"].items()}) for k, v in m.items() if k in ("classifier", "escalation")}, indent=2))

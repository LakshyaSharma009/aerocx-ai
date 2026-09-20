"""Reproducible synthetic aviation customer-service dataset generator.

DISCLAIMER: All records are SYNTHETIC and generated with a fixed random seed.
They do not come from, and do not represent, any real airline, MRO, OEM
(including GE Aerospace), or real customer. They exist only so this portfolio
project can demonstrate ML/NLP/RAG engineering without proprietary data.

Fields:
    ticket_id, customer_message, category, sentiment, severity,
    delay_hours, previous_complaints, customer_priority, aircraft_type,
    resolution_time_hours, escalated
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = PROJECT_ROOT / "data" / "raw" / "tickets.csv"

CATEGORIES = [
    "Maintenance",
    "Maintenance Delay",
    "Technical Issue",
    "Parts Availability",
    "Billing",
    "Service Quality",
    "Scheduling",
    "Contract",
    "Other",
]

# Realistic class imbalance (must sum to 1.0).
CATEGORY_PROBS = np.array([0.18, 0.17, 0.15, 0.12, 0.10, 0.09, 0.08, 0.06, 0.05])

AIRCRAFT_TYPES = ["A320neo", "B737 MAX 8", "A321neo", "B787-9", "A350-900", "B777-300ER", "ATR 72-600", "E190-E2"]
PRIORITIES = ["standard", "silver", "gold", "platinum"]
PRIORITY_PROBS = np.array([0.45, 0.28, 0.18, 0.09])

TEMPLATES: dict[str, list[str]] = {
    "Maintenance": [
        "Engine {eng} on our {ac} requires unscheduled {item} inspection before next departure from {stn}. Please advise on maintenance slot.",
        "We need line maintenance support at {stn} for {ac}: {item} fault indication observed during turnaround.",
        "Request maintenance crew for {ac} at {stn}; {item} check could not be deferred per MEL. Need guidance.",
    ],
    "Maintenance Delay": [
        "Our {ac} departure from {stn} is delayed {h}h due to {item} maintenance. {n} passengers are impacted and we need recovery options.",
        "Maintenance delay of {h} hours on {ac} at {stn} because of {item}. This is causing misconnections; please escalate handling.",
        "Aircraft {ac} held at {stn} for extended {item} work ({h}h delay). Need revised departure plan and customer messaging.",
    ],
    "Technical Issue": [
        "{item} fault message keeps recurring on {ac} ({eng}). Troubleshooting per AMM did not clear it. Request engineering support.",
        "Intermittent {item} anomaly on {ac} at {stn}; {n} repeat write-ups this week. Need root-cause assistance.",
        "EICAS {item} warning on {ac} climb out of {stn}. Crew followed QRH. Aircraft on ground; advise next steps.",
    ],
    "Parts Availability": [
        "Urgent AOG: need {item} for {ac} ({eng}) at {stn}. Current lead time quoted is {h}h which we cannot accept.",
        "No stock of {item} at {stn} for scheduled {ac} check. Can you confirm alternate pooling or loan availability?",
        "Parts request: {item} for {ac} has been backordered {h}h. Please expedite or propose approved alternative.",
    ],
    "Billing": [
        "Invoice {inv} for {ac} shop visit appears to double-charge the {item} work scope. Please review and correct.",
        "Dispute on PBH invoice {inv}: {item} charges do not match contracted rate. Request credit note.",
        "We were billed for {item} on {ac} under invoice {inv} though the part was under warranty. Please investigate.",
    ],
    "Service Quality": [
        "Turnaround cleaning and {item} servicing at {stn} for {ac} were below standard; cabin not ready for boarding.",
        "Ground handling of {ac} at {stn} was poor: late {item} servicing and unhelpful staff. {n} similar events this month.",
        "Catering and {item} replenishment missed on {ac} at {stn}. Passengers complained; please address service quality.",
    ],
    "Scheduling": [
        "Proposed shop-visit slot for {ac} ({eng}) conflicts with our peak schedule. Can we move the {item} work earlier?",
        "Need to reschedule {item} maintenance for {ac} at {stn}; crew duty limits are affected by the {h}h shift.",
        "Slot request: {item} check for {ac} week of {wk}. Please confirm hangar availability at {stn}.",
    ],
    "Contract": [
        "Request clarification of {item} coverage under our service agreement for the {ac} fleet before we approve invoice {inv}.",
        "SLA breach: {item} response time at {stn} exceeded contracted {h}h limit twice this quarter. Request remedies.",
        "Renewal discussion: we want {item} support added for {ac} fleet ({n} aircraft). Please send commercial terms.",
    ],
    "Other": [
        "General enquiry about {item} documentation for {ac} ({eng}) operations at {stn}.",
        "Following up on earlier correspondence regarding {ac} {item} matter; please update status.",
        "Please call back regarding {ac} support at {stn} ({item}). Contact window next {h}h.",
    ],
}

ITEMS = ["fan blade", "fuel nozzle", "HPT shroud", "oil filter", "vibration sensor", "igniter plug", "thrust reverser actuator", "bleed valve", "FADEC unit", "gearbox seal"]
ENGINES = ["LEAP-1A", "LEAP-1B", "GEnx-1B", "GE9X", "CFM56-5B", "CF34-8E"]
STATIONS = ["JFK", "LHR", "DXB", "SIN", "DEL", "FRA", "ORD", "HND", "SYD", "BOM"]


def _sample_sentiment(rng: np.random.Generator, category: str, severity: str) -> str:
    """Sample sentiment correlated with category/severity (with noise)."""
    if severity == "high":
        probs = [0.08, 0.22, 0.70]  # pos, neu, neg
    elif severity == "medium":
        probs = [0.18, 0.42, 0.40]
    else:
        probs = [0.45, 0.35, 0.20]
    if category in ("Billing", "Maintenance Delay", "Parts Availability"):
        probs = [max(0.02, probs[0] - 0.08), probs[1] - 0.02, min(0.85, probs[2] + 0.10)]
    return str(rng.choice(["positive", "neutral", "negative"], p=np.array(probs) / sum(probs)))


def generate(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Generate n synthetic tickets deterministically."""
    rng = np.random.default_rng(seed)
    rnd = random.Random(seed)

    cats = rng.choice(CATEGORIES, size=n, p=CATEGORY_PROBS)
    rows = []
    for i in range(n):
        cat = str(cats[i])
        tmpl = rnd.choice(TEMPLATES[cat])
        h = int(rng.integers(1, 72))
        msg = tmpl.format(
            eng=rnd.choice(ENGINES), ac=rnd.choice(AIRCRAFT_TYPES), item=rnd.choice(ITEMS),
            stn=rnd.choice(STATIONS), h=h, n=int(rng.integers(1, 12)),
            inv=f"INV-{int(rng.integers(10000, 99999))}", wk=f"W{int(rng.integers(1, 52))}",
        )
        # Severity correlated with category.
        base = {"Maintenance Delay": 0.55, "Technical Issue": 0.5, "Parts Availability": 0.45,
                "Maintenance": 0.35, "Contract": 0.3, "Billing": 0.22, "Scheduling": 0.2,
                "Service Quality": 0.18, "Other": 0.1}[cat]
        sev_score = base + rng.normal(0, 0.15)
        severity = "high" if sev_score > 0.55 else ("medium" if sev_score > 0.3 else "low")
        sentiment = _sample_sentiment(rng, cat, severity)
        delay = float(np.clip(rng.exponential(8) + (20 if cat == "Maintenance Delay" else 0), 0, 120))
        prev = int(np.clip(rng.poisson(1.2) + (1 if sentiment == "negative" else 0), 0, 10))
        priority = str(rng.choice(PRIORITIES, p=PRIORITY_PROBS))
        ac = rnd.choice(AIRCRAFT_TYPES)
        res_h = float(np.clip(rng.lognormal(2.2, 0.9) + (10 if severity == "high" else 0), 1, 400))
        # Escalation: logistic function of risk factors (no leakage: resolution_time excluded).
        logit = (-2.6 + 1.1 * (severity == "high") + 0.5 * (severity == "medium")
                 + 0.9 * (sentiment == "negative") + 0.25 * prev + 0.03 * delay
                 + 0.5 * (priority == "platinum") + 0.25 * (priority == "gold")
                 + 0.4 * (cat in ("Maintenance Delay", "Technical Issue", "Parts Availability"))
                 + rng.normal(0, 0.6))
        escalated = int(1 / (1 + np.exp(-logit)) > 0.5)
        rows.append({
            "ticket_id": f"T-{i+1:06d}", "customer_message": msg, "category": cat,
            "sentiment": sentiment, "severity": severity, "delay_hours": round(delay, 1),
            "previous_complaints": prev, "customer_priority": priority, "aircraft_type": ac,
            "resolution_time_hours": round(res_h, 1), "escalated": escalated,
        })
    df = pd.DataFrame(rows)
    # Inject ~1% missing values to exercise imputation (never in ticket_id/message).
    miss = rng.choice(n, size=max(1, n // 100), replace=False)
    df.loc[miss, "delay_hours"] = np.nan
    return df


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Generate synthetic AeroCX tickets (SYNTHETIC DATA).")
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default=str(DEFAULT_OUT))
    args = ap.parse_args()
    df = generate(n=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} synthetic tickets -> {out} (seed={args.seed})")
    print("Escalation rate:", round(df["escalated"].mean(), 3))


if __name__ == "__main__":
    main()

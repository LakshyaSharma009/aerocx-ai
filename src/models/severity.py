"""Severity estimation: rule-based triage over text + structured signals."""

from __future__ import annotations

import re

HIGH_PATTERNS = [
    r"\baog\b", r"grounded", r"engine (shutdown|failure|fire)", r"mayday",
    r"emergency", r"safety", r"evacuat", r"fuel leak", r"escalat\w*",
    r"misconnect\w* .*(hundreds|all|every)", r"\b\d{2,}h delay\b",
]
MED_PATTERNS = [r"delay", r"fault", r"warning", r"breach", r"dispute", r"backorder",
                r"no stock", r"urgent", r"asap", r"deadline", r"slot"]


def estimate_severity(text: str, delay_hours: float = 0.0,
                      previous_complaints: int = 0,
                      category: str = "Other") -> tuple[str, float]:
    """Return (severity, confidence). Deterministic and explainable.

    Priority: explicit high-risk language > delay magnitude > repeat complaints
    > delay-prone categories > default medium/low.
    """
    t = text.lower()
    if any(re.search(p, t) for p in HIGH_PATTERNS) or delay_hours >= 24 or previous_complaints >= 5:
        return "high", 0.85
    med_hits = sum(1 for p in MED_PATTERNS if re.search(p, t))
    if med_hits >= 1 or delay_hours >= 6 or previous_complaints >= 2 \
            or category in ("Maintenance Delay", "Technical Issue", "Parts Availability"):
        return "medium", 0.70
    return "low", 0.65


def risk_level(escalation_probability: float, severity: str) -> str:
    """Map probability + severity to low/medium/high risk."""
    p = float(escalation_probability)
    if p >= 0.7 or (p >= 0.5 and severity == "high"):
        return "high"
    if p >= 0.35 or severity == "medium":
        return "medium"
    return "low"


def recommended_action(category: str, risk: str, severity: str) -> str:
    """Template recommended next action for an agent."""
    base = {
        "Maintenance Delay": "Rebook affected connections, publish revised departure, assign recovery owner.",
        "Technical Issue": "Open engineering work order, attach fault codes/photos, allocate troubleshooting slot.",
        "Parts Availability": "Confirm pool/loan stock, expedite AOG order, share ETA with customer hourly.",
        "Billing": "Place invoice on hold, reconcile against contract rates, issue correction within 2 business days.",
        "Service Quality": "Apologise, log station-level corrective action, follow up within 48h.",
        "Scheduling": "Propose two alternate slots within 72h and hold hangar capacity tentatively.",
        "Contract": "Route to commercial owner with SLA extract and remedy options.",
        "Maintenance": "Confirm maintenance window and MEL implications, dispatch crew.",
    }.get(category, "Acknowledge, categorise, and assign an owner with a response SLA.")
    prefix = {"high": "PRIORITY — senior duty owner now. ", "medium": "Standard priority. ",
              "low": "Routine handling. "}.get(risk, "")
    return f"{prefix}{base} (Severity: {severity}, Risk: {risk}.)"

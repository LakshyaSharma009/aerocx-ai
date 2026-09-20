"""AeroCX AI — Streamlit dashboard (5 pages, calls the FastAPI backend or local pipeline)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AeroCX AI", layout="wide")
st.title("AeroCX AI — Aviation Customer Experience Intelligence")
st.caption("Synthetic-data demo. No proprietary or GE Aerospace data is used.")


def api_post(path: str, payload: dict):
    """POST to the FastAPI backend; return None when unreachable."""
    try:
        import urllib.request

        req = urllib.request.Request(API_URL + path, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def local_analyze(**kwargs):
    """Direct local pipeline (used when API is unreachable)."""
    from src.api.analysis import analyze_case

    return analyze_case(kwargs.pop("message"), kwargs.pop("delay_hours", 0.0),
                        kwargs.pop("previous_complaints", 0),
                        kwargs.pop("customer_priority", "standard"),
                        kwargs.pop("aircraft_type", "A320neo"))


@st.cache_data
def load_processed() -> pd.DataFrame:
    """Load processed tickets for analytics pages."""
    p = ROOT / "data" / "processed" / "full.csv"
    if p.exists():
        return pd.read_csv(p)
    p = ROOT / "data" / "raw" / "tickets.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_data
def load_metrics() -> dict:
    """Load training metrics (real numbers from scripts/train.py)."""
    p = ROOT / "models" / "metrics.json"
    return json.loads(p.read_text()) if p.exists() else {}


page = st.sidebar.radio("Navigate", ["Overview", "Case Analyzer", "Risk Analytics",
                                     "AI Knowledge Assistant", "Model Performance"])

df = load_processed()
metrics = load_metrics()

if page == "Overview":
    st.header("Overview")
    if df.empty:
        st.warning("No data found. Run: python -m src.data.generate_synthetic && python scripts/train.py")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total cases", len(df))
        c2.metric("Escalation rate", f"{df['escalated'].mean():.1%}")
        c3.metric("Avg delay (h)", f"{df['delay_hours'].fillna(0).mean():.1f}")
        neg = (df["sentiment"] == "negative").mean() if "sentiment" in df.columns else 0
        c4.metric("Negative sentiment", f"{neg:.1%}")
        st.subheader("Category distribution")
        st.bar_chart(df["category"].value_counts())
        if "escalated" in df.columns:
            st.subheader("Escalations by category")
            st.bar_chart(df.groupby("category")["escalated"].mean().sort_values(ascending=False))

elif page == "Case Analyzer":
    st.header("Case Analyzer")
    msg = st.text_area("Customer message", height=120,
                       value="Urgent AOG: need fuel nozzle for B737 MAX 8 at DXB, quoted lead time 48h.")
    col1, col2, col3, col4 = st.columns(4)
    delay = col1.number_input("Delay hours", 0.0, 500.0, 12.0)
    prev = col2.number_input("Previous complaints", 0, 50, 1)
    prio = col3.selectbox("Priority", ["standard", "silver", "gold", "platinum"])
    ac = col4.selectbox("Aircraft", ["A320neo", "B737 MAX 8", "A321neo", "B787-9", "A350-900", "B777-300ER", "ATR 72-600", "E190-E2"])
    if st.button("Analyze case", type="primary"):
        with st.spinner("Running classification → sentiment → escalation → RAG..."):
            res = api_post("/analyze", {"message": msg, "delay_hours": delay,
                                        "previous_complaints": int(prev),
                                        "customer_priority": prio, "aircraft_type": ac})
            if res is None:
                res = local_analyze(message=msg, delay_hours=delay,
                                    previous_complaints=int(prev),
                                    customer_priority=prio, aircraft_type=ac)
                st.info("FastAPI unreachable — used local pipeline.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Category", f"{res['category']} ({res.get('category_confidence', 0):.0%})")
        m2.metric("Sentiment", f"{res['sentiment']} ({res['sentiment_score']:.2f})")
        m3.metric("Severity / Risk", f"{res['severity']} / {res['risk_level']}")
        m4.metric("Escalation P", f"{res['escalation_probability']:.0%}")
        st.subheader("Important prediction factors")
        st.json(res.get("important_factors", []))
        st.subheader("Recommended action")
        st.write(res.get("recommended_action", ""))
        st.subheader("Generated response (grounded)")
        st.write(res.get("generated_response", ""))
        st.subheader("Sources")
        st.write(", ".join(res.get("sources", [])) or "—")

elif page == "Risk Analytics":
    st.header("Risk Analytics")
    if df.empty:
        st.warning("No data found.")
    else:
        st.subheader("Escalation distribution")
        st.bar_chart(df["escalated"].value_counts())
        if "sentiment" in df.columns:
            st.subheader("Sentiment distribution")
            st.bar_chart(df["sentiment"].value_counts())
        st.subheader("High-risk cases (escalated=1, sample)")
        st.dataframe(df[df["escalated"] == 1].head(25))
        if "delay_hours" in df.columns:
            st.subheader("Delay hours vs escalation")
            st.scatter_chart(df.sample(min(500, len(df)))[["delay_hours", "escalated"]])

elif page == "AI Knowledge Assistant":
    st.header("AI Knowledge Assistant")
    q = st.text_input("Ask about support procedures",
                      value="How are AOG parts expedited?")
    if st.button("Ask", type="primary"):
        with st.spinner("Retrieving context..."):
            res = api_post("/rag/query", {"query": q, "top_k": 4})
            if res is None:
                from src.rag import generator as gen
                from src.rag.retriever import Retriever

                try:
                    hits = Retriever().search(q)
                except Exception as e:
                    hits = []
                    st.error(str(e))
                out = gen.generate(q, hits)
                res = {"answer": out["answer"], "sources": out["sources"],
                       "provider": out["provider"]}
                st.info("FastAPI unreachable — used local RAG.")
        st.write(res["answer"])
        st.subheader("Sources")
        st.write(", ".join(res.get("sources", [])) or "—")
        if res.get("retrieved"):
            st.json(res["retrieved"])

else:
    st.header("Model Performance")
    if not metrics:
        st.warning("No metrics found. Run python scripts/train.py first.")
    else:
        clf_m = metrics["classifier"]["metrics"]
        best = metrics["classifier"]["best"]
        st.subheader(f"Issue classification (best: {best}, validation split)")
        rows = [{"model": k, "accuracy": v["accuracy"], "precision": v["precision_macro"],
                 "recall": v["recall_macro"], "F1": v["f1_macro"]} for k, v in clf_m.items()]
        st.dataframe(pd.DataFrame(rows).set_index("model"))
        st.subheader("Escalation prediction (validation split)")
        esc = metrics["escalation"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("F1", f"{esc['f1']:.3f}")
        c2.metric("ROC-AUC", f"{esc['roc_auc']:.3f}")
        c3.metric("PR-AUC", f"{esc['pr_auc']:.3f}")
        c4.metric("Recall", f"{esc['recall']:.3f}")
        st.write("Confusion matrix (rows=actual, cols=predicted):")
        st.dataframe(pd.DataFrame(esc["confusion_matrix"],
                                  index=["actual 0", "actual 1"], columns=["pred 0", "pred 1"]))
        st.caption("Metrics are real outputs of scripts/train.py on synthetic data — see docs/model_evaluation.md.")

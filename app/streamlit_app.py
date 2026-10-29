"""AeroCX AI — Streamlit dashboard (5 pages, calls the FastAPI backend or local pipeline).

UI layer only: all modelling lives in src/. Charts use Plotly with a shared brand
palette; the app degrades gracefully to the in-process pipeline when the API is down.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

API_URL = os.getenv("API_URL", "http://localhost:8000")
GITHUB_URL = "https://github.com/LakshyaSharma009/aerocx-ai"

# --- Brand palette (colourblind-aware, brand-blue led) -----------------------
BRAND = "#0b5fff"
CATEGORICAL = ["#0b5fff", "#00a6a6", "#f2a900", "#e4572e", "#7b61ff",
               "#2bb673", "#ff7eb6", "#8d99ae", "#c44536"]
SENTIMENT_COLORS = {"negative": "#e4572e", "neutral": "#8d99ae", "positive": "#2bb673"}
LEVEL_COLORS = {  # severity / risk level -> colour
    "low": "#2bb673", "medium": "#f2a900", "high": "#e4572e",
    "critical": "#c0152f", "unknown": "#8d99ae",
}

st.set_page_config(page_title="AeroCX AI", page_icon="✈️", layout="wide",
                   initial_sidebar_state="expanded")

# --- Styling -----------------------------------------------------------------
st.markdown(
    """
    <style>
      .block-container {padding-top: 2.2rem; max-width: 1200px;}
      /* Hero */
      .aero-hero {
        background: linear-gradient(120deg, #0b5fff 0%, #1e3a8a 100%);
        color: #fff; border-radius: 16px; padding: 26px 30px; margin-bottom: 8px;
      }
      .aero-hero h1 {color:#fff; font-size: 1.9rem; margin: 0 0 6px 0; font-weight: 800;}
      .aero-hero p {color: #dbe7ff; margin: 0; font-size: 0.97rem;}
      .aero-pill {
        display:inline-block; background: rgba(255,255,255,.16); color:#fff;
        border-radius: 999px; padding: 3px 12px; font-size: .78rem; margin-right: 6px;
        margin-top: 10px;
      }
      /* Metric cards */
      [data-testid="stMetric"] {
        background: var(--secondary-background-color, #f3f6fb);
        border: 1px solid rgba(11,95,255,.12); border-radius: 12px;
        padding: 14px 16px 10px 16px;
      }
      [data-testid="stMetricValue"] {font-size: 1.7rem; font-weight: 700;}
      /* Badges */
      .badge {display:inline-block; padding:4px 12px; border-radius:999px;
              color:#fff; font-weight:600; font-size:.82rem;}
      /* Chips */
      .chip {display:inline-block; background:#eef3ff; color:#0b5fff;
             border:1px solid #cfe0ff; border-radius:999px; padding:3px 10px;
             font-size:.8rem; margin:3px 4px 0 0;}
      /* Answer / response card */
      .aero-card {background: var(--secondary-background-color, #f3f6fb);
                  border-left: 4px solid #0b5fff; border-radius: 10px;
                  padding: 14px 18px; margin-top: 6px; line-height: 1.5;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="aero-hero">
      <h1>✈️ AeroCX AI — Aviation Customer Experience Intelligence</h1>
      <p>Triage aviation support cases end to end: classify → sentiment → severity →
      escalation risk → grounded RAG answer → recommended action.</p>
      <span class="aero-pill">FastAPI + Streamlit</span>
      <span class="aero-pill">XGBoost · scikit-learn</span>
      <span class="aero-pill">Retrieval-Augmented Generation</span>
      <span class="aero-pill">Synthetic data · $0 to run</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Synthetic-data demo. No proprietary or GE Aerospace data is used or claimed.")


# --- Helpers -----------------------------------------------------------------
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


def badge(text: str, color: str) -> str:
    """Return an HTML pill badge."""
    return f'<span class="badge" style="background:{color}">{text}</span>'


def level_color(level: str) -> str:
    return LEVEL_COLORS.get(str(level).lower(), BRAND)


def style_fig(fig: go.Figure, height: int = 340) -> go.Figure:
    """Apply a consistent, clean look to a Plotly figure."""
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=36, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13), showlegend=False,
        title=dict(font=dict(size=15)),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(140,153,174,.18)")
    return fig


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


# --- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.markdown("### ✈️ AeroCX AI")
    page = st.radio(
        "Navigate",
        ["Overview", "Case Analyzer", "Risk Analytics",
         "AI Knowledge Assistant", "Model Performance"],
        label_visibility="collapsed",
    )
    st.divider()
    with st.expander("ℹ️ About this demo", expanded=False):
        st.markdown(
            "- **Pipeline:** classify → sentiment → severity → escalation → RAG\n"
            "- **LLM:** `mock` provider (no API key, fully offline)\n"
            "- **RAG:** TF-IDF index over a synthetic knowledge base\n"
            "- **Backend:** falls back to the local pipeline if the API is down"
        )
    st.markdown(f"[📂 Source code]({GITHUB_URL})")

df = load_processed()
metrics = load_metrics()


# ---------------------------------------------------------------- OVERVIEW ---
if page == "Overview":
    if df.empty:
        st.warning("No data found. Run: python -m src.data.generate_synthetic && python scripts/train.py")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total cases", f"{len(df):,}")
        c2.metric("Escalation rate", f"{df['escalated'].mean():.1%}")
        c3.metric("Avg delay (h)", f"{df['delay_hours'].fillna(0).mean():.1f}")
        neg = (df["sentiment"] == "negative").mean() if "sentiment" in df.columns else 0
        c4.metric("Negative sentiment", f"{neg:.1%}")

        st.markdown("#### Case volume by category")
        vc = df["category"].value_counts().sort_values(ascending=True)
        fig = px.bar(x=vc.values, y=vc.index, orientation="h",
                     color=vc.values, color_continuous_scale="Blues",
                     labels={"x": "cases", "y": ""})
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)

        if "escalated" in df.columns:
            st.markdown("#### Escalation rate by category")
            er = (df.groupby("category")["escalated"].mean()
                    .sort_values(ascending=True))
            fig = px.bar(x=er.values, y=er.index, orientation="h",
                         color=er.values, color_continuous_scale="OrRd",
                         labels={"x": "escalation rate", "y": ""})
            fig.update_xaxes(tickformat=".0%")
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(style_fig(fig, 360), use_container_width=True)


# ----------------------------------------------------------- CASE ANALYZER ---
elif page == "Case Analyzer":
    st.subheader("Analyze a support case")
    msg = st.text_area("Customer message", height=120,
                       value="Urgent AOG: need fuel nozzle for B737 MAX 8 at DXB, quoted lead time 48h.")
    col1, col2, col3, col4 = st.columns(4)
    delay = col1.number_input("Delay hours", 0.0, 500.0, 12.0)
    prev = col2.number_input("Previous complaints", 0, 50, 1)
    prio = col3.selectbox("Priority", ["standard", "silver", "gold", "platinum"])
    ac = col4.selectbox("Aircraft", ["A320neo", "B737 MAX 8", "A321neo", "B787-9",
                                     "A350-900", "B777-300ER", "ATR 72-600", "E190-E2"])

    if st.button("🔍 Analyze case", type="primary"):
        with st.spinner("Running classification → sentiment → escalation → RAG..."):
            res = api_post("/analyze", {"message": msg, "delay_hours": delay,
                                        "previous_complaints": int(prev),
                                        "customer_priority": prio, "aircraft_type": ac})
            if res is None:
                res = local_analyze(message=msg, delay_hours=delay,
                                    previous_complaints=int(prev),
                                    customer_priority=prio, aircraft_type=ac)
                st.info("FastAPI unreachable — used in-process pipeline.")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Category", res["category"], f"{res.get('category_confidence', 0):.0%} conf.")
        m2.metric("Sentiment", res["sentiment"].title(), f"score {res['sentiment_score']:.2f}")
        m3.metric("Escalation probability", f"{res['escalation_probability']:.0%}")
        m4.metric("Avg category delay", f"{delay:.0f} h")

        st.markdown(
            "**Severity / Risk:** &nbsp;"
            + badge(str(res["severity"]).title(), level_color(res["severity"]))
            + " &nbsp; "
            + badge(str(res["risk_level"]).title() + " risk", level_color(res["risk_level"])),
            unsafe_allow_html=True,
        )

        left, right = st.columns([1, 1])
        with left:
            st.markdown("##### 🛠️ Recommended action")
            st.markdown(f'<div class="aero-card">{res.get("recommended_action", "—")}</div>',
                        unsafe_allow_html=True)
            st.markdown("##### 📌 Key prediction factors")
            factors = res.get("important_factors", [])
            if factors and isinstance(factors[0], dict):
                st.dataframe(pd.DataFrame(factors), use_container_width=True, hide_index=True)
            elif factors:
                st.markdown("\n".join(f"- {f}" for f in factors))
            else:
                st.caption("No factors returned.")
        with right:
            st.markdown("##### 🤖 Grounded response")
            st.markdown(f'<div class="aero-card">{res.get("generated_response", "—")}</div>',
                        unsafe_allow_html=True)
            srcs = res.get("sources", [])
            st.markdown("##### 📚 Sources")
            st.markdown("".join(f'<span class="chip">{s}</span>' for s in srcs) or "—",
                        unsafe_allow_html=True)


# ----------------------------------------------------------- RISK ANALYTICS ---
elif page == "Risk Analytics":
    if df.empty:
        st.warning("No data found.")
    else:
        colA, colB = st.columns(2)
        with colA:
            st.markdown("#### Escalated vs. not")
            counts = df["escalated"].map({0: "Not escalated", 1: "Escalated"}).value_counts()
            fig = px.pie(values=counts.values, names=counts.index, hole=0.55,
                         color=counts.index,
                         color_discrete_map={"Escalated": "#e4572e",
                                             "Not escalated": "#0b5fff"})
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(style_fig(fig, 320), use_container_width=True)
        with colB:
            if "sentiment" in df.columns:
                st.markdown("#### Sentiment distribution")
                sc = df["sentiment"].value_counts()
                fig = px.bar(x=sc.index, y=sc.values, color=sc.index,
                             color_discrete_map=SENTIMENT_COLORS,
                             labels={"x": "", "y": "cases"})
                st.plotly_chart(style_fig(fig, 320), use_container_width=True)

        if "delay_hours" in df.columns:
            st.markdown("#### Delay hours by escalation outcome")
            d = df.copy()
            d["outcome"] = d["escalated"].map({0: "Not escalated", 1: "Escalated"})
            fig = px.box(d, x="outcome", y="delay_hours", color="outcome",
                         color_discrete_map={"Escalated": "#e4572e",
                                             "Not escalated": "#0b5fff"},
                         labels={"outcome": "", "delay_hours": "delay (h)"})
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)

        st.markdown("#### High-risk cases (escalated, sample)")
        st.dataframe(df[df["escalated"] == 1].head(25), use_container_width=True)


# -------------------------------------------------- AI KNOWLEDGE ASSISTANT ---
elif page == "AI Knowledge Assistant":
    st.subheader("Ask the knowledge base")
    q = st.text_input("Ask about support procedures", value="How are AOG parts expedited?")
    if st.button("💬 Ask", type="primary"):
        with st.spinner("Retrieving context and composing a grounded answer..."):
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
                st.info("FastAPI unreachable — used in-process RAG.")

        st.markdown(f'<div class="aero-card">{res["answer"]}</div>', unsafe_allow_html=True)
        st.markdown("##### 📚 Sources")
        srcs = res.get("sources", [])
        st.markdown("".join(f'<span class="chip">{s}</span>' for s in srcs) or "—",
                    unsafe_allow_html=True)
        st.caption(f"Provider: {res.get('provider', 'mock')}")
        if res.get("retrieved"):
            with st.expander("Retrieved passages"):
                st.json(res["retrieved"])


# -------------------------------------------------------- MODEL PERFORMANCE ---
else:
    if not metrics:
        st.warning("No metrics found. Run python scripts/train.py first.")
    else:
        clf_m = metrics["classifier"]["metrics"]
        best = metrics["classifier"]["best"]
        st.markdown(f"#### Issue classification — best model: `{best}` (validation split)")
        rows = [{"model": k, "accuracy": v["accuracy"], "precision": v["precision_macro"],
                 "recall": v["recall_macro"], "F1": v["f1_macro"]} for k, v in clf_m.items()]
        st.dataframe(pd.DataFrame(rows).set_index("model"), use_container_width=True)

        st.markdown("#### Escalation prediction (validation split)")
        esc = metrics["escalation"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("F1", f"{esc['f1']:.3f}")
        c2.metric("ROC-AUC", f"{esc['roc_auc']:.3f}")
        c3.metric("PR-AUC", f"{esc['pr_auc']:.3f}")
        c4.metric("Recall", f"{esc['recall']:.3f}")

        st.markdown("#### Confusion matrix")
        cm = esc["confusion_matrix"]
        fig = px.imshow(cm, text_auto=True, color_continuous_scale="Blues",
                        x=["pred: no escalation", "pred: escalation"],
                        y=["actual: no escalation", "actual: escalation"],
                        labels={"color": "cases"})
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)
        st.caption("Metrics are real outputs of scripts/train.py on synthetic data — "
                   "see docs/model_evaluation.md.")

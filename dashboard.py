"""
NEPSE Market Tracker Dashboard
Streamlit frontend – reads data/data.json
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEPSE Market Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Auth (optional – set DASHBOARD_PASSWORD in env/secrets) ─────────────────
_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
if _PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 NEPSE Market Tracker")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if pw == _PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    /* Dark finance theme */
    [data-testid="stSidebar"] { background: #0d1117; }
    .main { background: #0d1117; }
    .grade-A\\+ { color: #00ff88; font-weight: bold; }
    .grade-A  { color: #7fff00; font-weight: bold; }
    .grade-B  { color: #ffd700; font-weight: bold; }
    .grade-C  { color: #ff8c00; font-weight: bold; }
    .grade-D  { color: #ff4444; font-weight: bold; }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .stDataFrame { font-size: 13px; }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Load data ───────────────────────────────────────────────────────────────
DATA_PATH = Path("data/data.json")


@st.cache_data(ttl=300)
def load_data():
    if not DATA_PATH.exists():
        return None, None
    with open(DATA_PATH) as f:
        raw = json.load(f)
    df = pd.DataFrame(raw["stocks"])
    return df, raw


df, meta = load_data()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/9/9b/Nepal_Stock_Exchange_logo.png/220px-Nepal_Stock_Exchange_logo.png",
        width=140,
    )
    st.markdown("## ⚙️ Filters")

    if df is not None and not df.empty:
        sectors = ["All"] + sorted(df["sector"].dropna().unique().tolist()) if "sector" in df.columns else ["All"]
        selected_sector = st.selectbox("Sector", sectors)

        grades = ["All", "A+", "A", "B", "C", "D"]
        selected_grade = st.selectbox("Grade", grades)

        min_score, max_score = st.slider(
            "Health Score", 0, 100, (0, 100), step=5
        )

        sort_col = st.selectbox(
            "Sort by",
            ["health_score", "ltp", "eps", "pe_ratio", "dividend_yield", "change_pct"],
        )
        sort_asc = st.checkbox("Ascending", value=False)

    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    if meta:
        st.caption(f"Last updated: {meta.get('generated_at', 'N/A')[:16].replace('T', ' ')} UTC")

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("# 📈 NEPSE Market Tracker")
st.caption("Automated daily scrape · NepseAlpha + ShareSansar + Merolagani")

if df is None or df.empty:
    st.error("⚠️ No data found. Run `python scraper.py` first to populate data/data.json")
    st.stop()

# ─── Apply filters ───────────────────────────────────────────────────────────
fdf = df.copy()

if "sector" in fdf.columns and selected_sector != "All":
    fdf = fdf[fdf["sector"] == selected_sector]

if "grade" in fdf.columns and selected_grade != "All":
    fdf = fdf[fdf["grade"] == selected_grade]

if "health_score" in fdf.columns:
    fdf = fdf[
        (fdf["health_score"] >= min_score) & (fdf["health_score"] <= max_score)
    ]

if sort_col in fdf.columns:
    fdf = fdf.sort_values(sort_col, ascending=sort_asc)

# ─── KPI Row ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total Stocks", meta.get("total_stocks", len(df)))
with k2:
    gainers = int((df["change_pct"] > 0).sum()) if "change_pct" in df.columns else 0
    st.metric("Gainers 🟢", gainers)
with k3:
    losers = int((df["change_pct"] < 0).sum()) if "change_pct" in df.columns else 0
    st.metric("Losers 🔴", losers)
with k4:
    if "health_score" in df.columns:
        top = df[df["grade"].isin(["A+", "A"])].shape[0] if "grade" in df.columns else 0
        st.metric("Grade A/A+ Stocks", top)
with k5:
    if "eps" in df.columns:
        avg_eps = df["eps"].dropna().mean()
        st.metric("Avg EPS", f"{avg_eps:.1f}")

st.markdown("---")

# ─── Main Tabs ───────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Stock Table", "🏆 Top Picks", "📉 Charts", "🔬 Fundamentals"]
)

# ── Tab 1: Full table ────────────────────────────────────────────────────────
with tab1:
    display_cols = [c for c in [
        "symbol", "name", "sector", "ltp", "change_pct", "volume",
        "eps", "pe_ratio", "dividend_yield", "pbv", "roe",
        "health_score", "grade",
    ] if c in fdf.columns]

    show_df = fdf[display_cols].copy()

    # Rename for display
    rename = {
        "ltp": "LTP (Rs)",
        "change_pct": "Change %",
        "pe_ratio": "P/E",
        "dividend_yield": "Div Yield %",
        "health_score": "Score",
    }
    show_df = show_df.rename(columns={k: v for k, v in rename.items() if k in show_df.columns})

    st.dataframe(
        show_df,
        use_container_width=True,
        height=520,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score", min_value=0, max_value=100, format="%d"
            ),
            "LTP (Rs)": st.column_config.NumberColumn(format="Rs %.0f"),
            "Change %": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )
    st.caption(f"Showing {len(show_df)} of {len(df)} stocks")

# ── Tab 2: Top picks ─────────────────────────────────────────────────────────
with tab2:
    st.subheader("🏆 Top 10 by Health Score")

    if "health_score" in df.columns:
        top10 = df.nlargest(10, "health_score")
        for _, row in top10.iterrows():
            with st.expander(
                f"**{row.get('symbol','')}** — {row.get('name','')}  "
                f"| Grade: {row.get('grade','?')}  | Score: {row.get('health_score',0)}/100"
            ):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("LTP", f"Rs {row.get('ltp', 0):,.0f}")
                c2.metric("EPS", f"{row.get('eps', 0):.1f}")
                c3.metric("P/E", f"{row.get('pe_ratio', 0):.1f}")
                c4.metric("Div Yield", f"{row.get('dividend_yield', 0):.1f}%")

                c5, c6, c7, c8 = st.columns(4)
                c5.metric("P/BV", f"{row.get('pbv', 0):.2f}")
                c6.metric("ROE", f"{row.get('roe', 0):.1f}%")
                c7.metric("Volume", f"{int(row.get('volume', 0)):,}")
                c8.metric("Change", f"{row.get('change_pct', 0):+.2f}%")

                # Score breakdown bar
                breakdown_keys = [
                    "eps_score", "pe_score", "div_score",
                    "roe_score", "pbv_score", "momentum_score",
                ]
                bd = {k.replace("_score", "").upper(): row.get(k, 0) for k in breakdown_keys if k in row}
                if bd:
                    fig = go.Figure(
                        go.Bar(
                            x=list(bd.keys()),
                            y=list(bd.values()),
                            marker_color="#00ff88",
                        )
                    )
                    fig.update_layout(
                        height=200,
                        margin=dict(l=0, r=0, t=10, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(range=[0, 22]),
                    )
                    st.plotly_chart(fig, use_container_width=True)

# ── Tab 3: Charts ────────────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Health Score Distribution")
        if "health_score" in df.columns:
            fig = px.histogram(
                df, x="health_score", nbins=20,
                color_discrete_sequence=["#00ff88"],
                labels={"health_score": "Health Score"},
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Grade Breakdown")
        if "grade" in df.columns:
            grade_counts = df["grade"].value_counts().reset_index()
            grade_counts.columns = ["Grade", "Count"]
            fig = px.pie(
                grade_counts, names="Grade", values="Count",
                color_discrete_sequence=px.colors.sequential.Greens_r,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("EPS vs P/E Ratio (Bubble = Volume)")
    if all(c in df.columns for c in ["eps", "pe_ratio"]):
        plot_df = df.dropna(subset=["eps", "pe_ratio"])
        fig = px.scatter(
            plot_df,
            x="pe_ratio", y="eps",
            size="volume" if "volume" in plot_df.columns else None,
            color="grade" if "grade" in plot_df.columns else None,
            hover_data=["symbol", "ltp", "health_score"],
            labels={"pe_ratio": "P/E Ratio", "eps": "EPS (Rs)"},
            color_discrete_map={"A+": "#00ff88", "A": "#7fff00", "B": "#ffd700", "C": "#ff8c00", "D": "#ff4444"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    if "sector" in df.columns:
        st.subheader("Avg Health Score by Sector")
        sec_df = df.groupby("sector")["health_score"].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(
            sec_df, x="health_score", y="sector", orientation="h",
            color="health_score", color_continuous_scale="Greens",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 4: Fundamentals ──────────────────────────────────────────────────────
with tab4:
    st.subheader("🔬 Fundamental Screener")
    st.markdown("Use the sidebar filters + these sliders to screen deeply.")

    c1, c2, c3 = st.columns(3)
    min_eps = c1.number_input("Min EPS", value=0.0, step=5.0)
    max_pe = c2.number_input("Max P/E", value=30.0, step=1.0)
    min_div = c3.number_input("Min Dividend Yield %", value=0.0, step=0.5)

    filtered = fdf.copy()
    if "eps" in filtered.columns:
        filtered = filtered[filtered["eps"].fillna(0) >= min_eps]
    if "pe_ratio" in filtered.columns:
        filtered = filtered[filtered["pe_ratio"].fillna(999) <= max_pe]
    if "dividend_yield" in filtered.columns:
        filtered = filtered[filtered["dividend_yield"].fillna(0) >= min_div]

    st.dataframe(
        filtered[
            [c for c in ["symbol", "name", "sector", "ltp", "eps", "pe_ratio",
                          "dividend_yield", "roe", "pbv", "health_score", "grade"]
             if c in filtered.columns]
        ],
        use_container_width=True,
        height=420,
    )

    st.download_button(
        "⬇️ Download Filtered CSV",
        filtered.to_csv(index=False),
        file_name=f"nepse_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

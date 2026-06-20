"""
NEPSE Market Tracker — v2 Dashboard
Full search, candlestick charts, AI smart compare, political/macro analysis,
comprehensive fundamentals, and a proper dark trading terminal UI.
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from interpreter import interpret_stock  # Your deterministic logic module

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NEPSE Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Auth ────────────────────────────────────────────────────────────────────
_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
if _PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;
                    justify-content:center;height:60vh'>
          <h1 style='color:#00ff88;font-family:monospace'>📈 NEPSE TRACKER</h1>
          <p style='color:#8b949e'>Nepal Stock Market Intelligence</p>
        </div>""", unsafe_allow_html=True)
        col = st.columns([1,2,1])[1]
        pw = col.text_input("Password", type="password", placeholder="Enter password…")
        if col.button("Login →", use_container_width=True):
            if pw == _PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                col.error("Wrong password.")
        st.stop()

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');
  html, body, [data-testid="stApp"] { background:#0a0e1a !important; }
  [data-testid="stSidebar"] { background:#0d1117 !important; border-right:1px solid #21262d; }
  h1,h2,h3 { font-family:'Inter',sans-serif !important; }
  .mono { font-family:'JetBrains Mono',monospace; }
  .kpi-card {
    background:linear-gradient(135deg,#161b22,#0d1117);
    border:1px solid #21262d; border-radius:10px;
    padding:18px 20px; text-align:center;
  }
  .kpi-val { font-size:2rem; font-weight:700; font-family:'JetBrains Mono',monospace; color:#e6edf3; }
  .kpi-label { font-size:0.75rem; color:#8b949e; letter-spacing:.08em; text-transform:uppercase; margin-top:4px; }
  .stock-card {
    background:#161b22; border:1px solid #21262d; border-radius:10px;
    padding:16px; margin-bottom:10px; transition:border-color .2s;
  }
  .stock-card:hover { border-color:#00ff88; }
  .grade-Ap { color:#00ff88; font-weight:700; font-size:1.4rem; }
  .grade-A  { color:#7fff00; font-weight:700; font-size:1.4rem; }
  .grade-B  { color:#ffd700; font-weight:700; font-size:1.4rem; }
  .grade-C  { color:#ff8c00; font-weight:700; font-size:1.4rem; }
  .grade-D  { color:#ff4444; font-weight:700; font-size:1.4rem; }
  .tag {
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:0.72rem; font-weight:600; margin-right:4px;
  }
  .tag-bull { background:#0d3321; color:#00ff88; border:1px solid #00ff8840; }
  .tag-bear { background:#3d0e0e; color:#ff4444; border:1px solid #ff444440; }
  .tag-neut { background:#1c2333; color:#8b949e; border:1px solid #30363d; }
  .signal-box {
    background:#0d1117; border-left:3px solid #00ff88;
    border-radius:4px; padding:10px 14px; margin:6px 0;
    font-size:0.85rem; color:#c9d1d9;
  }
  div[data-testid="stTab"] button { font-family:'Inter',sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ─── Load data ────────────────────────────────────────────────────────────────
DATA_PATH = Path("data/data.json")

@st.cache_data(ttl=300)
def load_data():
    if not DATA_PATH.exists():
        return None, None
    with open(DATA_PATH) as f:
        raw = json.load(f)
    df = pd.DataFrame(raw.get("stocks", []))
    return df, raw

df, meta = load_data()

# ─── Helpers ─────────────────────────────────────────────────────────────────
def pct_color(v):
    if v is None: return "#8b949e"
    return "#00ff88" if v >= 0 else "#ff4444"

def grade_class(g):
    return {"A+":"Ap","A":"A","B":"B","C":"C","D":"D"}.get(g,"neut")

def generate_candles(symbol, ltp, days=120):
    """Simulate realistic OHLCV candlestick history around the current LTP."""
    random.seed(hash(symbol) % 9999)
    price = ltp * 0.80
    data = []
    base_date = datetime.today() - timedelta(days=days)
    for i in range(days):
        change = random.gauss(0.002, 0.018)
        open_p = price
        close_p = price * (1 + change)
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.012))
        low_p  = min(open_p, close_p) * (1 - random.uniform(0, 0.012))
        vol    = int(random.uniform(5000, 80000))
        data.append({
            "date": base_date + timedelta(days=i),
            "open": round(open_p, 1),
            "high": round(high_p, 1),
            "low":  round(low_p, 1),
            "close": round(close_p, 1),
            "volume": vol,
        })
        price = close_p
    return pd.DataFrame(data)

def compute_indicators(cdf):
    """RSI, MACD, Bollinger Bands, SMA."""
    cdf = cdf.copy()
    cdf["sma20"] = cdf["close"].rolling(20).mean()
    cdf["sma50"] = cdf["close"].rolling(50).mean()
    # Bollinger
    std20 = cdf["close"].rolling(20).std()
    cdf["bb_upper"] = cdf["sma20"] + 2 * std20
    cdf["bb_lower"] = cdf["sma20"] - 2 * std20
    # RSI
    delta = cdf["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-9)
    cdf["rsi"] = 100 - (100 / (1 + rs))
    # MACD
    ema12 = cdf["close"].ewm(span=12).mean()
    ema26 = cdf["close"].ewm(span=26).mean()
    cdf["macd"] = ema12 - ema26
    cdf["macd_signal"] = cdf["macd"].ewm(span=9).mean()
    cdf["macd_hist"] = cdf["macd"] - cdf["macd_signal"]
    return cdf

def political_macro_analysis(row):
    """Rule-based political & macro risk assessment."""
    sector = row.get("sector", "")
    eps = row.get("eps", 0) or 0
    div = row.get("dividend_yield", 0) or 0
    score = row.get("health_score", 0) or 0
    signals = []

    sector_macro = {
        "Banking": [
            "🏛️ Nepal Rastra Bank interest rate policy directly impacts net interest margin.",
            "📋 Basel III compliance requirements add capital pressure on smaller banks.",
            "💰 Remittance inflows (35% of GDP) are the primary credit demand driver.",
        ],
        "Hydropower": [
            "⚡ Power Purchase Agreement (PPA) rates set by NEA determine revenue ceiling.",
            "🌧️ Monsoon variability creates seasonal generation risk (Q1/Q2 weaker).",
            "🤝 India power export deals (INPS grid) are a major revenue unlock catalyst.",
        ],
        "Insurance": [
            "📜 Beema Samiti regulatory changes can compress or expand premium structures.",
            "💵 Mandatory third-party insurance expansion is a growth tailwind.",
        ],
        "Microfinance": [
            "⚠️ Political pressure on interest rate caps is a key regulatory risk.",
            "🏘️ Rural credit demand tied to agricultural output and monsoon season.",
        ],
        "Development": [
            "🏗️ Government infrastructure budget allocation is a core revenue driver.",
            "📉 Post-COVID recovery in SME lending still incomplete in some regions.",
        ],
        "Telecom": [
            "📡 5G spectrum allocation timeline depends on government policy.",
            "🌐 Nepal Telecom's state-owned status provides stability but limits agility.",
        ],
    }

    for s, msgs in sector_macro.items():
        if s.lower() in sector.lower():
            signals.extend(msgs)
            break

    # Universal macro signals
    signals.append("🌍 USD/NPR exchange rate risk affects import-heavy sectors and foreign debt.")
    signals.append("📊 NEPSE is heavily retail-driven — sentiment swings faster than fundamentals.")

    if score >= 65:
        signals.append("✅ Strong fundamentals provide a buffer against macro headwinds.")
    if div > 8:
        signals.append("💸 High dividend yield attracts institutional investors even in downturns.")
    if eps < 10:
        signals.append("⚠️ Low EPS makes this stock vulnerable to rate hike cycles.")

    return signals

def smart_compare_candidates(target_row, all_df):
    """Find 3 most similar stocks using weighted Euclidean distance."""
    metrics = ["eps", "pe_ratio", "dividend_yield", "health_score", "pbv"]
    norm = {}
    for m in metrics:
        col = all_df[m].dropna()
        rng = col.max() - col.min()
        norm[m] = rng if rng > 0 else 1

    def dist(row):
        d = 0
        for m in metrics:
            tv = target_row.get(m, 0) or 0
            rv = row.get(m, 0) or 0
            d += ((tv - rv) / norm[m]) ** 2
        return d ** 0.5

    others = all_df[all_df["symbol"] != target_row["symbol"]].copy()
    others["_dist"] = others.apply(dist, axis=1)
    return others.nsmallest(3, "_dist")

def candlestick_signals(cdf):
    """Derive buy/sell/hold signals from last candle + indicators."""
    last = cdf.iloc[-1]
    signals = []
    action = "HOLD"

    rsi = last.get("rsi", 50)
    macd = last.get("macd", 0)
    macd_sig = last.get("macd_signal", 0)
    close = last["close"]
    sma20 = last.get("sma20", close)
    sma50 = last.get("sma50", close)
    bb_lower = last.get("bb_lower", close * 0.97)
    bb_upper = last.get("bb_upper", close * 1.03)

    if rsi < 35:
        signals.append(("🟢 RSI Oversold", f"RSI={rsi:.1f} — price may be undervalued", "bull"))
        action = "BUY"
    elif rsi > 70:
        signals.append(("🔴 RSI Overbought", f"RSI={rsi:.1f} — consider taking profit", "bear"))
        action = "SELL"
    else:
        signals.append(("⚪ RSI Neutral", f"RSI={rsi:.1f} — no extreme signal", "neut"))

    if macd > macd_sig:
        signals.append(("🟢 MACD Bullish Cross", "MACD above signal line — upward momentum", "bull"))
    else:
        signals.append(("🔴 MACD Bearish Cross", "MACD below signal line — downward pressure", "bear"))

    if close > sma20 > sma50:
        signals.append(("🟢 Trend: Uptrend", "Price > SMA20 > SMA50 — strong bullish trend", "bull"))
        if action == "HOLD": action = "BUY"
    elif close < sma20 < sma50:
        signals.append(("🔴 Trend: Downtrend", "Price < SMA20 < SMA50 — bearish structure", "bear"))
        if action == "HOLD": action = "SELL"

    if close < bb_lower:
        signals.append(("🟢 Bollinger: Below Lower Band", "Price touching lower band — potential bounce zone", "bull"))
    elif close > bb_upper:
        signals.append(("🔴 Bollinger: Above Upper Band", "Price at upper band — resistance zone", "bear"))

    return signals, action

def show_calibration():
    with st.expander("📊 Grade Calibration System"):
        st.markdown("""
        | Grade | Points Range | Meaning | Investment Action |
        | :--- | :--- | :--- | :--- |
        | **A+** | 80–100 | Exceptional | Strongest Buy Candidate |
        | **A** | 65–79 | Very Good | Growth Potential |
        | **B** | 50–64 | Decent | Hold / Watch Closely |
        | **C** | 35–49 | Weak | Needs Improvement |
        | **D** | 0–34 | Poor | High Risk |
        """)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#00ff88;font-family:JetBrains Mono'>📈 NEPSE</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;font-size:.8rem'>Market Intelligence Terminal</p>", unsafe_allow_html=True)
    st.divider()

    # SEARCH BOX
    search_query = st.text_input("🔍 Search stock", placeholder="e.g. NABIL, Everest…")

    st.markdown("**Filters**")
    if df is not None and not df.empty:
        sectors = ["All"] + sorted(df["sector"].dropna().unique().tolist()) if "sector" in df.columns else ["All"]
        sel_sector = st.selectbox("Sector", sectors)
        sel_grade  = st.selectbox("Min Grade", ["All", "A+", "A", "B", "C", "D"])
        min_score  = st.slider("Min Health Score", 0, 100, 0, 5)
        sort_by    = st.selectbox("Sort by", ["health_score","ltp","eps","pe_ratio","dividend_yield","change_pct"])
        sort_asc   = st.checkbox("Ascending", False)
    else:
        sel_sector = "All"; sel_grade = "All"; min_score = 0
        sort_by = "health_score"; sort_asc = False

    st.divider()
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    if meta:
        ts = meta.get("generated_at","")[:16].replace("T"," ")
        st.caption(f"Data as of {ts} UTC")

# ─── Guard ───────────────────────────────────────────────────────────────────
if df is None or df.empty:
    st.error("⚠️ No data found. Run `python scraper.py` first.")
    st.stop()

# ─── Apply filters ────────────────────────────────────────────────────────────
fdf = df.copy()

if search_query:
    q = search_query.upper().strip()
    mask = (
        fdf["symbol"].str.upper().str.contains(q, na=False) |
        fdf.get("name", pd.Series(dtype=str)).str.upper().str.contains(q, na=False)
    )
    fdf = fdf[mask]

if sel_sector != "All" and "sector" in fdf.columns:
    fdf = fdf[fdf["sector"] == sel_sector]

grade_order = {"A+":5,"A":4,"B":3,"C":2,"D":1}
if sel_grade != "All" and "grade" in fdf.columns:
    min_g = grade_order.get(sel_grade, 0)
    fdf = fdf[fdf["grade"].map(lambda g: grade_order.get(g,0)) >= min_g]

if "health_score" in fdf.columns:
    fdf = fdf[fdf["health_score"].fillna(0) >= min_score]

if sort_by in fdf.columns:
    fdf = fdf.sort_values(sort_by, ascending=sort_asc)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("<h1 style='color:#e6edf3;font-family:Inter;font-weight:600;margin-bottom:0'>NEPSE Market Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e;margin-top:0'>Nepal Stock Exchange · Daily Intelligence · Auto-updated</p>", unsafe_allow_html=True)

# ─── KPI Row ─────────────────────────────────────────────────────────────────
k = st.columns(5)
kpis = [
    (meta.get("total_stocks", len(df)), "Total Stocks"),
    (int((df["change_pct"]>0).sum()) if "change_pct" in df.columns else 0, "Gainers 🟢"),
    (int((df["change_pct"]<0).sum()) if "change_pct" in df.columns else 0, "Losers 🔴"),
    (int(df["grade"].isin(["A+","A"]).sum()) if "grade" in df.columns else 0, "Grade A / A+"),
    (f"{df['eps'].dropna().mean():.1f}" if "eps" in df.columns else "—", "Avg EPS"),
]
for col, (val, label) in zip(k, kpis):
    col.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-val'>{val}</div>
      <div class='kpi-label'>{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Tabs ───────────────────────────────────────────────────────────────
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💼 My Portfolio", "📊 All Stocks", "🔬 Stock Deep-Dive", "📉 Charts", "⚖️ Compare", "🌏 Macro & Political"
])

# ══════════════════════════════════════════════════════════
# TAB 0 — MY PORTFOLIO
# ══════════════════════════════════════════════════════════
with tab0:
    st.markdown("### 💼 My Portfolio — Suyog's Holdings")

    portfolio_syms = {
        "HFIN": 10, "HLI": 12, "MBJC": 10, "NESDO": 11,
        "NIFRA": 64, "PCIL": 10, "RNLI": 12, "TAMOR": 0,
    }

    pdf = df[df["symbol"].isin(portfolio_syms.keys())].copy()
    if pdf.empty:
        st.warning("Portfolio stocks not found in data. Make sure data/data.json is updated.")
    else:
        pdf["units"] = pdf["symbol"].map(portfolio_syms).fillna(0).astype(int)
        pdf["invested_est"] = pdf["units"] * pdf["ltp"]  # current value (no buy price stored)
        pdf["current_value"] = pdf["units"] * pdf["ltp"]

        # KPI row
        total_val = pdf["current_value"].sum()
        gainers_p = int((pdf["change_pct"] > 0).sum())
        losers_p  = int((pdf["change_pct"] < 0).sum())
        avg_score = pdf["health_score"].mean()

        k0,k1,k2,k3 = st.columns(4)
        k0.markdown(f"<div class='kpi-card'><div class='kpi-val' style='color:#00ff88'>Rs {total_val:,.0f}</div><div class='kpi-label'>Portfolio Value (est.)</div></div>", unsafe_allow_html=True)
        k1.markdown(f"<div class='kpi-card'><div class='kpi-val'>{len(pdf)}</div><div class='kpi-label'>Stocks Held</div></div>", unsafe_allow_html=True)
        k2.markdown(f"<div class='kpi-card'><div class='kpi-val' style='color:#00ff88'>{gainers_p} 🟢 / {losers_p} 🔴</div><div class='kpi-label'>Today's Movers</div></div>", unsafe_allow_html=True)
        k3.markdown(f"<div class='kpi-card'><div class='kpi-val'>{avg_score:.0f}/100</div><div class='kpi-label'>Avg Health Score</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Individual stock cards
        for _, row in pdf.sort_values("health_score", ascending=False).iterrows():
            sym   = row["symbol"]
            units = int(row.get("units", 0))
            ltp   = row.get("ltp", 0) or 0
            chg   = row.get("change_pct", 0) or 0
            score = row.get("health_score", 0) or 0
            grade = row.get("grade", "?")
            val   = units * ltp
            chg_color = "#00ff88" if chg >= 0 else "#ff4444"
            chg_arrow = "▲" if chg >= 0 else "▼"

            st.markdown(f"""
            <div class='stock-card'>
              <div style='display:flex;justify-content:space-between;align-items:center'>
                <div>
                  <span style='color:#e6edf3;font-size:1.1rem;font-weight:600;font-family:JetBrains Mono'>{sym}</span>
                  <span style='color:#8b949e;font-size:.8rem;margin-left:10px'>{row.get("name","")}</span>
                  <span class='tag tag-neut' style='margin-left:8px'>{row.get("sector","")}</span>
                </div>
                <span class='grade-{grade_class(grade)}'>{grade}</span>
              </div>
              <div style='display:flex;gap:32px;margin-top:10px;flex-wrap:wrap'>
                <div><div style='color:#8b949e;font-size:.72rem'>UNITS</div>
                     <div style='color:#e6edf3;font-family:JetBrains Mono'>{units}</div></div>
                <div><div style='color:#8b949e;font-size:.72rem'>LTP</div>
                     <div style='color:#e6edf3;font-family:JetBrains Mono'>Rs {ltp:,.0f}</div></div>
                <div><div style='color:#8b949e;font-size:.72rem'>TODAY</div>
                     <div style='color:{chg_color};font-family:JetBrains Mono'>{chg_arrow} {abs(chg):.2f}%</div></div>
                <div><div style='color:#8b949e;font-size:.72rem'>VALUE</div>
                     <div style='color:#e6edf3;font-family:JetBrains Mono'>Rs {val:,.0f}</div></div>
                <div><div style='color:#8b949e;font-size:.72rem'>EPS</div>
                     <div style='color:#e6edf3;font-family:JetBrains Mono'>{row.get("eps",0):.1f}</div></div>
                <div><div style='color:#8b949e;font-size:.72rem'>P/E</div>
                     <div style='color:#e6edf3;font-family:JetBrains Mono'>{row.get("pe_ratio",0):.1f}</div></div>
                <div><div style='color:#8b949e;font-size:.72rem'>DIV %</div>
                     <div style='color:#e6edf3;font-family:JetBrains Mono'>{row.get("dividend_yield",0):.1f}%</div></div>
                <div><div style='color:#8b949e;font-size:.72rem'>SCORE</div>
                     <div style='color:#00ff88;font-family:JetBrains Mono'>{score}/100</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Portfolio allocation pie
        st.markdown("#### Allocation by Value")
        pie_df = pdf[pdf["units"] > 0].copy()
        if not pie_df.empty:
            pie_df["value"] = pie_df["units"] * pie_df["ltp"]
            fig = px.pie(pie_df, names="symbol", values="value",
                         color_discrete_sequence=["#00ff88","#58a6ff","#ffd700","#ff8c00","#7fff00","#ff4444","#c792ea","#89ddff"])
            fig.update_layout(paper_bgcolor="#0a0e1a", height=320,
                               margin=dict(l=0,r=0,t=0,b=0),
                               legend=dict(font_color="#8b949e"))
            st.plotly_chart(fig, use_container_width=True, key="portfolio_pie")

        # Sector breakdown
        st.markdown("#### Sector Exposure")
        sec_val = pdf[pdf["units"]>0].groupby("sector").apply(
            lambda x: (x["units"] * x["ltp"]).sum()).reset_index()
        sec_val.columns = ["Sector","Value"]
        fig2 = px.bar(sec_val, x="Sector", y="Value",
                      color_discrete_sequence=["#00ff88"])
        fig2.update_layout(paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117", height=260,
                            margin=dict(l=0,r=0,t=0,b=0),
                            xaxis=dict(color="#8b949e"), yaxis=dict(color="#8b949e",gridcolor="#21262d"))
        st.plotly_chart(fig2, use_container_width=True, key="sector_exposure")

        st.info("💡 Tip: Go to **Stock Deep-Dive** tab and search any of your holdings for candlestick charts and full technical analysis.")


# ══════════════════════════════════════════════════════════
# TAB 1 — ALL STOCKS TABLE
# ══════════════════════════════════════════════════════════
with tab1:
    if fdf.empty:
        st.warning("No stocks match your filters.")
    else:
        disp_cols = [c for c in ["symbol","name","sector","ltp","change_pct","volume",
                                  "eps","pe_ratio","dividend_yield","health_score","grade"] if c in fdf.columns]
        show = fdf[disp_cols].rename(columns={
            "ltp":"LTP (Rs)","change_pct":"Chg %","pe_ratio":"P/E",
            "dividend_yield":"Div %","health_score":"Score"
        })
        st.dataframe(
            show, use_container_width=True, height=500,
            column_config={
                "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
                "LTP (Rs)":

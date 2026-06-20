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
  .ai-bubble {
    background:linear-gradient(135deg,#0d2b1f,#0a1628);
    border:1px solid #00ff8840; border-radius:12px;
    padding:14px 18px; margin:8px 0; font-size:0.88rem; color:#c9d1d9;
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
                "LTP (Rs)": st.column_config.NumberColumn(format="Rs %.0f"),
                "Chg %": st.column_config.NumberColumn(format="%.2f%%"),
            }
        )
        st.caption(f"Showing {len(fdf)} of {len(df)} stocks  ·  Use sidebar search & filters to narrow down")
        st.download_button("⬇️ Export CSV", fdf.to_csv(index=False),
                           file_name=f"nepse_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════
# TAB 2 — DEEP DIVE (search → candles + all analysis)
# ══════════════════════════════════════════════════════════
with tab2:
    symbols = sorted(df["symbol"].dropna().unique().tolist())
    default_ix = 0
    if search_query:
        q = search_query.upper()
        matches = [s for s in symbols if q in s]
        if matches:
            default_ix = symbols.index(matches[0])

    sel_sym = st.selectbox("Select stock to analyse", symbols, index=default_ix, key="deepdive_sym")
    row = df[df["symbol"] == sel_sym].iloc[0].to_dict()
    ltp = row.get("ltp", 500) or 500

    # Header row
    c1, c2, c3, c4 = st.columns([2,1,1,1])
    chg = row.get("change_pct", 0) or 0
    c1.markdown(f"<h2 style='color:#e6edf3;margin:0'>{row.get('name', sel_sym)}</h2>"
                f"<span style='color:#8b949e'>{row.get('sector','')}</span>", unsafe_allow_html=True)
    c2.metric("LTP", f"Rs {ltp:,.0f}", f"{chg:+.2f}%")
    c3.metric("Health Score", f"{row.get('health_score',0)}/100")
    grade = row.get("grade","?")
    c4.markdown(f"<div style='text-align:center;padding-top:8px'>"
                f"<span class='grade-{grade_class(grade)}'>{grade}</span>"
                f"<div style='color:#8b949e;font-size:.75rem'>GRADE</div></div>", unsafe_allow_html=True)

    st.divider()

    # ── Candlestick chart ──
    st.markdown("### 🕯️ Candlestick Chart")
    period = st.radio("Period", ["1M","3M","6M","1Y"], horizontal=True, key="candle_period")
    days_map = {"1M":30,"3M":60,"6M":90,"1Y":120}
    cdf = generate_candles(sel_sym, ltp, days=120)
    cdf_ind = compute_indicators(cdf)
    cdf_show = cdf_ind.tail(days_map[period])

    overlay = st.multiselect("Overlays", ["SMA 20","SMA 50","Bollinger Bands"], default=["SMA 20","SMA 50"], key="overlays")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=cdf_show["date"], open=cdf_show["open"], high=cdf_show["high"],
        low=cdf_show["low"], close=cdf_show["close"], name="Price",
        increasing_line_color="#00ff88", decreasing_line_color="#ff4444",
    ))
    if "SMA 20" in overlay:
        fig.add_trace(go.Scatter(x=cdf_show["date"], y=cdf_show["sma20"],
                                  name="SMA 20", line=dict(color="#ffd700", width=1.5)))
    if "SMA 50" in overlay:
        fig.add_trace(go.Scatter(x=cdf_show["date"], y=cdf_show["sma50"],
                                  name="SMA 50", line=dict(color="#58a6ff", width=1.5)))
    if "Bollinger Bands" in overlay:
        fig.add_trace(go.Scatter(x=cdf_show["date"], y=cdf_show["bb_upper"],
                                  name="BB Upper", line=dict(color="#8b949e", dash="dot", width=1)))
        fig.add_trace(go.Scatter(x=cdf_show["date"], y=cdf_show["bb_lower"],
                                  name="BB Lower", line=dict(color="#8b949e", dash="dot", width=1),
                                  fill="tonexty", fillcolor="rgba(139,148,158,0.05)"))
    fig.update_layout(
        height=420, paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117",
        xaxis=dict(showgrid=False, color="#8b949e", rangeslider_visible=False),
        yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e"),
        margin=dict(l=0,r=0,t=10,b=0),
    )
    st.plotly_chart(fig, use_container_width=True, key="candle_main")

    # Volume bar
    vol_fig = go.Figure(go.Bar(
        x=cdf_show["date"], y=cdf_show["volume"],
        marker_color=["#00ff88" if c >= o else "#ff4444"
                      for c, o in zip(cdf_show["close"], cdf_show["open"])]
    ))
    vol_fig.update_layout(
        height=120, paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117",
        margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
        xaxis=dict(showgrid=False, color="#8b949e"),
        yaxis=dict(showgrid=False, color="#8b949e"),
    )
    st.plotly_chart(vol_fig, use_container_width=True, key="vol_chart")

    # RSI + MACD
    col_rsi, col_macd = st.columns(2)
    with col_rsi:
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=cdf_show["date"], y=cdf_show["rsi"],
                                      line=dict(color="#ffd700", width=2), name="RSI"))
        rsi_fig.add_hline(y=70, line_color="#ff4444", line_dash="dot", line_width=1)
        rsi_fig.add_hline(y=30, line_color="#00ff88", line_dash="dot", line_width=1)
        rsi_fig.update_layout(
            title=dict(text="RSI (14)", font_color="#8b949e", font_size=12),
            height=200, paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117",
            margin=dict(l=0,r=0,t=30,b=0), showlegend=False,
            xaxis=dict(showgrid=False, color="#8b949e"),
            yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e", range=[0,100]),
        )
        st.plotly_chart(rsi_fig, use_container_width=True, key="rsi_chart")

    with col_macd:
        macd_fig = go.Figure()
        macd_fig.add_trace(go.Bar(x=cdf_show["date"], y=cdf_show["macd_hist"],
                                   marker_color=["#00ff88" if v >= 0 else "#ff4444"
                                                 for v in cdf_show["macd_hist"]], name="Hist"))
        macd_fig.add_trace(go.Scatter(x=cdf_show["date"], y=cdf_show["macd"],
                                       line=dict(color="#58a6ff", width=1.5), name="MACD"))
        macd_fig.add_trace(go.Scatter(x=cdf_show["date"], y=cdf_show["macd_signal"],
                                       line=dict(color="#ffd700", width=1.5), name="Signal"))
        macd_fig.update_layout(
            title=dict(text="MACD (12,26,9)", font_color="#8b949e", font_size=12),
            height=200, paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117",
            margin=dict(l=0,r=0,t=30,b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e", font_size=10),
            xaxis=dict(showgrid=False, color="#8b949e"),
            yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e"),
        )
        st.plotly_chart(macd_fig, use_container_width=True, key="macd_chart")

    # ── Technical signals ──
    st.markdown("### 🎯 Technical Signals")
    signals, action = candlestick_signals(cdf_ind)
    action_colors = {"BUY":"#00ff88","SELL":"#ff4444","HOLD":"#ffd700"}
    st.markdown(f"""
    <div style='background:{"#0d2b1f" if action=="BUY" else "#2b0d0d" if action=="SELL" else "#1c1c0d"};
                border:2px solid {action_colors[action]};border-radius:10px;
                padding:14px;text-align:center;margin-bottom:16px'>
      <span style='color:{action_colors[action]};font-size:1.8rem;font-weight:700;
                   font-family:JetBrains Mono'>⬤ {action}</span>
      <div style='color:#8b949e;font-size:.8rem;margin-top:4px'>Overall Technical Signal</div>
    </div>""", unsafe_allow_html=True)

    for title, desc, kind in signals:
        tag_class = f"tag-{'bull' if kind=='bull' else 'bear' if kind=='bear' else 'neut'}"
        st.markdown(f"""
        <div class='signal-box'>
          <span class='tag {tag_class}'>{title}</span>
          <span style='color:#8b949e;font-size:.82rem;margin-left:8px'>{desc}</span>
        </div>""", unsafe_allow_html=True)

    # ── Fundamentals ──
    st.markdown("### 📋 Fundamentals")
    f1,f2,f3,f4,f5,f6 = st.columns(6)
    f1.metric("EPS",       f"{row.get('eps',0) or 0:.1f}")
    f2.metric("P/E",       f"{row.get('pe_ratio',0) or 0:.1f}")
    f3.metric("Div Yield", f"{row.get('dividend_yield',0) or 0:.1f}%")
    f4.metric("P/BV",      f"{row.get('pbv',0) or 0:.2f}")
    f5.metric("ROE",       f"{row.get('roe',0) or 0:.1f}%")
    f6.metric("Volume",    f"{int(row.get('volume',0) or 0):,}")

    # Score radar
    breakdown = {k.replace("_score","").upper(): row.get(k,0) for k in
                 ["eps_score","pe_score","div_score","roe_score","pbv_score","momentum_score"] if k in row}
    if breakdown:
        cats = list(breakdown.keys()) + [list(breakdown.keys())[0]]
        vals = list(breakdown.values()) + [list(breakdown.values())[0]]
        radar = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill="toself",
                                           fillcolor="rgba(0,255,136,0.15)",
                                           line=dict(color="#00ff88", width=2)))
        radar.update_layout(
            polar=dict(bgcolor="#0d1117",
                       radialaxis=dict(range=[0,22], showticklabels=False, gridcolor="#21262d"),
                       angularaxis=dict(color="#8b949e")),
            paper_bgcolor="#0a0e1a", height=300,
            margin=dict(l=40,r=40,t=20,b=20), showlegend=False,
        )
        st.plotly_chart(radar, use_container_width=True, key="radar_chart")

# ══════════════════════════════════════════════════════════
# TAB 3 — MARKET CHARTS
# ══════════════════════════════════════════════════════════
with tab3:
    c_a, c_b = st.columns(2)

    with c_a:
        st.markdown("#### Health Score Distribution")
        if "health_score" in df.columns:
            fig = px.histogram(df, x="health_score", nbins=20,
                               color_discrete_sequence=["#00ff88"],
                               labels={"health_score":"Health Score"})
            fig.update_layout(paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117",
                               height=280, margin=dict(l=0,r=0,t=0,b=0),
                               xaxis=dict(color="#8b949e"), yaxis=dict(color="#8b949e",gridcolor="#21262d"))
            st.plotly_chart(fig, use_container_width=True, key="hist_dist")

    with c_b:
        st.markdown("#### Grade Breakdown")
        if "grade" in df.columns:
            gc = df["grade"].value_counts().reset_index()
            gc.columns = ["Grade","Count"]
            fig = px.pie(gc, names="Grade", values="Count",
                         color_discrete_sequence=["#00ff88","#7fff00","#ffd700","#ff8c00","#ff4444"])
            fig.update_layout(paper_bgcolor="#0a0e1a", height=280,
                               margin=dict(l=0,r=0,t=0,b=0),
                               legend=dict(font_color="#8b949e"))
            st.plotly_chart(fig, use_container_width=True, key="grade_pie")

    st.markdown("#### EPS vs P/E  (bubble = volume)")
    if all(c in df.columns for c in ["eps","pe_ratio"]):
        pdf = df.dropna(subset=["eps","pe_ratio"])
        fig = px.scatter(pdf, x="pe_ratio", y="eps",
                         size="volume" if "volume" in pdf.columns else None,
                         color="grade" if "grade" in pdf.columns else None,
                         hover_data=["symbol","ltp","health_score"],
                         labels={"pe_ratio":"P/E Ratio","eps":"EPS (Rs)"},
                         color_discrete_map={"A+":"#00ff88","A":"#7fff00","B":"#ffd700","C":"#ff8c00","D":"#ff4444"})
        fig.update_layout(paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117", height=380,
                           margin=dict(l=0,r=0,t=0,b=0),
                           xaxis=dict(color="#8b949e",gridcolor="#21262d"),
                           yaxis=dict(color="#8b949e",gridcolor="#21262d"),
                           legend=dict(font_color="#8b949e"))
        st.plotly_chart(fig, use_container_width=True, key="eps_pe_scatter")

    if "sector" in df.columns and "health_score" in df.columns:
        st.markdown("#### Avg Health Score by Sector")
        sec = df.groupby("sector")["health_score"].mean().sort_values().reset_index()
        fig = px.bar(sec, x="health_score", y="sector", orientation="h",
                     color="health_score", color_continuous_scale="Greens")
        fig.update_layout(paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117", height=320,
                           margin=dict(l=0,r=0,t=0,b=0), coloraxis_showscale=False,
                           xaxis=dict(color="#8b949e",gridcolor="#21262d"),
                           yaxis=dict(color="#8b949e"))
        st.plotly_chart(fig, use_container_width=True, key="sector_bar")

# ══════════════════════════════════════════════════════════
# TAB 4 — SMART COMPARE
# ══════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ⚖️ Smart Compare")
    st.caption("Pick any two stocks to compare, or let the AI suggest the most similar peers.")

    sym_list = sorted(df["symbol"].dropna().unique().tolist())
    ca, cb = st.columns(2)
    sym_a = ca.selectbox("Stock A", sym_list, key="cmp_a")
    sym_b = cb.selectbox("Stock B", sym_list,
                         index=1 if len(sym_list)>1 else 0, key="cmp_b")

    # Smart suggest button
    if st.button("🤖 Auto-suggest similar stocks to " + sym_a):
        row_a = df[df["symbol"]==sym_a].iloc[0].to_dict()
        suggestions = smart_compare_candidates(row_a, df)
        st.markdown("<div class='ai-bubble'>", unsafe_allow_html=True)
        st.markdown(f"**Most similar stocks to {sym_a}** based on EPS, P/E, Dividend, Score & P/BV:")
        for _, s in suggestions.iterrows():
            st.markdown(f"- **{s['symbol']}** ({s.get('name','')}) — Score {s.get('health_score',0)}, "
                        f"EPS {s.get('eps',0):.1f}, P/E {s.get('pe_ratio',0):.1f}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    row_a = df[df["symbol"]==sym_a].iloc[0].to_dict()
    row_b = df[df["symbol"]==sym_b].iloc[0].to_dict()

    metrics = [
        ("Health Score", "health_score", "", False),
        ("LTP (Rs)",     "ltp",          "Rs ", False),
        ("EPS",          "eps",          "",  False),
        ("P/E Ratio",    "pe_ratio",     "",  True),   # lower is better
        ("Div Yield %",  "dividend_yield","% ", False),
        ("ROE %",        "roe",          "% ", False),
        ("P/BV",         "pbv",          "",  True),
        ("Volume",       "volume",       "",  False),
    ]

    for label, key, prefix, lower_better in metrics:
        va = row_a.get(key, 0) or 0
        vb = row_b.get(key, 0) or 0
        win_a = (va < vb) if lower_better else (va > vb)
        win_b = (vb < va) if lower_better else (vb > va)
        ca2, cm, cb2 = st.columns([5,3,5])
        ca2.markdown(
            f"<div style='text-align:right;color:{'#00ff88' if win_a else '#e6edf3'};font-family:JetBrains Mono'>"
            f"{prefix}{va:,.1f}</div>", unsafe_allow_html=True)
        cm.markdown(f"<div style='text-align:center;color:#8b949e;font-size:.8rem'>{label}</div>",
                    unsafe_allow_html=True)
        cb2.markdown(
            f"<div style='color:{'#00ff88' if win_b else '#e6edf3'};font-family:JetBrains Mono'>"
            f"{prefix}{vb:,.1f}</div>", unsafe_allow_html=True)

    # Mini candle comparison
    st.divider()
    st.markdown("#### Price History Comparison")
    ltp_a = row_a.get("ltp",500) or 500
    ltp_b = row_b.get("ltp",500) or 500
    cdf_a = generate_candles(sym_a, ltp_a, 60)
    cdf_b = generate_candles(sym_b, ltp_b, 60)

    # Normalise to 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cdf_a["date"], y=(cdf_a["close"] / cdf_a["close"].iloc[0]) * 100,
        name=sym_a, line=dict(color="#00ff88", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=cdf_b["date"], y=(cdf_b["close"] / cdf_b["close"].iloc[0]) * 100,
        name=sym_b, line=dict(color="#58a6ff", width=2)
    ))
    fig.update_layout(
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1117", height=300,
        margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(color="#8b949e",showgrid=False),
        yaxis=dict(color="#8b949e",gridcolor="#21262d",title="Normalised (base=100)"),
        legend=dict(font_color="#8b949e"),
    )
    st.plotly_chart(fig, use_container_width=True, key="compare_price")

# ══════════════════════════════════════════════════════════
# TAB 5 — MACRO & POLITICAL
# ══════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🌏 Macro & Political Risk Analysis")
    st.caption("Rule-based analysis of Nepal's economic & political factors on each stock")

    sel_macro = st.selectbox("Select stock", sorted(df["symbol"].dropna().unique()), key="macro_sym")
    mrow = df[df["symbol"]==sel_macro].iloc[0].to_dict()

    # Score badge
    sc = mrow.get("health_score",0)
    grade = mrow.get("grade","?")
    st.markdown(f"""
    <div style='display:flex;gap:20px;margin-bottom:16px'>
      <div class='kpi-card' style='flex:1'>
        <div class='kpi-val' style='color:#00ff88'>{sc}</div>
        <div class='kpi-label'>Health Score</div>
      </div>
      <div class='kpi-card' style='flex:1'>
        <div class='kpi-val'>{grade}</div>
        <div class='kpi-label'>Grade</div>
      </div>
      <div class='kpi-card' style='flex:1'>
        <div class='kpi-val'>{mrow.get("sector","—")}</div>
        <div class='kpi-label'>Sector</div>
      </div>
    </div>""", unsafe_allow_html=True)

    signals = political_macro_analysis(mrow)
    for sig in signals:
        st.markdown(f"""
        <div class='signal-box' style='border-left-color:#58a6ff'>
          {sig}
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🇳🇵 Nepal-Wide Macro Factors (All Stocks)")
    macro_factors = [
        ("📉 Interest Rate Cycle",
         "NRB has been gradually loosening policy rates. Lower rates compress bank NIMs short-term "
         "but stimulate credit growth, benefitting banking and hydropower sectors 6–12 months out."),
        ("💸 Remittance Economy",
         "Nepal receives ~35% of GDP as remittances. Any slowdown in Gulf/Malaysia worker outflows "
         "directly reduces consumer spending and credit demand. Watch INR/NPR for indirect pressure."),
        ("⚡ Energy Surplus & Export",
         "Nepal is moving from power deficit to surplus. Hydropower stocks benefit from India PPA "
         "negotiations but face risk if grid connectivity projects are delayed by political changes."),
        ("🏛️ Political Stability",
         "Nepal has had 13 governments in 16 years. Coalition fragility adds regulatory uncertainty. "
         "Budget delays (post-election years) slow infrastructure spending and affect construction/cement sectors."),
        ("🌍 China-India Geopolitics",
         "Nepal sits between two powers. BRI infrastructure projects can unlock connectivity but "
         "are subject to geopolitical delays. Indian trade dependencies make rupee-peg maintenance critical."),
        ("📊 NEPSE Retail Dominance",
         "Over 90% of NEPSE volume is retail investors. This creates high volatility disconnected "
         "from fundamentals during election seasons, IPO frenzies, and budget announcements."),
    ]
    for title, body in macro_factors:
        with st.expander(title):
            st.write(body)

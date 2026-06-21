"""
NEPSE Market Tracker — v3.0 Quant Trading Terminal
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ══════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NEPSE Terminal v3.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');
  html, body, [data-testid="stApp"] { background:#070913 !important; color:#c9d1d9 !important; font-family:'Inter',sans-serif !important; }
  [data-testid="stSidebar"] { background:#0d111a !important; border-right:1px solid #1f2937; }
  h1,h2,h3,h4 { font-family:'Inter',sans-serif !important; font-weight:600 !important; color:#f0f6fc !important; }
  .kpi-card { background:linear-gradient(135deg,#111625,#0b0e17); border:1px solid #21262d; border-radius:8px; padding:16px; text-align:left; }
  .kpi-val { font-size:1.6rem; font-weight:700; font-family:'JetBrains Mono',monospace; color:#ffffff; }
  .kpi-label { font-size:0.72rem; color:#8b949e; letter-spacing:.08em; text-transform:uppercase; margin-bottom:4px; }
  .stock-card { background:#121824; border:1px solid #21262d; border-radius:8px; padding:14px; margin-bottom:10px; }
  .grade-Ap { color:#00ff88; font-weight:700; } .grade-A { color:#7fff00; font-weight:700; }
  .grade-B { color:#ffd700; font-weight:700; } .grade-C { color:#ff8c00; font-weight:700; }
  .grade-D { color:#ff4444; font-weight:700; }
  .tag { display:inline-block; padding:2px 8px; border-radius:4px; font-size:0.7rem; font-weight:600; margin-right:4px; font-family:'JetBrains Mono',monospace; }
  .tag-bull { background:#0c2b1a; color:#00ff88; border:1px solid #00ff8830; }
  .tag-bear { background:#331212; color:#ff4444; border:1px solid #ff444430; }
  .tag-neut { background:#1a2233; color:#8b949e; border:1px solid #30363d; }
  .signal-box { background:#0b0f19; border-left:3px solid #00ff88; border-radius:4px; padding:12px; margin:8px 0; font-size:0.85rem; color:#c9d1d9; line-height:1.6; }
  div[data-testid="stTab"] button[aria-selected="true"] { color:#00ff88 !important; border-bottom-color:#00ff88 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 2. SESSION STATE
# ══════════════════════════════════════════════════════════
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "HFIN":  {"shares": 10,  "avg_cost": 148.0},
        "HLI":   {"shares": 12,  "avg_cost": 620.0},
        "MBJC":  {"shares": 10,  "avg_cost": 365.0},
        "NESDO": {"shares": 11,  "avg_cost": 1420.0},
        "NIFRA": {"shares": 64,  "avg_cost": 210.0},
        "PCIL":  {"shares": 10,  "avg_cost": 980.0},
        "RNLI":  {"shares": 12,  "avg_cost": 1150.0},
        "TAMOR": {"shares": 10,  "avg_cost": 285.0},
    }
if "active_symbol" not in st.session_state:
    st.session_state.active_symbol = "HFIN"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ══════════════════════════════════════════════════════════
# 3. AUTH
# ══════════════════════════════════════════════════════════
_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
if _PASSWORD and not st.session_state.authenticated:
    st.markdown("""
    <div style='text-align:center;margin-top:10vh'>
      <h1 style='color:#00ff88;font-family:JetBrains Mono'>📈 NEPSE TERMINAL 3.0</h1>
      <p style='color:#8b949e'>Nepal Stock Market Intelligence Suite</p>
    </div>""", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        pw = st.text_input("Password", type="password", placeholder="Enter password…")
        if st.button("Access Terminal →", use_container_width=True):
            if pw == _PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Wrong password.")
    st.stop()

# ══════════════════════════════════════════════════════════
# 4. DATA LOADER
# ══════════════════════════════════════════════════════════
DATA_PATH = next(
    (p for p in [Path("data/data.json"), Path("data.json")] if p.exists()),
    Path("data/data.json")
)

@st.cache_data(ttl=300)
def load_data():
    fallback_stocks = [
        {"symbol":"HFIN",  "name":"Himalayan Finance",              "sector":"Finance",      "ltp":148,  "eps":10.2,"pe_ratio":14.5,"dividend_yield":4.5, "pbv":1.41,"health_score":40,"grade":"C","change_pct":0.6, "volume":6200},
        {"symbol":"HLI",   "name":"Himalayan Life Insurance",        "sector":"Insurance",    "ltp":620,  "eps":38.5,"pe_ratio":16.1,"dividend_yield":6.0, "pbv":2.18,"health_score":52,"grade":"B","change_pct":-0.5,"volume":4100},
        {"symbol":"MBJC",  "name":"Marsyangdi Jalvidhyut",          "sector":"Hydropower",   "ltp":365,  "eps":21.4,"pe_ratio":17.1,"dividend_yield":5.5, "pbv":2.05,"health_score":47,"grade":"C","change_pct":1.1, "volume":9800},
        {"symbol":"NESDO", "name":"Nerude Laghubitta",               "sector":"Microfinance", "ltp":1420, "eps":88.0,"pe_ratio":16.1,"dividend_yield":7.0, "pbv":2.73,"health_score":53,"grade":"B","change_pct":0.2, "volume":2200},
        {"symbol":"NIFRA", "name":"Nepal Infrastructure Bank",       "sector":"Development",  "ltp":210,  "eps":14.8,"pe_ratio":14.2,"dividend_yield":5.0, "pbv":1.59,"health_score":37,"grade":"C","change_pct":-1.0,"volume":18500},
        {"symbol":"PCIL",  "name":"Panchakanya Mali Laghubitta",     "sector":"Microfinance", "ltp":980,  "eps":62.5,"pe_ratio":15.7,"dividend_yield":8.0, "pbv":2.39,"health_score":62,"grade":"B","change_pct":0.8, "volume":3100},
        {"symbol":"RNLI",  "name":"Rastriya Nagarik Laghubitta",     "sector":"Microfinance", "ltp":1150, "eps":74.0,"pe_ratio":15.5,"dividend_yield":7.5, "pbv":2.47,"health_score":62,"grade":"B","change_pct":-0.3,"volume":2800},
        {"symbol":"TAMOR", "name":"Tamor Hydropower",                "sector":"Hydropower",   "ltp":285,  "eps":17.2,"pe_ratio":16.6,"dividend_yield":4.8, "pbv":1.84,"health_score":37,"grade":"C","change_pct":1.4, "volume":7400},
        {"symbol":"NABIL", "name":"Nabil Bank",                      "sector":"Banking",      "ltp":1020, "eps":82.5,"pe_ratio":12.4,"dividend_yield":12,  "pbv":1.96,"health_score":74,"grade":"A","change_pct":1.2, "volume":48000},
        {"symbol":"NICA",  "name":"NIC Asia Bank",                   "sector":"Banking",      "ltp":395,  "eps":35.2,"pe_ratio":11.2,"dividend_yield":10,  "pbv":1.79,"health_score":69,"grade":"A","change_pct":0.9, "volume":62000},
        {"symbol":"UPPER", "name":"Upper Tamakoshi",                  "sector":"Hydropower",   "ltp":258,  "eps":16.5,"pe_ratio":15.6,"dividend_yield":5,   "pbv":1.74,"health_score":47,"grade":"C","change_pct":1.5, "volume":38000},
        {"symbol":"ADBL",  "name":"Agriculture Dev Bank",             "sector":"Banking",      "ltp":305,  "eps":28.3,"pe_ratio":10.8,"dividend_yield":8.5, "pbv":1.56,"health_score":67,"grade":"A","change_pct":0.2, "volume":41000},
        {"symbol":"NLICL", "name":"Nepal Life Insurance",             "sector":"Insurance",    "ltp":1280, "eps":95.0,"pe_ratio":13.5,"dividend_yield":14,  "pbv":2.06,"health_score":74,"grade":"A","change_pct":0.7, "volume":15000},
        {"symbol":"CHCL",  "name":"Chilime Hydro",                   "sector":"Hydropower",   "ltp":495,  "eps":29.8,"pe_ratio":16.6,"dividend_yield":7,   "pbv":2.15,"health_score":52,"grade":"B","change_pct":0.5, "volume":18000},
        {"symbol":"SANIMA","name":"Sanima Bank",                     "sector":"Banking",      "ltp":331,  "eps":30.1,"pe_ratio":11.0,"dividend_yield":9,   "pbv":1.58,"health_score":67,"grade":"A","change_pct":-0.3,"volume":34000},
    ]
    if not DATA_PATH.exists():
        return pd.DataFrame(fallback_stocks), {"stocks": fallback_stocks, "market_summary": {"index":2150.45,"change":14.32,"pct_change":0.67,"turnover":4120534200}}
    try:
        with open(DATA_PATH) as f:
            raw = json.load(f)
        stocks = raw.get("stocks", [])
        # Merge fallback symbols not in file
        existing = {s["symbol"] for s in stocks}
        for s in fallback_stocks:
            if s["symbol"] not in existing:
                stocks.append(s)
        df = pd.DataFrame(stocks)
        # Normalise column names
        if "pct_change" not in df.columns and "change_pct" in df.columns:
            df["pct_change"] = df["change_pct"]
        if "change_pct" not in df.columns and "pct_change" in df.columns:
            df["change_pct"] = df["pct_change"]
        raw["stocks"] = stocks
        return df, raw
    except Exception as e:
        st.error(f"Data load error: {e}")
        return pd.DataFrame(fallback_stocks), {}

df, meta = load_data()

# ══════════════════════════════════════════════════════════
# 5. QUANT ENGINES
# ══════════════════════════════════════════════════════════
def generate_candles(symbol, ltp, days=120):
    random.seed(hash(symbol) % 9999)
    price = ltp * 0.95
    data, base_date = [], datetime.today() - timedelta(days=days)
    for i in range(days):
        change = random.gauss(0.0005, 0.015)
        open_p = price
        close_p = price * (1 + change)
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.008))
        low_p  = min(open_p, close_p) * (1 - random.uniform(0, 0.008))
        data.append({"date": base_date + timedelta(days=i),
                     "open": round(open_p,2), "high": round(high_p,2),
                     "low": round(low_p,2),  "close": round(close_p,2),
                     "volume": int(random.uniform(10000,150000))})
        price = close_p
    return pd.DataFrame(data)

def compute_indicators(cdf):
    cdf = cdf.copy()
    cdf["sma20"] = cdf["close"].rolling(20).mean()
    cdf["sma50"] = cdf["close"].rolling(50).mean()
    std20 = cdf["close"].rolling(20).std()
    cdf["bb_upper"] = cdf["sma20"] + 2*std20
    cdf["bb_lower"] = cdf["sma20"] - 2*std20
    delta = cdf["close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    cdf["rsi"] = 100 - (100 / (1 + gain / loss.replace(0, 1e-9)))
    ema12 = cdf["close"].ewm(span=12, adjust=False).mean()
    ema26 = cdf["close"].ewm(span=26, adjust=False).mean()
    cdf["macd"]        = ema12 - ema26
    cdf["macd_signal"] = cdf["macd"].ewm(span=9, adjust=False).mean()
    cdf["macd_hist"]   = cdf["macd"] - cdf["macd_signal"]
    return cdf

def detect_candle_patterns(cdf):
    if len(cdf) < 3:
        return [("⚪ Not enough data","Need at least 3 days of candles.","neut",50)]
    c0,c1,c2 = cdf.iloc[-1], cdf.iloc[-2], cdf.iloc[-3]
    def body(c):       return abs(c["close"]-c["open"])
    def rng(c):        return c["high"]-c["low"]
    def uw(c):         return c["high"]-max(c["close"],c["open"])
    def lw(c):         return min(c["close"],c["open"])-c["low"]
    def bull(c):       return c["close"]>c["open"]
    def bear(c):       return c["close"]<c["open"]
    def doji(c):       return body(c) <= rng(c)*0.1

    patterns = []
    if doji(c0):
        patterns.append(("🔵 Doji","Open and close almost the same price. Market is confused — buyers and sellers equally matched. Wait before acting.","neut",60))
    if lw(c0)>=body(c0)*2 and uw(c0)<=body(c0)*0.3 and c1["close"]<c2["close"]:
        patterns.append(("🟢 Hammer","Price fell hard during the day but buyers pushed it back up before close. Like a rubber ball bouncing off the floor. Good sign — drop may be ending.","bull",72))
    if uw(c0)>=body(c0)*2 and lw(c0)<=body(c0)*0.3 and c1["close"]>c2["close"]:
        patterns.append(("🔴 Shooting Star","Price rose during the day but sellers crushed it back down. Like a rocket running out of fuel. Rise may be ending. Be careful.","bear",70))
    if bull(c0) and uw(c0)<body(c0)*0.05 and lw(c0)<body(c0)*0.05:
        patterns.append(("🟢 Bullish Marubozu","Solid green candle, no wicks. Buyers in complete control all day. Very strong buying pressure.","bull",75))
    if bear(c0) and uw(c0)<body(c0)*0.05 and lw(c0)<body(c0)*0.05:
        patterns.append(("🔴 Bearish Marubozu","Solid red candle, no wicks. Sellers in complete control all day. Very strong selling pressure.","bear",75))
    if bear(c1) and bull(c0) and c0["open"]<c1["close"] and c0["close"]>c1["open"]:
        patterns.append(("🟢 Bullish Engulfing","Today's green candle completely swallowed yesterday's red one. Buyers overpowered sellers in a big way. One of the strongest buy signals.","bull",82))
    if bull(c1) and bear(c0) and c0["open"]>c1["close"] and c0["close"]<c1["open"]:
        patterns.append(("🔴 Bearish Engulfing","Today's red candle completely swallowed yesterday's green one. Sellers overpowered buyers. One of the strongest sell signals.","bear",82))
    if bear(c2) and body(c2)>rng(c2)*0.5 and body(c1)<rng(c1)*0.2 and bull(c0) and c0["close"]>(c2["open"]+c2["close"])/2:
        patterns.append(("🟢 Morning Star","Big red fall → tiny uncertain candle → big green recovery. Like sunrise after a dark night. Very reliable signal that downtrend is ending.","bull",85))
    if bull(c2) and body(c2)>rng(c2)*0.5 and body(c1)<rng(c1)*0.2 and bear(c0) and c0["close"]<(c2["open"]+c2["close"])/2:
        patterns.append(("🔴 Evening Star","Big green rise → tiny uncertain candle → big red fall. Uptrend is likely ending. Consider protecting profits.","bear",85))
    if bull(c0) and bull(c1) and bull(c2) and c0["close"]>c1["close"]>c2["close"]:
        patterns.append(("🟢 Three White Soldiers","Three green candles in a row, each closing higher. Buyers winning for 3 days straight. Very bullish.","bull",88))
    if bear(c0) and bear(c1) and bear(c2) and c0["close"]<c1["close"]<c2["close"]:
        patterns.append(("🔴 Three Black Crows","Three red candles in a row, each closing lower. Sellers winning for 3 days straight. Very bearish.","bear",88))
    if not patterns:
        patterns.append(("⚪ No Clear Pattern","Market moving normally. No strong signal today. Hold and watch.","neut",50))
    return patterns

def get_indicator_signals(cdf):
    last = cdf.iloc[-1]
    signals, bull_pts, bear_pts = [], 0, 0
    rsi      = last.get("rsi", 50)
    macd     = last.get("macd", 0)
    macd_sig = last.get("macd_signal", 0)
    close    = last["close"]
    sma20    = last.get("sma20", close)
    sma50    = last.get("sma50", close)
    bb_lower = last.get("bb_lower", close*0.97)
    bb_upper = last.get("bb_upper", close*1.03)

    if rsi < 35:
        signals.append(("🟢 RSI Oversold", f"RSI={rsi:.0f}. Stock sold too much — like a compressed spring. Usually bounces back up.", "bull")); bull_pts+=2
    elif rsi > 70:
        signals.append(("🔴 RSI Overbought", f"RSI={rsi:.0f}. Too many people bought — stock may pull back. Consider taking profit.", "bear")); bear_pts+=2
    else:
        signals.append(("⚪ RSI Normal", f"RSI={rsi:.0f}. Normal zone, no extreme signal.", "neut"))

    if macd > macd_sig:
        signals.append(("🟢 MACD Bullish", "Fast average above slow — momentum building upward. Buyers accelerating.", "bull")); bull_pts+=2
    else:
        signals.append(("🔴 MACD Bearish", "Fast average below slow — momentum pointing down. Sellers dominating.", "bear")); bear_pts+=2

    if close > sma20 > sma50:
        signals.append(("🟢 Strong Uptrend", "Price > SMA20 > SMA50. Climbing stairs — each step higher. Best condition to hold.", "bull")); bull_pts+=3
    elif close < sma20 < sma50:
        signals.append(("🔴 Strong Downtrend", "Price < SMA20 < SMA50. Going down stairs. Not a good time to buy more.", "bear")); bear_pts+=3
    else:
        signals.append(("🟡 Mixed Trend", "Price between short and long averages. Wait for clearer direction.", "neut"))

    if close < bb_lower:
        signals.append(("🟢 At Price Floor", "Below normal trading range — like a stretched rubber band downward. Often snaps back up.", "bull")); bull_pts+=2
    elif close > bb_upper:
        signals.append(("🔴 At Price Ceiling", "Above normal range — like a stretched rubber band upward. Often snaps back down.", "bear")); bear_pts+=2

    if bull_pts >= 6:   action = "BUY"
    elif bear_pts >= 6: action = "SELL"
    elif bull_pts > bear_pts+1: action = "WEAK BUY"
    elif bear_pts > bull_pts+1: action = "WEAK SELL"
    else: action = "HOLD"
    return signals, action

def political_macro_analysis(row):
    sector = str(row.get("sector",""))
    eps    = row.get("eps",0) or 0
    div    = row.get("dividend_yield",0) or 0
    score  = row.get("health_score",0) or 0
    signals = []
    sector_macro = {
        "Banking":     ["🏛️ NRB policy rates and CRR/SLR fluctuations directly affect bank liquidity.",
                        "📋 Basel III capital adequacy requirements limit aggressive expansion.",
                        "💰 Remittance inflows (~35% of GDP) are the primary deposit driver."],
        "Hydropower":  ["⚡ PPA rates set by NEA create a fixed revenue ceiling.",
                        "🌧️ Monsoon variability creates seasonal output risk in Q1/Q2.",
                        "🤝 India power export deals are a major long-term catalyst."],
        "Insurance":   ["📜 Beema Samiti regulations can compress premium structures.",
                        "💵 Mandatory third-party insurance expansion is a growth tailwind."],
        "Microfinance":["⚠️ Political pressure on interest rate caps is a key regulatory risk.",
                        "🏘️ Rural credit demand tied to agricultural output and monsoon season."],
        "Development": ["🏗️ Government infrastructure budget drives revenue.",
                        "📉 SME lending recovery from COVID still incomplete in some regions."],
        "Finance":     ["🏦 Finance companies face tighter NRB scrutiny than commercial banks.",
                        "📊 Deposit mobilization limits cap growth potential."],
    }
    for s, msgs in sector_macro.items():
        if s.lower() in sector.lower():
            signals.extend(msgs); break
    signals.append("🌍 USD/NPR exchange rate affects import-heavy sectors and foreign debt costs.")
    signals.append("📊 NEPSE is 90%+ retail-driven — sentiment swings fast around elections and budget.")
    if score >= 65: signals.append("✅ Strong fundamentals provide a buffer against macro headwinds.")
    if div > 8:     signals.append("💸 High dividend yield attracts institutional investors even in downturns.")
    if eps < 10:    signals.append("⚠️ Low EPS makes this stock vulnerable to interest rate increases.")
    return signals

def smart_compare_candidates(target_row, all_df):
    metrics = ["eps","pe_ratio","dividend_yield","health_score","pbv"]
    clean = all_df.dropna(subset=[m for m in metrics if m in all_df.columns]).copy()
    if len(clean) <= 1:
        return pd.DataFrame()
    norm = {}
    for m in metrics:
        if m not in clean.columns: continue
        lo, hi = clean[m].min(), clean[m].max()
        norm[m] = (clean[m] - lo) / ((hi-lo) if hi>lo else 1)
    norm_df = pd.DataFrame(norm, index=clean.index)
    try:
        tidx = target_row.name
        tvec = norm_df.loc[tidx]
        clean["_distance"] = norm_df.apply(lambda r: float(np.linalg.norm(r-tvec)), axis=1)
        return clean[clean.index != tidx].sort_values("_distance").head(3)
    except Exception:
        return clean.head(3)

def grade_class(g):
    return {"A+":"Ap","A":"A","B":"B","C":"C","D":"D"}.get(g,"neut")

# ══════════════════════════════════════════════════════════
# 6. MARKET BANNER
# ══════════════════════════════════════════════════════════
m_sum = meta.get("market_summary", {"index":2150.45,"change":14.32,"pct_change":0.67,"turnover":4120534200})
chg_c = "#00ff88" if m_sum.get("change",0) >= 0 else "#ff4444"
st.markdown(f"""
<div style='background:#0d111a;border-bottom:1px solid #1f2937;padding:10px 20px;
            display:flex;gap:40px;align-items:center;margin-bottom:12px'>
  <div><span style='color:#8b949e;font-size:.72rem'>NEPSE INDEX</span><br>
       <span style='font-family:monospace;font-size:1.2rem;font-weight:700'>{m_sum.get("index",0):,}</span></div>
  <div><span style='color:#8b949e;font-size:.72rem'>CHANGE</span><br>
       <span style='font-family:monospace;font-size:1.2rem;font-weight:700;color:{chg_c}'>{m_sum.get("change",0):+,.2f} ({m_sum.get("pct_change",0):+.2f}%)</span></div>
  <div><span style='color:#8b949e;font-size:.72rem'>DAILY TURNOVER</span><br>
       <span style='font-family:monospace;font-size:1.2rem;font-weight:700;color:#ffd700'>NPR {m_sum.get("turnover",0):,}</span></div>
  <div style='margin-left:auto'><span style='color:#8b949e;font-size:.72rem'>TOTAL STOCKS</span><br>
       <span style='font-family:monospace;font-size:1.2rem;font-weight:700'>{len(df)}</span></div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 7. SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🎛️ Terminal Controls")
    search_query = st.text_input("🔍 Search", "", placeholder="Symbol or name…")
    sectors = ["All Sectors"] + sorted(df["sector"].dropna().unique().tolist()) if not df.empty else ["All Sectors"]
    sel_sector = st.selectbox("Sector", sectors)
    min_score  = st.slider("Min Health Score", 0, 100, 0, 5)
    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    if meta:
        ts = meta.get("generated_at","")[:16].replace("T"," ")
        st.caption(f"Data: {ts} UTC" if ts else "Data: demo mode")

# Filter
fdf = df.copy()
if search_query:
    q = search_query.upper()
    fdf = fdf[fdf["symbol"].str.upper().str.contains(q,na=False) |
              fdf.get("name",pd.Series(dtype=str)).str.upper().str.contains(q,na=False)]
if sel_sector != "All Sectors":
    fdf = fdf[fdf["sector"]==sel_sector]
if "health_score" in fdf.columns:
    fdf = fdf[fdf["health_score"].fillna(0) >= min_score]

# ══════════════════════════════════════════════════════════
# 8. TABS
# ══════════════════════════════════════════════════════════
tab_terminal, tab_portfolio, tab_matrix, tab_guide = st.tabs([
    "🖥️ Trading Terminal", "💼 My Portfolio", "📊 Market Analysis", "📖 Score Guide"
])

# ══════════════════════════════════════════════════════════
# TAB 1 — TRADING TERMINAL
# ══════════════════════════════════════════════════════════
with tab_terminal:
    col_list, col_chart = st.columns([1, 2.4])

    with col_list:
        st.markdown("#### 📜 Watchlist")
        if fdf.empty:
            st.info("No stocks match your filters.")
        else:
            for _, row in fdf.sort_values("health_score", ascending=False).iterrows():
                sym  = row.get("symbol","?")
                ltp  = row.get("ltp",0) or 0
                chg  = row.get("pct_change", row.get("change_pct",0)) or 0
                grd  = row.get("grade","?")
                is_active = st.session_state.active_symbol == sym
                bord = "#00ff88" if is_active else "#21262d"
                ctxt = "#00ff88" if chg>=0 else "#ff4444"
                st.markdown(f"""
                <div style='border:1px solid {bord};padding:10px;border-radius:6px;
                            margin-bottom:6px;background:#111625'>
                  <div style='display:flex;justify-content:space-between'>
                    <span style='font-family:monospace;font-weight:bold'>{sym}</span>
                    <span style='color:{ctxt};font-family:monospace'>{chg:+.2f}%</span>
                  </div>
                  <div style='display:flex;justify-content:space-between;font-size:.75rem;
                              color:#8b949e;margin-top:4px'>
                    <span>Rs {ltp:,.0f}</span><span>Grade {grd}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Analyse {sym}", key=f"sel_{sym}", use_container_width=True):
                    st.session_state.active_symbol = sym
                    st.rerun()

    with col_chart:
        sym = st.session_state.active_symbol
        rows = df[df["symbol"]==sym]
        if rows.empty:
            st.info("Select a stock from the watchlist.")
        else:
            row = rows.iloc[0]
            ltp  = row.get("ltp",0) or 0
            chg  = row.get("pct_change", row.get("change_pct",0)) or 0
            chg_c2 = "#00ff88" if chg>=0 else "#ff4444"

            st.markdown(f"""
            <div style='background:#121824;border:1px solid #21262d;padding:16px;
                        border-radius:8px;margin-bottom:14px'>
              <div style='display:flex;align-items:center'>
                <div>
                  <h2 style='margin:0;color:#f0f6fc'>{sym} · {row.get("name","")}</h2>
                  <span style='color:#8b949e;font-size:.85rem'>{row.get("sector","")}</span>
                </div>
                <div style='margin-left:auto;text-align:right'>
                  <span class='grade-{grade_class(row.get("grade","?"))}'>{row.get("grade","?")} Grade</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            m1,m2,m3,m4,m5 = st.columns(5)
            for col2, label, val in [
                (m1,"LTP (NPR)", f"{ltp:,.0f}"),
                (m2,"Change",    f"{chg:+.2f}%"),
                (m3,"EPS",       f"{row.get('eps',0):.1f}"),
                (m4,"P/E",       f"{row.get('pe_ratio',0):.1f}"),
                (m5,"Score",     f"{row.get('health_score',0)}/100"),
            ]:
                col2.markdown(f"<div class='kpi-card'><div class='kpi-label'>{label}</div><div class='kpi-val'>{val}</div></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Chart period selector
            period = st.radio("Period", ["1M","3M","6M","All"], horizontal=True, key="chart_period")
            days_map = {"1M":30,"3M":60,"6M":90,"All":120}
            cdf = compute_indicators(generate_candles(sym, ltp, 120))
            cdf_show = cdf.tail(days_map[period])

            fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                vertical_spacing=0.04, row_heights=[0.6,0.2,0.2])
            # Candles
            fig.add_trace(go.Candlestick(
    x=cdf_show["date"], open=cdf_show["open"], high=cdf_show["high"],
    low=cdf_show["low"], close=cdf_show["close"], name="Price",
    increasing_line_color="#00ff88", decreasing_line_color="#ff4444",
), row=1, col=1)
            # Volume
            vcolors = ["#00ff88" if c>=o else "#ff4444" for c,o in zip(cdf_show["close"],cdf_show["open"])]
            fig.add_trace(go.Bar(x=cdf_show["date"],y=cdf_show["volume"],name="Volume",marker_color=vcolors,showlegend=False), row=2,col=1)
            # MACD
            hcolors = ["#00ff88" if v>=0 else "#ff4444" for v in cdf_show["macd_hist"]]
            fig.add_trace(go.Bar(x=cdf_show["date"],y=cdf_show["macd_hist"],name="Hist",marker_color=hcolors,showlegend=False), row=3,col=1)
            fig.add_trace(go.Scatter(x=cdf_show["date"],y=cdf_show["macd"],name="MACD",line=dict(color="#54a0ff",width=1.2)), row=3,col=1)
            fig.add_trace(go.Scatter(x=cdf_show["date"],y=cdf_show["macd_signal"],name="Signal",line=dict(color="#ffd700",width=1.2)), row=3,col=1)

            fig.update_layout(
                height=520, paper_bgcolor="#070913", plot_bgcolor="#0b0f19",
                xaxis_rangeslider_visible=False,
                margin=dict(l=10,r=10,t=10,b=10),
                legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,font_color="#8b949e"),
            )
            fig.update_xaxes(gridcolor="#1f2937",showline=True,linecolor="#21262d",color="#8b949e")
            fig.update_yaxes(gridcolor="#1f2937",showline=True,linecolor="#21262d",color="#8b949e")
            st.plotly_chart(fig, use_container_width=True, key="main_chart")

            # Patterns + Signals
            st.markdown("### 🕯️ What the Candles Are Saying")
            patterns = detect_candle_patterns(cdf)
            for pname, pdesc, pkind, pconf in patterns:
                bg   = "#0c2b1a" if pkind=="bull" else "#331212" if pkind=="bear" else "#12161f"
                bord = "#00ff88" if pkind=="bull" else "#ff4444" if pkind=="bear" else "#30363d"
                cc   = "#00ff88" if pconf>=80 else "#ffd700" if pconf>=65 else "#8b949e"
                st.markdown(f"""
                <div style='background:{bg};border:1px solid {bord};border-radius:8px;
                            padding:12px 16px;margin-bottom:8px'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:4px'>
                    <span style='color:#e6edf3;font-weight:600'>{pname}</span>
                    <span style='color:{cc};font-size:.78rem;font-family:monospace'>{pconf}% confidence</span>
                  </div>
                  <div style='color:#c9d1d9;font-size:.87rem;line-height:1.6'>{pdesc}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("### 🎯 Indicator Signals")
            ind_signals, action = get_indicator_signals(cdf)
            action_meta = {
                "BUY":       ("#00ff88","#0c2b1a","✅ BUY",      "Most indicators agree — good conditions to hold or buy more."),
                "WEAK BUY":  ("#7fff00","#0d2218","🟡 WEAK BUY", "More positive than negative. Could buy carefully with a small amount."),
                "HOLD":      ("#ffd700","#1c1c0d","⏸️ HOLD",     "Mixed signals. Keep what you have. Wait for clearer direction."),
                "WEAK SELL": ("#ff8c00","#2b1a0d","🟠 WEAK SELL","More negative than positive. Don't add more. Protect profits."),
                "SELL":      ("#ff4444","#331212","🔴 SELL",     "Multiple indicators pointing down. Consider reducing position."),
            }
            ac,bg2,label,explanation = action_meta.get(action,action_meta["HOLD"])
            st.markdown(f"""
            <div style='background:{bg2};border:2px solid {ac};border-radius:10px;
                        padding:16px 20px;margin-bottom:14px'>
              <div style='color:{ac};font-size:1.5rem;font-weight:700;font-family:monospace'>{label}</div>
              <div style='color:#c9d1d9;font-size:.88rem;margin-top:4px'>{explanation}</div>
            </div>""", unsafe_allow_html=True)
            for title, desc, kind in ind_signals:
                tc = "tag-bull" if kind=="bull" else "tag-bear" if kind=="bear" else "tag-neut"
                st.markdown(f"""
                <div class='signal-box'>
                  <span class='tag {tc}'>{title}</span>
                  <div style='color:#c9d1d9;font-size:.85rem;margin-top:6px;line-height:1.5'>{desc}</div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — PORTFOLIO
# ══════════════════════════════════════════════════════════
with tab_portfolio:
    st.markdown("### 💼 My Portfolio")
    p_action, p_order = st.columns([1, 2.5])

    with p_action:
        st.markdown("#### 🔄 Buy / Sell")
        sym_opts = sorted(df["symbol"].dropna().unique().tolist())
        t_sym = st.selectbox("Ticker", sym_opts, key="order_sym")
        t_shares = st.number_input("Shares", min_value=1, step=1, value=10)
        match = df[df["symbol"]==t_sym]
        default_price = float(match["ltp"].values[0]) if not match.empty else 100.0
        t_price = st.number_input("Price (NPR)", min_value=1.0, step=0.5, value=default_price)
        t_side  = st.selectbox("Action", ["BUY","SELL"])

        if st.button("Execute Order", use_container_width=True):
            cur = st.session_state.portfolio.get(t_sym, {"shares":0,"avg_cost":0.0})
            if t_side == "BUY":
                total = cur["shares"]*cur["avg_cost"] + t_shares*t_price
                new_shares = cur["shares"] + t_shares
                st.session_state.portfolio[t_sym] = {"shares":new_shares,"avg_cost":round(total/new_shares,2)}
                st.success(f"Bought {t_shares} shares of {t_sym} @ Rs {t_price:.2f}")
            else:
                if cur["shares"] >= t_shares:
                    new_shares = cur["shares"] - t_shares
                    if new_shares == 0:
                        st.session_state.portfolio.pop(t_sym,None)
                    else:
                        st.session_state.portfolio[t_sym]["shares"] = new_shares
                    st.success(f"Sold {t_shares} shares of {t_sym}")
                else:
                    st.error(f"You only have {cur['shares']} shares of {t_sym}.")
            st.rerun()

    with p_order:
        if not st.session_state.portfolio:
            st.info("No holdings. Use the Buy/Sell panel to add positions.")
        else:
            records, total_val, total_cost = [], 0.0, 0.0
            for psym, pdata in st.session_state.portfolio.items():
                m = df[df["symbol"]==psym]
                live = float(m["ltp"].values[0]) if not m.empty else pdata["avg_cost"]
                sec  = m["sector"].values[0] if not m.empty else "—"
                shares = pdata["shares"]
                cost  = shares * pdata["avg_cost"]
                mval  = shares * live
                pnl   = mval - cost
                pnl_p = (pnl/cost*100) if cost>0 else 0
                total_val += mval; total_cost += cost
                records.append({"Stock":psym,"Sector":sec,"Units":shares,
                                 "Avg Cost":pdata["avg_cost"],"LTP":live,
                                 "Cost Basis":cost,"Market Value":mval,
                                 "P&L":pnl,"Return %":pnl_p})

            tot_pnl = total_val - total_cost
            tot_pct = (tot_pnl/total_cost*100) if total_cost>0 else 0
            pnl_col = "#00ff88" if tot_pnl>=0 else "#ff4444"

            k1,k2,k3 = st.columns(3)
            k1.markdown(f"<div class='kpi-card'><div class='kpi-label'>Market Value</div><div class='kpi-val' style='color:#ffd700'>Rs {total_val:,.0f}</div></div>", unsafe_allow_html=True)
            k2.markdown(f"<div class='kpi-card'><div class='kpi-label'>Cost Basis</div><div class='kpi-val'>Rs {total_cost:,.0f}</div></div>", unsafe_allow_html=True)
            k3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total P&L</div><div class='kpi-val' style='color:{pnl_col}'>Rs {tot_pnl:+,.0f} ({tot_pct:+.1f}%)</div></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            p_df = pd.DataFrame(records)
            st.dataframe(
                p_df.style.format({
                    "Avg Cost":"Rs {:.2f}","LTP":"Rs {:.2f}",
                    "Cost Basis":"Rs {:.0f}","Market Value":"Rs {:.0f}",
                    "P&L":"Rs {:+.0f}","Return %":"{:+.1f}%"
                }).map(lambda v: "color:#00ff88" if isinstance(v,float) and v>0
                       else "color:#ff4444" if isinstance(v,float) and v<0 else "",
                       subset=["P&L","Return %"]),
                use_container_width=True, hide_index=True
            )

# ══════════════════════════════════════════════════════════
# TAB 3 — MARKET ANALYSIS
# ══════════════════════════════════════════════════════════
with tab_matrix:
    sym = st.session_state.active_symbol
    rows = df[df["symbol"]==sym]
    if rows.empty:
        st.info("Select a stock from the Trading Terminal watchlist first.")
    else:
        row = rows.iloc[0]
        st.markdown(f"### Analysis for {sym} — {row.get('name','')}")

        col_macro, col_peer = st.columns(2)

        with col_macro:
            st.markdown("#### 🏛️ Political & Macro Risk")
            for sig in political_macro_analysis(row):
                st.markdown(f"<div class='signal-box' style='border-left-color:#58a6ff'>{sig}</div>", unsafe_allow_html=True)

            st.markdown("<br>**🇳🇵 Nepal-Wide Macro Factors**")
            macro_nw = [
                ("📉 Interest Rate Cycle","NRB loosening policy rates stimulates credit demand but compresses bank margins short term."),
                ("💸 Remittance Economy","~35% of GDP from remittances drives deposits and consumer spending."),
                ("⚡ Energy Surplus","Nepal moving from power deficit to surplus — hydro stocks benefit from India export deals."),
                ("🏛️ Political Stability","13 governments in 16 years adds regulatory uncertainty. Budget delays hurt infrastructure."),
                ("📊 Retail Market","90%+ retail NEPSE volume creates high volatility around elections and budget announcements."),
            ]
            for title, body in macro_nw:
                with st.expander(title):
                    st.write(body)

        with col_peer:
            st.markdown("#### 🤖 Most Similar Stocks")
            st.caption("Found using Euclidean distance across EPS, P/E, Dividend, Score, P/BV")
            peers = smart_compare_candidates(row, df)
            if peers.empty:
                st.info("Need more stocks in the dataset for peer matching.")
            else:
                for _, pr in peers.iterrows():
                    dist = pr.get("_distance",0)
                    pg   = pr.get("grade","?")
                    st.markdown(f"""
                    <div class='stock-card'>
                      <div style='display:flex;justify-content:space-between'>
                        <span style='font-family:monospace;font-weight:bold;font-size:1rem'>{pr["symbol"]} — {pr.get("name","")}</span>
                        <span style='color:#ffd700;font-family:monospace;font-size:.8rem'>dist {dist:.3f}</span>
                      </div>
                      <div style='color:#8b949e;font-size:.78rem;margin:4px 0'>{pr.get("sector","")}</div>
                      <div style='display:flex;gap:16px;font-size:.85rem;font-family:monospace;margin-top:6px'>
                        <span>Rs {pr.get("ltp",0):,.0f}</span>
                        <span>P/E {pr.get("pe_ratio",0):.1f}</span>
                        <span>EPS {pr.get("eps",0):.1f}</span>
                        <span style='color:#00ff88'>Score {pr.get("health_score",0)}/100</span>
                        <span class='grade-{grade_class(pg)}'>{pg}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)

        # Full market table
        st.markdown("---")
        st.markdown("#### 📋 Full Market Table")
        disp = [c for c in ["symbol","name","sector","ltp","change_pct","eps","pe_ratio","dividend_yield","health_score","grade"] if c in df.columns]
        st.dataframe(
            df[disp].sort_values("health_score",ascending=False).rename(columns={"change_pct":"Chg %","pe_ratio":"P/E","dividend_yield":"Div %","health_score":"Score","ltp":"LTP"}),
            use_container_width=True, height=400,
            column_config={"Score": st.column_config.ProgressColumn("Score",min_value=0,max_value=100,format="%d")}
        )

# ══════════════════════════════════════════════════════════
# TAB 4 — SCORE GUIDE
# ══════════════════════════════════════════════════════════
with tab_guide:
    st.markdown("### 📖 Complete Score & Grade Guide")
    st.caption("Everything explained in plain English — no finance degree needed.")

    st.markdown("---")
    st.markdown("## 🎓 Grades")
    for grade, color, pts, label, desc in [
        ("A+","#00ff88","80–100","Excellent","Almost everything is strong. Earnings are good, price is fair, pays solid dividend. These are the stocks you want to hold long-term."),
        ("A", "#7fff00","65–79", "Very Good","Strong fundamentals with maybe one or two small weaknesses. A solid investment."),
        ("B", "#ffd700","50–64", "Decent",   "Doing okay but has weaknesses — maybe low volume or thin dividend. Your PCIL, RNLI, NESDO are here. Not bad, just watch closely."),
        ("C", "#ff8c00","35–49", "Weak",     "Several things below average. HFIN, MBJC, NIFRA, TAMOR are here. Understand why before adding more money."),
        ("D", "#ff4444","0–34",  "High Risk","Failing multiple checks. Losing money, overpriced, or nobody trading it. Avoid unless you have a specific reason."),
    ]:
        st.markdown(f"""
        <div style='background:#161b22;border:1px solid #21262d;border-radius:10px;
                    padding:16px 20px;margin-bottom:10px;display:flex;gap:20px;align-items:flex-start'>
          <div style='text-align:center;min-width:55px'>
            <div style='color:{color};font-size:2rem;font-weight:700;font-family:monospace'>{grade}</div>
            <div style='color:#8b949e;font-size:.68rem'>{pts} pts</div>
          </div>
          <div>
            <div style='color:#e6edf3;font-weight:600;margin-bottom:4px'>{label}</div>
            <div style='color:#c9d1d9;font-size:.87rem;line-height:1.6'>{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🔢 The 6 Score Factors (100 pts total)")
    factors = [
        ("1. EPS — Earnings Per Share","20 pts","#00ff88",
         "How much profit does the company make per share you own? Higher = better.",
         [("Rs 50+","20","World class earner"),("Rs 30–50","15","Strong"),("Rs 15–30","10","Decent"),("Rs 1–15","5","Weak but profitable"),("Negative","0","Losing money 🚨")],
         "Your best: NESDO (88), RNLI (74), PCIL (62) all get full 20 pts."),
        ("2. P/E Ratio","20 pts","#58a6ff",
         "How many years of earnings are you paying for? Lower = cheaper = better.",
         [("Below 10","20","Very cheap — bargain"),("10–15","15","Fair value"),("15–20","10","Slightly expensive"),("20–30","5","Expensive"),("Above 30","0","Very overvalued")],
         "Most of your stocks score 10–15 pts here. Reasonable for Nepal."),
        ("3. Dividend Yield","20 pts","#ffd700",
         "What % of your investment comes back as cash each year?",
         [("Above 10%","20","Exceptional — beats most FDs"),("7–10%","15","Great"),("5–7%","10","Decent"),("2–5%","5","Low"),("Below 2%","0","Barely paying anything")],
         "PCIL (8%), RNLI (7.5%), NESDO (7%) score 15 pts each."),
        ("4. ROE — Return on Equity","20 pts","#c792ea",
         "How efficiently does management turn your money into profit? (EPS ÷ Book Value × 100)",
         [("Above 25%","20","Exceptional management"),("18–25%","15","Great"),("12–18%","10","Good"),("5–12%","5","Okay"),("Below 5%","0","Poor use of money")],
         ""),
        ("5. P/BV — Price to Book Value","10 pts","#ff8c00",
         "Are you paying more or less than what the company is actually worth on paper?",
         [("Below 1.0","10","Buying Rs 100 of assets for less than Rs 100"),("1.0–1.5","7","Fair — small premium"),("1.5–2.5","4","Moderate premium"),("Above 2.5","0","Paying a lot over real value")],
         ""),
        ("6. Momentum — Volume & Price","10 pts","#89ddff",
         "Is the market actively interested in this stock today?",
         [("High volume + price up","10","Strong interest, buyers winning"),("Medium volume + flat","5","Normal trading"),("Low volume","3","Not much interest — fine for long-term"),("Price fell 3%+","0","Active selling, be cautious")],
         "Reason your microfinance stocks score C — great EPS but very low daily volume on NEPSE."),
    ]
    for title, maxpts, color, explanation, tiers, note in factors:
        with st.expander(f"{title}  —  {maxpts}"):
            st.markdown(f"<p style='color:#c9d1d9'>{explanation}</p>", unsafe_allow_html=True)
            for tier_l, pts_v, tier_d in tiers:
                st.markdown(f"""
                <div style='display:flex;gap:14px;padding:7px 0;border-bottom:1px solid #21262d'>
                  <div style='min-width:100px;color:{color};font-family:monospace;font-weight:600'>{tier_l}</div>
                  <div style='min-width:50px;color:#00ff88;font-family:monospace'>{pts_v} pts</div>
                  <div style='color:#8b949e;font-size:.83rem'>{tier_d}</div>
                </div>""", unsafe_allow_html=True)
            if note:
                st.markdown(f"<p style='color:#58a6ff;font-size:.82rem;margin-top:8px'>💡 {note}</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🕯️ Candlestick Patterns — Plain English Reference")
    for emoji, name, kind, desc in [
        ("🟢","Hammer","bull","Price fell hard during day but buyers pushed back up before close. Drop may be ending."),
        ("🟢","Bullish Engulfing","bull","Today's green candle swallowed yesterday's red one. Buyers won convincingly."),
        ("🟢","Morning Star","bull","3 candles: big fall → small uncertain → big recovery. Downtrend ending."),
        ("🟢","Three White Soldiers","bull","3 green candles in a row, each higher. Buyers dominating for 3 days."),
        ("🔴","Shooting Star","bear","Price rose but sellers pushed it back down. Rise may be ending."),
        ("🔴","Bearish Engulfing","bear","Today's red candle swallowed yesterday's green one. Sellers won convincingly."),
        ("🔴","Evening Star","bear","3 candles: big rise → small uncertain → big fall. Uptrend ending."),
        ("🔴","Three Black Crows","bear","3 red candles in a row, each lower. Sellers dominating for 3 days."),
        ("🔵","Doji","neut","Open and close almost same price. Market is undecided. Wait before acting."),
        ("🔵","Spinning Top","neut","Big wicks both ways, small body. Neither buyers nor sellers winning."),
    ]:
        bg   = "#0c2b1a" if kind=="bull" else "#331212" if kind=="bear" else "#12161f"
        bord = "#00ff8840" if kind=="bull" else "#ff444440" if kind=="bear" else "#30363d"
        st.markdown(f"""
        <div style='background:{bg};border:1px solid {bord};border-radius:6px;
                    padding:9px 14px;margin-bottom:5px;display:flex;gap:12px;align-items:center'>
          <span>{emoji}</span>
          <span style='color:#e6edf3;font-weight:600;min-width:180px;font-size:.88rem'>{name}</span>
          <span style='color:#8b949e;font-size:.84rem'>{desc}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='background:#121824;border:1px solid #21262d;border-radius:10px;padding:20px'>
      <p style='color:#e6edf3;font-weight:600;margin-bottom:12px'>🎯 Signal Meanings</p>
      <div style='margin:8px 0'><span style='color:#00ff88;font-family:monospace;font-weight:700'>BUY      </span><span style='color:#c9d1d9;margin-left:12px'>Most indicators agree. Good time to hold or add more.</span></div>
      <div style='margin:8px 0'><span style='color:#7fff00;font-family:monospace;font-weight:700'>WEAK BUY </span><span style='color:#c9d1d9;margin-left:12px'>More positive than negative. Buy a small amount carefully.</span></div>
      <div style='margin:8px 0'><span style='color:#ffd700;font-family:monospace;font-weight:700'>HOLD     </span><span style='color:#c9d1d9;margin-left:12px'>Mixed signals. Keep what you have. Wait for clarity.</span></div>
      <div style='margin:8px 0'><span style='color:#ff8c00;font-family:monospace;font-weight:700'>WEAK SELL</span><span style='color:#c9d1d9;margin-left:12px'>More negative. Do not add more. Protect your profits.</span></div>
      <div style='margin:8px 0'><span style='color:#ff4444;font-family:monospace;font-weight:700'>SELL     </span><span style='color:#c9d1d9;margin-left:12px'>Multiple indicators pointing down. Consider reducing position.</span></div>
      <p style='color:#8b949e;font-size:.78rem;margin-top:14px'>⚠️ These are mathematical signals, not guarantees. Never invest money you cannot afford to lose.</p>
    </div>
    """, unsafe_allow_html=True)

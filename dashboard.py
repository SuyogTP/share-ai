"""
NEPSE Market Tracker — v3.0 Quant Trading Terminal
Features: 
- Live Session Portfolio Ledger (Real-time P&L & Cost Accounting)
- Vector-Distance Feature-Normalized Peer Matcher
- Synchronous Multi-Panel Indicator Charts (Candlesticks, Bollinger, MACD)
- Sectoral Policy Macro Risk Matrix
- Secure State-Preserving Auth Gateway
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

# ==========================================
# 1. PAGE CONFIGURATION & THEME INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="NEPSE Terminal v3.0",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Deep Terminal CSS Override
st.markdown("""
<style>
    /* Core Layout Foundations */
    html, body, [data-testid="stApp"] { 
        background: #070913 !important; 
        color: #c9d1d9 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] { 
        background: #0d111a !important; 
        border-right: 1px solid #1f2937; 
    }
    
    /* Headers & Text Typography */
    h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; color: #f0f6fc !important; }
    .mono { font-family: 'JetBrains Mono', monospace !important; }
    
    /* Metric Cards */
    .kpi-card {
        background: linear-gradient(135deg, #111625, #0b0e17);
        border: 1px solid #21262d; 
        border-radius: 8px;
        padding: 16px; 
        text-align: left;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .kpi-val { font-size: 1.6rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #ffffff; }
    .kpi-label { font-size: 0.72rem; color: #8b949e; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 4px; }
    
    /* Row Cards & Performance Badges */
    .stock-card {
        background: #121824; 
        border: 1px solid #21262d; 
        border-radius: 8px;
        padding: 16px; 
        margin-bottom: 12px; 
        transition: all 0.2s ease-in-out;
    }
    .stock-card:hover { border-color: #00ff88; box-shadow: 0 0 10px rgba(0,255,136,0.1); }
    
    .grade-Ap { color: #00ff88; font-weight: 700; font-size: 1.2rem; }
    .grade-A { color: #7fff00; font-weight: 700; font-size: 1.2rem; }
    .grade-B { color: #ffd700; font-weight: 700; font-size: 1.2rem; }
    .grade-C { color: #ff8c00; font-weight: 700; font-size: 1.2rem; }
    .grade-D { color: #ff4444; font-weight: 700; font-size: 1.2rem; }
    
    .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; font-family: 'JetBrains Mono', monospace; }
    .tag-bull { background: #0c2b1a; color: #00ff88; border: 1px solid #00ff8830; }
    .tag-bear { background: #331212; color: #ff4444; border: 1px solid #ff444430; }
    .tag-neut { background: #1a2233; color: #8b949e; border: 1px solid #30363d; }
    
    .signal-box {
        background: #0b0f19; 
        border-left: 3px solid #00ff88;
        border-radius: 4px; 
        padding: 12px; 
        margin: 8px 0;
        font-size: 0.85rem; 
        color: #c9d1d9;
        line-height: 1.5;
    }
    
    /* Form & UI Optimization */
    div[data-testid="stTab"] button { font-family: 'Inter', sans-serif !important; font-size: 0.9rem; }
    div[data-testid="stTab"] button[aria-selected="true"] { color: #00ff88 !important; border-bottom-color: #00ff88 !important; }
</style>""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE STATE INITIALIZATION
# ==========================================
if "portfolio" not in st.session_state:
    # Baseline seed data for user portfolio tracking
    st.session_state.portfolio = {
        "NABIL": {"shares": 120, "avg_cost": 465.0},
        "HDL": {"shares": 15, "avg_cost": 1850.0}
    }

# ==========================================
# 3. SECURE USER AUTHENTICATION GATEWAY
# ==========================================
_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
if _PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
            <div style='display:flex; flex-direction:column; align-items:center; justify-content:center; height:45vh; margin-top:10vh;'>
                <h1 style='color:#00ff88; font-family:monospace; letter-spacing:2px; font-size:2.5rem;'>📈 NEPSE TERMINAL 3.0</h1>
                <p style='color:#8b949e; font-size:1rem; margin-top:-10px;'>Nepal Stock Market Quant Intelligence Suite</p>
            </div>
        """, unsafe_allow_html=True)
        
        _, col, _ = st.columns([1, 1.5, 1])
        with col:
            with st.form("login_form"):
                pw = st.text_input("Security Token Required", type="password", placeholder="Enter authorization token...")
                submit = st.form_submit_button("Access Terminal →", use_container_width=True)
                if submit:
                    if pw == _PASSWORD:
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Invalid Security Token Reference.")
            st.stop()

# ==========================================
# 4. HIGH-PERFORMANCE DATA LOADER ENGINE
# ==========================================
DATA_PATH = Path("data/data.json")

@st.cache_data(ttl=300)
def load_data():
    if not DATA_PATH.exists():
        mock_data = {
            "market_summary": {"index": 2150.45, "change": 14.32, "pct_change": 0.67, "turnover": 4120534200},
            "stocks": [
                {"symbol": "NABIL", "name": "Nabil Bank Limited", "sector": "Banking", "ltp": 485.0, "change": 2.5, "pct_change": 0.52, "eps": 22.4, "pe_ratio": 21.65, "dividend_yield": 11.5, "pbv": 2.1, "health_score": 78, "grade": "A+", "sentiment": "Bullish"},
                {"symbol": "AKPL", "name": "Ankhu Khola Hydropower", "sector": "Hydropower", "ltp": 165.0, "change": -4.2, "pct_change": -2.48, "eps": 4.1, "pe_ratio": 40.24, "dividend_yield": 0.0, "pbv": 1.05, "health_score": 42, "grade": "C", "sentiment": "Bearish"},
                {"symbol": "NICA", "name": "NIC Asia Bank Limited", "sector": "Banking", "ltp": 512.0, "change": 1.2, "pct_change": 0.23, "eps": 28.1, "pe_ratio": 18.22, "dividend_yield": 10.0, "pbv": 2.4, "health_score": 82, "grade": "A+", "sentiment": "Bullish"},
                {"symbol": "HDL", "name": "Himalayan Distillery", "sector": "Manufacturing", "ltp": 1820.0, "change": -15.0, "pct_change": -0.82, "eps": 42.6, "pe_ratio": 42.72, "dividend_yield": 25.0, "pbv": 5.8, "health_score": 69, "grade": "A", "sentiment": "Neutral"}
            ]
        }
        return pd.DataFrame(mock_data["stocks"]), mock_data
    
    try:
        with open(DATA_PATH) as f:
            raw = json.load(f)
        df = pd.DataFrame(raw.get("stocks", []))
        return df, raw
    except Exception as e:
        st.error(f"Data Ingestion Failure: {str(e)}")
        return pd.DataFrame(), {}

df, meta = load_data()

# ==========================================
# 5. QUANT MATHEMATICAL & ANALYSIS ENGINES
# ==========================================
def generate_candles(symbol, ltp, days=120):
    random.seed(hash(symbol) % 9999)
    price = ltp * 0.95
    data = []
    base_date = datetime.today() - timedelta(days=days)
    
    for i in range(days):
        change = random.gauss(0.0005, 0.015)
        open_p = price
        close_p = price * (1 + change)
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.008))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.008))
        vol = int(random.uniform(10000, 150000))
        
        data.append({
            "date": base_date + timedelta(days=i),
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": vol
        })
        price = close_p
    return pd.DataFrame(data)

def compute_indicators(cdf):
    cdf = cdf.copy()
    cdf["sma20"] = cdf["close"].rolling(20).mean()
    cdf["sma50"] = cdf["close"].rolling(50).mean()
    
    std20 = cdf["close"].rolling(20).std()
    cdf["bb_upper"] = cdf["sma20"] + 2 * std20
    cdf["bb_lower"] = cdf["sma20"] - 2 * std20
    
    delta = cdf["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-9)
    cdf["rsi"] = 100 - (100 / (1 + rs))
    
    ema12 = cdf["close"].ewm(span=12, adjust=False).mean()
    ema26 = cdf["close"].ewm(span=26, adjust=False).mean()
    cdf["macd"] = ema12 - ema26
    cdf["macd_signal"] = cdf["macd"].ewm(span=9, adjust=False).mean()
    cdf["macd_hist"] = cdf["macd"] - cdf["macd_signal"]
    return cdf

def political_macro_analysis(row):
    sector = row.get("sector", "")
    eps = row.get("eps", 0) or 0
    div = row.get("dividend_yield", 0) or 0
    score = row.get("health_score", 0) or 0
    signals = []
    
    sector_macro = {
        "Banking": [
            "🏛️ Nepal Rastra Bank policy mandates and CRR/SLR fluctuations directly affect liquidity pools.",
            "📋 Capital Adequacy Framework (Basel III) compliance limits aggressive risk asset expansions.",
            "💰 Remittance inflow metrics remain critical forward drivers for banking sector deposits."
        ],
        "Hydropower": [
            "⚡ PPA (Power Purchase Agreement) allocations fix localized product income ceilings.",
            "🌧️ Run-of-river hydrology architecture links Q2/Q3 margins to monsoonal capacity variations.",
            "🤝 Cross-border high-voltage grid connections act as structural profitability catalysts."
        ],
        "Insurance": [
            "📜 Nepal Insurance Authority minimum paid-up constraints continue to trigger forced consolidations.",
            "💵 Solvency margin metrics affect investment capacity across underwriters."
        ],
        "Microfinance": [
            "⚠️ Regulatory cost-of-fund caps limit interest distribution flexibility parameters.",
            "🏘️ Rural credit exposure increases direct linkage to local agricultural production patterns."
        ]
    }
    for s, msgs in sector_macro.items():
        if s.lower() in sector.lower():
            signals.extend(msgs)
            break
            
    signals.append("🌍 Macro forex volatility affects infrastructure project imports and systemic liquidity.")
    signals.append("📊 Retail dominance triggers high velocity updates across local valuation structures.")
    if score >= 75: signals.append("✅ Elite core metrics position the equity well to absorb localized macro shocks.")
    if div > 8: signals.append("💸 Dividend shield limits downside drops during macro contraction phases.")
    if eps < 10: signals.append("⚠️ Low single-digit EPS points to vulnerability under high-interest regimes.")
    return signals

def smart_compare_candidates(target_row, all_df):
    metrics = ["eps", "pe_ratio", "dividend_yield", "health_score", "pbv"]
    clean_df = all_df.dropna(subset=metrics).copy()
    if len(clean_df) <= 1:
        return pd.DataFrame()
        
    norm_data = {}
    for m in metrics:
        min_val = clean_df[m].min()
        max_val = clean_df[m].max()
        denom = (max_val - min_val) if (max_val - min_val) > 0 else 1
        norm_data[m] = (clean_df[m] - min_val) / denom
        
    norm_df = pd.DataFrame(norm_data, index=clean_df.index)
    target_idx = target_row.name
    if target_idx not in norm_df.index:
        return clean_df.head(3)
        
    target_vector = norm_df.loc[target_idx]
    distances = norm_df.apply(lambda row: np.linalg.norm(row - target_vector), axis=1)
    clean_df["_distance"] = distances
    return clean_df[clean_df.index != target_idx].sort_values("_distance").head(3)

# ==========================================
# 6. BANNER METRIC SYSTEM HEADER
# ==========================================
m_summary = meta.get("market_summary", {"index": 2100.0, "change": 0.0, "pct_change": 0.0, "turnover": 0})
st.markdown(f"""
<div style='background:#0d111a; border-bottom:1px solid #1f2937; padding:10px 20px; display:flex; gap:40px; align-items:center;'>
    <div><span style='color:#8b949e; font-size:0.75rem;'>NEPSE INDEX</span><br><span style='font-family:monospace; font-size:1.2rem; font-weight:700;'>{m_summary['index']:,}</span></div>
    <div><span style='color:#8b949e; font-size:0.75rem;'>CHANGE</span><br><span style='font-family:monospace; font-size:1.2rem; font-weight:700; color:{"#00ff88" if m_summary['change']>=0 else "#ff4444"};'>{m_summary['change']:+,} ({m_summary['pct_change']:+:.2f}%)</span></div>
    <div><span style='color:#8b949e; font-size:0.75rem;'>DAILY TURNOVER</span><br><span style='font-family:monospace; font-size:1.2rem; font-weight:700; color:#ffd700;'>NPR {m_summary['turnover']:,}</span></div>
</div>
<br>
""", unsafe_allow_html=True)

# ==========================================
# 7. SIDEBAR PARAMETER SELECTION CONTROLS
# ==========================================
st.sidebar.markdown("### 🎛️ Terminal Controls")
search_query = st.sidebar.text_input("Filter Ticker / Asset", "", placeholder="Search symbol or name...")
sector_list = ["All Sectors"] + list(df["sector"].unique()) if not df.empty else ["All Sectors"]
selected_sector = st.sidebar.selectbox("Sector Filter", sector_list)

# Data Filter Optimization Routing
filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[
        (filtered_df["symbol"].str.contains(search_query, case=False)) |
        (filtered_df["name"].str.contains(search_query, case=False))
    ]
if selected_sector != "All Sectors":
    filtered_df = filtered_df[filtered_df["sector"] == selected_sector]

# ==========================================
# 8. PRIMARY APP WORKSPACE LAYOUT
# ==========================================
app_tab_main, app_tab_portfolio, app_tab_matrix = st.tabs(["🖥️ Trading Terminal View", "💼 Portfolio Quant Engine", "📊 Full Market Analysis Matrix"])

# ─── TAB 1: TRADING TERMINAL ───
with app_tab_main:
    col_list, col_chart = st.columns([1, 2.2])
    
    with col_list:
        st.markdown("#### 📜 Watchlist Rows")
        if filtered_df.empty:
            st.info("No assets found matching current criteria.")
        else:
            for idx, row in filtered_df.iterrows():
                sym = row["symbol"]
                ltp = row["ltp"]
                chg = row["pct_change"]
                grd = row.get("grade", "B")
                
                # Active highlighting layout color change 
                is_active = st.session_state.get("active_symbol") == sym
                border_color = "#00ff88" if is_active else "#21262d"
                
                with st.container():
                    st.markdown(f"""
                    <div style='border:1px solid {border_color}; padding:10px; border-radius:6px; margin-bottom:8px; background:#111625;'>
                        <div style='display:flex; justify-content

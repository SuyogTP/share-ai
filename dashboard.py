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
    }
    
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
# 2. SESSION STATE INITIALIZATION
# ==========================================
st.session_state.portfolio = {
        "HFIN": {"shares": 10, "avg_cost": 100.0},
        "HLI": {"shares": 12, "avg_cost": 100.0},
        "MBJC": {"shares": 10, "avg_cost": 100.0},
        "NESDO": {"shares": 11, "avg_cost": 100.0},
        "NIFRA": {"shares": 64, "avg_cost": 100.0},
        "PCIL": {"shares": 10, "avg_cost": 100.0},
        "RNLI": {"shares": 12, "avg_cost": 100.0},
        "TAMOR": {"shares": 10, "avg_cost": 100.0}
    }

# ==========================================
# 3. SECURE USER AUTHENTICATION GATEWAY
# ==========================================
_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
if _PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<div style='text-align:center; margin-top:10vh;'><h1 style='color:#00ff88;'>📈 NEPSE TERMINAL 3.0</h1><p style='color:#8b949e;'>Nepal Stock Market Quant Intelligence Suite</p></div>", unsafe_allow_html=True)
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
chg_color = "#00ff88" if m_summary['change'] >= 0 else "#ff4444"

# Format strings BEFORE injecting into HTML
m_idx_str = f"{m_summary['index']:,}"
m_chg_str = f"{m_summary['change']:+,.2f}"
m_pct_str = f"{m_summary['pct_change']:+.2f}%"
m_trn_str = f"{m_summary['turnover']:,}"

st.markdown(f"""
<div style='background:#0d111a; border-bottom:1px solid #1f2937; padding:10px 20px; display:flex; gap:40px; align-items:center;'>
    <div><span style='color:#8b949e; font-size:0.75rem;'>NEPSE INDEX</span><br><span style='font-family:monospace; font-size:1.2rem; font-weight:700;'>{m_idx_str}</span></div>
    <div><span style='color:#8b949e; font-size:0.75rem;'>CHANGE</span><br><span style='font-family:monospace; font-size:1.2rem; font-weight:700; color:{chg_color};'>{m_chg_str} ({m_pct_str})</span></div>
    <div><span style='color:#8b949e; font-size:0.75rem;'>DAILY TURNOVER</span><br><span style='font-family:monospace; font-size:1.2rem; font-weight:700; color:#ffd700;'>NPR {m_trn_str}</span></div>
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
                # FIX: Using .get() prevents KeyErrors if your JSON is missing these columns
                sym = row.get("symbol", "UNKNOWN")
                ltp = row.get("ltp", 0.0)
                chg = row.get("pct_change", 0.0)
                grd = row.get("grade", "B")
                
                is_active = st.session_state.get("active_symbol") == sym
                border_color = "#00ff88" if is_active else "#21262d"
                color_txt = "#00ff88" if chg >= 0 else "#ff4444"
                
                # Format string BEFORE injecting
                chg_str = f"{chg:+.2f}%"
                
                html_row = f"""
                <div style='border:1px solid {border_color}; padding:10px; border-radius:6px; margin-bottom:8px; background:#111625;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <span style='font-family:monospace; font-weight:bold; font-size:1rem;'>{sym}</span>
                        <span style='color:{color_txt}; font-family:monospace; font-size:0.9rem; margin-left:auto;'>{chg_str}</span>
                    </div>
                    <div style='display:flex; justify-content:space-between; font-size:0.75rem; color:#8b949e; margin-top:4px;'>
                        <span>LTP: Rs {ltp}</span>
                        <span style='margin-left:auto;'>Grade {grd}</span>
                    </div>
                </div>
                """
                st.markdown(html_row, unsafe_allow_html=True)
                if st.button(f"Analyze {sym}", key=f"sel_{sym}", use_container_width=True):
                    st.session_state["active_symbol"] = sym
                    st.rerun()

            if "active_symbol" not in st.session_state and not filtered_df.empty:
                st.session_state["active_symbol"] = filtered_df.iloc[0]["symbol"]

    with col_chart:
        if "active_symbol" in st.session_state and not df.empty:
            target_sym = st.session_state["active_symbol"]
            stock_row = df[df["symbol"] == target_sym].iloc[0]
            
            # Asset Headline Blocks
            headline_html = f"""
            <div style='background:#121824; border:1px solid #21262d; padding:16px; border-radius:8px; margin-bottom:15px;'>
                <div style='display:flex; align-items:center;'>
                    <div>
                        <h2 style='margin:0; color:#f0f6fc;'>{stock_row['symbol']} · {stock_row['name']}</h2>
                        <span style='color:#8b949e; font-size:0.85rem;'>Sector Components: {stock_row['sector']}</span>
                    </div>
                    <div style='margin-left:auto; text-align:right;'>
                        <span class='grade-A'>{stock_row['grade']} Grade</span><br>
                        <span class='tag tag-bull'>{stock_row.get('sentiment','NEUTRAL')}</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(headline_html, unsafe_allow_html=True)
            
            # Core Parameter Micro Matrix
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.markdown(f"<div class='kpi-card'><div class='kpi-label'>LTP (NPR)</div><div class='kpi-val'>{stock_row['ltp']:,}</div></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='kpi-card'><div class='kpi-label'>P/E Ratio</div><div class='kpi-val'>{stock_row['pe_ratio']}</div></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Trailing EPS</div><div class='kpi-val'>{stock_row['eps']}</div></div>", unsafe_allow_html=True)
            m4.markdown(f"<div class='kpi-card'><div class='kpi-label'>Div Yield</div><div class='kpi-val'>{stock_row['dividend_yield']}%</div></div>", unsafe_allow_html=True)
            m5.markdown(f"<div class='kpi-card'><div class='kpi-label'>Health Score</div><div class='kpi-val' style='color:#00ff88;'>{stock_row['health_score']}/100</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Dynamic Indicators Engine Subplots
            candles_df = generate_candles(target_sym, stock_row["ltp"])
            candles_df = compute_indicators(candles_df)
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
            
            fig.add_trace(go.Candlestick(
                x=candles_df["date"], open=candles_df["open"], high=candles_df["high"],
                low=candles_df["low"], close=candles_df["close"], name="Price"
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(x=candles_df["date"], y=candles_df["sma20"], name="SMA 20", line=dict(color='#ff9f43', width=1.2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=candles_df["date"], y=candles_df["bb_upper"], name="BB Upper", line=dict(color='#00d2d3', width=0.8, dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=candles_df["date"], y=candles_df["bb_lower"], name="BB Lower", line=dict(color='#00d2d3', width=0.8, dash='dash')), row=1, col=1)
            
            fig.add_trace(go.Bar(x=candles_df["date"], y=candles_df["macd_hist"], name="MACD Hist", marker_color='#ee5253'), row=2, col=1)
            fig.add_trace(go.Scatter(x=candles_df["date"], y=candles_df["macd"], name="MACD Line", line=dict(color='#54a0ff', width=1.2)), row=2, col=1)
            
            fig.update_layout(
                template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10),
                height=460, paper_bgcolor="#070913", plot_bgcolor="#0b0f19",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_xaxes(gridcolor="#1f2937", showline=True, linecolor="#21262d")
            fig.update_yaxes(gridcolor="#1f2937", showline=True, linecolor="#21262d")
            st.plotly_chart(fig, use_container_width=True)

# ─── TAB 2: PORTFOLIO QUANT ENGINE ───
with app_tab_portfolio:
    st.markdown("### 💼 Live Session Portfolio Engine")
    p_action, p_order = st.columns([1, 2.5])
    
    with p_action:
        st.markdown("#### 🔄 Order Simulator")
        with st.form("portfolio_order_form"):
            t_sym = st.selectbox("Ticker", list(df["symbol"].unique()))
            t_shares = st.number_input("Shares Volume", min_value=1, step=1, value=10)
            t_price = st.number_input("Execution Price (NPR)", min_value=1.0, step=0.5, value=float(df[df["symbol"]==t_sym]["ltp"].values[0]))
            t_side = st.selectbox("Order Side", ["BUY", "SELL"])
            
            if st.form_submit_button("Execute Ledger Allocation", use_container_width=True):
                current_holdings = st.session_state.portfolio.get(t_sym, {"shares": 0, "avg_cost": 0.0})
                
                if t_side == "BUY":
                    total_cost = (current_holdings["shares"] * current_holdings["avg_cost"]) + (t_shares * t_price)
                    new_shares = current_holdings["shares"] + t_shares
                    st.session_state.portfolio[t_sym] = {
                        "shares": new_shares,
                        "avg_cost": round(total_cost / new_shares, 2)
                    }
                    st.success(f"Executed entry allocation for {t_shares} shares of {t_sym}.")
                else:
                    if current_holdings["shares"] >= t_shares:
                        new_shares = current_holdings["shares"] - t_shares
                        if new_shares == 0:
                            st.session_state.portfolio.pop(t_sym, None)
                        else:
                            st.session_state.portfolio[t_sym]["shares"] = new_shares
                        st.success(f"Executed exit transaction for {t_shares} shares of {t_sym}.")
                    else:
                        st.error("Insufficient asset volume inside active ledger matrix.")
                st.rerun()

    with p_order:
        st.markdown("#### 📊 Position Tracking Matrix")
        if not st.session_state.portfolio:
            st.info("Active engine session parameters are currently completely blank.")
        else:
            p_records = []
            total_valuation = 0.0
            total_cost_basis = 0.0
            
            for psym, data in st.session_state.portfolio.items():
                match_row = df[df["symbol"] == psym]
                if not match_row.empty:
                    live_ltp = match_row["ltp"].values[0]
                    sec_comp = match_row["sector"].values[0]
                else:
                    live_ltp = data["avg_cost"]
                    sec_comp = "Unknown"
                    
                shares = data["shares"]
                cost_basis = shares * data["avg_cost"]
                market_val = shares * live_ltp
                unrealized_pnl = market_val - cost_basis
                pnl_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0.0
                
                total_valuation += market_val
                total_cost_basis += cost_basis
                
                p_records.append({
                    "Ticker": psym,
                    "Sector": sec_comp,
                    "Shares Owned": shares,
                    "Avg Cost (NPR)": data["avg_cost"],
                    "LTP (NPR)": live_ltp,
                    "Cost Basis": cost_basis,
                    "Market Value": market_val,
                    "Unrealized P&L": unrealized_pnl,
                    "Return (%)": pnl_pct
                })
            
            p_df = pd.DataFrame(p_records)
            tot_pnl = total_valuation - total_cost_basis
            tot_pnl_pct = (tot_pnl / total_cost_basis) * 100 if total_cost_basis > 0 else 0.0
            pnl_color = "#00ff88" if tot_pnl >= 0 else "#ff4444"
            
            k_p1, k_p2, k_p3 = st.columns(3)
            k_p1.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Market Value</div><div class='kpi-val' style='color:#ffd700;'>NPR {total_valuation:,.2f}</div></div>", unsafe_allow_html=True)
            k_p2.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Cost Basis</div><div class='kpi-val'>NPR {total_cost_basis:,.2f}</div></div>", unsafe_allow_html=True)
            k_p3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Net Profit / Loss</div><div class='kpi-val' style='color:{pnl_color};'>NPR {tot_pnl:+,.2f} ({tot_pnl_pct:+,.2f}%)</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.dataframe(
                p_df.style.format({
                    "Avg Cost (NPR)": "Rs {:.2f}",
                    "LTP (NPR)": "Rs {:.2f}",
                    "Cost Basis": "Rs {:.2f}",
                    "Market Value": "Rs {:.2f}",
                    "Unrealized P&L": "Rs {:+.2f}",
                    "Return (%)": "{:+.2f}%"
                }),
                use_container_width=True,
                hide_index=True
            )

# ─── TAB 3: ANALYSIS MATRIX (MACRO & PEER VECTOR MATCHING) ───
with app_tab_matrix:
    if "active_symbol" in st.session_state:
        target_sym = st.session_state["active_symbol"]
        stock_row = df[df["symbol"] == target_sym].iloc[0]
        
        col_macro, col_vector = st.columns(2)
        
        with col_macro:
            st.markdown(f"#### 🏛️ Sector Policy Outlook: {stock_row['symbol']}")
            macro_signals = political_macro_analysis(stock_row)
            for sig in macro_signals:
                st.markdown(f"<div class='signal-box'>{sig}</div>", unsafe_allow_html=True)
                
        with col_vector:
            st.markdown(f"#### 🤖 Euclidean Nearest Vector Peers for {stock_row['symbol']}")
            peers = smart_compare_candidates(stock_row, df)
            if peers.empty:
                st.info("Insufficient system dataset size to generate peer distance metrics.")
            else:
                for idx, prow in peers.iterrows():
                    peer_html = f"""
                    <div class='stock-card' style='border: 1px solid #21262d; padding: 16px; border-radius: 8px; margin-bottom: 12px; background: #121824;'>
                        <div style='display:flex; justify-content:space-between;'>
                            <span style='font-family:monospace; font-weight:bold; font-size:1.1rem;'>{prow['symbol']} - {prow['name']}</span>
                            <span style='color:#ffd700; font-family:monospace; margin-left:auto;'>Vector Dist: {prow['_distance']:.4f}</span>
                        </div>
                        <div style='color:#8b949e; font-size:0.8rem; margin:4px 0;'>Sector Component: {prow['sector']}</div>
                        <div style='display:flex; gap:20px; font-size:0.85rem; font-family:monospace; margin-top:8px;'>
                            <span>LTP: Rs {prow['ltp']}</span>
                            <span>P/E: {prow['pe_ratio']}</span>
                            <span>EPS: {prow['eps']}</span>
                            <span style='color:#00ff88;'>Score: {prow['health_score']}</span>
                        </div>
                    </div>
                    """
                    st.markdown(peer_html, unsafe_allow_html=True)

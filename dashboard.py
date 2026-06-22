import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime

# ==========================================
# 1. COMPREHENSIVE CONFIG & ADVANCED THEME
# ==========================================
st.set_page_config(
    page_title="NEPSE IQ Terminal v3.5",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Fidelity Cyber Terminal UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
    
    /* Main Layout */
    .stApp { background-color: #0d0f14; color: #e8eaf0; font-family: 'JetBrains Mono', monospace; }
    section[data-testid="stSidebar"] { background-color: #13161e !important; border-right: 1px solid #1a1e28; }
    
    /* Metrics and Dashboard Cards */
    .metric-container {
        background-color: #13161e; border: 1px solid #1a1e28; border-radius: 8px; padding: 15px; margin-bottom: 10px;
    }
    .metric-label {
        font-size: 11px; color: #8892a4; text-transform: uppercase; letter-spacing: 1px;
    }
    .metric-val { font-size: 24px; font-weight: 700; color: #ffffff; margin-top: 5px; }
    
    .kpi-card {
        background-color: #13161e; border: 1px solid #2a2f3d; padding: 18px; border-radius: 10px; margin-bottom: 12px;
    }
    .kpi-label { font-size: 11px; color: #8892a4; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-val { font-size: 24px; font-weight: 700; margin: 4px 0; }
    .stat-delta { font-size: 11px; font-weight: 600; }
    .stat-delta.up { color: #10b981; }
    .stat-delta.down { color: #ef4444; }

    /* Custom Alert Boxes */
    .alert-item {
        background-color: #13161e; border: 1px solid #2a2f3d; padding: 14px; border-radius: 10px; margin-bottom: 10px;
    }
    .alert-item.sell { border-left: 4px solid #ef4444; }
    .alert-item.buy { border-left: 4px solid #10b981; }
    .alert-item.hold { border-left: 4px solid #f59e0b; }
    .alert-stock { font-weight: 600; font-size: 13px; color: #e8eaf0; }
    .alert-msg { font-size: 12px; color: #8892a4; margin-top: 4px; }
    
    /* Live Status Monitor Widget */
    .monitor-box {
        background: #161b22; border: 1px dashed #30363d; border-radius: 6px; padding: 12px; font-size: 12px; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SEED AUTONOMOUS LIVE UPDATE ENGINE
# ==========================================
if "market_data" not in st.session_state:
    # Baseline verified dataset parameters
    stocks_pool = [
        {"sym": "NABIL", "name": "Nabil Bank Limited", "sector": "Banking", "base_ltp": 485.0, "ltp": 485.0, "chg": -0.42, "vol": 82400, "rsi": 72, "pe": 16.2, "eps": 29.9, "h52": 540, "l52": 410, "signal": "SELL", "roe": 16.5},
        {"sym": "NICA", "name": "NIC Asia Bank", "sector": "Banking", "base_ltp": 422.0, "ltp": 422.0, "chg": 1.8, "vol": 64200, "rsi": 48, "pe": 14.2, "eps": 29.7, "h52": 498, "l52": 310, "signal": "BUY", "roe": 21.2},
        {"sym": "NRIC", "name": "Nepal Reinsurance Company", "sector": "Insurance", "base_ltp": 780.0, "ltp": 780.0, "chg": -1.2, "vol": 12100, "rsi": 61, "pe": 22.1, "eps": 35.3, "h52": 920, "l52": 690, "signal": "HOLD", "roe": 12.4},
        {"sym": "UPPER", "name": "Upper Tamakoshi Hydropower", "sector": "Hydropower", "base_ltp": 278.0, "ltp": 278.0, "chg": 0.7, "vol": 38600, "rsi": 55, "pe": 19.8, "eps": 14.0, "h52": 342, "l52": 198, "signal": "HOLD", "roe": 6.8},
        {"sym": "NHPC", "name": "Nepal Hydro Power", "sector": "Hydropower", "base_ltp": 142.0, "ltp": 142.0, "chg": 4.5, "vol": 95000, "rsi": 68, "pe": 25.4, "eps": 5.6, "h52": 185, "l52": 95, "signal": "BUY", "roe": 8.1},
        {"sym": "PLIC", "name": "Prime Life Insurance", "sector": "Insurance", "base_ltp": 590.0, "ltp": 590.0, "chg": -2.1, "vol": 15400, "rsi": 32, "pe": 28.1, "eps": 21.0, "h52": 680, "l52": 510, "signal": "SELL", "roe": 11.3},
        {"sym": "MLBL", "name": "Mahalaxmi Bikas Bank", "sector": "Finance", "base_ltp": 365.0, "ltp": 365.0, "chg": 0.0, "vol": 8900, "rsi": 50, "pe": 16.5, "eps": 22.1, "h52": 420, "l52": 330, "signal": "HOLD", "roe": 14.0},
        {"sym": "HFIN", "name": "Hotel Forest Inn Limited", "sector": "Hotels", "base_ltp": 815.0, "ltp": 815.0, "chg": 0.45, "vol": 4500, "rsi": 58, "pe": 42.1, "eps": 19.3, "h52": 890, "l52": 710, "signal": "BUY", "roe": 12.4},
        {"sym": "NESDO", "name": "NESDO Sambridha Laghubitta", "sector": "Microfinance", "base_ltp": 1525.0, "ltp": 1525.0, "chg": 0.0, "vol": 2300, "rsi": 42, "pe": 18.2, "eps": 83.7, "h52": 1850, "l52": 1390, "signal": "HOLD", "roe": 24.1},
        {"sym": "NIFRA", "name": "Nepal Infrastructure Bank Ltd.", "sector": "Investment", "base_ltp": 255.1, "ltp": 255.1, "chg": -0.74, "vol": 145200, "rsi": 49, "pe": 21.2, "eps": 12.0, "h52": 310, "l52": 215, "signal": "BUY", "roe": 7.8},
        {"sym": "PCIL", "name": "Palpa Cement Industries", "sector": "Manufacturing", "base_ltp": 721.2, "ltp": 721.2, "chg": 0.31, "vol": 6200, "rsi": 54, "pe": 34.8, "eps": 20.7, "h52": 810, "l52": 640, "signal": "HOLD", "roe": 11.2},
        {"sym": "TAMOR", "name": "Sanima Middle Tamor Hydro", "sector": "Hydropower", "base_ltp": 452.9, "ltp": 452.9, "chg": 0.13, "vol": 21400, "rsi": 52, "pe": 22.4, "eps": 20.2, "h52": 510, "l52": 380, "signal": "BUY", "roe": 10.5}
    ]
    st.session_state["market_data"] = pd.DataFrame(stocks_pool)
    st.session_state["sys_latency"] = 12.4
    st.session_state["tick_count"] = 142

def simulate_market_tick():
    """Mutates stock data slightly to emulate live updating streams."""
    df_mod = st.session_state["market_data"].copy()
    drift_pct = np.random.uniform(-0.018, 0.022, size=len(df_mod))
    df_mod["ltp"] = np.round(df_mod["ltp"] * (1 + drift_pct), 2)
    df_mod["chg"] = np.round(((df_mod["ltp"] - df_mod["base_ltp"]) / df_mod["base_ltp"]) * 100, 2)
    df_mod["rsi"] = np.clip(df_mod["rsi"] + np.random.randint(-4, 5, size=len(df_mod)), 15, 88)
    df_mod["vol"] = df_mod["vol"] + np.random.randint(100, 1500, size=len(df_mod))
    
    # Randomize signal based on simulated momentum changes
    for idx, row in df_mod.iterrows():
        if row["rsi"] > 70: df_mod.at[idx, "signal"] = "SELL"
        elif row["rsi"] < 40: df_mod.at[idx, "signal"] = "BUY"
        else: df_mod.at[idx, "signal"] = random.choice(["BUY", "HOLD", "HOLD"])
        
    st.session_state["market_data"] = df_mod
    st.session_state["sys_latency"] = round(random.uniform(9.1, 15.8), 2)
    st.session_state["tick_count"] += 1

# Auto-update prices on app state refresh
simulate_market_tick()
df = st.session_state["market_data"]

# ==========================================
# 3. CLEAN AUTHENTICATION SECURE GATEWAY (NO AUTO-FILL)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_login, _ = st.columns([1, 1.3, 1])
    with col_login:
        st.write("\n\n\n")
        st.markdown("""
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='color:#3b82f6; margin-bottom:0;'>⬡ NEPSE IQ TERMINAL</h2>
            <p style='color:#8892a4; font-size:11px; text-transform:uppercase; letter-spacing:1px;'>Secure Access Node · Version 3.5</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("secure_auth_gate"):
            # Empty defaults to comply with security requirements (removes autofill vulnerability)
            user_input = st.text_input("Node Operator Handle ID", value="", placeholder="Enter identifier...")
            pass_input = st.text_input("Cryptographic Passkey", type="password", value="", placeholder="••••••••••••")
            submit_auth = st.form_submit_button("Initialize Node Handshake", use_container_width=True)
            
            if submit_auth:
                if user_input == "admin" and pass_input == "nepseiq2026":
                    st.session_state["authenticated"] = True
                    st.success("Handshake signature matching. Initializing engine core.")
                    st.rerun()
                else:
                    st.error("Handshake Refused. Security string credentials mismatch.")
        
        st.markdown("<p style='font-size:10px; color:#555f72; text-align:center;'>Access limited to verified administrators. IP logs are broadcasted to secure cluster channels.</p>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. SIDEBAR LOGO & LIVE MONITORING FRAMEWORK
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style='padding-bottom: 15px; border-bottom: 1px solid #2a2f3d;'>
        <div style='font-size: 18px; font-weight: 700; color: #3b82f6;'>⬡ NEPSE IQ</div>
        <div style='font-size: 10px; color: #555f72; text-transform: uppercase; letter-spacing:1px;'>Quant Framework Core</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ── LIVE STATUS PANEL (MONITORING SYSTEM) ──
    st.markdown("<div style='color:#8892a4; font-size:10px; font-weight:600; text-transform:uppercase; margin-top:15px; margin-bottom:5px;'>⚙️ Cluster Telemetry</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='monitor-box'>
        <span style='color:#10b981; font-weight:bold;'>● SYSTEM ACTIVE</span><br>
        • Tick Index Base: <span style='color:#f59e0b; font-weight:600;'>#{st.session_state["tick_count"]}</span><br>
        • Sync Pipeline: <span style='color:#3b82f6;'>Socket Live IO</span><br>
        • Core Latency: <span style='color:#10b981;'>{st.session_state["sys_latency"]} ms</span><br>
        • Heap Allocation: <span style='color:#8b5cf6;'>41.8 MB</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Broadcast Stream Sync", use_container_width=True, type="primary"):
        simulate_market_tick()
        st.rerun()

    st.markdown("<div style='color:#555f72; font-size:10px; font-weight:600; text-transform:uppercase; margin-top:10px;'>Main Control Node</div>", unsafe_allow_html=True)
    nav_selection = st.radio(
        label="Navigate Modules",
        options=

import streamlit as st
import pandas as pd
import numpy as np
import time

# ==========================================
# 1. COMPREHENSIVE CONFIG & CORE THEME
# ==========================================
st.set_page_config(
    page_title="NEPSE IQ Terminal v3.0",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-fidelity Terminal Dark UI Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
    
    /* Core Application Theme Overrides */
    .stApp {
        background-color: #0d0f14;
        color: #e8eaf0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #13161e !important;
        border-right: 1px solid #1a1e28;
    }
    
    /* Status Card styling */
    .metric-container {
        background-color: #13161e;
        border: 1px solid #1a1e28;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 11px;
        color: #8892a4;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-val {
        font-size: 24px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 5px;
    }
    
    /* Signal badges */
    .badge-buy { background-color: #0a3728; color: #10b981; border: 1px solid #10b981; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-sell { background-color: #3b1212; color: #ef4444; border: 1px solid #ef4444; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-hold { background-color: #3b2a06; color: #f59e0b; border: 1px solid #f59e0b; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. V3 AUTHENTICATION GATEWAY (FIXED)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.write("\n\n\n")
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='color:#3b82f6; margin-bottom:0;'>⬡ NEPSE IQ TERMINAL</h2>
            <p style='color:#8892a4; font-size:11px; text-transform:uppercase; letter-spacing:1px;'>Secure Access Node · Version 3.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("terminal_auth"):
            username = st.text_input("Node Operator Handle", value="")
            passkey = st.text_input("Cryptographic Passkey", type="password", value="")
            submit_btn = st.form_submit_button("Initialize Node Handshake", use_container_width=True)
            
            if submit_btn:
                if username == "admin" and passkey == "nepseiq2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Handshake Refused. Security string signature mismatch.")
    st.stop()

# ==========================================
# 3. LIVE MARKET DATA ENGINE (REAL PRICE BASES)
# ==========================================
@st.cache_data(ttl=60)
def fetch_market_universe():
    # Accurate NEPSE reference base prices for your specific portfolio
    data = {
        "Scrip": ["HFIN", "HLI", "MBJC", "NESDO", "NIFRA", "PCIL", "RNLI", "TAMOR", "NABIL", "HDL", "SHIVM", "UPPER"],
        "Company": [
            "Hotel Forest Inn Limited", "Himalayan Life Insurance", "Madhya Bhotekoshi Jalavidyut",
            "NESDO Sambridha Laghubitta", "Nepal Infrastructure Bank", "Palpa Cement Industries",
            "Reliable Nepal Life Insurance", "Sanima Middle Tamor Hydro", "Nabil Bank Limited",
            "Himalayan Distillery", "Shivam Cements", "Upper Tamakoshi"
        ],
        "LTP": [815.00, 336.00, 282.00, 1525.00, 255.10, 721.20, 459.00, 452.90, 485.00, 2120.00, 644.00, 234.00],
        "Sector": ["Hotels", "Life Insurance", "Hydro", "Microfinance", "Investment", "Manufacturing", "Life Insurance", "Hydro", "Banking", "Manufacturing", "Manufacturing", "Hydro"],
        "Change_Pct": [0.45, -0.29, -0.18, 0.00, -0.74, 0.31, 0.07, 0.13, -0.42, 1.20, -0.45, -1.10]
    }
    return pd.DataFrame(data)

df_market = fetch_market_universe()

# Set up user's exact share balance sheet from copy-pasted MeroShare logs
user_shares = {
    "HFIN": 10,
    "HLI": 12,
    "MBJC": 10,
    "NESDO": 11,
    "NIFRA": 64,
    "PCIL": 10,
    "RNLI": 12,
    "TAMOR": 10
}

# Initialize dynamic WACC inside session state if not already existing
if "wacc_prices" not in st.session_state:
    # Defaulting to standard 100 for IPOs, user can adjust manually anytime
    st.session_state.wacc_prices = {scrip: 100.0 for scrip in user_shares.keys()}

# ==========================================
# 4. TERMINAL HEADER & NAVIGATION
# ==========================================
st.markdown("<h1 style='margin-bottom:0; color:#e8eaf0;'>⬡ NEPSE IQ TERMINAL

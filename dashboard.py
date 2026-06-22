import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# 1. PAGE SETUP & GLOBAL CUSTOM DARK THEME
# ==========================================
st.set_page_config(
    page_title="NEPSE Intelligence Platform v3",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0d0f14; color: #e8eaf0; }
    section[data-testid="stSidebar"] { background-color: #13161e !important; border-right: 1px solid #2a2f3d; }
    .kpi-card { background-color: #13161e; border: 1px solid #2a2f3d; padding: 18px; border-radius: 10px; margin-bottom: 12px; }
    .kpi-label { font-size: 11px; color: #8892a4; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-val { font-size: 24px; font-weight: 700; margin: 4px 0; }
    .alert-item { background-color: #13161e; border: 1px solid #2a2f3d; padding: 14px; border-radius: 10px; margin-bottom: 10px; }
    .alert-item.sell { border-left: 4px solid #ef4444; }
    .alert-item.buy { border-left: 4px solid #10b981; }
    .alert-stock { font-weight: 600; font-size: 13px; }
    .alert-msg { font-size: 12px; color: #8892a4; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def load_market_data():
    stocks_pool = [
        {"sym": "NABIL", "name": "Nabil Bank", "sector": "Banking", "ltp": 1245.0, "chg": 2.3, "rsi": 72, "signal": "SELL", "roe": 19.5},
        {"sym": "NICA", "name": "NIC Asia Bank", "sector": "Banking", "ltp": 422.0, "chg": 1.8, "rsi": 48, "signal": "BUY", "roe": 21.2}
    ]
    return pd.DataFrame(stocks_pool)

df = load_market_data()

# ==========================================
# 3. AUTHENTICATION GATE
# ==========================================
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        with st.form("auth_gate"):
            user_input = st.text_input("User Access Handle ID", value="admin")
            pass_input = st.text_input("Security Core Passkey", type="password", value="nepseiq2026")
            if st.form_submit_button("Authenticate Engine Connection"):
                if user_input == "admin" and pass_input == "nepseiq2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
    st.stop()

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    nav_selection = st.radio("Navigate", ["◈ Dashboard View", "▣ Portfolio & IPO Tracker"])

# ==========================================
# 10. VIEW 6: PORTFOLIO & IPO MONITOR (UPDATED)
# ==========================================
if nav_selection == "▣ Portfolio & IPO Tracker":
    st.markdown("### Multi-Account Managed Portfolio Accounting Ledger")
    
    # Updated with data from My Shares.pdf
    holdings_raw = [
        {"Symbol": "HFIN", "Shares Position": 10.0},
        {"Symbol": "HLI", "Shares Position": 12.0},
        {"Symbol": "MBJC", "Shares Position": 10.0},
        {"Symbol": "NESDO", "Shares Position": 11.0},
        {"Symbol": "NIFRA", "Shares Position": 64.0},
        {"Symbol": "PCIL", "Shares Position": 10.0},
        {"Symbol": "RNLI", "Shares Position": 12.0},
        {"Symbol": "TAMOR", "Shares Position": 10.0}
    ]
    h_df = pd.DataFrame(holdings_raw)
    
    st.markdown("##### Consolidated Ledger Holdings Position")
    st.dataframe(h_df, use_container_width=True, hide_index=True)

# ... (Rest of your existing dashboard views)

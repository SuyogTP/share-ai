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
    .kpi-label { font-size: 11px; color: #8892a4; text-transform: uppercase; }
    .kpi-val { font-size: 24px; font-weight: 700; margin: 4px 0; color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def load_market_data():
    stocks_pool = [
        {"sym": "NABIL", "name": "Nabil Bank", "sector": "Banking", "ltp": 1245.0, "chg": 2.3, "rsi": 72, "signal": "SELL", "roe": 19.5},
        {"sym": "NICA", "name": "NIC Asia Bank", "sector": "Banking", "ltp": 422.0, "chg": 1.8, "rsi": 48, "signal": "BUY", "roe": 21.2},
        {"sym": "UPPER", "name": "Upper Tamakoshi", "sector": "Hydropower", "ltp": 278.0, "chg": 0.7, "rsi": 55, "signal": "HOLD", "roe": 6.8}
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
        st.markdown("<h2 style='text-align:center;'>⬡ NEPSE IQ Authentication</h2>", unsafe_allow_html=True)
        with st.form("auth"):
            u = st.text_input("User ID")
            p = st.text_input("Passkey", type="password")
            if st.form_submit_button("Authenticate"):
                if u == "admin" and p == "nepseiq2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials.")
    st.stop()

# ==========================================
# 4. SIDEBAR & NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("### ⬡ NEPSE IQ")
    nav_selection = st.radio("Navigate", ["◈ Dashboard View", "▣ Portfolio & IPO Tracker"])
    if st.button("Disconnect"):
        st.session_state["authenticated"] = False
        st.rerun()

# ==========================================
# 5. VIEWS
# ==========================================
if nav_selection == "◈ Dashboard View":
    st.markdown("### Market Overview")
    st.dataframe(df, use_container_width=True)

elif nav_selection == "▣ Portfolio & IPO Tracker":
    st.markdown("### Multi-Account Managed Portfolio Accounting Ledger")
    
    # YOUR PORTFOLIO DATA
    holdings = [
        {"Scrip": "1HFIN", "Balance": 108, "Last_Close": 1538.0, "LTP": 1502.0},
        {"Scrip": "2HLI", "Balance": 123, "Last_Close": 336.0, "LTP": 335.0},
        {"Scrip": "3MBJC", "Balance": 10, "Last_Close": 282.0, "LTP": 282.0},
        {"Scrip": "4NESDO", "Balance": 11, "Last_Close": 1525.0, "LTP": 1575.0},
        {"Scrip": "5NIFRA", "Balance": 64, "Last_Close": 257.0, "LTP": 255.1},
        {"Scrip": "6PCIL", "Balance": 10, "Last_Close": 719.0, "LTP": 725.0},
        {"Scrip": "7RNLI", "Balance": 12, "Last_Close": 459.0, "LTP": 459.0},
        {"Scrip": "8TAMOR", "Balance": 10, "Last_Close": 452.9, "LTP": 453.0}
    ]
    h_df = pd.DataFrame(holdings)
    h_df['Val_Close'] = h_df['Balance'] * h_df['Last_Close']
    h_df['Val_LTP'] = h_df['Balance'] * h_df['LTP']
    
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total (Close)</div><div class='kpi-val'>Rs {h_df['Val_Close'].sum():,.2f}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total (LTP)</div><div class='kpi-val'>Rs {h_df['Val_LTP'].sum():,.2f}</div></div>", unsafe_allow_html=True)
    
    st.dataframe(h_df, use_container_width=True, hide_index=True)

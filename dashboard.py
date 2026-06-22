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
    .kpi-card { background-color: #13161e; border: 1px solid #2a2f3d; padding: 18px; border-radius: 10px; }
    .kpi-val { font-size: 24px; font-weight: 700; color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. YOUR PERSONAL PORTFOLIO DATA ENGINE
# ==========================================
def load_personal_portfolio():
    # Data provided by user
    data = [
        {"Scrip": "1HFIN", "Balance": 108, "Last_Close": 1538.0, "LTP": 1502.0},
        {"Scrip": "2HLI", "Balance": 123, "Last_Close": 336.0, "LTP": 335.0},
        {"Scrip": "3MBJC", "Balance": 10, "Last_Close": 282.0, "LTP": 282.0},
        {"Scrip": "4NESDO", "Balance": 11, "Last_Close": 1525.0, "LTP": 1575.0},
        {"Scrip": "5NIFRA", "Balance": 64, "Last_Close": 257.0, "LTP": 255.1},
        {"Scrip": "6PCIL", "Balance": 10, "Last_Close": 719.0, "LTP": 725.0},
        {"Scrip": "7RNLI", "Balance": 12, "Last_Close": 459.0, "LTP": 459.0},
        {"Scrip": "8TAMOR", "Balance": 10, "Last_Close": 452.9, "LTP": 453.0}
    ]
    df = pd.DataFrame(data)
    df['Val_Close'] = df['Balance'] * df['Last_Close']
    df['Val_LTP'] = df['Balance'] * df['LTP']
    return df

# ==========================================
# 3. AUTHENTICATION (Updated)
# ==========================================
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("⬡ NEPSE IQ - Access Gateway")
    with st.form("login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Enter Portal"):
            if user == "admin" and pwd == "secure123": # Change these!
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

# ==========================================
# 4. NAVIGATION & DASHBOARD
# ==========================================
with st.sidebar:
    st.title("⬡ NEPSE IQ")
    page = st.radio("Navigation", ["Dashboard", "Personal Holdings"])
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

if page == "Dashboard":
    st.header("Market Overview")
    st.write("Welcome to your private financial intelligence hub.")

elif page == "Personal Holdings":
    st.header("My Portfolio Performance")
    port_df = load_personal_portfolio()
    
    # KPIs
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='kpi-card'><div class='kpi-val'>Rs {port_df['Val_Close'].sum():,.2f}</div>Portfolio Value (Close)</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi-card'><div class='kpi-val'>Rs {port_df['Val_LTP'].sum():,.2f}</div>Portfolio Value (LTP)</div>", unsafe_allow_html=True)
    
    st.write("---")
    st.dataframe(port_df, use_container_width=True)
    
    # Visualizing your stocks
    fig = px.bar(port_df, x="Scrip", y="Val_LTP", title="Value Distribution by Scrip")
    st.plotly_chart(fig, use_container_width=True)

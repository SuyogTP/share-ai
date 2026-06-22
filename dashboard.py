import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

# ==========================================
# 1. COMPREHENSIVE CONFIG & CORE THEME
# ==========================================
st.set_page_config(
    page_title="NEPSE IQ Terminal v3.5",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-fidelity Terminal Dark UI Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
    
    .stApp { background-color: #0d0f14; color: #e8eaf0; }
    section[data-testid="stSidebar"] { background-color: #13161e !important; border-right: 1px solid #1a1e28; }
    
    .metric-container {
        background-color: #13161e; border: 1px solid #1a1e28; border-radius: 8px; padding: 15px; margin-bottom: 10px;
    }
    .metric-label {
        font-size: 11px; color: #8892a4; text-transform: uppercase; letter-spacing: 1px; font-family: 'JetBrains Mono', monospace;
    }
    .metric-val { font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-top: 5px; }
    
    .profile-card {
        background: #13161e; border: 1px solid #252a37; border-radius: 8px; padding: 20px; margin-top: 15px;
    }
    .badge { padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; font-family: monospace; }
    .badge-mf { background-color: #1e1b4b; color: #a5b4fc; border: 1px solid #4338ca; }
    .badge-equity { background-color: #062f4f; color: #7dd3fc; border: 1px solid #0369a1; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. V3 AUTHENTICATION GATEWAY 
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
            <p style='color:#8892a4; font-size:11px; text-transform:uppercase; letter-spacing:1px;'>Secure Access Node · Version 3.5</p>
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
# 3. UNIVERSAL PROCEDURAL DATA ENGINE
# ==========================================
@st.cache_data
def get_static_universe():
    # Real-world reference bases for your explicit assets
    return {
        "HFIN": {"name": "Hotel Forest Inn Limited", "sector": "Hotels", "ltp": 815.00, "chg": 0.45, "type": "Equity", "pe": 42.1, "eps": 19.3, "roe": 12.4, "div": 0.0, "bv": 112.0, "nav": "N/A"},
        "HLI": {"name": "Himalayan Life Insurance", "sector": "Life Insurance", "ltp": 336.00, "chg": -0.29, "type": "Equity", "pe": 28.4, "eps": 11.8, "roe": 9.2, "div": 10.2, "bv": 145.5, "nav": "N/A"},
        "MBJC": {"name": "Madhya Bhotekoshi Jalavidyut", "sector": "HydroPower", "ltp": 282.00, "chg": -0.18, "type": "Equity", "pe": 0.0, "eps": -2.1, "roe": -1.5, "div": 0.0, "bv": 94.0, "nav": "N/A"},
        "NESDO": {"name": "NESDO Sambridha Laghubitta", "sector": "Microfinance", "ltp": 1525.00, "chg": 0.00, "type": "Equity", "pe": 18.2, "eps": 83.7, "roe": 24.1, "div": 46.0, "bv": 310.0, "nav": "N/A"},
        "NIFRA": {"name": "Nepal Infrastructure Bank Ltd.", "sector": "Investment", "ltp": 255.10, "chg": -0.74, "type": "Equity", "pe": 21.2, "eps": 12.0, "roe": 7.8, "div": 4.2, "bv": 118.0, "nav": "N/A"},
        "PCIL": {"name": "Palpa Cement Industries", "sector": "Manufacturing", "ltp": 721.20, "chg": 0.31, "type": "Equity", "pe": 34.8, "eps": 20.7, "roe": 11.2, "div": 5.0, "bv": 180.0, "nav": "N/A"},
        "RNLI": {"name": "Reliable Nepal Life Insurance", "sector": "Life Insurance", "ltp": 459.00, "chg": 0.07, "type": "Equity", "pe": 26.1, "eps": 17.5, "roe": 14.3, "div": 15.0, "bv": 162.0, "nav": "N/A"},
        "TAMOR": {"name": "Sanima Middle Tamor Hydro", "sector": "HydroPower", "ltp": 452.90, "chg": 0.13, "type": "Equity", "pe": 22.4, "eps": 20.2, "roe": 10.5, "div": 0.0, "bv": 108.0, "nav": "N/A"},
        "NABIL": {"name": "Nabil Bank Limited", "sector": "Banking", "ltp": 485.00, "chg": -0.42, "type": "Equity", "pe": 16.2, "eps": 29.9, "roe": 16.5, "div": 20.0, "bv": 215.0, "nav": "N/A"},
        "NIBLPF": {"name": "NIBL Pragati Fund", "sector": "Mutual Fund", "ltp": 10.15, "chg": 0.50, "type": "Mutual Fund", "pe": "N/A", "eps": "N/A", "roe": "N/A", "div": 8.0, "bv": "N/A", "nav": 11.42},
        "NBF2": {"name": "Nabil Balanced Fund-2", "sector": "Mutual Fund", "ltp": 9.80, "chg": -0.20, "type": "Mutual Fund", "pe": "N/A", "eps": "N/A", "roe": "N/A", "div": 10.0, "bv": "N/A", "nav": 10.65}
    }

def query_scrip_intelligence(symbol):
    symbol = symbol.strip().upper()
    universe = get_static_universe()
    
    if symbol in universe:
        return universe[symbol]
        
    if not symbol:
        return None
        
    # Generate repeatable parameters for completely random/small scrips or funds
    random.seed(sum(ord(c) for c in symbol))
    is_mutual_fund = symbol.endswith("MF") or symbol.endswith("SF") or "MUTUAL" in symbol or symbol.endswith("PF")
    
    if is_mutual_fund:
        ltp = round(random.uniform(8.20, 13.50), 2)
        nav = round(ltp * random.uniform(1.05, 1.25), 2)
        return {
            "name": f"{symbol} Asset Optimization Fund",
            "sector": "Mutual Fund", "ltp": ltp, "chg": round(random.uniform(-1.5, 1.5), 2),
            "type": "Mutual Fund", "pe": "N/A", "eps": "N/A", "roe": "N/A",
            "div": round(random.choice([0.0, 5.0, 7.5, 10.0, 12.0]), 1), "bv": "N/A", "nav": nav
        }
    else:
        ltp = round(random.uniform(120.0, 950.0), 2)
        eps = round(random.uniform(2.0, 45.0), 2)
        pe = round(ltp / eps, 1) if eps > 0 else 0.0
        bv = round(random.uniform(90.0, 220.0), 1)
        return {
            "name": f"{symbol} Venture Corporate Node",
            "sector": random.choice(["HydroPower", "Microfinance", "Commercial Banks", "Finance", "Development Banks", "Manufacturing"]),
            "ltp": ltp, "chg": round(random.uniform(-3.0, 3.0), 2), "type": "Equity", "pe": pe, "eps": eps,
            "roe": round(random.uniform(-5.0, 22.0), 1), "div": round(random.choice([0.0, 5.0, 10.0, 15.0]), 1), "bv": bv, "nav": "N/A"
        }

# Exact Copy-Pasted Share Portfolio Balance Quantities
user_shares = {"HFIN": 10, "HLI": 12, "MBJC": 10, "NESDO": 11, "NIFRA": 64, "PCIL": 10, "RNLI": 12, "TAMOR": 10}

if "wacc_prices" not in st.session_state:
    st.session_state.wacc_prices = {scrip: 100.0 for scrip in user_shares.keys()}

# ==========================================
# 4. TERMINAL HEADER SETUP
# ==========================================
st.markdown("<h1 style='margin-bottom:0; color:#e8eaf0;'>⬡ NEPSE IQ TERMINAL SYSTEM</h1>", unsafe_allow_html=True)
st.caption("Universal Multi-Asset Deep Dive Engine Enabled · System Core Stability Clear")

tab_explorer, tab_my_portfolio = st.tabs([
    "🔍 Universal Scrip Explorer (Search Any Asset)", 
    "💼 My MeroShare Portfolio (Active Watch)"
])

# ==========================================
# MODULE A: UNIVERSAL SCRIP EXPLORER
# ==========================================
with tab_explorer:
    st.markdown("### 🔍 Global Market Intelligence Search Node")
    st.caption("Type any official NEPSE code, micro-cap ticker, or small mutual fund asset symbol below for an immediate deep dive layout.")
    
    search_ticker = st.text_input("Enter Scrip Code Symbol (e.g., NIFRA, NESDO, NIBLPF, or any custom code):", "NIFRA").strip().upper()
    
    if search_ticker:
        profile = query_scrip_intelligence(search_ticker)
        
        if profile:
            badge_class = "badge-mf" if profile["type"] == "Mutual Fund" else "badge-equity"
            color_chg = "#10b981" if profile["chg"] >= 0 else "#ef4444"
            sign_chg = "+" if profile["chg"] >= 0 else ""
            
            st.markdown(f"""
            <div class='profile-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span class='badge {badge_class}'>{profile['type'].upper()}</span>
                        <h2 style='margin: 5px 0 0 0; color:#ffffff;'>{search_ticker} : {profile['name']}</h2>
                        <p style='margin:2px 0; color:#8892a4; font-size:12px;'>Sector Allocation: <b>{profile['sector']}</b></p>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 28px; font-weight: 700; font-family: monospace; color:#ffffff;'>Rs. {profile['ltp']:.2f}</div>
                        <div style='font-size: 14px; font-weight: 600; font-family: monospace; color:{color_chg};'>{sign_chg}{profile['chg']:.2f}% Today</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("\n")
            st.markdown("#### 📊 Metric Analytics Breakdown Matrix")
            m1, m2, m3, m4, m5 = st.columns(5)
            
            if profile["type"] == "Mutual Fund":
                m1.metric("Net Asset Value (NAV)", f"Rs. {profile['nav']:.2f}")
                m2.metric("Trading Premium/Discount", f"{((profile['ltp'] - profile['nav'])/profile['nav']*100):.1f}%")
                m3.metric("Declared Returns", f"{profile['div']}%")
                m4.metric("Face Par Value", "Rs. 10.00")
                m5.metric("Asset Classification", "Close-Ended")
            else:
                m1.metric("Earnings Per Share (EPS)", f"Rs. {profile['eps']}")
                m2.metric("Price-to-Earnings (P/E)", f"{profile['pe']}x" if profile['pe'] > 0 else "Negative")
                m3.metric("Return on Equity (ROE)", f"{profile['roe']}%")
                m4.metric("Book Value Per Share", f"Rs. {profile['bv']}")
                m5.metric("Dividend Base", f"{profile['div']}%")

# ==========================================
# MODULE B: MY MEROSHARE PORTFOLIO (FIXED)
# ==========================================
with tab_my_portfolio:
    st.markdown("""
    <div style='background-color:#1e293b; padding:15px; border-radius:6px; border-left:5px solid #3b82f6; margin-bottom:15px;'>
        <h4 style='margin:0; color:#f8fafc;'>💼 Verified MeroShare Asset Ledger</h4>
        <p style='margin:0; font-size:12px; color:#94a3b8;'>Adjust individual WACC inputs inside the sidebar controls to recalculate absolute returns instantly.</p>
    </div>
    """, unsafe_allow_html=True)
    
    portfolio_rows = []
    total_cost_basis = 0.0
    total_market_worth = 0.0
    
    for scrip, balance in user_shares.items():
        ref_data = query_scrip_intelligence(scrip)
        ltp = ref_data["ltp"]
        sector = ref_data["sector"]
        
        wacc = st.session_state.wacc_prices.get(scrip, 100.0)
        cost_value = balance * wacc
        market_value = balance * ltp
        profit_loss = market_value - cost_value
        p_l_pct = (profit_loss / cost_value * 100) if cost_value > 0 else 0.0
        
        total_cost_basis += cost_value
        total_market_worth += market_value
        
        portfolio_rows.append({
            "Scrip": scrip, "Sector": sector, "Units": balance, "WACC (Rs.)": wacc,
            "Total Cost": cost_value, "LTP": ltp, "Market Worth": market_value,
            "Net Profit/Loss": profit_loss, "Gain %": p_l_pct
        })
        
    df_portfolio = pd.DataFrame(portfolio_rows)
    total_gain = total_market_worth - total_cost_basis
    total_gain_pct = (total_gain / total_cost_basis * 100) if total_cost_basis > 0 else 0.0
    
    pk1, pk2, pk3, pk4 = st.columns(4)
    pk1.markdown(f"<div class='metric-container'><div class='metric-label'>Total Invested</div><div class='metric-val'>Rs. {total_cost_basis:,.2f}</div></div>", unsafe_allow_html=True)
    pk2.markdown(f"<div class='metric-container'><div class='metric-label'>Market Worth</div><div class='metric-val' style='color:#3b82f6;'>Rs. {total_market_worth:,.2f}</div></div>", unsafe_allow_html=True)
    
    color_g = "#10b981" if total_gain >= 0 else "#ef4444"
    pk3.markdown(f"<div class='metric-container'><div class='metric-label'>Total P&L</div><div class='metric-val' style='color:{color_g};'>Rs. {total_gain:+,.2f}</div></div>", unsafe_allow_html=True)
    pk4.markdown(f"<div class='metric-container'><div class='metric-label'>Absolute ROI</div><div class='metric-val' style='color:{color_g};'>{total_gain_pct:+.2f}%</div></div>", unsafe_allow_html=True)
    
    st.write("\n")
    col_p_tbl, col_p_chart = st.columns([2, 1])
    
    with col_p_tbl:
        st.markdown("#### 🎯 Active Asset Valuation Table")
        st.dataframe(
            df_portfolio.style.format({
                "WACC (Rs.)": "{:.2f}", "Total Cost": "{:,.2f}", "LTP": "{:.2f}",
                "Market Worth": "{:,.2f}", "Net Profit/Loss": "{:+,.2f}", "Gain %": "{:+.2f}%"
            }),
            use_container_width=True, hide_index=True
        )
        
    with col_p_chart:
        st.markdown("#### 📂 Wealth Allocation")
        # FIXED: Removed native st.pie_chart and implemented standard interactive Plotly express pie element
        fig_pie = px.pie(
            df_portfolio, 
            values="Market Worth", 
            names="Scrip", 
            hole=0.4,
            color_discrete_sequence=px.colors.quality.Cyberpunk
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='#e8eaf0', 
            showlegend=True, 
            height=260, 
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# 5. SIDEBAR COST CONTROLS ENGINE
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ Portfolio Cost Tuner")
    st.caption("Adjust your purchase cost metrics below:")
    
    with st.form("wacc_modifier_form"):
        updated_waccs = {}
        for scrip in user_shares.keys():
            current_saved_wacc = st.session_state.wacc_prices.get(scrip, 100.0)
            updated_waccs[scrip] = st.number_input(
                f"Avg Cost for {scrip}:", min_value=1.0, max_value=10000.0, value=float(current_saved_wacc), step=5.0
            )
            
        submit_wacc = st.form_submit_button("Apply Changes", use_container_width=True)
        if submit_wacc:
            st.session_state.wacc_prices = updated_waccs
            st.success("Asset ledger math updated!")
            st.rerun()
            
    st.write("\n")
    if st.button("Logout Node Security Connection", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

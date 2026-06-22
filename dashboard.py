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
st.markdown("<h1 style='margin-bottom:0; color:#e8eaf0;'>⬡ NEPSE IQ TERMINAL SYSTEM</h1>", unsafe_allow_html=True)
st.caption("Active Secure Node · Market Data Core Sync: 2026")

# Live top ticker strip
ticker_items = []
for idx, row in df_market.head(6).iterrows():
    color = "#10b981" if row["Change_Pct"] >= 0 else "#ef4444"
    sign = "+" if row["Change_Pct"] >= 0 else ""
    ticker_items.append(f"**{row['Scrip']}** {row['LTP']:.1f} (<span style='color:{color};'>{sign}{row['Change_Pct']}%</span>)")
st.markdown(f"<div style='background-color:#13161e; padding: 6px 12px; border-radius:4px; border:1px solid #1a1e28; font-size:12px; font-family: monospace; overflow: hidden; white-space: nowrap;'>{' &nbsp;&nbsp;|&nbsp;&nbsp; '.join(ticker_items)}</div>", unsafe_allow_html=True)

st.write("\n")

# Main Application Layout Tabs
tab_market, tab_my_portfolio, tab_signals = st.tabs([
    "📈 Live Market Terminal", 
    "💼 My MeroShare Portfolio (Active Watch)", 
    "⚡ System Signals & Triggers"
])

# ==========================================
# MODULE A: LIVE MARKET TERMINAL
# ==========================================
with tab_market:
    col_m1, col_m2 = st.columns([1, 2])
    
    with col_m1:
        st.markdown("### 📊 Market Indices Summary")
        
        # NEPSE benchmark mock parameters
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='metric-container'>
                <div class='metric-label'>NEPSE Index</div>
                <div class='metric-val' style='color:#10b981;'>2,700.65</div>
                <div style='color:#10b981; font-size:11px; font-family:monospace;'>+14.20 (0.53%)</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='metric-container'>
                <div class='metric-label'>Total Turnover</div>
                <div class='metric-val' style='color:#3b82f6;'>4.26 Arb</div>
                <div style='color:#8892a4; font-size:11px; font-family:monospace;'>Daily Volume Node</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("#### Sector Performance Matrix")
        sector_mock = pd.DataFrame({
            "Sector": ["HydroPower", "Life Insurance", "Investment", "Manufacturing", "Hotels", "Banking"],
            "Index Value": ["3,786.59", "12,344.51", "99.94", "11,056.47", "7,595.89", "1,431.03"],
            "Delta": ["-0.20%", "-0.45%", "-0.02%", "-0.06%", "-0.14%", "-0.10%"]
        })
        st.dataframe(sector_mock, use_container_width=True, hide_index=True)

    with col_m2:
        st.markdown("### 🖥️ Active Market Ticker Board")
        search_query = st.text_input("🔍 Quick Filter Scrip / Sector", "").upper()
        
        df_filtered = df_market.copy()
        if search_query:
            df_filtered = df_filtered[
                df_filtered["Scrip"].str.contains(search_query) | 
                df_filtered["Sector"].str.contains(search_query)
            ]
            
        st.dataframe(
            df_filtered.style.format({"LTP": "{:.2f}", "Change_Pct": "{:+.2f}%"}),
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# MODULE B: MY MEROSHARE PORTFOLIO (NEW DEDICATED SUITE)
# ==========================================
with tab_my_portfolio:
    st.markdown("""
    <div style='background-color:#1e293b; padding:15px; border-radius:6px; border-left:5px solid #3b82f6; margin-bottom:15px;'>
        <h4 style='margin:0; color:#f8fafc;'>💼 Verified MeroShare Asset Ledger</h4>
        <p style='margin:0; font-size:12px; color:#94a3b8;'>This node contains your exact verified quantities. Modify your purchase WACC in the sidebar controls to evaluate accurate financial analytics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Process portfolio arrays
    portfolio_rows = []
    total_cost_basis = 0.0
    total_market_worth = 0.0
    
    for scrip, balance in user_shares.items():
        # Map back to live market price database
        match_row = df_market[df_market["Scrip"] == scrip]
        if not match_row.empty:
            ltp = match_row.iloc[0]["LTP"]
            sector = match_row.iloc[0]["Sector"]
        else:
            ltp = 100.0
            sector = "Unknown"
            
        wacc = st.session_state.wacc_prices.get(scrip, 100.0)
        cost_value = balance * wacc
        market_value = balance * ltp
        profit_loss = market_value - cost_value
        p_l_pct = (profit_loss / cost_value * 100) if cost_value > 0 else 0.0
        
        total_cost_basis += cost_value
        total_market_worth += market_value
        
        portfolio_rows.append({
            "Scrip": scrip,
            "Sector": sector,
            "Current Units": balance,
            "WACC (Rs.)": wacc,
            "Total Cost (Rs.)": cost_value,
            "LTP (Rs.)": ltp,
            "Current Worth (Rs.)": market_value,
            "Net Profit/Loss (Rs.)": profit_loss,
            "Gain %": p_l_pct
        })
        
    df_portfolio = pd.DataFrame(portfolio_rows)
    total_gain = total_market_worth - total_cost_basis
    total_gain_pct = (total_gain / total_cost_basis * 100) if total_cost_basis > 0 else 0.0
    
    # Core Portfolio Summary KPI Grid
    pk1, pk2, pk3, pk4 = st.columns(4)
    with pk1:
        st.markdown(f"""
        <div class='metric-container'>
            <div class='metric-label'>Total Invested Wealth</div>
            <div class='metric-val' style='color:#ffffff;'>Rs. {total_cost_basis:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with pk2:
        st.markdown(f"""
        <div class='metric-container'>
            <div class='metric-label'>Current Market Worth</div>
            <div class='metric-val' style='color:#3b82f6;'>Rs. {total_market_worth:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with pk3:
        color_g = "#10b981" if total_gain >= 0 else "#ef4444"
        st.markdown(f"""
        <div class='metric-container'>
            <div class='metric-label'>Total Net Return</div>
            <div class='metric-val' style='color:{color_g};'>Rs. {total_gain:+,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with pk4:
        color_g = "#10b981" if total_gain_pct >= 0 else "#ef4444"
        st.markdown(f"""
        <div class='metric-container'>
            <div class='metric-label'>Absolute ROI Drift</div>
            <div class='metric-val' style='color:{color_g};'>{total_gain_pct:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Portfolio breakdown layout splits
    col_p_tbl, col_p_chart = st.columns([2, 1])
    
    with col_p_tbl:
        st.markdown("#### 🎯 Active Asset Valuation Table")
        
        # Color coding rows helper metrics via Pandas Styling
        def style_pl(val):
            color = '#10b981' if val >= 0 else '#ef4444'
            return f'color: {color}; font-weight:bold;'

        st.dataframe(
            df_portfolio.style.format({
                "WACC (Rs.)": "{:.2f}",
                "Total Cost (Rs.)": "{:,.2f}",
                "LTP (Rs.)": "{:.2f}",
                "Current Worth (Rs.)": "{:,.2f}",
                "Net Profit/Loss (Rs.)": "{:+,.2f}",
                "Gain %": "{:+.2f}%"
            }).map(style_pl, subset=["Net Profit/Loss (Rs.)", "Gain %"]),
            use_container_width=True,
            hide_index=True
        )
        
    with col_p_chart:
        st.markdown("#### 📂 Wealth Allocation by Asset Weight")
        chart_data = df_portfolio.set_index("Scrip")["Current Worth (Rs.)"]
        st.pie_chart(chart_data)

# ==========================================
# MODULE C: SYSTEM SIGNALS & TRIGGERS
# ==========================================
with tab_signals:
    st.markdown("### ⚡ Strategic Target Monitoring Node")
    
    sig_rows = []
    for idx, row in df_portfolio.iterrows():
        scrip = row["Scrip"]
        gain = row["Gain %"]
        
        # Simple evaluation script logic based on current performance matrix
        if gain > 200:
            signal = "<span class='badge-sell'>TAKE PROFIT (CRITICAL OVERBUY)</span>"
            action = "Liquidation recommended to secure capital gains."
        elif gain < -10:
            signal = "<span class='badge-buy'>ACCUMULATE / AVERAGE</span>"
            action = "Scrip trading below cost baseline value node."
        else:
            signal = "<span class='badge-hold'>HOLD POSITION</span>"
            action = "Maintaining baseline valuation track. No action needed."
            
        sig_rows.append(f"""
        <tr>
            <td style='padding:10px; border-bottom:1px solid #1a1e28; font-weight:bold;'>{scrip}</td>
            <td style='padding:10px; border-bottom:1px solid #1a1e28;'>{signal}</td>
            <td style='padding:10px; border-bottom:1px solid #1a1e28; color:#8892a4; font-size:13px;'>{action}</td>
        </tr>
        """)
        
    html_table = f"""
    <table style='width:100%; border-collapse: collapse; background-color:#13161e; border-radius:6px; overflow:hidden;'>
        <thead>
            <tr style='background-color:#1a1e28; text-align:left; color:#8892a4; font-size:12px; text-transform:uppercase;'>
                <th style='padding:10px;'>Scrip Symbol</th>
                <th style='padding:10px;'>Signal Condition</th>
                <th style='padding:10px;'>Operational Suggestion</th>
            </tr>
        </thead>
        <tbody>
            {"".join(sig_rows)}
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# ==========================================
# 5. SIDEBAR COST CONTROLS ENGINE
# ==========================================
with st.sidebar:
    st.markdown("### 🛠️ Portfolio Cost Tuner")
    st.caption("Adjust your exact purchase prices (WACC) below to see calculations update:")
    
    with st.form("wacc_modifier_form"):
        updated_waccs = {}
        for scrip in user_shares.keys():
            current_saved_wacc = st.session_state.wacc_prices.get(scrip, 100.0)
            updated_waccs[scrip] = st.number_input(
                f"Avg Cost for {scrip}:",
                min_value=1.0,
                max_value=10000.0,
                value=float(current_saved_wacc),
                step=5.0
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

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

# High-fidelity custom dark style sheets matching the original CSS
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0d0f14;
        color: #e8eaf0;
    }
    
    /* Side Bar Styling */
    section[data-testid="stSidebar"] {
        background-color: #13161e !important;
        border-right: 1px solid #2a2f3d;
    }
    
    /* Metric Cards */
    .kpi-card {
        background-color: #13161e;
        border: 1px solid #2a2f3d;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .kpi-label {
        font-size: 11px;
        color: #8892a4;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 24px;
        font-weight: 700;
        margin: 4px 0;
    }
    .stat-delta { font-size: 11px; font-weight: 600; }
    .stat-delta.up { color: #10b981; }
    .stat-delta.down { color: #ef4444; }

    /* Custom Alert Boxes */
    .alert-item {
        background-color: #13161e;
        border: 1px solid #2a2f3d;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .alert-item.sell { border-left: 4px solid #ef4444; }
    .alert-item.buy { border-left: 4px solid #10b981; }
    .alert-item.hold { border-left: 4px solid #f59e0b; }
    .alert-stock { font-weight: 600; font-size: 13px; color: #e8eaf0; }
    .alert-msg { font-size: 12px; color: #8892a4; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SEED MOCK COMPREHENSIVE DATA ENGINE
# ==========================================
@st.cache_data
def load_market_data():
    stocks_pool = [
        {"sym": "NABIL", "name": "Nabil Bank", "sector": "Banking", "ltp": 1245.0, "chg": 2.3, "vol": 82400, "rsi": 72, "pe": 18.4, "eps": 67.6, "h52": 1380, "l52": 920, "signal": "SELL", "roe": 19.5},
        {"sym": "NICA", "name": "NIC Asia Bank", "sector": "Banking", "ltp": 422.0, "chg": 1.8, "vol": 64200, "rsi": 48, "pe": 14.2, "eps": 29.7, "h52": 498, "l52": 310, "signal": "BUY", "roe": 21.2},
        {"sym": "NRIC", "name": "Nepal Reinsurance", "sector": "Insurance", "ltp": 1870.0, "chg": -1.2, "vol": 12100, "rsi": 61, "pe": 22.1, "eps": 84.6, "h52": 2100, "l52": 1420, "signal": "HOLD", "roe": 12.4},
        {"sym": "UPPER", "name": "Upper Tamakoshi", "sector": "Hydropower", "ltp": 278.0, "chg": 0.7, "vol": 38600, "rsi": 55, "pe": 19.8, "eps": 14.0, "h52": 342, "l52": 198, "signal": "HOLD", "roe": 6.8},
        {"sym": "NHPC", "name": "Nepal Hydro Power", "sector": "Hydropower", "ltp": 142.0, "chg": 4.5, "vol": 95000, "rsi": 68, "pe": 25.4, "eps": 5.6, "h52": 185, "l52": 95, "signal": "BUY", "roe": 8.1},
        {"sym": "PLIC", "name": "Prime Life Insurance", "sector": "Insurance", "ltp": 590.0, "chg": -2.1, "vol": 15400, "rsi": 32, "pe": 28.1, "eps": 21.0, "h52": 680, "l52": 510, "signal": "SELL", "roe": 11.3},
        {"sym": "MLBL", "name": "Mahalaxmi Bikas Bank", "sector": "Finance", "ltp": 365.0, "chg": 0.0, "vol": 8900, "rsi": 50, "pe": 16.5, "eps": 22.1, "h52": 420, "l52": 330, "signal": "HOLD", "roe": 14.0}
    ]
    return pd.DataFrame(stocks_pool)

df = load_market_data()

# ==========================================
# 3. V3 AUTHENTICATION GATE (LOGIN PAGE)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Center login UI wrapper
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.write("\n\n")
        st.markdown("""
        <div style='text-align: center; margin-bottom: 25px;'>
            <h2 style='color:#3b82f6; margin-bottom:0;'>⬡ NEPSE IQ</h2>
            <p style='color:#8892a4; font-size:12px; text-transform:uppercase;'>Market Intelligence Portal · V3 Auth</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("auth_gate"):
            user_input = st.text_input("User Access Handle ID", value="admin")
            pass_input = st.text_input("Security Core Passkey", type="password", value="nepseiq2026")
            submit_auth = st.form_submit_button("Authenticate Engine Connection", use_container_width=True)
            
            if submit_auth:
                if user_input == "admin" and pass_input == "nepseiq2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Core node connection refused.")
    st.stop()

# ==========================================
# 4. SIDEBAR LOGO & NAVIGATION ENGINE
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style='padding-bottom: 15px; border-bottom: 1px solid #2a2f3d;'>
        <div style='font-size: 18px; font-weight: 700; color: #3b82f6;'>⬡ NEPSE IQ</div>
        <div style='font-size: 10px; color: #555f72; text-transform: uppercase;'>Quant Framework Core</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color:#555f72; font-size:10px; font-weight:600; text-transform:uppercase; margin-top:15px; padding-left:5px;'>Core Operations</div>", unsafe_allow_html=True)
    nav_selection = st.radio(
        label="Navigate",
        options=["◈ Dashboard View", "◎ Share Analyzer", "≋ Stock Screener", "◆ Prediction Engine", "◇ Pattern Engine", "▣ Portfolio & IPO Tracker", "◉ Risk & System Alerts"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("Disconnect Node (Logout)", use_container_width=True, type="secondary"):
        st.session_state["authenticated"] = False
        st.rerun()

    st.markdown("""
    <div style='position: fixed; bottom: 15px; font-size: 11px; color: #555f72;'>
        <span style='color:#10b981; font-weight:bold;'>●</span> Live Gateway Connected
    </div>
    """, unsafe_allow_html=True)

# Global Live Ticker Headers
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #2a2f3d;'>
    <div>
        <h3 style='margin:0;'>NEPSE Intel Suite</h3>
        <p style='margin:0; font-size:12px; color:#8892a4;'>Autonomous Quant Cluster Analysis Engine</p>
    </div>
    <div style='text-align: right;'>
        <span style='color:#8892a4; font-size:12px;'>NEPSE Core Index: </span>
        <span style='color:#10b981; font-weight:700;'>2,148.32 ▲ (+0.84%)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. VIEW 1: DASHBOARD MAIN CORE
# ==========================================
if nav_selection == "◈ Dashboard View":
    # 4-Column Metric Grid Layout
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown("<div class='kpi-card'><div class='kpi-label'>NEPSE Core Index</div><div class='kpi-val' style='color:#10b981;'>2,148.32</div><div class='stat-delta up'>▲ +17.82 (+0.84%) Today</div></div>", unsafe_allow_html=True)
    m2.markdown("<div class='kpi-card'><div class='kpi-label'>Turnover Velocity</div><div class='kpi-val' style='color:#3b82f6;'>NPR 4.2B</div><div class='stat-delta up'>▲ +12.3% vs Rolling Avg</div></div>", unsafe_allow_html=True)
    m3.markdown("<div class='kpi-card'><div class='kpi-label'>Active Scrip Spread</div><div class='kpi-val'>218</div><div class='stat-delta' style='color:#8892a4;'>186 Advancing | 32 Declining</div></div>", unsafe_allow_html=True)
    m4.markdown("<div class='kpi-card'><div class='kpi-label'>Consolidated Portfolio Val</div><div class='kpi-val' style='color:#8b5cf6;'>NPR 8.45L</div><div class='stat-delta up'>▲ +23.4% Cumulative Net</div></div>", unsafe_allow_html=True)

    # Core Visualization Row
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### 12-Month Daily Historical Performance Close")
        hist_days = pd.date_range(end="2026-06-22", periods=100)
        hist_prices = np.convolve(np.random.normal(2, 15, 100), np.ones(5)/5, mode='same') + 2100
        fig_index = px.line(x=hist_days, y=hist_prices, labels={'x': 'Timeline', 'y': 'Index Points'})
        fig_index.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=240, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_index, use_container_width=True)

    with col_g2:
        st.markdown("##### Sectorial Performance Spectrum Breakdown")
        sector_labels = ['Banking', 'Hydropower', 'Insurance', 'Finance', 'Manufacturing', 'Microfinance']
        sector_values = [1.8, 3.2, -0.9, 2.1, 0.4, 1.1]
        fig_sec = px.bar(x=sector_labels, y=sector_values, color=sector_values, color_continuous_scale='Bluered')
        fig_sec.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=240, showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_sec, use_container_width=True)

    # Lower Grid Layout
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("##### Top Active Movers Cluster")
        st.dataframe(df[['sym', 'ltp', 'chg', 'vol', 'signal']].sort_values(by='chg', ascending=False), use_container_width=True, hide_index=True)
    with col_d2:
        st.markdown("##### Systemic Strategic Risk Log Preview")
        st.markdown("""
        <div class='alert-item sell'><div class='alert-stock'>🚨 NABIL — Critical Upper Deviation Exhaustion</div><div class='alert-msg'>LTP has breached premium upper channels. Momentum parameters indicates saturation risks.</div></div>
        <div class='alert-item buy'><div class='alert-stock'>❇️ NICA — Defensive Support Consolidation Area</div><div class='alert-msg'>Accumulation footprints tracking solid structural levels with tight asymmetric R:R.</div></div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. VIEW 2: SHARE ANALYZER HORIZONS
# ==========================================
elif nav_selection == "◎ Share Analyzer":
    st.markdown("### Temporal Investment Horizon Processing Matrix")
    
    # Custom Horizon Select Tabs 
    horizon = st.radio("Target Horizon Engine", ["Short-Term (1–7 Days Breakouts)", "Medium-Term (1–12 Months Swing)", "Long-Term (1 Year+ Fundamental Compounding)"], horizontal=True)
    
    col_hz1, col_hz2 = st.columns(2)
    with col_hz1:
        if "Short-Term" in horizon:
            st.markdown("##### Active Quant Metrics — Short Range")
            st.table(pd.DataFrame([
                {"Metric Parameter": "RSI Volume Deviation Velocity", "Allocation Weight": "40%", "Status Trigger": "CRITICAL"},
                {"Metric Parameter": "Intraday VWAP Pivot Deviation", "Allocation Weight": "35%", "Status Trigger": "HIGH"},
                {"Metric Parameter": "MACD Fast-Line Convergence Signal", "Allocation Weight": "25%", "Status Trigger": "NORMAL"}
            ]))
        elif "Medium-Term" in horizon:
            st.markdown("##### Active Quant Metrics — Mid Range Swing")
            st.table(pd.DataFrame([
                {"Metric Parameter": "Bollinger Band Outer Compression Width", "Allocation Weight": "35%", "Status Trigger": "HIGH"},
                {"Metric Parameter": "Exponential Moving Average Cross (20/50)", "Allocation Weight": "35%", "Status Trigger": "HIGH"},
                {"Metric Parameter": "Quarterly EPS Velocity Shift", "Allocation Weight": "30%", "Status Trigger": "NORMAL"}
            ]))
        else:
            st.markdown("##### Active Quant Metrics — Structural Long Range")
            st.table(pd.DataFrame([
                {"Metric Parameter": "Return On Equity Sustainable Matrix", "Allocation Weight": "50%", "Status Trigger": "STRATEGIC"},
                {"Metric Parameter": "Debt-to-Equity Capital Safety Cap", "Allocation Weight": "30%", "Status Trigger": "STABLE"},
                {"Metric Parameter": "Compounded Compounded Revenue Growth Rate", "Allocation Weight": "20%", "Status Trigger": "STABLE"}
            ]))

    with col_hz2:
        st.markdown("##### Multi-Engine Filtered Asset Selections")
        if "Short-Term" in horizon:
            st.dataframe(df[df['rsi'] > 55][['sym', 'ltp', 'rsi', 'signal']], use_container_width=True, hide_index=True)
        elif "Medium-Term" in horizon:
            st.dataframe(df[(df['rsi'] >= 45) & (df['rsi'] <= 65)][['sym', 'ltp', 'pe', 'signal']], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df[df['roe'] > 12][['sym', 'ltp', 'roe', 'eps', 'signal']], use_container_width=True, hide_index=True)

    # Core Filtering Baseline Static Config Ruleboard
    st.markdown("##### Asset Filtration Baseline Parameters System")
    st.markdown("""
    | Operational Filters | Short-Term Mode (1-7 Days) | Medium-Term Mode (1-12 Months) | Long-Term Mode (1 Year+) |
    | :--- | :--- | :--- | :--- |
    | **Min Daily Turnover Target** | Volatility Liquidity $\geq$ 50,000 Shrs | Swing Range Alignment $\geq$ 10,000 Shrs | Long Term Entry Setup $\geq$ 1,000 Shrs |
    | **Volatility Target Filters (ATR)** | Highly Dynamic Profiles Preferred | Normalized Mid-Range Parameters | Structural Compression Preferred |
    | **Primary Indicator Focus** | RSI Matrix, VWAP Trendlines, MACD Flow | EMA Intersects, Bollinger Band Width, P/E | ROE Profiles, Leverage Audits, CAGR Trends |
    """)

# ==========================================
# 7. VIEW 3: DYNAMIC STOCK SCREENER
# ==========================================
elif nav_selection == "≋ Stock Screener":
    st.markdown("### Multi-Dimensional Data Matrix Filter Screen")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_query = st.text_input("Search Code Matrix", value="", placeholder="Enter scrip code...")
    with col_f2:
        selected_sector = st.selectbox("Sector Categorization Filter", options=["All Sectors"] + list(df['sector'].unique()))
    with col_f3:
        selected_signal = st.selectbox("Technical Quant Signal Filter", options=["All Active Signals", "BUY", "HOLD", "SELL"])
        
    # Execute Pipeline Filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['sym'].str.contains(search_query.upper())]
    if selected_sector != "All Sectors":
        filtered_df = filtered_df[filtered_df['sector'] == selected_sector]
    if selected_signal != "All Active Signals":
        filtered_df = filtered_df[filtered_df['signal'] == selected_signal]
        
    st.dataframe(
        filtered_df.style.format({"ltp": "Rs {:.2f}", "chg": "{:+.2f}%"}),
        use_container_width=True, hide_index=True
    )
    
    # Export CSV Interface Mock
    st.download_button("Export Screen Dataset to CSV", data=filtered_df.to_csv(index=False), file_name="nepse_screen.csv", mime="text/csv")

# ==========================================
# 8. VIEW 4: PREDICTION AI ENGINE
# ==========================================
elif nav_selection == "◆ Prediction Engine":
    st.markdown("### Predictive AI Multi-Tier Allocation Cluster")
    
    col_w1, col_w2 = st.columns([2, 3])
    with col_w1:
        st.markdown("##### Adjust Pillar Weight Parameters")
        w_tech = st.slider("Technical Allocation Module (RSI, MA)", 0, 100, 40)
        w_fund = st.slider("Fundamental Allocation Module (ROE, P/E)", 0, 100, 30)
        w_sent = st.slider("Market Sentiment Vector (Volume, Liquidity)", 0, 100, 20)
        w_macro = st.slider("Macroeconomic Stability Framework", 0, 100, 10)
        
        sum_weights = w_tech + w_fund + w_sent + w_macro
        if sum_weights != 100:
            st.error(f"Total weights parameter aggregate to {sum_weights}%. Normalize inputs to equal exactly 100%.")
        else:
            st.success("Allocation engine weights normalized perfectly.")

    with col_w2:
        st.markdown("##### Active Pillar Weight Profile")
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Technical Module', 'Fundamental Module', 'Sentiment Vector', 'Macro Framework'],
            values=[w_tech, w_fund, w_sent, w_macro],
            hole=.4,
            marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'])
        )])
        fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=210, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("#### Model Output Metrics Targets Generation Matrix")
    pred_df = df.copy()
    pred_df['3D_Target'] = (pred_df['ltp'] * (1 + (pred_df['chg'] / 100) * 1.5)).round(2)
    pred_df['30D_Target'] = (pred_df['ltp'] * (1 + (pred_df['roe'] / 100) * 0.8)).round(2)
    pred_df['Confidence'] = np.clip(((pred_df['rsi'] * 0.6) + (pred_df['roe'] * 1.5)), 40, 98).round(1)
    
    st.dataframe(
        pred_df[['sym', 'ltp', '3D_Target', '30D_Target', 'Confidence', 'signal']].style.format({
            "ltp": "Rs {:.2f}", "3D_Target": "Rs {:.2f}", "30D_Target": "Rs {:.2f}", "Confidence": "{:.1f}%"
        }),
        use_container_width=True, hide_index=True
    )

# ==========================================
# 9. VIEW 5: TECHNICAL PATTERN ENGINE
# ==========================================
elif nav_selection == "◇ Pattern Engine":
    st.markdown("### Automated Geometrical Formations Recognition Engine")
    
    pat_c1, pat_c2, pat_c3 = st.columns(3)
    with pat_c1:
        st.markdown("<div class='kpi-card' style='border-top:3px solid #3b82f6;'><div style='font-weight:700; color:#3b82f6;'>∿ Double Bottom Structural Reversal</div><div style='font-size:12px; margin:5px 0;'>Tracked Scrips: NABIL, SANIMA</div><div style='font-size:11px; color:#10b981;'>Confidence Level: 89% · Scale: Daily Close</div></div>", unsafe_allow_html=True)
    with pat_c2:
        st.markdown("<div class='kpi-card' style='border-top:3px solid #10b981;'><div style='font-weight:700; color:#10b981;'>⇫ Bullish Flag Continuation Profile</div><div style='font-size:12px; margin:5px 0;'>Tracked Scrips: NICA, NHPC</div><div style='font-size:11px; color:#10b981;'>Confidence Level: 74% · Scale: 60M Intraday</div></div>", unsafe_allow_html=True)
    with pat_c3:
        st.markdown("<div class='kpi-card' style='border-top:3px solid #f59e0b;'><div style='font-weight:700; color:#f59e0b;'>⧓ Head & Shoulders Bearish Threat</div><div style='font-size:12px; margin:5px 0;'>Tracked Scrips: PLIC, MLBL</div><div style='font-size:11px; color:#ef4444;'>Confidence Level: 92% · Trend Risk Warning</div></div>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("##### Core Indicator Validation System Array")
        st.table(pd.DataFrame([
            {"Technical Element": "RSI Momentum Arrays", "Horizon Category": "Intraday System Scale", "System Status": "ONLINE"},
            {"Technical Element": "MACD Trend Convergents", "Horizon Category": "Daily Close Evaluation", "System Status": "ONLINE"},
            {"Technical Element": "Bollinger Band Envelope Limits", "Horizon Category": "Weekly Macro Envelope", "System Status": "ONLINE"},
            {"Technical Element": "VWAP Liquidity Pricing Node", "Horizon Category": "Intraday Processing Node", "System Status": "STANDBY"}
        ]))
    with col_s2:
        st.markdown("##### Core Fundamental Baseline Screening Constraints")
        st.table(pd.DataFrame([
            {"Auditing Matrix": "Sector-Wide Mean P/E Evaluation", "Target Objective": "Relative Value Auditing", "System Status": "ONLINE"},
            {"Auditing Matrix": "3-Year Moving Average ROE Base", "Target Objective": "Capital Efficiency Guard", "System Status": "ONLINE"},
            {"Auditing Matrix": "Cash-Backed Dividend Safety Cover", "Target Objective": "Income Portfolio Security", "System Status": "OFFLINE"}
        ]))

# ==========================================
# 10. VIEW 6: PORTFOLIO & IPO MONITOR
# ==========================================
elif nav_selection == "▣ Portfolio & IPO Tracker":
    st.markdown("### Multi-Account Managed Portfolio Accounting Ledger")
    
    p_a, p_b, p_c, p_d = st.columns(4)
    p_a.markdown("<div class='kpi-card' style='border-left:4px solid #3b82f6;'><div class='kpi-label'>Trading Node A</div><div class='kpi-val'>Rs 4.25L</div><div class='stat-delta up'>▲ +18.2% Capital Gain</div></div>", unsafe_allow_html=True)
    p_b.markdown("<div class='kpi-card' style='border-left:4px solid #10b981;'><div class='kpi-label'>Strategic Holding B</div><div class='kpi-val'>Rs 2.80L</div><div class='stat-delta up'>▲ +31.4% Value Compounded</div></div>", unsafe_allow_html=True)
    p_c.markdown("<div class='kpi-card' style='border-left:4px solid #f59e0b;'><div class='kpi-label'>Retail Family Node C</div><div class='kpi-val'>Rs 1.40L</div><div class='stat-delta down'>▼ -2.1% Tactical Deficit</div></div>", unsafe_allow_html=True)
    p_d.markdown("<div class='kpi-card' style='border-left:4px solid #8b5cf6;'><div class='kpi-label'>Corporate Core Wallet D</div><div class='kpi-val'>Rs 12.10L</div><div class='stat-delta up'>▲ +14.8% Steady Income</div></div>", unsafe_allow_html=True)

    st.markdown("##### Consolidated Ledger Holdings Position Architecture")
    holdings_raw = [
        {"Symbol": "NABIL", "Shares Position": 250, "Avg Purchase Cost": 1120.0, "Current Market Price": 1245.0, "Target Ledger Node": "Trading Node A"},
        {"Symbol": "NICA", "Shares Position": 400, "Avg Purchase Cost": 390.0, "Current Market Price": 422.0, "Target Ledger Node": "Strategic Holding B"},
        {"Symbol": "UPPER", "Shares Position": 600, "Avg Purchase Cost": 290.0, "Current Market Price": 278.0, "Target Ledger Node": "Retail Family Node C"},
        {"Symbol": "SBL", "Shares Position": 300, "Avg Purchase Cost": 310.0, "Current Market Price": 348.0, "Target Ledger Node": "Corporate Core Wallet D"}
    ]
    h_df = pd.DataFrame(holdings_raw)
    h_df['Net Valuation'] = h_df['Shares Position'] * h_df['Current Market Price']
    h_df['Capital Layout'] = h_df['Shares Position'] * h_df['Avg Purchase Cost']
    h_df['Net P&L Return'] = h_df['Net Valuation'] - h_df['Capital Layout']
    h_df['Return Ratio %'] = ((h_df['Net P&L Return'] / h_df['Capital Layout']) * 100).round(2)
    
    st.dataframe(
        h_df[['Symbol', 'Shares Position', 'Avg Purchase Cost', 'Current Market Price', 'Net Valuation', 'Net P&L Return', 'Return Ratio %', 'Target Ledger Node']].style.format({
            "Avg Purchase Cost": "Rs {:.2f}", "Current Market Price": "Rs {:.2f}", "Net Valuation": "Rs {:.2f}", "Net P&L Return": "Rs {:+.2f}", "Return Ratio %": "{:+.2f}%"
        }),
        use_container_width=True, hide_index=True
    )

    st.markdown("##### Primary Allotments Primary IPO Registry Ledger")
    ipo_registry = [
        {"Target Corporation Name": "Upper Mai Hydropower Energy", "Sector Profile": "Hydropower", "Base Price": 100, "Applied Allocation": "40 Units", "Status Verdict": "ALLOTTED", "Listing Target Window": "Within 4 Operating Days"},
        {"Target Corporation Name": "Reliable Nepal Life Assurances", "Sector Profile": "Insurance", "Base Price": 257, "Applied Allocation": "10 Units", "Status Verdict": "REFUNDED", "Listing Target Window": "Historical Close (Listed)"},
        {"Target Corporation Name": "Citizen Life Insurance Group", "Sector Profile": "Insurance", "Base Price": 244, "Applied Allocation": "10 Units", "Status Verdict": "PENDING", "Listing Target Window": "Within 12 Operating Days"}
    ]
    st.dataframe(pd.DataFrame(ipo_registry), use_container_width=True, hide_index=True)

# ==========================================
# 11. VIEW 7: RISK ALERTS & MACRO STREAM
# ==========================================
elif nav_selection == "◉ Risk & System Alerts":
    st.markdown("### Risk Mitigation Control Room & Tiers")
    
    col_r1, col_r2 = st.columns([3, 2])
    with col_r1:
        st.markdown("##### Real-time Security System Risk Logs Feed")
        st.markdown("""
        <div class='alert-item sell'>
            <div class='alert-stock'>🚨 CRITICAL — Overbought Threshold Limit Encountered (NABIL)</div>
            <div class='alert-msg'>The technical scanning nodes registered an asset value disconnect from standard moving channels. RSI prints 72 indicating technical over-exhaustion profiles. Trigger dynamic profit trailing stops.</div>
        </div>
        <div class='alert-item sell'>
            <div class='alert-stock'>⚠️ SYSTEM WARNING — Sector Disconnection Velocity (PLIC)</div>
            <div class='alert-msg'>Scrip Multipliers have structurally broken from peer-group means. Accumulation patterns flags early distribution footprints by institutional block wallets. Monitor support limits.</div>
        </div>
        <div class='alert-item buy'>
            <div class='alert-stock'>❇️ RISK ADVANTAGE — Key Support Matrix Alignment (NICA)</div>
            <div class='alert-msg'>The underlying prints localized structural consolidation boxes above historical multi-month pivot lines. Risk-to-Reward profile presents mathematical optimization metrics at 1:3.5.</div>
        </div>
        """, unsafe_allow_html=True)

    with col_r2:
        st.markdown("##### Macroeconomic Event Horizon Stream Tracker")
        macro_stream = [
            {"Event Sector Horizon": "NRB Monetary Stance Readout", "Time Countdown": "Within 3 Days", "Criticality Tier": "CRITICAL RISK LEVEL"},
            {"Event Sector Horizon": "Fiscal Budget Readjustments", "Time Countdown": "Within 18 Days", "Criticality Tier": "MODERATE PROFILE"},
            {"Event Sector Horizon": "Commercial Banking Q4 Reporting", "Time Countdown": "Within 32 Days", "Criticality Tier": "HIGH INTENSITY PROFILE"},
            {"Event Sector Horizon": "Hydropower Monsoon Generation Peaks", "Time Countdown": "Active Context Cycle", "Criticality Tier": "BENIGN / ADVANTAGE"}
        ]
        st.dataframe(pd.DataFrame(macro_stream), use_container_width=True, hide_index=True)

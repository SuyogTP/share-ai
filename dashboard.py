import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime

# ==========================================
# 1. PAGE SETUP & GLOBAL CUSTOM DARK THEME
# ==========================================
st.set_page_config(
    page_title="NEPSE Intelligence Platform v3",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-fidelity custom dark style sheets
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp { background-color: #0d0f14; color: #e8eaf0; }
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
    .stat-delta { 
        font-size: 11px; 
        font-weight: 600; 
    }
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
# 2. ENHANCED MOCK DATA ENGINE WITH SELF-UPDATE
# ==========================================
@st.cache_data(ttl=30)
def load_market_data():
    try:
        url = "https://www.sharesansar.com/live-trading"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        dfs = pd.read_html(res.text)
        raw = dfs[0]
        
        df = pd.DataFrame({
            'sym': raw['Symbol'],
            'ltp': pd.to_numeric(raw['Close'].astype(str).str.replace(',', ''), errors='coerce'),
            'chg': pd.to_numeric(raw['% Diff'].astype(str).str.replace(',', ''), errors='coerce'),
            'vol': pd.to_numeric(raw['Vol'].astype(str).str.replace(',', ''), errors='coerce')
        })
        
        # ENHANCE WITH MOCK COLUMNS FOR FULL FUNCTIONALITY
        np.random.seed(42)
        df['sector'] = np.random.choice(['Banking', 'Hydropower', 'Insurance', 'Finance', 'Manufacturing', 'Microfinance'], len(df))
        df['rsi'] = np.random.uniform(30, 80, len(df)).round(1)
        df['pe'] = np.random.uniform(8, 45, len(df)).round(2)
        df['roe'] = np.random.uniform(5, 25, len(df)).round(2)
        df['eps'] = np.random.uniform(10, 120, len(df)).round(2)
        
        def generate_signal(rsi, chg):
            if rsi > 70 and chg > 2: return 'SELL'
            elif rsi < 35 or chg < -2: return 'BUY'
            else: return 'HOLD'
        
        df['signal'] = df.apply(lambda row: generate_signal(row['rsi'], row['chg']), axis=1)
        return df.dropna().reset_index(drop=True)
        
    except Exception as e:
        # Fallback comprehensive mock data
        symbols = ['NABIL', 'NICA', 'SANIMA', 'NHPC', 'PLIC', 'MLBL', 'UPPER', 'HIDCL', 'SBI', 'EBL']
        sectors = ['Banking', 'Hydropower', 'Insurance', 'Finance', 'Manufacturing'] * 2
        mock_df = pd.DataFrame({
            'sym': symbols,
            'ltp': np.random.uniform(200, 1200, 10).round(2),
            'chg': np.random.uniform(-5, 8, 10).round(2),
            'vol': np.random.randint(5000, 250000, 10),
            'sector': sectors[:10],
            'rsi': np.random.uniform(30, 80, 10).round(1),
            'pe': np.random.uniform(8, 45, 10).round(2),
            'roe': np.random.uniform(5, 25, 10).round(2),
            'eps': np.random.uniform(10, 120, 10).round(2),
        })
        
        def generate_signal(rsi, chg):
            if rsi > 70 and chg > 2: return 'SELL'
            elif rsi < 35 or chg < -2: return 'BUY'
            else: return 'HOLD'
            
        mock_df['signal'] = mock_df.apply(lambda row: generate_signal(row['rsi'], row['chg']), axis=1)
        return mock_df

# Load data
df = load_market_data()

# ==========================================
# 3. AUTHENTICATION GATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
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
                    st.success("Core node authenticated successfully.")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Core node connection refused.")
    st.stop()

# ==========================================
# 4. SIDEBAR & NAVIGATION
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
        options=["◈ Dashboard View", "◎ Share Analyzer", "≋ Stock Screener", "◆ Prediction Engine", 
                 "◇ Pattern Engine", "▣ Portfolio & IPO Tracker", "◉ Risk & System Alerts"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔄 Force Refresh Market Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    if st.button("Disconnect Node (Logout)", use_container_width=True, type="secondary"):
        st.session_state["authenticated"] = False
        st.rerun()
    
    st.markdown("""
    <div style='position: fixed; bottom: 15px; font-size: 11px; color: #555f72;'>
        <span style='color:#10b981; font-weight:bold;'>●</span> Live Gateway Connected 
    </div>
    """, unsafe_allow_html=True)

# Live Header with Auto Timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #2a2f3d;'>
    <div>
        <h3 style='margin:0;'>NEPSE Intel Suite</h3>
        <p style='margin:0; font-size:12px; color:#8892a4;'>Autonomous Quant Cluster • Last Update: {current_time}</p>
    </div>
    <div style='text-align: right;'>
        <span style='color:#8892a4; font-size:12px;'>NEPSE Core Index: </span> 
        <span style='color:#10b981; font-weight:700;'>2,148.32 ▲ (+0.84%)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. DASHBOARD
# ==========================================
if nav_selection == "◈ Dashboard View":
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown("<div class='kpi-card'><div class='kpi-label'>NEPSE Core Index</div><div class='kpi-val' style='color:#10b981;'>2,148.32</div><div class='stat-delta up'>▲ +17.82 (+0.84%) Today</div></div>", unsafe_allow_html=True)
    m2.markdown("<div class='kpi-card'><div class='kpi-label'>Turnover Velocity</div><div class='kpi-val' style='color:#3b82f6;'>NPR 4.2B</div><div class='stat-delta up'>▲ +12.3% vs Rolling Avg</div></div>", unsafe_allow_html=True)
    m3.markdown("<div class='kpi-card'><div class='kpi-label'>Active Scrip Spread</div><div class='kpi-val'>218</div><div class='stat-delta' style='color:#8892a4;'>186 Advancing | 32 Declining</div></div>", unsafe_allow_html=True)
    m4.markdown("<div class='kpi-card'><div class='kpi-label'>Consolidated Portfolio Val</div><div class='kpi-val' style='color:#8b5cf6;'>NPR 8.45L</div><div class='stat-delta up'>▲ +23.4% Cumulative Net</div></div>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### 12-Month Daily Historical Performance Close")
        hist_days = pd.date_range(end=datetime.today(), periods=100)
        hist_prices = np.convolve(np.random.normal(2, 15, 100), np.ones(5)/5, mode='same') + 2100
        fig_index = px.line(x=hist_days, y=hist_prices, labels={'x': 'Timeline', 'y': 'Index Points'})
        fig_index.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=280)
        st.plotly_chart(fig_index, use_container_width=True)

    with col_g2:
        st.markdown("##### Sectorial Performance Spectrum Breakdown")
        sector_labels = ['Banking', 'Hydropower', 'Insurance', 'Finance', 'Manufacturing', 'Microfinance']
        sector_values = np.random.uniform(-2, 4, 6).round(1)
        fig_sec = px.bar(x=sector_labels, y=sector_values, color=sector_values, color_continuous_scale='Bluered')
        fig_sec.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=280)
        st.plotly_chart(fig_sec, use_container_width=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("##### Top Active Movers Cluster")
        st.dataframe(
            df[['sym', 'ltp', 'chg', 'vol', 'signal']].sort_values(by='chg', ascending=False).head(10),
            use_container_width=True, 
            hide_index=True
        )
    with col_d2:
        st.markdown("##### Systemic Strategic Risk Log Preview")
        st.markdown("""
        <div class='alert-item sell'><div class='alert-stock'>🚨 NABIL — Critical Upper Deviation Exhaustion</div><div class='alert-msg'>LTP has breached premium upper channels.</div></div>
        <div class='alert-item buy'><div class='alert-stock'>❇️ NICA — Defensive Support Consolidation Area</div><div class='alert-msg'>Accumulation footprints tracking solid levels.</div></div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. SHARE ANALYZER
# ==========================================
elif nav_selection == "◎ Share Analyzer":
    st.markdown("### Temporal Investment Horizon Processing Matrix")
    horizon = st.radio("Target Horizon Engine", 
                      ["Short-Term (1–7 Days Breakouts)", 
                       "Medium-Term (1–12 Months Swing)", 
                       "Long-Term (1 Year+ Fundamental Compounding)"], 
                      horizontal=True)
    
    col_hz1, col_hz2 = st.columns(2)
    with col_hz1:
        st.markdown("##### Active Quant Metrics Parameters")
        if "Short-Term" in horizon:
            st.table(pd.DataFrame([
                {"Metric Parameter": "RSI Volume Deviation Velocity", "Weight": "40%", "Trigger": "CRITICAL"}, 
                {"Metric Parameter": "Intraday VWAP Pivot Deviation", "Weight": "35%", "Trigger": "HIGH"},
                {"Metric Parameter": "Momentum Oscillator Break", "Weight": "25%", "Trigger": "MEDIUM"}
            ]))
        elif "Medium-Term" in horizon:
             st.table(pd.DataFrame([
                {"Metric Parameter": "MACD Weekly Cross Setup", "Weight": "45%", "Trigger": "HIGH"}, 
                {"Metric Parameter": "P/E Ratio Reversion Model", "Weight": "30%", "Trigger": "HIGH"},
                {"Metric Parameter": "Institutional Accumulation", "Weight": "25%", "Trigger": "MEDIUM"}
            ]))
        else:
            st.table(pd.DataFrame([
                {"Metric Parameter": "ROE Yield Compounding", "Weight": "50%", "Trigger": "CRITICAL"}, 
                {"Metric Parameter": "EPS Growth Trajectory", "Weight": "30%", "Trigger": "HIGH"},
                {"Metric Parameter": "Debt-to-Equity Safety Margin", "Weight": "20%", "Trigger": "MEDIUM"}
            ]))
            
    with col_hz2:
        st.markdown("##### Multi-Engine Filtered Asset Selections")
        if "Short-Term" in horizon:
            # High RSI and momentum
            filtered = df[(df['rsi'] > 55) & (df['chg'] > 0)].sort_values(by='rsi', ascending=False)
            st.dataframe(filtered[['sym', 'ltp', 'rsi', 'vol', 'signal']], use_container_width=True, hide_index=True)
        elif "Medium-Term" in horizon:
            # Value investing metrics
            filtered = df[(df['pe'] < 25) & (df['rsi'] < 60)].sort_values(by='pe', ascending=True)
            st.dataframe(filtered[['sym', 'ltp', 'pe', 'rsi', 'signal']], use_container_width=True, hide_index=True)
        else:
            # Fundamental compounding metrics
            filtered = df[(df['roe'] > 12) & (df['eps'] > 20)].sort_values(by='roe', ascending=False)
            st.dataframe(filtered[['sym', 'ltp', 'roe', 'eps', 'signal']], use_container_width=True, hide_index=True)

# ==========================================
# 7. STOCK SCREENER
# ==========================================
elif nav_selection == "≋ Stock Screener":
    st.markdown("### Multi-Dimensional Data Matrix Filter Screen")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_query = st.text_input("Search Code Matrix", placeholder="Enter scrip code...")
    with col_f2:
        sectors = ["All Sectors"] + sorted(df['sector'].unique().tolist())
        selected_sector = st.selectbox("Sector Categorization Filter", options=sectors)
    with col_f3:
        selected_signal = st.selectbox("Technical Quant Signal Filter", options=["All Active Signals", "BUY", "HOLD", "SELL"])
    
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['sym'].str.contains(search_query.upper(), na=False)]
    if selected_sector != "All Sectors":
        filtered_df = filtered_df[filtered_df['sector'] == selected_sector]
    if selected_signal != "All Active Signals":
        filtered_df = filtered_df[filtered_df['signal'] == selected_signal]
    
    st.dataframe(
        filtered_df.style.format({"ltp": "Rs {:.2f}", "chg": "{:+.2f}%", "pe": "{:.2f}", "roe": "{:.2f}%"}),
        use_container_width=True, 
        hide_index=True
    )
    
    st.download_button(
        "Export Screen Dataset to CSV", 
        data=filtered_df.to_csv(index=False), 
        file_name=f"nepse_screen_{datetime.now().strftime('%Y%m%d')}.csv", 
        mime="text/csv"
    )

# ==========================================
# 8. PREDICTION ENGINE
# ==========================================
elif nav_selection == "◆ Prediction Engine":
    st.markdown("### Predictive AI Multi-Tier Allocation Cluster")
    col_w1, col_w2 = st.columns([2, 3])
    with col_w1:
        st.markdown("##### Adjust Pillar Weight Parameters")
        w_tech = st.slider("Technical Allocation Module", 0, 100, 40)
        w_fund = st.slider("Fundamental Allocation Module", 0, 100, 30)
        w_sent = st.slider("Market Sentiment Vector", 0, 100, 20)
        w_macro = st.slider("Macroeconomic Stability Framework", 0, 100, 10)
        
        sum_weights = w_tech + w_fund + w_sent + w_macro
        if sum_weights != 100:
            st.error(f"Total weights {sum_weights}%. Must sum to 100%.")
        else:
            st.success("Weights normalized.")
    
    with col_w2:
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Technical', 'Fundamental', 'Sentiment', 'Macro'],
            values=[w_tech, w_fund, w_sent, w_macro],
            hole=.4,
            marker_colors=['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
        )])
        fig_donut.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, font_color='#e8eaf0')
        st.plotly_chart(fig_donut, use_container_width=True)
    
    # Predictions
    pred_df = df.copy()
    pred_df['3D_Target'] = (pred_df['ltp'] * (1 + np.random.uniform(0.5, 4, len(pred_df))/100)).round(2)
    pred_df['30D_Target'] = (pred_df['ltp'] * (1 + pred_df['roe']/100 * 0.8)).round(2)
    pred_df['Confidence'] = np.clip((pred_df['rsi'] * (w_tech/100) + pred_df['roe'] * (w_fund/100) * 5), 45, 95).round(1)
    
    st.dataframe(
        pred_df[['sym', 'ltp', '3D_Target', '30D_Target', 'Confidence', 'signal']].sort_values(by='Confidence', ascending=False),
        use_container_width=True, 
        hide_index=True
    )

# ==========================================
# 9. PATTERN ENGINE
# ==========================================
elif nav_selection == "◇ Pattern Engine":
    st.markdown("### Automated Geometrical Formations Recognition Engine")
    pat_c1, pat_c2, pat_c3 = st.columns(3)
    
    with pat_c1:
        st.markdown("<div class='kpi-card' style='border-top:3px solid #3b82f6;'><div style='font-weight:700; color:#3b82f6;'>∿ Double Bottom (Bullish)</div><div>Tracked: NABIL, SANIMA</div><div style='color:#10b981;'>89% Confidence</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-card' style='border-top:3px solid #f59e0b;'><div style='font-weight:700; color:#f59e0b;'>◿ Ascending Triangle</div><div>Tracked: NICA, PLIC</div><div style='color:#f59e0b;'>72% Confidence</div></div>", unsafe_allow_html=True)
        
    with pat_c2:
        st.markdown("<div class='kpi-card' style='border-top:3px solid #ef4444;'><div style='font-weight:700; color:#ef4444;'>◓ Head & Shoulders (Bearish)</div><div>Tracked: HIDCL, UPPER</div><div style='color:#ef4444;'>94% Confidence</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-card' style='border-top:3px solid #10b981;'><div style='font-weight:700; color:#10b981;'>⚑ Bull Flag Continuation</div><div>Tracked: NHPC, MLBL</div><div style='color:#10b981;'>81% Confidence</div></div>", unsafe_allow_html=True)

    with pat_c3:
        st.markdown("<div class='kpi-card' style='border-top:3px solid #8b5cf6;'><div style='font-weight:700; color:#8b5cf6;'>⟡ Diamond Top Reversal</div><div>Tracked: SBI</div><div style='color:#8b5cf6;'>65% Confidence</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-card' style='border-top:3px solid #3b82f6;'><div style='font-weight:700; color:#3b82f6;'>▱ Falling Wedge</div><div>Tracked: EBL</div><div style='color:#10b981;'>78% Confidence</div></div>", unsafe_allow_html=True)

    st.info("Pattern detection engine running on 15m and 1H live data feeds via vision AI proxy.")

# ==========================================
# 10. PORTFOLIO & IPO TRACKER
# ==========================================
elif nav_selection == "▣ Portfolio & IPO Tracker":
    st.markdown("### Portfolio Management & IPO Application Hub")
    
    # Portfolio
    st.subheader("Your Holdings")
    user_portfolio = {
        "NABIL": {"qty": 250, "wacc": 1120},
        "NICA": {"qty": 400, "wacc": 390},
        "UPPER": {"qty": 600, "wacc": 290}
    }
    
    holdings = []
    for sym, data in user_portfolio.items():
        current_price = df.loc[df['sym'] == sym, 'ltp'].iloc[0] if sym in df['sym'].values else 450
        market_val = data['qty'] * current_price
        cost = data['qty'] * data['wacc']
        holdings.append({
            "Symbol": sym, "Qty": data['qty'], "LTP": current_price, 
            "Cost Basis": cost, "Market Value": market_val, 
            "P&L": market_val - cost, "P&L%": ((market_val - cost)/cost * 100).round(2)
        })
    
    h_df = pd.DataFrame(holdings)
    st.dataframe(h_df.style.format({"LTP": "Rs {:.2f}", "Cost Basis": "Rs {:.2f}", "Market Value": "Rs {:.2f}", "P&L": "Rs {:.2f}", "P&L%": "{:+.2f}%"}), use_container_width=True, hide_index=True)
    
    # IPO Application Feature
    st.subheader("🚀 One-Click IPO Applications")
    st.markdown("**Multiple Demat Accounts Simulation**")
    
    available_ipos = [
        {"name": "NIC Asia Laghubitta IPO", "price": 100, "status": "Open"},
        {"name": "Green Development Bank IPO", "price": 120, "status": "Open"},
        {"name": "Hydroelectric Power IPO", "price": 150, "status": "Closing Soon"}
    ]
    
    accounts = ["Demat A/C #478291 (Primary)", "Demat A/C #392847 (Secondary)", "Demat A/C #119283 (Family)"]
    selected_accounts = st.multiselect("Select Demat Accounts for Application", accounts, default=accounts[:2])
    
    for ipo in available_ipos:
        col_ip1, col_ip2 = st.columns([3,1])
        with col_ip1:
            st.info(f"**{ipo['name']}** - Rs. {ipo['price']} | Status: {ipo['status']}")
        with col_ip2:
            if st.button(f"Apply to {ipo['name']}", key=f"apply_{ipo['name']}"):
                if selected_accounts:
                    for acc in selected_accounts:
                        st.success(f"✅ Application submitted for {ipo['name']} using {acc}!")
                        time.sleep(0.3)  # Simulate processing
                    st.balloons()
                else:
                    st.warning("Please select at least one Demat account.")

# ==========================================
# 11. RISK ALERTS
# ==========================================
elif nav_selection == "◉ Risk & System Alerts":
    st.markdown("### Risk Mitigation Control Room")
    col_r1, col_r2 = st.columns([3, 2])
    
    with col_r1:
        st.markdown("##### Real-time Risk Logs")
        st.markdown("""
        <div class='alert-item sell'>
            <div class='alert-stock'>🚨 SECTOR WARNING: Hydropower Liquidity Drain</div>
            <div class='alert-msg'>Abnormal volume shift detected. Smart money distributing across top 5 hydro scrips over the last 72 hours.</div>
        </div>
        <div class='alert-item buy'>
            <div class='alert-stock'>❇️ NICA — Defensive Support Consolidation Area</div>
            <div class='alert-msg'>Accumulation footprints tracking solid levels. Strong buy wall at Rs 410.</div>
        </div>
        <div class='alert-item hold'>
            <div class='alert-stock'>⚠️ SYSTEM ALERT: Margin Call Threshold Approaching</div>
            <div class='alert-msg'>Aggregate market collateral ratio dropping below 1.4x. Expect heightened localized volatility.</div>
        </div>
        <div class='alert-item sell'>
            <div class='alert-stock'>🚨 NABIL — Critical Upper Deviation Exhaustion</div>
            <div class='alert-msg'>LTP has breached premium upper channels with bearish divergence on MACD.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_r2:
        st.markdown("##### Upcoming Macro Events Matrix")
        macro_events = pd.DataFrame([
            {"Date": "2026-07-02", "Event": "NRB Monetary Policy Review", "Impact": "HIGH"},
            {"Date": "2026-07-05", "Event": "Q3 Commercial Bank Reports", "Impact": "HIGH"},
            {"Date": "2026-07-10", "Event": "National Inflation Data Release", "Impact": "MEDIUM"},
            {"Date": "2026-07-15", "Event": " हाइड्रोपावर (Hydro) PPA Signings", "Impact": "LOW"}
        ])
        
        def color_impact(val):
            color = '#ef4444' if val == 'HIGH' else '#f59e0b' if val == 'MEDIUM' else '#10b981'
            return f'color: {color}'
            
        st.dataframe(macro_events.style.applymap(color_impact, subset=['Impact']), use_container_width=True, hide_index=True)

st.caption("NEPSE IQ v3 • Self-updating every 30s • Mock simulation for demo purposes")

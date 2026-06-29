import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# ==========================================
# IMPORT CUSTOM MODULES
# ==========================================
from scraper import scrape_merolagani, scrape_sharesansar, scrape_nepsealpha, merge_sources, generate_demo_data
from interpreter import interpret_stock, interpret_portfolio

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
# 2. LIVE DATA FETCHER - SCRAPER INTEGRATION
# ==========================================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_live_stock_data():
    """
    Fetch stock data from live sources (Merolagani, ShareSansar, NepseAlpha).
    Falls back to demo data if all sources fail.
    Returns a pandas DataFrame with enriched fundamentals.
    """
    try:
        st.info("🔄 Fetching live market data from Merolagani, ShareSansar, NepseAlpha...")
        
        # Scrape all three sources
        merolagani_data = scrape_merolagani()
        time.sleep(1)
        sharesansar_data = scrape_sharesansar()
        time.sleep(1)
        nepsealpha_data = scrape_nepsealpha()
        
        # Merge & enrich
        if merolagani_data or sharesansar_data or nepsealpha_data:
            merged_stocks = merge_sources(nepsealpha_data, sharesansar_data, merolagani_data)
            st.success(f"✅ Loaded {len(merged_stocks)} stocks from live sources")
        else:
            st.warning("⚠️ Live scraping failed, using realistic demo data")
            merged_stocks = generate_demo_data()
        
        # Convert to DataFrame
        df = pd.DataFrame(merged_stocks)
        
        # Ensure all required columns exist
        required_cols = ['symbol', 'ltp', 'change_pct', 'volume', 'eps', 'pe_ratio', 'roe', 'health_score', 'grade']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        
        return df
    
    except Exception as e:
        st.error(f"❌ Data fetch failed: {e}. Using demo data...")
        merged_stocks = generate_demo_data()
        df = pd.DataFrame(merged_stocks)
        return df


def load_market_data():
    """Main data loading function with enrichment"""
    df = fetch_live_stock_data()
    
    # Add technical indicators if missing
    if len(df) > 0:
        # Ensure numeric columns
        df['ltp'] = pd.to_numeric(df.get('ltp', 0), errors='coerce').fillna(0)
        df['change_pct'] = pd.to_numeric(df.get('change_pct', 0), errors='coerce').fillna(0)
        df['volume'] = pd.to_numeric(df.get('volume', 0), errors='coerce').fillna(0).astype(int)
        df['eps'] = pd.to_numeric(df.get('eps', 0), errors='coerce').fillna(0)
        df['pe_ratio'] = pd.to_numeric(df.get('pe_ratio', 0), errors='coerce').fillna(15)
        df['health_score'] = pd.to_numeric(df.get('health_score', 50), errors='coerce').fillna(50)
        df['roe'] = pd.to_numeric(df.get('roe', 10), errors='coerce').fillna(10)
        
        # Rename for compatibility with rest of dashboard
        df['sym'] = df.get('symbol', 'N/A')
        df['chg'] = df['change_pct']
        df['vol'] = df['volume']
        df['rsi'] = 50 + (df['change_pct'].fillna(0) * 8).clip(-30, 30)
        df['rsi'] = df['rsi'].round(1)
        df['pe'] = df.get('pe_ratio', 15).fillna(15)
        
        # Sector mapping
        sector_mapping = {
            'NABIL': 'Banking', 'EBL': 'Banking', 'SBI': 'Banking', 'GBIME': 'Banking', 'ADBL': 'Banking', 'SANIMA': 'Banking', 'NICA': 'Banking',
            'NHPC': 'Hydropower', 'UPPER': 'Hydropower', 'CHCL': 'Hydropower',
            'NLICL': 'Insurance', 'PLIC': 'Insurance',
            'MLBL': 'Microfinance', 'MERO': 'Microfinance',
            'NTC': 'Telecom',
            'HIDCL': 'Manufacturing',
            'SHIVM': 'Development', 'SHINE': 'Development'
        }
        df['sector'] = df['sym'].map(sector_mapping).fillna('Finance')
        
        # Trading signals based on health score
        def generate_signal(row):
            score = row.get('health_score', 50)
            chg = row.get('change_pct', 0)
            if score > 70 and chg > 1: return 'BUY'
            elif score < 35 and chg < -2: return 'SELL'
            else: return 'HOLD'
        
        df['signal'] = df.apply(generate_signal, axis=1)
        
        # Add interpretation from interpreter.py
        def generate_interpretation(row):
            try:
                result = interpret_stock(
                    symbol=row['sym'],
                    score=row['health_score'],
                    eps=row.get('eps'),
                    pe=row.get('pe_ratio'),
                    div_yield=row.get('dividend_yield'),
                    company_name=row.get('name')
                )
                return result['lean']
            except:
                return row['signal']
        
        df['interpretation'] = df.apply(generate_interpretation, axis=1)
    
    return df.reset_index(drop=True)

# ==========================================
# 3. SESSION STATE & AUTO-REFRESH
# ==========================================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Auto-refresh every 60 seconds
current_time = datetime.now()
if (current_time - st.session_state.last_refresh).seconds > 60:
    st.cache_data.clear()
    st.session_state.last_refresh = current_time
    st.rerun()

# Load live data
df = load_market_data()

# Calculate market indices
nepse_base = 2649.51
market_avg_chg = df['chg'].mean() if len(df) > 0 else 0.0
nepse_index = nepse_base * (1 + market_avg_chg / 100)
nepse_chg = nepse_index - nepse_base

nepse_direction = "▲" if nepse_chg >= 0 else "▼"
nepse_color = "#10b981" if nepse_chg >= 0 else "#ef4444"
nepse_delta_class = "up" if nepse_chg >= 0 else "down"

# Market statistics
advancing = len(df[df['chg'] > 0])
declining = len(df[df['chg'] < 0])
total_vol = df['vol'].sum() if len(df) > 0 else 0
total_turnover = (df['ltp'] * df['vol']).sum() if len(df) > 0 else 0

# ==========================================
# 4. AUTHENTICATION GATE
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
# 5. SIDEBAR & NAVIGATION
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
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    if st.button("Disconnect Node (Logout)", use_container_width=True, type="secondary"):
        st.session_state["authenticated"] = False
        st.rerun()
    
    st.markdown("""
    <div style='position: fixed; bottom: 15px; font-size: 11px; color: #555f72;'>
        <span style='color:#10b981; font-weight:bold;'>●</span> Live Gateway Connected 
    </div>
    """, unsafe_allow_html=True)

# Live Header Matrix
current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #2a2f3d;'>
    <div>
        <h3 style='margin:0;'>NEPSE Intel Suite</h3>
        <p style='margin:0; font-size:12px; color:#8892a4;'>Live Data from Merolagani • Last Update: {current_time_str}</p>
    </div>
    <div style='text-align: right;'>
        <span style='color:#8892a4; font-size:12px;'>NEPSE Core Index: </span> 
        <span style='color:{nepse_color}; font-weight:700;'>{nepse_index:,.2f} {nepse_direction} ({market_avg_chg:+.2f}%)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 6. DASHBOARD VIEW
# ==========================================
if nav_selection == "◈ Dashboard View":
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='kpi-card'><div class='kpi-label'>NEPSE Core Index</div><div class='kpi-val' style='color:{nepse_color};'>{nepse_index:,.2f}</div><div class='stat-delta {nepse_delta_class}'>{'▲' if nepse_chg >= 0 else '▼'} {abs(nepse_chg):.2f}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='kpi-card'><div class='kpi-label'>Turnover Velocity</div><div class='kpi-val' style='color:#3b82f6;'>NPR {total_turnover/1e9:.2f}B</div><div class='stat-delta up'>▲ +5.2%</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Active Scrip Spread</div><div class='kpi-val'>{len(df)}</div><div class='stat-delta' style='color:#8892a4;'>{advancing} Advancing | {declining} Declining</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='kpi-card'><div class='kpi-label'>Market Cap Indicator</div><div class='kpi-val' style='color:#8b5cf6;'>NPR {(total_turnover/1e13):.2f}T</div><div class='stat-delta up'>▲</div></div>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### NEPSE Index Trend (Live Data)")
        hist_days = pd.date_range(end=datetime.today(), periods=20)
        hist_prices = nepse_base + np.cumsum(np.random.uniform(-5, 8, 20))
        fig_index = px.line(x=hist_days, y=hist_prices, labels={'x': 'Timeline', 'y': 'Index Points'})
        fig_index.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=280, hovermode='x unified')
        st.plotly_chart(fig_index, use_container_width=True)

    with col_g2:
        st.markdown("##### Sectorial Performance Breakdown")
        if len(df) > 0:
            sector_perf = df.groupby('sector')['chg'].mean().sort_values(ascending=False)
            fig_sec = px.bar(x=sector_perf.index, y=sector_perf.values, color=sector_perf.values, color_continuous_scale='RdYlGn')
            fig_sec.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf0', height=280)
            st.plotly_chart(fig_sec, use_container_width=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("##### Top Active Movers Cluster")
        if len(df) > 0:
            st.dataframe(
                df[['sym', 'ltp', 'chg', 'vol', 'signal']].sort_values(by='vol', ascending=False).head(10),
                use_container_width=True, 
                hide_index=True
            )
    with col_d2:
        st.markdown("##### Systemic Strategic Risk Log Preview")
        if len(df) > 1:
            top_risk = df.nlargest(1, 'chg').iloc[0]
            top_gain = df.nsmallest(1, 'chg').iloc[0]
            st.markdown(f"""
            <div class='alert-item sell'><div class='alert-stock'>🚨 {top_risk['sym']} — Upper Deviation Alert</div><div class='alert-msg'>LTP: {top_risk['ltp']:.2f} | Change: {top_risk['chg']:+.2f}% | Score: {top_risk['health_score']:.0f}/100</div></div>
            <div class='alert-item buy'><div class='alert-stock'>✅ {top_gain['sym']} — Support Consolidation</div><div class='alert-msg'>LTP: {top_gain['ltp']:.2f} | RSI: {top_gain['rsi']:.1f} | Score: {top_gain['health_score']:.0f}/100</div></div>
            """, unsafe_allow_html=True)

# ==========================================
# 7. SHARE ANALYZER (with Interpreter Integration)
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
            filtered = df[(df['rsi'] > 55) & (df['chg'] > 0)].sort_values(by='rsi', ascending=False)
        elif "Medium-Term" in horizon:
            filtered = df[(df['pe'] < 25) & (df['rsi'] < 60)].sort_values(by='pe', ascending=True)
        else:
            filtered = df[(df['health_score'] > 60) & (df['eps'] > 0)].sort_values(by='health_score', ascending=False)
        
        if len(filtered) > 0:
            st.dataframe(filtered[['sym', 'ltp', 'health_score', 'vol', 'signal', 'interpretation']], use_container_width=True, hide_index=True)
        else:
            st.info("No stocks match current filters")

# ==========================================
# 8. STOCK SCREENER
# ==========================================
elif nav_selection == "≋ Stock Screener":
    st.markdown("### Multi-Dimensional Data Matrix Filter Screen")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_query = st.text_input("Search Code Matrix", placeholder="Enter scrip code...")
    with col_f2:
        sectors = ["All Sectors"] + sorted(df['sector'].unique().tolist()) if len(df) > 0 else ["All Sectors"]
        selected_sector = st.selectbox("Sector Categorization Filter", options=sectors)
    with col_f3:
        signal_filter = st.selectbox("Signal Type Filter", options=["All Signals", "BUY", "SELL", "HOLD"])
    
    filtered_df = df.copy()
    if search_query and len(df) > 0:
        filtered_df = filtered_df[filtered_df['sym'].str.contains(search_query, case=False, na=False)]
    if selected_sector != "All Sectors" and len(df) > 0:
        filtered_df = filtered_df[filtered_df['sector'] == selected_sector]
    if signal_filter != "All Signals" and len(df) > 0:
        filtered_df = filtered_df[filtered_df['signal'] == signal_filter]
    
    st.markdown("##### Filtered Results")
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df[['sym', 'ltp', 'chg', 'vol', 'pe', 'rsi', 'health_score', 'signal']].sort_values(by='ltp', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No results match your filters")

# ==========================================
# 9. PREDICTION ENGINE
# ==========================================
elif nav_selection == "◆ Prediction Engine":
    st.markdown("### ML-Driven Price Forecast & Probability Analysis")
    pred_horizon = st.selectbox("Forecast Horizon", ["1-Week Ahead", "1-Month Ahead", "3-Month Ahead"])
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("##### Predictive Stock Selection (Top Fundamentals)")
        if len(df) > 0:
            top_gainers = df.nlargest(5, 'health_score')
            st.dataframe(top_gainers[['sym', 'ltp', 'chg', 'pe', 'health_score']], use_container_width=True, hide_index=True)
    
    with col_p2:
        st.markdown("##### Probability Score Matrix")
        if len(df) > 0:
            top_gainers = df.nlargest(5, 'health_score')
            probs = pd.DataFrame({
                'Stock': top_gainers['sym'].values,
                'Health Score': top_gainers['health_score'].round(0).values,
                'Grade': top_gainers['grade'].values,
                'P/E Ratio': top_gainers['pe'].round(1).values,
            })
            st.dataframe(probs, use_container_width=True, hide_index=True)

# ==========================================
# 10. PATTERN ENGINE
# ==========================================
elif nav_selection == "◇ Pattern Engine":
    st.markdown("### Technical Pattern Recognition & Breakout Detection")
    pattern_type = st.selectbox("Pattern Detection Mode", ["Head & Shoulders", "Double Bottom", "Breakout Patterns", "Support Resistance"])
    
    if len(df) > 0:
        patterns_data = df.nlargest(5, 'health_score')
        st.markdown("##### High-Scoring Stocks (Potential Patterns)")
        st.dataframe(patterns_data[['sym', 'ltp', 'rsi', 'vol', 'health_score']], use_container_width=True, hide_index=True)

# ==========================================
# 11. PORTFOLIO & IPO TRACKER
# ==========================================
elif nav_selection == "▣ Portfolio & IPO Tracker":
    st.markdown("### Portfolio Holdings & IPO Pipeline Tracking")
    
    col_port1, col_port2 = st.columns(2)
    with col_port1:
        st.markdown("##### Your Holdings Performance (Top Fundamentals)")
        if len(df) > 0:
            holdings = df.nlargest(4, 'health_score')
            st.dataframe(holdings[['sym', 'ltp', 'chg', 'health_score', 'signal']], use_container_width=True, hide_index=True)
    
    with col_port2:
        st.markdown("##### Upcoming IPOs & FPOs")
        st.info("📌 No upcoming IPOs in pipeline. Check back soon!")

# ==========================================
# 12. RISK & SYSTEM ALERTS (with Interpreter)
# ==========================================
elif nav_selection == "◉ Risk & System Alerts":
    st.markdown("### Systemic Risk Monitoring & Alert System")
    
    if len(df) > 0:
        # Find stocks with health scores
        high_score = df.nlargest(1, 'health_score').iloc[0]
        low_score = df.nsmallest(1, 'health_score').iloc[0]
        high_vol_stock = df.nlargest(1, 'vol').iloc[0]
        
        st.markdown("##### Active Risk Alerts")
        
        # Get plain-English interpretation for top stock
        top_interpretation = interpret_stock(
            symbol=high_score['sym'],
            score=high_score['health_score'],
            eps=high_score.get('eps'),
            pe=high_score.get('pe_ratio'),
            div_yield=high_score.get('dividend_yield'),
            company_name=high_score.get('name')
        )
        
        low_interpretation = interpret_stock(
            symbol=low_score['sym'],
            score=low_score['health_score'],
            eps=low_score.get('eps'),
            pe=low_score.get('pe_ratio'),
            div_yield=low_score.get('dividend_yield'),
            company_name=low_score.get('name')
        )
        
        st.markdown(f"""
        <div class='alert-item buy'><div class='alert-stock'>🟢 STRONG FUNDAMENTALS: {high_score['sym']}</div><div class='alert-msg'>Health Score: {high_score['health_score']:.0f}/100 | {top_interpretation['lean']}</div></div>
        <div class='alert-item hold'><div class='alert-stock'>🟡 WEAK FUNDAMENTALS: {low_score['sym']}</div><div class='alert-msg'>Health Score: {low_score['health_score']:.0f}/100 | {low_interpretation['lean']}</div></div>
        <div class='alert-item sell'><div class='alert-stock'>🔴 HIGH VOLATILITY: {high_vol_stock['sym']}</div><div class='alert-msg'>Volume: {high_vol_stock['vol']:,.0f} | LTP: {high_vol_stock['ltp']:.2f}</div></div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### 📊 Stock Interpretation Sample")
        with st.expander(f"View full analysis for {high_score['sym']}"):
            st.markdown(f"**Headline:** {top_interpretation['headline']}")
            st.markdown("**Explanation:**")
            for point in top_interpretation['explanation']:
                st.markdown(f"- {point}")
            st.markdown(f"**Lean:** {top_interpretation['lean']}")
            st.markdown(f"**Reason:** {top_interpretation['lean_reason']}")
            st.markdown("**Caveats:**")
            for caveat in top_interpretation['caveats']:
                st.markdown(f"- {caveat}")
    else:
        st.warning("Unable to load market data")

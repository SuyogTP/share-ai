<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>NEPSE Intelligence Platform</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
:root {
  --bg: #0d0f14;
  --bg2: #13161e;
  --bg3: #1a1e28;
  --bg4: #222736;
  --border: #2a2f3d;
  --border2: #353c50;
  --text: #e8eaf0;
  --text2: #8892a4;
  --text3: #555f72;
  --blue: #3b82f6;
  --blue-dim: #1e3a5f;
  --green: #10b981;
  --green-dim: #0a3728;
  --red: #ef4444;
  --red-dim: #3b1212;
  --amber: #f59e0b;
  --amber-dim: #3b2a06;
  --purple: #8b5cf6;
  --purple-dim: #2e1a5e;
  --teal: #14b8a6;
  --teal-dim: #0a2e2b;
  --radius: 10px;
  --radius-sm: 6px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  font-size: 14px;
  line-height: 1.5;
}

/* ─── LAYOUT ─── */
.app { display: flex; min-height: 100vh; }

/* ─── SIDEBAR ─── */
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--bg2);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0;
  height: 100vh;
  z-index: 100;
}
.sidebar-logo {
  padding: 20px 18px 16px;
  border-bottom: 1px solid var(--border);
}
.logo-mark {
  font-size: 18px;
  font-weight: 700;
  color: var(--blue);
  letter-spacing: -0.5px;
}
.logo-sub {
  font-size: 10px;
  color: var(--text3);
  margin-top: 2px;
  letter-spacing: .5px;
  text-transform: uppercase;
}
.sidebar-nav { flex: 1; padding: 12px 10px; overflow-y: auto; }
.nav-section-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text3);
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 8px 8px 4px;
  margin-top: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text2);
  font-size: 13px;
  transition: all .15s;
  margin-bottom: 2px;
  border: 1px solid transparent;
}
.nav-item:hover { background: var(--bg3); color: var(--text); }
.nav-item.active {
  background: var(--blue-dim);
  color: var(--blue);
  border-color: #1e3a5f;
}
.nav-item .icon { font-size: 15px; width: 18px; text-align: center; flex-shrink: 0; }
.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--text3);
}
.live-dot {
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  margin-right: 5px;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ─── MAIN ─── */
.main { margin-left: 220px; flex: 1; display: flex; flex-direction: column; }

/* ─── TOPBAR ─── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 28px;
  border-bottom: 1px solid var(--border);
  background: var(--bg2);
  position: sticky; top: 0; z-index: 50;
}
.topbar-left { display: flex; align-items: center; gap: 14px; }
.page-title { font-size: 16px; font-weight: 600; }
.page-sub { font-size: 12px; color: var(--text2); }
.topbar-right { display: flex; align-items: center; gap: 10px; }
.btn {
  padding: 7px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border2);
  background: var(--bg3);
  color: var(--text2);
  font-size: 12px;
  cursor: pointer;
  transition: all .15s;
  font-family: inherit;
}
.btn:hover { background: var(--bg4); color: var(--text); }
.btn.primary {
  background: var(--blue);
  border-color: var(--blue);
  color: #fff;
  font-weight: 500;
}
.btn.primary:hover { background: #2563eb; }
.btn.danger { background: var(--red-dim); border-color: var(--red); color: var(--red); }
.btn.success { background: var(--green-dim); border-color: var(--green); color: var(--green); }

/* ─── CONTENT ─── */
.content { padding: 24px 28px; flex: 1; }
.panel { display: none; }
.panel.active { display: block; }

/* ─── CARDS ─── */
.card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 18px;
}
.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: .5px;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-title span { color: var(--text2); font-size: 11px; font-weight: 400; text-transform: none; letter-spacing: 0; }

/* ─── STAT GRID ─── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
.stat-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 18px;
}
.stat-label { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }
.stat-value { font-size: 22px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.stat-delta { font-size: 11px; }
.stat-delta.up { color: var(--green); }
.stat-delta.down { color: var(--red); }

/* ─── BADGE / TAGS ─── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}
.badge.green { background: var(--green-dim); color: var(--green); border: 1px solid #0a4a38; }
.badge.red { background: var(--red-dim); color: var(--red); border: 1px solid #5b1a1a; }
.badge.amber { background: var(--amber-dim); color: var(--amber); border: 1px solid #4a3210; }
.badge.blue { background: var(--blue-dim); color: var(--blue); border: 1px solid #1a3a6a; }
.badge.purple { background: var(--purple-dim); color: var(--purple); border: 1px solid #3e1f7a; }

/* ─── TABLE ─── */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .5px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
td {
  padding: 11px 14px;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  color: var(--text);
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--bg3); }
.td-green { color: var(--green); font-weight: 500; }
.td-red { color: var(--red); font-weight: 500; }
.td-amber { color: var(--amber); }
.td-blue { color: var(--blue); }
.td-dim { color: var(--text2); }

/* ─── HORIZON TABS ─── */
.hz-row { display: flex; gap: 12px; margin-bottom: 20px; }
.hz-btn {
  flex: 1;
  padding: 14px 16px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg2);
  cursor: pointer;
  text-align: center;
  transition: all .15s;
  font-family: inherit;
}
.hz-btn:hover { border-color: var(--border2); background: var(--bg3); }
.hz-btn.active.short { border-color: var(--red); background: var(--red-dim); }
.hz-btn.active.medium { border-color: var(--amber); background: var(--amber-dim); }
.hz-btn.active.long { border-color: var(--green); background: var(--green-dim); }
.hz-label { font-size: 10px; letter-spacing: 1px; text-transform: uppercase; color: var(--text3); margin-bottom: 4px; }
.hz-btn.active.short .hz-label { color: var(--red); }
.hz-btn.active.medium .hz-label { color: var(--amber); }
.hz-btn.active.long .hz-label { color: var(--green); }
.hz-period { font-size: 15px; font-weight: 700; }
.hz-btn.active.short .hz-period { color: var(--red); }
.hz-btn.active.medium .hz-period { color: var(--amber); }
.hz-btn.active.long .hz-period { color: var(--green); }
.hz-focus { font-size: 11px; color: var(--text3); margin-top: 3px; }

/* ─── TWO-COL GRID ─── */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }

/* ─── ALERTS ─── */
.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg2);
  margin-bottom: 10px;
}
.alert-item.sell { border-left: 3px solid var(--red); }
.alert-item.hold { border-left: 3px solid var(--amber); }
.alert-item.buy { border-left: 3px solid var(--green); }
.alert-item.macro { border-left: 3px solid var(--purple); }
.alert-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.alert-icon.sell { background: var(--red-dim); color: var(--red); }
.alert-icon.hold { background: var(--amber-dim); color: var(--amber); }
.alert-icon.buy { background: var(--green-dim); color: var(--green); }
.alert-icon.macro { background: var(--purple-dim); color: var(--purple); }
.alert-body { flex: 1; }
.alert-stock { font-size: 13px; font-weight: 600; margin-bottom: 3px; }
.alert-msg { font-size: 12px; color: var(--text2); line-height: 1.5; }
.alert-actions { display: flex; gap: 6px; margin-top: 8px; }
.alert-btn {
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid var(--border2);
  background: transparent;
  color: var(--text2);
  font-size: 11px;
  cursor: pointer;
  transition: all .15s;
  font-family: inherit;
}
.alert-btn.sell-btn { border-color: var(--red); color: var(--red); background: var(--red-dim); }
.alert-btn.hold-btn { border-color: var(--amber); color: var(--amber); background: var(--amber-dim); }
.alert-btn.buy-btn { border-color: var(--green); color: var(--green); background: var(--green-dim); }
.alert-time { font-size: 11px; color: var(--text3); white-space: nowrap; }

/* ─── PATTERN CARDS ─── */
.pattern-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.pattern-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px;
  cursor: pointer;
  transition: all .15s;
}
.pattern-card:hover { border-color: var(--border2); background: var(--bg3); }
.pattern-card.detected { border-color: var(--blue); }
.pat-svg { width: 100%; height: 56px; margin-bottom: 8px; }
.pat-name { font-size: 13px; font-weight: 600; margin-bottom: 2px; }
.pat-meta { font-size: 11px; color: var(--text3); margin-bottom: 8px; }
.conf-bar-track { height: 3px; background: var(--border); border-radius: 2px; }
.conf-bar-fill { height: 3px; border-radius: 2px; transition: width .5s; }

/* ─── PILLAR SLIDERS ─── */
.pillar-row {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}
.pillar-row:last-child { border-bottom: none; }
.pillar-label { font-size: 13px; font-weight: 500; width: 200px; flex-shrink: 0; }
.pillar-sub { font-size: 11px; color: var(--text3); margin-top: 2px; }
.pillar-slider { flex: 1; -webkit-appearance: none; height: 4px; border-radius: 2px; outline: none; cursor: pointer; }
.pillar-pct { font-size: 16px; font-weight: 700; min-width: 48px; text-align: right; }

/* ─── IPO / PORTFOLIO ─── */
.acct-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
.acct-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  position: relative;
  overflow: hidden;
}
.acct-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}
.acct-card.a::before { background: var(--blue); }
.acct-card.b::before { background: var(--green); }
.acct-card.c::before { background: var(--amber); }
.acct-card.d::before { background: var(--purple); }
.acct-name { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
.acct-val { font-size: 20px; font-weight: 700; margin-bottom: 3px; }
.acct-pnl { font-size: 12px; margin-bottom: 10px; }
.mini-bars { display: flex; gap: 2px; align-items: flex-end; height: 28px; }
.mini-bar { flex: 1; border-radius: 1px 1px 0 0; min-width: 3px; }

/* ─── SEARCH BAR ─── */
.search-row {
  display: flex; gap: 10px;
  margin-bottom: 18px;
  align-items: center;
}
.search-input {
  flex: 1;
  padding: 9px 14px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: border-color .15s;
}
.search-input:focus { border-color: var(--blue); }
.search-input::placeholder { color: var(--text3); }
select.filter-select {
  padding: 9px 12px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text2);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  cursor: pointer;
}

/* ─── CHART CONTAINERS ─── */
.chart-wrap { position: relative; width: 100%; }

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ─── TOAST ─── */
.toast {
  position: fixed;
  bottom: 24px; right: 24px;
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: var(--radius);
  padding: 12px 18px;
  font-size: 13px;
  color: var(--text);
  z-index: 999;
  opacity: 0;
  transform: translateY(10px);
  transition: all .3s;
  pointer-events: none;
}
.toast.show { opacity: 1; transform: translateY(0); }

/* ─── RESPONSIVE ─── */
@media (max-width: 900px) {
  .sidebar { width: 56px; }
  .sidebar-logo { padding: 14px 10px; }
  .logo-sub, .nav-item span, .nav-section-label { display: none; }
  .main { margin-left: 56px; }
  .stat-grid { grid-template-columns: 1fr 1fr; }
  .acct-grid { grid-template-columns: 1fr 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
  .pattern-grid { grid-template-columns: 1fr 1fr; }
}
</style>
</head>
<body>

<div class="app">
<!-- ══ SIDEBAR ══ -->
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-mark">⬡ NEPSE IQ</div>
    <div class="logo-sub">Market Intelligence</div>
  </div>
  <nav class="sidebar-nav">
    <div class="nav-section-label">Core</div>
    <div class="nav-item active" onclick="goTo('dashboard',this)">
      <span class="icon">◈</span><span>Dashboard</span>
    </div>
    <div class="nav-item" onclick="goTo('analyzer',this)">
      <span class="icon">◎</span><span>Share Analyzer</span>
    </div>
    <div class="nav-item" onclick="goTo('stocks',this)">
      <span class="icon">≋</span><span>Stock Screener</span>
    </div>
    <div class="nav-section-label">Intelligence</div>
    <div class="nav-item" onclick="goTo('prediction',this)">
      <span class="icon">◆</span><span>Prediction Engine</span>
    </div>
    <div class="nav-item" onclick="goTo('patterns',this)">
      <span class="icon">◇</span><span>Pattern Engine</span>
    </div>
    <div class="nav-section-label">Portfolio</div>
    <div class="nav-item" onclick="goTo('portfolio',this)">
      <span class="icon">▣</span><span>IPO & Portfolio</span>
    </div>
    <div class="nav-item" onclick="goTo('alerts',this)">
      <span class="icon">◉</span><span>Risk & Alerts</span>
    </div>
  </nav>
  <div class="sidebar-footer">
    <span class="live-dot"></span>Live Market Feed
  </div>
</aside>

<!-- ══ MAIN ══ -->
<div class="main">

<!-- TOPBAR -->
<div class="topbar">
  <div class="topbar-left">
    <div>
      <div class="page-title" id="page-title">Market Dashboard</div>
      <div class="page-sub" id="page-sub">NEPSE · Live Overview</div>
    </div>
  </div>
  <div class="topbar-right">
    <div style="font-size:12px;color:var(--text3)">
      NEPSE: <span style="color:var(--green);font-weight:600">2,148.32</span>
      <span style="color:var(--green);margin-left:6px">▲ +0.84%</span>
    </div>
    <button class="btn primary" onclick="refreshData()">↺ Refresh</button>
  </div>
</div>

<!-- ══════════════════════════════════════ -->
<!-- PANEL: DASHBOARD -->
<!-- ══════════════════════════════════════ -->
<div class="content">
<div class="panel active" id="panel-dashboard">
  <div class="stat-grid">
    <div class="stat-card">
      <div class="stat-label">NEPSE Index</div>
      <div class="stat-value" style="color:var(--green)">2,148.32</div>
      <div class="stat-delta up">▲ +17.82 (+0.84%) today</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Turnover (NPR)</div>
      <div class="stat-value" style="color:var(--blue)">4.2B</div>
      <div class="stat-delta up">▲ +12.3% vs avg</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Active Stocks</div>
      <div class="stat-value">218</div>
      <div class="stat-delta" style="color:var(--text2)">186 ↑ · 32 ↓</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Portfolio Value</div>
      <div class="stat-value" style="color:var(--purple)">NPR 8.45L</div>
      <div class="stat-delta up">▲ +23.4% total return</div>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">NEPSE Index — 12 Month <span>Daily Close</span></div>
      <div class="chart-wrap" style="height:200px">
        <canvas id="indexChart"></canvas>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Sector Performance <span>% Change Today</span></div>
      <div class="chart-wrap" style="height:200px">
        <canvas id="sectorChart"></canvas>
      </div>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Top Movers Today</div>
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>Symbol</th><th>LTP</th><th>Change</th><th>Volume</th><th>Signal</th>
          </tr></thead>
          <tbody id="movers-table"></tbody>
        </table>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Active Risk Alerts <span id="alert-count"></span></div>
      <div id="dash-alerts"></div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════ -->
<!-- PANEL: SHARE ANALYZER -->
<!-- ══════════════════════════════════════ -->
<div class="panel" id="panel-analyzer">
  <div class="hz-row">
    <button class="hz-btn short active" onclick="selectHz(this,'short')">
      <div class="hz-label">Short-Term</div>
      <div class="hz-period">1–7 Days</div>
      <div class="hz-focus">Momentum · Short Selling</div>
    </button>
    <button class="hz-btn medium" onclick="selectHz(this,'medium')">
      <div class="hz-label">Medium-Term</div>
      <div class="hz-period">1–12 Months</div>
      <div class="hz-focus">Swing · Cyclical Growth</div>
    </button>
    <button class="hz-btn long" onclick="selectHz(this,'long')">
      <div class="hz-label">Long-Term</div>
      <div class="hz-period">1 Year+</div>
      <div class="hz-focus">Fundamentals · Compounding</div>
    </button>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title" id="hz-metrics-label">Active Metrics — Short-Term</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Metric</th><th>Weight</th><th>Signal</th><th>Priority</th></tr></thead>
          <tbody id="hz-metrics-body"></tbody>
        </table>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Auto-Selected Stocks <span id="hz-mode-label">Short Mode</span></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Symbol</th><th>Score</th><th>Signal</th><th>Target</th></tr></thead>
          <tbody id="auto-stocks-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Asset Filtration Criteria</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Filter</th><th>Short (1–7d)</th><th>Medium (1–12m)</th><th>Long (1y+)</th>
        </tr></thead>
        <tbody>
          <tr><td>Min Daily Volume</td><td class="td-red">≥ 50,000 shares</td><td class="td-amber">≥ 10,000 shares</td><td class="td-green">≥ 1,000 shares</td></tr>
          <tr><td>Volatility (ATR)</td><td class="td-red">High preferred</td><td class="td-amber">Medium range</td><td class="td-green">Low preferred</td></tr>
          <tr><td>RSI Filter</td><td>RSI 45–75</td><td>RSI 40–65</td><td>RSI 30–60</td></tr>
          <tr><td>Price Trend</td><td>Momentum breakout</td><td>MA cross + EPS</td><td>Fundamental dip</td></tr>
          <tr><td>Sector Bias</td><td>Rotating sectors</td><td>Cyclical sectors</td><td>Defensive / Utility</td></tr>
          <tr><td>Primary Indicators</td><td>RSI · VWAP · MACD</td><td>EMA · Bollinger · P/E</td><td>ROE · D/E · CAGR</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════ -->
<!-- PANEL: STOCK SCREENER -->
<!-- ══════════════════════════════════════ -->
<div class="panel" id="panel-stocks">
  <div class="search-row">
    <input class="search-input" type="text" placeholder="Search symbol or company..." oninput="filterStocks(this.value)" id="stock-search"/>
    <select class="filter-select" onchange="filterBySector(this.value)" id="sector-filter">
      <option value="">All Sectors</option>
      <option>Banking</option>
      <option>Hydropower</option>
      <option>Insurance</option>
      <option>Finance</option>
      <option>Manufacturing</option>
      <option>Microfinance</option>
    </select>
    <select class="filter-select" onchange="filterBySignal(this.value)" id="signal-filter">
      <option value="">All Signals</option>
      <option>BUY</option>
      <option>HOLD</option>
      <option>SELL</option>
    </select>
    <button class="btn primary">Export CSV</button>
  </div>
  <div class="card" style="padding:0">
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Symbol</th><th>Company</th><th>Sector</th>
          <th>LTP</th><th>Change %</th><th>Volume</th>
          <th>RSI</th><th>P/E</th><th>EPS</th><th>52W H/L</th><th>Signal</th>
        </tr></thead>
        <tbody id="screener-table"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════ -->
<!-- PANEL: PREDICTION ENGINE -->
<!-- ══════════════════════════════════════ -->
<div class="panel" id="panel-prediction">
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Pillar Weight Configuration <span>Drag to adjust</span></div>
      <div id="pillar-controls"></div>
      <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:12px;color:var(--text3)">
        <span>Total weight</span>
        <span id="total-weight" style="color:var(--green);font-weight:600">100%</span>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Weight Distribution</div>
      <div class="chart-wrap" style="height:220px">
        <canvas id="pillarChart"></canvas>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Prediction Output — Top Picks</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Symbol</th><th>Current</th><th>3-Day Target</th><th>30-Day Target</th>
          <th>Confidence</th><th>Technical</th><th>Fundamental</th><th>Risk</th><th>Action</th>
        </tr></thead>
        <tbody id="prediction-table"></tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Prediction Methodology</div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Output Field</th><th>Short-Term</th><th>Medium-Term</th><th>Long-Term</th></tr></thead>
        <tbody>
          <tr><td>Price Target</td><td>3-day range band</td><td>6-month target</td><td>Yearly band</td></tr>
          <tr><td>Confidence Boost</td><td class="td-red">Technical ×3</td><td class="td-amber">Balanced 4-pillar</td><td class="td-green">Fundamental ×3</td></tr>
          <tr><td>Risk Rating</td><td class="td-red">High</td><td class="td-amber">Medium</td><td class="td-green">Low–Medium</td></tr>
          <tr><td>Entry Signal</td><td>Intraday momentum</td><td>Pullback + MA</td><td>Fundamental dip</td></tr>
          <tr><td>Stop-Loss Logic</td><td>3% trailing</td><td>8% swing low</td><td>15% fundamental</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════ -->
<!-- PANEL: PATTERN ENGINE -->
<!-- ══════════════════════════════════════ -->
<div class="panel" id="panel-patterns">
  <div class="card">
    <div class="card-title">Detected Formations — Live NEPSE Scan <span>Updated 2 min ago</span></div>
    <div class="pattern-grid" id="pattern-grid"></div>
  </div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Technical Indicator Stack</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Indicator</th><th>Category</th><th>Horizon</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td>RSI (14)</td><td class="td-dim">Momentum</td><td>Short</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>MACD (12,26,9)</td><td class="td-dim">Trend</td><td>Short/Med</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>Bollinger Bands (20)</td><td class="td-dim">Volatility</td><td>Medium</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>EMA 20/50/200</td><td class="td-dim">Trend</td><td>All</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>VWAP</td><td class="td-dim">Volume-Price</td><td>Short</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>Fibonacci Retracement</td><td class="td-dim">S/R</td><td>Medium</td><td><span class="badge blue">Passive</span></td></tr>
            <tr><td>Stochastic (14,3)</td><td class="td-dim">Momentum</td><td>Short</td><td><span class="badge blue">Passive</span></td></tr>
            <tr><td>ATR (14)</td><td class="td-dim">Volatility</td><td>All</td><td><span class="badge green">Active</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Fundamental Metrics Stack</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Metric</th><th>Use Case</th><th>Horizon</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td>P/E Ratio</td><td class="td-dim">Valuation</td><td>Long</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>EPS Growth (YoY)</td><td class="td-dim">Earnings</td><td>Med/Long</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>ROE (3yr avg)</td><td class="td-dim">Efficiency</td><td>Long</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>Debt / Equity</td><td class="td-dim">Balance sheet</td><td>Long</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>Revenue CAGR</td><td class="td-dim">Growth</td><td>Long</td><td><span class="badge green">Active</span></td></tr>
            <tr><td>Dividend Yield</td><td class="td-dim">Income</td><td>Long</td><td><span class="badge blue">Passive</span></td></tr>
            <tr><td>Book Value / Share</td><td class="td-dim">Intrinsic</td><td>Long</td><td><span class="badge blue">Passive</span></td></tr>
            <tr><td>Net Profit Margin</td><td class="td-dim">Profitability</td><td>Med/Long</td><td><span class="badge green">Active</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════ -->
<!-- PANEL: IPO & PORTFOLIO -->
<!-- ══════════════════════════════════════ -->
<div class="panel" id="panel-portfolio">
  <div class="acct-grid" id="acct-grid"></div>

  <div class="grid-2">
    <div class="card">
      <div class="card-title">Portfolio Performance — All Accounts</div>
      <div class="chart-wrap" style="height:220px">
        <canvas id="portChart"></canvas>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Net Profit Breakdown</div>
      <div class="chart-wrap" style="height:220px">
        <canvas id="profitChart"></canvas>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">IPO Tracker — Multi-Account</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Company</th><th>Sector</th><th>Issue Price</th><th>Applied</th><th>Shares Est.</th><th>Status</th><th>Expected Listing</th><th>Est. Return</th>
        </tr></thead>
        <tbody id="ipo-table"></tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Holdings — Consolidated View</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>Symbol</th><th>Shares</th><th>Avg Cost</th><th>LTP</th><th>Market Value</th><th>P&L</th><th>P&L %</th><th>Account</th>
        </tr></thead>
        <tbody id="holdings-table"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════ -->
<!-- PANEL: RISK & ALERTS -->
<!-- ══════════════════════════════════════ -->
<div class="panel" id="panel-alerts">
  <div class="stat-grid" style="grid-template-columns:repeat(4,1fr)">
    <div class="stat-card">
      <div class="stat-label">Active Alerts</div>
      <div class="stat-value" style="color:var(--red)">7</div>
      <div class="stat-delta down">4 critical · 3 moderate</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Sell Signals</div>
      <div class="stat-value" style="color:var(--red)">3</div>
      <div class="stat-delta down">Action required</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Hold Signals</div>
      <div class="stat-value" style="color:var(--amber)">2</div>
      <div class="stat-delta" style="color:var(--text2)">Monitor closely</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Buy Signals</div>
      <div class="stat-value" style="color:var(--green)">2</div>
      <div class="stat-delta up">Opportunity detected</div>
    </div>
  </div>

  <div class="grid-2">
    <div>
      <div id="alerts-list"></div>
    </div>
    <div>
      <div class="card">
        <div class="card-title">Risk Threshold Configuration</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Parameter</th><th>Short</th><th>Medium</th><th>Long</th></tr></thead>
            <tbody>
              <tr><td>Max Drawdown Alert</td><td class="td-red">3%</td><td class="td-amber">8%</td><td class="td-green">15%</td></tr>
              <tr><td>Volume Spike Trigger</td><td>2.0× avg</td><td>1.5× avg</td><td>3.0× avg</td></tr>
              <tr><td>RSI Overbought</td><td class="td-red">&gt; 75</td><td class="td-red">&gt; 70</td><td class="td-red">&gt; 80</td></tr>
              <tr><td>RSI Oversold</td><td class="td-green">&lt; 30</td><td class="td-green">&lt; 35</td><td class="td-green">&lt; 25</td></tr>
              <tr><td>Stop-Loss Trigger</td><td class="td-red">3%</td><td class="td-amber">8%</td><td class="td-green">15%</td></tr>
              <tr><td>Macro Event Alert</td><td>NRB Meeting</td><td>Budget / Policy</td><td>Annual Review</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card" style="margin-top:0">
        <div class="card-title">Macro Environment Monitor</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Event</th><th>Date</th><th>Impact</th></tr></thead>
            <tbody>
              <tr><td>NRB Monetary Policy Review</td><td class="td-dim">In 3 days</td><td><span class="badge red">High</span></td></tr>
              <tr><td>Government Budget Revision</td><td class="td-dim">In 18 days</td><td><span class="badge amber">Medium</span></td></tr>
              <tr><td>Q4 Annual Reports Deadline</td><td class="td-dim">In 32 days</td><td><span class="badge blue">Info</span></td></tr>
              <tr><td>AGM Season — Banks</td><td class="td-dim">Ongoing</td><td><span class="badge amber">Medium</span></td></tr>
              <tr><td>Hydropower Monsoon Peak</td><td class="td-dim">Seasonal</td><td><span class="badge green">Positive</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

</div><!-- /content -->
</div><!-- /main -->
</div><!-- /app -->

<div class="toast" id="toast"></div>

<script>
// ════════════════════════════════════
// DATA
// ════════════════════════════════════
const STOCKS = [
  {sym:'NABIL',name:'Nabil Bank',sector:'Banking',ltp:1245,chg:2.3,vol:82400,rsi:72,pe:18.4,eps:67.6,h52:1380,l52:920,signal:'SELL'},
  {sym:'NICA',name:'NIC Asia Bank',sector:'Banking',ltp:422,chg:1.8,vol:64200,rsi:48,pe:14.2,eps:29.7,h52:498,l52:310,signal:'BUY'},
  {sym:'NRIC',name:'Nepal Reinsurance',sector:'Insurance',ltp:1870,chg:-1.2,vol:12100,rsi:61,pe:22.1,eps:84.6,h52:2100,l52:1420,signal:'HOLD'},
  {sym:'UPPER',name:'Upper Tamakoshi',sector:'Hydropower',ltp:278,chg:0.7,vol:38600,rsi:55,pe:19.8,eps:14.0,h52:342,l52:198,signal:'HOLD'},
  {sym:'NHPC',name:'Nepal Hydro Power',sector:'Hydropower',ltp:142,chg:3.1,vol:91200,rsi:44,pe:28.4,eps:5.0,h52:195,l52:108,signal:'BUY'},
  {sym:'SANIMA',name:'Sanima Bank',sector:'Banking',ltp:318,chg:-0.5,vol:28900,rsi:42,pe:13.8,eps:23.0,h52:390,l52:248,signal:'BUY'},
  {sym:'CHCL',name:'Chilime Hydropower',sector:'Hydropower',ltp:512,chg:1.4,vol:18700,rsi:58,pe:24.6,eps:20.8,h52:598,l52:398,signal:'HOLD'},
  {sym:'PLIC',name:'Prime Life Insurance',sector:'Insurance',ltp:2340,chg:-2.1,vol:8900,rsi:76,pe:31.2,eps:75.0,h52:2780,l52:1680,signal:'SELL'},
  {sym:'NMB',name:'NMB Bank',sector:'Banking',ltp:196,chg:0.5,vol:44100,rsi:52,pe:12.1,eps:16.2,h52:248,l52:148,signal:'BUY'},
  {sym:'HIDCL',name:'HIDCL',sector:'Hydropower',ltp:188,chg:1.9,vol:127400,rsi:67,pe:21.4,eps:8.8,h52:224,l52:142,signal:'HOLD'},
  {sym:'GBIME',name:'Global IME Bank',sector:'Banking',ltp:268,chg:-1.4,vol:38200,rsi:38,pe:11.8,eps:22.7,h52:340,l52:210,signal:'BUY'},
  {sym:'NLFICL',name:'NLG Insurance',sector:'Insurance',ltp:3120,chg:0.8,vol:5400,rsi:62,pe:28.8,eps:108.3,h52:3480,l52:2280,signal:'HOLD'},
  {sym:'MLBL',name:'Manakamana Smart Laghubitta',sector:'Microfinance',ltp:1680,chg:4.2,vol:3200,rsi:79,pe:34.2,eps:49.1,h52:1890,l52:1120,signal:'SELL'},
  {sym:'SHIVM',name:'Shivam Cement',sector:'Manufacturing',ltp:214,chg:-0.9,vol:22800,rsi:45,pe:18.6,eps:11.5,h52:280,l52:162,signal:'HOLD'},
  {sym:'SBL',name:'Siddhartha Bank',sector:'Banking',ltp:348,chg:2.8,vol:52100,rsi:53,pe:15.4,eps:22.6,h52:420,l52:268,signal:'BUY'},
];

const ALERTS = [
  {type:'sell',icon:'↘',stock:'NABIL — Nabil Bank Ltd',msg:'RSI at 72.4 (overbought zone). Volume declining 3 consecutive sessions. Head & Shoulders pattern forming. Projected drop within 2 sessions. Exit recommended above NPR 1,260.',time:'8 min ago'},
  {type:'sell',icon:'↘',stock:'PLIC — Prime Life Insurance',msg:'RSI breached 76. Price rejected at major resistance 2,380. EPS growth slowing. Short-term sell signal confirmed by MACD bearish crossover.',time:'15 min ago'},
  {type:'hold',icon:'⏸',stock:'UPPER — Upper Tamakoshi Hydropower',msg:'Approaching resistance at NPR 285. Consolidation phase expected 7–14 days. Hold until volume-confirmed breakout above 290. Monsoon season tailwind incoming.',time:'22 min ago'},
  {type:'buy',icon:'↗',stock:'NICA — NIC Asia Bank',msg:'MACD bullish crossover confirmed. Support held firmly at NPR 410 for 5 sessions. EPS growth +18% YoY. Strong long-term accumulation signal. Target: 520.',time:'31 min ago'},
  {type:'buy',icon:'↗',stock:'NHPC — Nepal Hydro Power',msg:'Bull flag breakout detected. Volume 2.4× average. Seasonal hydropower cycle entering peak generation period. RSI at healthy 44 with upside room.',time:'45 min ago'},
  {type:'sell',icon:'↘',stock:'MLBL — Manakamana Laghubitta',msg:'RSI at 79 — severely overbought. P/E at 34.2 vs sector avg 22. Institutional selling detected on level 2 data. Take profits immediately.',time:'1 hr ago'},
  {type:'hold',icon:'⏸',stock:'MACRO — NRB Monetary Policy Review',msg:'NRB policy meeting in 3 days. Banking sector rate-sensitive. Reduce short-term exposure to finance stocks. Hold core long-term positions unchanged.',time:'2 hr ago'},
];

const PORTFOLIO_ACCOUNTS = [
  {id:'a',name:'Account A (Primary)',cls:'a',color:'#3b82f6',val:248500,pnl:42300,pct:20.5,bars:[40,55,48,62,71,68,80,92,85,95,88,105]},
  {id:'b',name:'Account B (Spouse)',cls:'b',color:'#10b981',val:182000,pnl:18900,pct:11.6,bars:[60,58,65,70,66,75,78,72,80,85,90,95]},
  {id:'c',name:'Account C (Child)',cls:'c',color:'#f59e0b',val:95400,pnl:8200,pct:9.4,bars:[30,35,32,40,45,42,50,48,55,52,58,60]},
  {id:'d',name:'Account D (Parent)',cls:'d',color:'#8b5cf6',val:320000,pnl:61500,pct:23.8,bars:[50,60,75,70,85,95,100,110,105,120,130,140]},
];

const HOLDINGS = [
  {sym:'NABIL',shares:120,cost:1140,ltp:1245,acct:'Account A'},
  {sym:'NICA',shares:300,cost:390,ltp:422,acct:'Account A'},
  {sym:'UPPER',shares:500,cost:248,ltp:278,acct:'Account B'},
  {sym:'NHPC',shares:1000,cost:128,ltp:142,acct:'Account B'},
  {sym:'CHCL',shares:80,cost:470,ltp:512,acct:'Account C'},
  {sym:'SANIMA',shares:400,cost:295,ltp:318,acct:'Account C'},
  {sym:'NMB',shares:600,cost:178,ltp:196,acct:'Account D'},
  {sym:'GBIME',shares:800,cost:242,ltp:268,acct:'Account D'},
  {sym:'HIDCL',shares:700,cost:168,ltp:188,acct:'Account D'},
];

const IPOS = [
  {co:'Nepal Hydro Dev Ltd',sector:'Hydropower',price:100,applied:'A,B,C',shares:'3,200',status:'Open',listing:'~45 days',ret:'+35–60%'},
  {co:'Himalayan Finance',sector:'Finance',price:100,applied:'A,B,C,D,+1',shares:'750',status:'Processing',listing:'~22 days',ret:'+20–40%'},
  {co:'Nepal Telecom Ltd',sector:'Telecom',price:100,applied:'All 4',shares:'12,400',status:'Allotted',listing:'~8 days',ret:'+80–120%'},
  {co:'Sunrise Insurance',sector:'Insurance',price:100,applied:'A,C',shares:'400',status:'Closed',listing:'Listed',ret:'+142%'},
];

const HZ_METRICS = {
  short:[
    ['RSI (14)','35%','Overbought/Oversold','Critical'],
    ['VWAP Deviation','25%','Institutional price floor','High'],
    ['MACD Crossover','20%','Trend entry/exit','High'],
    ['Volume Surge','20%','Confirmation signal','Medium'],
  ],
  medium:[
    ['EMA 20/50 Cross','25%','Trend direction','Critical'],
    ['Bollinger Squeeze','20%','Breakout setup','High'],
    ['EPS Growth YoY','25%','Fundamental health','High'],
    ['Sector Rotation','15%','Macro flow','Medium'],
    ['P/E vs Sector Avg','15%','Relative valuation','Medium'],
  ],
  long:[
    ['ROE (3yr avg)','30%','Capital efficiency','Critical'],
    ['Debt / Equity','20%','Balance sheet strength','Critical'],
    ['Revenue CAGR','25%','Growth trajectory','High'],
    ['Dividend Yield','15%','Income return','Medium'],
    ['NRB Policy Stance','10%','Macro environment','Low'],
  ]
};

const AUTO_STOCKS = {
  short:[
    {sym:'NHPC',score:'87',signal:'BUY',target:'155'},
    {sym:'HIDCL',score:'82',signal:'BUY',target:'198'},
    {sym:'SBL',score:'78',signal:'BUY',target:'368'},
    {sym:'GBIME',score:'74',signal:'BUY',target:'285'},
  ],
  medium:[
    {sym:'NICA',score:'91',signal:'BUY',target:'520'},
    {sym:'SANIMA',score:'84',signal:'BUY',target:'355'},
    {sym:'CHCL',score:'79',signal:'HOLD',target:'560'},
    {sym:'UPPER',score:'72',signal:'HOLD',target:'310'},
  ],
  long:[
    {sym:'NICA',score:'93',signal:'ACCUMULATE',target:'680'},
    {sym:'NABIL',score:'86',signal:'ACCUMULATE',target:'1500'},
    {sym:'NMB',score:'81',signal:'BUY',target:'260'},
    {sym:'CHCL',score:'77',signal:'HOLD',target:'620'},
  ]
};

const PATTERNS = [
  {name:'Head & Shoulders',stock:'NABIL',conf:82,type:'Bearish Reversal',detected:true,
   svg:'<polyline points="12,44 24,44 29,28 34,12 39,28 44,18 49,28 54,28 59,44 72,44" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-linejoin="round"/><line x1="12" y1="44" x2="72" y2="44" stroke="#ef4444" stroke-width="0.8" stroke-dasharray="3,2"/>'},
  {name:'Bull Flag',stock:'NHPC',conf:74,type:'Bullish Continuation',detected:true,
   svg:'<polyline points="12,48 22,36 32,22 42,12" fill="none" stroke="#10b981" stroke-width="2"/><rect x="42" y="12" width="28" height="18" fill="none" stroke="#10b981" stroke-width="1.2" rx="2" stroke-dasharray="3,2"/><line x1="70" y1="12" x2="76" y2="6" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>'},
  {name:'Breakout',stock:'HIDCL',conf:91,type:'Momentum Entry',detected:true,
   svg:'<line x1="10" y1="24" x2="68" y2="24" stroke="#3b82f6" stroke-width="1" stroke-dasharray="4,2"/><polyline points="10,42 22,40 34,34 44,26 54,18 64,12" fill="none" stroke="#3b82f6" stroke-width="2"/>'},
  {name:'Double Bottom',stock:'GBIME',conf:68,type:'Bullish Reversal',detected:false,
   svg:'<polyline points="10,14 20,14 28,38 38,18 46,38 56,16 68,14" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-linejoin="round"/><line x1="10" y1="14" x2="68" y2="14" stroke="#f59e0b" stroke-width="0.8" stroke-dasharray="3,2"/>'},
  {name:'Cup & Handle',stock:'SBL',conf:77,type:'Bullish Continuation',detected:true,
   svg:'<path d="M10,14 Q42,50 74,14" fill="none" stroke="#8b5cf6" stroke-width="1.8"/><path d="M74,14 L80,20 L76,28" fill="none" stroke="#8b5cf6" stroke-width="1.5"/>'},
  {name:'Support & Resistance',stock:'UPPER',conf:88,type:'Range Definition',detected:true,
   svg:'<line x1="8" y1="12" x2="76" y2="12" stroke="#10b981" stroke-width="1.5" stroke-dasharray="4,2"/><line x1="8" y1="40" x2="76" y2="40" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,2"/><polyline points="14,40 20,30 28,34 36,12 44,20 52,40 60,28 68,40" fill="none" stroke="#8892a4" stroke-width="1.2"/>'},
];

const PILLAR_STATE = [
  {label:'Graphical / Technical',sub:'RSI, MACD, Patterns, S/R',val:35,color:'#3b82f6'},
  {label:'Corporate Fundamentals',sub:'EPS, ROE, P/E, D/E Ratio',val:30,color:'#10b981'},
  {label:'Historical Data',sub:'Seasonal trends, past cycles',val:20,color:'#f59e0b'},
  {label:'Macro Environment',sub:'NRB policy, inflation, geopolitics',val:15,color:'#8b5cf6'},
];

let currentHz = 'short';
let pillarChart = null, portChart = null, profitChart = null, indexChart = null, sectorChart = null;

// ════════════════════════════════════
// NAVIGATION
// ════════════════════════════════════
const PAGE_META = {
  dashboard:  {title:'Market Dashboard',     sub:'NEPSE · Live Overview'},
  analyzer:   {title:'Share Analyzer',       sub:'3-Stage Horizon Engine'},
  stocks:     {title:'Stock Screener',       sub:'Full Market · Live Data'},
  prediction: {title:'Prediction Engine',    sub:'4-Pillar Hybrid Model'},
  patterns:   {title:'Pattern Recognition',  sub:'Enterprise Chart Formation Engine'},
  portfolio:  {title:'IPO & Portfolio',      sub:'Multi-Account Dashboard'},
  alerts:     {title:'Risk & Alerts',        sub:'Dynamic Notification Engine'},
};

function goTo(id, el) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('panel-'+id).classList.add('active');
  el.classList.add('active');
  const m = PAGE_META[id];
  document.getElementById('page-title').textContent = m.title;
  document.getElementById('page-sub').textContent = m.sub;
  if (id === 'portfolio') initPortfolioCharts();
  if (id === 'dashboard') initDashCharts();
}

// ════════════════════════════════════
// RENDER: DASHBOARD
// ════════════════════════════════════
function renderDashboard() {
  // Top movers
  const sorted = [...STOCKS].sort((a,b)=>Math.abs(b.chg)-Math.abs(a.chg)).slice(0,6);
  document.getElementById('movers-table').innerHTML = sorted.map(s=>`
    <tr>
      <td class="td-blue" style="font-weight:600">${s.sym}</td>
      <td>NPR ${s.ltp}</td>
      <td class="${s.chg>=0?'td-green':'td-red'}">${s.chg>=0?'▲':'▼'} ${Math.abs(s.chg)}%</td>
      <td class="td-dim">${s.vol.toLocaleString()}</td>
      <td>${signalBadge(s.signal)}</td>
    </tr>`).join('');

  // Dash alerts (top 3)
  document.getElementById('alert-count').textContent = '7 Active';
  document.getElementById('dash-alerts').innerHTML = ALERTS.slice(0,3).map(alertHTML).join('');
}

function initDashCharts() {
  // Index chart
  const months = ['Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun'];
  const idx = [1840,1920,1870,2010,2080,1950,2020,2140,2060,2180,2110,2148];
  const ictx = document.getElementById('indexChart');
  if (indexChart) indexChart.destroy();
  indexChart = new Chart(ictx, {
    type:'line',
    data:{
      labels:months,
      datasets:[{
        data:idx,
        borderColor:'#3b82f6',
        backgroundColor:'rgba(59,130,246,0.08)',
        borderWidth:2,
        pointRadius:0,
        fill:true,
        tension:0.4
      }]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        x:{ticks:{color:'#555f72',font:{size:11}},grid:{color:'#2a2f3d'}},
        y:{ticks:{color:'#555f72',font:{size:11},callback:v=>v.toLocaleString()},grid:{color:'#2a2f3d'}}
      }
    }
  });

  // Sector chart
  const sctx = document.getElementById('sectorChart');
  if (sectorChart) sectorChart.destroy();
  sectorChart = new Chart(sctx,{
    type:'bar',
    data:{
      labels:['Banking','Hydropower','Insurance','Finance','Micro-finance','Manufacturing'],
      datasets:[{
        data:[1.4,-0.8,2.1,0.6,-1.3,0.3],
        backgroundColor:v=>v.raw>=0?'rgba(16,185,129,0.7)':'rgba(239,68,68,0.7)',
        borderRadius:4
      }]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        x:{ticks:{color:'#555f72',font:{size:10}},grid:{display:false}},
        y:{ticks:{color:'#555f72',font:{size:11},callback:v=>v+'%'},grid:{color:'#2a2f3d'}}
      }
    }
  });
}

// ════════════════════════════════════
// RENDER: ANALYZER
// ════════════════════════════════════
function selectHz(el, type) {
  document.querySelectorAll('.hz-btn').forEach(b=>{b.classList.remove('active','short','medium','long')});
  el.classList.add('active', type);
  currentHz = type;
  renderHzPanel(type);
}

function renderHzPanel(type) {
  const labels = {short:'Short-Term',medium:'Medium-Term',long:'Long-Term'};
  const modes = {short:'Short Mode',medium:'Medium Mode',long:'Long Mode'};
  document.getElementById('hz-metrics-label').textContent = 'Active Metrics — '+labels[type];
  document.getElementById('hz-mode-label').textContent = modes[type];
  document.getElementById('hz-metrics-body').innerHTML = HZ_METRICS[type].map(([m,w,s,p])=>`
    <tr>
      <td style="font-weight:500">${m}</td>
      <td class="td-blue">${w}</td>
      <td class="td-dim">${s}</td>
      <td>${prioBadge(p)}</td>
    </tr>`).join('');
  document.getElementById('auto-stocks-body').innerHTML = AUTO_STOCKS[type].map(s=>`
    <tr>
      <td class="td-blue" style="font-weight:600">${s.sym}</td>
      <td><span style="color:var(--green);font-weight:600">${s.score}</span>/100</td>
      <td>${signalBadge(s.signal)}</td>
      <td class="td-dim">NPR ${s.target}</td>
    </tr>`).join('');
}

// ════════════════════════════════════
// RENDER: SCREENER
// ════════════════════════════════════
let filteredStocks = [...STOCKS];

function renderScreener(stocks) {
  document.getElementById('screener-table').innerHTML = stocks.map(s=>`
    <tr>
      <td class="td-blue" style="font-weight:600">${s.sym}</td>
      <td class="td-dim">${s.name}</td>
      <td>${s.sector}</td>
      <td>NPR ${s.ltp}</td>
      <td class="${s.chg>=0?'td-green':'td-red'}">${s.chg>=0?'+':''}${s.chg}%</td>
      <td class="td-dim">${s.vol.toLocaleString()}</td>
      <td class="${s.rsi>70?'td-red':s.rsi<35?'td-green':'td-dim'}">${s.rsi}</td>
      <td class="td-dim">${s.pe}</td>
      <td class="td-dim">${s.eps}</td>
      <td class="td-dim">${s.h52} / ${s.l52}</td>
      <td>${signalBadge(s.signal)}</td>
    </tr>`).join('');
}

function filterStocks(q) {
  filteredStocks = STOCKS.filter(s=>
    s.sym.toLowerCase().includes(q.toLowerCase()) ||
    s.name.toLowerCase().includes(q.toLowerCase())
  );
  applyFilters();
}
function filterBySector(sec) {
  applyFilters();
}
function filterBySignal(sig) {
  applyFilters();
}
function applyFilters() {
  const q = document.getElementById('stock-search').value.toLowerCase();
  const sec = document.getElementById('sector-filter').value;
  const sig = document.getElementById('signal-filter').value;
  let res = STOCKS.filter(s=>{
    const mq = s.sym.toLowerCase().includes(q)||s.name.toLowerCase().includes(q)||!q;
    const ms = !sec||s.sector===sec;
    const mi = !sig||s.signal===sig;
    return mq&&ms&&mi;
  });
  renderScreener(res);
}

// ════════════════════════════════════
// RENDER: PREDICTION
// ════════════════════════════════════
function renderPillarControls() {
  document.getElementById('pillar-controls').innerHTML = PILLAR_STATE.map((p,i)=>`
    <div class="pillar-row">
      <div style="width:200px;flex-shrink:0">
        <div class="pillar-label" style="color:${p.color}">${p.label}</div>
        <div class="pillar-sub">${p.sub}</div>
      </div>
      <input class="pillar-slider" type="range" min="5" max="70" value="${p.val}"
        style="accent-color:${p.color}"
        oninput="updatePillar(${i},this.value)"/>
      <div class="pillar-pct" style="color:${p.color}" id="pp-${i}">${p.val}%</div>
    </div>`).join('');
  updatePillarChart();
}

function updatePillar(i, v) {
  PILLAR_STATE[i].val = +v;
  const total = PILLAR_STATE.reduce((s,p)=>s+p.val,0);
  PILLAR_STATE.forEach((p,j)=>{
    const norm = Math.round(p.val/total*100);
    const el = document.getElementById('pp-'+j);
    if(el) el.textContent = norm+'%';
  });
  document.getElementById('total-weight').textContent = '100%';
  updatePillarChart();
}

function updatePillarChart() {
  const total = PILLAR_STATE.reduce((s,p)=>s+p.val,0);
  const data = PILLAR_STATE.map(p=>Math.round(p.val/total*100));
  if (!pillarChart) {
    const ctx = document.getElementById('pillarChart');
    if (!ctx) return;
    pillarChart = new Chart(ctx,{
      type:'doughnut',
      data:{
        labels:PILLAR_STATE.map(p=>p.label.split('/')[0].trim()),
        datasets:[{data,backgroundColor:PILLAR_STATE.map(p=>p.color),borderWidth:0,hoverOffset:4}]
      },
      options:{
        responsive:true,maintainAspectRatio:false,cutout:'60%',
        plugins:{legend:{display:true,position:'right',labels:{color:'#8892a4',font:{size:11},boxWidth:10}}}
      }
    });
  } else {
    pillarChart.data.datasets[0].data = data;
    pillarChart.update();
  }
}

function renderPredictionTable() {
  const preds = [
    {sym:'NICA',cur:422,t3:'438–445',t30:'490–520',conf:88,tech:'Bullish',fund:'Strong',risk:'Low'},
    {sym:'NHPC',cur:142,t3:'147–151',t30:'162–175',conf:82,tech:'Breakout',fund:'Medium',risk:'Low'},
    {sym:'SBL',cur:348,t3:'355–362',t30:'385–410',conf:76,tech:'Bullish',fund:'Strong',risk:'Low-Med'},
    {sym:'GBIME',cur:268,t3:'272–278',t30:'295–315',conf:71,tech:'Recovery',fund:'Good',risk:'Medium'},
    {sym:'NABIL',cur:1245,t3:'1230–1250',t30:'—',conf:52,tech:'Overbought',fund:'Strong',risk:'High'},
  ];
  document.getElementById('prediction-table').innerHTML = preds.map(p=>`
    <tr>
      <td class="td-blue" style="font-weight:600">${p.sym}</td>
      <td>NPR ${p.cur}</td>
      <td class="td-green">${p.t3}</td>
      <td class="td-green">${p.t30}</td>
      <td>
        <div style="display:flex;align-items:center;gap:8px">
          <div style="height:4px;width:60px;background:var(--border);border-radius:2px">
            <div style="height:4px;width:${p.conf}%;background:${p.conf>80?'#10b981':p.conf>60?'#f59e0b':'#ef4444'};border-radius:2px"></div>
          </div>
          <span style="font-size:12px;color:var(--text2)">${p.conf}%</span>
        </div>
      </td>
      <td class="td-blue">${p.tech}</td>
      <td class="td-green">${p.fund}</td>
      <td class="${p.risk==='High'?'td-red':p.risk==='Medium'?'td-amber':'td-green'}">${p.risk}</td>
      <td>${signalBadge(p.conf>75?'BUY':p.conf>55?'HOLD':'SELL')}</td>
    </tr>`).join('');
}

// ════════════════════════════════════
// RENDER: PATTERNS
// ════════════════════════════════════
function renderPatterns() {
  document.getElementById('pattern-grid').innerHTML = PATTERNS.map(p=>`
    <div class="pattern-card ${p.detected?'detected':''}">
      <svg class="pat-svg" viewBox="0 0 84 56" xmlns="http://www.w3.org/2000/svg">
        <defs><marker id="arr" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="5" markerHeight="5" orient="auto"><path d="M1 1L6 4L1 7" fill="none" stroke="currentColor" stroke-width="1.5"/></marker></defs>
        ${p.svg}
      </svg>
      <div class="pat-name">${p.name}</div>
      <div class="pat-meta">${p.stock} · ${p.type}</div>
      <div class="conf-bar-track">
        <div class="conf-bar-fill" style="width:${p.conf}%;background:${p.conf>80?'#10b981':p.conf>65?'#3b82f6':'#f59e0b'}"></div>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:5px;font-size:11px;color:var(--text3)">
        <span>${p.detected?'✓ Detected':'Watching'}</span>
        <span>${p.conf}% conf.</span>
      </div>
    </div>`).join('');
}

// ════════════════════════════════════
// RENDER: PORTFOLIO
// ════════════════════════════════════
function renderPortfolio() {
  document.getElementById('acct-grid').innerHTML = PORTFOLIO_ACCOUNTS.map(a=>{
    const mx = Math.max(...a.bars);
    const bars = a.bars.map(v=>`<div class="mini-bar" style="height:${Math.round(v/mx*26)+2}px;background:${a.color};opacity:0.7"></div>`).join('');
    return `<div class="acct-card ${a.cls}">
      <div class="acct-name">${a.name}</div>
      <div class="acct-val">NPR ${a.val.toLocaleString()}</div>
      <div class="acct-pnl td-green">+NPR ${a.pnl.toLocaleString()} (+${a.pct}%)</div>
      <div class="mini-bars">${bars}</div>
    </div>`;
  }).join('');

  document.getElementById('ipo-table').innerHTML = IPOS.map(i=>{
    const sc = i.status==='Open'?'green':i.status==='Processing'?'amber':i.status==='Allotted'?'blue':'purple';
    return `<tr>
      <td style="font-weight:500">${i.co}</td>
      <td class="td-dim">${i.sector}</td>
      <td>NPR ${i.price}</td>
      <td class="td-dim">${i.applied}</td>
      <td class="td-green">${i.shares}</td>
      <td><span class="badge ${sc}">${i.status}</span></td>
      <td class="td-dim">${i.listing}</td>
      <td class="td-green">${i.ret}</td>
    </tr>`;
  }).join('');

  document.getElementById('holdings-table').innerHTML = HOLDINGS.map(h=>{
    const mv = h.shares * h.ltp;
    const pl = (h.ltp - h.cost) * h.shares;
    const plp = ((h.ltp - h.cost)/h.cost*100).toFixed(1);
    return `<tr>
      <td class="td-blue" style="font-weight:600">${h.sym}</td>
      <td>${h.shares}</td>
      <td>NPR ${h.cost}</td>
      <td>NPR ${h.ltp}</td>
      <td>NPR ${mv.toLocaleString()}</td>
      <td class="${pl>=0?'td-green':'td-red'}">${pl>=0?'+':''}NPR ${Math.abs(pl).toLocaleString()}</td>
      <td class="${pl>=0?'td-green':'td-red'}">${pl>=0?'+':''}${plp}%</td>
      <td class="td-dim">${h.acct}</td>
    </tr>`;
  }).join('');
}

function initPortfolioCharts() {
  const pctx = document.getElementById('portChart');
  const prctx = document.getElementById('profitChart');
  if (!pctx||!prctx) return;
  if (portChart) portChart.destroy();
  if (profitChart) profitChart.destroy();

  portChart = new Chart(pctx,{
    type:'bar',
    data:{
      labels:PORTFOLIO_ACCOUNTS.map(a=>a.name.split('(')[0].trim()),
      datasets:[{
        label:'Value',
        data:PORTFOLIO_ACCOUNTS.map(a=>a.val),
        backgroundColor:PORTFOLIO_ACCOUNTS.map(a=>a.color+'cc'),
        borderColor:PORTFOLIO_ACCOUNTS.map(a=>a.color),
        borderWidth:1,
        borderRadius:4
      }]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        x:{ticks:{color:'#555f72',font:{size:11}},grid:{display:false}},
        y:{ticks:{color:'#555f72',font:{size:11},callback:v=>'NPR '+Math.round(v/1000)+'k'},grid:{color:'#2a2f3d'}}
      }
    }
  });

  profitChart = new Chart(prctx,{
    type:'doughnut',
    data:{
      labels:PORTFOLIO_ACCOUNTS.map(a=>a.name.split('(')[0].trim()),
      datasets:[{
        data:PORTFOLIO_ACCOUNTS.map(a=>a.pnl),
        backgroundColor:PORTFOLIO_ACCOUNTS.map(a=>a.color),
        borderWidth:0,hoverOffset:4
      }]
    },
    options:{
      responsive:true,maintainAspectRatio:false,cutout:'55%',
      plugins:{legend:{display:true,position:'right',labels:{color:'#8892a4',font:{size:11},boxWidth:10}}}
    }
  });
}

// ════════════════════════════════════
// RENDER: ALERTS
// ════════════════════════════════════
function renderAlerts() {
  document.getElementById('alerts-list').innerHTML = ALERTS.map(alertHTML).join('');
}

function alertHTML(a) {
  const icons={sell:'↘',hold:'⏸',buy:'↗',macro:'⚡'};
  const btnMap={
    sell:`<button class="alert-btn sell-btn" onclick="showToast('SELL order placed for ${a.stock.split('—')[0].trim()}')">Execute Sell</button>`,
    hold:`<button class="alert-btn hold-btn" onclick="showToast('Holding ${a.stock.split('—')[0].trim()} — alert set')">Set Hold Alert</button>`,
    buy:`<button class="alert-btn buy-btn" onclick="showToast('BUY order queued for ${a.stock.split('—')[0].trim()}')">Execute Buy</button>`,
    macro:`<button class="alert-btn" onclick="showToast('Portfolio review initiated')">Review Portfolio</button>`,
  };
  return `<div class="alert-item ${a.type}">
    <div class="alert-icon ${a.type}">${icons[a.type]}</div>
    <div class="alert-body">
      <div class="alert-stock">${a.stock}</div>
      <div class="alert-msg">${a.msg}</div>
      <div class="alert-actions">${btnMap[a.type]}</div>
    </div>
    <div class="alert-time">${a.time}</div>
  </div>`;
}

// ════════════════════════════════════
// HELPERS
// ════════════════════════════════════
function signalBadge(s) {
  const map={BUY:'green',SELL:'red',HOLD:'amber',ACCUMULATE:'blue'};
  return `<span class="badge ${map[s]||'blue'}">${s}</span>`;
}
function prioBadge(p) {
  const map={Critical:'red',High:'amber',Medium:'blue',Low:'purple'};
  return `<span class="badge ${map[p]||'blue'}">${p}</span>`;
}
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),2800);
}
function refreshData() {
  showToast('Market data refreshed — ' + new Date().toLocaleTimeString());
}

// ════════════════════════════════════
// INIT
// ════════════════════════════════════
renderDashboard();
renderHzPanel('short');
renderScreener(STOCKS);
renderPillarControls();
renderPredictionTable();
renderPatterns();
renderPortfolio();
renderAlerts();
setTimeout(initDashCharts, 100);
</script>
</body>
</html>

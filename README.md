# 📈 NEPSE Market Tracker

> Automated daily stock analysis for Nepal Stock Exchange — zero cost, zero API limits, 100% yours.

---

## What this does

| Step | What happens |
|------|-------------|
| **Scrape** | GitHub Action runs every weekday at 3:45 PM NPT (market close) |
| **Analyze** | A rule-based engine scores every stock 0–100 using EPS, P/E, Dividend, ROE, P/BV, and Volume |
| **Save** | Results written to `data/data.json` and `data/data.csv`, committed back to this repo |
| **Display** | Streamlit dashboard reads the JSON and shows interactive tables + charts |

---

## Health Score Formula

```python
def calculate_health_score(record):
    score = 0

    # EPS quality (0-20 pts)
    if eps > 50:  score += 20
    elif eps > 30: score += 15
    elif eps > 15: score += 10
    elif eps > 0:  score += 5

    # P/E valuation (0-20 pts)
    if 0 < pe < 10:  score += 20
    elif pe < 15:    score += 15
    elif pe < 20:    score += 10
    elif pe < 30:    score += 5

    # Dividend yield (0-20 pts)
    if div > 10:  score += 20
    elif div > 7: score += 15
    elif div > 5: score += 10
    elif div > 2: score += 5

    # ROE (0-20 pts)
    if roe > 25:  score += 20
    elif roe > 18: score += 15
    elif roe > 12: score += 10
    elif roe > 5:  score += 5

    # P/BV (0-10 pts)
    if 0 < pbv < 1:   score += 10
    elif pbv < 1.5:   score += 7
    elif pbv < 2.5:   score += 4

    # Momentum (0-10 pts)
    if volume > 50000 and change_pct > 0: score += 10
    elif volume > 10000 and change_pct >= 0: score += 5
    elif change_pct < -3: score += 0
    else: score += 3

    return score  # max 100
```

Grades: **A+** (≥80) · **A** (≥65) · **B** (≥50) · **C** (≥35) · **D** (<35)

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/Market-Tracker.git
cd Market-Tracker
pip install -r requirements.txt
```

### 2. Run the scraper once

```bash
python scraper.py
# → creates data/data.json and data/data.csv
```

### 3. Launch the dashboard locally

```bash
streamlit run dashboard.py
# → opens http://localhost:8501
```

---

## GitHub Actions Automation

The workflow at `.github/workflows/main.yml`:
- Runs **Monday–Friday at 10:15 UTC (3:45 PM NPT)**
- Installs dependencies, runs `scraper.py`, and pushes updated data files
- Can also be triggered manually from the **Actions** tab → **Run workflow**

---

## Deploying to Streamlit Cloud (Free)

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Connect your GitHub repo
3. Set **Main file** to `dashboard.py`
4. Under **Secrets**, add:
   ```toml
   DASHBOARD_PASSWORD = "your_secret_password"
   ```
5. Deploy → you get a public URL, password-protected

---

## Repository Setup (GitHub Secrets)

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|--------|-------|
| `DASHBOARD_USER` | `susal` |
| `DASHBOARD_PASSWORD` | `suyog` |

---

## Data Sources

| Source | Data |
|--------|------|
| NepseAlpha | Live price, volume, change % |
| ShareSansar | OHLCV, live market table |
| Merolagani | EPS, P/E, Book Value fundamentals |

All are public sites — no API keys required.

---

## Files

```
Market-Tracker/
├── scraper.py              # Data collection + health score engine
├── dashboard.py            # Streamlit dashboard
├── requirements.txt        # Python dependencies
├── .github/
│   └── workflows/
│       └── main.yml        # GitHub Actions automation
├── .streamlit/
│   └── config.toml         # Dark theme config
└── data/
    ├── data.json           # Auto-updated daily
    └── data.csv            # Same data in CSV format
```

---

## Upgrading the Scoring Model

Edit the `calculate_health_score()` function in `scraper.py`. Ideas:
- Add **52-week high/low** proximity scoring
- Weight sectors differently (banking vs hydropower)
- Add a **trend score** by comparing today's score to last week's

> The logic is yours. Run it as many times as you want. No token limits, no AI hallucinations.

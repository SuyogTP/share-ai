"""
NEPSE Market Tracker - Data Scraper
Fetches stock data from NepseAlpha, ShareSansar, and Merolagani
and saves structured JSON for the dashboard.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import time
import logging
from datetime import datetime, date
from pathlib import Path
import random

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

# ─── Constants ───────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_JSON = DATA_DIR / "data.json"
OUTPUT_CSV = DATA_DIR / "data.csv"


# ─── Health Score Engine ──────────────────────────────────────────────────────
def calculate_health_score(record: dict) -> dict:
    """
    Multi-factor scoring model. Returns score (0-100) + individual sub-scores.
    """
    eps = record.get("eps", 0) or 0
    pe = record.get("pe_ratio", 999) or 999
    div = record.get("dividend_yield", 0) or 0
    roe = record.get("roe", 0) or 0
    pbv = record.get("pbv", 999) or 999
    volume = record.get("volume", 0) or 0
    change_pct = record.get("change_pct", 0) or 0

    score = 0
    breakdown = {}

    # EPS quality (0–20 pts)
    if eps > 50:
        pts = 20
    elif eps > 30:
        pts = 15
    elif eps > 15:
        pts = 10
    elif eps > 0:
        pts = 5
    else:
        pts = 0
    score += pts
    breakdown["eps_score"] = pts

    # P/E valuation (0–20 pts)
    if 0 < pe < 10:
        pts = 20
    elif pe < 15:
        pts = 15
    elif pe < 20:
        pts = 10
    elif pe < 30:
        pts = 5
    else:
        pts = 0
    score += pts
    breakdown["pe_score"] = pts

    # Dividend yield (0–20 pts)
    if div > 10:
        pts = 20
    elif div > 7:
        pts = 15
    elif div > 5:
        pts = 10
    elif div > 2:
        pts = 5
    else:
        pts = 0
    score += pts
    breakdown["div_score"] = pts

    # ROE (0–20 pts)
    if roe > 25:
        pts = 20
    elif roe > 18:
        pts = 15
    elif roe > 12:
        pts = 10
    elif roe > 5:
        pts = 5
    else:
        pts = 0
    score += pts
    breakdown["roe_score"] = pts

    # P/BV (0–10 pts)
    if 0 < pbv < 1:
        pts = 10
    elif pbv < 1.5:
        pts = 7
    elif pbv < 2.5:
        pts = 4
    else:
        pts = 0
    score += pts
    breakdown["pbv_score"] = pts

    # Momentum – volume & price change (0–10 pts)
    if volume > 50000 and change_pct > 0:
        pts = 10
    elif volume > 10000 and change_pct >= 0:
        pts = 5
    elif change_pct < -3:
        pts = 0
    else:
        pts = 3
    score += pts
    breakdown["momentum_score"] = pts

    # Grade
    if score >= 80:
        grade = "A+"
    elif score >= 65:
        grade = "A"
    elif score >= 50:
        grade = "B"
    elif score >= 35:
        grade = "C"
    else:
        grade = "D"

    return {"health_score": score, "grade": grade, **breakdown}


# ─── Source 1: NepseAlpha ────────────────────────────────────────────────────
def scrape_nepsealpha() -> list[dict]:
    """
    Scrape fundamental data from NepseAlpha's company listing.
    URL: https://nepsealpha.com/trading/1/history (public page)
    Falls back to their JSON API endpoint if table parsing fails.
    """
    log.info("Scraping NepseAlpha …")
    results = []

    try:
        # Try API endpoint first (faster and more reliable)
        api_url = "https://nepsealpha.com/nepse-data"
        params = {"page": 1, "per_page": 50}
        resp = requests.get(api_url, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table tbody tr")

        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) < 5:
                continue
            try:
                results.append(
                    {
                        "symbol": cols[0],
                        "name": cols[1],
                        "ltp": _to_float(cols[2]),
                        "change_pct": _to_float(cols[3].replace("%", "")),
                        "volume": _to_int(cols[4]),
                        "source": "NepseAlpha",
                    }
                )
            except Exception:
                continue

    except Exception as e:
        log.warning(f"NepseAlpha scrape failed: {e}")

    log.info(f"  -> {len(results)} records from NepseAlpha")
    return results


# ─── Source 2: ShareSansar ───────────────────────────────────────────────────
def scrape_sharesansar() -> list[dict]:
    """
    Scrape live market data from ShareSansar's market table.
    """
    log.info("Scraping ShareSansar …")
    results = []

    try:
        url = "https://www.sharesansar.com/live-trading"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        table = soup.find("table", {"id": "headFixed"})
        if not table:
            table = soup.find("table")

        if table:
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) < 8:
                    continue
                try:
                    results.append(
                        {
                            "symbol": cols[1],
                            "ltp": _to_float(cols[2]),
                            "change_pct": _to_float(cols[4].replace("%", "")),
                            "open": _to_float(cols[5]),
                            "high": _to_float(cols[6]),
                            "low": _to_float(cols[7]),
                            "volume": _to_int(cols[8]) if len(cols) > 8 else 0,
                            "source": "ShareSansar",
                        }
                    )
                except Exception:
                    continue

    except Exception as e:
        log.warning(f"ShareSansar scrape failed: {e}")

    log.info(f"  -> {len(results)} records from ShareSansar")
    return results


# ─── Source 3: Merolagani ────────────────────────────────────────────────────
def scrape_merolagani() -> list[dict]:
    """
    Scrape fundamental data (EPS, P/E, Book Value) from Merolagani.
    """
    log.info("Scraping Merolagani …")
    results = []

    try:
        url = "https://merolagani.com/StockQuote.aspx"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Merolagani embeds data in a table with class 'table'
        table = soup.find("table", class_="table")
        if table:
            rows = table.find_all("tr")[1:]  # skip header
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cols) < 6:
                    continue
                try:
                    results.append(
                        {
                            "symbol": cols[0],
                            "ltp": _to_float(cols[1]),
                            "eps": _to_float(cols[3]),
                            "pe_ratio": _to_float(cols[4]),
                            "book_value": _to_float(cols[5]),
                            "source": "Merolagani",
                        }
                    )
                except Exception:
                    continue

    except Exception as e:
        log.warning(f"Merolagani scrape failed: {e}")

    log.info(f"  -> {len(results)} records from Merolagani")
    return results


# ─── Merge & Enrich ──────────────────────────────────────────────────────────
def merge_sources(
    nepsealpha: list, sharesansar: list, merolagani: list
) -> list[dict]:
    """Merge three source lists by symbol into unified records."""
    master: dict[str, dict] = {}

    def upsert(records: list):
        for r in records:
            sym = r.get("symbol", "").upper().strip()
            if not sym:
                continue
            if sym not in master:
                master[sym] = {"symbol": sym}
            master[sym].update({k: v for k, v in r.items() if v is not None})

    upsert(nepsealpha)
    upsert(sharesansar)
    upsert(merolagani)

    # Compute derived fields
    enriched = []
    for sym, rec in master.items():
        ltp = rec.get("ltp", 0) or 0
        book = rec.get("book_value", 0) or 0
        eps = rec.get("eps", 0) or 0

        # P/BV
        rec["pbv"] = round(ltp / book, 2) if book > 0 else None
        # Dividend yield (placeholder – real dividend scraped separately)
        rec["dividend_yield"] = rec.get("dividend_yield", 0)
        # ROE from EPS / Book Value * 100
        rec["roe"] = round((eps / book) * 100, 2) if book > 0 and eps > 0 else None

        # Health score
        scores = calculate_health_score(rec)
        rec.update(scores)

        rec["last_updated"] = datetime.utcnow().isoformat() + "Z"
        enriched.append(rec)

    # Sort by health score desc
    enriched.sort(key=lambda x: x.get("health_score", 0), reverse=True)
    return enriched


# ─── Demo / Fallback Data ────────────────────────────────────────────────────
def generate_demo_data() -> list[dict]:
    """
    Returns realistic demo records when live scraping is blocked
    (e.g., in GitHub Actions with IP restrictions).
    These are based on publicly known NEPSE data as of mid-2025.
    """
    base_stocks = [
        {"symbol": "NABIL", "name": "Nabil Bank", "sector": "Banking",         "ltp": 1020, "eps": 82.5,  "pe_ratio": 12.4, "book_value": 520, "dividend_yield": 12, "volume": 48000, "change_pct": 1.2},
        {"symbol": "NTC",   "name": "Nepal Telecom","sector": "Telecom",        "ltp": 740,  "eps": 48.6,  "pe_ratio": 15.2, "book_value": 390, "dividend_yield": 9,  "volume": 32000, "change_pct": 0.4},
        {"symbol": "SHIVM", "name": "Shiva Bikash Bank","sector": "Development","ltp": 188,  "eps": 12.1,  "pe_ratio": 15.5, "book_value": 110, "dividend_yield": 6,  "volume": 11000, "change_pct": -0.8},
        {"symbol": "GBIME", "name": "Global IME Bank","sector": "Banking",      "ltp": 262,  "eps": 22.4,  "pe_ratio": 11.7, "book_value": 165, "dividend_yield": 7.5,"volume": 95000, "change_pct": 2.1},
        {"symbol": "HIDCL", "name": "HIDCL",          "sector": "Hydropower",   "ltp": 192,  "eps": 9.8,   "pe_ratio": 19.6, "book_value": 140, "dividend_yield": 4,  "volume": 27000, "change_pct": -1.1},
        {"symbol": "NICA",  "name": "NIC Asia Bank",  "sector": "Banking",      "ltp": 395,  "eps": 35.2,  "pe_ratio": 11.2, "book_value": 220, "dividend_yield": 10, "volume": 62000, "change_pct": 0.9},
        {"symbol": "UPPER", "name": "Upper Tamakoshi", "sector": "Hydropower",  "ltp": 258,  "eps": 16.5,  "pe_ratio": 15.6, "book_value": 148, "dividend_yield": 5,  "volume": 38000, "change_pct": 1.5},
        {"symbol": "ADBL",  "name": "Agriculture Dev Bank","sector": "Banking",  "ltp": 305,  "eps": 28.3,  "pe_ratio": 10.8, "book_value": 195, "dividend_yield": 8.5,"volume": 41000, "change_pct": 0.2},
        {"symbol": "SANIMA","name": "Sanima Bank",    "sector": "Banking",      "ltp": 331,  "eps": 30.1,  "pe_ratio": 11.0, "book_value": 210, "dividend_yield": 9,  "volume": 34000, "change_pct": -0.3},
        {"symbol": "SHINE", "name": "Shine Resunga", "sector": "Development",   "ltp": 172,  "eps": 10.5,  "pe_ratio": 16.4, "book_value": 105, "dividend_yield": 5,  "volume": 8000,  "change_pct": -2.0},
        {"symbol": "NLICL", "name": "Nepal Life Insurance","sector": "Insurance","ltp": 1280, "eps": 95.0,  "pe_ratio": 13.5, "book_value": 620, "dividend_yield": 14, "volume": 15000, "change_pct": 0.7},
        {"symbol": "EBL",   "name": "Everest Bank",   "sector": "Banking",      "ltp": 910,  "eps": 74.2,  "pe_ratio": 12.3, "book_value": 480, "dividend_yield": 11, "volume": 22000, "change_pct": 1.0},
        {"symbol": "CHCL",  "name": "Chilime Hydro",  "sector": "Hydropower",   "ltp": 495,  "eps": 29.8,  "pe_ratio": 16.6, "book_value": 230, "dividend_yield": 7,  "volume": 18000, "change_pct": 0.5},
        {"symbol": "PRVU",  "name": "Prabhu Bank",    "sector": "Banking",      "ltp": 218,  "eps": 17.6,  "pe_ratio": 12.4, "book_value": 128, "dividend_yield": 6,  "volume": 43000, "change_pct": 1.8},
        {"symbol": "MERO",  "name": "Mero Microfinance","sector": "Microfinance","ltp": 3100, "eps": 205.0, "pe_ratio": 15.1, "book_value": 900, "dividend_yield": 18, "volume": 4200,  "change_pct": 0.3},
    ]

    enriched = []
    for s in base_stocks:
        book = s["book_value"]
        eps = s["eps"]
        ltp = s["ltp"]
        s["pbv"] = round(ltp / book, 2)
        s["roe"] = round((eps / book) * 100, 2)
        s["open"] = round(ltp * (1 - s["change_pct"] / 100), 1)
        s["high"] = round(ltp * 1.015, 1)
        s["low"] = round(ltp * 0.985, 1)
        s["source"] = "Demo (Live scrape unavailable)"
        scores = calculate_health_score(s)
        s.update(scores)
        s["last_updated"] = datetime.utcnow().isoformat() + "Z"
        enriched.append(s)

    enriched.sort(key=lambda x: x.get("health_score", 0), reverse=True)
    return enriched


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _to_float(val) -> float | None:
    try:
        return float(str(val).replace(",", "").strip())
    except Exception:
        return None


def _to_int(val) -> int | None:
    try:
        return int(str(val).replace(",", "").strip())
    except Exception:
        return None


# ─── Save ────────────────────────────────────────────────────────────────────
def save_data(records: list[dict]):
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generated_date": date.today().isoformat(),
        "total_stocks": len(records),
        "stocks": records,
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    log.info(f"Saved JSON -> {OUTPUT_JSON}")

    if records:
        keys = records[0].keys()
        with open(OUTPUT_CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(records)
        log.info(f"Saved CSV  -> {OUTPUT_CSV}")


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 50)
    log.info("NEPSE Tracker – Scrape Run")
    log.info("=" * 50)

    na = scrape_nepsealpha()
    time.sleep(2)
    ss = scrape_sharesansar()
    time.sleep(2)
    ml = scrape_merolagani()

    if na or ss or ml:
        merged = merge_sources(na, ss, ml)
        log.info(f"Merged -> {len(merged)} unique stocks")
    else:
        log.warning("All live scrapes failed – using demo data")
        merged = generate_demo_data()

    save_data(merged)
    log.info("Done ✓")


if __name__ == "__main__":
    main()

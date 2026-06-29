from __future__ import annotations

import json
import re
from datetime import datetime, date
from pathlib import Path
from typing import Any

import pandas as pd

from interpreter import interpret_stock
from scraper import (
    generate_demo_data,
    merge_sources,
    scrape_merolagani,
    scrape_sharesansar,
    scrape_nepsealpha,
)
from trend_signals import analyze_trend

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SNAPSHOT_JSON = DATA_DIR / "data.json"
SNAPSHOT_CSV = DATA_DIR / "data.csv"


def _to_numeric(series: object, default: float = 0.0) -> pd.Series:
    if isinstance(series, pd.Series):
        return pd.to_numeric(series, errors="coerce").fillna(default)
    return pd.Series([series], dtype="float64").fillna(default)


def _looks_like_real_symbol(value: object) -> bool:
    if value is None:
        return False
    symbol = str(value).strip().upper()
    if not symbol or len(symbol) < 2 or len(symbol) > 10:
        return False
    return bool(re.fullmatch(r"[A-Z0-9.-]+", symbol)) and not symbol.isdigit()


def _sanitize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for record in records or []:
        symbol = record.get("symbol") or record.get("sym") or ""
        if not _looks_like_real_symbol(symbol):
            continue
        ltp = float(record.get("ltp", record.get("price", 0)) or 0)
        if ltp <= 0:
            continue
        cleaned = dict(record)
        cleaned["symbol"] = str(symbol).strip().upper()
        cleaned["name"] = cleaned.get("name") or cleaned.get("company_name") or cleaned["symbol"]
        sanitized.append(cleaned)
    return sanitized


def _to_string(series: object, default: str = "") -> pd.Series:
    if isinstance(series, pd.Series):
        return series.fillna(default).astype(str)
    return pd.Series([str(series if series is not None else default)])


def _build_price_history(record: dict[str, Any]) -> pd.DataFrame:
    base_price = float(record.get("ltp", 0) or 0)
    change_pct = float(record.get("change_pct", 0) or 0)
    if base_price <= 0:
        base_price = 100.0

    dates = pd.date_range(end=datetime.today(), periods=28, freq="D")
    prices = []
    current_price = base_price
    for idx in range(len(dates)):
        drift = ((idx % 7) - 3) * 0.003 * base_price
        daily_change = (change_pct / 100.0) / 12.0 + drift / base_price
        current_price = current_price * (1 + daily_change)
        prices.append(current_price)

    return pd.DataFrame({"date": dates, "close": prices})


def _classify_signal(row: dict[str, Any]) -> str:
    score = float(row.get("health_score", 50) or 50)
    change_pct = float(row.get("change_pct", 0) or 0)
    trend_signal = (row.get("trend_result") or {}).get("signal") if isinstance(row.get("trend_result"), dict) else None

    if trend_signal == "bullish" and score >= 60 and change_pct >= 0:
        return "BUY"
    if trend_signal == "bearish" and (score < 45 or change_pct < -1.5):
        return "SELL"
    if score > 70 and change_pct > 1.0:
        return "BUY"
    if score < 35 and change_pct < -2.0:
        return "SELL"
    return "HOLD"


def enrich_market_records(records: list[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(records, pd.DataFrame):
        records = records.to_dict(orient="records")

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records).copy()
    if df.empty:
        return df

    df = df[df["symbol"].apply(lambda value: _looks_like_real_symbol(value)) | df["sym"].apply(lambda value: _looks_like_real_symbol(value))] if {"symbol", "sym"}.issubset(df.columns) else df
    if df.empty:
        return pd.DataFrame()

    df["symbol"] = _to_string(df.get("symbol", df.get("sym", ""))).str.upper().str.strip()
    df["name"] = _to_string(df.get("name", df.get("company_name", "")))
    df["ltp"] = _to_numeric(df.get("ltp", 0), 0.0)
    df = df[df["ltp"] > 0].copy()
    if df.empty:
        return pd.DataFrame()
    df["change_pct"] = _to_numeric(df.get("change_pct", 0), 0.0)
    df["volume"] = _to_numeric(df.get("volume", 0), 0.0).astype(int)
    df["eps"] = _to_numeric(df.get("eps", 0), 0.0)
    df["pe_ratio"] = _to_numeric(df.get("pe_ratio", df.get("pe", 15)), 15.0)
    df["book_value"] = _to_numeric(df.get("book_value", 0), 0.0)
    df["dividend_yield"] = _to_numeric(df.get("dividend_yield", df.get("div_yield", 0)), 0.0)
    df["health_score"] = _to_numeric(df.get("health_score", 50), 50.0)
    df["grade"] = _to_string(df.get("grade", "C"))
    df["roe"] = _to_numeric(df.get("roe", 10), 10.0)

    df["sym"] = df["symbol"]
    df["chg"] = df["change_pct"]
    df["vol"] = df["volume"]
    df["pe"] = df["pe_ratio"]
    df["rsi"] = (50 + (df["change_pct"].fillna(0) * 8).clip(-30, 30)).round(1)

    sector_mapping = {
        "NABIL": "Banking",
        "EBL": "Banking",
        "SBI": "Banking",
        "GBIME": "Banking",
        "ADBL": "Banking",
        "SANIMA": "Banking",
        "NICA": "Banking",
        "NHPC": "Hydropower",
        "UPPER": "Hydropower",
        "CHCL": "Hydropower",
        "NLICL": "Insurance",
        "PLIC": "Insurance",
        "MLBL": "Microfinance",
        "MERO": "Microfinance",
        "NTC": "Telecom",
        "HIDCL": "Manufacturing",
        "SHIVM": "Development",
        "SHINE": "Development",
    }
    df["sector"] = df["sym"].map(sector_mapping).fillna("Finance")

    trend_results = []
    interpretations = []
    for _, row in df.iterrows():
        history_df = _build_price_history(row)
        trend_result = analyze_trend(history_df)
        trend_results.append(trend_result)

        interpretation_result = interpret_stock(
            symbol=row.get("symbol", ""),
            score=float(row.get("health_score", 50) or 50),
            eps=float(row.get("eps", 0) or 0),
            pe=float(row.get("pe_ratio", 15) or 15),
            div_yield=float(row.get("dividend_yield", 0) or 0),
            trend_result=trend_result,
            company_name=row.get("name") or None,
        )
        interpretations.append(interpretation_result)

    df["trend_result"] = trend_results
    df["trend_signal"] = df["trend_result"].apply(lambda item: item.get("signal") if isinstance(item, dict) else None)
    df["trend_confidence"] = df["trend_result"].apply(lambda item: item.get("confidence") if isinstance(item, dict) else None)
    df["interpretation"] = [item for item in interpretations]
    df["interpretation_lean"] = [item["lean"] for item in interpretations]
    df["interpretation_headline"] = [item["headline"] for item in interpretations]
    df["interpretation_reason"] = [item["lean_reason"] for item in interpretations]
    df["signal"] = df.apply(_classify_signal, axis=1)
    df["last_updated"] = datetime.utcnow().isoformat() + "Z"
    df["source"] = df.get("source", "Demo")

    return df.reset_index(drop=True)


def fetch_live_records() -> list[dict[str, Any]]:
    try:
        merolagani_data = scrape_merolagani()
        sharesansar_data = scrape_sharesansar()
        nepsealpha_data = scrape_nepsealpha()
        if merolagani_data or sharesansar_data or nepsealpha_data:
            merged = merge_sources(nepsealpha_data, sharesansar_data, merolagani_data)
            sanitized = _sanitize_records(merged)
            if len(sanitized) >= 10:
                return sanitized
    except Exception:
        pass
    return generate_demo_data()


def save_market_snapshot(records: list[dict[str, Any]] | pd.DataFrame) -> None:
    df = enrich_market_records(records)
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generated_date": date.today().isoformat(),
        "total_stocks": len(df),
        "stocks": df.to_dict(orient="records"),
    }
    SNAPSHOT_JSON.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    if not df.empty:
        df.to_csv(SNAPSHOT_CSV, index=False)


def load_market_snapshot(force_refresh: bool = False) -> tuple[pd.DataFrame, str]:
    if not force_refresh and SNAPSHOT_JSON.exists():
        try:
            payload = json.loads(SNAPSHOT_JSON.read_text(encoding="utf-8"))
            stocks = payload.get("stocks", [])
            if stocks:
                return enrich_market_records(stocks), "cached"
        except Exception:
            pass

    records = fetch_live_records()
    save_market_snapshot(records)
    source = str(records[0].get("source", "") if records else "")
    source_label = "live" if "Demo" not in source else "demo"
    df = enrich_market_records(records)
    return df, source_label

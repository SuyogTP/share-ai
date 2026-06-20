"""
trend_signals.py
-----------------
Lightweight trend / momentum signal engine for share-ai.

IMPORTANT HONESTY NOTE (read this before wiring it in):
This module does NOT predict the future. No model can reliably predict
short-term stock price moves, especially on a small market like NSE with
thin historical data. What this module DOES do is detect well-known,
mechanical trend signals (moving average crossovers, momentum, volatility)
that traders commonly use as ONE input among many. Treat the output as
"what the recent price action looks like," not "what will happen next."

Expected input
--------------
A pandas DataFrame `price_df` with at least:
    - a date-like column (default name: "date"), sorted ascending
    - a closing price column (default name: "close")

If your data uses different column names (e.g. "LTP", "Date"), pass
date_col / price_col accordingly when calling the functions.

Drop this file next to your existing app code and:
    from trend_signals import analyze_trend

    result = analyze_trend(price_df)
    print(result["signal"])       # "bullish" / "bearish" / "neutral"
    print(result["details"])      # dict of the underlying numbers
"""

from __future__ import annotations
import pandas as pd
import numpy as np


def _sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average."""
    return series.rolling(window=window, min_periods=window).mean()


def _rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index (0-100).
    >70 is traditionally considered 'overbought', <30 'oversold'.
    These thresholds are conventions, not laws of physics -- treat them
    as soft signals, not triggers.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _momentum(series: pd.Series, window: int = 10) -> pd.Series:
    """Percent change over `window` periods. Positive = upward momentum."""
    return series.pct_change(periods=window) * 100


def _volatility(series: pd.Series, window: int = 20) -> pd.Series:
    """Rolling standard deviation of daily returns, annualized-ish (%)."""
    returns = series.pct_change()
    return returns.rolling(window=window, min_periods=window).std() * 100


def analyze_trend(
    price_df: pd.DataFrame,
    date_col: str = "date",
    price_col: str = "close",
    short_window: int = 5,
    long_window: int = 20,
) -> dict:
    """
    Analyze recent price action and return a structured trend read.

    Parameters
    ----------
    price_df : DataFrame with at least [date_col, price_col], ascending by date.
               Needs at least `long_window + 1` rows to produce a full signal;
               fewer rows will still return what it can, flagged accordingly.
    date_col, price_col : column names in your DataFrame.
    short_window, long_window : periods (in rows/days) for the moving averages.

    Returns
    -------
    dict with:
        "signal": "bullish" | "bearish" | "neutral" | "insufficient_data"
        "confidence": "low" | "medium" -- this is about signal AGREEMENT,
                       not about predictive accuracy. Never expose this as
                       a probability of price going up.
        "details": dict of raw numbers (sma_short, sma_long, rsi, momentum_pct,
                    volatility_pct) for transparency / debugging / display.
        "reasons": list of short plain-English strings explaining WHY,
                   e.g. "Short-term average is above long-term average
                   (uptrend)".
    """
    df = price_df.sort_values(date_col).reset_index(drop=True)
    prices = df[price_col].astype(float)

    if len(prices) < long_window + 1:
        return {
            "signal": "insufficient_data",
            "confidence": "low",
            "details": {},
            "reasons": [
                f"Need at least {long_window + 1} days of price history; "
                f"only {len(prices)} available."
            ],
        }

    sma_short = _sma(prices, short_window).iloc[-1]
    sma_long = _sma(prices, long_window).iloc[-1]
    rsi = _rsi(prices).iloc[-1]
    momentum_pct = _momentum(prices, window=short_window).iloc[-1]
    volatility_pct = _volatility(prices, window=long_window).iloc[-1]
    last_price = prices.iloc[-1]

    reasons = []
    bullish_votes = 0
    bearish_votes = 0

    # Signal 1: moving average crossover
    if pd.notna(sma_short) and pd.notna(sma_long):
        if sma_short > sma_long:
            bullish_votes += 1
            reasons.append(
                f"Short-term average (Rs {sma_short:,.1f}) is above the "
                f"long-term average (Rs {sma_long:,.1f}) — short-term uptrend."
            )
        elif sma_short < sma_long:
            bearish_votes += 1
            reasons.append(
                f"Short-term average (Rs {sma_short:,.1f}) is below the "
                f"long-term average (Rs {sma_long:,.1f}) — short-term downtrend."
            )

    # Signal 2: RSI
    if pd.notna(rsi):
        if rsi >= 70:
            bearish_votes += 1
            reasons.append(
                f"RSI is {rsi:.0f}, in 'overbought' territory — the recent "
                f"rally may be due for a pause."
            )
        elif rsi <= 30:
            bullish_votes += 1
            reasons.append(
                f"RSI is {rsi:.0f}, in 'oversold' territory — selling may "
                f"be overdone."
            )
        else:
            reasons.append(f"RSI is {rsi:.0f} — neither overbought nor oversold.")

    # Signal 3: momentum
    if pd.notna(momentum_pct):
        if momentum_pct > 1:
            bullish_votes += 1
            reasons.append(
                f"Price is up {momentum_pct:.1f}% over the last "
                f"{short_window} sessions — positive momentum."
            )
        elif momentum_pct < -1:
            bearish_votes += 1
            reasons.append(
                f"Price is down {momentum_pct:.1f}% over the last "
                f"{short_window} sessions — negative momentum."
            )

    # Decide overall signal
    if bullish_votes > bearish_votes:
        signal = "bullish"
    elif bearish_votes > bullish_votes:
        signal = "bearish"
    else:
        signal = "neutral"

    total_votes = bullish_votes + bearish_votes
    confidence = "medium" if total_votes >= 2 and abs(bullish_votes - bearish_votes) >= 2 else "low"

    return {
        "signal": signal,
        "confidence": confidence,
        "details": {
            "last_price": round(float(last_price), 2),
            "sma_short": None if pd.isna(sma_short) else round(float(sma_short), 2),
            "sma_long": None if pd.isna(sma_long) else round(float(sma_long), 2),
            "rsi": None if pd.isna(rsi) else round(float(rsi), 1),
            "momentum_pct": None if pd.isna(momentum_pct) else round(float(momentum_pct), 2),
            "volatility_pct": None if pd.isna(volatility_pct) else round(float(volatility_pct), 2),
        },
        "reasons": reasons,
    }

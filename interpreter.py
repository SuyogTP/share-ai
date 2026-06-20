"""
interpreter.py
--------------
Turns your existing fundamentals SCORE + (optional) trend_signals output
into a short, plain-English summary for someone who, in your words,
"doesn't know anything about shares."

This module makes NO buy/sell recommendation as financial advice -- it
translates numbers into plain language and a clearly-labeled "lean"
(Buy-side lean / Hold / Avoid-side lean), with the reasoning shown so the
user can judge for themselves. It always reminds the user this isn't
financial advice, because it genuinely isn't -- a fundamentals score and
a few trend signals can't account for news, management quality, sector
risk, macro shocks, etc.

Usage
-----
    from interpreter import interpret_stock

    summary = interpret_stock(
        symbol="RNLI",
        score=62,                 # your existing 0-100 health score
        eps=74.0,
        pe=15.5,
        div_yield=7.5,
        trend_result=trend_signals.analyze_trend(price_df),  # optional
    )

    print(summary["headline"])
    print(summary["explanation"])
    print(summary["lean"])
    print(summary["caveats"])
"""

from __future__ import annotations
from typing import Optional


def _score_band(score: float) -> tuple[str, str]:
    """Map a 0-100 score to a label + plain-English meaning."""
    if score >= 75:
        return "Strong", "the company's fundamentals look solid right now"
    elif score >= 60:
        return "Good", "the company's fundamentals look reasonably healthy"
    elif score >= 45:
        return "Average", "the company's fundamentals are mixed -- some good signs, some weak ones"
    elif score >= 30:
        return "Weak", "the company's fundamentals look shaky"
    else:
        return "Poor", "the company's fundamentals look concerning"


def _pe_comment(pe: Optional[float]) -> Optional[str]:
    if pe is None:
        return None
    if pe < 10:
        return f"Its P/E of {pe:.1f} is low, meaning the stock is cheap relative to earnings -- but check why (sometimes the market expects trouble ahead)."
    elif pe <= 20:
        return f"Its P/E of {pe:.1f} is in a fairly normal range for NSE stocks."
    else:
        return f"Its P/E of {pe:.1f} is on the higher side, meaning you're paying a premium relative to current earnings."


def _div_comment(div_yield: Optional[float]) -> Optional[str]:
    if div_yield is None:
        return None
    if div_yield >= 8:
        return f"The {div_yield:.1f}% dividend yield is quite high -- good for income, but very high yields can sometimes mean the price has dropped a lot, so it's worth checking why."
    elif div_yield >= 3:
        return f"The {div_yield:.1f}% dividend yield is decent, giving you some steady income while you hold."
    elif div_yield > 0:
        return f"The {div_yield:.1f}% dividend yield is modest -- this stock leans more toward growth than income."
    return None


def _eps_comment(eps: Optional[float]) -> Optional[str]:
    if eps is None:
        return None
    if eps <= 0:
        return "Earnings per share is negative or zero, meaning the company isn't currently profitable -- worth extra caution."
    return f"EPS of {eps:.1f} shows the company is currently profitable on a per-share basis."


def interpret_stock(
    symbol: str,
    score: float,
    eps: Optional[float] = None,
    pe: Optional[float] = None,
    div_yield: Optional[float] = None,
    trend_result: Optional[dict] = None,
    company_name: Optional[str] = None,
) -> dict:
    """
    Build a plain-English interpretation of a single stock.

    Parameters
    ----------
    symbol : ticker, e.g. "RNLI"
    score : your existing 0-100 health score
    eps, pe, div_yield : optional fundamentals (pass what you have)
    trend_result : optional output of trend_signals.analyze_trend(); if
                   omitted, the summary is fundamentals-only.
    company_name : optional full name for a friendlier headline.

    Returns
    -------
    dict with: "headline", "explanation" (list of strings), "lean",
    "lean_reason", "caveats" (list of strings).
    """
    label = symbol if not company_name else f"{company_name} ({symbol})"
    band, band_meaning = _score_band(score)

    explanation = [f"Health score: {score:.0f}/100 ({band}) — {band_meaning}."]

    for comment in (_eps_comment(eps), _pe_comment(pe), _div_comment(div_yield)):
        if comment:
            explanation.append(comment)

    # Combine fundamentals band with trend (if available) into a "lean"
    # This is intentionally a LEAN, not a directive -- worded to avoid
    # sounding like financial advice.
    fundamentals_positive = score >= 60
    fundamentals_negative = score < 45

    trend_signal = trend_result.get("signal") if trend_result else None

    if trend_result:
        explanation.append("Recent price action:")
        explanation.extend(f"  • {r}" for r in trend_result.get("reasons", []))

    # Decide lean
    if fundamentals_positive and trend_signal == "bullish":
        lean = "Leans toward: Buy-side"
        lean_reason = "Both the fundamentals and the recent price trend look favorable."
    elif fundamentals_negative and trend_signal == "bearish":
        lean = "Leans toward: Avoid / Caution"
        lean_reason = "Both the fundamentals and the recent price trend look weak."
    elif fundamentals_positive and trend_signal in ("bearish", None):
        lean = "Leans toward: Hold"
        lean_reason = (
            "Fundamentals look healthy, but recent price action is weak or unclear "
            "-- often a sign to wait rather than chase the price."
        )
    elif fundamentals_negative and trend_signal in ("bullish", None):
        lean = "Leans toward: Hold / Watch closely"
        lean_reason = (
            "Recent price action looks okay, but the underlying fundamentals are weak "
            "-- a bounce on weak fundamentals can fade."
        )
    else:
        lean = "Leans toward: Hold"
        lean_reason = "Signals are mixed -- nothing here strongly points one way or the other."

    if trend_signal in (None, "insufficient_data"):
        lean_reason += " (Note: this lean is based on fundamentals only -- no price trend data was available.)"

    headline = f"{label}: {band} fundamentals ({score:.0f}/100), {lean.replace('Leans toward: ', '').lower()}"

    caveats = [
        "This is an automated summary of numbers, not financial advice.",
        "It doesn't know about company news, management changes, sector trends, or macro events in Nepal.",
        "A 'lean' here is a starting point for your own research, not a recommendation to act.",
        "Past price patterns do not reliably predict future price moves.",
    ]

    return {
        "headline": headline,
        "explanation": explanation,
        "lean": lean,
        "lean_reason": lean_reason,
        "caveats": caveats,
    }


def interpret_portfolio(holdings: list[dict]) -> dict:
    """
    Roll up interpret_stock() results across a portfolio into a short
    overview -- useful for the "My Portfolio" page.

    Parameters
    ----------
    holdings : list of dicts, each with at minimum {"symbol", "score"},
               and optionally the same optional fields as interpret_stock,
               plus "trend_result".

    Returns
    -------
    dict with "overview" (string) and "per_stock" (list of interpret_stock results).
    """
    per_stock = []
    for h in holdings:
        result = interpret_stock(
            symbol=h["symbol"],
            score=h["score"],
            eps=h.get("eps"),
            pe=h.get("pe"),
            div_yield=h.get("div_yield"),
            trend_result=h.get("trend_result"),
            company_name=h.get("company_name"),
        )
        per_stock.append(result)

    avg_score = sum(h["score"] for h in holdings) / len(holdings) if holdings else 0
    buy_leaning = sum(1 for r in per_stock if "Buy" in r["lean"])
    avoid_leaning = sum(1 for r in per_stock if "Avoid" in r["lean"])
    hold_leaning = len(per_stock) - buy_leaning - avoid_leaning

    overview = (
        f"Across your {len(holdings)} holdings, the average health score is "
        f"{avg_score:.0f}/100. {buy_leaning} lean Buy-side, {hold_leaning} lean Hold, "
        f"and {avoid_leaning} lean toward caution/avoid. "
        f"Remember: this is a snapshot of current numbers, not a forecast."
    )

    return {"overview": overview, "per_stock": per_stock}

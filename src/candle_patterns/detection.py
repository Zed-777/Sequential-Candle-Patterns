from __future__ import annotations

import pandas as pd
from typing import List, Dict, Any


def candle_color(row: pd.Series) -> str:
    return "green" if row["close"] >= row["open"] else "red"


def is_doji(window: pd.DataFrame, tol: float = 0.1) -> bool:
    # small body relative to range
    row = window.iloc[-1]
    body = abs(row["close"] - row["open"])
    rng = row["high"] - row["low"]
    if rng == 0:
        return False
    return body <= tol * rng


def is_hammer(window: pd.DataFrame, tol: float = 0.1) -> bool:
    # small body near top, long lower wick
    row = window.iloc[-1]
    body = abs(row["close"] - row["open"])
    lower_wick = min(row["open"], row["close"]) - row["low"]
    upper_wick = row["high"] - max(row["open"], row["close"])
    if body == 0:
        return False
    return lower_wick >= 2 * body and upper_wick <= body


def is_bullish_engulfing(window: pd.DataFrame) -> bool:
    if len(window) < 2:
        return False
    prev = window.iloc[-2]
    cur = window.iloc[-1]
    return (prev["close"] < prev["open"] and cur["close"] > cur["open"] and cur["close"] > prev["open"] and cur["open"] < prev["close"])


def is_morning_star(window: pd.DataFrame) -> bool:
    if len(window) < 3:
        return False
    a, b, c = window.iloc[-3], window.iloc[-2], window.iloc[-1]
    return (a["close"] < a["open"] and is_doji(window.iloc[-2:-1]) and c["close"] > c["open"] and c["close"] > (a["open"] + a["close"]) / 2)


RULES = {
    "doji": is_doji,
    "hammer": is_hammer,
    "bullish_engulfing": is_bullish_engulfing,
    "morning_star": is_morning_star,
}


def detect_patterns(df: pd.DataFrame, window_size: int = 5) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for i in range(len(df)):
        # consider up to last window_size rows ending at i
        start = max(0, i - window_size + 1)
        window = df.iloc[start : i + 1]
        for name, fn in RULES.items():
            try:
                if fn(window):
                    results.append({"index": i, "timestamp": df.iloc[i]["timestamp"], "pattern": name})
            except Exception:
                # avoid noisy exceptions in detection
                continue
    return results

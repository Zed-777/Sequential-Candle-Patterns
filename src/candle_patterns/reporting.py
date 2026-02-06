from __future__ import annotations


from typing import List, Dict, Any

import pandas as pd

from .backtest import simple_pattern_backtest


def summarize_detections(
    df: pd.DataFrame, detections: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Aggregate detections by pattern and compute counts, support, and basic backtest metrics."""

    n = len(df)

    by_pattern: Dict[str, List[Dict[str, Any]]] = {}

    for d in detections:

        by_pattern.setdefault(d["pattern"], []).append(d)

    rows: List[Dict[str, Any]] = []

    for pattern, occ in by_pattern.items():

        count = len(occ)

        support = count / max(1, n)

        back = simple_pattern_backtest(df, occ, hold=1)

        rows.append(
            {
                "pattern": pattern,
                "count": count,
                "support": support,
                "avg_return": back.get("avg_return", 0.0),
                "win_rate": back.get("win_rate", 0.0),
            }
        )

    # sort by count desc

    rows.sort(key=lambda r: r["count"], reverse=True)

    return rows


def pattern_sparkline_series(df: pd.DataFrame, detections: List[Dict[str, Any]], horizon: int = 5) -> Dict[str, List[float]]:
    """Compute average return series per pattern for hold periods 1..horizon.

    Returns a dict: { pattern_name: [avg_return@1, avg_return@2, ..., avg_return@horizon] }
    """
    from .backtest import simple_pattern_backtest

    by_pattern: Dict[str, List[Dict[str, Any]]] = {}
    for d in detections:
        by_pattern.setdefault(d["pattern"], []).append(d)

    out: Dict[str, List[float]] = {}
    for pattern, occ in by_pattern.items():
        series: List[float] = []
        for h in range(1, horizon + 1):
            back = simple_pattern_backtest(df, occ, hold=h)
            series.append(float(back.get("avg_return", 0.0)))
        out[pattern] = series
    return out

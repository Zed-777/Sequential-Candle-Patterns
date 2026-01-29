from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Dict, Any


def simple_pattern_backtest(
    df: pd.DataFrame, detections: List[Dict[str, Any]], hold: int = 1
) -> Dict[str, float]:
    """Backtest a naive strategy: on detection at index i, buy at next open and hold `hold` periods.
    Returns simple metrics: returns_total, avg_return, win_rate
    """
    returns: List[float] = []
    for d in detections:
        i = d["index"]
        if i + 1 >= len(df):
            continue
        buy_price = df.iloc[i + 1]["open"]
        sell_index = min(len(df) - 1, i + 1 + hold)
        sell_price = df.iloc[sell_index]["close"]
        ret = (sell_price - buy_price) / buy_price
        returns.append(ret)
    if not returns:
        return {"count": 0, "returns_total": 0.0, "avg_return": 0.0, "win_rate": 0.0}
    arr = np.array(returns)
    return {
        "count": len(arr),
        "returns_total": float(arr.sum()),
        "avg_return": float(arr.mean()),
        "win_rate": float((arr > 0).mean()),
    }

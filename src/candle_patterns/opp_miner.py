from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Iterable, List, Tuple, Dict


def ordinal_encode(seq: Iterable[float]) -> Tuple[int, ...]:
    """Encode a sequence of numbers into ordinal ranks.

    Example: [3,1,2] -> (3,1,2) ranks -> (3,1,2) -> after ranking (3->3,1->1,2->2) returns (3,1,2)
    Implementation uses argsort twice to compute ranks (1-based).
    """
    arr = np.array(list(seq))
    # argsort twice to get ranks (starting at 1)
    ranks = arr.argsort().argsort() + 1
    return tuple(int(r) for r in ranks)


def sliding_windows(arr: np.ndarray, length: int, step: int = 1) -> Iterable[np.ndarray]:
    for i in range(0, len(arr) - length + 1, step):
        yield arr[i : i + length]


def extract_windows(df: pd.DataFrame, length: int) -> List[Tuple[Tuple[int, ...], int]]:
    """Extract ordinal-encoded windows of given length. Returns list of (pattern, index_end).
    index_end is the index of the window's last element (for mapping back to original series).
    """
    seq = df["close"].values
    results: List[Tuple[Tuple[int, ...], int]] = []
    for i in range(length - 1, len(seq)):
        window = seq[i - length + 1 : i + 1]
        pat = ordinal_encode(window)
        results.append((pat, i))
    return results


def opp_miner(df: pd.DataFrame, length: int, min_support: float = 0.01) -> Dict[Tuple[int, ...], int]:
    """Simple OPP miner: counts ordinal patterns of fixed length and returns those with support >= min_support.
    Returns dict pattern->count
    """
    windows = extract_windows(df, length)
    counts: Dict[Tuple[int, ...], int] = {}
    for pat, _ in windows:
        counts[pat] = counts.get(pat, 0) + 1
    total = len(windows)
    min_count = max(1, int(np.ceil(min_support * total)))
    return {p: c for p, c in counts.items() if c >= min_count}

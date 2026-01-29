from __future__ import annotations


import numpy as np

import pandas as pd

from typing import Iterable, List, Tuple, Dict


def ordinal_encode(seq: Iterable[float]) -> Tuple[int, ...]:

    arr = np.array(list(seq))

    ranks = arr.argsort().argsort() + 1

    return tuple(int(r) for r in ranks)


def extract_windows(df: pd.DataFrame, length: int) -> List[Tuple[Tuple[int, ...], int]]:

    seq = df["close"].values

    results: List[Tuple[Tuple[int, ...], int]] = []

    for i in range(length - 1, len(seq)):

        window = seq[i - length + 1 : i + 1]

        pat = ordinal_encode(window)

        results.append((pat, i))

    return results


def opp_miner(
    df: pd.DataFrame, length: int, min_support: float = 0.01
) -> Dict[Tuple[int, ...], int]:

    windows = extract_windows(df, length)

    counts: Dict[Tuple[int, ...], int] = {}

    for pat, _ in windows:

        counts[pat] = counts.get(pat, 0) + 1

    total = len(windows)

    min_count = max(1, int(np.ceil(min_support * total)))

    return {p: c for p, c in counts.items() if c >= min_count}


def opp_miner_variable_lengths(
    df: pd.DataFrame, min_len: int = 3, max_len: int = 6, min_support: float = 0.01
) -> Dict[int, Dict[Tuple[int, ...], int]]:
    """Run OPP mining across a range of lengths and return a dict mapping length -> pattern counts (filtered by min_support)."""

    results: Dict[int, Dict[Tuple[int, ...], int]] = {}

    for L in range(min_len, max_len + 1):

        res = opp_miner(df, L, min_support=min_support)

        if res:

            results[L] = res

    return results


def top_patterns_across_lengths(
    df: pd.DataFrame,
    min_len: int = 3,
    max_len: int = 6,
    min_support: float = 0.01,
    top_k: int = 10,
):
    """Return a sorted list of (length, pattern, count, support) across lengths, top_k overall."""

    results = opp_miner_variable_lengths(
        df, min_len=min_len, max_len=max_len, min_support=min_support
    )

    combined: List[Tuple[int, Tuple[int, ...], int]] = []

    for L, d in results.items():

        for p, c in d.items():

            combined.append((L, p, c))

    # sort by count desc

    combined.sort(key=lambda x: x[2], reverse=True)

    top = []

    for L, p, c in combined[:top_k]:

        support = c / max(1, (len(df) - L + 1))

        top.append({"length": L, "pattern": p, "count": c, "support": support})

    return top

"""
Multi-Timeframe Analysis Module.

Fetches the same symbol at multiple intervals and scans for sequential
colour patterns at each timeframe, then identifies alignment — where
the same directional bias appears across timeframes simultaneously.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# Timeframe hierarchy — lower index = shorter timeframe
TIMEFRAME_ORDER = [
    "1m", "2m", "5m", "15m", "30m", "60m", "90m",
    "1h", "4h", "1d", "5d", "1wk", "1mo",
]

# Sensible default period per interval to get enough candles
DEFAULT_PERIOD_FOR_INTERVAL = {
    "1m": "7d",
    "2m": "7d",
    "5m": "30d",
    "15m": "60d",
    "30m": "60d",
    "60m": "6mo",
    "90m": "6mo",
    "1h": "6mo",
    "4h": "1y",
    "1d": "2y",
    "5d": "5y",
    "1wk": "5y",
    "1mo": "max",
}

# Map common aliases
_INTERVAL_ALIASES = {"1h": "60m", "4h": "60m"}


def fetch_multi_timeframe(
    symbol: str,
    intervals: List[str],
    period: Optional[str] = None,
) -> Dict[str, pd.DataFrame]:
    """Fetch OHLCV data for *symbol* at each interval in *intervals*.

    Parameters
    ----------
    symbol : str
        Ticker symbol (e.g. ``"AAPL"``, ``"BTC-USD"``).
    intervals : list[str]
        List of yfinance-compatible intervals (e.g. ``["1h", "1d", "1wk"]``).
    period : str | None
        If given, used for every interval; otherwise we pick a sensible
        per-interval default from ``DEFAULT_PERIOD_FOR_INTERVAL``.

    Returns
    -------
    dict[str, DataFrame]
        Mapping ``interval -> DataFrame`` with standardised columns
        (``timestamp, open, high, low, close, volume``).
        Intervals that fail to fetch are omitted with a warning.
    """
    from candle_patterns.data_feeds import fetch_yahoo_data

    results: Dict[str, pd.DataFrame] = {}

    for iv in intervals:
        p = period or DEFAULT_PERIOD_FOR_INTERVAL.get(iv, "6mo")
        try:
            df = fetch_yahoo_data(symbol, period=p, interval=iv)
            if df is not None and len(df) > 0:
                results[iv] = df
            else:
                logger.warning("No data returned for %s @ %s", symbol, iv)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch %s @ %s: %s", symbol, iv, exc)

    return results


def scan_multi_timeframe(
    frames: Dict[str, pd.DataFrame],
    sequences: List[str],
) -> Dict[str, Dict[str, List[int]]]:
    """Scan every timeframe for each sequence.

    Parameters
    ----------
    frames : dict[str, DataFrame]
        Output of :func:`fetch_multi_timeframe`.
    sequences : list[str]
        Sequence strings to scan (e.g. ``["3R -> 2G", "5R -> 3G"]``).

    Returns
    -------
    dict[str, dict[str, list[int]]]
        ``{interval: {sequence: [end_indices]}}``.
    """
    from candle_patterns.patterns import (
        find_sequence_occurrences,
        find_wildcard_sequence,
    )

    results: Dict[str, Dict[str, List[int]]] = {}

    for iv, df in frames.items():
        iv_results: Dict[str, List[int]] = {}
        for seq in sequences:
            if "*" in seq:
                matches = find_wildcard_sequence(df, seq)
                iv_results[seq] = [m["end_idx"] for m in matches]
            else:
                iv_results[seq] = find_sequence_occurrences(df, seq)
        results[iv] = iv_results

    return results


def detect_alignment(
    scan_results: Dict[str, Dict[str, List[int]]],
    frames: Dict[str, pd.DataFrame],
    lookback: int = 5,
) -> List[Dict]:
    """Find timeframe alignment — sequences matching near the end across
    multiple timeframes.

    A sequence is "aligned" at a timeframe if at least one match
    occurs within the last *lookback* candles of that timeframe.

    Parameters
    ----------
    scan_results : dict
        Output of :func:`scan_multi_timeframe`.
    frames : dict[str, DataFrame]
        The DataFrames keyed by interval (for length info).
    lookback : int
        How many candles from the end to consider "recent".

    Returns
    -------
    list[dict]
        Each dict: ``{sequence, aligned_timeframes, alignment_count,
        total_timeframes}``.
    """
    if not scan_results:
        return []

    # Gather all unique sequences
    all_seqs: set = set()
    for iv_data in scan_results.values():
        all_seqs.update(iv_data.keys())

    alignment_info: List[Dict] = []

    for seq in sorted(all_seqs):
        aligned_tfs: List[str] = []
        for iv, iv_data in scan_results.items():
            indices = iv_data.get(seq, [])
            if not indices:
                continue
            df_len = len(frames[iv])
            # "recent" = within last `lookback` candles
            if any(idx >= df_len - lookback for idx in indices):
                aligned_tfs.append(iv)

        alignment_info.append(
            {
                "sequence": seq,
                "aligned_timeframes": aligned_tfs,
                "alignment_count": len(aligned_tfs),
                "total_timeframes": len(scan_results),
            }
        )

    # Sort by alignment count descending
    alignment_info.sort(key=lambda x: x["alignment_count"], reverse=True)
    return alignment_info


def multi_timeframe_summary(
    symbol: str,
    intervals: List[str],
    sequences: List[str],
    lookback: int = 5,
    period: Optional[str] = None,
) -> Dict:
    """Convenience wrapper: fetch + scan + alignment in one call.

    Returns
    -------
    dict
        ``{symbol, intervals, frames_loaded, scan_results, alignment,
        per_timeframe_stats}``.
    """
    frames = fetch_multi_timeframe(symbol, intervals, period=period)

    scan_results = scan_multi_timeframe(frames, sequences)
    alignment = detect_alignment(scan_results, frames, lookback=lookback)

    # Per-timeframe summary
    per_tf: Dict[str, Dict] = {}
    for iv, df in frames.items():
        total_matches = sum(len(v) for v in scan_results.get(iv, {}).values())
        per_tf[iv] = {
            "candle_count": len(df),
            "total_matches": total_matches,
            "sequences_found": sum(
                1 for v in scan_results.get(iv, {}).values() if v
            ),
        }

    return {
        "symbol": symbol,
        "intervals": list(frames.keys()),
        "frames_loaded": len(frames),
        "scan_results": scan_results,
        "alignment": alignment,
        "per_timeframe_stats": per_tf,
    }

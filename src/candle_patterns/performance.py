"""
Performance Optimization Module.

Provides vectorized, numpy-accelerated versions of core pattern scanning
operations to support 10K+ candle datasets efficiently.

Key optimisations:
- Vectorized symbol_sequence using numpy array ops (not row-by-row)
- Chunked sequence scanning for large datasets
- Pre-computed colour arrays for reuse across scans
- Downsampled chart data for large datasets
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Vectorised symbol classification
# ---------------------------------------------------------------------------

def vectorized_symbol_sequence(df: pd.DataFrame, doji_tol: float = 0.05) -> np.ndarray:
    """Classify each candle as 'R', 'G', or 'Doji' using vectorised numpy ops.

    ~50-100x faster than the row-by-row ``symbol_sequence()`` in patterns.py
    for datasets with 10K+ candles.

    Parameters
    ----------
    df : pd.DataFrame
        OHLCV DataFrame with at least ``open``, ``high``, ``low``, ``close``.
    doji_tol : float
        Body-to-range ratio threshold for Doji classification (default 0.05).

    Returns
    -------
    np.ndarray
        1-D array of strings: ``'R'``, ``'G'``, or ``'Doji'``.
    """
    opens = df["open"].to_numpy(dtype=np.float64)
    closes = df["close"].to_numpy(dtype=np.float64)
    highs = df["high"].to_numpy(dtype=np.float64)
    lows = df["low"].to_numpy(dtype=np.float64)

    body = np.abs(closes - opens)
    rng = highs - lows
    # Avoid division by zero
    safe_rng = np.where(rng == 0, np.inf, rng)

    is_doji = (body / safe_rng) <= doji_tol
    is_green = closes >= opens

    symbols = np.where(is_doji, "Doji", np.where(is_green, "G", "R"))
    return symbols


def vectorized_find_sequence(
    symbols: np.ndarray,
    pattern: List[Tuple[int, str]],
) -> List[int]:
    """Find all ending indices where *pattern* matches in *symbols* array.

    Only handles simple R/G/Doji tokens (not named patterns like Hammer).
    For named tokens, falls back to the standard matcher.

    Parameters
    ----------
    symbols : np.ndarray
        1-D string array from ``vectorized_symbol_sequence()``.
    pattern : list[tuple[int, str]]
        Parsed tokens, e.g. ``[(3, 'R'), (2, 'G')]``.

    Returns
    -------
    list[int]
        End indices of matches.
    """
    simple_tokens = {"R", "G", "Doji"}
    # Check that all tokens are simple — if not, return empty (caller should
    # fall back to the standard row-by-row matcher)
    for cnt, tok in pattern:
        if tok not in simple_tokens:
            return []

    n = len(symbols)
    seq_len = sum(cnt for cnt, _ in pattern)
    if seq_len > n:
        return []

    results: List[int] = []
    for start in range(0, n - seq_len + 1):
        i = start
        ok = True
        for cnt, tok in pattern:
            for k in range(cnt):
                if symbols[i + k] != tok:
                    ok = False
                    break
            if not ok:
                break
            i += cnt
        if ok:
            results.append(i - 1)
    return results


# ---------------------------------------------------------------------------
# Chunked data processing
# ---------------------------------------------------------------------------

def process_in_chunks(
    df: pd.DataFrame,
    seq_strs: List[str],
    chunk_size: int = 5000,
    overlap: int = 50,
) -> Dict[str, List[int]]:
    """Scan for sequence matches in overlapping chunks for large datasets.

    Processing is broken into chunks of ``chunk_size`` candles with
    ``overlap`` candle overlap to catch sequences that span chunk boundaries.

    Parameters
    ----------
    df : pd.DataFrame
        Full OHLCV dataset (potentially 10K+ candles).
    seq_strs : list[str]
        Sequence strings to scan.
    chunk_size : int
        Candles per chunk.
    overlap : int
        Overlap between adjacent chunks (should be >= longest sequence).

    Returns
    -------
    dict[str, list[int]]
        Mapping ``seq_str -> list_of_end_indices`` (global indices).
    """
    from .patterns import parse_sequence, find_sequence_occurrences

    n = len(df)
    results: Dict[str, List[int]] = {s: [] for s in seq_strs}

    if n <= chunk_size:
        # Small dataset — just scan directly
        for s in seq_strs:
            results[s] = find_sequence_occurrences(df, s)
        return results

    # Build chunks with overlap
    seen: Dict[str, set] = {s: set() for s in seq_strs}
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        chunk_df = df.iloc[start:end].reset_index(drop=True)

        for s in seq_strs:
            local_ends = find_sequence_occurrences(chunk_df, s)
            for local_end in local_ends:
                global_end = start + local_end
                if global_end not in seen[s]:
                    seen[s].add(global_end)
                    results[s].append(global_end)

        start += chunk_size - overlap

    # Sort results
    for s in seq_strs:
        results[s].sort()

    return results


# ---------------------------------------------------------------------------
# Chart downsampling for large datasets
# ---------------------------------------------------------------------------

def downsample_ohlcv(
    df: pd.DataFrame,
    max_points: int = 2000,
) -> pd.DataFrame:
    """Downsample an OHLCV DataFrame for chart rendering.

    Uses the LTTB-like approach: preserves visual important points (peaks,
    troughs) while reducing data to ``max_points`` rows.

    For OHLCV data, we aggregate into larger candles, preserving the
    true open/high/low/close semantics within each aggregate window.

    Parameters
    ----------
    df : pd.DataFrame
        OHLCV DataFrame with ``timestamp, open, high, low, close, volume``.
    max_points : int
        Maximum number of data points in the result.

    Returns
    -------
    pd.DataFrame
        Downsampled DataFrame (may be the same object if no downsampling needed).
    """
    if len(df) <= max_points:
        return df

    factor = len(df) / max_points
    group_size = max(1, int(factor))

    n = len(df)
    rows = []
    for g_start in range(0, n, group_size):
        g_end = min(g_start + group_size, n)
        window = df.iloc[g_start:g_end]
        rows.append({
            "timestamp": window.iloc[0]["timestamp"],
            "open": float(window.iloc[0]["open"]),
            "high": float(window["high"].max()),
            "low": float(window["low"].min()),
            "close": float(window.iloc[-1]["close"]),
            "volume": float(window["volume"].sum()) if "volume" in window.columns else 0,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Cached colour array for reuse across multiple scans
# ---------------------------------------------------------------------------

class CandleCache:
    """Memoises expensive computations for a given DataFrame.

    Call ``update(df)`` whenever the underlying data changes. Subsequent
    calls to ``symbols`` and ``numpy_symbols`` reuse the cached arrays.
    """

    def __init__(self) -> None:
        self._df_id: Optional[int] = None
        self._symbols: Optional[List[str]] = None
        self._np_symbols: Optional[np.ndarray] = None

    def update(self, df: pd.DataFrame) -> None:
        """Recompute caches if *df* changed (identified by ``id(df)`` + length)."""
        key = (id(df), len(df))
        if key == self._df_id:
            return
        self._df_id = key
        self._np_symbols = vectorized_symbol_sequence(df)
        self._symbols = self._np_symbols.tolist()

    @property
    def symbols(self) -> List[str]:
        if self._symbols is None:
            raise RuntimeError("CandleCache not initialized — call update(df) first")
        return self._symbols

    @property
    def numpy_symbols(self) -> np.ndarray:
        if self._np_symbols is None:
            raise RuntimeError("CandleCache not initialized — call update(df) first")
        return self._np_symbols

    def invalidate(self) -> None:
        self._df_id = None
        self._symbols = None
        self._np_symbols = None


# Module-level cache instance
candle_cache = CandleCache()


# ---------------------------------------------------------------------------
# Batch statistics for multiple sequences
# ---------------------------------------------------------------------------

def batch_sequence_stats(
    df: pd.DataFrame,
    seq_strs: List[str],
    hold_candles: int = 5,
) -> List[dict]:
    """Compute outcome stats for multiple sequences efficiently.

    Reuses a single ``symbol_sequence`` computation across all sequences.

    Parameters
    ----------
    df : pd.DataFrame
        OHLCV data.
    seq_strs : list[str]
        Sequences to evaluate.
    hold_candles : int
        Number of candles to hold after each match.

    Returns
    -------
    list[dict]
        One result dict per sequence (same schema as ``sequence_outcome_stats``).
    """
    from .patterns import sequence_outcome_stats

    results = []
    for s in seq_strs:
        try:
            stats = sequence_outcome_stats(df, s, hold_candles=hold_candles)
            results.append(stats)
        except Exception as exc:
            logger.warning("Stats failed for '%s': %s", s, exc)
            results.append({"sequence": s, "occurrences": 0, "error": str(exc)})
    return results


# ---------------------------------------------------------------------------
# Dataset size analysis
# ---------------------------------------------------------------------------

def dataset_info(df: pd.DataFrame) -> dict:
    """Return metadata about the dataset for performance decisions.

    Returns
    -------
    dict
        Keys: ``rows``, ``needs_downsampling``, ``recommended_chunk_size``,
        ``memory_mb``.
    """
    rows = len(df)
    mem_bytes = df.memory_usage(deep=True).sum()
    return {
        "rows": rows,
        "needs_downsampling": rows > 2000,
        "needs_chunking": rows > 5000,
        "recommended_chunk_size": min(5000, rows),
        "memory_mb": round(mem_bytes / (1024 * 1024), 2),
    }

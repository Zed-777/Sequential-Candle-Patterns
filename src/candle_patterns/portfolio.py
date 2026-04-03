"""Portfolio-level multi-symbol scanning.

Scan a list of ticker symbols for sequential colour patterns and aggregate
the results into a ranked summary.

Example
-------
>>> from candle_patterns.portfolio import scan_portfolio, rank_symbols
>>> results = scan_portfolio(["AAPL", "MSFT", "GOOG"], ["3R -> 2G", "Hammer -> 2G"])
>>> ranked = rank_symbols(results)
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core scanning
# ---------------------------------------------------------------------------


def scan_symbol(
    symbol: str,
    sequences: List[str],
    period: str = "6mo",
    interval: str = "1d",
    hold_candles: int = 5,
) -> Dict:
    """Fetch one symbol and scan it for every sequence.

    Returns a dict with keys:
        symbol, candles, matches (list of per-sequence dicts), error (str|None).
    """
    from .data_feeds import fetch_yahoo_data
    from .patterns import (
        find_sequence_occurrences,
        find_wildcard_sequence,
        sequence_outcome_stats,
    )

    result: Dict = {"symbol": symbol, "candles": 0, "matches": [], "error": None}

    try:
        df = fetch_yahoo_data(symbol, period=period, interval=interval)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    if df is None or df.empty:
        result["error"] = "No data returned"
        return result

    result["candles"] = len(df)

    for seq_str in sequences:
        entry: Dict = {"sequence": seq_str, "count": 0, "indices": [], "stats": {}}
        try:
            if "*" in seq_str:
                hits = find_wildcard_sequence(df, seq_str)
                entry["indices"] = [h["end_idx"] for h in hits]
            else:
                entry["indices"] = find_sequence_occurrences(df, seq_str)
            entry["count"] = len(entry["indices"])

            # Outcome stats when there are matches
            if entry["count"] > 0:
                stats = sequence_outcome_stats(df, seq_str, hold_candles=hold_candles)
                entry["stats"] = {
                    "win_rate": stats.get("win_rate"),
                    "avg_return": stats.get("avg_return"),
                    "max_gain": stats.get("max_gain"),
                    "max_loss": stats.get("max_loss"),
                }
        except Exception as exc:
            entry["error"] = str(exc)

        result["matches"].append(entry)

    return result


def scan_portfolio(
    symbols: List[str],
    sequences: List[str],
    period: str = "6mo",
    interval: str = "1d",
    hold_candles: int = 5,
    max_workers: int = 4,
) -> List[Dict]:
    """Scan multiple symbols for a set of sequences.

    Parameters
    ----------
    symbols : list[str]
        Ticker symbols to scan.
    sequences : list[str]
        Sequence strings (e.g. ``["3R -> 2G", "Hammer -> 1R"]``).
    period / interval : str
        Yahoo Finance fetch parameters.
    hold_candles : int
        Hold period for outcome stats.
    max_workers : int
        Parallel threads for fetching (default 4).

    Returns
    -------
    list[dict]
        One result dict per symbol (see :func:`scan_symbol`).
    """
    results: List[Dict] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(
                scan_symbol, sym, sequences, period, interval, hold_candles
            ): sym
            for sym in symbols
        }
        for future in as_completed(futures):
            sym = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                logger.error("Portfolio scan failed for %s: %s", sym, exc)
                results.append(
                    {"symbol": sym, "candles": 0, "matches": [], "error": str(exc)}
                )

    # Sort by symbol for deterministic output
    results.sort(key=lambda r: r["symbol"])
    return results


# ---------------------------------------------------------------------------
# Ranking / aggregation
# ---------------------------------------------------------------------------


def rank_symbols(
    results: List[Dict],
    sort_by: str = "total_matches",
) -> List[Dict]:
    """Rank portfolio scan results.

    Parameters
    ----------
    results : list[dict]
        Output of :func:`scan_portfolio`.
    sort_by : str
        ``"total_matches"`` (default), ``"avg_win_rate"``, or ``"avg_return"``.

    Returns
    -------
    list[dict]
        Sorted list with ``{symbol, total_matches, avg_win_rate, avg_return, sequences_matched}``.
    """
    ranked: List[Dict] = []

    for r in results:
        total = 0
        win_rates: List[float] = []
        returns: List[float] = []
        sequences_matched = 0

        for m in r.get("matches", []):
            total += m.get("count", 0)
            stats = m.get("stats", {})
            if m.get("count", 0) > 0:
                sequences_matched += 1
            wr = stats.get("win_rate")
            ar = stats.get("avg_return")
            if wr is not None:
                win_rates.append(wr)
            if ar is not None:
                returns.append(ar)

        ranked.append(
            {
                "symbol": r["symbol"],
                "total_matches": total,
                "avg_win_rate": sum(win_rates) / len(win_rates) if win_rates else None,
                "avg_return": sum(returns) / len(returns) if returns else None,
                "sequences_matched": sequences_matched,
                "error": r.get("error"),
            }
        )

    # Sort
    if sort_by == "avg_win_rate":
        ranked.sort(key=lambda x: x.get("avg_win_rate") or 0, reverse=True)
    elif sort_by == "avg_return":
        ranked.sort(key=lambda x: x.get("avg_return") or 0, reverse=True)
    else:
        ranked.sort(key=lambda x: x.get("total_matches", 0), reverse=True)

    return ranked


def portfolio_summary(results: List[Dict]) -> Dict:
    """High-level summary across all symbols.

    Returns
    -------
    dict
        ``{symbols_scanned, symbols_with_matches, total_matches,
        best_symbol, best_sequence}``.
    """
    symbols_scanned = len(results)
    symbols_with_matches = 0
    total_matches = 0
    best_symbol: Optional[str] = None
    best_symbol_matches = 0
    best_sequence: Optional[str] = None
    best_seq_matches = 0

    for r in results:
        sym_total = sum(m.get("count", 0) for m in r.get("matches", []))
        if sym_total > 0:
            symbols_with_matches += 1
        total_matches += sym_total
        if sym_total > best_symbol_matches:
            best_symbol_matches = sym_total
            best_symbol = r["symbol"]

        for m in r.get("matches", []):
            if m.get("count", 0) > best_seq_matches:
                best_seq_matches = m["count"]
                best_sequence = f"{r['symbol']}: {m['sequence']}"

    return {
        "symbols_scanned": symbols_scanned,
        "symbols_with_matches": symbols_with_matches,
        "total_matches": total_matches,
        "best_symbol": best_symbol,
        "best_sequence": best_sequence,
    }

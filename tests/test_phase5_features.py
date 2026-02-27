"""Tests for Phase 5 features:

- Multi-Timeframe analysis module
- Watchlist persistence
- Data feed caching
- Extended named tokens (Engulfing, MorningStar, EveningStar, etc.)
- Backtesting integration helpers
"""

from __future__ import annotations

import json
import os
import tempfile
import time

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candles(n: int = 50) -> pd.DataFrame:
    """Create a synthetic OHLCV DataFrame with predictable colour patterns."""
    rows = []
    for i in range(n):
        o = 100 + i * 0.5
        # alternate red / green
        if i % 3 == 0:
            c = o - 1.0  # red
        else:
            c = o + 1.0  # green
        h = max(o, c) + 0.5
        l = min(o, c) - 0.5
        rows.append({"timestamp": f"2025-01-{(i % 28) + 1:02d}", "open": o, "high": h, "low": l, "close": c, "volume": 1000 + i})
    return pd.DataFrame(rows)


def _make_engulfing_candles() -> pd.DataFrame:
    """Build candles where index 1 is a bullish engulfing of index 0."""
    rows = [
        {"timestamp": "2025-01-01", "open": 105, "high": 106, "low": 99, "close": 100, "volume": 100},  # red
        {"timestamp": "2025-01-02", "open": 99, "high": 112, "low": 98, "close": 110, "volume": 100},   # green, body >= prev body
        {"timestamp": "2025-01-03", "open": 110, "high": 115, "low": 109, "close": 114, "volume": 100}, # green
    ]
    return pd.DataFrame(rows)


def _make_star_candles() -> pd.DataFrame:
    """Build candles for Morning Star (idx 2) and Evening Star (idx 5)."""
    rows = [
        # Morning Star: bearish -> small body -> bullish
        {"timestamp": "2025-01-01", "open": 110, "high": 112, "low": 100, "close": 101, "volume": 100},  # red
        {"timestamp": "2025-01-02", "open": 101, "high": 102, "low": 100, "close": 101.2, "volume": 100}, # small body
        {"timestamp": "2025-01-03", "open": 102, "high": 112, "low": 101, "close": 111, "volume": 100},  # green (morning star end)
        # Evening Star: bullish -> small body -> bearish
        {"timestamp": "2025-01-04", "open": 111, "high": 120, "low": 110, "close": 119, "volume": 100},  # green
        {"timestamp": "2025-01-05", "open": 119, "high": 120, "low": 118, "close": 119.3, "volume": 100}, # small body
        {"timestamp": "2025-01-06", "open": 119, "high": 120, "low": 110, "close": 111, "volume": 100},  # red (evening star end)
    ]
    return pd.DataFrame(rows)


# =====================================================================
# Multi-Timeframe Module Tests
# =====================================================================

class TestMultiTimeframeModule:
    """Tests for multi_timeframe.py pure-logic functions (no network)."""

    def test_import(self):
        from candle_patterns.multi_timeframe import (
            fetch_multi_timeframe,
            scan_multi_timeframe,
            detect_alignment,
            multi_timeframe_summary,
            TIMEFRAME_ORDER,
            DEFAULT_PERIOD_FOR_INTERVAL,
        )
        assert "1d" in TIMEFRAME_ORDER
        assert "1d" in DEFAULT_PERIOD_FOR_INTERVAL

    def test_scan_multi_timeframe_basic(self):
        """scan_multi_timeframe with pre-built frames dict."""
        from candle_patterns.multi_timeframe import scan_multi_timeframe

        df = _make_candles(50)
        frames = {"1d": df, "1h": df}
        sequences = ["1R -> 1G"]
        result = scan_multi_timeframe(frames, sequences)

        assert "1d" in result
        assert "1h" in result
        assert "1R -> 1G" in result["1d"]
        assert isinstance(result["1d"]["1R -> 1G"], list)

    def test_scan_multi_timeframe_wildcard(self):
        """Wildcard sequences are handled correctly."""
        from candle_patterns.multi_timeframe import scan_multi_timeframe

        df = _make_candles(50)
        frames = {"1d": df}
        sequences = ["1R -> * -> 1G"]
        result = scan_multi_timeframe(frames, sequences)
        assert "1R -> * -> 1G" in result["1d"]

    def test_detect_alignment_empty(self):
        from candle_patterns.multi_timeframe import detect_alignment
        assert detect_alignment({}, {}) == []

    def test_detect_alignment_finds_recent(self):
        """Alignment detection identifies sequences ending near end of data."""
        from candle_patterns.multi_timeframe import scan_multi_timeframe, detect_alignment

        df = _make_candles(50)
        frames = {"1d": df, "1h": df}
        scan_results = scan_multi_timeframe(frames, ["1R -> 1G"])
        alignment = detect_alignment(scan_results, frames, lookback=50)

        # With lookback=50 covering all data, all timeframes should align
        for a in alignment:
            if a["sequence"] == "1R -> 1G":
                assert a["alignment_count"] == 2  # both 1d and 1h

    def test_detect_alignment_no_recent(self):
        """With lookback=1 and no match at the very end, alignment = 0."""
        from candle_patterns.multi_timeframe import scan_multi_timeframe, detect_alignment

        # Build a DataFrame where the last candle doesn't end a sequence
        df = _make_candles(10)
        frames = {"1d": df}
        sequences = ["5R -> 5G"]  # unlikely to match at all in 10 candles
        scan_results = scan_multi_timeframe(frames, sequences)
        alignment = detect_alignment(scan_results, frames, lookback=1)

        for a in alignment:
            assert a["alignment_count"] == 0

    def test_timeframe_order_length(self):
        from candle_patterns.multi_timeframe import TIMEFRAME_ORDER
        assert len(TIMEFRAME_ORDER) >= 10


# =====================================================================
# Watchlist Tests
# =====================================================================

class TestWatchlist:
    """Tests for watchlist.py — file-based sequence library."""

    def _tmp_path(self) -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        return path

    def test_list_empty(self):
        from candle_patterns.watchlist import list_watchlist
        path = self._tmp_path()
        try:
            # Remove the file so it's truly empty
            os.unlink(path)
            result = list_watchlist(path)
            assert result == []
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_add_and_list(self):
        from candle_patterns.watchlist import add_to_watchlist, list_watchlist
        path = self._tmp_path()
        try:
            os.unlink(path)
            entry = add_to_watchlist("Bull Setup", ["3R -> 2G", "5R -> 3G"], symbol="AAPL", path=path)
            assert entry["label"] == "Bull Setup"
            assert len(entry["sequences"]) == 2
            assert entry["symbol"] == "AAPL"
            assert entry["id"] > 0

            entries = list_watchlist(path)
            assert len(entries) == 1
            assert entries[0]["label"] == "Bull Setup"
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_add_empty_label_raises(self):
        from candle_patterns.watchlist import add_to_watchlist
        path = self._tmp_path()
        try:
            os.unlink(path)
            with pytest.raises(ValueError, match="label"):
                add_to_watchlist("", ["3R -> 2G"], path=path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_add_no_sequences_raises(self):
        from candle_patterns.watchlist import add_to_watchlist
        path = self._tmp_path()
        try:
            os.unlink(path)
            with pytest.raises(ValueError, match="sequence"):
                add_to_watchlist("Test", [], path=path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_remove(self):
        from candle_patterns.watchlist import add_to_watchlist, remove_from_watchlist, list_watchlist
        path = self._tmp_path()
        try:
            os.unlink(path)
            e = add_to_watchlist("ToRemove", ["1R -> 1G"], path=path)
            assert remove_from_watchlist(e["id"], path=path) is True
            assert list_watchlist(path) == []
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_remove_nonexistent(self):
        from candle_patterns.watchlist import remove_from_watchlist
        path = self._tmp_path()
        try:
            os.unlink(path)
            assert remove_from_watchlist(999999, path=path) is False
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_update_last_used(self):
        from candle_patterns.watchlist import add_to_watchlist, update_last_used, get_watchlist_entry
        path = self._tmp_path()
        try:
            os.unlink(path)
            e = add_to_watchlist("Test", ["2R -> 2G"], path=path)
            assert e["last_used"] is None
            assert update_last_used(e["id"], path=path) is True
            updated = get_watchlist_entry(e["id"], path=path)
            assert updated is not None
            assert updated["last_used"] is not None
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_clear(self):
        from candle_patterns.watchlist import add_to_watchlist, clear_watchlist, list_watchlist
        path = self._tmp_path()
        try:
            os.unlink(path)
            add_to_watchlist("A", ["1R"], path=path)
            add_to_watchlist("B", ["2G"], path=path)
            count = clear_watchlist(path)
            assert count == 2
            assert list_watchlist(path) == []
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_export_import(self):
        from candle_patterns.watchlist import add_to_watchlist, export_watchlist, import_watchlist, list_watchlist
        path = self._tmp_path()
        path2 = self._tmp_path()
        try:
            os.unlink(path)
            os.unlink(path2)
            add_to_watchlist("X", ["3R -> 2G"], path=path)
            exported = export_watchlist(path)
            imported_count = import_watchlist(exported, merge=False, path=path2)
            assert imported_count == 1
            entries = list_watchlist(path2)
            assert len(entries) == 1
            assert entries[0]["label"] == "X"
        finally:
            for p in [path, path2]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_import_invalid_json_raises(self):
        from candle_patterns.watchlist import import_watchlist
        with pytest.raises(ValueError, match="Invalid JSON"):
            import_watchlist("not json")

    def test_update_entry(self):
        from candle_patterns.watchlist import add_to_watchlist, update_watchlist_entry, get_watchlist_entry
        path = self._tmp_path()
        try:
            os.unlink(path)
            e = add_to_watchlist("Original", ["1R"], path=path)
            assert update_watchlist_entry(e["id"], label="Updated", path=path) is True
            updated = get_watchlist_entry(e["id"], path=path)
            assert updated is not None
            assert updated["label"] == "Updated"
        finally:
            if os.path.exists(path):
                os.unlink(path)


# =====================================================================
# Data Feed Caching Tests
# =====================================================================

class TestDataFeedCache:
    """Tests for the in-memory LRU cache in data_feeds.py."""

    def test_cache_imports(self):
        from candle_patterns.data_feeds import cache_clear, cache_stats, cache_get, cache_put
        assert callable(cache_clear)

    def test_cache_put_get(self):
        from candle_patterns.data_feeds import cache_put, cache_get, cache_clear
        cache_clear()
        df = pd.DataFrame({"a": [1, 2, 3]})
        cache_put("test-key", df)
        result = cache_get("test-key")
        assert result is not None
        assert len(result) == 3
        cache_clear()

    def test_cache_miss(self):
        from candle_patterns.data_feeds import cache_get, cache_clear
        cache_clear()
        assert cache_get("nonexistent") is None

    def test_cache_clear_returns_count(self):
        from candle_patterns.data_feeds import cache_put, cache_clear
        cache_clear()
        cache_put("k1", pd.DataFrame({"x": [1]}))
        cache_put("k2", pd.DataFrame({"x": [2]}))
        count = cache_clear()
        assert count == 2

    def test_cache_stats(self):
        from candle_patterns.data_feeds import cache_stats, cache_clear
        cache_clear()
        stats = cache_stats()
        assert stats["size"] == 0
        assert stats["max_size"] > 0
        assert stats["ttl_seconds"] > 0

    def test_cache_returns_copy(self):
        """Modifying returned DataFrame shouldn't corrupt cache."""
        from candle_patterns.data_feeds import cache_put, cache_get, cache_clear
        cache_clear()
        df = pd.DataFrame({"x": [10, 20, 30]})
        cache_put("copy-test", df)
        result = cache_get("copy-test")
        assert result is not None
        result["x"] = [99, 99, 99]  # mutate
        result2 = cache_get("copy-test")
        assert result2 is not None
        assert list(result2["x"]) == [10, 20, 30]  # original preserved
        cache_clear()


# =====================================================================
# Named Token Tests (Engulfing, MorningStar, EveningStar, etc.)
# =====================================================================

class TestNamedTokens:
    """Tests for extended match_named_token support in patterns.py."""

    def test_doji_still_works(self):
        from candle_patterns.patterns import match_named_token
        df = pd.DataFrame([
            {"open": 100.0, "high": 110.0, "low": 90.0, "close": 100.1, "volume": 100},
        ])
        assert match_named_token(df, 0, "Doji") is True

    def test_hammer_still_works(self):
        from candle_patterns.patterns import match_named_token
        df = pd.DataFrame([
            {"open": 105.0, "high": 106.0, "low": 90.0, "close": 106.0, "volume": 100},
        ])
        assert match_named_token(df, 0, "Hammer") is True

    def test_bullish_engulfing(self):
        from candle_patterns.patterns import match_named_token
        df = _make_engulfing_candles()
        assert match_named_token(df, 1, "BullEngulfing") is True

    def test_engulfing_generic(self):
        from candle_patterns.patterns import match_named_token
        df = _make_engulfing_candles()
        assert match_named_token(df, 1, "Engulfing") is True

    def test_morning_star(self):
        from candle_patterns.patterns import match_named_token
        df = _make_star_candles()
        assert match_named_token(df, 2, "MorningStar") is True

    def test_evening_star(self):
        from candle_patterns.patterns import match_named_token
        df = _make_star_candles()
        assert match_named_token(df, 5, "EveningStar") is True

    def test_shooting_star(self):
        from candle_patterns.patterns import match_named_token
        df = pd.DataFrame([
            {"open": 100.0, "high": 120.0, "low": 99.0, "close": 101.0, "volume": 100},
        ])
        # upper wick = 120 - 101 = 19, body = 1 => 19 >= 2*1 => true
        assert match_named_token(df, 0, "ShootingStar") is True

    def test_spinning_top(self):
        from candle_patterns.patterns import match_named_token
        df = pd.DataFrame([
            {"open": 100.0, "high": 110.0, "low": 90.0, "close": 100.5, "volume": 100},
        ])
        # body = 0.5, range = 20, 0.5 <= 0.2*20 = 4 => true
        assert match_named_token(df, 0, "SpinningTop") is True

    def test_unknown_token_returns_false(self):
        from candle_patterns.patterns import match_named_token
        df = _make_candles(5)
        assert match_named_token(df, 2, "FakeToken") is False

    def test_engulfing_at_index_0_returns_false(self):
        """Engulfing at index 0 can't look back, should return False."""
        from candle_patterns.patterns import match_named_token
        df = _make_engulfing_candles()
        assert match_named_token(df, 0, "Engulfing") is False


# =====================================================================
# Backtesting Integration Tests
# =====================================================================

class TestBacktestIntegration:
    """Tests for backtesting engine used by the dashboard callback."""

    def test_engine_import(self):
        from candle_patterns.backtesting import BacktestEngine
        engine = BacktestEngine()
        assert engine.risk_free_rate == 0.02

    def test_calculate_returns_basic(self):
        from candle_patterns.backtesting import BacktestEngine
        df = _make_candles(50)
        engine = BacktestEngine()
        trades = engine.calculate_returns(df, [0, 5, 10], hold_periods=3)
        assert len(trades) > 0
        assert "return" in trades.columns
        assert "profit" in trades.columns

    def test_equity_curve(self):
        from candle_patterns.backtesting import BacktestEngine
        df = _make_candles(50)
        engine = BacktestEngine()
        trades = engine.calculate_returns(df, [0, 5, 10, 15, 20], hold_periods=3)
        eq = engine.calculate_equity_curve(trades, initial_capital=10000)
        assert len(eq) == len(trades)
        assert eq.iloc[0] != 0  # equity should start from initial_capital + first profit

    def test_sharpe_ratio(self):
        from candle_patterns.backtesting import BacktestEngine
        engine = BacktestEngine()
        df = _make_candles(50)
        trades = engine.calculate_returns(df, [0, 5, 10, 15], hold_periods=3)
        sharpe = engine.calculate_sharpe_ratio(trades["return"])
        assert isinstance(sharpe, float)

    def test_win_rate(self):
        from candle_patterns.backtesting import BacktestEngine
        engine = BacktestEngine()
        df = _make_candles(50)
        trades = engine.calculate_returns(df, [0, 5, 10], hold_periods=3)
        wr, wins, losses = engine.calculate_win_rate(trades)
        assert 0 <= wr <= 1
        assert wins + losses == len(trades)

    def test_empty_indices(self):
        from candle_patterns.backtesting import BacktestEngine
        engine = BacktestEngine()
        df = _make_candles(50)
        trades = engine.calculate_returns(df, [], hold_periods=3)
        assert len(trades) == 0


# =====================================================================
# Integration: named tokens in sequence scanning
# =====================================================================

class TestNamedTokenSequenceScanning:
    """Use extended named tokens inside full sequence scanning."""

    def test_sequence_with_engulfing(self):
        """Scan '1R -> Engulfing' against data with a bullish engulfing."""
        from candle_patterns.patterns import find_sequence_occurrences
        df = _make_engulfing_candles()
        # idx 0 = red, idx 1 = engulfing
        results = find_sequence_occurrences(df, "1R -> Engulfing")
        assert len(results) >= 1

    def test_sequence_with_morning_star(self):
        """Scan for MorningStar token in a sequence."""
        from candle_patterns.patterns import find_sequence_occurrences
        df = _make_star_candles()
        # The morning star completes at index 2: indices [0,1,2]
        # We need: 1R -> ... -> MorningStar. Since morning star checks idx-2,idx-1,idx
        # and match_named_token uses single candle count=1, we just need MorningStar at idx 2
        results = find_sequence_occurrences(df, "MorningStar")
        # MorningStar at index 2 => end index = 3
        assert len(results) >= 1

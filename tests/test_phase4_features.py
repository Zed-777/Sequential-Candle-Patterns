"""Tests for Phase 4 features: data_feeds, reverse_pattern_finder,
sequence_confidence, sequence_heatmap_data.
"""
from __future__ import annotations

import pandas as pd
import pytest

from candle_patterns.patterns import (
    reverse_pattern_finder,
    sequence_confidence,
    sequence_heatmap_data,
    find_sequence_occurrences,
    sequence_outcome_stats,
)

from candle_patterns.data_feeds import (
    fetch_yahoo_data,
    search_symbols,
    POPULAR_SYMBOLS,
    VALID_INTERVALS,
    VALID_PERIODS,
    ALL_POPULAR,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candles(colours: str, base_open: float = 100.0, volatility: float = 2.0) -> pd.DataFrame:
    """Build a DataFrame from a colour string like 'RRGGRD'.

    R = red (close < open), G = green (close > open), D = doji.
    """
    rows = []
    for i, c in enumerate(colours):
        o = base_open + i * 0.5
        if c == "R":
            rows.append({"timestamp": f"2025-01-{i+1:02d}", "open": o + volatility, "high": o + volatility + 1, "low": o - 1, "close": o, "volume": 100})
        elif c == "G":
            rows.append({"timestamp": f"2025-01-{i+1:02d}", "open": o, "high": o + volatility + 1, "low": o - 1, "close": o + volatility, "volume": 100})
        else:  # Doji
            rows.append({"timestamp": f"2025-01-{i+1:02d}", "open": o, "high": o + 5, "low": o - 5, "close": o, "volume": 100})
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def _make_volatile_candles(n: int = 50) -> pd.DataFrame:
    """Build a dataset with some big moves for reverse pattern finder testing."""
    rows = []
    import random
    random.seed(42)
    price = 100.0
    for i in range(n):
        change = random.uniform(-3, 3)
        # Insert some big moves
        if i in (15, 25, 35, 45):
            change = random.choice([5, -5, 4, -4])
        o = price
        c = price + change
        h = max(o, c) + abs(change) * 0.3
        l = min(o, c) - abs(change) * 0.3
        rows.append({
            "timestamp": f"2025-01-{(i % 28) + 1:02d}",
            "open": round(o, 4),
            "high": round(h, 4),
            "low": round(l, 4),
            "close": round(c, 4),
            "volume": 100,
        })
        price = c
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ===========================================================================
# Data Feeds — constants and validation
# ===========================================================================

class TestDataFeedsConstants:
    def test_valid_intervals_list(self):
        assert "1d" in VALID_INTERVALS
        assert "1h" in VALID_INTERVALS
        assert "5m" in VALID_INTERVALS
        assert len(VALID_INTERVALS) >= 10

    def test_valid_periods_list(self):
        assert "6mo" in VALID_PERIODS
        assert "1y" in VALID_PERIODS
        assert "max" in VALID_PERIODS

    def test_popular_symbols_structure(self):
        assert "Stocks" in POPULAR_SYMBOLS
        assert "Crypto" in POPULAR_SYMBOLS
        assert "AAPL" in POPULAR_SYMBOLS["Stocks"]
        assert "BTC-USD" in POPULAR_SYMBOLS["Crypto"]

    def test_all_popular_flattened(self):
        assert "AAPL" in ALL_POPULAR
        assert "BTC-USD" in ALL_POPULAR
        assert len(ALL_POPULAR) > 30


class TestFetchYahooData:
    def test_empty_symbol_raises(self):
        with pytest.raises(ValueError, match="empty"):
            fetch_yahoo_data("")

    def test_invalid_interval_raises(self):
        with pytest.raises(ValueError, match="Invalid interval"):
            fetch_yahoo_data("AAPL", interval="99x")

    def test_invalid_period_raises(self):
        with pytest.raises(ValueError, match="Invalid period"):
            fetch_yahoo_data("AAPL", period="99x")

    @pytest.mark.skipif(True, reason="Network test — enable manually for integration testing")
    def test_fetch_aapl_daily(self):
        """Integration test: fetch AAPL daily data (requires internet)."""
        df = fetch_yahoo_data("AAPL", period="1mo", interval="1d")
        assert len(df) > 10
        assert "timestamp" in df.columns
        assert "open" in df.columns
        assert "close" in df.columns


class TestSearchSymbols:
    def test_empty_query(self):
        result = search_symbols("")
        assert result == []

    @pytest.mark.skipif(True, reason="Network test — enable manually for integration testing")
    def test_search_apple(self):
        """Integration test: search for Apple (requires internet)."""
        results = search_symbols("Apple")
        assert len(results) > 0
        assert any("AAPL" in r.get("symbol", "") for r in results)


# ===========================================================================
# Reverse Pattern Finder
# ===========================================================================

class TestReversePatternFinder:
    def test_returns_list(self):
        df = _make_volatile_candles(50)
        results = reverse_pattern_finder(df, threshold_pct=2.0, direction="up")
        assert isinstance(results, list)

    def test_result_structure(self):
        df = _make_volatile_candles(50)
        results = reverse_pattern_finder(df, threshold_pct=1.0, direction="both")
        if results:
            r = results[0]
            assert "sequence" in r
            assert "count" in r
            assert "length" in r
            assert "avg_move_pct" in r
            assert "direction" in r

    def test_direction_up(self):
        df = _make_volatile_candles(50)
        results = reverse_pattern_finder(df, threshold_pct=2.0, direction="up")
        for r in results:
            assert r["avg_move_pct"] > 0

    def test_direction_down(self):
        df = _make_volatile_candles(50)
        results = reverse_pattern_finder(df, threshold_pct=2.0, direction="down")
        for r in results:
            assert r["avg_move_pct"] < 0

    def test_too_few_candles(self):
        df = _make_candles("RG")
        results = reverse_pattern_finder(df, threshold_pct=1.0, lookback=5)
        assert results == []

    def test_top_k_limit(self):
        df = _make_volatile_candles(50)
        results = reverse_pattern_finder(df, threshold_pct=0.5, direction="both", top_k=5)
        assert len(results) <= 5

    def test_high_threshold_no_results(self):
        df = _make_candles("RRGGRRGG")  # small moves
        results = reverse_pattern_finder(df, threshold_pct=50.0, direction="up")
        assert results == []


# ===========================================================================
# Sequence Confidence Scoring
# ===========================================================================

class TestSequenceConfidence:
    def test_returns_dict(self):
        df = _make_candles("RRGGRRGGRRGG")
        result = sequence_confidence(df, "2R", hold_candles=2)
        assert isinstance(result, dict)

    def test_all_fields_present(self):
        df = _make_candles("RRGGRRGGRRGG")
        result = sequence_confidence(df, "2R", hold_candles=2)
        expected = ["z_score", "p_value", "confidence_level", "sequence_avg",
                     "baseline_avg", "baseline_std", "sample_size", "is_significant"]
        for k in expected:
            assert k in result, f"Missing key: {k}"

    def test_insufficient_data(self):
        df = _make_candles("RG")  # only 1 possible occurrence
        result = sequence_confidence(df, "1R -> 1G", hold_candles=1)
        # Should handle gracefully
        assert result["confidence_level"] in ("Insufficient data", "Insufficient baseline",
                                               "Very High (p < 0.01)", "High (p < 0.05)",
                                               "Moderate (p < 0.10)", "Low (p >= 0.10)")

    def test_p_value_range(self):
        df = _make_candles("RRGGRRGGRRGGRRGG")
        result = sequence_confidence(df, "2R", hold_candles=2)
        assert 0 <= result["p_value"] <= 2.0  # two-tailed p-value

    def test_z_score_numeric(self):
        df = _make_candles("RRGGRRGGRRGG")
        result = sequence_confidence(df, "2R", hold_candles=2)
        assert isinstance(result["z_score"], float)

    def test_is_significant_boolean(self):
        df = _make_candles("RRGGRRGGRRGG")
        result = sequence_confidence(df, "2R", hold_candles=2)
        assert isinstance(result["is_significant"], bool)


# ===========================================================================
# Sequence Heatmap Data
# ===========================================================================

class TestSequenceHeatmapData:
    def test_returns_dict(self):
        df = _make_candles("RRGGRRGGRRGG")
        result = sequence_heatmap_data(df, ["2R", "2G"], bucket_size=4)
        assert isinstance(result, dict)

    def test_structure(self):
        df = _make_candles("RRGGRRGGRRGG")
        result = sequence_heatmap_data(df, ["2R", "2G"], bucket_size=4)
        assert "buckets" in result
        assert "timestamps" in result
        assert "sequences" in result
        assert "2R" in result["sequences"]
        assert "2G" in result["sequences"]

    def test_bucket_count(self):
        df = _make_candles("RRGGRRGGRRGGRRGG")  # 16 candles
        result = sequence_heatmap_data(df, ["2R"], bucket_size=4)
        assert len(result["buckets"]) == 4  # 16 / 4 = 4 buckets
        assert len(result["sequences"]["2R"]) == 4

    def test_counts_are_nonnegative(self):
        df = _make_candles("RRGGRRGG")
        result = sequence_heatmap_data(df, ["2R", "2G"], bucket_size=2)
        for seq_str, counts in result["sequences"].items():
            for c in counts:
                assert c >= 0

    def test_wildcard_sequence(self):
        df = _make_candles("RRGGRRGGRR")
        result = sequence_heatmap_data(df, ["2R -> * -> 2G"], bucket_size=5)
        assert "2R -> * -> 2G" in result["sequences"]

    def test_single_bucket(self):
        df = _make_candles("RRGG")
        result = sequence_heatmap_data(df, ["2R"], bucket_size=100)
        assert len(result["buckets"]) == 1

    def test_timestamps_populated(self):
        df = _make_candles("RRGGRRGG")
        result = sequence_heatmap_data(df, ["2R"], bucket_size=4)
        assert len(result["timestamps"]) == 2
        assert result["timestamps"][0] != ""


# ===========================================================================
# Integration: Patterns + Data combo
# ===========================================================================

class TestPatternsIntegration:
    def test_reverse_finder_sequences_are_scannable(self):
        """Sequences returned by reverse_pattern_finder should be valid for find_sequence_occurrences."""
        df = _make_volatile_candles(50)
        results = reverse_pattern_finder(df, threshold_pct=1.0, direction="both", top_k=5)
        for r in results:
            occurrences = find_sequence_occurrences(df, r["sequence"])
            assert isinstance(occurrences, list)

    def test_confidence_works_with_outcome_stats(self):
        """sequence_confidence and sequence_outcome_stats should agree on occurrences."""
        df = _make_candles("RRGGRRGGRRGG")
        stats = sequence_outcome_stats(df, "2R", hold_candles=2)
        conf = sequence_confidence(df, "2R", hold_candles=2)
        assert conf["sample_size"] == stats["occurrences"]

    def test_heatmap_with_no_matches(self):
        """Heatmap should work even when a sequence has zero matches."""
        df = _make_candles("RRRRRRRRRR")
        result = sequence_heatmap_data(df, ["5G"], bucket_size=5)
        assert all(c == 0 for c in result["sequences"]["5G"])

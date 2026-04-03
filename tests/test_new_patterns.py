"""Unit tests for the 5 new candlestick patterns added in Phase 2."""

import pandas as pd
from candle_patterns.detection import detect_patterns


def make_candle(ts, open_, high, low, close):
    """Create a single OHLC candle row."""
    return {
        "timestamp": pd.Timestamp(ts),
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
    }


def df_from_candles(candles):
    """Create a DataFrame from a list of candle dicts."""
    return pd.DataFrame(candles)


# --- Dark Cloud Cover ---
# Requires: prior green candle, then red candle opens above prior close,
# closes below midpoint of prior body.


class TestDarkCloudCover:
    def test_dark_cloud_cover_detected(self):
        """Classic dark cloud cover: green candle followed by red candle opening
        above prior close and closing below prior midpoint."""
        df = df_from_candles(
            [
                make_candle(
                    "2024-01-01", 10.0, 15.0, 9.0, 14.0
                ),  # Green: open=10, close=14
                make_candle(
                    "2024-01-02", 15.0, 16.0, 10.5, 11.0
                ),  # Red: open=15 > 14, close=11 < midpoint(12)
            ]
        )
        results = detect_patterns(df)
        assert any(
            r["pattern"] == "dark_cloud_cover" for r in results
        ), f"dark_cloud_cover not found in {[r['pattern'] for r in results]}"

    def test_dark_cloud_cover_not_detected_close_above_midpoint(self):
        """If the red candle closes above the midpoint, it's NOT dark cloud cover."""
        df = df_from_candles(
            [
                make_candle(
                    "2024-01-01", 10.0, 15.0, 9.0, 14.0
                ),  # Green: open=10, close=14, mid=12
                make_candle(
                    "2024-01-02", 15.0, 16.0, 12.5, 13.0
                ),  # Red: close=13 > midpoint(12)
            ]
        )
        results = detect_patterns(df)
        assert not any(
            r["pattern"] == "dark_cloud_cover" for r in results
        ), "dark_cloud_cover was falsely detected"


# --- Bullish Harami ---
# Requires: prior red candle, then green candle with body fully inside prior candle's range.


class TestBullishHarami:
    def test_bullish_harami_detected(self):
        """Classic bullish harami: large red candle followed by small green candle inside."""
        df = df_from_candles(
            [
                make_candle(
                    "2024-01-01", 20.0, 21.0, 9.0, 10.0
                ),  # Large red: o=20, h=21, l=9, c=10
                make_candle(
                    "2024-01-02", 12.0, 18.0, 11.0, 16.0
                ),  # Small green inside: h=18<21, l=11>9
            ]
        )
        results = detect_patterns(df)
        assert any(
            r["pattern"] == "bullish_harami" for r in results
        ), f"bullish_harami not found in {[r['pattern'] for r in results]}"

    def test_bullish_harami_not_detected_outside_range(self):
        """If the second candle exceeds the prior high, it's NOT bullish harami."""
        df = df_from_candles(
            [
                make_candle("2024-01-01", 20.0, 21.0, 9.0, 10.0),  # Red: h=21
                make_candle(
                    "2024-01-02", 12.0, 22.0, 11.0, 16.0
                ),  # Green but h=22 > 21
            ]
        )
        results = detect_patterns(df)
        assert not any(
            r["pattern"] == "bullish_harami" for r in results
        ), "bullish_harami was falsely detected"


# --- Bearish Harami ---
# Requires: prior green candle, then red candle with body fully inside prior candle's range.


class TestBearishHarami:
    def test_bearish_harami_detected(self):
        """Classic bearish harami: large green candle followed by small red candle inside."""
        df = df_from_candles(
            [
                make_candle(
                    "2024-01-01", 10.0, 21.0, 9.0, 20.0
                ),  # Large green: o=10, h=21, l=9, c=20
                make_candle(
                    "2024-01-02", 18.0, 19.0, 11.0, 12.0
                ),  # Small red inside: h=19<21, l=11>9
            ]
        )
        results = detect_patterns(df)
        assert any(
            r["pattern"] == "bearish_harami" for r in results
        ), f"bearish_harami not found in {[r['pattern'] for r in results]}"

    def test_bearish_harami_not_detected_outside_range(self):
        """If the second candle breaks below the prior low, it's NOT bearish harami."""
        df = df_from_candles(
            [
                make_candle("2024-01-01", 10.0, 21.0, 9.0, 20.0),  # Green: l=9
                make_candle("2024-01-02", 18.0, 19.0, 8.0, 12.0),  # Red but l=8 < 9
            ]
        )
        results = detect_patterns(df)
        assert not any(
            r["pattern"] == "bearish_harami" for r in results
        ), "bearish_harami was falsely detected"


# --- On Neck Line ---
# Requires: red candle, then another red candle closing near the prior low.


class TestOnNeckLine:
    def test_on_neck_line_detected(self):
        """On neck line: first red candle, second red closes near the first's low."""
        df = df_from_candles(
            [
                make_candle("2024-01-01", 20.0, 21.0, 15.0, 16.0),  # Red: low=15
                make_candle(
                    "2024-01-02", 16.5, 17.0, 14.8, 15.0
                ),  # Red: close=15.0, near prior low=15.0
            ]
        )
        results = detect_patterns(df)
        assert any(
            r["pattern"] == "on_neck_line" for r in results
        ), f"on_neck_line not found in {[r['pattern'] for r in results]}"


# --- In Neck Line ---
# Requires: red candle, then another red candle closing above the prior close
# but opening below the prior open.


class TestInNeckLine:
    def test_in_neck_line_detected(self):
        """In neck line: first red candle, second red closes slightly above prior close."""
        df = df_from_candles(
            [
                make_candle("2024-01-01", 20.0, 21.0, 14.5, 15.0),  # Red: o=20, c=15
                make_candle(
                    "2024-01-02", 17.0, 18.0, 15.0, 16.0
                ),  # Red: o=17<20, c=16>15
            ]
        )
        results = detect_patterns(df)
        assert any(
            r["pattern"] == "in_neck_line" for r in results
        ), f"in_neck_line not found in {[r['pattern'] for r in results]}"


# --- Integration test: all new patterns detectable ---


class TestNewPatternsIntegration:
    def test_all_new_patterns_in_rules(self):
        """Verify all 5 new patterns are registered in RULES dictionary."""
        from candle_patterns.detection import RULES

        new_patterns = [
            "dark_cloud_cover",
            "bullish_harami",
            "bearish_harami",
            "on_neck_line",
            "in_neck_line",
        ]
        for pname in new_patterns:
            assert pname in RULES, f"Pattern '{pname}' not found in RULES dictionary"

    def test_total_pattern_count_at_least_17(self):
        """Verify RULES contains 17+ patterns (12 original + 5 new)."""
        from candle_patterns.detection import RULES

        assert len(RULES) >= 17, f"Expected 17+ patterns, got {len(RULES)}"

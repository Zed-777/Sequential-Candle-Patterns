"""Tests for reporting module."""

import pandas as pd
import pytest

from candle_patterns.reporting import summarize_detections, pattern_sparkline_series


@pytest.fixture
def sample_df():
    """Create a simple OHLCV dataframe for testing."""
    return pd.DataFrame({
        'open': [100, 101, 102, 103, 104, 105],
        'high': [102, 103, 104, 105, 106, 107],
        'low': [99, 100, 101, 102, 103, 104],
        'close': [101, 102, 103, 104, 105, 106],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500],
    })


@pytest.fixture
def sample_detections():
    """Create sample detections for testing."""
    return [
        {'pattern': '3R', 'index': 0},
        {'pattern': '3R', 'index': 1},
        {'pattern': '2G', 'index': 2},
        {'pattern': '2G', 'index': 3},
    ]


class TestSummarizeDetections:
    """Tests for summarize_detections function."""

    def test_summarize_detections_basic(self, sample_df, sample_detections):
        """Test basic aggregation by pattern."""
        result = summarize_detections(sample_df, sample_detections)

        assert len(result) == 2  # Two patterns: 3R, 2G
        assert result[0]['pattern'] in ('3R', '2G')
        assert result[0]['count'] == 2
        assert result[1]['count'] == 2

    def test_summarize_detections_keys(self, sample_df, sample_detections):
        """Test that result rows have required keys."""
        result = summarize_detections(sample_df, sample_detections)

        for row in result:
            assert 'pattern' in row
            assert 'count' in row
            assert 'support' in row
            assert 'avg_return' in row
            assert 'win_rate' in row

    def test_summarize_detections_sorted_by_count(self, sample_df):
        """Test that results are sorted by count descending."""
        detections = [
            {'pattern': 'A', 'index': 0},
            {'pattern': 'A', 'index': 1},
            {'pattern': 'A', 'index': 2},
            {'pattern': 'B', 'index': 3},
        ]
        result = summarize_detections(sample_df, detections)

        assert result[0]['count'] == 3  # Pattern A has 3 occurrences
        assert result[1]['count'] == 1  # Pattern B has 1 occurrence

    def test_summarize_detections_empty(self, sample_df):
        """Test with empty detections list."""
        result = summarize_detections(sample_df, [])
        assert result == []

    def test_summarize_detections_support_calculation(self, sample_df):
        """Test that support is calculated correctly (count / n)."""
        detections = [
            {'pattern': 'X', 'index': 0},
            {'pattern': 'X', 'index': 1},
        ]
        result = summarize_detections(sample_df, detections)

        # n = 6, count = 2, so support = 2/6 ≈ 0.333
        assert abs(result[0]['support'] - (2 / 6)) < 0.01


class TestPatternSparklineSeries:
    """Tests for pattern_sparkline_series function."""

    def test_sparkline_series_basic(self, sample_df, sample_detections):
        """Test that sparkline returns dict with pattern keys."""
        result = pattern_sparkline_series(sample_df, sample_detections, horizon=3)

        assert isinstance(result, dict)
        assert '3R' in result
        assert '2G' in result

    def test_sparkline_series_length(self, sample_df, sample_detections):
        """Test that each pattern has the correct series length."""
        horizon = 5
        result = pattern_sparkline_series(sample_df, sample_detections, horizon=horizon)

        for _, series in result.items():
            assert len(series) == horizon

    def test_sparkline_series_values_are_floats(self, sample_df, sample_detections):
        """Test that all series values are floats."""
        result = pattern_sparkline_series(sample_df, sample_detections, horizon=2)

        for _, series in result.items():
            for val in series:
                assert isinstance(val, float)

    def test_sparkline_series_empty_detections(self, sample_df):
        """Test with empty detections."""
        result = pattern_sparkline_series(sample_df, [], horizon=3)
        assert result == {}

    def test_sparkline_series_single_pattern(self, sample_df):
        """Test with single pattern detection."""
        detections = [{'pattern': 'SINGLE', 'index': 0}]
        result = pattern_sparkline_series(sample_df, detections, horizon=2)

        assert 'SINGLE' in result
        assert len(result['SINGLE']) == 2

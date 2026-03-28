"""Tests for sequential colour-pattern functions in patterns.py.

Covers: parse_sequence, symbol_sequence, match_named_token,
        find_sequence_occurrences, sequence_length,
        _run_length_encode, discover_color_sequences.
"""
from __future__ import annotations

import pandas as pd

from candle_patterns.patterns import (
    parse_sequence,
    symbol_sequence,
    match_named_token,
    find_sequence_occurrences,
    sequence_length,
    _run_length_encode,
    discover_color_sequences,
    find_wildcard_sequence,
    what_comes_next,
    sequence_outcome_stats,
    count_followup_pattern,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candles(colours: str, base_open: float = 100.0) -> pd.DataFrame:
    """Build a tiny DataFrame from a colour string like 'RRGGRD'.

    R = red (close < open), G = green (close > open), D = doji (close == open).
    """
    rows = []
    for i, c in enumerate(colours):
        o = base_open + i
        if c == "R":
            rows.append({"timestamp": f"2025-01-{i+1:02d}", "open": o + 2, "high": o + 3, "low": o - 1, "close": o, "volume": 100})
        elif c == "G":
            rows.append({"timestamp": f"2025-01-{i+1:02d}", "open": o, "high": o + 3, "low": o - 1, "close": o + 2, "volume": 100})
        else:  # Doji  (open == close, but body_size relative to range matters)
            rows.append({"timestamp": f"2025-01-{i+1:02d}", "open": o, "high": o + 5, "low": o - 5, "close": o, "volume": 100})
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ---------------------------------------------------------------------------
# parse_sequence
# ---------------------------------------------------------------------------

class TestParseSequence:
    def test_simple_two_tokens(self):
        tokens = parse_sequence("3R -> 2G")
        assert tokens == [(3, "R"), (2, "G")]

    def test_single_token(self):
        tokens = parse_sequence("5G")
        assert tokens == [(5, "G")]

    def test_named_token_doji(self):
        tokens = parse_sequence("2R -> Doji -> 1G")
        assert tokens == [(2, "R"), (1, "Doji"), (1, "G")]

    def test_alternating_sequence(self):
        tokens = parse_sequence("1R -> 1G -> 1R -> 1G")
        assert len(tokens) == 4
        assert tokens[0] == (1, "R")
        assert tokens[3] == (1, "G")

    def test_case_insensitive(self):
        tokens = parse_sequence("2r -> 3g")
        assert tokens == [(2, "R"), (3, "G")]

    def test_arrow_variants(self):
        # '>' separator
        tokens = parse_sequence("2R > 2G")
        assert tokens == [(2, "R"), (2, "G")]


# ---------------------------------------------------------------------------
# sequence_length
# ---------------------------------------------------------------------------

class TestSequenceLength:
    def test_simple(self):
        assert sequence_length("3R -> 2G") == 5

    def test_with_named_token(self):
        assert sequence_length("2R -> Doji -> 3G") == 6

    def test_single_token(self):
        assert sequence_length("1R") == 1

    def test_long_sequence(self):
        assert sequence_length("5R -> 5G") == 10


# ---------------------------------------------------------------------------
# _run_length_encode
# ---------------------------------------------------------------------------

class TestRunLengthEncode:
    def test_basic(self):
        assert _run_length_encode(("R", "R", "R", "G", "G")) == "3R -> 2G"

    def test_single(self):
        assert _run_length_encode(("G",)) == "1G"

    def test_alternating(self):
        assert _run_length_encode(("R", "G", "R", "G")) == "1R -> 1G -> 1R -> 1G"

    def test_doji_token(self):
        assert _run_length_encode(("R", "Doji", "G")) == "1R -> Doji -> 1G"

    def test_empty(self):
        assert _run_length_encode(()) == ""


# ---------------------------------------------------------------------------
# symbol_sequence
# ---------------------------------------------------------------------------

class TestSymbolSequence:
    def test_red_green(self):
        df = _make_candles("RRG")
        syms = symbol_sequence(df)
        assert syms == ["R", "R", "G"]

    def test_with_doji(self):
        df = _make_candles("RDG")
        syms = symbol_sequence(df)
        assert syms[0] == "R"
        assert syms[1] == "Doji"
        assert syms[2] == "G"

    def test_all_green(self):
        df = _make_candles("GGGG")
        syms = symbol_sequence(df)
        assert all(s == "G" for s in syms)


# ---------------------------------------------------------------------------
# find_sequence_occurrences
# ---------------------------------------------------------------------------

class TestFindSequenceOccurrences:
    def test_simple_match(self):
        df = _make_candles("RRRGG")
        ends = find_sequence_occurrences(df, "3R -> 2G")
        assert len(ends) == 1
        assert ends[0] == 4  # last index of the match

    def test_no_match(self):
        df = _make_candles("GGGGG")
        ends = find_sequence_occurrences(df, "2R -> 1G")
        assert ends == []

    def test_multiple_matches(self):
        df = _make_candles("RGRGRG")
        ends = find_sequence_occurrences(df, "1R -> 1G")
        assert len(ends) >= 2

    def test_overlapping_matches(self):
        df = _make_candles("RRRRR")
        ends = find_sequence_occurrences(df, "2R")
        # 5 candles, windows: 0-1, 1-2, 2-3, 3-4 = 4 matches
        assert len(ends) == 4

    def test_full_length_match(self):
        df = _make_candles("RRGGG")
        ends = find_sequence_occurrences(df, "2R -> 3G")
        assert len(ends) == 1
        assert ends[0] == 4


class TestFollowupPatternCount:
    def test_followup_5r_after_3r_3g(self):
        df = _make_candles("RRRGGGRRRGGGG")  # 3R->3G occurs twice, first followed by 2R (not full5), second followed by 5G
        stats = count_followup_pattern(df, "3R -> 3G", "5R", 5)
        assert stats["total_matches"] == 2
        assert stats["followup_success"] == 0
        assert stats["followup_rate"] == 0.0

    def test_followup_5g_success(self):
        df = _make_candles("RRRGGGGGGG")  # 3R->3G at idx 0-5, then 5G at 6-10 is not enough (index range ends)
        stats = count_followup_pattern(df, "3R -> 3G", "5G", 5)
        assert stats["total_matches"] == 1
        assert stats["followup_success"] == 0


# ---------------------------------------------------------------------------
# discover_color_sequences
# ---------------------------------------------------------------------------

class TestDiscoverColorSequences:
    def test_returns_list_of_dicts(self):
        df = _make_candles("RRRGGRRRGGRRRGG")
        results = discover_color_sequences(df, min_len=3, max_len=5, top_k=5)
        assert isinstance(results, list)
        for r in results:
            assert "sequence" in r
            assert "count" in r
            assert "length" in r
            assert "support" in r

    def test_discovers_repeated_pattern(self):
        # RRGG repeated three times → "2R -> 2G" should be frequent
        df = _make_candles("RRGGRRGGRRGG")
        results = discover_color_sequences(df, min_len=3, max_len=5, top_k=10)
        seqs = [r["sequence"] for r in results]
        # At least one sequence containing R and G should be found
        assert len(seqs) > 0

    def test_top_k_limit(self):
        df = _make_candles("RGRGRGRGRGRGRGRG")
        results = discover_color_sequences(df, min_len=3, max_len=6, top_k=3)
        assert len(results) <= 3

    def test_empty_data(self):
        df = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
        results = discover_color_sequences(df, min_len=3, max_len=5, top_k=5)
        assert results == []

    def test_support_range(self):
        df = _make_candles("RRGGRRGGRRGG")
        results = discover_color_sequences(df, min_len=3, max_len=5, top_k=10)
        for r in results:
            assert 0 <= r["support"] <= 1.0


# ---------------------------------------------------------------------------
# match_named_token
# ---------------------------------------------------------------------------

class TestMatchNamedToken:
    def test_doji_match(self):
        df = _make_candles("D")
        assert match_named_token(df, 0, "Doji") is True

    def test_doji_no_match(self):
        df = _make_candles("R")
        assert match_named_token(df, 0, "Doji") is False

    def test_unknown_token_returns_false(self):
        df = _make_candles("G")
        assert match_named_token(df, 0, "UnknownPattern") is False


# ---------------------------------------------------------------------------
# find_wildcard_sequence
# ---------------------------------------------------------------------------

class TestFindWildcardSequence:
    def test_simple_wildcard(self):
        df = _make_candles("RRGGRR")
        # 2R -> * -> 2R  should find the match with * = GG (span 2)
        results = find_wildcard_sequence(df, "2R -> * -> 2R", wildcard_min=1, wildcard_max=3)
        assert len(results) >= 1
        assert results[0]["start_idx"] == 0
        assert results[0]["end_idx"] == 5

    def test_no_wildcard_in_string(self):
        df = _make_candles("RRRGG")
        results = find_wildcard_sequence(df, "3R -> 2G")
        assert len(results) == 1

    def test_wildcard_no_match(self):
        df = _make_candles("GGGGG")
        results = find_wildcard_sequence(df, "2R -> * -> 2R", wildcard_min=1, wildcard_max=3)
        assert results == []

    def test_wildcard_multiple_matches(self):
        df = _make_candles("RRGRRRGRR")
        results = find_wildcard_sequence(df, "2R -> * -> 2R", wildcard_min=1, wildcard_max=2)
        assert len(results) >= 1


# ---------------------------------------------------------------------------
# what_comes_next
# ---------------------------------------------------------------------------

class TestWhatComesNext:
    def test_basic_prediction(self):
        df = _make_candles("RRGGGRRGGG")
        result = what_comes_next(df, "2R", lookahead=2)
        assert "total_occurrences" in result
        assert "distribution" in result
        assert "most_likely_next" in result
        assert result["total_occurrences"] >= 1
        assert len(result["distribution"]) == 2

    def test_no_occurrences(self):
        df = _make_candles("GGGGG")
        result = what_comes_next(df, "3R", lookahead=2)
        assert result["total_occurrences"] == 0

    def test_distribution_sums(self):
        df = _make_candles("RRGGRRGGRR")
        result = what_comes_next(df, "2R", lookahead=1)
        if result["total_occurrences"] > 0:
            d = result["distribution"][0]
            total = d["R"] + d["G"] + d["Doji"]
            assert total > 0
            assert abs(d["R_pct"] + d["G_pct"] + d["Doji_pct"] - 1.0) < 0.01


# ---------------------------------------------------------------------------
# sequence_outcome_stats
# ---------------------------------------------------------------------------

class TestSequenceOutcomeStats:
    def test_basic_stats(self):
        df = _make_candles("RRRGGGGGRR")
        result = sequence_outcome_stats(df, "3R", hold_candles=3)
        assert "sequence" in result
        assert result["sequence"] == "3R"
        assert "avg_return_pct" in result
        assert "win_rate" in result
        assert "occurrences" in result

    def test_no_occurrences_stats(self):
        df = _make_candles("GGGGG")
        result = sequence_outcome_stats(df, "5R", hold_candles=3)
        assert result["occurrences"] == 0
        assert result["avg_return_pct"] == 0
        assert result["win_rate"] == 0

    def test_win_rate_range(self):
        df = _make_candles("RRGGRRGGRRGG")
        result = sequence_outcome_stats(df, "2R", hold_candles=2)
        assert 0 <= result["win_rate"] <= 1.0

    def test_all_fields_present(self):
        df = _make_candles("RRGGRRGGRR")
        result = sequence_outcome_stats(df, "2R", hold_candles=2)
        expected_keys = [
            "sequence", "occurrences", "avg_return_pct", "median_return_pct",
            "win_rate", "max_gain_pct", "max_loss_pct", "avg_high_pct", "avg_low_pct",
        ]
        for k in expected_keys:
            assert k in result, f"Missing key: {k}"

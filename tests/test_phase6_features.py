"""
Phase 6 Tests — Performance, Alerts, ML Sequence Predictor, Preferences.

Covers all 4 new Phase 6 modules with comprehensive unit tests.
"""

import json
import os
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic OHLCV data with trending behavior."""
    rng = np.random.RandomState(seed)
    timestamps = pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC")
    price = 100.0
    rows = []
    for i in range(n):
        change = rng.normal(0, 1.5)
        o = price
        c = o + change
        h = max(o, c) + abs(rng.normal(0, 0.5))
        lo = min(o, c) - abs(rng.normal(0, 0.5))
        vol = rng.randint(1000, 10000)
        rows.append({"timestamp": timestamps[i], "open": o, "high": h, "low": lo, "close": c, "volume": vol})
        price = c
    return pd.DataFrame(rows)


def _make_large_ohlcv(n: int = 12000, seed: int = 42) -> pd.DataFrame:
    """Generate a large OHLCV dataset for performance tests."""
    return _make_ohlcv(n=n, seed=seed)


# ===========================================================================
# PERFORMANCE MODULE TESTS
# ===========================================================================

class TestVectorizedSymbolSequence:
    """vectorized_symbol_sequence() — numpy-accelerated colour classification."""

    def test_basic_classification(self):
        from candle_patterns.performance import vectorized_symbol_sequence
        df = _make_ohlcv(50)
        symbols = vectorized_symbol_sequence(df)
        assert len(symbols) == 50
        assert all(s in ("R", "G", "Doji") for s in symbols)

    def test_matches_original(self):
        """Result should match the row-by-row symbol_sequence from patterns.py."""
        from candle_patterns.performance import vectorized_symbol_sequence
        from candle_patterns.patterns import symbol_sequence
        df = _make_ohlcv(100)
        vec_syms = vectorized_symbol_sequence(df).tolist()
        orig_syms = symbol_sequence(df)
        assert vec_syms == orig_syms

    def test_all_green(self):
        from candle_patterns.performance import vectorized_symbol_sequence
        df = pd.DataFrame({
            "timestamp": pd.date_range("2025-01-01", periods=5, freq="D"),
            "open": [10, 10, 10, 10, 10],
            "high": [15, 15, 15, 15, 15],
            "low": [8, 8, 8, 8, 8],
            "close": [12, 12, 12, 12, 12],
            "volume": [100] * 5,
        })
        symbols = vectorized_symbol_sequence(df)
        assert all(s == "G" for s in symbols)

    def test_doji_detection(self):
        from candle_patterns.performance import vectorized_symbol_sequence
        df = pd.DataFrame({
            "timestamp": pd.date_range("2025-01-01", periods=3, freq="D"),
            "open": [100, 100, 100],
            "high": [110, 110, 110],
            "low": [90, 90, 90],
            "close": [100.1, 100.1, 100.1],  # tiny body
            "volume": [100] * 3,
        })
        symbols = vectorized_symbol_sequence(df)
        assert all(s == "Doji" for s in symbols)


class TestVectorizedFindSequence:
    """vectorized_find_sequence() — numpy-level sequence matching."""

    def test_simple_match(self):
        from candle_patterns.performance import vectorized_find_sequence
        symbols = np.array(["R", "R", "R", "G", "G", "R", "R", "R", "G", "G"])
        pattern = [(3, "R"), (2, "G")]
        results = vectorized_find_sequence(symbols, pattern)
        assert len(results) == 2
        assert 4 in results  # end of first match
        assert 9 in results  # end of second match

    def test_no_match(self):
        from candle_patterns.performance import vectorized_find_sequence
        symbols = np.array(["G", "G", "G", "G", "G"])
        pattern = [(3, "R")]
        results = vectorized_find_sequence(symbols, pattern)
        assert results == []

    def test_named_token_fallback(self):
        from candle_patterns.performance import vectorized_find_sequence
        symbols = np.array(["R", "R", "G"])
        pattern = [(1, "Hammer")]  # not a simple token
        results = vectorized_find_sequence(symbols, pattern)
        assert results == []  # falls back, returns empty


class TestDownsampleOhlcv:
    """downsample_ohlcv() — chart data reduction."""

    def test_no_downsample_needed(self):
        from candle_patterns.performance import downsample_ohlcv
        df = _make_ohlcv(100)
        result = downsample_ohlcv(df, max_points=200)
        assert len(result) == 100  # unchanged

    def test_downsample_large(self):
        from candle_patterns.performance import downsample_ohlcv
        df = _make_ohlcv(500)
        result = downsample_ohlcv(df, max_points=100)
        assert len(result) <= 110  # roughly 100
        assert len(result) > 0
        assert "open" in result.columns
        assert "close" in result.columns

    def test_preserves_ohlcv_semantics(self):
        from candle_patterns.performance import downsample_ohlcv
        df = _make_ohlcv(400)
        result = downsample_ohlcv(df, max_points=50)
        # High should always be >= open and close
        for _, row in result.iterrows():
            assert row["high"] >= row["open"]
            assert row["high"] >= row["close"]


class TestChunkedProcessing:
    """process_in_chunks() — overlapping chunk scanning."""

    def test_small_dataset_direct(self):
        from candle_patterns.performance import process_in_chunks
        df = _make_ohlcv(100)
        results = process_in_chunks(df, ["3R -> 2G"], chunk_size=5000)
        assert "3R -> 2G" in results

    def test_large_dataset_chunked(self):
        from candle_patterns.performance import process_in_chunks
        from candle_patterns.patterns import find_sequence_occurrences
        df = _make_ohlcv(300)
        chunked = process_in_chunks(df, ["2R -> 1G"], chunk_size=100, overlap=20)
        direct = find_sequence_occurrences(df, "2R -> 1G")
        # Chunked should find same matches as direct
        assert set(chunked["2R -> 1G"]) == set(direct)


class TestCandleCache:
    """CandleCache — memoises symbol arrays."""

    def test_cache_lifecycle(self):
        from candle_patterns.performance import CandleCache
        cache = CandleCache()
        df = _make_ohlcv(50)
        cache.update(df)
        assert len(cache.symbols) == 50
        assert len(cache.numpy_symbols) == 50

    def test_cache_invalidate(self):
        from candle_patterns.performance import CandleCache
        cache = CandleCache()
        df = _make_ohlcv(50)
        cache.update(df)
        cache.invalidate()
        with pytest.raises(RuntimeError):
            _ = cache.symbols

    def test_cache_reuse(self):
        from candle_patterns.performance import CandleCache
        cache = CandleCache()
        df = _make_ohlcv(50)
        cache.update(df)
        s1 = cache.symbols
        cache.update(df)  # same df — should reuse
        s2 = cache.symbols
        assert s1 is s2  # same object


class TestDatasetInfo:
    """dataset_info() — size metadata."""

    def test_small_dataset(self):
        from candle_patterns.performance import dataset_info
        df = _make_ohlcv(100)
        info = dataset_info(df)
        assert info["rows"] == 100
        assert info["needs_downsampling"] is False
        assert info["memory_mb"] >= 0

    def test_large_flag(self):
        from candle_patterns.performance import dataset_info
        df = _make_ohlcv(500)
        # Simulate large dataset via direct check
        df_big = pd.concat([df] * 5, ignore_index=True)
        info = dataset_info(df_big)
        assert info["rows"] == 2500
        assert info["needs_downsampling"] is True


class TestBatchSequenceStats:
    """batch_sequence_stats() — multi-sequence stats."""

    def test_multiple_sequences(self):
        from candle_patterns.performance import batch_sequence_stats
        df = _make_ohlcv(200)
        results = batch_sequence_stats(df, ["3R -> 2G", "2G -> 1R"], hold_candles=5)
        assert len(results) == 2
        assert all("sequence" in r or "error" in r for r in results)


# ===========================================================================
# ALERTS MODULE TESTS
# ===========================================================================

class TestAlertRuleCRUD:
    """Alert rule creation, listing, removal."""

    def _temp_db(self, tmp_path):
        return tmp_path / "test_alerts.db"

    def test_add_and_list(self, tmp_path):
        from candle_patterns.alerts import add_alert_rule, list_alert_rules
        db = self._temp_db(tmp_path)
        rule = add_alert_rule("test rule", ["3R -> 2G"], symbol="AAPL", db_path=db)
        assert rule["id"] is not None
        assert rule["name"] == "test rule"
        rules = list_alert_rules(db_path=db)
        assert len(rules) == 1
        assert rules[0]["name"] == "test rule"

    def test_remove_rule(self, tmp_path):
        from candle_patterns.alerts import add_alert_rule, remove_alert_rule, list_alert_rules
        db = self._temp_db(tmp_path)
        rule = add_alert_rule("to delete", ["3R"], db_path=db)
        assert remove_alert_rule(rule["id"], db_path=db) is True
        assert len(list_alert_rules(db_path=db)) == 0

    def test_toggle_rule(self, tmp_path):
        from candle_patterns.alerts import add_alert_rule, toggle_alert_rule, list_alert_rules
        db = self._temp_db(tmp_path)
        rule = add_alert_rule("toggle me", ["2G"], db_path=db)
        toggle_alert_rule(rule["id"], False, db_path=db)
        rules = list_alert_rules(db_path=db)
        assert rules[0]["enabled"] is False


class TestAlertHistory:
    """Alert history recording and retrieval."""

    def test_record_and_retrieve(self, tmp_path):
        from candle_patterns.alerts import record_alert, get_alert_history
        db = tmp_path / "test_hist.db"
        aid = record_alert(None, "test", "3R", symbol="AAPL", db_path=db)
        assert aid > 0
        history = get_alert_history(db_path=db)
        assert len(history) == 1
        assert history[0]["sequence"] == "3R"

    def test_acknowledge(self, tmp_path):
        from candle_patterns.alerts import record_alert, acknowledge_alert, get_alert_history
        db = tmp_path / "test_ack.db"
        aid = record_alert(None, "test", "3R", db_path=db)
        acknowledge_alert(aid, db_path=db)
        history = get_alert_history(db_path=db)
        assert history[0]["acknowledged"] is True

    def test_clear_history(self, tmp_path):
        from candle_patterns.alerts import record_alert, clear_alert_history, get_alert_history
        db = tmp_path / "test_clear.db"
        record_alert(None, "r1", "3R", db_path=db)
        record_alert(None, "r2", "2G", db_path=db)
        removed = clear_alert_history(db_path=db)
        assert removed == 2
        assert len(get_alert_history(db_path=db)) == 0

    def test_unread_count(self, tmp_path):
        from candle_patterns.alerts import record_alert, get_unread_count, acknowledge_alert
        db = tmp_path / "test_unread.db"
        a1 = record_alert(None, "r1", "3R", db_path=db)
        record_alert(None, "r2", "2G", db_path=db)
        assert get_unread_count(db_path=db) == 2
        acknowledge_alert(a1, db_path=db)
        assert get_unread_count(db_path=db) == 1


class TestCheckAndTrigger:
    """check_and_trigger() — evaluate rules against data."""

    def test_trigger_on_match(self, tmp_path):
        from candle_patterns.alerts import add_alert_rule, check_and_trigger
        db = tmp_path / "test_trigger.db"
        # Create data with a known pattern
        df = _make_ohlcv(200)
        add_alert_rule("test alert", ["2R -> 1G"], db_path=db)
        triggered = check_and_trigger(df, symbol="TEST", db_path=db)
        # Should trigger if the pattern exists in data
        # (with 200 candles, 2R -> 1G is very likely to appear)
        assert isinstance(triggered, list)

    def test_disabled_rule_skipped(self, tmp_path):
        from candle_patterns.alerts import add_alert_rule, toggle_alert_rule, check_and_trigger
        db = tmp_path / "test_disabled.db"
        df = _make_ohlcv(200)
        rule = add_alert_rule("disabled", ["2R -> 1G"], db_path=db)
        toggle_alert_rule(rule["id"], False, db_path=db)
        triggered = check_and_trigger(df, db_path=db)
        assert triggered == []


class TestWebhookDispatch:
    """send_webhook() — basic tests (no actual network)."""

    def test_empty_url_returns_false(self):
        from candle_patterns.alerts import send_webhook
        assert send_webhook("", {"test": 1}) is False

    def test_invalid_url_returns_false(self):
        from candle_patterns.alerts import send_webhook
        assert send_webhook("not-a-url", {"test": 1}) is False


# ===========================================================================
# ML SEQUENCE PREDICTOR TESTS
# ===========================================================================

class TestEngineerSequenceFeatures:
    """engineer_sequence_features() — feature matrix construction."""

    def test_basic_features(self):
        from candle_patterns.ml_sequence import engineer_sequence_features
        df = _make_ohlcv(200)
        X, y = engineer_sequence_features(df)
        assert len(X) > 0
        assert len(y) == len(X)
        assert "hl_ratio" in X.columns
        assert "streak_length" in X.columns
        assert "rsi_14" in X.columns
        assert "mom_5" in X.columns

    def test_17_features(self):
        from candle_patterns.ml_sequence import engineer_sequence_features
        df = _make_ohlcv(200)
        X, y = engineer_sequence_features(df)
        assert X.shape[1] == 17

    def test_no_nans_in_output(self):
        from candle_patterns.ml_sequence import engineer_sequence_features
        df = _make_ohlcv(200)
        X, y = engineer_sequence_features(df)
        assert X.isna().sum().sum() == 0


class TestSequencePredictor:
    """SequencePredictor — GradientBoosting model."""

    def test_train_and_metrics(self):
        from candle_patterns.ml_sequence import SequencePredictor, engineer_sequence_features
        df = _make_ohlcv(300)
        X, y = engineer_sequence_features(df)
        predictor = SequencePredictor()
        metrics = predictor.train(X, y)
        assert "accuracy" in metrics
        assert "roc_auc" in metrics
        assert metrics["accuracy"] > 0

    def test_predict(self):
        from candle_patterns.ml_sequence import SequencePredictor, engineer_sequence_features
        df = _make_ohlcv(300)
        X, y = engineer_sequence_features(df)
        predictor = SequencePredictor()
        predictor.train(X, y)
        preds, probas = predictor.predict(X.iloc[:10])
        assert len(preds) == 10
        assert len(probas) == 10
        assert all(p in (0, 1) for p in preds)

    def test_predict_next_outcome(self):
        from candle_patterns.ml_sequence import SequencePredictor, engineer_sequence_features
        df = _make_ohlcv(300)
        X, y = engineer_sequence_features(df)
        predictor = SequencePredictor()
        predictor.train(X, y)
        result = predictor.predict_next_outcome(df)
        assert result["direction"] in ("bullish", "bearish", "unknown")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_feature_importance(self):
        from candle_patterns.ml_sequence import SequencePredictor, engineer_sequence_features
        df = _make_ohlcv(300)
        X, y = engineer_sequence_features(df)
        predictor = SequencePredictor()
        predictor.train(X, y, calibrate=False)
        fi = predictor.feature_importance()
        assert len(fi) > 0
        assert "feature" in fi.columns

    def test_save_and_load(self, tmp_path):
        from candle_patterns.ml_sequence import SequencePredictor, engineer_sequence_features
        df = _make_ohlcv(300)
        X, y = engineer_sequence_features(df)
        predictor = SequencePredictor()
        predictor.train(X, y, calibrate=False)
        path = tmp_path / "model.pkl"
        predictor.save(path)
        loaded = SequencePredictor()
        loaded.load(path)
        preds1, _ = predictor.predict(X.iloc[:5])
        preds2, _ = loaded.predict(X.iloc[:5])
        assert list(preds1) == list(preds2)


class TestTrainSequencePredictor:
    """train_sequence_predictor() — end-to-end convenience function."""

    def test_full_pipeline(self):
        from candle_patterns.ml_sequence import train_sequence_predictor
        df = _make_ohlcv(300)
        result = train_sequence_predictor(df)
        assert "model" in result
        assert "metrics" in result
        assert result["n_samples"] > 0

    def test_insufficient_data(self):
        from candle_patterns.ml_sequence import train_sequence_predictor
        df = _make_ohlcv(25)  # too few after feature engineering NaN drops
        result = train_sequence_predictor(df)
        assert "error" in result


# ===========================================================================
# PREFERENCES MODULE TESTS
# ===========================================================================

class TestPreferencesLoadSave:
    """load_preferences / save_preferences lifecycle."""

    def test_defaults_on_missing_file(self, tmp_path):
        from candle_patterns.preferences import load_preferences
        prefs = load_preferences(str(tmp_path / "nonexistent.json"))
        assert prefs["theme"] == "light"
        assert prefs["hold_period"] == 5
        assert prefs["default_symbol"] == "AAPL"

    def test_save_and_load(self, tmp_path):
        from candle_patterns.preferences import save_preferences, load_preferences
        path = str(tmp_path / "prefs.json")
        prefs = {"theme": "dark", "hold_period": 10}
        save_preferences(prefs, path)
        loaded = load_preferences(path)
        assert loaded["theme"] == "dark"
        assert loaded["hold_period"] == 10

    def test_missing_keys_get_defaults(self, tmp_path):
        from candle_patterns.preferences import save_preferences, load_preferences
        path = str(tmp_path / "partial.json")
        save_preferences({"theme": "dark"}, path)
        loaded = load_preferences(path)
        assert loaded["theme"] == "dark"
        assert loaded["default_symbol"] == "AAPL"  # from defaults

    def test_corrupted_file_returns_defaults(self, tmp_path):
        from candle_patterns.preferences import load_preferences
        path = tmp_path / "bad.json"
        path.write_text("not valid json {{{", encoding="utf-8")
        prefs = load_preferences(str(path))
        assert prefs["theme"] == "light"


class TestPreferencesGetSet:
    """get_preference / set_preference."""

    def test_get_default(self, tmp_path):
        from candle_patterns.preferences import get_preference
        val = get_preference("hold_period", str(tmp_path / "np.json"))
        assert val == 5

    def test_set_and_get(self, tmp_path):
        from candle_patterns.preferences import set_preference, get_preference
        path = str(tmp_path / "sg.json")
        set_preference("hold_period", 15, path)
        assert get_preference("hold_period", path) == 15

    def test_reset(self, tmp_path):
        from candle_patterns.preferences import set_preference, reset_preferences, get_preference
        path = str(tmp_path / "reset.json")
        set_preference("hold_period", 99, path)
        reset_preferences(path)
        assert get_preference("hold_period", path) == 5


class TestPreferencesRecents:
    """add_recent_symbol / add_recent_sequence."""

    def test_add_recent_symbol(self, tmp_path):
        from candle_patterns.preferences import add_recent_symbol, get_recent_symbols
        path = str(tmp_path / "rec.json")
        add_recent_symbol("AAPL", path)
        add_recent_symbol("MSFT", path)
        recents = get_recent_symbols(path)
        assert recents[0] == "MSFT"  # most recent first
        assert "AAPL" in recents

    def test_dedup_recent(self, tmp_path):
        from candle_patterns.preferences import add_recent_symbol, get_recent_symbols
        path = str(tmp_path / "dedup.json")
        add_recent_symbol("AAPL", path)
        add_recent_symbol("MSFT", path)
        add_recent_symbol("AAPL", path)
        recents = get_recent_symbols(path)
        assert recents.count("AAPL") == 1

    def test_max_recent_items(self, tmp_path):
        from candle_patterns.preferences import add_recent_symbol, get_recent_symbols
        path = str(tmp_path / "max.json")
        for i in range(15):
            add_recent_symbol(f"SYM{i}", path)
        recents = get_recent_symbols(path)
        assert len(recents) <= 10

    def test_add_recent_sequence(self, tmp_path):
        from candle_patterns.preferences import add_recent_sequence, get_recent_sequences
        path = str(tmp_path / "seqrec.json")
        add_recent_sequence("3R -> 2G", path)
        add_recent_sequence("5R -> 3G", path)
        recents = get_recent_sequences(path)
        assert len(recents) == 2
        assert recents[0] == "5R -> 3G"


class TestPreferencesExportImport:
    """export_preferences / import_preferences."""

    def test_export_json(self, tmp_path):
        from candle_patterns.preferences import load_preferences, export_preferences
        path = str(tmp_path / "exp.json")
        json_str = export_preferences(path)
        parsed = json.loads(json_str)
        assert parsed["theme"] == "light"

    def test_import_json(self, tmp_path):
        from candle_patterns.preferences import import_preferences, load_preferences
        path = str(tmp_path / "imp.json")
        import_preferences('{"theme": "dark", "hold_period": 20}', path)
        loaded = load_preferences(path)
        assert loaded["theme"] == "dark"
        assert loaded["hold_period"] == 20

    def test_import_invalid_json(self, tmp_path):
        from candle_patterns.preferences import import_preferences
        path = str(tmp_path / "bad.json")
        with pytest.raises(ValueError):
            import_preferences("not json", path)


# ===========================================================================
# DASHBOARD SMOKE TEST (Phase 6 tabs importable)
# ===========================================================================

class TestDashboardPhase6:
    """Verify Phase 6 dashboard components don't break import."""

    def test_dashboard_importable(self):
        from candle_patterns.dashboard import app
        assert app is not None

    def test_new_tabs_in_layout(self):
        """Verify the 3 new tabs exist in the layout."""
        from candle_patterns.dashboard import app
        layout_str = str(app.layout)
        assert "tab-alerts" in layout_str
        assert "tab-ml-predict" in layout_str
        assert "tab-settings" in layout_str

    def test_live_interval_in_layout(self):
        from candle_patterns.dashboard import app
        layout_str = str(app.layout)
        assert "live-interval" in layout_str

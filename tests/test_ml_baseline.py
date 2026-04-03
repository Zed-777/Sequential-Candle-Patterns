"""
Tests for the ML baseline module.
"""

import pytest
import pandas as pd
import numpy as np
from candle_patterns.ml_baseline import PatternMLModel, train_baseline_model  # type: ignore


@pytest.fixture
def sample_ohlc_data():
    """Create sample OHLC data for testing."""
    dates = pd.date_range("2024-01-01", periods=100, freq="1h", tz="UTC")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(100) * 0.5)

    return pd.DataFrame(
        {
            "timestamp": dates,
            "open": close + np.random.randn(100) * 0.2,
            "high": close + np.abs(np.random.randn(100) * 0.5),
            "low": close - np.abs(np.random.randn(100) * 0.5),
            "close": close,
            "volume": np.random.randint(1000, 10000, 100),
        }
    )


@pytest.fixture
def sample_patterns():
    """Create sample detected patterns."""
    return [
        {"timestamp": pd.Timestamp("2024-01-01 05:00:00", tz="UTC"), "pattern": "Doji"},
        {
            "timestamp": pd.Timestamp("2024-01-01 15:00:00", tz="UTC"),
            "pattern": "Hammer",
        },
        {
            "timestamp": pd.Timestamp("2024-01-02 08:00:00", tz="UTC"),
            "pattern": "Engulfing",
        },
    ]


def test_model_initialization():
    """Test that model initializes correctly."""
    model = PatternMLModel()
    assert model.model is None
    assert model.scaler is None
    assert model.feature_names is None


def test_feature_engineering(sample_ohlc_data, sample_patterns):
    """Test feature engineering."""
    model = PatternMLModel()
    X, y = model.engineer_features(sample_ohlc_data, sample_patterns)

    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)
    assert len(X) > 0
    assert len(X) == len(y)
    assert X.shape[1] >= 4  # At least 4 features
    assert set(y.unique()).issubset({0, 1})  # Binary labels


def test_model_training(sample_ohlc_data, sample_patterns):
    """Test model training."""
    model = PatternMLModel()
    X, y = model.engineer_features(sample_ohlc_data, sample_patterns)

    metrics = model.train(X, y, test_size=0.3)

    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert 0 <= metrics["accuracy"] <= 1
    assert model.model is not None
    assert model.scaler is not None


def test_cross_validation(sample_ohlc_data, sample_patterns):
    """Test time series cross-validation."""
    model = PatternMLModel()
    X, y = model.engineer_features(sample_ohlc_data, sample_patterns)

    cv_results = model.cross_validate(X, y, n_splits=3)

    assert "accuracy" in cv_results
    assert "f1" in cv_results
    assert "roc_auc" in cv_results

    for metric, (mean, std) in cv_results.items():
        assert 0 <= mean <= 1
        assert std >= 0


def test_feature_importance(sample_ohlc_data, sample_patterns):
    """Test feature importance extraction."""
    model = PatternMLModel()
    X, y = model.engineer_features(sample_ohlc_data, sample_patterns)
    model.train(X, y)

    importance_df = model.feature_importance()

    assert isinstance(importance_df, pd.DataFrame)
    assert "feature" in importance_df.columns
    assert "importance" in importance_df.columns
    assert len(importance_df) == len(model.feature_names)
    assert importance_df["importance"].sum() > 0


def test_predictions(sample_ohlc_data, sample_patterns):
    """Test model predictions."""
    model = PatternMLModel()
    X, y = model.engineer_features(sample_ohlc_data, sample_patterns)
    model.train(X, y)

    # Test on a subset of training data
    X_test = X.iloc[:10]
    predictions, probabilities = model.predict(X_test)

    assert len(predictions) == len(X_test)
    assert len(probabilities) == len(X_test)
    assert set(predictions).issubset({0, 1})
    assert np.all((probabilities >= 0) & (probabilities <= 1))


def test_model_persistence(tmp_path, sample_ohlc_data, sample_patterns):
    """Test model save and load."""
    model1 = PatternMLModel()
    X, y = model1.engineer_features(sample_ohlc_data, sample_patterns)
    model1.train(X, y)

    # Save
    model_path = tmp_path / "test_model.pkl"
    model1.save(model_path)
    assert model_path.exists()

    # Load
    model2 = PatternMLModel()
    model2.load(model_path)

    # Verify loaded model works
    predictions1, probs1 = model1.predict(X.iloc[:5])
    predictions2, probs2 = model2.predict(X.iloc[:5])

    assert np.array_equal(predictions1, predictions2)
    assert np.allclose(probs1, probs2)


def test_train_baseline_model(sample_ohlc_data, sample_patterns):
    """Test the baseline model training function."""
    results = train_baseline_model(sample_ohlc_data, sample_patterns)

    assert "model" in results
    assert "train_metrics" in results
    assert "cv_results" in results
    assert "feature_importance" in results
    assert results["n_samples"] > 0
    assert results["n_features"] > 0


def test_insufficient_data():
    """Test handling of insufficient data."""
    # Very small dataset
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=3, freq="1h", tz="UTC"),
            "open": [100, 101, 102],
            "high": [101, 102, 103],
            "low": [99, 100, 101],
            "close": [100.5, 101.5, 102.5],
            "volume": [1000, 1000, 1000],
        }
    )
    patterns = []

    results = train_baseline_model(df, patterns)
    assert "error" in results or results.get("n_samples", 0) < 5

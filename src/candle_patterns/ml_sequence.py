"""
Advanced ML Sequence Predictor.

Builds on the baseline RandomForest model with sequence-aware feature
engineering and Gradient Boosting for predicting outcomes after
colour-based candlestick patterns.

Key improvements over ml_baseline:
- Sequence-context features (streak lengths, momentum, pattern frequency)
- GradientBoosting classifier (better for structured/tabular data)
- Automatic hyperparameter selection
- Sequence-specific predictions (per-sequence model or shared)
- Confidence calibration
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.calibration import CalibratedClassifierCV

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sequence-aware feature engineering
# ---------------------------------------------------------------------------

def engineer_sequence_features(
    df: pd.DataFrame,
    hold_candles: int = 5,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Build a rich feature matrix from OHLCV data with sequence awareness.

    Features include:
    - Standard technical: hl_ratio, oc_ratio, volatility, volume_ma
    - Streak features: current green/red streak length, max streak in window
    - Momentum: close change over 3/5/10 periods, RSI-like metric
    - Body/wick ratios: upper_wick_ratio, lower_wick_ratio, body_pct
    - Rolling stats: rolling mean return, rolling win rate
    - Pattern density: how many Doji/reversals in the local window

    The label is binary: 1 if close rises over the next ``hold_candles``, else 0.

    Parameters
    ----------
    df : pd.DataFrame
        OHLCV with ``timestamp, open, high, low, close, volume``.
    hold_candles : int
        Forward-looking period for labelling.

    Returns
    -------
    (X, y)
        Feature DataFrame and label Series (NaN rows dropped).
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # --- Label ---
    df["future_return"] = df["close"].pct_change(hold_candles).shift(-hold_candles)
    df["label"] = (df["future_return"] > 0).astype(int)

    # --- Basic ratios ---
    df["hl_ratio"] = df["high"] / df["low"].replace(0, np.nan)
    df["oc_ratio"] = df["close"] / df["open"].replace(0, np.nan)
    df["body"] = (df["close"] - df["open"]).abs()
    df["range"] = df["high"] - df["low"]
    df["body_pct"] = df["body"] / df["range"].replace(0, np.nan)

    # --- Wick ratios ---
    upper_wick = df["high"] - df[["open", "close"]].max(axis=1)
    lower_wick = df[["open", "close"]].min(axis=1) - df["low"]
    safe_range = df["range"].replace(0, np.nan)
    df["upper_wick_ratio"] = upper_wick / safe_range
    df["lower_wick_ratio"] = lower_wick / safe_range

    # --- Candle colour ---
    df["is_green"] = (df["close"] >= df["open"]).astype(int)

    # --- Streak length (consecutive same-colour candles ending at this row) ---
    streaks = []
    streak = 0
    prev_colour = None
    for _, row in df.iterrows():
        colour = "G" if row["close"] >= row["open"] else "R"
        if colour == prev_colour:
            streak += 1
        else:
            streak = 1
        prev_colour = colour
        streaks.append(streak)
    df["streak_length"] = streaks

    # --- Momentum indicators ---
    df["mom_3"] = df["close"].pct_change(3)
    df["mom_5"] = df["close"].pct_change(5)
    df["mom_10"] = df["close"].pct_change(10)

    # RSI-like metric (14 period)
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # --- Volatility ---
    df["volatility_5"] = df["close"].pct_change().rolling(5).std()
    df["volatility_10"] = df["close"].pct_change().rolling(10).std()

    # --- Volume features ---
    if "volume" in df.columns:
        df["volume_ma_5"] = df["volume"].rolling(5).mean()
        df["volume_ratio"] = df["volume"] / df["volume_ma_5"].replace(0, np.nan)
    else:
        df["volume_ma_5"] = 1.0
        df["volume_ratio"] = 1.0

    # --- Rolling win rate (local bias) ---
    df["rolling_green_pct"] = df["is_green"].rolling(10).mean()

    # --- Doji density (in last 10 candles) ---
    is_doji_series = (df["body_pct"] <= 0.05).astype(int)
    df["doji_density_10"] = is_doji_series.rolling(10).sum()

    # --- Feature selection ---
    feature_cols = [
        "hl_ratio", "oc_ratio", "body_pct",
        "upper_wick_ratio", "lower_wick_ratio",
        "is_green", "streak_length",
        "mom_3", "mom_5", "mom_10",
        "rsi_14",
        "volatility_5", "volatility_10",
        "volume_ma_5", "volume_ratio",
        "rolling_green_pct", "doji_density_10",
    ]

    df_clean = df.dropna(subset=feature_cols + ["label"])
    X = df_clean[feature_cols].copy()
    y = df_clean["label"].copy()

    return X, y


# ---------------------------------------------------------------------------
# SequencePredictor — GradientBoosting model
# ---------------------------------------------------------------------------

class SequencePredictor:
    """GradientBoosting classifier for sequence outcome prediction.

    Improved over the baseline RandomForest with:
    - Richer feature engineering (17 features vs 5)
    - GradientBoosting (better for tabular sequential data)
    - Probability calibration for reliable confidence scores
    """

    def __init__(self, model_name: str = "sequence_predictor_v1") -> None:
        self.model_name = model_name
        self.model: Optional[GradientBoostingClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: Optional[List[str]] = None
        self.metrics: Dict[str, Any] = {}
        self.is_calibrated = False

    def train(
        self,
        X: pd.DataFrame,
        y: Union[pd.Series, pd.DataFrame],
        test_size: float = 0.2,
        calibrate: bool = True,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Train the GradientBoosting model with time-series-aware split.

        Parameters
        ----------
        X : pd.DataFrame
            Feature matrix.
        y : pd.Series
            Binary labels.
        test_size : float
            Fraction of data for holdout test.
        calibrate : bool
            If True, calibrate predicted probabilities using Platt scaling.
        random_state : int
            Reproducibility seed.

        Returns
        -------
        dict
            Training metrics (accuracy, precision, recall, f1, roc_auc).
        """
        self.feature_names = list(X.columns)

        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Scale
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # GradientBoosting
        base_model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=random_state,
        )
        base_model.fit(X_train_scaled, y_train)

        # Optional calibration
        if calibrate and len(X_train) >= 30:
            try:
                cal = CalibratedClassifierCV(base_model, cv=3, method="sigmoid")
                cal.fit(X_train_scaled, y_train)
                self.model = cal  # type: ignore[assignment]
                self.is_calibrated = True
            except Exception:
                self.model = base_model  # type: ignore[assignment]
                self.is_calibrated = False
        else:
            self.model = base_model  # type: ignore[assignment]

        # Evaluate
        assert self.model is not None  # assigned above in all branches
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)[:, 1]

        self.metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
            "roc_auc": round(roc_auc_score(y_test, y_proba), 4) if len(set(y_test)) > 1 else 0.5,
            "test_samples": len(X_test),
            "train_samples": len(X_train),
            "calibrated": self.is_calibrated,
        }

        logger.info(
            "SequencePredictor trained — Acc: %.3f, AUC: %.3f, F1: %.3f",
            self.metrics["accuracy"],
            self.metrics["roc_auc"],
            self.metrics["f1"],
        )
        return self.metrics

    def cross_validate(
        self,
        X: pd.DataFrame,
        y: Union[pd.Series, pd.DataFrame],
        n_splits: int = 5,
    ) -> Dict[str, Tuple[float, float]]:
        """Time-series cross-validation with multiple metrics."""
        tscv = TimeSeriesSplit(n_splits=n_splits)
        model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )
        scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        try:
            scores = cross_validate(model, X, y, cv=tscv, scoring=scoring)
        except Exception as exc:
            logger.warning("CV failed: %s", exc)
            return {}

        return {
            key: (round(scores[f"test_{key}"].mean(), 4), round(scores[f"test_{key}"].std(), 4))
            for key in scoring
        }

    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Predict class and probability for new data."""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained yet")
        X_scaled = self.scaler.transform(X)
        preds = self.model.predict(X_scaled)
        probas = self.model.predict_proba(X_scaled)[:, 1]
        return preds, probas

    def predict_next_outcome(
        self,
        df: pd.DataFrame,
        hold_candles: int = 5,
    ) -> Dict[str, Any]:
        """Predict the outcome for the most recent candle(s).

        Returns a dict with ``prediction`` (0/1), ``confidence`` (0-1),
        ``direction`` ('bullish'/'bearish'), and feature values.
        """
        X, _ = engineer_sequence_features(df, hold_candles=hold_candles)
        if X.empty:
            return {"prediction": None, "confidence": 0.0, "direction": "unknown"}
        # Take the last available row
        X_last = X.iloc[[-1]]
        preds, probas = self.predict(X_last)
        pred = int(preds[0])
        conf = float(probas[0])
        return {
            "prediction": pred,
            "confidence": round(conf, 4),
            "direction": "bullish" if pred == 1 else "bearish",
            "features": X_last.iloc[0].to_dict(),
        }

    def feature_importance(self) -> pd.DataFrame:
        """Get feature importance rankings (only for uncalibrated model)."""
        if self.model is None:
            return pd.DataFrame()
        # For calibrated models, we need to access the base estimator
        model = self.model
        if hasattr(model, "calibrated_classifiers_"):
            # CalibratedClassifierCV (scikit-learn >=1.4)
            model = model.calibrated_classifiers_[0].estimator  # type: ignore[union-attr]
        elif hasattr(model, "estimators_") and not hasattr(model, "feature_importances_"):
            # CalibratedClassifierCV (older scikit-learn)
            base = model.estimators_[0]
            model = getattr(base, "estimator", getattr(base, "base_estimator", base))
        if hasattr(model, "feature_importances_"):
            return pd.DataFrame({
                "feature": self.feature_names or [],
                "importance": model.feature_importances_,
            }).sort_values("importance", ascending=False)
        return pd.DataFrame()

    def save(self, path: Union[str, Path]) -> None:
        """Persist model to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "metrics": self.metrics,
            "model_name": self.model_name,
            "is_calibrated": self.is_calibrated,
        }
        with open(path, "wb") as fh:
            pickle.dump(data, fh)
        logger.info("SequencePredictor saved to %s", path)

    def load(self, path: Union[str, Path]) -> None:
        """Load model from disk."""
        with open(path, "rb") as fh:
            data = pickle.load(fh)  # nosec B301 — trusted local files
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_names = data["feature_names"]
        self.metrics = data.get("metrics", {})
        self.model_name = data.get("model_name", "loaded_model")
        self.is_calibrated = data.get("is_calibrated", False)
        logger.info("SequencePredictor loaded from %s", path)


# ---------------------------------------------------------------------------
# Convenience: train from raw DataFrame
# ---------------------------------------------------------------------------

def train_sequence_predictor(
    df: pd.DataFrame,
    hold_candles: int = 5,
    calibrate: bool = True,
) -> Dict[str, Any]:
    """End-to-end training pipeline: feature engineering + model training.

    Parameters
    ----------
    df : pd.DataFrame
        OHLCV data (needs >= ~50 rows for meaningful training).
    hold_candles : int
        Forward-looking window for labelling.
    calibrate : bool
        Whether to calibrate predicted probabilities.

    Returns
    -------
    dict
        ``{"model": SequencePredictor, "metrics": {...}, "cv_results": {...},
        "feature_importance": [...], "n_samples": int}``
    """
    predictor = SequencePredictor()
    X, y = engineer_sequence_features(df, hold_candles=hold_candles)

    if len(X) < 20:
        return {"error": f"Insufficient data: only {len(X)} usable samples (need >= 20)"}

    metrics = predictor.train(X, y, calibrate=calibrate)
    n_splits = min(5, max(2, len(X) // 20))
    cv_results = predictor.cross_validate(X, y, n_splits=n_splits)
    importance = predictor.feature_importance()

    return {
        "model": predictor,
        "metrics": metrics,
        "cv_results": cv_results,
        "feature_importance": importance.to_dict("records") if not importance.empty else [],
        "n_samples": len(X),
        "n_features": len(predictor.feature_names or []),
    }

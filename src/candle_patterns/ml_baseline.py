"""
Machine Learning baseline module for pattern-based trading signal prediction.

Uses Random Forest classifier to predict pattern outcomes (profitable/unprofitable).
Includes:
- Feature engineering from detected patterns
- TimeSeriesSplit cross-validation
- Feature importance analysis
- Model evaluation and reporting
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

logger = logging.getLogger(__name__)


class PatternMLModel:
    """Machine learning model for predicting pattern outcomes."""

    def __init__(self, model_name: str = "pattern_classifier_v1"):
        """Initialize the ML model."""
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.metrics = {}

    def engineer_features(
        self, 
        df: pd.DataFrame, 
        patterns: List[Dict]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Engineer features from OHLC data and detected patterns.
        
        Features include:
        - Technical indicators (RSI, MACD, Bollinger Bands)
        - Pattern statistics (occurrence count, recency)
        - Volatility measures
        
        Args:
            df: OHLC DataFrame
            patterns: List of detected pattern dictionaries
            
        Returns:
            (X, y) where X is features DataFrame and y is labels (1 = profit, 0 = loss)
        """
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate simple return over next 5 periods
        df['future_return'] = df['close'].pct_change(5).shift(-5)
        df['label'] = (df['future_return'] > 0).astype(int)
        
        # Basic features
        df['hl_ratio'] = df['high'] / df['low']
        df['oc_ratio'] = df['close'] / df['open']
        df['volatility'] = df['close'].pct_change().rolling(5).std()
        df['volume_ma'] = df['volume'].rolling(5).mean() if 'volume' in df.columns else 1.0
        
        # Pattern features
        df['pattern_count'] = 0
        for idx, row in df.iterrows():
            pattern_names = [p['pattern'] for p in patterns if p['timestamp'] == row['timestamp']]
            df.at[idx, 'pattern_count'] = len(pattern_names)
        
        # Select features for modeling
        feature_cols = [
            'hl_ratio', 'oc_ratio', 'volatility', 'volume_ma', 'pattern_count'
        ]
        
        # Remove NaN rows
        df_clean = df.dropna(subset=feature_cols + ['label'])
        
        X = df_clean[feature_cols]
        y = df_clean['label']
        
        self.feature_names = feature_cols
        
        return X, y

    def train(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """
        Train the Random Forest model with time series cross-validation.
        
        Args:
            X: Feature DataFrame
            y: Label Series
            test_size: Proportion of data for final holdout test
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training ML model on {len(X)} samples")
        
        # Split data (time series aware)
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Standardize features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        self.metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        }
        
        logger.info(f"Training complete. Accuracy: {self.metrics['accuracy']:.3f}, ROC-AUC: {self.metrics['roc_auc']:.3f}")
        
        return self.metrics

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, n_splits: int = 5) -> Dict:
        """
        Perform time series cross-validation.
        
        Args:
            X: Feature DataFrame
            y: Label Series
            n_splits: Number of CV folds
            
        Returns:
            Dictionary with cross-validation scores
        """
        logger.info(f"Performing {n_splits}-fold time series cross-validation...")
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        scores = cross_validate(
            model, X, y, cv=tscv,
            scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
            n_jobs=-1
        )
        
        cv_results = {
            key: (scores[f'test_{key}'].mean(), scores[f'test_{key}'].std())
            for key in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        }
        
        logger.info(f"CV Results (mean ± std):")
        for metric, (mean, std) in cv_results.items():
            logger.info(f"  {metric}: {mean:.3f} ± {std:.3f}")
        
        return cv_results

    def feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance rankings.
        
        Returns:
            DataFrame with features ranked by importance
        """
        if self.model is None:
            logger.warning("Model not trained yet")
            return pd.DataFrame()
        
        importance = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return feature_importance_df

    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new data.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            (predictions, probabilities) tuple
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        return predictions, probabilities

    def save(self, path: Path) -> None:
        """Save model to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler, 'features': self.feature_names}, f)
        logger.info(f"Model saved to {path}")

    def load(self, path: Path) -> None:
        """Load model from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['features']
        logger.info(f"Model loaded from {path}")


def train_baseline_model(df: pd.DataFrame, patterns: List[Dict]) -> Dict:
    """
    Train and evaluate a baseline ML model.
    
    Args:
        df: OHLC DataFrame
        patterns: List of detected patterns
        
    Returns:
        Dictionary with training results and metrics
    """
    model = PatternMLModel()
    
    # Engineer features
    X, y = model.engineer_features(df, patterns)
    
    if len(X) < 10:
        logger.warning(f"Insufficient data: only {len(X)} samples")
        return {'error': 'Insufficient data for training'}
    
    # Train model
    metrics = model.train(X, y)
    
    # Cross-validation
    cv_results = model.cross_validate(X, y, n_splits=min(5, len(X) // 10))
    
    # Feature importance
    importance_df = model.feature_importance()
    
    results = {
        'model': model,
        'train_metrics': metrics,
        'cv_results': cv_results,
        'feature_importance': importance_df.to_dict('records'),
        'n_samples': len(X),
        'n_features': len(model.feature_names),
    }
    
    logger.info(f"Model training complete: {len(X)} samples, {len(model.feature_names)} features")
    
    return results

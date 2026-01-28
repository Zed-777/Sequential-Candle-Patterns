from typing import Dict
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def train_baseline_models(df: pd.DataFrame, label_col: str = "target") -> Dict[str, object]:
    """Train simple baseline models (Random Forest) to predict `label_col`.

    The function expects a DataFrame where features are numeric columns and label_col is binary 0/1.
    Returns a dict of trained models and train/test metrics.
    """
    X = df.drop(columns=[label_col])
    y = df[label_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    rf.fit(X_train, y_train)

    preds = rf.predict(X_test)
    acc = accuracy_score(y_test, preds)

    return {"rf": rf, "metrics": {"accuracy": acc}}

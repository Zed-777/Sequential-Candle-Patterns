import pandas as pd
import numpy as np
from candle_patterns.ml.poc import train_baseline_models


def test_train_baseline_models_smoke():
    # create synthetic data: 100 rows, 4 numeric features, binary target
    rng = np.random.RandomState(42)
    X = rng.randn(100, 4)
    y = rng.randint(0, 2, size=100)
    df = pd.DataFrame(X, columns=["f1", "f2", "f3", "f4"])
    df["target"] = y

    res = train_baseline_models(df, label_col="target")
    assert "rf" in res and "metrics" in res
    assert res["metrics"]["accuracy"] >= 0.0

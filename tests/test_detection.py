import pandas as pd
from candle_patterns.detection import detect_patterns


def make_sample():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2022-01-01", periods=6, freq="D"),
            "open": [5, 4, 3, 2, 3, 2],
            "high": [6, 5, 4, 3, 4, 3],
            "low": [4.5, 3.5, 2.5, 1.5, 2.5, 1.5],
            "close": [4.8, 3.8, 3.5, 2.8, 3.8, 2.9],
        }
    )
    return df


def test_detect_runs():
    df = make_sample()
    res = detect_patterns(df)
    assert isinstance(res, list)

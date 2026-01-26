import pandas as pd
from candle_patterns.backtest import simple_pattern_backtest


def test_backtest_no_detections():
    df = pd.DataFrame({"open": [1, 2], "close": [1.5, 2.5]})
    res = simple_pattern_backtest(df, [])
    assert res["count"] == 0


def test_backtest_basic():
    df = pd.DataFrame({"open": [1, 2, 3], "close": [1.1, 2.1, 3.1]})
    detections = [{"index": 0}, {"index": 1}]
    res = simple_pattern_backtest(df, detections, hold=1)
    assert res["count"] == 2

import pandas as pd
from candle_patterns.opp_miner import ordinal_encode, extract_windows, opp_miner


def test_ordinal_encode_simple():
    assert ordinal_encode([3, 1, 2]) == (3, 1, 2)
    assert ordinal_encode([1, 2, 3]) == (1, 2, 3)


def test_extract_windows():
    df = pd.DataFrame({"close": [1, 2, 3, 4, 5]})
    ws = extract_windows(df, length=3)
    assert len(ws) == 3


def test_opp_miner():
    df = pd.DataFrame({"close": [1, 2, 3, 1, 2, 3, 1]})
    res = opp_miner(df, length=3, min_support=0.2)
    assert isinstance(res, dict)

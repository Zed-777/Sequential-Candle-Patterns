import pandas as pd
from candle_patterns.ingestion import load_csv, validate_schema


def test_validate_schema_ok(tmp_path):
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2022-01-01", periods=3),
            "open": [1, 2, 3],
            "high": [2, 3, 4],
            "low": [0.5, 1.5, 2.5],
            "close": [1.5, 2.5, 3.5],
        }
    )
    path = tmp_path / "test.csv"
    df.to_csv(path, index=False)
    loaded = load_csv(str(path))
    assert list(loaded.columns) >= list(df.columns)


def test_validate_schema_missing():
    df = pd.DataFrame({"a": [1]})
    try:
        validate_schema(df)
        assert False
    except ValueError:
        assert True

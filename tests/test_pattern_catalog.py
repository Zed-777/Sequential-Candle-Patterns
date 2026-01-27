import pandas as pd
from candle_patterns.detection import detect_patterns


def make_row(symbol):
    if symbol == "G":
        return {"timestamp": pd.Timestamp("2022-01-01"), "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5}
    if symbol == "R":
        return {"timestamp": pd.Timestamp("2022-01-01"), "open": 2.0, "high": 2.5, "low": 1.5, "close": 1.6}
    if symbol == "Doji":
        return {"timestamp": pd.Timestamp("2022-01-01"), "open": 1.0, "high": 1.05, "low": 0.95, "close": 1.02}
    if symbol == "Shooting":
        return {"timestamp": pd.Timestamp("2022-01-01"), "open": 1.0, "high": 3.0, "low": 0.9, "close": 1.05}
    if symbol == "Hanging":
        return {"timestamp": pd.Timestamp("2022-01-01"), "open": 1.2, "high": 1.3, "low": 0.5, "close": 1.15}
    if symbol == "Spinning":
        return {"timestamp": pd.Timestamp("2022-01-01"), "open": 1.0, "high": 1.5, "low": 0.9, "close": 1.05}
    return {"timestamp": pd.Timestamp("2022-01-01"), "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5}


def df_from_symbols(symbols):
    rows = [make_row(s) for s in symbols]
    return pd.DataFrame(rows)


def test_additional_patterns_detected():
    patterns = {
        "spinning_top": ["Spinning"],
        "shooting_star": ["Shooting"],
        "hanging_man": ["Hanging"],
        "piercing_line": ["R", "G"],
        "morning_star": ["R", "Spinning", "G"],
        "evening_star": ["G", "Spinning", "R"],
    }

    for pname, seq in patterns.items():
        df = df_from_symbols(seq)
        res = detect_patterns(df)
        assert any(r["pattern"] == pname for r in res), f"{pname} not found in {res} for seq {seq}"

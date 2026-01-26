from __future__ import annotations

import pandas as pd
from typing import Optional

REQUIRED_COLUMNS = {"timestamp", "open", "high", "low", "close"}


def validate_schema(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_csv(path: str, parse_dates: Optional[str] = "timestamp") -> pd.DataFrame:
    df = pd.read_csv(path)
    # parse date
    if parse_dates and parse_dates in df.columns:
        df[parse_dates] = pd.to_datetime(df[parse_dates], utc=True, errors="raise")
    validate_schema(df)
    # sort
    df = df.sort_values(by=parse_dates).reset_index(drop=True)
    return df

"""
Data ingestion and validation utilities.

This module provides functions to load and validate OHLC (candlestick) data
from CSV files or other sources.

Key functions:
- validate_schema(): Check that a DataFrame has required OHLC columns
- load_csv(): Load a CSV file with type conversion and date parsing

Required columns: timestamp (or datetime), open, high, low, close

Example:
    >>> df = load_csv('data.csv')
    >>> validate_schema(df)
"""

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
    # Normalise common timestamp column name aliases
    if "timestamp" not in df.columns and "time" in df.columns:
        df = df.rename(columns={"time": "timestamp"})
    # parse date
    if parse_dates and parse_dates in df.columns:
        df[parse_dates] = pd.to_datetime(df[parse_dates], utc=True, errors="raise")
    validate_schema(df)
    # sort
    df = df.sort_values(by=parse_dates).reset_index(drop=True)
    return df

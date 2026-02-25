"""Yahoo Finance data feed integration.

Fetch historical OHLCV data directly from Yahoo Finance so users can scan
real market data for sequential colour patterns instead of relying solely on
CSV uploads.

Supports stocks, ETFs, crypto, indices, and forex.
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_INTERVALS = [
    "1m", "2m", "5m", "15m", "30m", "60m", "90m",
    "1h", "1d", "5d", "1wk", "1mo", "3mo",
]

VALID_PERIODS = [
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max",
]

POPULAR_SYMBOLS = {
    "Stocks": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "JPM", "V", "WMT", "UNH", "MA", "HD", "PG", "JNJ",
    ],
    "Crypto": [
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD",
        "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "MATIC-USD",
    ],
    "Indices": [
        "^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX",
        "^FTSE", "^GDAXI", "^N225",
    ],
    "ETFs": [
        "SPY", "QQQ", "IWM", "DIA", "VOO",
        "GLD", "SLV", "TLT", "XLF", "XLE",
    ],
    "Forex": [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X",
    ],
}

# Flatten for quick lookup
ALL_POPULAR = [sym for group in POPULAR_SYMBOLS.values() for sym in group]


# ---------------------------------------------------------------------------
# Core fetch function
# ---------------------------------------------------------------------------

def fetch_yahoo_data(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance.

    Parameters
    ----------
    symbol : str
        Ticker symbol (e.g. "AAPL", "BTC-USD", "^GSPC").
    period : str
        How far back to fetch. Ignored when *start*/*end* are given.
        One of: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max.
    interval : str
        Candle interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.
    start : str, optional
        Start date in YYYY-MM-DD format. Overrides *period*.
    end : str, optional
        End date in YYYY-MM-DD format.

    Returns
    -------
    pd.DataFrame
        Standardised OHLCV DataFrame with columns:
        timestamp, open, high, low, close, volume

    Raises
    ------
    ValueError
        If symbol is empty, interval is invalid, or no data returned.
    ConnectionError
        If Yahoo Finance is unreachable.
    """
    import yfinance as yf

    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval '{interval}'. Must be one of: {VALID_INTERVALS}")
    if period not in VALID_PERIODS and start is None:
        raise ValueError(f"Invalid period '{period}'. Must be one of: {VALID_PERIODS}")

    logger.info("Fetching %s data: symbol=%s period=%s interval=%s", symbol, symbol, period, interval)

    try:
        ticker = yf.Ticker(symbol)

        if start and end:
            df = ticker.history(start=start, end=end, interval=interval)
        elif start:
            df = ticker.history(start=start, interval=interval)
        else:
            df = ticker.history(period=period, interval=interval)
    except Exception as exc:
        logger.error("Yahoo Finance fetch failed for %s: %s", symbol, exc)
        raise ConnectionError(f"Failed to fetch data for '{symbol}': {exc}") from exc

    if df is None or df.empty:
        raise ValueError(f"No data returned for symbol '{symbol}'. Check symbol validity.")

    # Standardise column names to match our system expectation
    df = df.reset_index()
    rename_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ("date", "datetime"):
            rename_map[col] = "timestamp"
        elif col_lower == "open":
            rename_map[col] = "open"
        elif col_lower == "high":
            rename_map[col] = "high"
        elif col_lower == "low":
            rename_map[col] = "low"
        elif col_lower == "close":
            rename_map[col] = "close"
        elif col_lower == "volume":
            rename_map[col] = "volume"

    df = df.rename(columns=rename_map)

    # Ensure required columns exist
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Fetched data missing required columns: {missing}")

    # Keep only standard columns
    keep_cols = ["timestamp", "open", "high", "low", "close"]
    if "volume" in df.columns:
        keep_cols.append("volume")
    df = df[keep_cols].copy()

    # Convert timestamp to datetime with UTC
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Drop any rows with NaN in OHLC
    df = df.dropna(subset=["open", "high", "low", "close"])

    logger.info("Fetched %d candles for %s (%s, %s)", len(df), symbol, period, interval)
    return df


def search_symbols(query: str, max_results: int = 10) -> list[dict]:
    """Search Yahoo Finance for matching ticker symbols.

    Parameters
    ----------
    query : str
        Search string (company name, symbol prefix, etc.)
    max_results : int
        Maximum results to return.

    Returns
    -------
    list[dict]
        Each dict has keys: symbol, name, type, exchange
    """
    import yfinance as yf

    query = query.strip()
    if not query:
        return []

    try:
        # yfinance search — uses Yahoo Finance search endpoint
        search = yf.Search(query)

        results = []
        # search.quotes contains the matching symbols
        for quote in (search.quotes or [])[:max_results]:
            results.append({
                "symbol": quote.get("symbol", ""),
                "name": quote.get("shortname", quote.get("longname", "")),
                "type": quote.get("quoteType", ""),
                "exchange": quote.get("exchange", ""),
            })
        return results
    except Exception as exc:
        logger.warning("Symbol search failed for '%s': %s", query, exc)
        # Fallback: check against our popular symbols list
        query_upper = query.upper()
        fallback = []
        for sym in ALL_POPULAR:
            if query_upper in sym:
                fallback.append({"symbol": sym, "name": sym, "type": "popular", "exchange": ""})
        return fallback[:max_results]


def get_symbol_info(symbol: str) -> dict:
    """Get basic info about a symbol (name, type, currency, exchange).

    Returns a dict with available metadata. Gracefully handles failures.
    """
    import yfinance as yf

    symbol = symbol.strip().upper()
    if not symbol:
        return {}

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        return {
            "symbol": symbol,
            "name": info.get("shortName", info.get("longName", symbol)),
            "type": info.get("quoteType", "Unknown"),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", "Unknown"),
            "market_cap": info.get("marketCap"),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
        }
    except Exception as exc:
        logger.warning("Cannot get info for %s: %s", symbol, exc)
        return {"symbol": symbol, "name": symbol}

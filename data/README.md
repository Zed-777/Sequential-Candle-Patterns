# Data Directory

This directory contains runtime data and sample datasets for the Sequential Candle Patterns system.

---

## Directory Structure

```text
data/
├── README.md          — This file
├── samples/           — Pre-built sample OHLCV CSV files for testing/demos
│   ├── AAPL_sample.csv
│   └── BTC_sample.csv
├── candle_patterns.db — SQLite database (auto-created at runtime, gitignored)
├── alerts.db          — Alerts database (auto-created at runtime, gitignored)
├── watchlist.json     — Saved sequence watchlist (auto-created, gitignored)
└── preferences.json   — User preferences (auto-created, gitignored)
```

## Sample Data

The `samples/` directory includes pre-built CSV files you can load directly into the dashboard or CLI:

| File | Description | Rows | Date Range |
|------|-------------|------|------------|
| `AAPL_sample.csv` | Apple Inc. synthetic daily OHLCV data | 200 | ~Jun 2025 – Dec 2025 |
| `BTC_sample.csv` | Bitcoin synthetic daily OHLCV data | 200 | ~Jun 2025 – Dec 2025 |

### CSV Format

All CSV files follow this schema:

```
timestamp,open,high,low,close,volume
2025-01-01 00:00:00,150.00,155.00,148.00,153.00,1000000
```

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime | ISO 8601 date/time string |
| `open` | float | Opening price |
| `high` | float | Highest price in period |
| `low` | float | Lowest price in period |
| `close` | float | Closing price |
| `volume` | int (optional) | Trade volume |

## Generating New Sample Data

To regenerate or create new sample data:

```bash
python generate_sample_data.py
```

Or use the ingestion module directly:

```python
from candle_patterns.data_feeds import fetch_yahoo_data

df = fetch_yahoo_data("AAPL", period="1y")
df.to_csv("data/samples/AAPL_live.csv", index=False)
```

## Runtime Files

The following files are created automatically at runtime and are **not tracked in git**:

- `candle_patterns.db` — Detection and upload history (30-day auto-cleanup)
- `alerts.db` — Alert rules and alert history
- `watchlist.json` — User-saved sequence libraries
- `preferences.json` — UI settings, defaults, and recent searches

These files are excluded by `.gitignore`. To reset them, simply delete the files and restart the application.

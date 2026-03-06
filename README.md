# Candlestick Patterns — Sequential Pattern Analysis System

[![tests](https://github.com/Zed-777/candle-patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Zed-777/candle-patterns/actions/workflows/ci.yml)

A **sequential colour-based candle pattern scanner** that lets you define candlestick colour sequences (e.g. `3R -> 2G`, `5R -> Doji -> 3G`), scan historical OHLCV data for matches, auto-discover recurring patterns, and predict likely continuations — all from an interactive 12-tab Dash web dashboard or CLI.

**v1.3.0** — 279 tests passing, 15 named tokens, 12 dashboard tabs, Yahoo Finance integration, ML prediction, sequence alerts, performance optimization.

---

## Features

### Core Pattern Engine

- **Sequential Colour Scanner** — define sequences like `3R -> 2G`, `5R -> Doji -> 3G`, scan 200+ candles
- **Wildcard Matching** — `3R -> * -> 2G` matches any 1-3 candles between segments
- **Multi-Sequence Scanning** — scan multiple sequences simultaneously with colour-coded chart highlights
- **15 Preset Sequences** — common colour patterns ready to use
- **15 Named Tokens** — Doji, Hammer, InvertedHammer, Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows

### Analysis & Prediction

- **Auto-Discovery Engine** — finds the most common R/G sequences in data automatically
- **What-Comes-Next Prediction** — R/G/Doji probability analysis after each sequence
- **Outcome Statistics** — win rate, avg return, max gain/loss for each sequence
- **Confidence Scoring** — z-score, p-value, statistical significance for each pattern's edge
- **Reverse Pattern Finder** — discover what sequences preceded big price moves
- **Sequence Heatmap** — density visualisation of pattern matches across time buckets
- **Advanced ML Predictor** — GradientBoosting model with 17 engineered features, calibrated probabilities

### Data & Connectivity

- **Yahoo Finance Integration** — fetch real stock/crypto/index/forex data directly from sidebar
- **Multi-Timeframe Analysis** — scan the same symbol across 1H/4H/Daily/Weekly, detect alignment
- **Data Feed Caching** — LRU cache with 5-min TTL for Yahoo Finance fetches
- **CSV Ingestion** — upload and validate custom OHLCV data

### Alerts & Monitoring

- **Sequence Alerts** — create rules to watch for specific patterns, with SQLite persistence
- **Webhook Notifications** — POST JSON to any URL when patterns match
- **Email Notifications** — SMTP-based email alerts when patterns are detected
- **Live Refresh** — configurable auto-scan interval for real-time pattern detection

### Dashboard (12 Tabs)

| Tab | Purpose |
|---|---|
| **Chart** | Interactive OHLCV candlestick chart with coloured match highlights |
| **Matches** | Detailed table of every match per sequence |
| **Discovery** | Top 25 auto-discovered recurring colour sequences with win rate |
| **Statistics** | Per-sequence outcome stats + what-comes-next prediction |
| **Heatmap** | Pattern density heatmap across time buckets |
| **Reverse Finder** | Find sequences that preceded big price moves |
| **Backtesting** | Equity curve, Sharpe ratio, max drawdown, profit factor |
| **Multi-TF** | Cross-timeframe alignment analysis |
| **Watchlist** | Save/load/export/import sequence libraries |
| **Alerts** | Alert rules management, history, webhook/email config |
| **ML Predict** | Train model, view metrics, predict next candle |
| **Settings** | User preferences, live refresh toggle, defaults |

### Other

- **Backtesting Engine** — equity curve, Sharpe ratio, max drawdown, profit factor per sequence
- **Sequence Watchlist** — save/load/export/import sequence libraries with JSON persistence
- **User Preferences** — JSON-backed profiles with defaults, recents, export/import
- **Performance Optimization** — vectorized numpy scanning (~50-100x faster), chunked processing for 10K+ datasets
- **17 Traditional Pattern Detectors** — Doji, Hammer, Engulfing, etc. (secondary feature)
- **ML Baseline** — RandomForest classifier
- **SQLite Persistence** — 30-day auto-cleanup for history
- **CLI Tools** — 5 commands: run, cleanup, train, predict, backtest
- **Docker** — multi-stage build + GHCR publish on release
- **CI/CD** — GitHub Actions: lint, test, security scan, Docker build

---

## Quickstart

### 1. Setup

```bash
# Clone
git clone https://github.com/Zed-777/candle-patterns.git
cd candle-patterns

# Create venv and install
# Windows PowerShell:
scripts\setup_venv.ps1
.\.venv\Scripts\Activate.ps1

# macOS/Linux:
scripts/setup_venv.sh
source .venv/bin/activate
```

### 2. Run the Dashboard

```bash
python scripts/run_dash.py
# Opens at http://localhost:8050
```

### 3. Run Tests

```bash
pytest tests/ -q
# 279 passed, 4 skipped
```

### 4. Docker

```bash
docker build -t candle-patterns:latest .
docker run --rm -p 8050:8050 candle-patterns:latest run
```

---

## Sequence Pattern Syntax

```text
NR       → N consecutive red candles       (e.g. 3R = 3 red in a row)
NG       → N consecutive green candles     (e.g. 2G = 2 green)
Doji     → single Doji candle
Hammer   → single Hammer candle
InvertedHammer → Inverted Hammer
Engulfing      → Engulfing (bullish or bearish)
BullEngulfing  → Bullish Engulfing only
BearEngulfing  → Bearish Engulfing only
MorningStar    → Morning Star reversal (3-candle)
EveningStar    → Evening Star reversal (3-candle)
ShootingStar   → Shooting Star
SpinningTop    → Spinning Top
Marubozu       → Full-body candle (bull or bear)
BullMarubozu   → Bullish full-body candle
BearMarubozu   → Bearish full-body candle
ThreeWhiteSoldiers → Three consecutive bullish candles (rising closes)
ThreeBlackCrows    → Three consecutive bearish candles (falling closes)
*          → wildcard (matches any 1-3 candles)
->         → separator between segments

Examples:
  3R -> 2G                  Three red followed by two green
  5R -> 3G                  Five red followed by three green
  2R -> Doji -> 2G          Two red, a doji, then two green
  3R -> * -> 2G             Three red, any 1-3 candles, then two green
  2R -> Engulfing           Two red then an engulfing pattern
  3R -> MorningStar         Three red then a morning star
  2R -> ThreeWhiteSoldiers  Two red then three white soldiers
```

---

## Project Structure

```text
candle-patterns/
├── src/candle_patterns/
│   ├── patterns.py ............. Core sequence engine (15 named tokens)
│   ├── dashboard.py ............ Dash web app (12 tabs)
│   ├── data_feeds.py ........... Yahoo Finance + LRU cache
│   ├── performance.py .......... Vectorized scanning, chunking, cache
│   ├── alerts.py ............... Alert rules, webhook + email dispatch
│   ├── ml_sequence.py .......... GradientBoosting ML predictor
│   ├── preferences.py .......... User profiles & preferences
│   ├── multi_timeframe.py ...... Multi-TF analysis
│   ├── watchlist.py ............ Sequence library persistence
│   ├── detection.py ............ Traditional pattern detectors (17)
│   ├── backtesting.py .......... Performance evaluation engine
│   ├── ml_baseline.py .......... RandomForest ML model
│   ├── storage.py .............. SQLite persistence
│   ├── cli.py .................. CLI (5 commands)
│   └── ingestion.py ............ CSV validation
├── tests/ ...................... 225 unit tests
├── .github/workflows/ .......... CI/CD pipelines
├── Dockerfile .................. Multi-stage Docker build
└── PROJECT_PLAN.md ............. Single Source of Truth (SSoT)
```

---

## Documentation

- [PROJECT_PLAN.md](PROJECT_PLAN.md) — Canonical SSoT with full feature inventory, architecture, test coverage, and decision log
- [PATTERN_CATALOG.md](PATTERN_CATALOG.md) — Catalogue of all pattern types
- [DASHBOARD_README.md](DASHBOARD_README.md) — Dashboard quick-start guide
- [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md) — Release notes

---

## License

This project is provided as-is for educational and research purposes.

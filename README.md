# Candlestick Patterns — Sequential Pattern Analysis System

[![tests](https://github.com/Zed-777/Sequential-Candle-Patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Zed-777/Sequential-Candle-Patterns/actions/workflows/ci.yml)
[![python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A **sequential colour-based candle pattern scanner** that lets you define candlestick colour sequences (e.g. `3R -> 2G`, `5R -> Doji -> 3G`), scan historical OHLCV data for matches, auto-discover recurring patterns, and predict likely continuations — all from an interactive 12-tab Dash web dashboard or CLI.

**v1.4.0** — 315 tests passing (100% success rate), 15 named tokens, 12 dashboard tabs, Yahoo Finance integration, multi-timeframe analysis, ML prediction, sequence alerts, REST API, performance optimization.

---

## Quick Start

### Docker (Recommended)

```bash
# Build and run in Docker
docker build -t candle-patterns:latest .
docker run --rm -p 8050:8050 candle-patterns:latest run

# Opens at http://localhost:8050
```

### Local Setup

```bash
# Clone and install
git clone https://github.com/Zed-777/Sequential-Candle-Patterns.git
cd Sequential-Candle-Patterns

# Windows PowerShell:
scripts\setup_venv.ps1
.\.venv\Scripts\Activate.ps1
pip install -e .

# macOS/Linux:
scripts/setup_venv.sh
source .venv/bin/activate
pip install -e .

# Run the dashboard
python scripts/run_dash.py
# Opens at http://localhost:8050
```

---

## Usage Examples

### Minimal Example: Scan for a Single Pattern

```bash
# Scan AAPL for 3 red candles followed by 2 green candles
python -c "
from candle_patterns.data_feeds import fetch_yahoo_data
from candle_patterns.patterns import find_sequence_occurrences

df = fetch_yahoo_data('AAPL', period='3mo')
matches = find_sequence_occurrences(df, '3R -> 2G')
print(f'Found {len(matches)} matches')
"
```

### Realistic Workflow: Full Analysis with Live Dashboard

1. **Open dashboard:** `python scripts/run_dash.py` → <http://localhost:8050>
2. **Enter symbol:** Type `AAPL` in sidebar, select period `3mo`, click **Fetch Data**
3. **Define patterns:** Enter `3R -> 2G` in Matches tab, see all candlestick positions highlighted on chart
4. **Auto-discover:** Switch to Discovery tab, see ML-discovered top 25 recurring patterns
5. **Predict outcomes:** Switch to Statistics tab, see win rate and what-comes-next probability
6. **Backtest:** Switch to Backtesting tab, see equity curve and Sharpe ratio for pattern
7. **Save pattern:** Switch to Watchlist tab, click **Save Sequence** (persisted as JSON)
8. **Create alert:** Switch to Alerts tab, create rule to notify via webhook when pattern matches

---

## Architecture Overview

**System Components:**

The system is built around a **sequential colour pattern scanner engine** with integrated analysis, prediction, and monitoring:

```text
User Input (Dashboard/API)
    ↓
Data Fetch (Yahoo Finance + Cache)
    ↓
Pattern Matching Engine (vectorized numpy scanning)
    ↓
Statistics & Prediction (outcome analysis + ML model)
    ↓
Visualization (interactive Plotly charts)
    ↓
Persistence (SQLite alerts, JSON watchlists, user preferences)
```

**Key Modules:**

| Module | Purpose | Key Functions |
|---|---|---|
| `patterns.py` | Core engine | Find sequences, discover patterns, predict outcomes, reverse finder, confidence scoring |
| `dashboard.py` | Web UI | 12 interactive tabs with ~31 Dash callbacks |
| `data_feeds.py` | Data layer | Yahoo Finance integration + 5-min TTL LRU cache |
| `performance.py` | Optimization | Vectorized numpy scanning (~50-100x faster), chunked processing, caching |
| `ml_sequence.py` | Prediction | GradientBoosting with 17 engineered features, calibration |
| `alerts.py` | Monitoring | SQLite-backed rules, webhook + email dispatch |
| `multi_timeframe.py` | Analysis | Cross-interval scanning + alignment detection |
| `backtesting.py` | Evaluation | Equity curve, Sharpe ratio, drawdown, profit factor |

**See [architecture.md](architecture.md) for detailed system design and data flows.**

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
- **CI/CD** — GitHub Actions: lint, test, security scan, Docker build, E2E tests
- **REST API** — JSON endpoints for scan, discover, portfolio scan, symbol search

---

## Project Status & Roadmap

**Current Milestone:** Phase 11 Complete — Production Ready  
**Status:** ✅ All MVP features delivered, 100% test pass rate (315 tests)  
**See [MPDP.md](MPDP.md) for current milestone, next 3 actionable tasks, and roadmap timeline.**

Current focus: Phase 12 repository standards and governance (architecture docs, UML diagrams, developer onboarding).

---

## Testing & Quality

### Run Tests

```bash
# All tests
pytest tests/ -q
# Expected: 315 passed, 4 skipped, 100% success rate

# Specific test file
pytest tests/test_sequence_patterns.py -v

# With coverage
pytest tests/ --cov=src/candle_patterns --cov-report=term-missing
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### CI Pipeline

The repository runs automated tests and quality checks on every pull request:

- **Linting:** `ruff check` (Python style and import sorting)
- **Formatting:** `black` (code style)
- **Type checking:** Future enhancement (planned)
- **Security:** `bandit` (vulnerability scan)
- **Tests:** `pytest` on Python 3.10, 3.12, 3.14
- **Docker build:** Multi-stage build verification
- **E2E tests:** Playwright browser automation (36 tests)

**See [.github/workflows/ci.yml](.github/workflows/ci.yml) for full details.**

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

## Security

For security policies, vulnerability reporting, and data handling practices, see [SECURITY.md](SECURITY.md).

**Key points:**

- No secrets stored in repository (use .env.example and environment variables)
- SQLite databases excluded from version control (local-only)
- SMTP credentials in memory only (never persisted to disk)

---

## Contributing

Contributions welcome! For branch strategy, PR workflow, code style, and testing expectations, see [CONTRIBUTING.md](CONTRIBUTING.md).

**Quick summary:**

- Create feature branch: `git checkout -b feature/your-feature`
- Write tests for new functionality
- Ensure all tests pass: `pytest tests/ -q`
- Submit PR with description and reference to related issue/MPDP task
- At least one reviewer approval required before merge

---

## Support the Project

If Candle Patterns adds value to your workflow, consider supporting continued development:

### Cryptocurrency Donations

Your contribution helps sustain:

- Active development and feature improvements
- Bug fixes and security patching
- Documentation and tutorials
- Community support

**Wallet Addresses:**

| Cryptocurrency | Address |
|---|---|
| **Bitcoin** | `bc1qezg26hp8n7339x8fa0084wrf4ct8xuytqkydt9` |
| **Ethereum** | `0x641F7431aC0aC4Ba411016161816b1AA3D886b60` |
| **USDT (Ethereum/Polygon)** | `0x641F7431aC0aC4Ba411016161816b1AA3D886b60` |

*This project is open-source (MIT licensed) and will always remain free to use. Donations are entirely voluntary and appreciated but not required.*

---

## Changelog & Releases

The project follows **semantic versioning** (major.minor.patch):

- **v1.4.0** (Current) — Phase 11 complete: E2E tests, 315 passing tests, production-ready
- **v1.3.0** — Phase 8–10: REST API, portfolio scanner, extended tokens, email alerts
- **v1.2.0** — Phase 6–7: Performance optimization, ML predictor, alerts, user preferences
- **v1.1.0** — Phase 4–5: Yahoo Finance, multi-timeframe, backtesting, watchlist
- **v1.0.0** — MVP: Core pattern scanner, discovery, statistics, dashboard

**See [GitHub Releases](https://github.com/Zed-777/Sequential-Candle-Patterns/releases) for detailed release notes.**

---

## License & Contact

**License:** MIT — See [LICENSE](LICENSE) for full text.

**Maintainer:** [Zed-777](https://github.com/Zed-777)

For questions, feature requests, or bug reports, [open an issue on GitHub](https://github.com/Zed-777/Sequential-Candle-Patterns/issues).

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
├── tests/ ...................... 315 unit + E2E tests (100% pass rate)
├── .github/workflows/ .......... CI/CD pipelines (lint, test, build, E2E)
├── Dockerfile .................. Multi-stage Docker build + .dockerignore
├── pyproject.toml .............. Python package config + pytest settings
├── MPDP.md ..................... Master Progress & Development Plan (SSoT)
├── PROJECT_GUIDELINES.md ....... Repository standards (required files, structure)
└── docs/ ....................... Additional documentation
    ├── architecture.md ......... System design (TO BE CREATED)
    ├── RELEASE_NOTES.md ........ Release notes
    └── SSoT_UPDATES.md ......... Single source of truth updates
```

---

## Documentation

- **[MPDP.md](MPDP.md)** — Master Progress & Development Plan (project status, roadmap, next tasks)
- **[PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md)** — Repository standards & governance
- **[SECURITY.md](SECURITY.md)** — Security policies and data handling
- **[PATTERN_CATALOG.md](PATTERN_CATALOG.md)** — Catalogue of all pattern types
- **[DASHBOARD_README.md](DASHBOARD_README.md)** — Dashboard quick-start guide
- **[docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md)** — Release notes

---

## Notes for Claims & Transparency

Any performance or accuracy claims in project documentation must include:

- **Dataset:** The specific OHLCV data used for evaluation
- **Evaluation Method:** How metrics were calculated
- **Baseline:** Comparison against a known standard or random baseline
- Or label as:** "Internal experiment results"

Example: "GradientBoosting ML predictor achieves 62% accuracy on S&P 500 data (2016–2024) using 5-fold cross-validation, compared to 50% baseline random guessing."

---

**Last Updated:** April 2, 2026  
**Version:** 1.4.0

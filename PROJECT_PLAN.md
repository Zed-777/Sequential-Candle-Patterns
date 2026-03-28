# Sequential Candle Pattern Analysis System — Development Plan & Progress

**Last Updated**: March 7, 2026 (Phase 11 — E2E Playwright Test Suite)  
**Project Status**: PHASE 11 COMPLETE — v1.4.0 — E2E Playwright Test Suite  
**Overall Progress**: MVP + Phase 2–10 + Phase 11 Done

---

## Executive Summary

The Candle Patterns system is a **sequential colour-based candle pattern scanner**. Its primary purpose is to let users define colour sequences (e.g., "after 5 red and 2 green candles, observe 4 red candles") and scan historical OHLCV data for matches. The system also auto-discovers recurring patterns and provides outcome statistics.

### Core Capabilities (Operational)

- ✅ **Sequential Colour Pattern Scanner** — define sequences like `3R -> 2G`, `5R -> Doji -> 3G`, scan 200+ candles
- ✅ **Wildcard Matching** — `3R -> * -> 2G` matches any 1-3 candles between segments
- ✅ **Multi-Sequence Scanning** — scan multiple sequences simultaneously, highlighted on chart
- ✅ **15 Preset Sequences** — common colour patterns ready to use
- ✅ **Auto-Discovery Engine** — automatically finds the most common R/G sequences in data
- ✅ **What-Comes-Next Prediction** — after each sequence occurrence, predicts likely continuation
- ✅ **Outcome Statistics** — win rate, avg return, max gain/loss for each sequence
- ✅ **Yahoo Finance Integration** — fetch real stock/crypto/index data directly from sidebar
- ✅ **Reverse Pattern Finder** — discover what sequences preceded big price moves
- ✅ **Confidence Scoring** — statistical significance (z-score, p-value) for each pattern
- ✅ **Sequence Heatmap** — density visualisation of pattern matches across time buckets
- ✅ **Configurable Hold Period** — adjustable 1-20 candle hold for statistics
- ✅ **Backtesting Tab** — equity curve, Sharpe ratio, max drawdown, profit factor per sequence
- ✅ **Multi-Timeframe Analysis** — scan the same symbol across 1H/4H/Daily/Weekly, detect alignment
- ✅ **Sequence Watchlist** — save/load/export/import sequence libraries with JSON persistence
- ✅ **15 Named Tokens** — Doji, Hammer, InvertedHammer, Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows
- ✅ **Data Feed Caching** — LRU cache with 5-min TTL for Yahoo Finance fetches
- ✅ **Performance Optimization** — vectorized numpy sequence scanning (~50-100x faster), chunked processing for 10K+ datasets, OHLCV-aware downsampling, CandleCache memoization
- ✅ **Sequence Alerts** — SQLite-backed alert rules CRUD, webhook dispatch, alert history, in-dashboard notification panel
- ✅ **Advanced ML Predictor** — GradientBoosting sequence outcome predictor, 17 engineered features, calibrated probabilities, feature importance
- ✅ **User Preferences** — JSON-backed user profiles with theme, defaults, recents, export/import
- ✅ **Live Refresh** — configurable auto-refresh interval (dcc.Interval) for real-time scanning
- ✅ **Email Alert Channel** — SMTP/TLS email alerts alongside webhooks
- ✅ **REST API** — JSON endpoints for scan, discover, portfolio scan, symbol search
- ✅ **Portfolio Scanner** — scan patterns across multiple symbols simultaneously, ranking & summary
- ✅ **Interactive Dashboard** — 12 tabs: Chart, Matches, Discovery, Statistics, Heatmap, Reverse Finder, Backtesting, Multi-TF, Watchlist, Alerts, ML Predict, Settings
- ✅ **CSV ingestion** with OHLCV validation
- ✅ **17 rule-based traditional pattern detectors** (secondary feature)
- ✅ **ML baseline model** (RandomForest classifier)
- ✅ **ML sequence predictor** (GradientBoosting with calibration)
- ✅ **Backtesting engine** with Sharpe ratio & drawdown
- ✅ **SQLite persistence** with 30-day cleanup
- ✅ **CLI tools** (run, cleanup, train, predict, backtest)
- ✅ **Docker containerization** + GitHub Actions CI/CD
- ✅ **315 tests** (279 unit + 36 E2E Playwright, all passing) — 100% pass rate
- ✅ **E2E Playwright test suite** — 36 browser-based tests (Chromium), 11 test classes, full dashboard UI coverage

---

## System Architecture

The system is built around **sequential colour-based pattern scanning** as its primary feature:

```text
User defines sequences (e.g. "5R -> 2G -> 4R")
        ↓
Scanner checks each position in 200 candles
        ↓
Matches highlighted on candlestick chart
        ↓
Statistics: win rate, avg return, predictions
```

### Key Modules

| Module | Purpose |
|---|---|
| `patterns.py` | **Core engine** — sequence parsing, matching, wildcards, discovery, predictions, outcome stats, reverse finder, confidence scoring, heatmap data, 9 named tokens |
| `performance.py` | **Performance optimization** — vectorized numpy scanning, chunked processing, downsampling, CandleCache |
| `alerts.py` | **Sequence alerts** — SQLite-backed rules CRUD, webhook dispatch, alert history, notifications |
| `ml_sequence.py` | **Advanced ML predictor** — GradientBoosting, 17 features, calibrated probabilities, feature importance |
| `preferences.py` | **User preferences** — JSON-backed profiles, defaults, recents, export/import |
| `dashboard.py` | Dash web app — 12 tabs, ~31 callbacks, sequence-focused UI |
| `data_feeds.py` | **Yahoo Finance integration** — fetch real market data (stocks, crypto, indices, forex) + LRU cache |
| `multi_timeframe.py` | **Multi-timeframe analysis** — cross-interval scanning + alignment detection |
| `watchlist.py` | **Sequence watchlist** — save/load/export/import sequence libraries (JSON) |
| `detection.py` | Traditional candlestick pattern detection (17 rules) — secondary |
| `opp_miner.py` | Ordinal pattern mining (complements discovery) |
| `ingestion.py` | CSV validation and loading |
| `storage.py` | SQLite persistence with history |
| `ml_baseline.py` | ML model for pattern classification |
| `backtesting.py` | Performance evaluation engine |
| `cli.py` | Command-line interface (5 commands) |

---

## Recent Progress

### Phase 8 Sprint — REST API, Portfolio Scanner & CI Modernisation (Mar 3, 2026) ✅

1. **Portfolio Scanner Module** (Priority 0)
   - New `portfolio.py` module: `scan_symbol()`, `scan_portfolio()`, `rank_symbols()`, `portfolio_summary()`
   - Threaded multi-symbol scanning with `ThreadPoolExecutor` (configurable `max_workers`)
   - Outcome stats per symbol per sequence (win rate, avg return, max gain/loss)
   - Ranking by total matches, avg win rate, or avg return
   - Aggregate summary (best symbol, best sequence, total matches)
   - Status: ✅ COMPLETE

2. **REST API Module** (Priority 0)
   - New `api.py` module with `register_api_routes()` mounted on Dash's Flask server
   - `GET /api/health` — liveness check with version
   - `GET /api/scan` — scan one symbol for sequences
   - `GET /api/discover` — auto-discover patterns for a symbol
   - `POST /api/portfolio/scan` — scan up to 50 symbols with ranking & summary
   - `GET /api/symbols/search` — search for ticker symbols
   - Auto-registered when dashboard imports
   - Status: ✅ COMPLETE

3. **CI Workflow Modernisation** (Priority 1)
   - `e2e.yml` updated to Python 3.12 + `actions/setup-python@v5`
   - `cleanup.yml` updated to Python 3.12 + `actions/setup-python@v5`
   - `publish.yml` updated to latest action versions (qemu@v3, login@v3, build-push@v6)
   - Status: ✅ COMPLETE

4. **27 New Phase 8 Tests** (Priority 0)
   - Portfolio: scan_symbol (3), scan_portfolio (2), rank_symbols (4), portfolio_summary (2)
   - API: health (1), scan (3), discover (3), portfolio/scan (3), symbols/search (3)
   - CI workflows: content verification (3)
   - Total: **279 tests** (279 passing, 4 skipped)
   - Status: ✅ COMPLETE

### Phase 7 Sprint — Extended Tokens, Email Alerts, Docs & CI Polish (Mar 3, 2026) ✅

1. **6 New Named Tokens** (Priority 0)
   - Added to `match_named_token()` in patterns.py: InvertedHammer, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows
   - Total named tokens: 15 (up from 9)
   - Usable in sequence syntax: `2R -> ThreeWhiteSoldiers`, `3R -> Marubozu`
   - Status: ✅ COMPLETE

2. **Email Alert Channel** (Priority 0)
   - Added `send_email()` function to alerts.py (SMTP-based via `smtplib`)
   - Added `configure_email()` for runtime SMTP configuration (host, port, user, password, TLS)
   - SMTP credentials stored in process memory only — never persisted to disk
   - Alert rules now support `email_to` field alongside `webhook_url`
   - `check_and_trigger()` dispatches to both webhook and email when configured
   - Status: ✅ COMPLETE

3. **Comprehensive README.md** (Priority 0)
   - Complete rewrite reflecting v1.1.0 with all features, 12 tabs, 15 named tokens
   - Quickstart guide, Docker instructions, pattern syntax reference, project structure
   - Status: ✅ COMPLETE

4. **SECURITY.md — GDPR/Security Documentation** (Priority 0)
   - Data handling policy, persistence inventory, credential management
   - Network communication audit (outbound/inbound)
   - GDPR applicability analysis, data deletion instructions
   - Status: ✅ COMPLETE

5. **CI/CD Modernization** (Priority 0)
   - CI matrix expanded to Python 3.10 + 3.12 + 3.14 (with `allow-prereleases`)
   - Updated to `actions/setup-python@v5`
   - Separated Docker build into its own job (runs after tests pass)
   - Lint/format/security scans run once on Python 3.12
   - Dockerfile updated from Python 3.10 to 3.12
   - Status: ✅ COMPLETE

6. **27 New Phase 7 Tests** (Priority 0)
   - Named tokens: InvertedHammer (2), Marubozu (6), ThreeWhiteSoldiers (4), ThreeBlackCrows (3), sequence integration (2)
   - Email alerts: configure_email (2), send_email (5), alert rule email_to (3)
   - Total: **252 tests** (252 passing, 4 skipped)
   - Status: ✅ COMPLETE

### Phase 6 Sprint — Performance, Alerts, ML Predictor, Preferences & Live Refresh (Mar 3, 2026) ✅

1. **Performance Optimization Module** (Priority 0)
   - New `performance.py` module: `vectorized_symbol_sequence()` (numpy-accelerated R/G/Doji classification, ~50-100x faster than row-by-row), `vectorized_find_sequence()` (numpy-level sequence matching for simple tokens), `process_in_chunks()` (overlapping chunk scanning for 10K+ datasets), `downsample_ohlcv()` (OHLCV-aware chart downsampling preserving open/high/low/close semantics), `CandleCache` (memoizes symbol arrays keyed by df id+length), `batch_sequence_stats()` (multi-sequence), `dataset_info()` (size metadata for performance decisions)
   - Status: ✅ COMPLETE

2. **Sequence Alerts System** (Priority 0)
   - New `alerts.py` module with SQLite-backed alert rules and history
   - `add_alert_rule()` / `list_alert_rules()` / `remove_alert_rule()` / `toggle_alert_rule()` (CRUD)
   - `record_alert()` / `get_alert_history()` / `acknowledge_alert()` / `clear_alert_history()` (history)
   - `send_webhook()` dispatches POST JSON to configurable URL via urllib
   - `check_and_trigger()` evaluates all enabled rules against DataFrame, fires webhooks, records alerts
   - New "Alerts" dashboard tab with rule form, rules table, history table
   - Status: ✅ COMPLETE

3. **Advanced ML Sequence Predictor** (Priority 0)
   - New `ml_sequence.py` module: `engineer_sequence_features()` builds 17 features (hl_ratio, oc_ratio, body_pct, upper/lower_wick_ratio, is_green, streak_length, mom_3/5/10, rsi_14, volatility_5/10, volume_ma_5, volume_ratio, rolling_green_pct, doji_density_10)
   - `SequencePredictor` class: GradientBoosting with optional CalibratedClassifierCV probability calibration
   - Methods: `train()`, `predict()`, `cross_validate()`, `feature_importance()`, `save()`/`load()`, `predict_next_outcome()`
   - `train_sequence_predictor()` convenience function
   - New "ML Predict" dashboard tab: hold period slider, train button, metrics cards, prediction display, feature importance
   - Status: ✅ COMPLETE

4. **User Preferences** (Priority 0)
   - New `preferences.py` module: JSON-backed user profiles at `data/preferences.json`
   - 25+ configurable keys: theme, default_sequences, default_symbol, default_period/interval, hold_period, lookahead, chart_style, live_refresh settings, etc.
   - `load_preferences()` / `save_preferences()` / `get_preference()` / `set_preference()` / `reset_preferences()`
   - `add_recent_symbol()` / `add_recent_sequence()` (deduped, max 10)
   - `export_preferences()` / `import_preferences()` (JSON backup/sharing)
   - New "Settings" dashboard tab: default symbol/period/interval, hold period, live refresh toggle/interval, discovery max, save/reset buttons, dataset info
   - Status: ✅ COMPLETE

5. **Live Refresh** (Priority 0)
   - Added `dcc.Interval(id='live-interval')` component (60s default, disabled by default)
   - Settings tab toggle enables/disables live refresh with configurable interval
   - Auto-fetches Yahoo Finance data on interval tick via `on_live_refresh` callback
   - Status: ✅ COMPLETE

6. **Dashboard Integration** (Priority 0)
   - 3 new tabs: Alerts, ML Predict, Settings (12 total)
   - ~10 new callbacks for alerts CRUD, ML train/predict, preferences save/reset, live refresh
   - `dcc.Store` components for live symbol and ML model state
   - Status: ✅ COMPLETE

7. **56 New Phase 6 Tests** (Priority 0)
   - Performance: vectorized_symbol_sequence (4), vectorized_find_sequence (3), downsample_ohlcv (3), chunked_processing (2), CandleCache (3), dataset_info (2), batch_sequence_stats (1)
   - Alerts: rule CRUD (3), alert history (4), check_and_trigger (2), webhook (2)
   - ML: engineer_sequence_features (3), SequencePredictor (5), train_sequence_predictor (2)
   - Preferences: load/save (4), get/set (3), recents (4), export/import (3)
   - Dashboard integration: importable (1), new tabs in layout (1), live interval (1)
   - Total: **225 tests** (225 passing, 4 skipped)
   - Status: ✅ COMPLETE

### Phase 5 Sprint — Multi-TF, Backtesting, Watchlist & Tokens (Feb 24, 2026) ✅

1. **Multi-Timeframe Analysis** (Priority 0)
   - New `multi_timeframe.py` module: `fetch_multi_timeframe()`, `scan_multi_timeframe()`, `detect_alignment()`, `multi_timeframe_summary()`
   - New "Multi-TF" dashboard tab with symbol input, timeframe picker, lookback control
   - Per-timeframe summary table + alignment percentage matrix
   - Status: ✅ COMPLETE

2. **Backtesting Dashboard Tab** (Priority 0)
   - New 7th tab integrating `BacktestEngine` from backtesting.py
   - Per-sequence equity curve (Plotly line chart), Sharpe ratio, max drawdown, profit factor
   - Configurable hold period + initial capital
   - Status: ✅ COMPLETE

3. **Sequence Watchlist** (Priority 0)
   - New `watchlist.py` module: add, remove, update, clear, export, import
   - JSON persistence at `data/watchlist.json`
   - New "Watchlist" dashboard tab with save form + entries table
   - Status: ✅ COMPLETE

4. **Extended Named Tokens** (Priority 0)
   - `match_named_token()` now supports 9 pattern types: Doji, Hammer, Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop
   - Usable in sequence syntax: `2R -> Engulfing`, `3R -> MorningStar`
   - Status: ✅ COMPLETE

5. **Data Feed Caching** (Priority 0)
   - LRU cache (50 entries, 5-min TTL) in `data_feeds.py`
   - `cache_get/put/clear/stats` functions
   - Avoids redundant Yahoo Finance API calls within same session
   - Status: ✅ COMPLETE

6. **42 New Tests** (Priority 0)
   - Multi-timeframe (7), Watchlist (11), Cache (6), Named tokens (10), Backtest integration (6), Sequence scanning (2)
   - Total: 169 tests (169 passing, 4 skipped)
   - Status: ✅ COMPLETE

### Phase 5.1 Enhancement — Followup Sequence Outcome Tracking (Apr 2026) ⏳
1. **Pattern + Followup Counter** (Priority 0)
   - New helper in `patterns.py`: `count_followup_pattern(df, base_seq, follow_seq, follow_len)`
   - Uses existing `find_sequence_occurrences()` for `base_seq`, checks `follow_seq` in subsequent `follow_len` candles
   - Outputs total hits, followup hits, success rate, and failed indices
2. **Scanner UI Integration** (Priority 0)
   - Add `followup-sequence` + `followup-length` in `Sequence Matches` tab form
   - Display computed followup statistics next to existing sequence metrics
3. **E2E + Unit tests** (Priority 0)
   - `tests/test_sequence_patterns.py`: synthethic cases for `3R -> 3G` followed by `5R`, assert count/rate
   - e2e flow: “set followup 5R, run scan, validate follow-up count in output table”
4. **Optional: aggregated followup analysis** (Priority 1)
   - Show “Top follow-up outcomes” (e.g. 5R, 4G) for a selected base pattern

(This is the next planned increment after Phase 5 core features.)

### Phase 4 Sprint — Data & Analytics Enhancement (Feb 24, 2026) ✅

1. **Yahoo Finance Integration** (Priority 0)
   - New `data_feeds.py` module with `fetch_yahoo_data()`, `search_symbols()`, `get_symbol_info()`
   - Sidebar section: symbol input, popular symbol quick-picks (stocks, crypto, indices, forex, ETFs)
   - Period selector (1d to max), interval selector (1m to 1mo)
   - Fetch button loads real OHLCV data directly into the scanner
   - Status: ✅ COMPLETE

2. **Reverse Pattern Finder** (Priority 0)
   - New `reverse_pattern_finder()` function in patterns.py
   - Answers: "What colour sequences preceded big price moves?"
   - Configurable threshold (%), direction (up/down/both), lookback depth
   - New "Reverse Finder" dashboard tab with controls and results table
   - Includes inline confidence scoring for each discovered pattern
   - Status: ✅ COMPLETE

3. **Statistical Confidence Scoring** (Priority 0)
   - New `sequence_confidence()` function in patterns.py
   - Z-score, p-value, confidence level for each sequence's edge
   - Compares sequence returns against random baseline (1000 samples)
   - Integrated into Statistics tab (shown per-sequence) and Reverse Finder
   - Significance levels: Very High (p<0.01), High (p<0.05), Moderate (p<0.10), Low
   - Status: ✅ COMPLETE

4. **Sequence Heatmap** (Priority 0)
   - New `sequence_heatmap_data()` function in patterns.py
   - New "Heatmap" dashboard tab with Plotly heatmap visualisation
   - Shows pattern match density across time buckets (10 candles each)
   - Darker cells = more pattern concentration
   - Status: ✅ COMPLETE

5. **Configurable Hold Period & Lookahead** (Priority 0)
   - Statistics tab now has sliders: Hold Period (1-20 candles), Lookahead (1-10 candles)
   - All stats and predictions update dynamically when sliders change
   - Status: ✅ COMPLETE

6. **Test Suite Expansion** (Priority 0)
   - Added 31 new tests for Phase 4 features (test_phase4_features.py)
   - Covers: data_feeds constants/validation, reverse_pattern_finder, sequence_confidence,
     sequence_heatmap_data, integration tests
   - Total: 127 tests (127 passing, 4 skipped)
   - Status: ✅ COMPLETE

### Phase 3 Sprint — Sequential Engine (Feb 24, 2026) ✅

1. **Pivoted Dashboard to Sequential Focus** (Priority 0)
   - Rewrote entire dashboard from traditional-pattern-focused to sequence-scanning-focused
   - 15 preset colour sequences in sidebar
   - Multi-sequence scanning with simultaneous chart highlighting
   - Auto-Discovery tab finds recurring patterns automatically
   - Status: ✅ COMPLETE

2. **Added Wildcard Sequence Matching** (Priority 0)
   - New `find_wildcard_sequence()` function in patterns.py
   - Syntax: `3R -> * -> 2G` where `*` matches any 1-3 candles
   - Recursive matcher supports multiple wildcards
   - Full test coverage (4 tests)
   - Status: ✅ COMPLETE

3. **Added What-Comes-Next Prediction** (Priority 0)
   - New `what_comes_next()` function — analyses continuation after sequences
   - Shows R/G/Doji distribution for next 3 candles
   - Visual probability bars in Statistics tab
   - Most-likely-continuation string (e.g., "2R -> 1G")
   - Status: ✅ COMPLETE

4. **Added Sequence Outcome Statistics** (Priority 0)
   - New `sequence_outcome_stats()` function
   - Win rate, avg return, median return, max gain/loss over 5-candle hold
   - Displayed in Statistics & Predictions tab with colour-coded cards
   - Also shown inline in Auto-Discovery table
   - Status: ✅ COMPLETE

5. **Added Statistics & Predictions Tab** (Priority 0)
   - 4th dashboard tab showing per-sequence outcome analysis
   - Win rate, avg/max return cards
   - What-Comes-Next prediction tables with visual bars
   - Auto-populates when sequences are scanned
   - Status: ✅ COMPLETE

6. **Enhanced Auto-Discovery Tab** (Priority 1)
   - Discovery table now includes Win Rate and Avg Return columns
   - Each discovered sequence has inline outcome statistics
   - Status: ✅ COMPLETE

7. **Comprehensive Test Suite Expansion** (Priority 0)
   - Added 42 new tests for sequential pattern functions
   - Covers: parse_sequence, symbol_sequence, find_sequence_occurrences,
     sequence_length, \_run\_length\_encode, discover_color_sequences,
     find_wildcard_sequence, what_comes_next, sequence_outcome_stats
   - Total: 96 tests (96 passing, 2 E2E skipped)
   - Status: ✅ COMPLETE

### Phase 2 Sprint (Feb 22, 2026) ✅

- Dashboard overhaul (10+ critical bugs fixed)
- Pattern expansion (12 → 17 traditional detectors)
- ML-CLI integration (train/predict/backtest commands)
- See previous commit history for details

### Phase 1 / MVP ✅

- CSV ingestion, pattern detection, dashboard, ML baseline, backtesting
- SQLite persistence, CLI tools, Docker, CI/CD, Release v0.1.0

---

## Dashboard — 12 Tabs

| Tab | Purpose |
|---|---|
| **Candlestick Chart** | Interactive OHLCV chart with sequence match highlights (coloured rectangles + legend) |
| **Sequence Matches** | Detailed table of every match per sequence — candle range, timestamps |
| **Auto-Discovery** | Top 25 recurring colour sequences found automatically, with win rate + avg return |
| **Statistics & Predictions** | Per-sequence outcome stats (win rate, return, confidence) + what-comes-next predictions + configurable hold/lookahead |
| **Heatmap** | Pattern density heatmap across time buckets — shows where patterns cluster |
| **Reverse Finder** | Find sequences that preceded big price moves — configurable threshold, direction, lookback |
| **Backtesting** | Per-sequence equity curve, Sharpe ratio, max drawdown, profit factor, win rate |
| **Multi-TF** | Cross-timeframe sequence alignment — scan same symbol at 1H/4H/Daily/Weekly |
| **Watchlist** | Save/load sequence libraries with labels, symbols, notes |
| **Alerts** | Sequence alert rules — add/toggle/remove rules, webhook URL, alert history with ack |
| **ML Predict** | Advanced ML sequence predictor — train GradientBoosting model, view metrics, predict next outcome, feature importance |
| **Settings** | User preferences — default symbol/period/interval, hold period, live refresh toggle/interval, save/reset |

### Sidebar Features

- Upload CSV / Load Sample Data (200 candles)
- **Yahoo Finance**: fetch real data by symbol, period, interval
- Popular symbols quick-pick: Stocks, Crypto, Indices, ETFs, Forex
- Date range filter
- **Sequence Scanner**: preset dropdown (15 sequences) + custom textarea + wildcard support
- History browser (SQLite)
- Export: Matches CSV, Discovery CSV, Chart PNG
- Maintenance: run cleanup

---

## Features — All Complete

| Feature | Status | Notes |
|---|---|---|
| Sequential Pattern Scanner | DONE | Core feature — multi-sequence, wildcard, chart highlights |
| Auto-Discovery Engine | DONE | Finds top recurring R/G sequences automatically |
| What-Comes-Next Prediction | DONE | R/G/Doji probability analysis after each sequence |
| Sequence Outcome Statistics | DONE | Win rate, avg return, max gain/loss per sequence |
| Wildcard Matching | DONE | `*` matches any 1-3 candles in sequences |
| 15 Preset Sequences | DONE | Common colour patterns ready in sidebar |
| Yahoo Finance Integration | DONE | Fetch real market data (stocks, crypto, indices, forex, ETFs) |
| Reverse Pattern Finder | DONE | Find sequences preceding big moves |
| Confidence Scoring | DONE | Z-score, p-value, significance for each pattern |
| Sequence Heatmap | DONE | Density visualisation across time buckets |
| Configurable Hold Period | DONE | 1-20 candle slider in Statistics tab |
| Backtesting Tab | DONE | Equity curve, Sharpe, drawdown, profit factor per sequence |
| Multi-Timeframe Analysis | DONE | Cross-interval scanning + alignment detection |
| Sequence Watchlist | DONE | Save/load/export/import sequence libraries |
| Extended Named Tokens | DONE | **15 types**: Doji, Hammer, InvertedHammer, Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows |
| Data Feed Caching | DONE | LRU cache with 5-min TTL for Yahoo Finance |
| CSV Ingestion | DONE | OHLCV validation, multiple format support |
| Traditional Pattern Detection | DONE | **17 patterns** (secondary feature) |
| Dashboard | DONE | **12 tabs**, ~31 callbacks, modern UI |
| SQLite Persistence | DONE | 30-day auto-cleanup + alert rules/history |
| CLI Tools | DONE | 5 commands: run, cleanup, train, predict, backtest |
| ML Baseline | DONE | RandomForest with feature engineering |
| ML Sequence Predictor | DONE | GradientBoosting, 17 features, calibrated probabilities |
| Performance Optimization | DONE | Vectorized numpy scanning, chunked processing, downsampling, cache |
| Sequence Alerts | DONE | SQLite rules CRUD, webhook + email dispatch, history, dashboard tab |
| Email Alert Channel | DONE | SMTP-based email notifications, runtime config, TLS support |
| User Preferences | DONE | JSON-backed profiles, defaults, recents, export/import |
| Live Refresh | DONE | Configurable auto-refresh interval for real-time scanning |
| REST API | DONE | JSON endpoints: /api/health, /api/scan, /api/discover, /api/portfolio/scan, /api/symbols/search |
| Portfolio Scanner | DONE | Multi-symbol threaded scanning, ranking, summary |
| Backtesting | DONE | Sharpe ratio, drawdown, win rate, profit factor |
| Unit Tests | DONE | **279 tests** (279 passing, 4 skipped) — 100% |
| Docker | DONE | Multi-stage build (Python 3.12), CI automation |
| CI/CD | DONE | GitHub Actions: Python 3.10/3.12/3.14 matrix, lint, test, security, Docker |
| SECURITY.md | DONE | GDPR/security documentation, data handling policy |
| Release v0.1.0 | DONE | Published and tagged |

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
Marubozu       → Full-body candle (bull or bear, body ≥ 90% of range)
BullMarubozu   → Bullish full-body candle
BearMarubozu   → Bearish full-body candle
ThreeWhiteSoldiers → Three consecutive bullish candles (rising closes)
ThreeBlackCrows    → Three consecutive bearish candles (falling closes)
*        → wildcard (matches any 1-3 candles)
->       → separator between segments

Examples:
  3R -> 2G                  Three red followed by two green
  5R -> 3G                  Five red followed by three green
  2R -> Doji -> 2G          Two red, a doji, then two green
  3R -> * -> 2G             Three red, any 1-3 candles, then two green
  2R -> Engulfing           Two red then an engulfing pattern
  3R -> MorningStar         Three red then a morning star reversal
  2R -> ThreeWhiteSoldiers  Two red then three white soldiers
  1R -> 1G -> 1R -> 1G     Alternating red-green-red-green
```

---

## Test Coverage Report

```text
Unit Tests: 279/279 PASSING ✅ (4 skipped: 2 E2E + 2 network)

├── Sequence Pattern Tests ........... 42 tests ✅  (Phase 3)
│   ├── ParseSequence ................ 6 tests
│   ├── SequenceLength ............... 4 tests
│   ├── RunLengthEncode .............. 5 tests
│   ├── SymbolSequence ............... 3 tests
│   ├── FindSequenceOccurrences ...... 5 tests
│   ├── DiscoverColorSequences ....... 5 tests
│   ├── MatchNamedToken .............. 3 tests
│   ├── FindWildcardSequence ......... 4 tests
│   ├── WhatComesNext ................ 3 tests
│   └── SequenceOutcomeStats ......... 4 tests
├── Phase 4 Feature Tests ............ 31 tests ✅  (Phase 4)
│   ├── DataFeedsConstants ........... 4 tests
│   ├── FetchYahooData ............... 4 tests (1 network skip)
│   ├── SearchSymbols ................ 2 tests (1 network skip)
│   ├── ReversePatternFinder ......... 7 tests
│   ├── SequenceConfidence ........... 6 tests
│   ├── SequenceHeatmapData .......... 7 tests
│   └── PatternsIntegration .......... 3 tests
├── Phase 5 Feature Tests ............ 42 tests ✅  (Phase 5)
│   ├── MultiTimeframeModule ......... 7 tests
│   ├── Watchlist .................... 11 tests
│   ├── DataFeedCache ................ 6 tests
│   ├── NamedTokens .................. 10 tests
│   ├── BacktestIntegration .......... 6 tests
│   └── NamedTokenSequenceScanning ... 2 tests
├── Phase 6 Feature Tests ............ 56 tests ✅  (Phase 6)
│   ├── VectorizedSymbolSequence ..... 4 tests
│   ├── VectorizedFindSequence ....... 3 tests
│   ├── DownsampleOhlcv .............. 3 tests
│   ├── ChunkedProcessing ............ 2 tests
│   ├── CandleCache .................. 3 tests
│   ├── DatasetInfo .................. 2 tests
│   ├── BatchSequenceStats ........... 1 test
│   ├── AlertRuleCRUD ................ 3 tests
│   ├── AlertHistory ................. 4 tests
│   ├── CheckAndTrigger .............. 2 tests
│   ├── WebhookDispatch .............. 2 tests
│   ├── EngineerSequenceFeatures ..... 3 tests
│   ├── SequencePredictor ............ 5 tests
│   ├── TrainSequencePredictor ....... 2 tests
│   ├── PreferencesLoadSave .......... 4 tests
│   ├── PreferencesGetSet ............ 3 tests
│   ├── PreferencesRecents ........... 4 tests
│   ├── PreferencesExportImport ...... 3 tests
│   └── DashboardPhase6 .............. 3 tests
├── Phase 7 Feature Tests ............ 27 tests ✅  (Phase 7)
│   ├── InvertedHammer ............... 2 tests
│   ├── Marubozu ..................... 6 tests
│   ├── ThreeWhiteSoldiers ........... 4 tests
│   ├── ThreeBlackCrows .............. 3 tests
│   ├── NamedTokenInSequence ......... 2 tests
│   ├── ConfigureEmail ............... 2 tests
│   ├── SendEmail .................... 5 tests
│   └── AlertRuleEmailTo ............. 3 tests
├── Phase 8 Feature Tests ............ 27 tests ✅  ← NEW (Phase 8)
│   ├── ScanSymbol ................... 3 tests
│   ├── ScanPortfolio ................ 2 tests
│   ├── RankSymbols .................. 4 tests
│   ├── PortfolioSummary ............. 2 tests
│   ├── ApiHealth .................... 1 test
│   ├── ApiScan ...................... 3 tests
│   ├── ApiDiscover .................. 3 tests
│   ├── ApiPortfolioScan ............. 3 tests
│   ├── ApiSymbolSearch .............. 3 tests
│   └── WorkflowFiles ............... 3 tests
├── Detection Tests .................. 1 test  ✅
├── Ingestion Tests .................. 2 tests ✅
├── Storage Tests .................... 4 tests ✅
├── Dashboard Tests .................. 2 tests ✅
├── CLI Tests (run/cleanup) .......... 2 tests ✅
├── CLI ML Tests (train/predict/bt)... 6 tests ✅
├── ML Baseline Tests ................ 9 tests ✅
├── ML PoC Tests ..................... 1 test  ✅
├── Backtesting Tests ................ 10 tests ✅
├── Backtest Module Tests ............ 2 tests ✅
├── OPP Mining Tests ................. 5 tests ✅
├── New Pattern Tests ................ 10 tests ✅
├── Pattern Catalog Tests ............ 1 test  ✅
├── Integration Tests ................ 1 test  ✅
└── Placeholder ...................... 1 test  ✅

E2E Tests: 2 skipped (documented reason)
Network Tests: 2 skipped (enable for integration testing)
Execution Time: ~153 seconds
Platform: Windows 10, Python 3.14.0, pytest-9.0.2
```

---

## Architecture Overview

```bash
candle-patterns/
├── src/candle_patterns/
│   ├── __main__.py ..................... CLI entry point
│   ├── cli.py .......................... Command-line interface (5 commands)
│   ├── ingestion.py .................... CSV validation
│   ├── patterns.py ..................... CORE: sequential pattern engine
│   │   ├── parse_sequence()            Parse "3R -> 2G" into tokens
│   │   ├── find_sequence_occurrences() Find all matches in data
│   │   ├── find_wildcard_sequence()    Wildcard matching (* = any 1-3)
│   │   ├── discover_color_sequences()  Auto-discover recurring patterns
│   │   ├── what_comes_next()           Predict continuation after sequence
│   │   ├── sequence_outcome_stats()    Win rate, returns after sequence
│   │   ├── reverse_pattern_finder()    Find sequences preceding big moves
│   │   ├── sequence_confidence()       Statistical significance scoring
│   │   ├── sequence_heatmap_data()     Pattern density across time buckets
│   │   └── match_named_token()        15 tokens: Doji, Hammer, Engulfing, etc.
│   ├── data_feeds.py ................... Yahoo Finance + LRU cache
│   │   ├── fetch_yahoo_data()          Fetch OHLCV (cached)
│   │   ├── search_symbols()            Symbol search/autocomplete
│   │   ├── cache_get/put/clear/stats   In-memory LRU cache
│   │   └── get_symbol_info()           Symbol metadata
│   ├── performance.py ................. Performance optimization
│   │   ├── vectorized_symbol_sequence() Numpy-accelerated R/G/Doji
│   │   ├── vectorized_find_sequence()   Numpy sequence matching
│   │   ├── process_in_chunks()         Overlapping chunk scanning
│   │   ├── downsample_ohlcv()          OHLCV-aware downsampling
│   │   ├── CandleCache                 Memoize symbol arrays
│   │   ├── batch_sequence_stats()       Multi-sequence stats
│   │   └── dataset_info()              Size metadata
│   ├── alerts.py ...................... Sequence alert system
│   │   ├── add/list/remove/toggle_rule  CRUD for alert rules
│   │   ├── record/get/ack/clear_alert   Alert history
│   │   ├── send_webhook()              POST JSON to URL
│   │   ├── configure_email()           SMTP settings (in-memory)
│   │   ├── send_email()                Email via SMTP/TLS
│   │   └── check_and_trigger()         Evaluate rules & fire (webhook + email)
│   ├── ml_sequence.py ................. Advanced ML predictor
│   │   ├── engineer_sequence_features() 17 features
│   │   ├── SequencePredictor            GradientBoosting + calibration
│   │   └── train_sequence_predictor()   Convenience wrapper
│   ├── preferences.py ................. User preferences
│   │   ├── load/save_preferences()      JSON persistence
│   │   ├── get/set_preference()         Individual key access
│   │   ├── add_recent_symbol/sequence() Deduped recents (max 10)
│   │   └── export/import_preferences()  JSON backup/sharing
│   ├── multi_timeframe.py .............. Multi-TF analysis
│   │   ├── fetch_multi_timeframe()     Fetch at multiple intervals
│   │   ├── scan_multi_timeframe()      Scan sequences per TF
│   │   ├── detect_alignment()          Find recent cross-TF alignment
│   │   └── multi_timeframe_summary()   Convenience wrapper
│   ├── watchlist.py .................... Sequence library persistence
│   │   ├── add_to_watchlist()          Save sequences with label/symbol
│   │   ├── remove/update/clear()       CRUD operations
│   │   └── export/import_watchlist()   JSON export/import
│   ├── detection.py .................... Traditional pattern detectors (17)
│   ├── portfolio.py .................... Multi-symbol portfolio scanning
│   │   ├── scan_symbol()               Fetch & scan one symbol
│   │   ├── scan_portfolio()            Threaded multi-symbol scanning
│   │   ├── rank_symbols()              Rank by matches/win_rate/return
│   │   └── portfolio_summary()         Aggregate stats across symbols
│   ├── api.py .......................... REST API endpoints (Flask)
│   │   ├── /api/health                 Liveness check
│   │   ├── /api/scan                   Scan one symbol
│   │   ├── /api/discover               Auto-discover patterns
│   │   ├── /api/portfolio/scan         Multi-symbol portfolio scan
│   │   └── /api/symbols/search         Ticker symbol search
│   ├── dashboard.py .................... Dash web app (12 tabs, ~31 callbacks)
│   ├── opp_miner.py .................... Ordinal pattern mining
│   ├── storage.py ...................... SQLite persistence
│   ├── ml_baseline.py .................. ML model (RandomForest)
│   ├── backtesting.py .................. Performance evaluation (Sharpe, equity curve)
│   └── reporting.py .................... Report generation
├── tests/ .............................. 279 unit tests (100% passing)
├── Dockerfile .......................... Multi-stage build (Python 3.12)
├── .github/workflows/ .................. CI/CD (ci.yml, e2e.yml, cleanup.yml, publish.yml)
├── data/ ............................... Sample datasets + watchlist.json
└── docs/ ............................... Documentation
```

---

## System Audit (Mar 3, 2026 — Post Phase 8)

✅ **Core Purpose**: Sequential colour pattern scanning — **FULLY OPERATIONAL**  
✅ **Code Repository**: Clean, all changes committed  
✅ **Test Suite**: **279/279 passing** (100% of executed tests, 4 skipped)  
✅ **Dashboard**: 12 tabs — Chart, Matches, Discovery, Statistics, Heatmap, Reverse Finder, Backtesting, Multi-TF, Watchlist, Alerts, ML Predict, Settings  
✅ **Pattern Engine**: parse, match, wildcard, discover, predict, statistics, reverse, confidence, heatmap, 15 named tokens  
✅ **Data Sources**: CSV upload + Yahoo Finance API (cached, stocks, crypto, indices, forex, ETFs)  
✅ **REST API**: 5 JSON endpoints (/api/health, /api/scan, /api/discover, /api/portfolio/scan, /api/symbols/search)  
✅ **Portfolio Scanner**: Threaded multi-symbol scanning, ranking, aggregated summary  
✅ **Multi-Timeframe**: Cross-interval scanning + alignment detection  
✅ **Backtesting**: Equity curve, Sharpe ratio, drawdown, profit factor per sequence  
✅ **Watchlist**: Save/load/export/import sequence libraries  
✅ **Performance**: Vectorized numpy scanning, chunked processing (10K+), OHLCV downsampling, CandleCache  
✅ **Alerts**: SQLite-backed rules CRUD, webhook + email dispatch, alert history, dashboard tab  
✅ **ML Predictor**: GradientBoosting + calibration, 17 features, feature importance, save/load  
✅ **Preferences**: JSON-backed profiles, defaults, recents, export/import  
✅ **Live Refresh**: Configurable auto-refresh interval for real-time scanning  
✅ **Sample Data**: Auto-loads (200 candles)  
✅ **Module Imports**: Clean (~31 registered callbacks)  
✅ **CLI**: 5 commands operational (run, cleanup, train, predict, backtest)  
✅ **CI/CD**: GitHub Actions (Python 3.10/3.12/3.14 matrix) + Docker (3.12-slim) + GHCR publish  
✅ **Security**: SECURITY.md — GDPR analysis, credential handling, data deletion  
✅ **Documentation**: README.md (comprehensive), SECURITY.md, PATTERN_CATALOG.md  

**Audit Status**: PASS — Phase 8 complete, system fully operational, v1.2.0 released

---

## Performance Metrics

| Metric | Value | Context |
|---|---|---|
| Test Suite Time | ~153s | All 279 tests on Windows |
| Dashboard Callbacks | ~31 | Lean, no duplicate outputs |
| Dashboard Load | <2s | 200 candles + auto-discovery |
| Sequence Scan | <500ms | 15 sequences against 200 candles |
| Vectorized Scan | <50ms | Numpy-accelerated for 10K+ candles |
| Chunk Processing | <2s | 10K+ candles, 5K chunks with overlap |
| Downsampling | <100ms | OHLCV-aware to target size |
| Auto-Discovery | <200ms | Scan lengths 3-8, top 25 |
| What-Comes-Next | <100ms | Per sequence prediction |
| Outcome Stats | <100ms | Per sequence, configurable hold |
| Reverse Finder | <500ms | Scan for preceding patterns |
| Confidence Score | <200ms | Z-score + p-value calculation |
| Heatmap Data | <200ms | Density across time buckets |
| Yahoo Finance Fetch | 1-3s | Depends on period/interval (cached after 1st) |
| Multi-TF Analysis | 3-10s | Depends on # timeframes (cached) |
| ML Training | 1-5s | GradientBoosting on 200 candles |
| Alert Evaluation | <100ms | Check all enabled rules |
| Watchlist Save/Load | <50ms | JSON file I/O |
| Preferences Load | <10ms | JSON file I/O |

---

## Decision Log

### Decision 1: System Focus — Sequential Colour Patterns

**Status**: ✅ IMPLEMENTED (Phase 3)  
**Choice**: Sequential colour-based scanning (R/G/Doji) as PRIMARY feature  
**Rationale**: User's core vision — "find patterns of sequence, like after 5 red and 2 green then we see 4 red candles"  
**Impact**: Dashboard restructured, traditional patterns made secondary

### Decision 2: Test Framework

**Status**: ✅ IMPLEMENTED  
**Choice**: pytest with comprehensive coverage  
**Rationale**: Industry standard, CI integration

### Decision 3: Pattern Syntax

**Status**: ✅ IMPLEMENTED  
**Choice**: `NR -> NG -> Doji` with `*` wildcards  
**Rationale**: Human-readable, flexible, expandable

### Decision 4: ML Framework

**Status**: ✅ IMPLEMENTED  
**Choice**: scikit-learn RandomForest (expandable)  
**Rationale**: Mature, interpretable, good baseline

---

## Phase 8 Tasks — Status

| ID | Task | Priority | Status | Notes |
|---|---|---|---|---|
| 90 | Portfolio scanner module | P0 | ✅ DONE | portfolio.py: scan_symbol, scan_portfolio (threaded), rank_symbols, portfolio_summary |
| 91 | REST API module | P0 | ✅ DONE | api.py: /api/health, /api/scan, /api/discover, /api/portfolio/scan, /api/symbols/search |
| 92 | API auto-registration | P1 | ✅ DONE | register_api_routes() called in dashboard.py on app startup |
| 93 | CI workflow modernisation | P1 | ✅ DONE | e2e.yml, cleanup.yml → Python 3.12 + v5; publish.yml → latest actions |
| 94 | 27 new Phase 8 tests | P0 | ✅ DONE | 279 total tests, 0 failures |
| 95 | Documentation update | P0 | ✅ DONE | PROJECT_PLAN.md, PROGRESS_SUMMARY.md |

## Phase 7 Tasks — Status

| ID | Task | Priority | Status | Notes |
|---|---|---|---|---|
| 82 | Extended named tokens (6 new) | P0 | ✅ DONE | InvertedHammer, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows |
| 83 | Email alert channel | P0 | ✅ DONE | configure_email(), send_email(), SMTP/TLS, integrated with check_and_trigger |
| 84 | README.md comprehensive rewrite | P0 | ✅ DONE | Features, quickstart, syntax reference, project structure |
| 85 | SECURITY.md (GDPR/security) | P0 | ✅ DONE | Data handling, credentials, GDPR analysis, data deletion |
| 86 | CI modernisation | P1 | ✅ DONE | Python 3.10/3.12/3.14 matrix, separated Docker job |
| 87 | Dockerfile update | P1 | ✅ DONE | Python 3.10 → 3.12-slim |
| 88 | 27 new Phase 7 tests | P0 | ✅ DONE | 252 total tests, 0 failures |
| 89 | Documentation update | P0 | ✅ DONE | PROJECT_PLAN.md, PROGRESS_SUMMARY.md |

## Phase 6 Tasks — Status

| ID | Task | Priority | Status | Notes |
|---|---|---|---|---|
| 72 | Performance optimization module | P0 | ✅ DONE | performance.py: vectorized scanning, chunking, downsampling, cache |
| 73 | Sequence alerts module | P0 | ✅ DONE | alerts.py: SQLite rules CRUD, webhook, history |
| 74 | Alerts dashboard tab | P0 | ✅ DONE | Rule form, rules table, history table |
| 75 | Advanced ML predictor module | P0 | ✅ DONE | ml_sequence.py: GradientBoosting, 17 features, calibration |
| 76 | ML Predict dashboard tab | P0 | ✅ DONE | Train button, metrics, prediction, feature importance |
| 77 | User preferences module | P0 | ✅ DONE | preferences.py: JSON profiles, defaults, recents, export/import |
| 78 | Settings dashboard tab | P0 | ✅ DONE | Default settings, live refresh toggle, save/reset |
| 79 | Live refresh (dcc.Interval) | P0 | ✅ DONE | Configurable auto-refresh for real-time scanning |
| 80 | 56 new Phase 6 tests | P0 | ✅ DONE | 225 total tests, 0 failures |
| 81 | Documentation update | P0 | ✅ DONE | PROJECT_PLAN.md, PROGRESS_SUMMARY.md |

## Phase 5 Tasks — Status

| ID | Task | Priority | Status | Notes |
|---|---|---|---|---|
| 63 | Multi-Timeframe module | P0 | ✅ DONE | multi_timeframe.py: fetch, scan, alignment, summary |
| 64 | Multi-TF dashboard tab | P0 | ✅ DONE | Symbol input, TF picker, alignment table |
| 65 | Backtesting dashboard tab | P0 | ✅ DONE | Equity curve, Sharpe, drawdown, profit factor |
| 66 | Watchlist module | P0 | ✅ DONE | watchlist.py: CRUD, export/import, JSON persistence |
| 67 | Watchlist dashboard tab | P0 | ✅ DONE | Save form + entries table |
| 68 | Extended named tokens | P0 | ✅ DONE | 9 types in match_named_token() |
| 69 | Data feed caching | P0 | ✅ DONE | LRU cache (50 entries, 5-min TTL) |
| 70 | 42 new Phase 5 tests | P0 | ✅ DONE | 169 total tests |
| 71 | Documentation update | P0 | ✅ DONE | PROJECT_PLAN.md, PHASE_2_AUTONOMY_PLAN.md |

## Phase 4 Tasks — Status

| ID | Task | Priority | Status | Notes |
|---|---|---|---|---|
| 51 | Yahoo Finance data_feeds.py module | P0 | ✅ DONE | fetch_yahoo_data, search_symbols, get_symbol_info |
| 52 | Yahoo Finance sidebar integration | P0 | ✅ DONE | Symbol input, popular picks, period/interval |
| 53 | Reverse Pattern Finder engine | P0 | ✅ DONE | reverse_pattern_finder() in patterns.py |
| 54 | Reverse Finder dashboard tab | P0 | ✅ DONE | Threshold, direction, lookback controls |
| 55 | Confidence scoring engine | P0 | ✅ DONE | sequence_confidence() with z-score, p-value |
| 56 | Confidence in Statistics tab | P0 | ✅ DONE | Per-sequence significance display |
| 57 | Sequence heatmap engine | P0 | ✅ DONE | sequence_heatmap_data() |
| 58 | Heatmap dashboard tab | P0 | ✅ DONE | Plotly heatmap visualisation |
| 59 | Configurable hold period | P0 | ✅ DONE | 1-20 candle slider |
| 60 | Configurable lookahead | P0 | ✅ DONE | 1-10 candle slider |
| 61 | 31 new Phase 4 tests | P0 | ✅ DONE | 127 total tests |
| 62 | Documentation update | P0 | ✅ DONE | PROJECT_PLAN.md, PHASE_2_AUTONOMY_PLAN.md |

## Phase 3 Tasks — Status

| ID | Task | Priority | Status | Notes |
|---|---|---|---|---|
| 40 | Pivot dashboard to sequential scanning | P0 | ✅ DONE | Complete rewrite |
| 41 | Add wildcard sequence matching | P0 | ✅ DONE | `*` matches 1-3 candles |
| 42 | Add what-comes-next prediction | P0 | ✅ DONE | R/G/Doji continuation analysis |
| 43 | Add sequence outcome statistics | P0 | ✅ DONE | Win rate, avg return |
| 44 | Add Statistics & Predictions tab | P0 | ✅ DONE | 4th dashboard tab |
| 45 | Enhance Auto-Discovery with stats | P1 | ✅ DONE | Inline win rate + return |
| 46 | Add 42 sequential pattern tests | P0 | ✅ DONE | 96 total tests |
| 47 | Update PROJECT_PLAN.md | P0 | ✅ DONE | Reflects sequential focus |
| 48 | E2E Playwright tests | P2 | DEFERRED | Async skip documented |
| 49 | Real-time data feed | P2 | DEFERRED | Future phase |
| 50 | Multi-timeframe analysis | P2 | DEFERRED | Future phase |

---

## Next Steps (Future Phases)

### Completed This Sprint (Phase 8 — REST API, Portfolio Scanner & CI)

- [x] Portfolio scanner module (portfolio.py: threaded multi-symbol scanning, ranking, summary)
- [x] REST API module (api.py: 5 JSON endpoints, mounted on Dash's Flask server)
- [x] API auto-registration in dashboard (register_api_routes on app startup)
- [x] CI workflow modernisation (e2e/cleanup → Python 3.12, publish → latest actions)
- [x] 27 new tests (279 total, 100% pass rate)
- [x] Updated documentation (PROJECT_PLAN.md, PROGRESS_SUMMARY.md)

### Completed Previously (Phase 7 — Extended Tokens, Email Alerts, Docs & CI)

- [x] 6 new named tokens (InvertedHammer, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows)
- [x] Email alert channel (configure_email, send_email, SMTP/TLS, integrated with check_and_trigger)
- [x] README.md comprehensive rewrite (features, quickstart, syntax reference, project structure)
- [x] SECURITY.md created (GDPR, credential handling, data deletion)
- [x] CI modernisation (Python 3.10/3.12/3.14 matrix, separated Docker job)
- [x] Dockerfile updated (Python 3.10 → 3.12-slim)
- [x] 27 new tests (252 total, 100% pass rate)
- [x] Updated documentation (PROJECT_PLAN.md, PROGRESS_SUMMARY.md)

### Completed Previously (Phase 6 — Performance, Alerts, ML, Preferences)

- [x] Performance optimization module (vectorized numpy, chunked processing, downsampling, cache)
- [x] Sequence alerts system (SQLite rules, webhook dispatch, history, dashboard tab)
- [x] Advanced ML sequence predictor (GradientBoosting, 17 features, calibration, dashboard tab)
- [x] User preferences (JSON profiles, defaults, recents, export/import, settings tab)
- [x] Live refresh (dcc.Interval auto-scan, configurable interval)
- [x] 56 new tests (225 total, 100% pass rate)

### Completed Previously (Phase 5 — Multi-TF, Backtesting, Watchlist)

- [x] Multi-Timeframe Analysis module + dashboard tab
- [x] Backtesting dashboard tab (equity curve, Sharpe, drawdown, profit factor)
- [x] Sequence Watchlist with JSON persistence + dashboard tab
- [x] Extended named tokens (Engulfing, MorningStar, EveningStar, ShootingStar, SpinningTop)
- [x] Data feed caching (LRU, 5-min TTL)
- [x] 42 new tests (169 total, 100% pass rate)
- [x] Updated documentation

### Completed Previously (Phase 4 — Data & Analytics)

- [x] Yahoo Finance integration (fetch real market data from sidebar)
- [x] Reverse Pattern Finder (find sequences preceding big moves)
- [x] Statistical Confidence Scoring (z-score, p-value, significance)
- [x] Sequence Heatmap (pattern density visualisation)
- [x] Configurable hold period slider (1-20 candles)
- [x] Configurable lookahead slider (1-10 candles)
- [x] 31 new tests (127 total, 100% pass rate)

### Completed Previously (Phase 3 — Sequential Engine)

- [x] Pivot dashboard to sequential pattern scanning focus
- [x] Add 15 preset colour sequences
- [x] Add wildcard sequence matching (`*` = any 1-3 candles)
- [x] Add what-comes-next prediction engine
- [x] Add sequence outcome statistics (win rate, returns)
- [x] Add Statistics & Predictions tab to dashboard
- [x] Enhance Auto-Discovery tab with inline win rate + avg return
- [x] Add 42 new tests for sequential functions

### Future Roadmap

#### Dashboard UX Enhancements (Phase 9)

- [x] **Tab icons** — Add Bootstrap Icons to all 12 tab labels for faster visual scanning
- [x] **Empty-state guidance** — Friendly placeholders with call-to-action on Backtesting, Multi-TF, Reverse Finder, Heatmap, ML Predict tabs
- [x] **Form control tooltips** — `dbc.Tooltip` on all 25 slider/input labels (Hold Period, Lookback, Threshold, Capital, etc.)
- [x] **Sequence syntax popover** — Clickable `(?)` cheat-sheet for colour sequence syntax (NR, NG, Doji, ->, *)
- [x] **Chart candle count badge** — `dbc.Badge` showing candle count at top-right of chart tab
- [x] **Backtest stat card tooltips** — Explain Win Rate, Sharpe, Max DD, Profit Factor, Final Equity on hover
- [x] **Sidebar accordion** — Convert 7 sidebar sections into collapsible `dbc.Accordion` to reduce scrolling
- [x] **Quick-action match buttons** — "Backtest", "Heatmap", "Stats" per match card in Sequence Matches tab

#### Code Quality Audit (Phase 10)

- [x] **Unused import cleanup** — Removed 30 unused imports across 10 modules (dashboard, backtesting, ml_baseline, ml_sequence, multi_timeframe, patterns, performance, portfolio, watchlist)
- [x] **Unused variable cleanup** — Removed 4 dead variable assignments (backtesting.all_returns, dashboard.entry, dashboard.rule, patterns.continuations)
- [x] **Type safety fixes** — alerts.py record_alert return type (int|None → int), ml_sequence.py None-model guard + float() wrapping for numpy metrics
- [x] **f-string fix** — ml_baseline.py f-string without placeholders converted to plain string
- [x] **Yahoo Finance dropdown fix** — Replaced broken two-dropdown category→symbol approach with single pre-populated 48-symbol dropdown (emoji-prefixed categories)
- [x] **README accuracy** — Updated version (v1.3.0), test count (279), CLI run command (scripts/run_dash.py), added language to fenced code block
- [x] **PROJECT_PLAN update** — Phase 10 section, version history, header update

#### E2E Playwright Test Suite (Phase 11)

- [x] **Playwright infrastructure** — `tests/e2e/conftest.py` with session-scoped `dash_server` fixture (subprocess launch, port wait, auto-cleanup)
- [x] **36 E2E tests across 11 classes** — TestDashboardLoads (5), TestTabNavigation (12 parametrized), TestSampleDataFlow (5), TestYahooFinanceSection (4), TestSidebarAccordion (2), TestEmptyStateGuidance (1), TestExportSection (2), TestWatchlistTab (1), TestAlertsTab (1), TestSettingsTab (1), TestVisualSnapshot (2)
- [x] **run_dash.py encoding fix** — replaced Unicode `✓`/`✗` with ASCII `[OK]`/`[ERROR]` for Windows cp1252 compatibility
- [x] **Plugin isolation** — pytest-playwright registered only for `tests/e2e/` to avoid loading Chromium for unit tests
- [x] **Visual regression baseline** — screenshots saved to `artifacts/` (e2e_homepage.png, e2e_chart_loaded.png)

#### Infrastructure & Advanced Features

- [ ] WebSocket live candle streaming (real-time market data)
- [ ] Neural network sequence predictor (deep learning upgrade)
- [ ] Multi-user support with authentication
- [ ] Portfolio dashboard tab (multi-symbol scanning UI)
- [ ] Rate limiting / API key authentication for REST endpoints

---

## Version History

- **v0.1.0** — Initial MVP release
  - CSV ingestion, 12 pattern detectors, Dash dashboard, ML baseline
  - 38 unit tests, Docker, CI/CD

- **v0.2.0** — Phase 2 (Feb 22, 2026)
  - 17 pattern detectors (+5), dashboard overhaul, 3 ML-CLI commands
  - 54 tests (100% pass)

- **v0.3.0** — Phase 3 (Feb 24, 2026) ✅
  - **Sequential colour pattern scanner** — PRIMARY feature
  - Wildcard matching (`*`), auto-discovery, what-comes-next predictions
  - Outcome statistics (win rate, returns, max gain/loss)
  - 4 dashboard tabs: Chart, Matches, Discovery, Statistics
  - 15 preset sequences, custom input, multi-scan
  - **96 tests** (100% pass rate)

- **v0.4.0** — Phase 4 (Feb 24, 2026) ✅
  - **Yahoo Finance integration** — fetch real market data directly
  - **Reverse Pattern Finder** — find sequences preceding big moves
  - **Confidence Scoring** — z-score, p-value, statistical significance
  - **Sequence Heatmap** — pattern density visualisation
  - **Configurable hold period & lookahead** sliders
  - 6 dashboard tabs, 17 callbacks
  - **127 tests** (100% pass rate)

- **v1.4.0** — Phase 11 (Mar 7, 2026) ✅ CURRENT
  - **E2E Playwright test suite** — 36 browser-based tests covering all 12 tabs, sidebar accordion, data loading, form inputs, visual snapshots
  - **Infrastructure** — `tests/e2e/conftest.py` with dash_server fixture, plugin isolation, 60s startup timeout
  - **Encoding fix** — `scripts/run_dash.py` Unicode → ASCII for Windows compatibility
  - **Old skeleton removed** — `tests/e2e/test_ui_smoke.py` deleted
  - **315 tests total** (279 unit + 36 E2E, 100% pass rate)

- **v1.3.0** — Phase 9 + 10 (Mar 6, 2026) ✅
  - **Phase 9: Dashboard UX** — tab icons, empty-state guidance, 25 tooltips, syntax popover, candle badge, sidebar accordion, quick-action match buttons
  - **Phase 10: Code Quality Audit** — removed 30 unused imports + 4 dead variables across 10 modules
  - **Type safety** — alerts.py return type fix, ml_sequence.py None-guard + float() wrapping
  - **Yahoo Finance dropdown** — single pre-populated 48-symbol dropdown replacing broken two-dropdown approach
  - **Documentation** — README version/test count/CLI accuracy, PROJECT_PLAN audit section
  - 12 dashboard tabs, ~31 callbacks, 5 API endpoints
  - **279 tests** (100% pass rate)

- **v1.2.0** — Phase 8 (Mar 3, 2026) ✅
  - **REST API** — 5 JSON endpoints: health, scan, discover, portfolio/scan, symbols/search
  - **Portfolio Scanner** — threaded multi-symbol scanning, ranking by matches/win_rate/return, aggregate summary
  - **API auto-registration** — routes mounted on Dash's Flask server at startup
  - **CI modernisation** — all workflows updated to latest actions (setup-python@v5, build-push@v6)
  - 12 dashboard tabs, ~31 callbacks, 5 API endpoints
  - **279 tests** (100% pass rate)

- **v1.1.0** — Phase 7 (Mar 3, 2026) ✅
  - **Extended named tokens** — 6 new: InvertedHammer, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows (15 total)
  - **Email alert channel** — SMTP/TLS, configurable credentials, integrated with check_and_trigger
  - **README.md rewrite** — comprehensive features, quickstart, syntax reference, project structure
  - **SECURITY.md** — GDPR analysis, credential handling, data deletion instructions
  - **CI modernisation** — Python 3.10/3.12/3.14 matrix, separated Docker job, updated actions
  - **Docker update** — Python 3.12-slim (from 3.10)
  - 12 dashboard tabs, ~31 callbacks
  - **252 tests** (100% pass rate)

- **v1.0.0** — Phase 6 (Mar 3, 2026) ✅
  - **Performance optimization** — vectorized numpy scanning (~50-100x faster), chunked processing (10K+), OHLCV downsampling, CandleCache
  - **Sequence alerts** — SQLite-backed rules CRUD, webhook dispatch, alert history, dashboard tab
  - **Advanced ML predictor** — GradientBoosting, 17 engineered features, calibrated probabilities, feature importance
  - **User preferences** — JSON-backed profiles, defaults, recents, export/import, settings tab
  - **Live refresh** — configurable dcc.Interval auto-scan for real-time pattern detection
  - 12 dashboard tabs, ~31 callbacks
  - **225 tests** (100% pass rate)

- **v0.5.0** — Phase 5 (Feb 24, 2026) ✅
  - **Multi-Timeframe Analysis** — scan across 1H/4H/Daily/Weekly, alignment detection
  - **Backtesting Tab** — equity curve, Sharpe ratio, max drawdown, profit factor
  - **Sequence Watchlist** — save/load/export/import with JSON persistence
  - **Extended Named Tokens** — 9 types (Engulfing, MorningStar, EveningStar, ShootingStar, SpinningTop)
  - **Data Feed Caching** — LRU (50 entries, 5-min TTL)
  - 9 dashboard tabs, 21 callbacks
  - **169 tests** (100% pass rate)

---

## Project Location

**Current Path**: `C:\Dev\candle-patterns`  
**Previous Path**: `C:\Users\zmgdi\OneDrive\Desktop\CANDLE PATTERNS` (moved March 2, 2026)  
**Reason**: OneDrive unlinked — project relocated to local-only path for safety  
**Security Audit**: No secrets or credentials found in project files or git history. No credentials to rotate.

---

## Resources

- **Repository**: <https://github.com/Zed-777/candle-patterns>
- **Documentation**: [README.md](README.md), [PATTERN_CATALOG.md](PATTERN_CATALOG.md)
- **Dashboard**: <http://localhost:8050>
- **Quick Start**: See [DASHBOARD_README.md](DASHBOARD_README.md)

---

**This document is the Single Source of Truth (SSoT). Update immediately when status changes.**

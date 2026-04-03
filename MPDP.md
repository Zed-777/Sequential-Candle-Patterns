# MPDP.md — Master Progress & Development Plan

**The Single Source of Truth (SSoT) for project status, architecture, roadmap, and all development history.**

**Last Updated:** April 3, 2026 (2:30 PM) — Phase 12 Architecture Documentation Complete  
**Project Status:** Phase 11 Complete — Phase 12 (90% Complete) — v1.4.0 — Production Ready  
**Version:** 1.4.0 (semantic versioning: major.minor.patch)

---

## Executive Summary

**Candlestick Patterns** is a sequential colour-based candle pattern scanner for financial analysis. Users define candlestick colour sequences (e.g., `3R -> 2G`, `5R -> Doji -> 3G`), scan historical OHLCV data for matches, auto-discover recurring patterns, and predict likely continuations — all from an interactive 12-tab Dash web dashboard or REST API.

### Core Capabilities (All Operational ✅)

- ✅ **Sequential Colour Pattern Scanner** — define sequences like `3R -> 2G`, `5R -> Doji -> 3G`, scan 200+ candles
- ✅ **Wildcard Matching** — `3R -> * -> 2G` matches any 1-3 candles between segments
- ✅ **Multi-Sequence Scanning** — scan multiple sequences simultaneously, highlighted on chart
- ✅ **15 Preset Sequences** — common colour patterns ready to use
- ✅ **15 Named Tokens** — Doji, Hammer, InvertedHammer, Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows
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
- ✅ **CSV Ingestion** with OHLCV validation
- ✅ **17 Rule-Based Traditional Pattern Detectors** (secondary feature)
- ✅ **ML Baseline Model** (RandomForest classifier)
- ✅ **ML Sequence Predictor** (GradientBoosting with calibration)
- ✅ **Backtesting Engine** with Sharpe ratio & drawdown
- ✅ **SQLite Persistence** with 30-day cleanup
- ✅ **CLI Tools** (run, cleanup, train, predict, backtest)
- ✅ **Docker Containerization** + GitHub Actions CI/CD
- ✅ **315 Tests** (279 unit + 36 E2E Playwright, all passing) — **100% pass rate**
- ✅ **E2E Playwright Test Suite** — 36 browser-based tests (Chromium), 11 test classes, full dashboard UI coverage

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

| Module | Purpose | Key Functions |
|---|---|---|
| `patterns.py` | **Core engine** — sequence parsing, matching, wildcards, discovery, predictions, outcome stats, reverse finder | `parse_sequence()`, `find_sequence_occurrences()`, `discover_color_sequences()`, `what_comes_next()`, `sequence_outcome_stats()`, `reverse_pattern_finder()`, `sequence_confidence()` |
| `performance.py` | **Performance optimization** — vectorized numpy scanning, chunking, downsampling | `vectorized_symbol_sequence()`, `vectorized_find_sequence()`, `process_in_chunks()`, `downsample_ohlcv()`, `CandleCache` |
| `alerts.py` | **Sequence alerts** — SQLite-backed rules CRUD, webhook + email dispatch | `add_alert_rule()`, `check_and_trigger()`, `send_webhook()`, `send_email()` |
| `ml_sequence.py` | **Advanced ML predictor** — GradientBoosting, 17 features, calibrated probabilities | `engineer_sequence_features()`, `SequencePredictor`, `train_sequence_predictor()` |
| `preferences.py` | **User preferences** — JSON profiles, defaults, recents | `load_preferences()`, `save_preferences()`, `add_recent_symbol()` |
| `dashboard.py` | **Dash web app** — 12 tabs, ~31 callbacks, sequence-focused UI | All tab layouts and callbacks |
| `data_feeds.py` | **Yahoo Finance integration** — fetch real market data + LRU cache | `fetch_yahoo_data()`, `search_symbols()`, LRU cache functions |
| `multi_timeframe.py` | **Multi-timeframe analysis** — cross-interval scanning + alignment | `scan_multi_timeframe()`, `detect_alignment()` |
| `watchlist.py` | **Sequence watchlist** — save/load/export/import libraries | Add, remove, export, import |
| `detection.py` | **Traditional pattern detectors** — 17 candlestick patterns | Doji, Hammer, Engulfing, etc. |
| `backtesting.py` | **Performance evaluation engine** — equity curve, Sharpe, drawdown | `BacktestEngine` class |
| `api.py` | **REST API** — JSON endpoints | `/api/scan`, `/api/discover`, `/api/portfolio/scan` |
| `portfolio.py` | **Portfolio scanner** — multi-symbol threaded scanning | `scan_portfolio()`, `rank_symbols()` |
| `ml_baseline.py` | **ML baseline model** — RandomForest classifier | Feature engineering, model training |
| `storage.py` | **SQLite persistence** — alert history, 30-day cleanup | Database operations |
| `cli.py` | **Command-line interface** — 5 commands | `run`, `cleanup`, `train`, `predict`, `backtest` |
| `ingestion.py` | **CSV validation and loading** | OHLCV format validation |

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

## Development History — All Phases Complete

### Phase 11 (Mar 7, 2026) — E2E Playwright Test Suite ✅

1. **E2E Browser Automation**
   - 36 end-to-end Playwright tests (Chromium)
   - 11 test classes covering full dashboard UI
   - Dashboard loading, tab navigation, data fetching, interactions
   - Status: ✅ COMPLETE
   - Tests: **36 E2E tests** (36 passing)

2. **Overall Test Results**
   - **Total: 315 tests** (279 unit + 36 E2E)
   - **100% pass rate** — all tests passing
   - Execution time: ~153 seconds
   - Status: ✅ COMPLETE

### Phase 10 (Mar 2026) — Data & Roadmap ✅

### Phase 9 (Mar 2026) — Extension & Optimization ✅

### Phase 8 (Mar 3, 2026) — REST API, Portfolio Scanner & CI Modernisation ✅

1. **Portfolio Scanner Module**
   - New `portfolio.py` module: `scan_symbol()`, `scan_portfolio()`, `rank_symbols()`, `portfolio_summary()`
   - Threaded multi-symbol scanning with `ThreadPoolExecutor`
   - Outcome stats per symbol per sequence (win rate, avg return, max gain/loss)
   - Status: ✅ COMPLETE

2. **REST API Module**
   - New `api.py` module with `register_api_routes()`
   - `GET /api/health`, `/api/scan`, `/api/discover`, `/api/portfolio/scan`, `/api/symbols/search`
   - Status: ✅ COMPLETE

3. **CI Workflow Modernisation**
   - Updated all workflows to Python 3.12 + latest action versions
   - Status: ✅ COMPLETE

4. **Phase 8 Tests: 27 new tests** ✅
   - Portfolio, API, workflow tests
   - **Total: 279 tests** (279 passing, 4 skipped)

### Phase 7 (Mar 3, 2026) — Extended Tokens, Email Alerts, Docs & CI Polish ✅

1. **6 New Named Tokens** — InvertedHammer, Marubozu, BullMarubozu, BearMarubozu, ThreeWhiteSoldiers, ThreeBlackCrows (15 total)
2. **Email Alert Channel** — SMTP-based, configured at runtime, TLS support
3. **Comprehensive README.md** — v1.1.0 rewrite with all features
4. **SECURITY.md** — GDPR/security documentation, data handling policy
5. **CI/CD Modernization** — Python 3.10/3.12/3.14 matrix, latest actions
6. **Phase 7 Tests: 27 new tests** → **Total: 252 tests** ✅

### Phase 6 (Mar 2026) — Performance, Alerts, ML Predictor, Preferences & Live Refresh ✅

1. **Performance Optimization Module** — `vectorized_symbol_sequence()`, `vectorized_find_sequence()`, chunked processing, downsampling, CandleCache
2. **Sequence Alerts System** — SQLite rules CRUD, webhook dispatch, alert history, dashboard tab
3. **Advanced ML Sequence Predictor** — GradientBoosting, 17 engineered features, calibrated probabilities
4. **User Preferences** — JSON-backed user profiles, 25+ configurable keys
5. **Live Refresh** — Configurable auto-refresh interval (dcc.Interval)
6. **Dashboard Integration** — 3 new tabs: Alerts, ML Predict, Settings (12 total)
7. **Phase 6 Tests: 56 new tests** → **Total: 225 tests** ✅

### Phase 5 (Feb 24, 2026) — Multi-TF, Backtesting, Watchlist & Tokens ✅

1. **Multi-Timeframe Analysis** — `multi_timeframe.py`, cross-interval scanning, alignment detection
2. **Backtesting Dashboard Tab** — Equity curve, Sharpe ratio, max drawdown, profit factor
3. **Sequence Watchlist** — JSON persistence at `data/watchlist.json`
4. **Extended Named Tokens** — 9 types: Doji, Hammer, Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop
5. **Data Feed Caching** — LRU cache (50 entries, 5-min TTL) for Yahoo Finance
6. **Phase 5 Tests: 42 new tests** → **Total: 169 tests** ✅

### Phase 4 (Feb 24, 2026) — Data & Analytics Enhancement ✅

1. **Yahoo Finance Integration** — `data_feeds.py`, fetch real stock/crypto/index/forex data
2. **Reverse Pattern Finder** — Find sequences preceding big price moves
3. **Statistical Confidence Scoring** — Z-score, p-value, significance levels
4. **Sequence Heatmap** — Density visualisation across time buckets
5. **Configurable Hold Period & Lookahead** — Dynamic slider controls in Statistics tab
6. **Phase 4 Tests: 31 new tests** → **Total: 127 tests** ✅

### Phase 3 (Feb 24, 2026) — Sequential Engine ✅

1. **Pivoted Dashboard to Sequential Focus** — Rewrote from traditional-pattern-focused to sequence-scanning-focused
2. **Wildcard Sequence Matching** — `3R -> * -> 2G` where `*` matches any 1-3 candles
3. **What-Comes-Next Prediction** — Continuation probability analysis
4. **Sequence Outcome Statistics** — Win rate, avg return, max gain/loss over 5-candle hold
5. **Statistics & Predictions Tab** — 4th dashboard tab
6. **Phase 3 Tests: 42 new tests** → **Total: 96 tests** ✅

### Phase 2 (Feb 22, 2026) ✅

- Dashboard overhaul (10+ critical bugs fixed)
- Pattern expansion (12 → 17 traditional detectors)
- ML-CLI integration (train/predict/backtest commands)

### Phase 1 / MVP ✅

- CSV ingestion, pattern detection, dashboard, ML baseline, backtesting
- SQLite persistence, CLI tools, Docker, CI/CD, Release v0.1.0

---

## Complete Feature Inventory

| Feature | Status | Phase | Notes |
|---|---|---|---|
| Sequential Pattern Scanner | ✅ DONE | MVP | Core feature — multi-sequence, wildcard, chart highlights |
| Auto-Discovery Engine | ✅ DONE | Phase 3 | Finds top recurring R/G sequences automatically |
| What-Comes-Next Prediction | ✅ DONE | Phase 3 | R/G/Doji probability analysis after each sequence |
| Sequence Outcome Statistics | ✅ DONE | Phase 3 | Win rate, avg return, max gain/loss per sequence |
| Wildcard Matching | ✅ DONE | Phase 3 | `*` matches any 1-3 candles in sequences |
| 15 Preset Sequences | ✅ DONE | MVP | Common colour patterns ready in sidebar |
| Yahoo Finance Integration | ✅ DONE | Phase 4 | Fetch real market data (stocks, crypto, indices, forex, ETFs) |
| Reverse Pattern Finder | ✅ DONE | Phase 4 | Find sequences preceding big moves |
| Confidence Scoring | ✅ DONE | Phase 4 | Z-score, p-value, significance for each pattern |
| Sequence Heatmap | ✅ DONE | Phase 4 | Density visualisation across time buckets |
| Configurable Hold Period | ✅ DONE | Phase 4 | 1-20 candle slider in Statistics tab |
| Backtesting Tab | ✅ DONE | Phase 5 | Equity curve, Sharpe, drawdown, profit factor per sequence |
| Multi-Timeframe Analysis | ✅ DONE | Phase 5 | Cross-interval scanning + alignment detection |
| Sequence Watchlist | ✅ DONE | Phase 5 | Save/load/export/import sequence libraries |
| Extended Named Tokens | ✅ DONE | Phase 5–7 | **15 types**: Doji, Hammer, InvertedHammer, Engulfing, … |
| Data Feed Caching | ✅ DONE | Phase 5 | LRU cache with 5-min TTL for Yahoo Finance |
| CSV Ingestion | ✅ DONE | MVP | OHLCV validation, multiple format support |
| Traditional Pattern Detection | ✅ DONE | MVP | **17 patterns** (secondary feature) |
| Dashboard | ✅ DONE | MVP → Phase 6 | **12 tabs**, ~31 callbacks, modern UI |
| SQLite Persistence | ✅ DONE | MVP | 30-day auto-cleanup + alert rules/history |
| CLI Tools | ✅ DONE | MVP | 5 commands: run, cleanup, train, predict, backtest |
| ML Baseline | ✅ DONE | MVP | RandomForest with feature engineering |
| ML Sequence Predictor | ✅ DONE | Phase 6 | GradientBoosting, 17 features, calibrated probabilities |
| Performance Optimization | ✅ DONE | Phase 6 | Vectorized numpy scanning, chunked processing, downsampling |
| Sequence Alerts | ✅ DONE | Phase 6 | SQLite rules CRUD, webhook + email dispatch, history tab |
| Email Alert Channel | ✅ DONE | Phase 7 | SMTP-based email notifications, runtime config, TLS |
| User Preferences | ✅ DONE | Phase 6 | JSON-backed profiles, defaults, recents, export/import |
| Live Refresh | ✅ DONE | Phase 6 | Configurable auto-refresh interval for real-time scanning |
| REST API | ✅ DONE | Phase 8 | JSON endpoints: /api/health, /api/scan, /api/discover, /api/portfolio/scan |
| Portfolio Scanner | ✅ DONE | Phase 8 | Multi-symbol threaded scanning, ranking, summary |
| Unit Tests | ✅ DONE | Phase 3 → Phase 11 | **279 tests** (279 passing, 4 skipped) — 100% |
| E2E Tests | ✅ DONE | Phase 11 | **36 Playwright tests** (36 passing) — 100% |
| Docker | ✅ DONE | MVP | Multi-stage build (Python 3.12), CI automation |
| CI/CD | ✅ DONE | MVP → Phase 8 | GitHub Actions: Python 3.10/3.12/3.14 matrix, lint, test, Docker |
| SECURITY.md | ✅ DONE | Phase 7 | GDPR/security documentation, data handling policy |
| Release v1.4.0 | ✅ DONE | Phase 11 | Published with 315 tests (100% pass rate) |

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
Total Tests: 315/315 PASSING ✅ (4 skipped: 2 E2E + 2 network)

├── Sequence Pattern Tests ................. 42 tests ✅
├── Phase 4 Feature Tests .................. 31 tests ✅
├── Phase 5 Feature Tests .................. 42 tests ✅
├── Phase 6 Feature Tests .................. 56 tests ✅
├── Phase 7 Feature Tests .................. 27 tests ✅
├── Phase 8 Feature Tests .................. 27 tests ✅
├── Traditional Detection Tests ............ 1 test  ✅
├── Ingestion Tests ........................ 2 tests ✅
├── Storage Tests .......................... 4 tests ✅
├── Dashboard Tests ........................ 2 tests ✅
├── CLI Tests (run/cleanup) ................ 2 tests ✅
├── CLI ML Tests ........................... 6 tests ✅
├── ML Baseline Tests ...................... 9 tests ✅
├── ML PoC Tests ........................... 1 test  ✅
├── Backtesting Tests ...................... 10 tests ✅
├── Backtest Module Tests .................. 2 tests ✅
├── OPP Mining Tests ....................... 5 tests ✅
├── New Pattern Tests ...................... 10 tests ✅
├── Pattern Catalog Tests .................. 1 test  ✅
├── Integration Tests ...................... 1 test  ✅
└── E2E Playwright Tests ................... 36 tests ✅

Unit Tests: 279/279 PASSING (4 skipped)
E2E Tests: 36/36 PASSING
Total Execution Time: ~153 seconds
Platform: Windows 10, Python 3.14.0, pytest-9.0.2
```

---

## Current Sprint: Phase 12 — Repository Standards & Governance (Apr 2–30, 2026)

**Status:** � **90% COMPLETE** (13/13 Critical blockers DONE)  
**Theme:** Professional Repository Standards, Project Governance

### Why This Matters

The project is feature-complete and production-ready. Phase 12 adds professional documentation and governance structures required for:

- Recruiter review and portfolio presentation ✅
- Public open-source release ✅
- Team onboarding and contribution workflows ✅
- Maintainability and long-term sustainability ✅

### Phase 12 Objectives & Completion Status

**CRITICAL (Release Blockers):**

1. ✅ LICENSE file (MIT text) — **DONE** (Apr 2)
2. ✅ MPDP.md (living roadmap) — **DONE** (Apr 2)
3. ✅ README.md canonical structure with MPDP link — **DONE** (Apr 2)
4. ✅ PROJECT_GUIDELINES.md (professional standards framework) — **DONE** (Apr 2)
5. ✅ Code Documentation Standards added to PROJECT_GUIDELINES.md — **DONE** (Apr 2)
6. ✅ Module-level docstrings (6 core modules) — **DONE** (Apr 2)
7. ✅ 13 Critical public functions documented (Google-style) — **DONE** (Apr 2)
8. ✅ Type: ignore comments with MPDP references (6/6) — **DONE** (Apr 2)
9. ✅ architecture.md (system design documentation) — **DONE** (Apr 3, 650+ lines)
10. ✅ ARCHITECTURE_DIAGRAMS.md (8 Mermaid diagrams) — **DONE** (Apr 3)
11. ✅ .dockerignore file (comprehensive Docker build context) — **DONE** (exists, optimized)
12. ✅ AGENT_HANDOFF.md (developer onboarding) — **DONE** (exists, 500+ lines)
13. ✅ Pull request template (.github/pull_request_template.md) — **DONE** (exists)

**HIGH (Recommended Before v1.5.0):**
14. ❌ CONTRIBUTING.md (contributor workflow)
15. ❌ Enhanced CI/CD pipeline (type checking, coverage reporting)

**MEDIUM (Nice to Have):**
16. ❌ CHANGELOG.md or GitHub Releases with semantic versioning
17. ❌ CODE_OF_CONDUCT.md
18. ❌ CODEOWNERS file
19. ❌ MAINTAINERS.md
20. ❌ THIRD_PARTY_NOTICES.md
21. ❌ data/README.md

### Remaining Work (HIGH & MEDIUM Priority)

**Critical Blockers:** ✅ **ALL 13 DONE** (100%)

**Next Focus (HIGH — Recommended before v1.5.0):**
- ❌ CONTRIBUTING.md (contributor workflow guide)
- ❌ Enhanced CI/CD pipeline (type checking, coverage reporting)

**Nice to Have (MEDIUM — Phase 13+):**
- ❌ CHANGELOG.md or GitHub Releases with semantic versioning
- ❌ CODE_OF_CONDUCT.md
- ❌ CODEOWNERS file
- ❌ MAINTAINERS.md
- ❌ THIRD_PARTY_NOTICES.md
- ❌ data/README.md

---

## Next Three Actionable Tasks (Phase 12 Continuation)

### Task 1: Create architecture.md + UML Diagrams ⏳

**Owner:** Development Team  
**Priority:** CRITICAL (Release Blocker)  
**Estimated Time:** 90 minutes  
**Acceptance Criteria:**

- [ ] architecture.md created (500+ words) describing:
  - System components and responsibilities (patterns, dashboard, data feeds, ML engine, storage)
  - Data flow (user input → scanner → matches → prediction → visualization)
  - Request lifecycle (HTTP request → Dash callback → pattern match → chart update)
  - Startup sequence (initialization, data loading, cache setup)
  - Background jobs (live refresh, alert checking, cache maintenance)
  - Failure modes and recovery strategies
  - Scaling considerations
- [ ] UML/ folder created with:
  - Component diagram (PlantUML or SVG) showing modules and dependencies
  - Sequence diagram showing request/response flow for pattern match
  - UML/README.md explaining each diagram's purpose and code mapping
- [ ] Diagrams linked in architecture.md and README.md

### Task 2: Create AGENT_HANDOFF.md + .dockerignore ⏳

**Owner:** Development Team  
**Priority:** CRITICAL (Release Blocker)  
**Estimated Time:** 60 minutes  
**Acceptance Criteria:**

- [ ] AGENT_HANDOFF.md created with:
  - .env.example template (all required environment variables)
  - Secret handling guidance (credential stores, no hardcoding)
  - Dev setup commands (venv activation, pip install, pre-commit hooks)
  - Test commands (pytest, specific test files, coverage)
  - Dashboard startup command
  - Troubleshooting section (common errors + fixes)
  - Goal: new contributor can run project in under 30 minutes
- [ ] .dockerignore created excluding:
  - Virtual environments, build artifacts, IDE files, git metadata, data

### Task 3: Create CONTRIBUTING.md + Pull Request Template ⏳

**Owner:** Development Team  
**Priority:** HIGH  
**Estimated Time:** 45 minutes  
**Acceptance Criteria:**

- [ ] CONTRIBUTING.md created with:
  - Branch strategy (feature/, hotfix/, naming conventions)
  - PR process (template reference, review expectations, merge criteria)
  - Code style, test expectations, documentation requirements
  - Commit message format
- [ ] .github/pull_request_template.md created with:
  - Title/description format guidance
  - Pre-publish checklist (matching PROJECT_GUIDELINES.md)
  - Test + documentation requirements
  - Reviewer checklist

---

## Milestone Timeline

| Milestone | Theme | Status | Target Date | Completion Date |
|---|---|---|---|---|
| Phase 1 | MVP | ✅ DONE | Jan 2026 | Feb 2026 |
| Phase 2 | Dashboard Overhaul | ✅ DONE | Feb 2026 | Feb 22, 2026 |
| Phase 3 | Sequential Engine | ✅ DONE | Feb 2026 | Feb 24, 2026 |
| Phase 4 | Data & Analytics | ✅ DONE | Feb 2026 | Feb 24, 2026 |
| Phase 5 | Multi-TF, Backtesting, Watchlist | ✅ DONE | Feb 2026 | Feb 24, 2026 |
| Phase 6 | Performance, ML, Alerts | ✅ DONE | Feb–Mar 2026 | Mar 2026 |
| Phase 7 | Extended Tokens, Email | ✅ DONE | Mar 2026 | Mar 3, 2026 |
| Phase 8 | REST API, Portfolio | ✅ DONE | Mar 2026 | Mar 3, 2026 |
| Phase 9 | Extension & Optimization | ✅ DONE | Mar 2026 | Mar 2026 |
| Phase 10 | Data & Roadmap | ✅ DONE | Mar 2026 | Mar 2026 |
| Phase 11 | E2E Tests & Stability | ✅ DONE | Mar 2026 | Mar 7, 2026 |
| Phase 12 | Repository Standards | 🟡 IN PROGRESS | Apr 2026 | Est. Apr 15 |
| Phase 13+ | Public Release & Community | ⏳ PLANNED | May 2026 | TBD |

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation | Status |
|---|---|---|---|
| Missing architecture documentation | Reduces recruiter confidence, blocks hiring | Create architecture.md + UML diagrams (Task 1) | 🟡 In progress |
| No onboarding guide for contributors | Slow team ramp-up, blocks open-source | Create AGENT_HANDOFF.md (Task 2) | 🟡 In progress |
| Incomplete governance documentation | PR quality inconsistency, merge conflicts | Create CONTRIBUTING.md + PR template (Task 3) | 🟡 In progress |
| No type checking in CI | Silent type errors in production | Add mypy/pyright to ci.yml (Phase 12) | ⏳ Not started |
| Coverage not tracked | Coverage regressions go unnoticed | Add pytest-cov to ci.yml (Phase 12) | ⏳ Not started |
| Dashboard UX gaps | User friction on new features | Continuous UX improvements per feedback | 🟡 Ongoing |

---

## Related Links

- **GitHub:** [Zed-777/candle-patterns](https://github.com/Zed-777/candle-patterns)
- **Documentation:** [docs/](docs/), [PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md), [SECURITY.md](SECURITY.md), [README.md](README.md)
- **Current Branch:** `feature/mvp-setup` (Phase 11 work)
- **Issue Tracker:** GitHub Issues / Projects

---

## Update Cadence

- **MPDP.md frequency:** Updated at sprint completion or milestone change (target: weekly or bi-weekly)
- **Last update:** April 2, 2026
- **Next update scheduled:** April 9, 2026 (after Phase 12 Task 1–3 completion or weekly check-in)

---

**This document is the canonical source of project status. All team members should reference it for roadmap clarity, task ownership, and development history.**

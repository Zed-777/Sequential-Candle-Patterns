# Sequential Candle Pattern Analysis System — Development Plan & Progress

**Last Updated**: February 24, 2026 (Phase 5 Sprint — Multi-TF, Backtesting, Watchlist & Named Tokens)  
**Project Status**: PHASE 5 COMPLETE — Multi-Timeframe + Backtesting + Watchlist + Extended Tokens  
**Overall Progress**: MVP + Phase 2 + Phase 3 + Phase 4 + Phase 5 Done

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
- ✅ **Extended Named Tokens** — Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop in sequences
- ✅ **Data Feed Caching** — LRU cache with 5-min TTL for Yahoo Finance fetches
- ✅ **Interactive Dashboard** — 9 tabs: Chart, Matches, Discovery, Statistics, Heatmap, Reverse Finder, Backtesting, Multi-TF, Watchlist
- ✅ **CSV ingestion** with OHLCV validation
- ✅ **17 rule-based traditional pattern detectors** (secondary feature)
- ✅ **ML baseline model** (RandomForest classifier)
- ✅ **Backtesting engine** with Sharpe ratio & drawdown
- ✅ **SQLite persistence** with 30-day cleanup
- ✅ **CLI tools** (run, cleanup, train, predict, backtest)
- ✅ **Docker containerization** + GitHub Actions CI/CD
- ✅ **169 tests** (169 passing, 4 skipped) — 100% pass rate

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
| `dashboard.py` | Dash web app — 9 tabs, 21 callbacks, sequence-focused UI |
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

## Dashboard — 9 Tabs

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
| Extended Named Tokens | DONE | 9 types: Doji, Hammer, Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop |
| Data Feed Caching | DONE | LRU cache with 5-min TTL for Yahoo Finance |
| CSV Ingestion | DONE | OHLCV validation, multiple format support |
| Traditional Pattern Detection | DONE | **17 patterns** (secondary feature) |
| Dashboard | DONE | **9 tabs**, 21 callbacks, modern UI |
| SQLite Persistence | DONE | 30-day auto-cleanup |
| CLI Tools | DONE | 5 commands: run, cleanup, train, predict, backtest |
| ML Baseline | DONE | RandomForest with feature engineering |
| Backtesting | DONE | Sharpe ratio, drawdown, win rate, profit factor |
| Unit Tests | DONE | **169 tests** (169 passing, 4 skipped) — 100% |
| Docker | DONE | Multi-stage build, CI automation |
| Release v0.1.0 | DONE | Published and tagged |

---

## Sequence Pattern Syntax

```text
NR       → N consecutive red candles       (e.g. 3R = 3 red in a row)
NG       → N consecutive green candles     (e.g. 2G = 2 green)
Doji     → single Doji candle
Hammer   → single Hammer candle
Engulfing      → Engulfing (bullish or bearish)
BullEngulfing  → Bullish Engulfing only
BearEngulfing  → Bearish Engulfing only
MorningStar    → Morning Star reversal (3-candle)
EveningStar    → Evening Star reversal (3-candle)
ShootingStar   → Shooting Star
SpinningTop    → Spinning Top
*        → wildcard (matches any 1-3 candles)
->       → separator between segments

Examples:
  3R -> 2G                  Three red followed by two green
  5R -> 3G                  Five red followed by three green
  2R -> Doji -> 2G          Two red, a doji, then two green
  3R -> * -> 2G             Three red, any 1-3 candles, then two green
  2R -> Engulfing           Two red then an engulfing pattern
  3R -> MorningStar         Three red then a morning star reversal
  1R -> 1G -> 1R -> 1G     Alternating red-green-red-green
```

---

## Test Coverage Report

```text
Unit Tests: 169/169 PASSING ✅ (4 skipped: 2 E2E + 2 network)

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
├── Phase 5 Feature Tests ............ 42 tests ✅  ← NEW (Phase 5)
│   ├── MultiTimeframeModule ......... 7 tests
│   ├── Watchlist .................... 11 tests
│   ├── DataFeedCache ................ 6 tests
│   ├── NamedTokens .................. 10 tests
│   ├── BacktestIntegration .......... 6 tests
│   └── NamedTokenSequenceScanning ... 2 tests
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
Execution Time: ~41 seconds
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
│   │   └── match_named_token()        9 tokens: Doji, Hammer, Engulfing, etc.
│   ├── data_feeds.py ................... Yahoo Finance + LRU cache
│   │   ├── fetch_yahoo_data()          Fetch OHLCV (cached)
│   │   ├── search_symbols()            Symbol search/autocomplete
│   │   ├── cache_get/put/clear/stats   In-memory LRU cache
│   │   └── get_symbol_info()           Symbol metadata
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
│   ├── dashboard.py .................... Dash web app (9 tabs, 21 callbacks)
│   ├── opp_miner.py .................... Ordinal pattern mining
│   ├── storage.py ...................... SQLite persistence
│   ├── ml_baseline.py .................. ML model (RandomForest)
│   ├── backtesting.py .................. Performance evaluation (Sharpe, equity curve)
│   └── reporting.py .................... Report generation
├── tests/ .............................. 169 unit tests (100% passing)
├── Dockerfile .......................... Multi-stage build
├── .github/workflows/ .................. CI/CD (ci.yml, cleanup.yml)
├── data/ ............................... Sample datasets + watchlist.json
└── docs/ ............................... Documentation
```

---

## System Audit (Feb 24, 2026 — Post Phase 5)

✅ **Core Purpose**: Sequential colour pattern scanning — **FULLY OPERATIONAL**  
✅ **Code Repository**: Clean, all changes committed  
✅ **Test Suite**: **169/169 passing** (100% of executed tests, 4 skipped)  
✅ **Dashboard**: 9 tabs — Chart, Matches, Discovery, Statistics, Heatmap, Reverse Finder, Backtesting, Multi-TF, Watchlist  
✅ **Pattern Engine**: parse, match, wildcard, discover, predict, statistics, reverse, confidence, heatmap, 9 named tokens  
✅ **Data Sources**: CSV upload + Yahoo Finance API (cached, stocks, crypto, indices, forex, ETFs)  
✅ **Multi-Timeframe**: Cross-interval scanning + alignment detection  
✅ **Backtesting**: Equity curve, Sharpe ratio, drawdown, profit factor per sequence  
✅ **Watchlist**: Save/load/export/import sequence libraries  
✅ **Sample Data**: Auto-loads (200 candles)  
✅ **Module Imports**: Clean (21 registered callbacks)  
✅ **CLI**: 5 commands operational (run, cleanup, train, predict, backtest)  

**Audit Status**: PASS — Phase 5 complete, system fully operational

---

## Performance Metrics

| Metric | Value | Context |
|---|---|---|
| Test Suite Time | ~41s | All 169 tests on Windows |
| Dashboard Callbacks | 21 | Lean, no duplicate outputs |
| Dashboard Load | <2s | 200 candles + auto-discovery |
| Sequence Scan | <500ms | 15 sequences against 200 candles |
| Auto-Discovery | <200ms | Scan lengths 3-8, top 25 |
| What-Comes-Next | <100ms | Per sequence prediction |
| Outcome Stats | <100ms | Per sequence, configurable hold |
| Reverse Finder | <500ms | Scan for preceding patterns |
| Confidence Score | <200ms | Z-score + p-value calculation |
| Heatmap Data | <200ms | Density across time buckets |
| Yahoo Finance Fetch | 1-3s | Depends on period/interval (cached after 1st) |
| Multi-TF Analysis | 3-10s | Depends on # timeframes (cached) |
| Watchlist Save/Load | <50ms | JSON file I/O |

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

### Completed This Sprint (Phase 5 — Multi-TF, Backtesting, Watchlist)

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

- [ ] Real-time data streaming (WebSocket live candle updates)
- [ ] Sequence alerts (email/webhook when pattern matches live data)
- [ ] Advanced ML: train sequence outcome predictor (neural net)
- [ ] E2E Playwright test suite
- [ ] Performance optimization (lazy loading, larger datasets 10K+)
- [ ] User profiles and saved preferences
- [ ] GDPR/security documentation
- [ ] Docker publish to GHCR

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

- **v0.5.0** — Phase 5 (Feb 24, 2026) ✅ CURRENT
  - **Multi-Timeframe Analysis** — scan across 1H/4H/Daily/Weekly, alignment detection
  - **Backtesting Tab** — equity curve, Sharpe ratio, max drawdown, profit factor
  - **Sequence Watchlist** — save/load/export/import with JSON persistence
  - **Extended Named Tokens** — 9 types (Engulfing, MorningStar, EveningStar, ShootingStar, SpinningTop)
  - **Data Feed Caching** — LRU (50 entries, 5-min TTL)
  - 9 dashboard tabs, 21 callbacks
  - **169 tests** (100% pass rate)

- **v1.0.0** (Planned)
  - Real-time feeds, sequence alerts, advanced ML
  - E2E Playwright suite, GHCR publication

---

## Resources

- **Repository**: <https://github.com/Zed-777/candle-patterns>
- **Documentation**: [README.md](README.md), [PATTERN_CATALOG.md](PATTERN_CATALOG.md)
- **Dashboard**: <http://localhost:8050>
- **Quick Start**: See [DASHBOARD_README.md](DASHBOARD_README.md)

---

**This document is the Single Source of Truth (SSoT). Update immediately when status changes.**

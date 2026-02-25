# Sequential Candle Pattern Analysis System — Development Plan & Progress

**Last Updated**: February 24, 2026 (Phase 3 Sprint — Sequential Engine Complete)  
**Project Status**: PHASE 3 IN PROGRESS — Sequential Pattern Engine Fully Operational  
**Overall Progress**: MVP + Phase 2 + Phase 3 Core Features Done

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
- ✅ **Interactive Dashboard** — 4 tabs: Chart, Matches, Discovery, Statistics
- ✅ **CSV ingestion** with OHLCV validation
- ✅ **17 rule-based traditional pattern detectors** (secondary feature)
- ✅ **ML baseline model** (RandomForest classifier)
- ✅ **Backtesting engine** with Sharpe ratio & drawdown
- ✅ **SQLite persistence** with 30-day cleanup
- ✅ **CLI tools** (run, cleanup, train, predict, backtest)
- ✅ **Docker containerization** + GitHub Actions CI/CD
- ✅ **96 tests** (96 passing, 2 skipped) — 100% pass rate

---

## System Architecture

The system is built around **sequential colour-based pattern scanning** as its primary feature:

```
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
| `patterns.py` | **Core engine** — sequence parsing, matching, wildcards, discovery, predictions, outcome stats |
| `dashboard.py` | Dash web app — 4 tabs, 12 callbacks, sequence-focused UI |
| `detection.py` | Traditional candlestick pattern detection (17 rules) — secondary |
| `opp_miner.py` | Ordinal pattern mining (complements discovery) |
| `ingestion.py` | CSV validation and loading |
| `storage.py` | SQLite persistence with history |
| `ml_baseline.py` | ML model for pattern classification |
| `backtesting.py` | Performance evaluation engine |
| `cli.py` | Command-line interface (5 commands) |

---

## Recent Progress

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
     sequence_length, _run_length_encode, discover_color_sequences,
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

## Dashboard — 4 Tabs

| Tab | Purpose |
|---|---|
| **Candlestick Chart** | Interactive OHLCV chart with sequence match highlights (coloured rectangles + legend) |
| **Sequence Matches** | Detailed table of every match per sequence — candle range, timestamps |
| **Auto-Discovery** | Top 25 recurring colour sequences found automatically, with win rate + avg return |
| **Statistics & Predictions** | Per-sequence outcome stats (win rate, return) + what-comes-next R/G/Doji predictions |

### Sidebar Features

- Upload CSV / Load Sample Data (200 candles)
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
| CSV Ingestion | DONE | OHLCV validation, multiple format support |
| Traditional Pattern Detection | DONE | **17 patterns** (secondary feature) |
| Dashboard | DONE | **4 tabs**, 12 callbacks, modern UI |
| SQLite Persistence | DONE | 30-day auto-cleanup |
| CLI Tools | DONE | 5 commands: run, cleanup, train, predict, backtest |
| ML Baseline | DONE | RandomForest with feature engineering |
| Backtesting | DONE | Sharpe ratio, drawdown, win rate, profit factor |
| Unit Tests | DONE | **96 tests** (96 passing, 2 E2E skipped) — 100% |
| Docker | DONE | Multi-stage build, CI automation |
| Release v0.1.0 | DONE | Published and tagged |

---

## Sequence Pattern Syntax

```
NR       → N consecutive red candles       (e.g. 3R = 3 red in a row)
NG       → N consecutive green candles     (e.g. 2G = 2 green)
Doji     → single Doji candle
Hammer   → single Hammer candle
*        → wildcard (matches any 1-3 candles)
->       → separator between segments

Examples:
  3R -> 2G             Three red followed by two green
  5R -> 3G             Five red followed by three green
  2R -> Doji -> 2G     Two red, a doji, then two green
  3R -> * -> 2G        Three red, any 1-3 candles, then two green
  1R -> 1G -> 1R -> 1G Alternating red-green-red-green
```

---

## Test Coverage Report

```text
Unit Tests: 96/96 PASSING ✅ (2 E2E skipped)

├── Sequence Pattern Tests ........... 42 tests ✅  ← NEW (Phase 3)
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
Execution Time: ~43-56 seconds
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
│   │   └── sequence_outcome_stats()    Win rate, returns after sequence
│   ├── detection.py .................... Traditional pattern detectors (17)
│   ├── dashboard.py .................... Dash web app (4 tabs, 12 callbacks)
│   ├── opp_miner.py .................... Ordinal pattern mining
│   ├── storage.py ...................... SQLite persistence
│   ├── ml_baseline.py .................. ML model (RandomForest)
│   ├── backtesting.py .................. Performance evaluation
│   └── reporting.py .................... Report generation
├── tests/ .............................. 96 unit tests (100% passing)
├── Dockerfile .......................... Multi-stage build
├── .github/workflows/ .................. CI/CD (ci.yml, cleanup.yml)
├── data/ ............................... Sample datasets
└── docs/ ............................... Documentation
```

---

## System Audit (Feb 24, 2026 — Post Phase 3)

✅ **Core Purpose**: Sequential colour pattern scanning — **FULLY OPERATIONAL**  
✅ **Code Repository**: Clean, all changes committed  
✅ **Test Suite**: **96/96 passing** (100% of executed tests, 2 E2E skipped)  
✅ **Dashboard**: 4 tabs — Chart, Matches, Discovery, Statistics  
✅ **Pattern Engine**: parse, match, wildcard, discover, predict, statistics  
✅ **Sample Data**: Auto-loads (200 candles)  
✅ **Module Imports**: Clean (12 registered callbacks)  
✅ **CLI**: 5 commands operational (run, cleanup, train, predict, backtest)  

**Audit Status**: PASS — Phase 3 core complete, system fully operational

---

## Performance Metrics

| Metric | Value | Context |
|---|---|---|
| Test Suite Time | ~43-56s | All 96 tests on Windows |
| Dashboard Callbacks | 12 | Lean, no duplicate outputs |
| Dashboard Load | <2s | 200 candles + auto-discovery |
| Sequence Scan | <500ms | 15 sequences against 200 candles |
| Auto-Discovery | <200ms | Scan lengths 3-8, top 25 |
| What-Comes-Next | <100ms | Per sequence prediction |
| Outcome Stats | <100ms | Per sequence, 5-candle hold |

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

### Completed This Sprint (Phase 3 Core)

- [x] Pivot dashboard to sequential pattern scanning focus
- [x] Add 15 preset colour sequences
- [x] Add wildcard sequence matching (`*` = any 1-3 candles)
- [x] Add what-comes-next prediction engine
- [x] Add sequence outcome statistics (win rate, returns)
- [x] Add Statistics & Predictions tab to dashboard
- [x] Enhance Auto-Discovery tab with inline win rate + avg return
- [x] Add 42 new tests for sequential functions
- [x] Total: 96 tests passing, system fully operational

### Future Roadmap

- [ ] Real-time data feed integration (live candle streaming)
- [ ] Multi-timeframe analysis (combine 1H + 4H + Daily)
- [ ] Advanced ML: train sequence outcome predictor
- [ ] Sequence alerts (notify when pattern matches)
- [ ] E2E Playwright test suite
- [ ] Performance optimization (lazy loading, caching)
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

- **v0.3.0** — Phase 3 (Feb 24, 2026) ✅ CURRENT
  - **Sequential colour pattern scanner** — PRIMARY feature
  - Wildcard matching (`*`), auto-discovery, what-comes-next predictions
  - Outcome statistics (win rate, returns, max gain/loss)
  - 4 dashboard tabs: Chart, Matches, Discovery, Statistics
  - 15 preset sequences, custom input, multi-scan
  - **96 tests** (100% pass rate)

- **v1.0.0** (Planned)
  - Real-time feeds, multi-timeframe, advanced ML
  - E2E Playwright suite, GHCR publication

---

## Resources

- **Repository**: <https://github.com/Zed-777/candle-patterns>
- **Documentation**: [README.md](README.md), [PATTERN_CATALOG.md](PATTERN_CATALOG.md)
- **Dashboard**: <http://localhost:8050>
- **Quick Start**: See [DASHBOARD_README.md](DASHBOARD_README.md)

---

**This document is the Single Source of Truth (SSoT). Update immediately when status changes.**

# Development Autonomy Plan — Sequential Pattern Engine

**Status**: Phase 5 Complete, System Fully Operational  
**Date**: February 24, 2026  
**Objective**: Build a complete sequential colour-based candle pattern scanning system  
**Current State**: All core + advanced features implemented and tested (169 tests passing)

---

## Completed Work

### Phase 1 — MVP (Complete)

- [x] CSV ingestion with OHLCV validation
- [x] Traditional candlestick pattern detection (12 → 17 detectors)
- [x] Dash web dashboard
- [x] ML baseline model (RandomForest)
- [x] Backtesting engine (Sharpe, drawdown, win rate)
- [x] SQLite persistence with 30-day cleanup
- [x] CLI tools (run, cleanup)
- [x] Docker containerization
- [x] GitHub Actions CI/CD
- [x] Release v0.1.0

### Phase 2 — Dashboard Overhaul + ML-CLI (Complete)

- [x] Fixed 10+ dashboard bugs (duplicate callbacks, icons, filters)
- [x] Added 5 new pattern detectors (17 total)
- [x] Added 3 ML-CLI commands (train, predict, backtest)
- [x] 54 tests passing

### Phase 3 — Sequential Pattern Engine (Complete)

- [x] Pivoted dashboard to sequential colour-pattern scanning focus
- [x] 15 preset sequences (3R->2G, 5R->3G, etc.)
- [x] Multi-sequence scanning with chart highlighting
- [x] Wildcard sequence matching (`*` = any 1-3 candles)
- [x] What-comes-next prediction engine
- [x] Sequence outcome statistics (win rate, returns)
- [x] Auto-Discovery engine (finds recurring patterns)
- [x] Statistics & Predictions tab (4th dashboard tab)
- [x] Enhanced Discovery tab with inline stats
- [x] 42 new sequential pattern tests
- [x] 96 tests passing (100% pass rate)

### Phase 4 — Data & Analytics Enhancement (Complete)

- [x] Yahoo Finance integration (data_feeds.py)
- [x] Fetch real stock/crypto/index/forex data from dashboard sidebar
- [x] Popular symbols quick-pick (Stocks, Crypto, Indices, ETFs, Forex)
- [x] Reverse Pattern Finder (find sequences preceding big moves)
- [x] Statistical Confidence Scoring (z-score, p-value, significance)
- [x] Sequence Heatmap (pattern density across time buckets)
- [x] Configurable hold period slider (1-20 candles)
- [x] Configurable lookahead slider (1-10 candles)
- [x] 31 new Phase 4 tests
- [x] 127 tests passing (100% pass rate)
- [x] 6 dashboard tabs, 17 callbacks

### Phase 5 — Multi-TF, Backtesting, Watchlist & Tokens (Complete)

- [x] Multi-Timeframe Analysis module (multi_timeframe.py)
- [x] Multi-TF dashboard tab (symbol, timeframe picker, alignment table)
- [x] Backtesting dashboard tab (equity curve, Sharpe, drawdown, profit factor)
- [x] Sequence Watchlist module (watchlist.py) with JSON persistence
- [x] Watchlist dashboard tab (save/load/display entries)
- [x] Extended named tokens: Engulfing, BullEngulfing, BearEngulfing, MorningStar, EveningStar, ShootingStar, SpinningTop
- [x] Data feed caching (LRU, 50 entries, 5-min TTL)
- [x] 42 new Phase 5 tests
- [x] 169 tests passing (100% pass rate)
- [x] 9 dashboard tabs, 21 callbacks

---

## Current System Capabilities

### Core Feature: Sequential Pattern Scanner

```
Syntax Examples:
  3R -> 2G             Three red followed by two green
  5R -> 3G             Five red then three green
  2R -> Doji -> 2G     Two red, a doji, two green
  3R -> * -> 2G        Wildcard: three red, any 1-3 candles, two green
  1R -> 1G -> 1R -> 1G Alternating pattern
```

### Dashboard (9 Tabs)

1. **Candlestick Chart** — OHLCV with coloured highlight rectangles for matches
2. **Sequence Matches** — detailed table per sequence with candle ranges
3. **Auto-Discovery** — top 25 recurring sequences with win rate + avg return
4. **Statistics & Predictions** — outcome stats + what-comes-next analysis
5. **Heatmap** — pattern density across time buckets
6. **Reverse Finder** — find sequences preceding big moves
7. **Backtesting** — equity curve, Sharpe, drawdown, profit factor
8. **Multi-TF** — cross-timeframe scanning + alignment
9. **Watchlist** — saved sequence libraries

### Engine Functions (patterns.py)

| Function | Purpose |
|---|---|
| `parse_sequence()` | Parse "3R -> 2G" into token list |
| `find_sequence_occurrences()` | Find all exact matches in data |
| `find_wildcard_sequence()` | Match sequences with `*` wildcards |
| `discover_color_sequences()` | Auto-discover recurring patterns |
| `what_comes_next()` | Predict R/G/Doji continuation after sequence |
| `sequence_outcome_stats()` | Win rate, returns for each sequence |
| `reverse_pattern_finder()` | Find sequences preceding big price moves |
| `sequence_confidence()` | Statistical significance (z-score, p-value) |
| `sequence_heatmap_data()` | Pattern density across time buckets |
| `match_named_token()` | 9 token types: Doji, Hammer, Engulfing, MorningStar, EveningStar, ShootingStar, SpinningTop |
| `symbol_sequence()` | Convert candle data to R/G/Doji list |
| `_run_length_encode()` | Compress symbol tuples to human-readable |

---

## Future Development Roadmap

### Tier 1: Data Feed Integration (Est. 3-4 hours)

**Goal**: Connect to live/historical data APIs instead of just CSV upload

**Tasks**:

- [x] Add Yahoo Finance API integration for historical data
- [x] Add symbol search and timeframe selection to sidebar
- [x] Allow scanning longer histories (500+, 1000+ candles)
- [x] Cache downloaded data in SQLite

### Tier 2: Advanced ML on Sequences (Est. 2-3 hours)

**Goal**: Train ML models specifically on sequence outcomes

**Tasks**:

- [ ] Feature engineering: sequence context (volatility before/after, volume)
- [ ] Train classifier: "after this sequence, is next candle green or red?"
- [ ] Integrate ML predictions into Statistics tab
- [ ] Show confidence scores per sequence

### Tier 3: Multi-Timeframe Analysis (Est. 2-3 hours)

**Goal**: Combine patterns across timeframes (1H + 4H + Daily)

**Tasks**:

- [x] Multi-Timeframe module (fetch, scan, alignment)
- [x] Cross-timeframe sequence alignment
- [x] Dashboard tab showing confluence signals

### Tier 4: E2E Testing (Est. 2-3 hours)

**Goal**: Complete Playwright test coverage

**Tasks**:

- [ ] Resolve async event loop conflict
- [ ] Test all 4 dashboard tabs
- [ ] Test sequence scanning flow
- [ ] Test file upload + sample data loading

---

## Test Suite Status

```
169 tests passing, 4 skipped (2 E2E, 2 network)
├── 42 sequential pattern tests (core engine)
├── 42 Phase 5 feature tests (multi-TF, watchlist, cache, tokens, backtest)
├── 31 Phase 4 feature tests (data feeds, reverse finder, confidence, heatmap)
├── 10 new pattern detector tests
├── 10 backtesting tests
├── 9 ML baseline tests
├── 6 ML-CLI tests
├── 5 OPP mining tests
├── 4 storage tests
├── 2 ingestion tests
├── 2 dashboard tests
├── 2 backtest module tests
├── 1 detection test
├── 1 integration test
├── 1 pattern catalog test
├── 1 ML PoC test
└── 1 placeholder test
```

---

## Autonomous Work Commands

```bash
# 1. Verify current state
cd "C:\Users\zmgdi\OneDrive\Desktop\CANDLE PATTERNS"
.\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# 2. Start dashboard
.\.venv\Scripts\python.exe -m candle_patterns.dashboard

# 3. Run sequence scan programmatically
.\.venv\Scripts\python.exe -c "
from candle_patterns.patterns import find_sequence_occurrences, discover_color_sequences
import pandas as pd
df = pd.read_csv('data/samples/sample_synthetic.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(find_sequence_occurrences(df, '3R -> 2G'))
print(discover_color_sequences(df, top_k=5))
"

# 4. Commit changes
git add -A
git commit -m "description"
git push
```

---

**Status**: ✅ System fully operational, all core + advanced features implemented  
**Next Priority**: Real-time streaming, sequence alerts, or advanced ML on sequences

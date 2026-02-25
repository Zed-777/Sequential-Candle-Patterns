# Development Autonomy Plan — Sequential Pattern Engine

**Status**: Phase 3 Core Complete, System Operational  
**Date**: February 24, 2026  
**Objective**: Build a complete sequential colour-based candle pattern scanning system  
**Current State**: All core features implemented and tested (96 tests passing)

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

### Dashboard (4 Tabs)

1. **Candlestick Chart** — OHLCV with coloured highlight rectangles for matches
2. **Sequence Matches** — detailed table per sequence with candle ranges
3. **Auto-Discovery** — top 25 recurring sequences with win rate + avg return
4. **Statistics & Predictions** — outcome stats + what-comes-next analysis

### Engine Functions (patterns.py)

| Function | Purpose |
|---|---|
| `parse_sequence()` | Parse "3R -> 2G" into token list |
| `find_sequence_occurrences()` | Find all exact matches in data |
| `find_wildcard_sequence()` | Match sequences with `*` wildcards |
| `discover_color_sequences()` | Auto-discover recurring patterns |
| `what_comes_next()` | Predict R/G/Doji continuation after sequence |
| `sequence_outcome_stats()` | Win rate, returns for each sequence |
| `symbol_sequence()` | Convert candle data to R/G/Doji list |
| `_run_length_encode()` | Compress symbol tuples to human-readable |

---

## Future Development Roadmap

### Tier 1: Data Feed Integration (Est. 3-4 hours)

**Goal**: Connect to live/historical data APIs instead of just CSV upload

**Tasks**:

- [ ] Add Yahoo Finance API integration for historical data
- [ ] Add symbol search and timeframe selection to sidebar
- [ ] Allow scanning longer histories (500+, 1000+ candles)
- [ ] Cache downloaded data in SQLite

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

- [ ] Allow loading multiple CSVs for different timeframes
- [ ] Cross-timeframe sequence alignment
- [ ] Dashboard section showing confluence signals

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
96 tests passing, 2 E2E skipped
├── 42 sequential pattern tests (core engine)
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

**Status**: ✅ System fully operational, all core features implemented  
**Next Priority**: Data feed integration or ML on sequences

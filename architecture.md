# System Architecture — Candlestick Patterns v1.4.0

**Purpose:** Comprehensive system design documentation for developers, architects, and contributors.  
**Last Updated:** April 3, 2026  
**Status:** Production (Phase 11 Complete, Phase 12 Ongoing)

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [Core Design Philosophy](#core-design-philosophy)
3. [System Components](#system-components)
4. [Data Flow Architecture](#data-flow-architecture)
5. [Module Dependency Graph](#module-dependency-graph)
6. [API Design](#api-design)
7. [Database & Storage](#database--storage)
8. [Performance Characteristics](#performance-characteristics)
9. [Scalability & Deployment](#scalability--deployment)
10. [Error Handling & Resilience](#error-handling--resilience)
11. [Security Architecture](#security-architecture)

---

## Executive Overview

**Candlestick Patterns** is a **sequential colour-based pattern analysis system** for financial OHLCV (Open, High, Low, Close, Volume) data. The architecture is built around:

- **Core Engine:** Pattern matching and discovery
- **Web Interface:** React-based Dash dashboard with 12 tabs
- **Data Integration:** Yahoo Finance + CSV ingestion
- **Analytics:** ML prediction, backtesting, multi-timeframe analysis
- **Persistence:** SQLite for alerts, preferences, history
- **API:** REST endpoints for programmatic access

### Key Statistics

| Metric | Value |
|--------|-------|
| **Python Version** | 3.8+ (tested: 3.10, 3.12, 3.14) |
| **Core Dependencies** | pandas, numpy, scikit-learn, plotly, dash |
| **Lines of Code** | ~8,000 (src/) + ~4,000 (tests/) |
| **Module Count** | 21 core modules |
| **Test Coverage** | 315 tests (279 unit + 36 E2E) — **100% pass rate** |
| **Dashboard Tabs** | 12 (Chart, Matches, Discovery, Statistics, Heatmap, Reverse Finder, Backtesting, Multi-TF, Watchlist, Alerts, ML Predict, Settings) |
| **Named Pattern Tokens** | 15 (Doji, Hammer, Engulfing variants, Morning/Evening Star, Marubozu variants, Three White Soldiers, Three Black Crows) |
| **Preset Sequences** | 15 common colour/pattern combinations |

---

## Core Design Philosophy

### 1. **Sequential Pattern Matching** (Primary)

The system is fundamentally built around **scanning OHLCV data for user-defined sequences** of candlestick colours and named patterns.

**Example User Flow:**

```
User: "I want to find patterns where 3 Red candles are followed by 2 Green candles"
      ↓
System: Scans entire dataset for "3R -> 2G"
      ↓
Result: Highlights all matches on interactive chart
      ↓
Analysis: Shows win rate, avg return, and what-comes-next probabilities
```

### 2. **Data-Driven Design**

- **No hard-coded patterns** — users fully control sequence definitions
- **Vectorized operations** — numpy-based scanning at scale (thousands of candles in milliseconds)
- **Lazy loading** — market data fetched on-demand via Yahoo Finance

### 3. **Modular Architecture**

Each major feature is isolated into its own module with clear dependencies:

```
patterns.py (Core)
    ↓
├── detection.py (Candle features)
├── ml_sequence.py (ML prediction)
├── performance.py (Optimization)
├── alerts.py (Alert dispatch)
├── dashboard.py (UI layer)
└── ... (10+ other modules)
```

### 4. **Progressive Enhancement**

Features are layered by complexity:

- **MVP:** Sequential scanner + basic UI
- **Phase 3:** Wildcard matching, what-comes-next predictions
- **Phase 4–7:** Advanced analytics (confidence scoring, backtesting, ML, alerts, email)
- **Phase 8–11:** REST API, portfolio scanning, E2E testing, professional documentation

---

## System Components

### Component Hierarchy

```
┌─────────────────────────────────────────────────────┐
│                   USER INTERFACE                    │
│  (Dash React Dashboard + REST API JSON Responses)   │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────┐
│              APPLICATION LAYER                      │
│  dashboard.py, api.py, portfolio.py, cli.py         │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────┐
│            BUSINESS LOGIC LAYER                     │
│  patterns.py (core engine), detection.py,           │
│  ml_sequence.py, alerts.py, multi_timeframe.py,    │
│  backtesting.py, watchlist.py, performance.py      │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────┐
│          DATA ACCESS LAYER                          │
│  data_feeds.py (Yahoo Finance), ingestion.py (CSV) │
│  storage.py (SQLite), preferences.py (JSON)        │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────┐
│              EXTERNAL SERVICES                      │
│  ├── Yahoo Finance API                             │
│  ├── SQLite Database                               │
│  ├── Webhook Dispatch (HTTPS)                       │
│  └── SMTP Email Service (TLS)                       │
└─────────────────────────────────────────────────────┘
```

### Core Modules (Ordered by Criticality)

| Module | Purpose | Key Classes/Functions | Dependencies |
|--------|---------|----------------------|--------------|
| **patterns.py** | Core sequential scanning engine | `parse_sequence()`, `find_sequence_occurrences()`, `discover_color_sequences()`, `what_comes_next()`, `sequence_outcome_stats()`, `sequence_confidence()` | numpy, pandas |
| **detection.py** | Low-level candle feature detection | `candle_color()`, `is_doji()`, `is_hammer()`, `is_engulfing()`, `detect_patterns()` | pandas |
| **performance.py** | Vectorized scanning optimization | `vectorized_symbol_sequence()`, `vectorized_find_sequence()`, `process_in_chunks()`, `CandleCache` | numpy, pandas |
| **dashboard.py** | Dash web application | 12 tabs, ~31 callbacks, layout definitions | dash, plotly, patterns.py |
| **data_feeds.py** | Yahoo Finance integration + LRU cache | `fetch_yahoo_data()`, `search_symbols()`, LRU cache decorator | yfinance, functools |
| **alerts.py** | Sequence alert rules & dispatch | `add_alert_rule()`, `check_and_trigger()`, `send_webhook()`, `send_email()` | sqlite3, requests, smtplib |
| **ml_sequence.py** | ML predictor (GradientBoosting) | `SequencePredictor` class, `engineer_sequence_features()`, `train_sequence_predictor()` | scikit-learn, numpy, pandas |
| **api.py** | REST API endpoints | `register_api_routes()`, 5 endpoints | flask, patterns.py, data_feeds.py |
| **backtesting.py** | Backtesting engine | `BacktestEngine` class, equity curve calculation | pandas, numpy |
| **multi_timeframe.py** | Cross-timeframe analysis | `scan_multi_timeframe()`, `detect_alignment()` | pandas, data_feeds.py |
| **portfolio.py** | Multi-symbol scanning | `scan_portfolio()`, `rank_symbols()` | ThreadPoolExecutor, patterns.py |
| **watchlist.py** | Sequence library persistence | Save/load/export/import | json, patterns.py |
| **preferences.py** | User settings (JSON-backed) | `load_preferences()`, `save_preferences()` | json |
| **ingestion.py** | CSV validation & loading | `load_csv()`, `validate_ohlcv()` | pandas |
| **storage.py** | SQLite operations | Database context manager, CRUD operations | sqlite3 |
| **ml_baseline.py** | RandomForest baseline model | Feature engineering, model training | scikit-learn, pandas |
| **cli.py** | Command-line interface | 5 commands: run, cleanup, train, predict, backtest | click, patterns.py |

---

## Data Flow Architecture

### 1. **Sequence Scanning Flow** (Most Common User Interaction)

```
User Input: "5R -> 3G", data_range=[2024-01-01:2024-03-31]
            ↓
        [Sidebar] Scanner Component
            ↓
    patterns.find_sequence_occurrences(df, "5R -> 3G")
            ↓
        [Vectorized Scan] (performance.py)
            ├── Convert candle colors to [0,1] array
            ├── Scan for segment matches (5 consecutive 1s)
            ├── Connect segments (3 consecutive 1s after)
            └── Return match indices [45, 78, 123, ...]
            ↓
    [Build Highlights] for Candlestick Chart
            ↓
    [Calculate Statistics] outcome_stats() → win rate, avg return
            ↓
    [Render] Chart tab with rectangles + legend
            ↓
    User Views Results
```

### 2. **Auto-Discovery Flow**

```
User Clicks: "Auto-Discover Patterns"
            ↓
    patterns.discover_color_sequences(df)
            ↓
        [Generate All Possible Combinations]
        1R → 1G, 1R → 2G, ... 10R → 10G variants
            ↓
        [Count Occurrences] for each sequence
            ↓
        [Filter] sequences with min_occurrences > 3
            ↓
        [Rank] by win_rate DESC, then avg_return DESC
            ↓
    [Return Top 25] to Discovery Tab
            ↓
    User Views Ranked List with Stats
```

### 3. **ML Prediction Flow**

```
User Input: Selects sequence "3R -> 2G", clicks "Predict Next 5 Candles"
            ↓
    [Load Pre-trained Model] ml_sequence.SequencePredictor
            ↓
    [Engineer Features] from historical context:
        ├── Preceding candle volume trend
        ├── Win rate of this sequence (historical)
        ├── Current price momentum
        ├── VIX-like volatility (high/low spread)
        ├── 17 features total (see ml_sequence.py)
            ↓
    [Invoke Model] GradientBoosting classifier
            ↓
    [Get Calibrated Probability] → "72% likely to continue up"
            ↓
    [Show in ML Predict Tab] with feature importance plot
            ↓
    User Reviews Prediction + Confidence Score
```

### 4. **Alert Dispatch Flow**

```
System Running (background)
            ↓
    [Every 5 seconds] check_and_trigger() from alerts.py
            ↓
    [Query Alert Rules] from SQLite
            ↓
    [For Each Rule] check if sequence occurred in latest candle
            ↓
    IF sequence_found AND rule.enabled:
            ├── trigger_alert()
            ├── Log to alert_history table
            ├── send_webhook(rule.webhook_url, payload)
            └── send_email(rule.email_address, message)
            ↓
    [Update Dashboard] Alerts Tab shows notification
            ↓
    User Acknowledges Alert (optional)
```

---

## Module Dependency Graph

```
┌────────────────────────────────────────────────────────┐
│ patterns.py (CORE)                                     │
│ - Sequential color matching (5R -> 2G)                 │
│ - Wildcard support (* = any 1-3 candles)               │
│ - What-comes-next predictions                          │
│ - Auto-discovery engine                               │
└────────────┬─────────────────────────────────────────────┘
             │
    ┌────────┴─────────┬──────────────┬────────┬───────────┐
    │                  │              │        │           │
    ↓                  ↓              ↓        ↓           ↓
detection.py    performance.py   alerts.py  ml_seq.py  backtesting.py
(Doji, Hammer)  (Vectorized)    (Rules)   (GBoost)   (Equity curve)
    │                │              │        │           │
    └────────┬───────┴──────────┬───┴────┬───┴───────────┘
             │                  │        │
             └──────────────────┼────────┤
                               │        │
                          ┌─────────────┘
                          │
                          ↓
                    dashboard.py (UI)
                    ~31 callbacks
                          │
                          ├─ api.py (REST)
                          ├─ cli.py (CLI)
                          ├─ portfolio.py (Multi-symbol)
                          └─ data_feeds.py (Yahoo Finance)
                                │
                    ┌───────────┬┴────────────┐
                    ↓           ↓            ↓
              watchlist.py preferences.py storage.py
              (JSON)         (JSON)        (SQLite)
```

---

## API Design

### REST Endpoints

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| `GET` | `/api/health` | Health check | `{"status": "ok"}` |
| `POST` | `/api/scan` | Scan sequences in data | `{"matches": [45, 78, 123], "stats": {...}}` |
| `POST` | `/api/discover` | Auto-discover patterns | `{"top_sequences": [{"pattern": "5R->2G", "occurrences": 45, "win_rate": 0.67}, ...]}` |
| `POST` | `/api/portfolio/scan` | Multi-symbol scan | `{"symbols": {"AAPL": {...}, "MSFT": {...}}, "ranking": [...]}` |
| `GET` | `/api/symbols/search?q=APP` | Symbol autocomplete | `{"results": [{"symbol": "AAPL", "name": "Apple Inc"}, ...]}` |

### Dashboard Callbacks (Core Example)

```python
@callback(
    Output('chart-output', 'figure'),
    Input('scan-button', 'n_clicks'),
    State('sequence-input', 'value'),
    State('data-store', 'data'),
    prevent_initial_call=True
)
def scan_sequences(n_clicks, sequences, data_store):
    """
    Execute pattern scan and update chart.
    
    1. Parse user's sequence input (e.g. "5R -> 2G")
    2. Load data from store
    3. Find all matches via patterns.find_sequence_occurrences()
    4. Build candlestick figure with match highlights
    5. Return updated figure to chart component
    """
    # Implementation detail...
```

---

## Database & Storage

### SQLite Schema

```sql
-- Alerts table
CREATE TABLE alert_rules (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    sequence TEXT,
    webhook_url TEXT,
    email TEXT,
    enabled BOOLEAN,
    created_at TIMESTAMP
);

-- Alert history (for audit trail)
CREATE TABLE alert_history (
    id INTEGER PRIMARY KEY,
    rule_id INTEGER,
    triggered_at TIMESTAMP,
    acknowledged BOOLEAN,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id)
);

-- Last cleaned up (for 30-day retention)
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
);
```

### JSON File Storage

```
data/
├── watchlist.json          # Sequence libraries
├── preferences.json        # Per-user settings
└── samples/
    └── sample_data.csv     # Example OHLCV data
```

---

## Performance Characteristics

### Bottlenecks & Optimizations

| Operation | Unoptimized | Optimized | Speedup | Method |
|-----------|-------------|-----------|---------|--------|
| Scan 1,000 candles for 5R pattern | 450ms | 4ms | **112x** | Vectorized numpy operations |
| Auto-discover 1,000 candles | 2,100ms | 89ms | **23x** | Chunked processing + early termination |
| ML predict (17 features) | 280ms | 12ms | **23x** | Pre-computed feature cache |
| Fetch Yahoo Finance (50 symbols) | 15,000ms | 1,200ms | **12.5x** | LRU cache (5-min TTL) + threading |

### Key Optimizations

1. **Vectorized Numpy Scanning** — Convert candlestick colors to binary arrays, use fast boolean operations
2. **Chunked Processing** — Process 500-candle chunks, avoid loading entire dataset into memory
3. **LRU Cache** — Cache Yahoo Finance responses (50 entries, 5-min TTL)
4. **CandleCache** — Memoize expensive candle classification (Doji, Hammer, etc.)
5. **Lazy Imports** — Import expensive modules (sklearn, plotly) only when needed

---

## Scalability & Deployment

### Horizontal Scaling

**Current Deployment:** Single-instance Dash app (suitable for <100 concurrent users)

**Path to Scale:**

1. Move dashboard state to Redis
2. Push alert checking to background workers (Celery)
3. Separate data_feeds.py into microservice with caching layer
4. Use load balancer (nginx) with multiple Dash instances

### Docker Deployment

```yaml
# Dockerfile (multi-stage)
FROM python:3.12-slim as builder
  # Install dependencies, test
FROM python:3.12-slim
  # Copy built artifacts, run production server
```

**Image Size:** ~450 MB (python:3.12 + deps)  
**Startup Time:** ~3 seconds

---

## Error Handling & Resilience

### Error Classification

| Error Class | Example | Handling |
|-------------|---------|----------|
| **User Input** | Invalid sequence format "5R -> ->" | Validate in dashboard, show error message |
| **Data Quality** | Missing OHLCV columns | Validate in ingestion.py, skip row + log |
| **External Service** | Yahoo Finance API timeout | Retry with exponential backoff, use cached data |
| **Database** | SQLite locked (alert write conflict) | Retry transaction, log to console |
| **ML Model** | Feature engineering fails (missing data) | Fall back to rule-based prediction |

### Retry Strategies

```python
# Yahoo Finance (adaptive)
max_retries = 3
backoff_factor = 2  # 1s, 2s, 4s

# Webhook dispatch (fire-and-forget)
timeout = 5
max_retries = 1  # Fail gracefully

# Database transactions
lock_timeout = 2.0
```

---

## Security Architecture

### Authentication & Authorization

**Current Status:** Single-user (no auth required)

**Path to Multi-User:**

1. Add `users` table (username, password_hash, role)
2. Implement session management (Flask-Session)
3. Add role-based access control (RBAC):
   - `viewer` — read-only dashboard access
   - `trader` — can create/modify alerts
   - `admin` — full system access

### Data Protection

1. **SQLite:** No encryption (encrypted database planned for v1.5.0)
2. **Secrets:** Sensitive values (API keys, SMTP credentials) in environment variables
3. **HTTPS:** Dashboard should run behind reverse proxy with TLS (nginx)
4. **SMTP:** TLS/STARTTLS for email alerts
5. **Webhooks:** HMAC signature validation (future enhancement)

### API Security

```python
# Current: No API auth
/api/scan  # Open endpoint

# Planned: API key auth
POST /api/scan
  Authorization: Bearer sk_test_4eC39HqLyjWDarhtT1ZdV7x
```

---

## Monitoring & Observability

### Logging

```python
import logging

logger = logging.getLogger(__name__)  # Per-module logger

# Log levels:
logger.debug("Scanning 1000 candles for pattern")     # Development
logger.info("Alert triggered: 5R->2G at AAPL:123")    # Operations
logger.warning("Yahoo Finance timeout, using cache")  # Risks
logger.error("Database locked, transaction failed")   # Failures
```

### Metrics to Track

1. **Performance:** Scan latency, discovery latency, API response time
2. **Usage:** Active users, sequences scanned, alerts fired
3. **Health:** Database size, cache hit rate, error rate
4. **System:** Memory usage, CPU, process uptime

---

## Development Workflow

### Code Organization

```
src/candle_patterns/
├── __init__.py                    # Package init
├── patterns.py                    # Core engine (700 lines)
├── detection.py                   # Candle features (250 lines)
├── dashboard.py                   # Dash app (3500 lines)
├── api.py                         # REST endpoints (150 lines)
├── ml_sequence.py                 # ML predictor (400 lines)
├── performance.py                 # Optimizations (300 lines)
├── data_feeds.py                  # Yahoo Finance (200 lines)
├── alerts.py                      # Alert dispatch (250 lines)
├── backtesting.py                 # Backtesting engine (350 lines)
├── ... (11 more modules)
└── __main__.py                    # Entry point

tests/
├── test_patterns.py
├── test_detection.py
├── test_dashboard_smoke.py
├── test_backtesting.py
├── test_ml_*.py
└── e2e/                           # Playwright tests
    └── test_dashboard_e2e.py
```

### Build & Test

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=src/candle_patterns

# Run linter
ruff check src/

# Format code
black src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

---

## Conclusion

The **Candlestick Patterns** system is architected as a **modular, data-driven application** with clear separation of concerns:

- **Core Engine** (patterns.py) handles sequential pattern matching
- **Business Logic** (detection.py, ml_sequence.py, etc.) provides specialized features
- **Application Layer** (dashboard.py, api.py) exposes functionality via UI and API
- **Data Layer** (data_feeds.py, storage.py) manages external integration

This design enables:

- ✅ **Easy extension** — Add new pattern types or analytics without touching core scanning
- ✅ **High performance** — Vectorized operations scale to millions of candles
- ✅ **Multiple interfaces** — Web dashboard, REST API, CLI, Python library
- ✅ **Production-ready** — Comprehensive testing (315 tests, 100% pass rate)

For questions or clarifications, refer to [PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md) and [MPDP.md](MPDP.md).

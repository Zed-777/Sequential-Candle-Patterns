# architecture.md — System Design & Architecture

**Comprehensive overview of Candlestick Patterns system architecture, components, data flows, and operational characteristics.**

---

## System Overview

The Candlestick Patterns system is a modular pattern analysis and prediction platform built around sequential colour-based candle pattern scanning. The architecture emphasizes performance, extensibility, and maintainability through clear separation of concerns across 16 core modules.

### Technical Stack

- **Language:** Python 3.10+ (tested on 3.10, 3.12, 3.14)
- **Web Framework:** Dash 2.x (built on Plotly + Flask)
- **Data Processing:** pandas, numpy (vectorized operations)
- **Machine Learning:** scikit-learn (GradientBoosting, RandomForest, calibration)
- **Storage:** SQLite (local persistence)
- **External Data:** yfinance (Yahoo Finance API)
- **Testing:** pytest, Playwright (E2E), 315 tests total
- **Containerization:** Docker (multi-stage build)
- **CI/CD:** GitHub Actions (Python 3.10/3.12/3.14 matrix)

---

## System Components

### 1. Core Pattern Engine (`patterns.py`)

**Responsibility:** Sequential pattern matching, discovery, prediction, and analysis

**Key Functions:**

- `parse_sequence()` — Parse human-readable sequences (e.g., "3R -> 2G") into tokens
- `symbol_sequence()` — Classify each candle as R (red), G (green), or Doji
- `find_sequence_occurrences()` — Find all matches of a pattern in OHLCV data
- `find_wildcard_sequence()` — Match patterns with wildcards (e.g., "3R -> * -> 2G")
- `discover_color_sequences()` — Auto-discover top recurring patterns
- `what_comes_next()` — Predict continuation probabilities (R/G/Doji distribution)
- `sequence_outcome_stats()` — Calculate win rate, returns, max gain/loss
- `reverse_pattern_finder()` — Find patterns preceding big price moves
- `sequence_confidence()` — Statistical significance scoring (z-score, p-value)
- `sequence_heatmap_data()` — Density visualization data

**Data Inputs:** pandas DataFrame with OHLCV columns (open, high, low, close, volume)  
**Data Outputs:** Match indices, statistics dicts, prediction probabilities, confidence scores

### 2. Web Dashboard (`dashboard.py`)

**Responsibility:** Interactive web UI with 12 tabs and ~31 Dash callbacks

**12 Tabs:**

1. **Chart** — Interactive candlestick + match highlights
2. **Matches** — Match table with timestamps and details
3. **Discovery** — Top 25 auto-discovered patterns
4. **Statistics** — Per-pattern outcome stats + predictions
5. **Heatmap** — Pattern density heatmap
6. **Reverse Finder** — Patterns preceding price moves
7. **Backtesting** — Equity curves, Sharpe, drawdown
8. **Multi-TF** — Cross-timeframe alignment
9. **Watchlist** — Saved sequence libraries
10. **Alerts** — Alert rules management
11. **ML Predict** — GradientBoosting prediction
12. **Settings** — User preferences

**Key Callbacks:**

- Pattern scan callback (main computation pipeline)
- Data fetch callback (Yahoo Finance integration)
- Alert rule CRUD callbacks
- ML model training/prediction callbacks
- Chart interaction callbacks (zoom, pan, hover)
- Settings save/reset callbacks

**Dependencies:** patterns.py, data_feeds.py, performance.py, ml_sequence.py, alerts.py, backtesting.py

### 3. Data Feeds & Caching (`data_feeds.py`)

**Responsibility:** External data sourcing with performance caching

**Key Functions:**

- `fetch_yahoo_data()` — Fetch OHLCV from Yahoo Finance
- `search_symbols()` — Symbol search and lookup
- `get_symbol_info()` — Get popular symbols (stocks, crypto, indices, forex, ETFs)
- LRU cache (50 entries, 5-min TTL) — Avoid redundant API calls

**Cache Behavior:** Prevents repeated Yahoo Finance calls within 5-minute window  
**Fallback:** Sample data loader for demo/testing

### 4. Performance Optimization (`performance.py`)

**Responsibility:** Vectorized scanning and efficient data processing

**Key Functions:**

- `vectorized_symbol_sequence()` — Numpy-accelerated candle classification (~50-100x faster)
- `vectorized_find_sequence()` — Vectorized sequence matching for simple patterns
- `process_in_chunks()` — Chunked processing for 10K+ candle datasets
- `downsample_ohlcv()` — OHLCV-aware downsampling preserving semantics
- `CandleCache` — Memoizes symbol arrays keyed by (df_id, length)
- `batch_sequence_stats()` — Compute stats for multiple sequences simultaneously
- `dataset_info()` — Return size metadata for optimization decisions

**Impact:** 10-50x speedup on large datasets, memory efficiency with 50-entry cache

### 5. Machine Learning (`ml_sequence.py`, `ml_baseline.py`)

**Responsibility:** Predictive modeling and feature engineering

**ml_sequence.py:**

- `engineer_sequence_features()` — 17 features (hl_ratio, oc_ratio, body_pct, mom_3/5/10, rsi_14, volatility, volume_ratio, etc.)
- `SequencePredictor` class — GradientBoosting with optional calibration
- Methods: `train()`, `predict()`, `cross_validate()`, `feature_importance()`, `save()`/`load()`

**ml_baseline.py:**

- RandomForest baseline model
- Feature engineering for traditional patterns

**Performance:** Calibrated probabilities, feature importance ranking, ~80+ feature variants tested

### 6. Alerts & Notifications (`alerts.py`)

**Responsibility:** Pattern monitoring and alert delivery

**Key Functions:**

- `add_alert_rule()` / `remove_alert_rule()` — CRUD operations
- `check_and_trigger()` — Evaluate all rules against new data
- `send_webhook()` — POST JSON to custom webhook URL
- `send_email()` — SMTP-based email dispatch
- `configure_email()` — Runtime email configuration (no disk persistence)
- `record_alert()` / `get_alert_history()` — SQLite-backed audit trail

**Channels:** Webhook + Email (mutually inclusive)  
**Security:** No credential persistence (memory-only SMTP config)

### 7. Additional Modules

| Module | Purpose |
|---|---|
| `preferences.py` | JSON-backed user profiles (theme, defaults, recents) |
| `multi_timeframe.py` | Cross-interval scanning + alignment detection |
| `watchlist.py` | Sequence library persistence (save/load/export/import) |
| `backtesting.py` | Performance evaluation (equity curve, Sharpe, drawdown) |
| `detection.py` | Traditional pattern detectors (17 patterns, secondary) |
| `api.py` | REST API endpoints (`/api/scan`, `/api/discover`, `/api/portfolio/scan`) |
| `portfolio.py` | Multi-symbol threaded scanning with ranking |
| `storage.py` | SQLite persistence + 30-day cleanup |
| `ingestion.py` | CSV validation and loading |
| `cli.py` | Command-line interface (5 commands) |

---

## Data Flow Architecture

### Request Lifecycle: Pattern Scan

```text
User Input (Dashboard)
    ↓
Sidebar: Select symbol, period, interval → Click "Fetch Data"
    ↓
data_feeds.fetch_yahoo_data() → Check LRU cache
    ├─ Cache HIT: Return cached DataFrame
    └─ Cache MISS: Fetch from yfinance, store in cache
    ↓
patterns.symbol_sequence() → Convert OHLCV to R/G/Doji sequence
    ↓
[For each pattern selected]
    patterns.find_sequence_occurrences() → Find match indices
    ↓
    patterns.sequence_outcome_stats() → Calculate win rate, returns
    ↓
    patterns.what_comes_next() → Predict continuation
    ↓
    performance.vectorized_find_sequence() → Fast scan for large datasets
    ↓
[Collect all results]
    ↓
dashboard.update_matches_tab() → Render table + chart highlights
    ↓
dashboard.update_statistics_tab() → Render outcome stats
    ↓
dashboard.update_chart() → Plotly chart with coloured match rectangles
    ↓
User sees results
```

### Background Job: Alert Checking

```text
[Live Refresh Timer: 60s default, configurable]
    ↓
alerts.check_and_trigger() → For each enabled alert rule:
    ├─ Fetch latest data (cached)
    ├─ Scan for pattern match
    ├─ If matched:
    │  ├─ alerts.send_webhook() → POST to custom URL
    │  ├─ alerts.send_email() → SMTP dispatch
    │  └─ alerts.record_alert() → SQLite history
    └─ Repeat for all rules
    ↓
[Update in-dashboard alert history panel]
    ↓
[Wait 60s, repeat]
```

### Startup Sequence

```text
python scripts/run_dash.py (or docker run ...)
    ↓
dashboard.py imports all modules
    ├─ patterns.py (core engine, no initialization needed)
    ├─ data_feeds.py (initialize LRU cache: 50 entries, 5-min TTL)
    ├─ performance.py (initialize CandleCache: empty dict)
    ├─ ml_sequence.py (load pre-trained model if exists)
    ├─ alerts.py (connect to SQLite, create schema if not exists)
    ├─ preferences.py (load JSON preferences from disk, or create defaults)
    └─ [Other modules lazy-load on first use]
    ↓
Dash.run_server(debug=False, host='127.0.0.1', port=8050)
    ↓
Dashboard available at http://127.0.0.1:8050/
    ↓
[Load sample data on first pageload if no data selected]
```

---

## Failure Modes & Recovery

| Failure | Impact | Detection | Recovery |
|---|---|---|---|
| Yahoo Finance API down | Cannot fetch live data | Network error in `fetch_yahoo_data()` | Fall back to sample data, cache stale data if available |
| Large dataset (10K+ candles) | Dashboard sluggish | Performance monitoring (dataset_info) | Use `process_in_chunks()` + `downsample_ohlcv()` |
| Alert webhook unreachable | Silent notification failure | HTTP timeout in `send_webhook()` | Log error to alert history, retry next cycle |
| Email SMTP misconfigured | Email alerts fail | SMTP connection error | Log error, continue with webhook alerts |
| SQLite database locked | Alert history unavailable | SQLite locked error | Retry with exponential backoff (3 attempts) |
| ML model file corrupted | ML Predict tab unavailable | Pickle load error | Graceful degradation (show "Model unavailable") |
| Memory exhaustion (CandleCache) | Cache eviction, slowdown | LRU eviction triggered | LRU automatically evicts oldest entries |

**General Recovery:**

- All module imports use try/except to prevent cascade failure
- Dashboard still functions with reduced features if optional modules fail
- Errors logged to console + optional file logging (not implemented yet)

---

## Scaling Considerations

### Horizontal Scaling

**Current Limitation:** Single-server Dash dashboard (stateful)

**To Scale:**

- Extract alert-checking to background job queue (Celery + Redis)
- Move data caching to distributed cache (Redis, Memcached)
- Use load balancer + multiple Dash instances with session sharing (Redis)

### Vertical Scaling (Current)

**Memory Optimization:**

- CandleCache limits in-memory candle arrays (50 entries max)
- Chunked processing for 10K+ candles
- OHLCV downsampling before chart rendering

**CPU Optimization:**

- Vectorized numpy scanning (50-100x faster than row-by-row)
- LRU cache (avoid redundant fetches)
- Batch sequence stats computation

**Current Limits:**

- Single symbol: handles 10K+ candles efficiently
- Multi-symbol portfolio scan: 50 symbols max (threaded, configurable workers)
- Alert rules: ~100 rules per instance (linear scan)

### Database Scaling

**Current:** SQLite (file-based, local)

**To Scale:**

- Switch to PostgreSQL or MySQL for multi-instance alert history
- Implement schema sharding by symbol or date range
- Use connection pooling (SQLAlchemy)

---

## Performance Characteristics

### Benchmark Results

**Sequential Pattern Matching:**

- Simple pattern (e.g., "3R -> 2G"): ~5-50ms for 1K candles
- Wildcard pattern (e.g., "3R -> * -> 2G"): ~20-100ms for 1K candles
- Vectorized scan (100 patterns simultaneously): ~50-200ms for 1K candles

**Data Fetch:**

- Yahoo Finance (cached): <10ms (LRU hit)
- Yahoo Finance (uncached): 500-2000ms (network dependent)
- CSV upload (validation + parse): 50-500ms (size dependent)

**Dashboard Render:**

- Candlestick chart (1K candles, 50 matches): ~100-300ms (browser-dependent)
- Match table (100 rows): ~50-100ms
- Tab switch: ~20-50ms (callback latency)

**ML Prediction:**

- Feature engineering (single sequence): ~10-50ms
- GradientBoosting predict: ~5-20ms
- Model training (1000 samples): ~1-5 seconds

---

## Security & Isolation

### Data Isolation

- **No multi-user support:** Single-user dashboard (authentication not implemented)
- **Local storage only:** SQLite + JSON files in container
- **No network persistence:** Alert history, watchlists not shared externally

### Credential Management

- **Email credentials:** In-memory only (never persisted to disk)
- **API keys:** yfinance uses free tier (no API key needed)
- **Webhook URLs:** Stored in SQLite alert rules (plain text, prefer HTTPS)

### Recommended Security Practices

For production deployment:

1. Use environment variables for webhook URLs (rotate regularly)
2. Enable email encryption (SMTP TLS/SSL)
3. Add authentication layer (not currently implemented)
4. Use reverse proxy (nginx) for HTTPS
5. Run in isolated container with no external volume mounts
6. Use secrets management (Kubernetes Secrets, HashiCorp Vault, etc.)

---

## Module Dependency Graph

```text
dashboard.py (top-level orchestrator)
├── patterns.py (core engine)
├── data_feeds.py (with cache)
├── performance.py (optimization)
├── ml_sequence.py (prediction)
├── ml_baseline.py (baseline model)
├── alerts.py (notifications)
├── backtesting.py (evaluation)
├── multi_timeframe.py (cross-TF analysis)
├── preferences.py (user config)
├── watchlist.py (library persistence)
├── storage.py (SQLite)
├── detection.py (traditional patterns)
├── ingestion.py (CSV validation)
├── cli.py (CLI commands)
└── api.py (REST API)
    └── All of the above (re-exported)
```

**No circular dependencies:** All imports flow downward (dashboard → modules, modules independent)

---

## Extensibility Points

### Adding a New Pattern Type

1. Create detector function in `patterns.py` or `detection.py`
2. Register in `match_named_token()` function
3. Add test case in `tests/test_sequence_patterns.py`
4. Update pattern syntax docs in README.md

### Adding a New Alert Channel

1. Create function in `alerts.py` (e.g., `send_slack()`)
2. Update `check_and_trigger()` to call new function
3. Update alert rule schema (add `slack_webhook_url` field)
4. Add dashboard UI controls in Alerts tab
5. Test with sample alert rule

### Adding a New Data Source

1. Create fetcher function in `data_feeds.py` (e.g., `fetch_crypto_api()`)
2. Cache result with same LRU mechanism
3. Update sidebar data source dropdown
4. Add error handling and fallback to sample data

---

## Deployment Options

### Local Development

```bash
python scripts/run_dash.py
# Dashboard at http://127.0.0.1:8050/
```

### Docker Container

```bash
docker build -t candle-patterns:latest .
docker run --rm -p 8050:8050 candle-patterns:latest run
```

### Cloud Deployment

- **AWS Elastic Beanstalk:** Deploy Docker container + RDS for alert history
- **Google Cloud Run:** Serverless container (stateless)
- **Heroku:** Direct Git push + buildpack
- **Kubernetes:** Helm charts for multi-replica deployment + Postgres

---

## Monitoring & Observability

### Current State

- **Logging:** Console output (stderr/stdout)
- **Metrics:** None (internal only)
- **Tracing:** None
- **Profiling:** None

### Recommended Additions

1. **Structured Logging** — Use Python `logging` with JSON formatter
2. **Metrics** — Prometheus metrics for alert triggers, API latency, cache hit rate
3. **Distributed Tracing** — OpenTelemetry for request flow
4. **APM** — Datadog, New Relic, or Sentry for error tracking

---

## Versioning & Release Process

**Semantic Versioning:** major.minor.patch (e.g., v1.4.0)

- **MAJOR** — Breaking API changes (rare)
- **MINOR** — New features, new pattern types, new dashboard tabs
- **PATCH** — Bug fixes, performance improvements, documentation

**Release Cadence:** Milestone-based (Phase completion), target bi-weekly

---

**Last Updated:** April 2, 2026  
**Next Review:** When architecture changes significantly (new modules, major refactoring)

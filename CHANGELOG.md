# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.4.0] - 2026-04-02 — Production Ready

### Added

- **E2E Tests** — 36 Playwright browser automation tests covering dashboard workflows
- **CI/CD Pipeline** — GitHub Actions with matrix testing (Python 3.10, 3.12, 3.14), linting, security scanning, Docker build
- **Architecture Documentation** — Comprehensive system design (docs/architecture.md) with data flows, failure modes, scaling considerations
- **Developer Onboarding** — AGENT_HANDOFF.md with exact setup commands, environment configuration, troubleshooting
- **Contribution Guidelines** — CONTRIBUTING.md with branch strategy, code style, testing requirements, PR workflow
- **PR Template** — .github/pull_request_template.md with checklist for quality gates
- **UML Diagrams** — Component and sequence diagrams (PlantUML) with generation instructions
- **PROJECT_GUIDELINES.md** — Repository governance and compliance standards
- **COMPLIANCE_REPORT.md** — Status report against PROJECT_GUIDELINES.md requirements
- **CODE_OF_CONDUCT.md** — Community conduct guidelines (Contributor Covenant 2.1)
- **THIRD_PARTY_NOTICES.md** — Attribution for all open-source dependencies
- **MAINTAINERS.md** — Active maintainer contact and decision-making process
- **CODEOWNERS** — GitHub auto-assignment of code reviews

### Fixed

- Dashboard lag on large datasets (5K+ candles) via chunked processing
- Markdown linting issues (100 errors → 0 via auto-formatter)
- Python type hints in dashboard.py (explicit list typing)
- Table formatting in documentation (proper markdown table syntax)

### Changed

- README.md restructured to follow PROJECT_GUIDELINES.md order (13 sections)
- MPDP.md elevated to canonical project status document
- Upgraded linting to enforce strict markdown standards
- Expanded test coverage (315 tests now, 100% pass rate)

### Deprecated

- No breaking changes in v1.4.0

---

## [1.3.0] - 2026-03-01 — REST API & Alerts

### Added

- REST API endpoints (/api/scan, /api/discover, /api/portfolio/scan)
- Sequence alerts with webhook + email support
- SQLite-backed alert history and persistence
- Portfolio scanner (multi-symbol threaded scanning)
- Email alert channel (SMTP/TLS support)
- Live refresh (configurable auto-refresh interval)
- Alert rule CRUD operations in dashboard Alerts tab

### Fixed

- Cache invalidation on symbol change
- Email configuration memory leak

### Changed

- Alerts tab now shows 7-day history
- Webhook retry logic with exponential backoff

---

## [1.2.0] - 2026-02-01 — Performance & ML

### Added

- GradientBoosting ML predictor with calibrated probabilities
- Feature engineering (17 features: hl_ratio, oc_ratio, body_pct, momentum, RSI, volatility, volume_ratio)
- Performance optimization (vectorized numpy scanning, 50-100x faster)
- Chunked processing for 10K+ candle datasets
- OHLCV-aware downsampling
- CandleCache memoization (50-entry LRU cache)
- ML Predict tab in dashboard
- Model persistence (save/load trained models)

### Fixed

- Dashboard hang on large datasets (chunking resolves issue)
- Memory exhaustion with unlimited caches

### Changed

- Pattern scanning now uses vectorized operations by default
- Cache TTL reduced from 10 min to 5 min for fresher data

---

## [1.1.0] - 2026-01-01 — Multi-Timeframe & Backtesting

### Added

- Multi-timeframe analysis (1H/4H/Daily/Weekly cross-interval scanning)
- Backtesting engine (equity curves, Sharpe ratio, max drawdown, profit factor)
- Sequence watchlist (save/load/export/import patterns as JSON)
- User preferences (theme, defaults, recents)
- Confidence scoring (z-score, p-value significance testing)
- Reverse pattern finder (discover sequences preceding big moves)
- Data ingestion/validation (CSV upload with schema validation)

### Fixed

- Symbol caching inconsistencies across timeframes
- Backtesting edge case with insufficient candles

### Changed

- Dashboard expanded from 8 tabs to 12 tabs
- Statistics tab now shows multi-sequence comparison

---

## [1.0.0] - 2025-12-01 — MVP Production Launch

### Added

- **Core Pattern Engine** — Sequential colour-based pattern matching with 15 named tokens
- **Pattern Scanner** — Find all occurrences of user-defined sequences (e.g., "3R -> 2G")
- **Wildcard Matching** — Support for wildcard patterns (e.g., "3R -> * -> 2G")
- **Auto-Discovery** — ML-driven discovery of top 25 recurring patterns
- **What-Comes-Next** — Predict continuation probabilities (R/G/Doji distribution)
- **Outcome Statistics** — Win rate, average return, max gain/loss per pattern
- **Interactive Dashboard** — 8-tab Dash web application with Plotly charts
- **Yahoo Finance Integration** — Real-time stock/crypto/index data fetching
- **Data Caching** — LRU cache with 5-min TTL for performance
- **Traditional Pattern Detectors** — 17 rule-based pattern detectors (secondary feature)
- **Dockerization** — Multi-stage Docker build + .dockerignore
- **Testing Suite** — 200+ unit tests with pytest
- **CLI Tools** — Command-line interface with 5 core commands
- **Documentation** — README, MPDP, pattern catalog, dashboard guide

### Security

- No secrets stored in repository (environment variables only)
- SQLite databases local-only (not persisted externally)
- SMTP credentials in-memory only (never to disk)

### Known Limitations

- Single-user dashboard (no authentication)
- Local storage only (not distributed)
- Yahoo Finance API rate limits apply (no caching for fast quotes)

---

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0) — Incompatible API changes (breaking changes)
- **MINOR** (0.X.0) — New features, backward compatible
- **PATCH** (0.0.X) — Bug fixes, backward compatible

Example: v1.4.0 = Major version 1, Minor version 4, Patch version 0

---

## How to Report Issues

- **Bug reports** → [GitHub Issues](https://github.com/Zed-777/Sequential-Candle-Patterns/issues)
- **Security issues** → See [SECURITY.md](SECURITY.md)
- **Feature requests** → [GitHub Discussions](https://github.com/Zed-777/Sequential-Candle-Patterns/discussions)

---

## Release Schedule

- **Phase completions** — New minor version (v1.X.0)
- **Bug fixes** — New patch version (v1.4.X)
- **Major refactors/API changes** — New major version (v2.0.0)

---

**Last Updated:** April 2, 2026

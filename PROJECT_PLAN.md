# Single Source of Truth (SSoT) — Development & Progress Plan ✅

**Purpose:**
This document is the canonical, living SSoT for the Sequential Pattern Analysis System (CSV → Patterns → Dashboard/CLI/Notebook). Use it to plan, assign, track, and report all work for the project.

---

## Project Snapshot 🔎
- **Name:** Sequential Pattern Analysis System
- **MVP Goal:** CSV ingestion + validation, rule-based detection (>=5 patterns), minimal Dash prototype (upload + annotated candlestick chart), CLI `analyzer run`, unit tests, CI pipeline, Docker image.
- **Cadence:** Weekly async updates + weekly 30-min sync/demo (day/time by team agreement).
- **Primary files:** `PROJECT_PLAN.md` (this document), `progress_tracker.csv` (tracker), GitHub Project board, `docs/` for architecture & GDPR.

---

## How to Use This SSoT 💡
- The SSoT is the authoritative source for milestones, status, owners, acceptance criteria and decisions. Update **the tracker** immediately when statuses change.
- Link each tracker row to a GitHub Issue/PR and a Milestone (use `#<issue>` format in tracker notes).
- Use RAG (Green/Amber/Red) and `%complete` for quick status assessment.
- Owners update their tasks before the weekly sync and post a short status blurb in the team thread.

---

## Roles & Responsibilities 🔧
- **Product Owner (PO):** [Name] — prioritization, acceptance, stakeholder communication.
- **Tech Lead:** [Name] — architecture reviews, CI/CD, final merges.
- **Engineering Leads:** Assigned per module (ingest, detection, ui, ml, infra).
- **QA Owner:** [Name] — test plan, regression, integration tests.
- **Compliance Owner:** [Name] — GDPR & security.

*(Replace placeholders with real names in the tracker or issue assignments.)*

---

## Tracker Schema & Conventions 🧾
- **Columns:** id,title,milestone,priority,owner,estimate_days,start,due,status,pct_complete,RAG,github_issue,notes
- **Status values:** To Do / In Progress / Review / QA / Blocked / Done
- **Priority:** P0 / P1 / P2
- **Branch naming:** `feature/<short>-<issue#>`, `fix/<issue#>`, `chore/<area>`
- **Commit message template:** `type(scope): short description (#<issue>)`

---

## Initial High-Level Milestones & Acceptance Criteria 📅
1. **MVP — Ingest → Detect → UI** (Est. 3–4 weeks)
   - Acceptance: Upload CSV → success validation; candlestick chart with at least 5 rule-based patterns annotated; CLI `analyzer run` outputs report CSV; tests pass in CI.
2. **Pattern Mining & OPP** (Est. 3–4 weeks)
   - Acceptance: OPP miner implemented; sample report and notebook demonstrating frequent order patterns.
3. **ML Models & Backtesting** (Est. 4–6 weeks)
   - Acceptance: Baseline RF/LSTM models trained; evaluation using TimeSeriesSplit; backtest module reporting Sharpe/drawdown.
4. **Productionization & Compliance** (Est. 2–3 weeks)
   - Acceptance: Docker image, GitHub Actions CI, GDPR procedures documented, encryption where applicable.

---

## CI/CD & Quality Gates ✅
- **Pre-merge checks:** Lint (ruff/black), Unit tests (pytest, coverage target), Type checking (mypy/Pylance), Security scan (bandit)
- **Deploy:** Multi-stage Docker build, staging deploy for acceptance, production on manual approval.
- **Automation:** Weekly progress report via script that reads `progress_tracker.csv`.

---

## GDPR & Security Checklist 🔐
- Data minimization & anonymization patterns.
- Right-to-erasure script and API endpoint.
- TLS in transit; AES for sensitive storage.
- Audit logs for session and data access.
- Document policies in `docs/GDPR.md`.

---

## Reporting & Meetings 📣
- **Weekly async update:** Owners update tracker by Friday EOD.
- **Weekly summary:** PO shares a 1–2 paragraph status and highlights (RAG).  
- **Monthly demo:** Live demo of features completed.

---

## Risks & Mitigations ⚠️
- **Model data scarcity:** Use rule-based baseline + synthetic data + strict evaluation pipeline.
- **GDPR gaps:** Early compliance review + automated data retention and erasure.
- **Performance on large series:** Add batch processing and profiling; support DB (Timescale) for scale.

---

## Files Created & Next Steps ✨
- Created: `PROJECT_PLAN.md` (this document) and `progress_tracker.csv` in repository root.
- Next: Create GitHub Issues and Milestones for initial tracker rows and scaffold a minimal Dash prototype branch `feature/mvp-ui-<issue#>`.

---

## Recent progress (automated updates)
- CSV ingestion and validator implemented and tested. ✅
- Rule-based detection skeleton (Doji, Hammer, Bullish Engulfing, Morning Star) implemented with unit tests. ✅
- CLI `analyzer run` implemented (Typer) and writes pattern CSV report. ✅
- Minimal Dash dashboard prototype implemented to upload CSV and annotate detected patterns. ✅
- CI workflow added (`.github/workflows/ci.yml`) to run lint/format/tests. ✅
- Updated `progress_tracker.csv` with current statuses. ✅
- Repository created at https://github.com/Zed-777/candle-patterns and draft PR opened: https://github.com/Zed-777/candle-patterns/pull/1 ✅

---

---

## Contact & Ownership
- **Maintainers:** Add team contacts here; include GitHub handles and preferred communication channel.

---

> Keep this document lightweight, update it during planning and after major decisions. Link PRs & issues directly to tracker rows.

---

*End of SSoT — keep this file as the single source of truth for development and tracking.*

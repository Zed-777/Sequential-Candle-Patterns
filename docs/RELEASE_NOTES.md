Release v0.1.0 — MVP baseline

Date: 2026-01-28

Summary:
- MVP features implemented: CSV ingestion & validation, rule-based detection (multiple patterns), CLI `analyzer run`, minimal Dash dashboard prototype (upload + annotated candlestick chart), OPP miner (variable-length + top-K summarization), per-pattern reporting and backtest skeleton.
- CI: GitHub Actions added to run lint/format/tests and enforces minimum coverage (`--cov-fail-under=80`).
- Repository cleanup: normalized file encodings to UTF-8 and removed corrupt backup files (permanent deletion).
- Tests: unit + integration tests pass locally (13 passed).

Next actions (manual/repo-owner required):
- Publish Docker image to a registry (requires credentials/secrets).  
- Add additional sample datasets and expand integration tests.  
- Begin ML POC for pattern discovery and add evaluation pipeline.

Notes:
- If you want me to publish a Docker image and create a GitHub Release draft, provide registry credentials or confirm I should create a draft release only (no published image).
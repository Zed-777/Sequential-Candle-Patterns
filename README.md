# Candlestick Patterns — Sequential Pattern Analysis System

[![tests](https://github.com/Zed-777/candle-patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Zed-777/candle-patterns/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Zed-777/candle-patterns/branch/feature/mvp-next-clean/graph/badge.svg?token=)](https://codecov.io/gh/Zed-777/candle-patterns)

This repository contains the Sequential Pattern Analysis System (CSV → patterns → dashboard/CLI/notebook).

Quickstart
1. Local env (recommended): run the venv setup script to create `.venv` and install dev deps:
   - Windows (PowerShell): `scripts\setup_venv.ps1`
   - macOS / Linux: `scripts/setup_venv.sh`
   After running the script activate the venv (PowerShell: `.\.venv\Scripts\Activate.ps1`; bash: `source .venv/bin/activate`).
2. (Optional) Conda: CI uses Miniforge/Conda; if you prefer conda locally see `scripts/setup_conda_sample.sh` (not required).
3. Activate the `.venv` and start the Dash app: `python -m dash` (or follow the dashboard README).

Build & run via Docker (lightweight example):

```bash
# build
docker build -t candle-patterns:latest .
# run the CLI help
docker run --rm candle-patterns:latest --help
# run the analyzer on a CSV
docker run --rm -v $(pwd):/data candle-patterns:latest run /data/tests/data/synthetic.csv --out /data/report.csv
```

Note: CI uploads coverage to Codecov using the `codecov` action — add the repository secret `CODECOV_TOKEN` to enable uploads and make the badge work.  

Current status: unit tests and integration test pass locally in `.venv`; branch `feature/mvp-next-clean` is ready for PR and review.

Files of interest:
- `PROJECT_PLAN.md` — canonical Single Source of Truth (SSoT)
- `progress_tracker.csv` — project tracker
- `requirements.txt` / `dev-requirements.txt` — dependencies
- `src/` — source code
- `tests/` — unit tests

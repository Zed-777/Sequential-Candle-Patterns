# Candlestick Patterns — Sequential Pattern Analysis System

[![tests](https://github.com/Zed-777/candle-patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Zed-777/candle-patterns/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Zed-777/candle-patterns/branch/feature/mvp-next-clean/graph/badge.svg?token=)](https://codecov.io/gh/Zed-777/candle-patterns)

This repository contains the Sequential Pattern Analysis System (CSV → patterns → dashboard/CLI/notebook).

Quickstart
1. Run the environment setup script: `scripts\setup_env.ps1` (Windows) or `scripts/setup_env.sh` (Linux/macOS).
2. Activate the `.venv` and start the Dash app: `python -m dash` (or follow the dashboard README).

Files of interest:
- `PROJECT_PLAN.md` — canonical Single Source of Truth (SSoT)
- `progress_tracker.csv` — project tracker
- `requirements.txt` / `dev-requirements.txt` — dependencies
- `src/` — source code
- `tests/` — unit tests

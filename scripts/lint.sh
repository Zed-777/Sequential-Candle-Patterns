#!/usr/bin/env bash
set -euo pipefail
"${CONDA_EXE:-conda}" run -p ./.conda ruff check .
"${CONDA_EXE:-conda}" run -p ./.conda black --check .
"${CONDA_EXE:-conda}" run -p ./.conda pytest -q
echo "Linting and tests passed"
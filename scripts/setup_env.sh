#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r dev-requirements.txt
python -m ipykernel install --user --name=candle-patterns --display-name "Candle Patterns (.venv)"
echo "Environment setup complete. Activate with: source .venv/bin/activate"
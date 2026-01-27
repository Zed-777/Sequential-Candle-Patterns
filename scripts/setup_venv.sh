#!/usr/bin/env bash
set -euo pipefail

# Create or update a local virtualenv at .venv and install dependencies
# Usage: bash scripts/setup_venv.sh
python -m venv .venv
echo "Created .venv virtual environment"

# shellcheck disable=SC1091
source .venv/bin/activate
echo "Activated .venv"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt -r dev-requirements.txt
echo "Installed requirements into .venv"
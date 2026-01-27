#!/usr/bin/env bash
# Sample conda setup (CI uses Miniforge). Use only if you prefer conda locally.
set -euo pipefail
conda create -p ./.conda python=3.10 -y
conda run -p ./.conda pip install -r requirements.txt -r dev-requirements.txt
echo "Installed requirements into ./.conda (sample)"
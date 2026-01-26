#!/usr/bin/env bash
set -euo pipefail
ENV_PATH="$(pwd)/.conda"
conda create -p "$ENV_PATH" python=3.10 -y
conda run -p "$ENV_PATH" python -m pip install --upgrade pip
conda run -p "$ENV_PATH" pip install -r requirements.txt
conda run -p "$ENV_PATH" pip install -r dev-requirements.txt
echo "Conda environment created at $ENV_PATH"
echo "Use: conda activate $ENV_PATH or conda run -p $ENV_PATH <command>"
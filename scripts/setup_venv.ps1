# PowerShell script to create a local virtualenv and install dependencies
# Usage: Open PowerShell (no admin required) and run: .\scripts\setup_venv.ps1

$ErrorActionPreference = 'Stop'

python -m venv .venv
Write-Host 'Created .venv virtual environment'

# Activate the venv for the current session
if (Test-Path .\.venv\Scripts\Activate.ps1) {
    . .\.venv\Scripts\Activate.ps1
    Write-Host 'Activated .venv'
} else {
    Write-Host 'Unable to find Activate.ps1 in .venv. Please activate manually: .\.venv\Scripts\Activate.ps1'
}

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt -r dev-requirements.txt
Write-Host 'Installed requirements into .venv'
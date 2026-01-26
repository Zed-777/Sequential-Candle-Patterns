# PowerShell setup script for Windows
Set-StrictMode -Version Latest
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r dev-requirements.txt
python -m ipykernel install --user --name=candle-patterns --display-name "Candle Patterns (.venv)"
Write-Host "Environment setup complete. Activate with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Green

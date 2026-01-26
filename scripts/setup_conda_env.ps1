# PowerShell script to create a local conda env for this project (Windows)
$envPath = Join-Path $PWD ".conda"
conda create -p $envPath python=3.10 -y
conda run -p $envPath pip install --upgrade pip
conda run -p $envPath pip install -r requirements.txt
conda run -p $envPath pip install -r dev-requirements.txt
Write-Host "Conda environment created at $envPath" -ForegroundColor Green
Write-Host "Use: conda activate $envPath (or conda run -p $envPath <command>)" -ForegroundColor Yellow

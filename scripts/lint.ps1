# PowerShell lint script for Windows
& 'C:/Users/zmgdi/miniforge3/Scripts/conda.exe' run -p .\.conda ruff check .
if ($LASTEXITCODE -ne 0) { Write-Host "ruff check failed" -ForegroundColor Red; exit $LASTEXITCODE }
& 'C:/Users/zmgdi/miniforge3/Scripts/conda.exe' run -p .\.conda black --check .
if ($LASTEXITCODE -ne 0) { Write-Host "black check failed" -ForegroundColor Red; exit $LASTEXITCODE }
& 'C:/Users/zmgdi/miniforge3/Scripts/conda.exe' run -p .\.conda pytest -q
if ($LASTEXITCODE -ne 0) { Write-Host "tests failed" -ForegroundColor Red; exit $LASTEXITCODE }
Write-Host "Linting and tests passed" -ForegroundColor Green

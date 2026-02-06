@echo off
setlocal enabledelayedexpansion
set PYTHONPATH=src
.venv\Scripts\python.exe start_waitress.py %*
exit /b %errorlevel%

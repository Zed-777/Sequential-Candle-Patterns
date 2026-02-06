import sys
from pathlib import Path
# Ensure package root 'src' is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
# Import and run the dashboard module (it calls app.run)
import importlib
importlib.import_module('candle_patterns.dashboard')

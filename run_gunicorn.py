#!/usr/bin/env python
"""
Start the Dash dashboard using Gunicorn (production WSGI server).
This bypasses Flask's development server issues on Windows.
"""
import os
import sys
import subprocess

# Set PYTHONPATH
os.environ['PYTHONPATH'] = 'src'

# Check if gunicorn is installed
try:
    import gunicorn
except ImportError:
    print("Gunicorn not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])

# Run gunicorn
print("Starting Dash dashboard via Gunicorn on http://localhost:8050")
print("Press Ctrl+C to stop\n")

subprocess.call([
    sys.executable, "-m", "gunicorn",
    "--bind", "127.0.0.1:8050",
    "--workers", "1",
    "--timeout", "120",
    "--worker-class", "sync",
    "candle_patterns.dashboard:server"
])

"""
E2E test fixtures — starts the Dash server in a subprocess for Playwright.

Usage:
    pytest tests/e2e/ -m e2e --headed   # watch in browser
    pytest tests/e2e/ -m e2e            # headless (CI)
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Register the Playwright plugin only for e2e tests
pytest_plugins = ["pytest_playwright.pytest_playwright"]

ROOT = Path(__file__).resolve().parent.parent.parent
SERVER_SCRIPT = ROOT / "scripts" / "run_dash.py"
HOST = "127.0.0.1"
PORT = 8050
BASE_URL = f"http://{HOST}:{PORT}"
STARTUP_TIMEOUT = 60  # seconds (dashboard imports are heavy)


def _port_in_use(port: int) -> bool:
    """Check if a port is already bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, port)) == 0


@pytest.fixture(scope="session")
def dash_server():
    """Start the Dash app in a subprocess and wait until it's ready.

    Yields the base URL. Kills the server when the session ends.
    """
    if _port_in_use(PORT):
        # Server already running (developer launched it manually) — reuse it
        yield BASE_URL
        return

    env = {
        "PYTHONPATH": str(ROOT / "src"),
        "PYTHONUNBUFFERED": "1",
        "PATH": str(ROOT / ".venv" / "Scripts") + ";" + str(Path(sys.executable).parent),
    }

    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        cwd=str(ROOT),
        env={**dict(__import__("os").environ), **env},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Wait for the server to start
    deadline = time.time() + STARTUP_TIMEOUT
    while time.time() < deadline:
        if _port_in_use(PORT):
            # Give Dash a moment to finish registering callbacks
            time.sleep(2)
            break
        if proc.poll() is not None:
            out = proc.stdout.read().decode() if proc.stdout else ""
            pytest.fail(f"Dash server exited prematurely (code {proc.returncode}):\n{out}")
        time.sleep(0.5)
    else:
        proc.kill()
        pytest.fail(f"Dash server did not start within {STARTUP_TIMEOUT}s")

    yield BASE_URL

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture()
def page(dash_server, page):
    """Override pytest-playwright's page fixture to inject the base URL."""
    page.goto(dash_server)
    page.wait_for_load_state("networkidle")
    return page

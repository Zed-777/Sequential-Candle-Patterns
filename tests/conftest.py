# Ensure `src` is on sys.path for tests when package isn't installed
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

pytest_plugins = ["pytest_playwright.pytest_playwright", "pytest_asyncio.plugin"]


@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8050"

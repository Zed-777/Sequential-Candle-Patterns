# Ensure `src` is on sys.path for tests when package isn't installed
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Only register playwright plugin if installed (optional for E2E tests)
pytest_plugins: list[str] = []
try:
    import pytest_playwright  # noqa: F401

    pytest_plugins.append("pytest_playwright.pytest_playwright")
except ImportError:
    pass


@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8050"

# AGENT_HANDOFF.md — Developer Onboarding & Setup Guide

**Complete guide for new developers to set up, run, and contribute to Candlestick Patterns.**

**Goal:** Get a new contributor running the project in under 30 minutes.

---

## Quick Start (5 minutes)

### Prerequisites

- Python 3.10+ (check: `python --version`)
- Git (check: `git --version`)
- pip (usually included with Python)

### Setup

**macOS/Linux:**

```bash
git clone https://github.com/Zed-777/candle-patterns.git
cd candle-patterns
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -q
# Expected: 315 passed, 4 skipped
```

**Windows PowerShell:**

```powershell
git clone https://github.com/Zed-777/candle-patterns.git
cd candle-patterns
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest tests/ -q
# Expected: 315 passed, 4 skipped
```

### Run Dashboard

```bash
python scripts/run_dash.py
# Opens at http://localhost:8050/
```

✅ **You're done!** Dashboard is running.

---

## Environment Setup

### Python Version

**Supported:** Python 3.10, 3.12, 3.14 (CI tests all three)

**Check your version:**

```bash
python --version
```

**If you don't have 3.10+:**

- **macOS:** `brew install python@3.12`
- **Ubuntu/Debian:** `sudo apt-get install python3.12`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

### Virtual Environment

**Why:** Isolates project dependencies, prevents global package conflicts

**Create & activate:**

```bash
# macOS/Linux
python -m venv .venv
source .venv/bin/activate

# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
python -m venv .venv
.venv\Scripts\activate.bat
```

**Verify activation:**

```bash
which python  # macOS/Linux: should show .venv path
where python  # Windows: should show .venv path
```

**Deactivate when done:**

```bash
deactivate
```

### Dependencies

**Install from pyproject.toml:**

```bash
pip install -e ".[dev]"
```

**Explanation:**

- `-e` = editable install (changes to `src/` reflected immediately)
- `.[dev]` = install package + dev dependencies (pytest, black, ruff, etc.)

**What this installs:**

- Core: pandas, numpy, plotly, dash, scikit-learn, yfinance
- Dev extras: pytest, pytest-cov, black, ruff, bandit

**Verify installation:**

```bash
python -c "import candle_patterns; print(candle_patterns.__file__)"
```

---

## .env Configuration

### Environment Variables

Create `.env` file in project root (copy from `.env.example` if it exists, otherwise create):

```bash
# .env (never commit this file!)
# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use Gmail app password, not account password
SMTP_TLS=true

# Webhook Configuration (optional)
DEFAULT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Dashboard Settings (optional)
DASH_DEBUG=false
DASH_dev_tools_ui=false
```

**Security Rules:**

- ✅ Store `.env` locally (never commit to git)
- ✅ Use app-specific passwords (Gmail) or API tokens, not account passwords
- ✅ Rotate credentials regularly
- ✅ For production: use secret manager (Kubernetes Secrets, Hashicorp Vault)

**Loading environment variables:**

The app automatically loads `.env` at startup via `python-dotenv` (included in dependencies).

---

## Running the Project

### Dashboard (Main Application)

```bash
python scripts/run_dash.py
```

**Opens at:** [http://localhost:8050/](http://localhost:8050/)

**Expected output:**

```text
Dash is running on http://127.0.0.1:8050/
WARNING in werkzeug: Running on development server...
```

**Stop dashboard:** Press `Ctrl+C` in terminal

### Tests

```bash
# Run all tests
pytest tests/ -q
# Expected: 315 passed, 4 skipped

# Run specific test file
pytest tests/test_sequence_patterns.py -v

# Run with coverage
pytest tests/ --cov=src/candle_patterns --cov-report=html

# Run only fast tests (skip network/E2E)
pytest tests/ -m "not network and not e2e" -q
```

### Linting & Formatting

```bash
# Check style (ruff lint)
ruff check src/

# Auto-format code (black)
black src/ tests/

# Check type hints (future: mypy/pyright)
# Currently not enforced in CI
```

### CLI Commands

```bash
# List available commands
python -m candle_patterns --help

# Run dashboard (same as scripts/run_dash.py)
python -m candle_patterns run

# Clean up old data (30+ days)
python -m candle_patterns cleanup

# Train ML model
python -m candle_patterns train --data data/samples/AAPL_sample.csv

# Make predictions
python -m candle_patterns predict --model models/sequence_predictor.pkl

# Backtest a pattern
python -m candle_patterns backtest --pattern "3R -> 2G" --data data/samples/AAPL_sample.csv
```

### Docker

```bash
# Build image
docker build -t candle-patterns:latest .

# Run container (development)
docker run --rm -p 8050:8050 -v $(pwd):/app candle-patterns:latest run

# Run container (production)
docker run --rm -p 8050:8050 candle-patterns:latest run
```

---

## Dataset Location & Retrieval

### Sample Datasets

**Location:** `data/samples/`

**Files:**

- `AAPL_sample.csv` — Apple stock (200 candles, daily)
- `BTC_sample.csv` — Bitcoin (200 candles, daily)
- Other samples as added

**Format:** CSV with columns `open,high,low,close,volume,date`

**Load in dashboard:**

1. Click "Load Sample Data" in sidebar
2. Or use CLI: `python -m candle_patterns predict --data data/samples/AAPL_sample.csv`

### Fetching Real Data

**Via Yahoo Finance (dashboard):**

1. Type symbol (e.g., "AAPL", "BTC-USD")
2. Select period (1d, 5d, 1mo, 3mo, 1y, max)
3. Select interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
4. Click "Fetch Data"

**Via Python:**

```python
from candle_patterns.data_feeds import fetch_yahoo_data
df = fetch_yahoo_data("AAPL", period="3mo", interval="1d")
print(df)
```

### Custom Data Upload

1. Prepare CSV with columns: `open,high,low,close,volume,date`
2. Click "Upload CSV" in dashboard
3. System validates OHLCV format
4. Data loaded into scanner

---

## Model Training & Evaluation

### Training ML Sequence Predictor

```bash
# Command line
python -m candle_patterns train --data data/samples/ --output models/my_model.pkl

# Python API
from candle_patterns.ml_sequence import train_sequence_predictor
from candle_patterns.data_feeds import fetch_yahoo_data

df = fetch_yahoo_data("AAPL", period="1y")
predictor = train_sequence_predictor(df, hold_period=5, model_path="models/aapl_model.pkl")
```

### Using Trained Model

```python
from candle_patterns.ml_sequence import SequencePredictor

predictor = SequencePredictor.load("models/aapl_model.pkl")

# Predict for a sequence
from candle_patterns.patterns import find_sequence_occurrences
matches = find_sequence_occurrences(df, "3R -> 2G")
predictions = [predictor.predict_next_outcome(df, idx) for idx in matches]
for pred in predictions:
    print(f"Pattern outcome: {pred['predicted_class']} (confidence: {pred['confidence']:.2f})")
```

### Backtesting

```bash
# Command line
python -m candle_patterns backtest --pattern "3R -> 2G" --data data/samples/AAPL_sample.csv

# Python API
from candle_patterns.backtesting import BacktestEngine
from candle_patterns.data_feeds import fetch_yahoo_data

df = fetch_yahoo_data("AAPL", period="1y")
bt = BacktestEngine(df, initial_capital=10000)
result = bt.run(["3R -> 2G", "5R -> 3G"])
print(f"Sharpe ratio: {result['sharpe']:.2f}")
print(f"Max drawdown: {result['max_drawdown']:.2%}")
```

---

## Pre-commit Hooks (Optional but Recommended)

Automatically check code before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks from .pre-commit-config.yaml
pre-commit install

# Run manually (all files)
pre-commit run --all-files

# Run manually (staged files only)
pre-commit run
```

**Checks:**

- Code formatting (black)
- Import sorting (isort)
- Linting (ruff)
- YAML/JSON validation
- Trailing whitespace
- Large file detection

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'candle_patterns'"

**Solution:** You're not in the virtual environment or didn't install package.

```bash
# Check virtual environment is activated (should show .venv in prompt)
which python  # macOS/Linux
where python  # Windows

# If not activated:
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows

# Re-install package
pip install -e ".[dev]"
```

### "Yahoo Finance API error / Connection timeout"

**Solution:** Network issue or API rate limit.

```bash
# Check internet connection
ping google.com

# Try again (might be temporary)
python scripts/run_dash.py

# Use sample data instead
# Click "Load Sample Data" in dashboard
```

### "Port 8050 already in use"

**Solution:** Another process is using port 8050.

```bash
# Kill process on port 8050
lsof -ti:8050 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8050  # Windows (find PID, then taskkill /PID <pid>)

# Or use different port
python -c "from candle_patterns.dashboard import app; app.run_server(debug=True, port=8051)"
```

### "Tests fail locally but pass in CI"

**Possible reasons:**

- Python version mismatch (CI tests 3.10, 3.12, 3.14)
- Missing dev dependencies
- System-specific path issues

**Solution:**

```bash
# Match CI Python version
python3.12 -m venv .venv
source .venv/bin/activate  # or Windows equivalent
pip install -e ".[dev]"
pytest tests/ -v
```

### "Dashboard hangs when scanning large dataset"

**Solution:** Use chunked processing for 10K+ candles.

```python
# In code using patterns.py:
from candle_patterns.performance import process_in_chunks

# Instead of:
matches = find_sequence_occurrences(df, "3R -> 2G")  # Slow on 10K+ rows

# Use:
from candle_patterns.performance import process_in_chunks
matches = process_in_chunks(df, find_sequence_occurrences, "3R -> 2G", chunk_size=1000)
```

### "ML model training is slow"

**Solution:** Use smaller sample or faster model.

```python
# Use subset of data
df_sample = df.iloc[-1000:]  # Last 1000 candles

# Or use RandomForest instead of GradientBoosting (faster, less accurate)
from candle_patterns.ml_baseline import train_ml_model
model = train_ml_model(df_sample, model_type='rf')
```

---

## Common Tasks

### Adding a New Pattern Detector

1. **Create function in `src/candle_patterns/patterns.py`:**

```python
def match_new_pattern(df, row_idx):
    """Detect custom pattern at row_idx."""
    # Your pattern logic here
    return is_match  # True/False
```

1. **Register in `match_named_token()`:**

```python
def match_named_token(df, row_idx, token):
    # ...existing tokens...
    elif token == "MyNewPattern":
        return match_new_pattern(df, row_idx)
```

1. **Write test in `tests/test_sequence_patterns.py`:**

```python
def test_my_new_pattern():
    df = get_sample_data()
    assert match_new_pattern(df, 10) == True
    assert match_new_pattern(df, 5) == False
```

1. **Run tests:**

```bash
pytest tests/test_sequence_patterns.py::test_my_new_pattern -v
```

### Adding a New Alert Channel

1. **Add function in `src/candle_patterns/alerts.py`:**

```python
def send_slack(message, webhook_url):
    """Send alert to Slack."""
    import requests
    requests.post(webhook_url, json={"text": message})
```

1. **Update `check_and_trigger()`:**

```python
if rule.get('slack_webhook_url'):
    send_slack(message, rule['slack_webhook_url'])
```

1. **Update dashboard UI to include Slack field**

2. **Write test & verify**

### Running E2E Tests Locally

```bash
# Install Playwright (one-time)
pip install playwright
playwright install

# Run E2E tests
pytest tests/e2e/ -v

# Run specific E2E test
pytest tests/e2e/test_dashboard_smoke.py::test_chart_loads -v
```

---

## Development Workflow

### Creating a Feature Branch

```bash
# Start from main branch
git checkout feature/mvp-setup  # Current development branch

# Create feature branch
git checkout -b feature/my-feature-name

# Make changes, test locally
pytest tests/ -q

# Commit with descriptive message
git add .
git commit -m "Add support for XYZ pattern matching"

# Push to GitHub
git push origin feature/my-feature-name

# Create Pull Request on GitHub
# (link to related MPDP task if applicable)
```

### Code Style Requirements

**Black formatter (enforced):**

```bash
black src/candle_patterns
```

**Ruff linter (enforced):**

```bash
ruff check src/
ruff check --fix src/  # Auto-fix issues
```

**Docstrings (required):**

```python
def find_sequence_occurrences(df, sequence, start_idx=0):
    """
    Find all occurrences of a sequence in OHLCV data.
    
    Args:
        df: pandas DataFrame with OHLC columns
        sequence: str, e.g. "3R -> 2G"
        start_idx: int, starting row (default 0)
    
    Returns:
        list of int, match indices
    """
```

### Test Coverage

**Run with coverage report:**

```bash
pytest tests/ --cov=src/candle_patterns --cov-report=html
# Opens htmlcov/index.html for detailed report
```

**Target:** 80%+ coverage on core modules (patterns, dashboard, ml_sequence)

---

## Git Workflow

### Committing Code

**Format:** Imperative mood, concise (50 chars), reference issues

```bash
# Good ✅
git commit -m "Add follow-up pattern matching (#123)"
git commit -m "Fix dashboard lag on large datasets"
git commit -m "Refactor vectorized_symbol_sequence for clarity"

# Bad ❌
git commit -m "WIP stuff"
git commit -m "Fixed a bunch of things"
git commit -m "asdf"
```

### Pull Request Checklist

Before submitting PR:

- [ ] All tests passing (`pytest -q`)
- [ ] Code formatted (`black src/`)
- [ ] Linting passes (`ruff check src/`)
- [ ] New tests added (if feature)
- [ ] Documentation updated (if needed)
- [ ] Docstrings added (if new functions)
- [ ] Linked to related MPDP.md task or issue
- [ ] Title & description clear & concise

---

## Resources & Getting Help

**Documentation:**

- [README.md](../README.md) — Feature overview
- [MPDP.md](../MPDP.md) — Roadmap & task tracking
- [architecture.md](../docs/architecture.md) — System design
- [SECURITY.md](../SECURITY.md) — Data handling & security

**Code References:**

- See class/function docstrings for detailed API docs
- Check tests for usage examples

**Common Issues:**
See "Troubleshooting" section above

**Contributing:**

- See [CONTRIBUTING.md](./CONTRIBUTING.md) for workflow & conventions
- Create GitHub issue for bugs/features

---

**Last Updated:** April 2, 2026  
**Status:** Ready for use  
**Feedback:** Open GitHub issue if setup instructions unclear

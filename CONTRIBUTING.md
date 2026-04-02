# CONTRIBUTING.md — Contribution Guidelines

**How to contribute to Candlestick Patterns: workflow, code style, testing, and review process.**

---

## Welcome Contributors

We're excited to have you contribute to Candlestick Patterns. This guide outlines how to submit code, report issues, and maintain code quality.

---

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Follow AGENT_HANDOFF.md** to set up environment
4. **Create a feature branch** (see "Branch Strategy" below)
5. **Make changes** following code standards
6. **Write/update tests** (required for all features)
7. **Submit a Pull Request** (see "Pull Request Process" below)

---

## Branch Strategy

### Naming Convention

**Pattern:** `{type}/{short-description}`

**Types:**

- `feature/` — New feature or enhancement
- `bugfix/` — Bug fix
- `hotfix/` — Urgent production fix
- `docs/` — Documentation only
- `refactor/` — Code refactoring (no behavior change)
- `test/` — Test additions or improvements
- `perf/` — Performance optimization

**Examples:**

```bash
git checkout -b feature/add-support-for-doji-patterns
git checkout -b bugfix/fix-dashboard-lag-on-large-datasets
git checkout -b docs/improve-architecture-documentation
git checkout -b perf/optimize-vectorized-scanning
```

### Branching from Current Development

```bash
# Current development branch
git checkout feature/mvp-setup  # Where new work is based

# Create your feature branch
git checkout -b feature/my-feature
```

---

## Commit Message Guidelines

**Format:** Imperative mood, clear, concise (50 chars max for subject)

**Structure:**

```text
<type>: <subject>

<body (optional, wrap at 72 chars)>

<footer (optional, reference issues)>
```

**Subject:**

- Imperative: "Add", "Fix", "Improve", "Refactor" (not "Added", "Fixed")
- Max 50 characters
- No period at end
- Lowercase (except acronyms like API)

**Body (if needed):**

- Explain *what* and *why*, not *how*
- Wrap at 72 characters
- Blank line between subject and body

**Footer (if needed):**

- Reference related issues: `Fixes #123`, `Related to #456`
- Reference MPDP.md tasks: `Task: architecture.md creation`

**Examples:**

```bash
# Good ✅
git commit -m "Add Doji pattern detection to token matching"
git commit -m "Fix dashboard lag on datasets >5K candles

Use chunked processing for better performance on large
datasets. Reduces initial scan latency from 5s to 500ms."

git commit -m "Refactor vectorized_symbol_sequence for clarity

This refactoring improves readability without changing
performance characteristics.

Fixes #234"

# Bad ❌
git commit -m "WIP"
git commit -m "Fixed stuff"
git commit -m "update code"  # Too vague
git commit -m "Added support for new patterns"  # Not imperative
```

---

## Code Style & Standards

### Python Conventions

**Follow PEP 8** with these tools enforcing standards:

#### Black (Code Formatting)

```bash
# Format your code before committing
black src/ tests/

# Check without modifying
black --check src/ tests/
```

**Enforced rules:**

- Line length: 88 characters
- Indentation: 4 spaces
- String quotes: double quotes (unless contains double quotes)

#### Ruff (Linting)

```bash
# Check for linting issues
ruff check src/ tests/

# Auto-fix simple issues
ruff check --fix src/ tests/
```

**Rules enforced:**

- Import sorting (isort)
- Unused imports
- Undefined names
- Complexity issues

#### Type Hints (Future)

*Not currently enforced* but encouraged.

```python
def find_sequence_occurrences(
    df: pd.DataFrame,
    sequence: str,
    start_idx: int = 0
) -> list[int]:
    """Find matches in OHLCV data."""
    # implementation
    return matches
```

### Docstring Style

**Format:** Google-style docstrings

```python
def sequence_outcome_stats(df, matches, hold_period=5):
    """
    Calculate win rate and returns for a sequence.
    
    Analyzes the outcome of pattern matches by tracking
    price movement over a configurable hold period.
    
    Args:
        df: pandas DataFrame with OHLC columns
        matches: list of int, match indices
        hold_period: int, candle count to hold (default 5)
    
    Returns:
        dict with keys:
            - win_rate: float, portion of wins
            - avg_return: float, average return %
            - max_gain: float, best return %
            - max_loss: float, worst return %
    
    Raises:
        ValueError: if matches is empty or invalid
        KeyError: if df missing required OHLC columns
    
    Example:
        >>> df = pd.DataFrame({'open': [...], 'close': [...]})
        >>> matches = [10, 20, 35]
        >>> stats = sequence_outcome_stats(df, matches)
        >>> print(f"Win rate: {stats['win_rate']:.2%}")
        Win rate: 66.67%
    """
    # implementation
    return stats
```

### Naming Conventions

**Functions & Variables:**

```python
# Good ✅
find_sequence_occurrences()
vectorized_symbol_sequence()
calculate_win_rate()
alert_rule_dict

# Bad ❌
FindSequenceOccurrences()  # Use lower_snake_case
find_seq_occ()  # Don't abbreviate
findSequenceMatches()  # Use snake_case, not camelCase
my_var  # Be descriptive
```

**Classes:**

```python
class SequencePredictor:  # CamelCase for classes
    pass

class BacktestEngine:
    pass
```

**Constants:**

```python
MAX_CANDLES = 10000  # UPPER_SNAKE_CASE for constants
DEFAULT_HOLD_PERIOD = 5
CACHE_TTL_SECONDS = 300
```

---

## Testing Requirements

### Test Coverage

**Minimum requirements:**

- All new functions must have tests
- All bug fixes must include regression tests
- Target 80%+ coverage on core modules (patterns, dashboard, ml_sequence)

### Writing Tests

**Location:** `tests/test_*.py`

**Format:** pytest with fixtures

```python
import pytest
from candle_patterns.patterns import find_sequence_occurrences

# Use fixtures for common data
@pytest.fixture
def sample_data():
    """Provide sample OHLCV data."""
    import pandas as pd
    return pd.DataFrame({
        'open': [100, 101, 102, 101, 100],
        'close': [101, 102, 101, 100, 99],
        'high': [102, 103, 103, 102, 101],
        'low': [99, 100, 100, 99, 98],
        'volume': [1000, 1000, 1000, 1000, 1000],
    })

def test_find_sequence_occurrences(sample_data):
    """Test sequence matching works for simple pattern."""
    matches = find_sequence_occurrences(sample_data, "2R -> 1G")
    assert len(matches) == 1
    assert matches[0] == 1  # Adjust based on actual data

def test_find_sequence_empty():
    """Test graceful handling of empty data."""
    import pandas as pd
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        find_sequence_occurrences(df, "3R -> 2G")
```

### Running Tests

```bash
# Run all tests
pytest tests/ -q

# Run specific test file
pytest tests/test_sequence_patterns.py -v

# Run with coverage
pytest tests/ --cov=src/candle_patterns

# Run only fast tests (skip network/E2E)
pytest tests/ -m "not network" -q
```

### Performance Testing

For performance-critical code (vectorized scanning, large datasets):

```python
def test_vectorized_scan_performance(benchmark):
    """Benchmark vectorized scanning vs row-by-row."""
    from candle_patterns.performance import vectorized_find_sequence
    import pandas as pd
    
    df = pd.DataFrame({'symbol_seq': ['R'] * 1000})
    
    # benchmark() will run the function and time it
    result = benchmark(vectorized_find_sequence, df, 'RRR')
    
    # Assert result is correct
    assert len(result) > 0
```

---

## Documentation Requirements

### When to Update Docs

- **New feature:** Add to README.md features list + MPDP.md roadmap
- **New pattern:** Add to PATTERN_CATALOG.md
- **Architecture change:** Update docs/architecture.md + UML diagrams
- **New API endpoint:** Document in README.md API section
- **Breaking change:** Update CHANGELOG.md (or GitHub Releases)

### What to Document

**README.md:**

- Feature summaries (bullet list)
- Quickstart for new users
- Links to detailed docs

**Docstrings (in code):**

- Function purpose
- Parameters with types
- Return value
- Exceptions raised
- Usage example

**docs/architecture.md:**

- Module responsibilities
- Data flows
- Component interactions

**MPDP.md:**

- Phase completion status
- Feature inventory
- Known issues

---

## Pull Request Process

1. **Create PR from feature branch** → base branch `feature/mvp-setup`
2. **Fill out PR template** (all sections required)
3. **Ensure all checks pass** (tests, linting, type checks)
4. **Request reviewers** (at least 1 required)
5. **Address review feedback** (push to same branch)
6. **Merge when approved** (squash or rebase, depending on preference)

### PR Template

See `.github/pull_request_template.md`

**Checklist items (all must pass):**

- ✅ Tests pass locally (`pytest -q`)
- ✅ Code formatted (`black src/`)
- ✅ Linting passes (`ruff check src/`)
- ✅ New tests added (if feature)
- ✅ Docstrings added (if new functions)
- ✅ Documentation updated (if needed)
- ✅ Linked to MPDP.md task or issue
- ✅ No breaking changes (or documented)

---

## Pre-commit Hooks

**Optional but strongly recommended** for local development:

```bash
# Install
pip install pre-commit
pre-commit install

# Checks run automatically before each commit:
# - Black (formatting)
# - Ruff (linting)
# - YAML/JSON validation
# - Large file detection
# - Trailing whitespace

# Test manually (all files)
pre-commit run --all-files

# Skip hooks if truly necessary (not recommended)
git commit --no-verify
```

---

## Code Review Expectations

### As an Author

- **Respond to all comments** (even if just "acknowledged")
- **Request re-review after changes** (don't assume automatic)
- **Keep commits clean** (use `git rebase -i` or squash merge)
- **Be open to feedback** (code review improves code quality + team standards)

### As a Reviewer

- **Be respectful and constructive**
- **Focus on code, not person** ("This function could..." not "You didn't...")
- **Explain *why* if not obvious** (education is part of review)
- **Approve when satisfied** (don't block on minor style issues if linting passes)
- **Verify tests added** (feature without tests = incomplete)

---

## Common Contribution Patterns

### Adding a New Pattern Detector

**Files to modify:**

1. `src/candle_patterns/patterns.py` — Add detector function
2. `src/candle_patterns/patterns.py` — Register in `match_named_token()`
3. `tests/test_sequence_patterns.py` — Add test cases
4. `README.md` — Add to pattern syntax documentation
5. `PATTERN_CATALOG.md` — Add detailed description

**Example PR checklist:**

- [ ] Detector function works on sample data
- [ ] 3+ test cases covering normal/edge cases
- [ ] Docstring with parameter types + example
- [ ] Pattern syntax documented
- [ ] Added to README feature list
- [ ] Tests pass + coverage maintained

### Adding a New Dashboard Tab

**Files to modify:**

1. `src/candle_patterns/dashboard.py` — Add tab layout + callbacks
2. `tests/test_dashboard_smoke.py` — Add smoke test for new tab
3. `MPDP.md` — Note in features + roadmap
4. `README.md` — Add to dashboard tab table + features list

**Example PR checklist:**

- [ ] Tab layout clean + responsive
- [ ] Callbacks handle edge cases (empty data, errors)
- [ ] Working demo with sample data
- [ ] Test verifies tab loads without errors
- [ ] Linked to MPDP.md task in PR description

### Optimizing Performance

**Files to modify:**

1. `src/candle_patterns/performance.py` — Add/improve optimization function
2. `tests/test_*.py` — Add performance benchmark
3. `docs/architecture.md` — Update performance characteristics
4. `README.md` — Update feature description if user-visible

**Example PR checklist:**

- [ ] Benchmark shows improvement (X% faster)
- [ ] No accuracy/behavior regressions
- [ ] Memory usage not increased
- [ ] Works on large datasets (10K+ candles)
- [ ] Backward compatible (no API changes)

---

## Getting Help

**Questions about process?**

- Check AGENT_HANDOFF.md for detailed setup
- Review existing PRs for examples of good practices
- Open a GitHub Discussion or issue

**Stuck on a problem?**

- Comment in PR for help from maintainers
- Tag `@Zed-777` if urgent

**Reporting bugs?**

- Use GitHub Issues with reproduction steps
- Include Python version, OS, error message
- Link to related feature if applicable

---

## Code of Conduct

- **Be respectful** — We're all volunteers
- **Be inclusive** — Welcome all experience levels
- **Give credit** — Acknowledge ideas and help from others
- **Focus on ideas** — Judge code, not people

---

## Questions?

See [README.md](./README.md) or [CONTRIBUTING.md](./CONTRIBUTING.md) for more details.

**Questions about contribution process?** Open an issue or discussion on GitHub.

---

**Last Updated:** April 2, 2026  
**Version:** 1.0 (aligned with Phase 12 governance)  
**Next Review:** When major workflow changes or new contribution types added

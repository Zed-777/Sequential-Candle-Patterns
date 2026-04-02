# Code Documentation Compliance Audit

**Date:** April 2, 2026  
**Standard:** PROJECT_GUIDELINES.md — Code Documentation Standards  
**Overall Compliance:** 59% (needs improvement)

---

## Executive Summary

The codebase partially follows the new documentation standards. Well-documented modules exist (api.py, backtesting.py, ml_baseline.py), but critical core modules lack docstrings and type hints.

| Category | Target | Current | Status |
|----------|--------|---------|--------|
| Module-level docstrings | 100% | 71% (15/21) | ⚠️ 6 modules missing |
| Public function docstrings | 100% | ~60% | ⚠️ ~40+ functions missing |
| Public function type hints | 100% | ~65% | ⚠️ ~50+ functions incomplete |
| `# type: ignore` with issue refs | 100% | 0% (0/6) | ❌ 6 instances non-compliant |
| TODO/FIXME with issue refs | 100% | N/A | ✅ None found |

---

## 🔴 Critical Issues (Fix This Sprint)

### 1. Missing Module-Level Docstrings (6 modules)

| Module | Lines | Impact | Status |
|--------|-------|--------|--------|
| **patterns.py** | 600+ | CRITICAL — Core pattern matching engine | ❌ No docstring |
| **detection.py** | 250+ | CRITICAL — Candle detection functions | ❌ No docstring |
| **dashboard.py** | 4,400+ | CRITICAL — Largest file, ~25+ undocumented callbacks | ❌ No docstring |
| **cli.py** | 200+ | HIGH — User-facing commands | ❌ No docstring |
| **backtest.py** | 50+ | HIGH — Public API | ❌ No docstring |
| **ingestion.py** | 100+ | MEDIUM — Data loading | ❌ No docstring |

### 2. Type: Ignore Comments Without Issue References (6 instances)

**Required format (per guidelines):** `# type: ignore[reason] — MPDP/issue reference`

| File | Line | Current | Required |
|------|------|---------|----------|
| ml_sequence.py | 238 | `# type: ignore[assignment]` | Add issue reference |
| ml_sequence.py | 241 | `# type: ignore[assignment]` | Add issue reference |
| ml_sequence.py | 244 | `# type: ignore[assignment]` | Add issue reference |
| ml_sequence.py | 338 | `# type: ignore[union-attr]` | Add issue reference |
| dashboard.py | 304 | `# type: ignore[attr-defined]` | Add issue reference |
| dashboard.py | 2147 | `# type: ignore[union-attr]` | Add issue reference |

### 3. Critical Public Functions Missing Docstrings

**patterns.py (Core Module)**
- `matches_sequence_at()` [L263]
- `count_followup_pattern()` [L286]
- `find_followup_outcomes()` [L318]
- `find_sequence_occurrences()` [L340]

**detection.py (Detection Engine)**
- `candle_color()` [L14]
- `is_doji()` [L19]
- `is_hammer()` [L34]
- `detect_patterns()` [L149] — Complex public API

**dashboard.py (Callbacks—~25+ missing)**
- `scan_sequences()` [L2444]
- `update_chart()` [L2577]
- `show_pattern_detail()` [L3180]
- `on_upload()` [L2347]
- `on_yf_fetch()` [L3370]
- + 20 more

---

## 🟠 High Priority Issues (Fix by Next Release)

### Public Functions Missing Type Hints (40+ instances)

**patterns.py:**
- `matches_sequence_at()` — missing return type

**detection.py:**
- `candle_color()` — missing return type hint
- `is_doji()` — missing return type hint
- `is_hammer()` — missing return type hint

**dashboard.py (majority of callbacks):**
- `load_sample_data()` — no type hints
- `build_candle_figure()` — no type hints
- `build_default_scan_results()` — no type hints
- `scan_sequences()` — no type hints
- `update_chart()` — no type hints
- `on_upload()` — no type hints
- `on_yf_fetch()` — no type hints
- (+ ~25 more callbacks)

**ingestion.py:**
- `load_csv()` — partial type hints

---

## 🟡 Medium Priority Issues (Fix in Next Sprint)

1. **Dash Callback Pattern** — No consistent documentation for complex multi-input callbacks
2. **Complex Return Types** — Dashboard functions returning `html.Div`, `dcc.Graph`, etc. lack type hints
3. **Incomplete Parameter Docs** — Some functions document Args but not Returns section

---

## ✅ Well-Documented Modules (Reference)

| Module | Coverage | Notes |
|--------|----------|-------|
| **api.py** | 95% | ✅ Module docstring, typed endpoints, complete |
| **backtesting.py** | 100% | ✅ Class docstrings, all methods documented |
| **ml_baseline.py** | 100% | ✅ Module docstring, comprehensive docs |
| **alerts.py** | 95% | ✅ All public functions documented |
| **ml_sequence.py** | 90% | ⚠️ Good docs but 4× `type: ignore` without refs |
| **multi_timeframe.py** | 95% | ✅ NumPy-style docstrings, full type hints |

---

## Remediation Plan

### Phase 1: Critical Fixes (This Week)

**1A. Add module-level docstrings to 6 core modules**

```python
# patterns.py (top of file)
"""
Candlestick pattern recognition via sequence parsing and matching.

This module provides functions to:
- Parse user-defined candle color sequences (e.g., "3R -> 2G -> Doji")
- Find matches in OHLC data
- Analyze pattern outcomes and statistics
- Discover repeating color sequences automatically

Key functions:
- parse_sequence(): Parse a sequence string into tokens
- find_sequence_occurrences(): Find all matches in a DataFrame
- sequence_outcome_stats(): Calculate win rate and returns
"""
```

**1B. Fix 6 `# type: ignore` comments with issue references**

```python
# Format: # type: ignore[reason] — MPDP-phase-X or issue-ID
# Example:
self.model = cal  # type: ignore[assignment] — MPDP-phase-11-ml-type-compatibility
```

### Phase 2: High Priority (This Sprint)

**2A. Document critical functions in patterns.py, detection.py**
- Add Google-style docstrings with Args, Returns, Examples
- Add full type hints to all public APIs

**2B. Document top 10 callbacks in dashboard.py**
- Focus on complex multi-input callbacks
- Document Inputs/Outputs/State relationships

### Phase 3: Complete (Next Release)

**3A. Document all remaining callbacks**
**3B. Standardize Dash callback pattern documentation**

---

## Expected Impact

- **Developer Onboarding:** Reduce setup time (currently unclear callback flow)
- **Code Reviews:** Faster PR reviews with clear API contracts
- **Maintainability:** Breaking changes immediately visible
- **IDE Support:** Full autocomplete in VS Code with proper type hints

---

## Files Requiring Action

### Remove This Code
- [ ] dashboard.py [L304] — Fix `# type: ignore[attr-defined]`
- [ ] dashboard.py [L2147] — Fix `# type: ignore[union-attr]`
- [ ] ml_sequence.py [L238, L241, L244, L338] — Fix all `# type: ignore` comments

### Add Module Docstrings
- [ ] patterns.py [TOP]
- [ ] detection.py [TOP]
- [ ] dashboard.py [TOP]
- [ ] cli.py [TOP]
- [ ] backtest.py [TOP]
- [ ] ingestion.py [TOP]

### Document Critical Functions
- [ ] patterns.py: matches_sequence_at, count_followup_pattern, find_followup_outcomes, find_sequence_occurrences
- [ ] detection.py: candle_color, is_doji, is_hammer, detect_patterns
- [ ] dashboard.py: Top 10 callbacks (scan_sequences, update_chart, show_pattern_detail, on_upload, on_yf_fetch, etc.)

---

**Summary:** 59% → Target 100% by end of Phase 11 (v1.4.0 final release)


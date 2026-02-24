# Phase 2 Autonomy Plan - Pattern Expansion & ML Integration

**Status**: MVP Complete, All Systems Operational  
**Date**: February 22, 2026  
**Objective**: Expand from MVP (10 patterns) to 15+ patterns + ML-CLI integration  
**Estimated Duration**: 10-14 hours across next 3-4 days

---

## Phase 2 Roadmap

### Tier 1: Pattern Catalog Expansion (2-4 hours)

**Goal**: Add 5-8 new candlestick patterns to reach 15+  

Current patterns (10):

1. Bullish Engulfing
2. Bearish Engulfing  
3. Hammer
4. Inverted Hammer
5. Three White Soldiers
6. Three Black Crows
7. Morning Star
8. Evening Star
9. Doji
10. Long-Legged Doji

New patterns to implement:

- [ ] Hanging Man (bearish reversal)
- [ ] Shooting Star (bearish reversal)
- [ ] Piercing Line (bullish reversal)
- [ ] Dark Cloud Cover (bearish reversal)
- [ ] On Neck Line (bearish continuation)
- [ ] In Neck Line (bearish continuation)
- [ ] Breakaway (both bullish & bearish)
- [ ] Harami (bullish engulfing variant)

**Tasks**:

1. Add detector methods to `src/candle_patterns/detection.py`
2. Register in `src/candle_patterns/patterns.py`
3. Write unit tests for each new pattern
4. Update `PATTERN_CATALOG.md` with descriptions
5. Regenerate sample_synthetic.csv with new patterns
6. Verify dashboard shows all new patterns in checklist

**Success Criteria**:

- ✅ 15+ detectors implemented
- ✅ All tests passing (50+ tests total)
- ✅ Sample data includes new patterns
- ✅ Dashboard renders new patterns correctly

---

### Tier 2: ML-CLI Integration (1-2 hours)

**Goal**: Add ML training/prediction commands to analyzer CLI  

New commands:

- [ ] `analyzer train --input data.csv --output model.pkl`
  - Load data, train RandomForest with k-fold CV
  - Save model to disk
  - Display feature importance
  
- [ ] `analyzer predict --model model.pkl --input data.csv --output predictions.csv`
  - Load trained model
  - Generate pattern features
  - Output probability predictions per pattern
  
- [ ] `analyzer backtest --model model.pkl --input data.csv`
  - Run strategy backtest using model predictions
  - Display Sharpe, max drawdown, win rate
  - Generate equity curve chart

**Tasks**:

1. Add `train` subcommand to `src/candle_patterns/cli.py`
2. Add `predict` subcommand
3. Add `backtest` subcommand
4. Create unit tests for new CLI commands
5. Update README with ML training workflow
6. Test end-to-end: train model → predict → backtest

**Success Criteria**:

- ✅ 3 new CLI commands working
- ✅ All tests passing
- ✅ Can train model from CSV
- ✅ Can predict on new data
- ✅ Can backtest strategy

---

### Tier 3: E2E Test Enhancement (3-4 hours)

**Goal**: Complete Playwright test coverage, resolve async conflict  

Current status:

- 2 tests skipped (documented reason)
- 1 sync smoke test covers basic UI
- Need: Full multi-tab testing

**Tasks**:

1. Analyze pytest-asyncio event loop conflict (root cause)
2. Refactor E2E tests to use sync-only approach
3. Add tests for each dashboard tab:
   - [ ] Candlestick Chart tab
   - [ ] Individual Patterns tab
   - [ ] Aggregated Summary tab
   - [ ] OPP Patterns tab
4. Add filter tests:
   - [ ] Date range filtering
   - [ ] Pattern checklist filtering
   - [ ] Combined filters
5. Add interaction tests:
   - [ ] Load Sample Data button
   - [ ] Upload CSV file
   - [ ] Custom sequence search
   - [ ] History selection
6. Add performance benchmarks

**Success Criteria**:

- ✅ All E2E tests running (no skips)
- ✅ 10+ E2E scenarios covered
- ✅ Dashboard tabs all verified
- ✅ Interactions tested
- ✅ <50 second test execution time

---

### Tier 4: Optional - Security & Documentation (2-3 hours)

**Goal**: GDPR compliance, security hardening, Docker registry  

**Tasks**:

1. Write GDPR/Privacy documentation
2. Add Docker image push to GitHub Container Registry (GHCR)
3. Create comprehensive API documentation
4. Add security guidelines to README
5. Generate architecture diagram (Mermaid)

**Success Criteria**:

- ✅ GDPR documentation written
- ✅ Docker image tagged and pushed
- ✅ API docs complete
- ✅ Security guidelines documented

---

## Execution Strategy

### Week 1: Pattern Expansion + Initial ML-CLI

**Monday** (4 hours):

- Add 4 new patterns (Hanging Man, Shooting Star, Piercing Line, Dark Cloud Cover)
- Write tests for new patterns
- Update sample data

**Tuesday** (3 hours):

- Add 4 more patterns (On Neck, In Neck, Breakaway, Harami)
- Complete pattern tests
- Update dashboard

**Wednesday** (2 hours):

- Add train command to CLI
- Add predict command to CLI
- Test train + predict workflow

**Thursday** (2 hours):

- Add backtest command to CLI
- End-to-end testing: train → predict → backtest
- Update README with examples

### Week 2: E2E Testing + Polish

**Friday** (3 hours):

- Analyze and fix async test conflict
- Implement sync-only Playwright tests
- Test all dashboard tabs

**Monday** (2 hours):

- Add filter tests
- Add interaction tests
- Performance optimization

**Tuesday** (2 hours):

- Optional: GDPR docs
- Optional: Docker push to GHCR
- Final polish and review

---

## Dependencies & Prerequisites

### Required Packages (Already Installed)

- scikit-learn (RandomForest)
- Dash/Plotly (dashboard)
- Pandas (data processing)
- pytest/Playwright (testing)
- Docker (containerization)

### Required Knowledge

- Candlestick pattern recognition (rules)
- RandomForest feature engineering
- Playwright test automation
- Docker image publishing

### Risk Mitigation

- All tests already passing (low risk for regressions)
- Pattern detection logic isolated (low risk)
- CLI commands follow existing patterns (low risk)
- Test coverage enforced (prevents issues)

---

## Success Criteria for Phase 2

| Milestone | Criteria | Status |
|-----------|----------|--------|
| Pattern Expansion | 15+ detectors, tests passing | 🔄 TODO |
| ML-CLI Integration | train/predict/backtest commands working | 🔄 TODO |
| E2E Testing | 10+ scenarios, all tests passing | 🔄 TODO |
| Documentation | GDPR, API, architecture docs | 🔄 TODO |
| Docker Registry | Image published to GHCR | 🔄 TODO |

---

## Handoff Checklist

### System State (Feb 22, 2026 - 09:56 UTC)

- ✅ All tests passing (38 executed, 2 skipped)
- ✅ Dashboard operational (callback fix deployed)
- ✅ Sample data loaded (200 candles, 544 patterns)
- ✅ Module imports clean
- ✅ Git history clean (16 commits staged for push)
- ✅ Code repository synchronized

### Ready to Begin Phase 2?

- ✅ MVP features complete
- ✅ Test coverage adequate (80%+)
- ✅ CI/CD pipeline functional
- ✅ Documentation up-to-date
- ✅ No blocking issues

**Status**: ✅ **READY FOR PHASE 2 AUTONOMY**

---

## Autonomous Work Commands

When resuming Phase 2 work:

```bash
# 1. Verify current state
cd "C:\Users\zmgdi\OneDrive\Desktop\CANDLE PATTERNS"
.\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short

# 2. Start pattern expansion
# Edit: src/candle_patterns/detection.py (add detector methods)
# Edit: src/candle_patterns/patterns.py (register patterns)
# Create: tests/test_new_patterns.py (unit tests)

# 3. Run tests to verify
.\.venv\Scripts\python.exe -m pytest tests/test_new_patterns.py -v

# 4. Add CLI commands
# Edit: src/candle_patterns/cli.py (add train/predict/backtest)
# Create: tests/test_ml_cli.py (unit tests)

# 5. Final verification
.\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
```

---

**Autonomous Session Ready**: Yes  
**Critical Dependencies**: None blocking  
**Recommended Start**: Pattern expansion (Tier 1)  
**Estimated Completion**: February 26, 2026

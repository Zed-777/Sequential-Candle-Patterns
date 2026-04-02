# Pull Request Template

**Before submitting, please ensure:**

- [ ] PR linked to a GitHub issue or MPDP.md task
- [ ] Title clearly describes the change
- [ ] All checklist items below completed

---

## PR Title

Keep it concise (50 chars max):

- `Add support for DeFi token patterns`
- `Fix dashboard lag on 5K+ candles`
- `Optimize vectorized_symbol_sequence`

---

## Description

**What does this PR do?**

(2-3 sentences explaining the change and why it matters)

**Related Issue/Task:**

Closes #123 or Task: [MPDP.md section and task name]

---

## Type of Change

- [ ] 🎨 Feature (new pattern, new tab, new API endpoint)
- [ ] 🐛 Bug fix (regression, crash, incorrect behavior)
- [ ] ⚡ Performance improvement (optimization, caching)
- [ ] 📚 Documentation (README, docstrings, guides)
- [ ] ♻️ Refactoring (code cleanup, no behavior change)
- [ ] 🧪 Test improvement (new tests, better coverage)

---

## Implementation Checklist

**Code Quality:**

- [ ] Code follows PEP 8 and project conventions
- [ ] `black src/` passes (code formatting)
- [ ] `ruff check src/` passes (linting)
- [ ] New functions have docstrings (Google style)
- [ ] Type hints added (if using Python 3.10+)

**Testing:**

- [ ] All tests pass: `pytest tests/ -q`
- [ ] New tests added for new functionality (or bug fix)
- [ ] Test coverage maintained or improved (80%+ on core modules)
- [ ] E2E tests pass (if UI changes): `pytest tests/e2e/ -v`

**Documentation:**

- [ ] Docstrings added/updated for new/modified functions
- [ ] README.md updated (if user-facing feature)
- [ ] MPDP.md updated (if roadmap-related)
- [ ] CHANGELOG.md updated (if public API change) [optional for patch]

**Breaking Changes:**

- [ ] No breaking API changes (or clearly documented)
- [ ] Backward compatible with existing workflows
- [ ] Migration path documented (if applicable)

---

## Testing Evidence

**Local test results:**

```text
pytest tests/ -q

# Paste output below:
[output of: pytest tests/ -q]
```

**Any manual testing performed?**

(e.g., "Tested with AAPL data, 1000 candles, 50 patterns. Dashboard renders in 300ms.")

---

## Risk Assessment

**What could go wrong?**

- [ ] Low risk (docs, tests, refactoring)
- [ ] Medium risk (new feature, isolated change)
- [ ] High risk (core logic change, performance impact)

**Mitigation:**
(If high/medium risk, explain how you've tested edge cases)

---

## Reviewer Checklist

*For reviewers:*

- [ ] Code is easy to understand
- [ ] Tests cover happy path + edge cases
- [ ] No unrelated changes included
- [ ] Performance not regressed (check benchmark if applicable)
- [ ] Docstrings are clear  
- [ ] No hardcoded values or secrets
- [ ] Follows project conventions (naming, style)
- [ ] Ready to merge ✅

---

## Additional Notes

(Optional: Any caveats, future work, or context for reviewers?)

---

**PR ready for review?**  
When all checklist items are complete, request a reviewer: `@Zed-777 please review`

---

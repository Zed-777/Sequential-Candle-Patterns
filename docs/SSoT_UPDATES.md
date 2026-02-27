# Recent Automated Updates (Summary)

- Expanded rule-based detectors: Spinning Top, Shooting Star, Hanging Man, Piercing Line, Morning Star, Evening Star (heuristic implementations + unit tests).
- Added OPP miner variable-length top-K summarization, demo script (`demos/opp_demo.py`), and unit tests.
- Dashboard: added aggregated pattern summary and Top OPP table widgets.
- CI: added coverage collection and changed to enforce coverage minimum in CI (`--cov-fail-under=80`); removed Codecov upload (no external token required).
- Tracker updated (`progress_tracker.csv`) to reflect these changes.

Notes:

- The expanded detectors use conservative heuristics for synthetic validation; parameters will be refined with more data and calibration.
- Branch `feature/mvp-next-clean` contains the clean PR candidate with these changes.

Actions done automatically: ran unit tests locally and fixed failing cases; updated tracker and PATTERN_CATALOG.  

- Added a lightweight `Dockerfile` and an integration test (`tests/integration/test_end_to_end.py`) with sample data (`tests/data/synthetic.csv`).  
- Adopted non-destructive repo-cleanup strategy: create PR from `feature/mvp-next-clean` and retain backup branch `backup/feature-mvp-next-bloat` until the PR is merged and validated.  
- CI: added integration test and collects coverage; CI now enforces a minimum coverage threshold (`--cov-fail-under=80`) and the Codecov upload step was removed per project preference (no external token required).  

Completed & validated (automated):

- Local dev standardization completed: `scripts/setup_venv.*` added and dev deps installed into `.venv`; tests pass in standardized environment.  ✅
- Integration tests added and passing.  ✅
- Packaging & Docker: `Dockerfile` added; CI validates Docker image build (see CI Docker build step).  ✅

Next Actions:

- No action required: Codecov uploads were intentionally removed; CI enforces coverage locally (`--cov-fail-under=80`).
- Open PR from `feature/mvp-next-clean` and request review; merge after validation.  ✅

Recent automated updates (summary)

- Expanded rule-based detectors: Spinning Top, Shooting Star, Hanging Man, Piercing Line, Morning Star, Evening Star (heuristic implementations + unit tests).
- Added OPP miner variable-length top-K summarization, demo script (`demos/opp_demo.py`), and unit tests.
- Dashboard: added aggregated pattern summary and Top OPP table widgets.
- CI: added coverage collection and upload to Codecov (CI step updated in `.github/workflows/ci.yml`).
- Tracker updated (`progress_tracker.csv`) to reflect these changes.

Notes:
- The expanded detectors use conservative heuristics for synthetic validation; parameters will be refined with more data and calibration.
- Branch `feature/mvp-next-clean` contains the clean PR candidate with these changes.

Actions done automatically: ran unit tests locally and fixed failing cases; updated tracker and PATTERN_CATALOG.

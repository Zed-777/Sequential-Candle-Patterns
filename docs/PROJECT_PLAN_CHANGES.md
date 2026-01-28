Project Plan - Recent Changes

This short note records a small but important update that modifies the CI and coverage policy referenced in `PROJECT_PLAN.md`.

- Change: The project opted *not* to upload coverage to Codecov. The CI workflow was updated to collect coverage and **enforce a minimum coverage threshold** using pytest-cov (`--cov-fail-under=80`). This avoids relying on an external coverage service or repository secret.

Where updated:

- `progress_tracker.csv` (rows: #5, #12, #19, #20 updated to reflect the decision)
- `README.md` (removed Codecov note and clarified coverage enforcement)
- `docs/SSoT_UPDATES.md` (automated updates now state Codecov upload removed and coverage enforcement added)
- `docs/COMPLETION.md` (removed instruction to add `CODECOV_TOKEN` and clarified that no action is required)

Notes:

- If you later decide to re-enable Codecov, add `CODECOV_TOKEN` to repository secrets and I can re-enable the upload step and the badge.

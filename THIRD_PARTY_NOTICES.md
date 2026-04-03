# Third-Party Notices

This project uses open-source software and libraries. This document provides attribution and licensing information for all third-party dependencies.

---

## Python Dependencies

### Core Data Processing

#### pandas

- **License:** BSD 3-Clause
- **Repository:** <https://github.com/pandas-dev/pandas>
- **Purpose:** DataFrames, time series data manipulation
- **Copyright:** Pandas Development Team

#### numpy

- **License:** BSD
- **Repository:** <https://github.com/numpy/numpy>
- **Purpose:** Vectorized numerical computing, array operations
- **Copyright:** NumPy Developers

### Web Framework & Visualization

#### Dash

- **License:** MIT
- **Repository:** <https://github.com/plotly/dash>
- **Purpose:** Interactive web dashboard framework
- **Copyright:** Plotly Technologies Inc.

#### Plotly

- **License:** MIT
- **Repository:** <https://github.com/plotly/plotly.py>
- **Purpose:** Interactive charts and visualizations
- **Copyright:** Plotly Technologies Inc.

#### Flask

- **License:** BSD 3-Clause
- **Repository:** <https://github.com/pallets/flask>
- **Purpose:** Web framework (dependency of Dash)
- **Copyright:** Armin Ronacher and Contributors

### Machine Learning & Statistics

#### scikit-learn

- **License:** BSD 3-Clause
- **Repository:** <https://github.com/scikit-learn/scikit-learn>
- **Purpose:** GradientBoosting, RandomForest ML models; statistical functions
- **Copyright:** scikit-learn Developers

### Data Sources

#### yfinance

- **License:** Apache 2.0
- **Repository:** <https://github.com/ranaroussi/yfinance>
- **Purpose:** Yahoo Finance data fetching (stocks, crypto, indices, forex)
- **Copyright:** Ran Aroussi

### Testing & Quality Assurance

#### pytest

- **License:** MIT
- **Repository:** <https://github.com/pytest-dev/pytest>
- **Purpose:** Unit testing framework
- **Copyright:** pytest Development Team

#### pytest-cov

- **License:** MIT
- **Repository:** <https://github.com/pytest-dev/pytest-cov>
- **Purpose:** Code coverage measurement
- **Copyright:** pytest-cov Contributors

#### Playwright

- **License:** Apache 2.0
- **Repository:** <https://github.com/microsoft/playwright-python>
- **Purpose:** E2E browser automation testing
- **Copyright:** Microsoft Corporation

#### black

- **License:** MIT
- **Repository:** <https://github.com/psf/black>
- **Purpose:** Python code formatter
- **Copyright:** Łukasz Langa and Contributors

#### ruff

- **License:** MIT
- **Repository:** <https://github.com/astral-sh/ruff>
- **Purpose:** Python linter and import sorter
- **Copyright:** Astral

#### bandit

- **License:** Apache 2.0
- **Repository:** <https://github.com/PyCQA/bandit>
- **Purpose:** Security vulnerability scanner
- **Copyright:** OpenStack Foundation

#### pre-commit

- **License:** MIT
- **Repository:** <https://github.com/pre-commit/pre-commit>
- **Purpose:** Git pre-commit hook framework
- **Copyright:** pre-commit Contributors

### Containerization

#### Docker

- **License:** Multiple (Apache 2.0, MIT, others)
- **Repository:** <https://github.com/moby/moby>
- **Purpose:** Container runtime and image building
- **Copyright:** Docker Inc. and Contributors

---

## Development Tools

### GitHub Actions

- **License:** Proprietary (GitHub)
- **Purpose:** CI/CD pipeline automation
- **Copyright:** GitHub Inc.

### Python (Language)

- **License:** Python Software Foundation License
- **Repository:** <https://github.com/python/cpython>
- **Purpose:** Programming language runtime
- **Copyright:** Python Software Foundation

---

## Font & Icon Resources

### Open Source Fonts

- **Fonts used:** System defaults (no external fonts included)
- **Icons:** Emoji/Unicode (no license required)

---

## Compliance Notes

### License Compatibility

This project uses a mix of permissive licenses:

- **MIT** — Permissive, allows commercial use
- **BSD 3-Clause** — Permissive, requires attribution
- **Apache 2.0** — Permissive, includes patent protection

All dependencies are compatible with MIT licensing (the license used by this project).

### Dependency Management

- **All dependencies listed in:** `pyproject.toml` and `requirements.txt`
- **Locked versions in:** `requirements-frozen.txt`
- **Update policy:** Regular updates via GitHub security alerts

### No GPL or Copyleft

This project does NOT include any GPL, AGPL, or other copyleft-licensed code. All dependencies use permissive licenses only.

---

## How to View Full Licenses

To view the full license text for each dependency:

```bash
# List all installed packages
pip list

# Print license of a specific package
pip show <package-name> | grep License

# View license file in installed package
cat $(python -c "import site; print(site.getsitepackages()[0])")/<package-name>-*/LICENSE
```

---

## Contributing

When adding new dependencies:

1. Verify the license is permissive (MIT, BSD, Apache 2.0, etc.)
2. Add entry to this file with copyright holder
3. Document the dependency in `pyproject.toml`
4. Update `requirements.txt` and `requirements-frozen.txt`

---

## Questions or Corrections

If you find any missing or incorrect attribution:

- Open a GitHub issue: <https://github.com/Zed-777/Sequential-Candle-Patterns/issues>
- Contact: Zed-777

---

**Last Updated:** April 2, 2026  
**Completeness:** All dependencies included as of v1.4.0

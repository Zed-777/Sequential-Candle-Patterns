# Maintainers

This document describes the active maintainers of the Candlestick Patterns project, their responsibilities, and how to contact them.

---

## Active Maintainers

### Zed-777 (Project Lead & Primary Maintainer)

**GitHub:** [@Zed-777](https://github.com/Zed-777)  
**Contact:** GitHub issues or discussions (preferred)

#### Responsibilities

- **Architecture & Design** — Overall system design, major refactoring, technical direction
- **Core Features** — Pattern matching engine, dashboard, ML predictor, alerts
- **Releases** — Version planning, release coordination, changelog maintenance
- **Code Review** — PR review and approval (primary reviewer)
- **Issue Triage** — Bug classification, feature prioritization
- **Documentation** — README, MPDP, architecture, governance documents
- **CI/CD** — GitHub Actions workflow maintenance, build configuration
- **Security** — Vulnerability assessment, security policy enforcement

#### Response Time

- **Critical bugs** (blocking use) — Best-effort within 48 hours
- **Regular issues** — Best-effort within 1 week
- **Features** — Evaluated in product planning, discussed in issues

#### Support Hours

- **Communication:** Asynchronous (GitHub-based, no guaranteed immediate response)
- **Timezone:** UTC (flexible availability)
- **Availability:** Best-effort based on other commitments

---

## Decision-Making Process

### Feature Requests

1. **Proposal** — Open GitHub Discussion or Issue with clear description
2. **Discussion** — Community feedback and use case evaluation
3. **Decision** — Maintainer evaluates fit with project vision
4. **Implementation** — Feature added in current/next Phase if approved
5. **Documentation** — Features documented in README and MPDP.md

### Bug Reports

1. **Report** — GitHub Issue with reproduction steps
2. **Triage** — Severity assessment (critical, major, minor)
3. **Investigation** — Reproduce and identify root cause
4. **Fix** — Implement solution with tests
5. **Release** — Patch release (v1.4.X) or next minor version

### Breaking Changes

1. **Planning** — Discussed in MPDP.md major version section
2. **Notice** — Announced in issues and releases
3. **Migration Path** — Documented with examples
4. **Timeline** — Minimum 1 major version notice before removal

### Releases

- **Semantic Versioning** — Major.Minor.Patch (e.g., v1.4.0)
- **Major (X.0.0)** — Breaking API changes, major refactors (~annually)
- **Minor (1.X.0)** — New features, enhancements (per Phase completion)
- **Patch (1.4.X)** — Bug fixes, security patches (as needed)
- **Schedule** — On-demand (not time-based); prioritizes Phase milestones

### Code Review Standards

All pull requests require:

- ✅ Code passes linting (Black, Ruff, Bandit)
- ✅ Tests pass locally and in CI (315+ tests)
- ✅ New tests added for new features
- ✅ Documentation updated (docstrings, README if user-facing)
- ✅ 1 maintainer approval (currently Zed-777)

---

## Escalation Path

If you need urgent attention:

1. **Critical Security Issue** → See [SECURITY.md](SECURITY.md)
2. **Blocking Bug** → Label issue `urgent` with reproduction steps
3. **Project Direction** → Open discussion in GitHub Discussions
4. **Maintainer Concern** → Private message [@Zed-777](https://github.com/Zed-777)

---

## Governance & Roadmap

### Project Vision

- Build the best sequential pattern analysis tool for candlestick traders
- Maintain high code quality (tests, documentation, linting)
- Keep the project approachable for contributors
- Remain focused (no scope creep; one tool, well-executed)

### Roadmap

See [MPDP.md](MPDP.md) for:

- Phase-by-phase milestones
- Current focus and next 3 actionable tasks
- Known risks and blockers
- Timeline and release dates

### Contribution Welcome

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Branch strategy (feature/, bugfix/, docs/)
- Commit message guidelines
- Code style (PEP 8, Black, Ruff)
- Testing expectations
- PR workflow

### License

All contributions must be compatible with the MIT license. By submitting a PR, you agree to license your contribution under MIT.

---

## Project Metrics & Health

### Code Quality

- **Test Coverage:** 315+ tests, 100% pass rate
- **Linting:** 0 errors (Black, Ruff, Bandit)
- **Documentation:** 6+ comprehensive guides
- **Type Safety:** 100% on new code

### Release Cadence

- **Versions:** v1.0 (Dec 2025) → v1.4 (Apr 2026) = ~1.0 per month
- **Phases:** 11 Phases complete (MVP → Production Ready)
- **Next:** Phase 12 (Governance) → Phase 13 (Post-Launch)

### Community

- **Contributors:** Currently 1 (Zed-777)
- **Open Issues:** Tracked in GitHub Issues
- **Discussions:** GitHub Discussions for features

---

## Transition Plan

If Zed-777 becomes unavailable:

1. **Issue Communication** — GitHub issues pinned with status
2. **Temporary Freeze** — No merges until coverage established
3. **Community Fork** — Contributors may fork if project stalls >3 months
4. **Handoff** — Maintainer responsibility transferred if agreed upon

Hopefully this is far in the future! 🚀

---

## Getting Help

- **Questions about project** → GitHub Discussions
- **Bug reports** → GitHub Issues with `bug` label
- **Feature requests** → GitHub Issues with `feature` label
- **Security concerns** → See [SECURITY.md](SECURITY.md)
- **Contributing questions** → See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Last Updated:** April 2, 2026  
**Status:** Actively Maintained  
**Next Review:** After Phase 12 completion or team expansion

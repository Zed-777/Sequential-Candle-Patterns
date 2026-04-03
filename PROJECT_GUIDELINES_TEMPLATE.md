# PROJECT_GUIDELINES.md

This document defines the required files, structure, rules, and checks every repository must include to be professional, reproducible, secure, and recruiter-ready.

---

## Required top-level files and minimum contents

Each file below must exist at the repository root and include the listed elements.

### • README.md

- Title and one-line pitch.
- Badges: build, coverage, license.
- Short description (2–4 sentences) describing scope and audience.
- Quickstart: Docker quickstart and local quickstart with exact commands and minimal prerequisites.
- Usage examples: one minimal command and one realistic workflow.
- Architecture overview: short paragraph, folder map, link to UML diagrams.
- MPDP summary: one-line link to MPDP.md and current milestone.
- Testing and quality: how to run tests, linters, and pre-commit hooks; CI badge and commands.
- Security: link to SECURITY.md and a short note about secrets handling.
- Contributing: link to CONTRIBUTING.md and a short summary of branch strategy and PR expectations.
- Changelog and releases: semantic versioning policy and link to CHANGELOG.md or Releases.
- License and contact: license name and maintainer contact.
- Claims rule: any performance or accuracy claim must state dataset, evaluation method, and baseline or be labeled as an internal experiment.

### • MPDP.md (Master Progress and Development Plan) — The living roadmap and canonical status document

- One-line project summary.
- Current milestone with status and dates.
- Milestone list with statuses and dates.
- Current sprint or focus.
- Next three actionable tasks with owners and acceptance criteria.
- Known risks and mitigations.
- Links to related issues and PRs.
- Update cadence: update at least once per milestone or sprint.

### • .gitignore

- Language- and environment-appropriate rules.
- Exclude venvs, compiled artifacts, IDE files, OS files, caches, large data, and secrets.
- If data is excluded, reference data/README.md.

### • LICENSE

- Full license text file.
- Reference license badge in README.md.

### • Dependency manifest and lock file

- Reproducible dependency declarations (e.g., requirements.txt + requirements-dev.txt or pyproject.toml + lock file).
- Pin or lock dependencies.
- Document exact command to recreate the environment.

### • Dockerfile and .dockerignore

- Dockerfile builds from repo root and produces a lean image.
- .dockerignore excludes local artifacts, venvs, and data.
- Docker quickstart documented in README.md.

### • SECURITY.md

- Contact for vulnerability reports and expected response time.
- Dependency update policy and whether automated scanning is enabled.
- Short threat model and mitigations.
- Secret handling and rotation instructions.

### • VULNERABILITY_ASSESSMENT.md

- Comprehensive security audit results before public release.
- Risk assessment: critical, high, medium, and low-risk findings (with none of critical/high required for release).
- Threat model coverage against common attacks (SQL injection, code execution, credential theft, etc.).
- Dependency vulnerability assessment (libraries, version requirements, known CVEs).
- Network security analysis (inbound/outbound connections, protocols, exposure).
- Data handling and privacy compliance review (PII, retention, deletion).
- Recommended security enhancements (prioritized by importance, blocking vs. optional).
- Public release decision: **APPROVED** or **BLOCKED** with justification.

### • AGENT_HANDOFF.md

- .env.example and instructions to populate environment variables.
- Secrets handling guidance and recommended secret stores.
- Devcontainer usage if present.
- Common development and test commands.
- Where to find datasets and how to obtain/regenerate them.
- How to retrain models and run evaluation.
- Troubleshooting tips and common failure modes.
- Goal: enable a new contributor to run the project in under 30 minutes.

### • UML/ and UML/README.md

- At least one component diagram and one sequence diagram (vector preferred).
- UML/README.md maps diagrams to code and runtime responsibilities.
- Diagrams updated when architecture changes.

### • architecture.md

- Textual system architecture: components, responsibilities, data flows, startup sequence, request lifecycle, background jobs, failure modes, and scaling considerations.
- Map architecture elements to folders and runtime responsibilities.

### • Standard directories and files

- **tests/** — unit, integration, and smoke tests; use fixtures and small sample datasets for CI.
- **docs/** — comprehensive documentation and guides.
- **scripts/** — idempotent, documented scripts with --help.
- **data/** — data/README.md explains expected files, formats, and retrieval or regeneration steps.
- **deploy/** — staging and production artifacts with clear instructions.
- **.github/workflows/** — CI templates covering tests, linting, type checks, and release automation.
- **CODE_OF_CONDUCT.md** — community conduct guidelines.
- **CONTRIBUTING.md** — contributor workflow and expectations.
- **CHANGELOG.md** — semantic versioning policy and release history.
- **CODEOWNERS** — file ownership and required reviewers.
- **THIRD_PARTY_NOTICES.md** — attribution for third-party libraries.
- **MAINTAINERS.md** — active maintainers and their responsibilities.
- **DATA_LICENSE.md / PRIVACY.md** — data-specific licensing and privacy policies (if applicable).
- **MODEL_CARD.md / DATA_CARD.md** — model or dataset documentation (if applicable).
- **Dependabot/Renovate config** — automated dependency updates.

---

## README structure (ordered, no repetition)

Follow this exact order to keep repositories predictable:

1. Title and one-line pitch
2. Badges for build, coverage, and license
3. Short description (2–4 sentences)
4. Quickstart: Docker and local quickstart with exact commands
5. Usage examples: minimal command and realistic workflow
6. Architecture overview: paragraph, folder map, link to UML
7. MPDP summary: link and current milestone
8. Testing and quality: how to run tests, linters, pre-commit hooks; CI badge
9. Security: link to SECURITY.md and secrets note
10. Contributing: link and branch/PR expectations
11. Changelog and releases: semantic versioning policy and link
12. License and maintainer contact
13. Claims rule reminder

---

## Version control, CI, and pre-publish checklist

### Branch strategy

- **Branch protection:** protect main (or stable); require PR reviews and green CI.
- **Branch naming:** feature/, hotfix/, optional develop for larger teams.
- **Commit messages:** imperative mood, concise subject, reference issue/MPDP IDs.

### Pull request workflow

- **PR checklist:** link to issue/MPDP task; include tests or justify omission; pass linters and type checks; update docs if behavior changed; at least one reviewer.

### CI pipeline

- **Scope:** run on PRs and main.
- **Steps:** dependency install, linting, type checking, tests, Docker build.
- **Fail fast:** critical errors must block merge.

### Code quality

- **Pre-commit hooks:** require formatting, import sorting, linter, and dependency safety scanner.
- **Coverage target:** aim for at least 80% on core modules; document exceptions in MPDP.md.
- **Test artifacts:** produce JUnit XML and coverage reports; store artifacts in CI for historical comparison.

### Code documentation

- **Module-level docstrings:** Each module should have a docstring describing its purpose, key classes/functions, and usage example.
- **Function/method docstrings:** Include parameter types, return types, and expected behavior; use language-standard format (Python: Google/NumPy style recommended).
- **Class docstrings:** Describe purpose, public interface, and initialization requirements.
- **Type hints:** Use full type annotations for public APIs (Python 3.7+); document complex types.
- **Inline comments:** Only for non-obvious logic; prefer readable code over comments.
- **Disable comments must explain why:** All "# TODO", "# FIXME", "# HACK" must reference an issue or MPDP task ID.

### Pre-publish checklist (must pass before public release)

- README quickstart works in under 10 minutes.
- MPDP.md lists next three tasks with owners and criteria.
- Tests pass locally and in CI.
- No secrets in repo; use .env.example for reference.
- Docker build succeeds.
- UML diagrams present (component and sequence).
- LICENSE file correct and badge in README.
- CHANGELOG.md or Releases documented.
- SECURITY.md present and complete.
- VULNERABILITY_ASSESSMENT.md completed and approved for public release.
- All required files listed in this document are present.

---

## Enforcement and automation

- **Location:** Place PROJECT_GUIDELINES.md at the repository root.
- **PR template:** Add a PR template (.github/pull_request_template.md) that references the pre-publish checklist and requires confirmation of checklist items before merging.
- **Automated checks:** Verify presence of required files, run tests, run linters, and build Docker images in CI.
- **Living documents:** Keep MPDP.md and README.md up to date; treat MPDP.md as canonical project status.

---

## Implementation Status (vX.Y.Z)

### Project Compliance

**Instructions:** Fill in this section as your project progresses. Track which required files are present and which standard directories have been created.

#### Tier 1: Critical Documentation

- [ ] README.md
- [ ] MPDP.md
- [ ] .gitignore
- [ ] LICENSE
- [ ] Dependency manifest and lock file
- [ ] Dockerfile and .dockerignore
- [ ] SECURITY.md
- [ ] VULNERABILITY_ASSESSMENT.md
- [ ] AGENT_HANDOFF.md
- [ ] UML/ and UML/README.md
- [ ] architecture.md
- [ ] .github/workflows/
- [ ] CONTRIBUTING.md

#### Tier 2: Governance & Community Files

- [ ] CODE_OF_CONDUCT.md
- [ ] CHANGELOG.md
- [ ] THIRD_PARTY_NOTICES.md
- [ ] MAINTAINERS.md
- [ ] CODEOWNERS

#### Standard Directories

- [ ] tests/
- [ ] docs/
- [ ] scripts/
- [ ] data/
- [ ] src/

**Total Compliance:** __/23 required files present

### Optional Files

- deploy/ — (explain applicability or defer)
- MODEL_CARD.md / DATA_CARD.md — (explain applicability or defer)
- PRIVACY.md / DATA_LICENSE.md — (explain applicability or defer)
- Dependabot/Renovate config — (explain applicability or defer)

---

## Quick editorial notes for maintainers

- **Clarity:** Use short, imperative sentences so checklist items can be validated by scripts.
- **Diagrams:** Prefer vector UML diagrams (SVG) and keep source files (e.g., PlantUML) in UML/.
- **Handoff:** Make AGENT_HANDOFF.md a runnable checklist: include exact commands, example .env values (no secrets), and a minimal troubleshooting section.
- **Precision:** Replace vague phrasing with explicit deliverables and measurable cadence (e.g., "update at least once per milestone or sprint").

---

**Last updated:** [YYYY-MM-DD]

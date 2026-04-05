# Security & Data Privacy Policy

**Last Updated**: March 3, 2026  
**Version**: 1.0.0

---

## Overview

Candle Patterns is a **local-first, single-user application** designed for personal use on a developer's workstation. It does not collect, transmit, or store personal data beyond what the user explicitly provides through the dashboard interface.

---

## Data Handling

### Data Sources

| Source | Type | Storage | Retention |
|---|---|---|---|
| CSV uploads | OHLCV market data | Processed in-memory | Session-only (not persisted) |
| Yahoo Finance | Public market data | In-memory LRU cache | 5-minute TTL, cleared on restart |
| Sample data | Synthetic OHLCV | Generated on demand | Session-only |

### Data Persistence

| Store | Location | Contents | Retention |
|---|---|---|---|
| SQLite database | `data/candle_patterns.db` | Upload history, detection results | 30-day auto-cleanup |
| Alerts database | `data/alerts.db` | Alert rules, alert history | Until manually cleared |
| Watchlist | `data/watchlist.json` | Saved sequence libraries | Until manually cleared |
| Preferences | `data/preferences.json` | UI settings, defaults, recents | Until manually reset |

### What Is NOT Stored

- **No personal information** (names, addresses, phone numbers, etc.)
- **No authentication tokens** or API keys (Yahoo Finance uses the public API)
- **No SMTP credentials on disk** — email configuration is held in process memory only
- **No telemetry or analytics** — the application does not phone home
- **No cookies or tracking** — the Dash UI runs locally without external tracking

---

## Authentication & Access Control

- The system is **single-user** and does not implement authentication
- The dashboard binds to `localhost:8050` by default — **not exposed to the network**
- No API keys or secrets are required for operation
- There are no user accounts, passwords, or session tokens

---

## Network Communication

### Outbound Connections

| Destination | Purpose | Protocol | When |
|---|---|---|---|
| Yahoo Finance API | Fetch public market data | HTTPS | On user request (sidebar fetch button or live refresh) |
| User-configured webhook URLs | Alert notifications | HTTPS (POST) | When alert rules trigger |
| User-configured SMTP server | Email alert notifications | SMTP/TLS | When alert rules with email trigger |

### Inbound Connections

- The Dash dashboard listens on `localhost:8050` (configurable)
- **No inbound connections from external sources** in default configuration

---

## Credential Management

### Webhook URLs

- Stored in SQLite (`data/alerts.db`) as part of alert rules
- User-provided; the system does not validate or sanitise URLs beyond basic format checks
- Recommendation: use HTTPS webhook endpoints

### SMTP Configuration

- Email SMTP settings (host, port, username, password) are configured via `configure_email()` at runtime
- **SMTP credentials are stored in process memory only** — they are never written to disk or database
- Credentials are lost on application restart and must be re-configured

### Yahoo Finance

- Uses the public `yfinance` API — **no API key required**
- No authentication tokens stored

---

## Security Measures

### Code Quality

- **Bandit** security scanner runs in CI — blocks MEDIUM/HIGH findings
- **Ruff** and **Black** enforce code quality standards
- All SQL queries use **parameterised statements** — no string interpolation in SQL
- `nosec` annotations are documented with rationale where Bandit false positives occur

### Input Validation

- CSV uploads are validated for OHLCV schema compliance before processing
- Sequence pattern syntax is parsed with strict regex validation
- Dashboard inputs are sanitised through Dash's built-in callback system

### Dependencies

- All dependencies are pinned in `requirements-frozen.txt`
- `requirements.txt` specifies minimum versions for compatibility
- No known vulnerabilities in current dependency set (as of v1.0.0)

---

## GDPR Considerations

### Applicability

This application is designed for **personal/research use** on a single workstation. In its default configuration:

- It does not process personal data of third parties
- It does not collect data from end users
- No data is transmitted to external services beyond Yahoo Finance (public market data) and user-configured webhook/email endpoints

### If Deployed in a Multi-User Context

If this application were adapted for multi-user deployment, the following GDPR considerations would apply:

1. **Data Processing Basis**: Market data analysis for research purposes (legitimate interest)
2. **Data Minimisation**: Only OHLCV market data is processed — no personal data fields
3. **Right to Erasure**: Users can clear all data via the CLI cleanup command or by deleting `data/` directory
4. **Data Portability**: Watchlist and preferences export to standard JSON format
5. **Breach Notification**: Not applicable in single-user mode — no personal data at risk

### Data Deletion

To fully remove all stored data:

```bash
# Remove all persistent data
rm -rf data/

# Or use the CLI cleanup command
python -m candle_patterns.cli cleanup
```

---

## Vulnerability Reporting

If you discover a security vulnerability, please report it by opening a GitHub issue at:  
<https://github.com/Zed-777/Sequential-Candle-Patterns/issues>

---

## Disclaimer

This software is provided for **educational and research purposes**. It is not financial advice. Use at your own risk. The authors assume no liability for trading decisions made based on this system's output.

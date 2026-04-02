# GDPR & Privacy Compliance (Placeholder)

This document describes the current GDPR/Privacy approach for the Candle Patterns project:

- Data minimization: only OHLCV data from user upload/Yahoo input is stored.
- Consent: user action required before upload.
- Right to erasure: implemented via CLI command `cli cleanup` and `clear_history` from dashboard.
- TLS-in-transit: assumed via HTTPS hosting; dashboard development supports reverse proxy setup.
- Sensitive storage encryption: no PII stored at this stage.
- Audit logs: job-level logs are stored in `logs/` (if enabled).

## TODO

- Add formal policy text.
- Add data processing agreement and DPA checklist.
- Add third-party vendor assessment for Yahoo Finance API usage.

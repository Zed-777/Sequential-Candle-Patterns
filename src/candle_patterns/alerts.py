"""
Sequence Alerts Module.

Monitors for pattern matches and triggers notifications via:
- In-app alert panel (stored in-memory and in SQLite)
- Webhook POST to user-configured URLs
- Email notifications via SMTP
- Logging-based alerts for server-side monitoring

Each alert rule specifies:
- One or more sequences to watch
- Optional symbol/interval context
- Alert action (in-app, webhook, email, or any combination)
"""

from __future__ import annotations

import json
import logging
import smtplib
import sqlite3
import time
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

_ALERTS_DB = Path("data/alerts.db")

# ---------------------------------------------------------------------------
# SQLite persistence for alert history & rules
# ---------------------------------------------------------------------------

def _init_alerts_db(db_path: Optional[Path] = None) -> None:
    db = db_path or _ALERTS_DB
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS alert_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sequences TEXT NOT NULL,
            symbol TEXT DEFAULT '',
            interval TEXT DEFAULT '',
            webhook_url TEXT DEFAULT '',
            email_to TEXT DEFAULT '',
            enabled INTEGER DEFAULT 1,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id INTEGER,
            rule_name TEXT,
            sequence TEXT NOT NULL,
            symbol TEXT DEFAULT '',
            match_count INTEGER DEFAULT 1,
            message TEXT,
            severity TEXT DEFAULT 'info',
            triggered_at REAL NOT NULL,
            acknowledged INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Alert Rule CRUD
# ---------------------------------------------------------------------------

def add_alert_rule(
    name: str,
    sequences: List[str],
    symbol: str = "",
    interval: str = "",
    webhook_url: str = "",
    email_to: str = "",
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Create a new alert rule. Returns the created rule dict."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    now = time.time()
    seqs_json = json.dumps(sequences)
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute(
        "INSERT INTO alert_rules (name, sequences, symbol, interval, webhook_url, email_to, enabled, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)",
        (name, seqs_json, symbol, interval, webhook_url, email_to, now, now),
    )
    rule_id = c.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": rule_id,
        "name": name,
        "sequences": sequences,
        "symbol": symbol,
        "interval": interval,
        "webhook_url": webhook_url,
        "email_to": email_to,
        "enabled": True,
        "created_at": now,
    }


def list_alert_rules(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return all alert rules."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM alert_rules ORDER BY created_at DESC").fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "name": r["name"],
            "sequences": json.loads(r["sequences"]),
            "symbol": r["symbol"],
            "interval": r["interval"],
            "webhook_url": r["webhook_url"],
            "email_to": r["email_to"] if "email_to" in r.keys() else "",
            "enabled": bool(r["enabled"]),
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        })
    return results


def remove_alert_rule(rule_id: int, db_path: Optional[Path] = None) -> bool:
    """Delete an alert rule by ID. Returns True if deleted."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def toggle_alert_rule(rule_id: int, enabled: bool, db_path: Optional[Path] = None) -> bool:
    """Enable/disable an alert rule."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute(
        "UPDATE alert_rules SET enabled = ?, updated_at = ? WHERE id = ?",
        (int(enabled), time.time(), rule_id),
    )
    updated = c.rowcount > 0
    conn.commit()
    conn.close()
    return updated


# ---------------------------------------------------------------------------
# Alert History
# ---------------------------------------------------------------------------

def record_alert(
    rule_id: Optional[int],
    rule_name: str,
    sequence: str,
    symbol: str = "",
    match_count: int = 1,
    message: str = "",
    severity: str = "info",
    db_path: Optional[Path] = None,
) -> int:
    """Record a triggered alert. Returns the alert history ID."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    now = time.time()
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute(
        "INSERT INTO alert_history "
        "(rule_id, rule_name, sequence, symbol, match_count, message, severity, triggered_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (rule_id, rule_name, sequence, symbol, match_count, message, severity, now),
    )
    alert_id = c.lastrowid
    conn.commit()
    conn.close()
    return alert_id


def get_alert_history(
    limit: int = 50,
    unacknowledged_only: bool = False,
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Return recent alert history entries."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM alert_history"
    if unacknowledged_only:
        query += " WHERE acknowledged = 0"
    query += " ORDER BY triggered_at DESC LIMIT ?"
    rows = conn.execute(query, (limit,)).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "rule_id": r["rule_id"],
            "rule_name": r["rule_name"],
            "sequence": r["sequence"],
            "symbol": r["symbol"],
            "match_count": r["match_count"],
            "message": r["message"],
            "severity": r["severity"],
            "triggered_at": r["triggered_at"],
            "acknowledged": bool(r["acknowledged"]),
        }
        for r in rows
    ]


def acknowledge_alert(alert_id: int, db_path: Optional[Path] = None) -> bool:
    """Mark an alert as acknowledged."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute("UPDATE alert_history SET acknowledged = 1 WHERE id = ?", (alert_id,))
    updated = c.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def clear_alert_history(db_path: Optional[Path] = None) -> int:
    """Delete all alert history. Returns number of rows removed."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    conn = sqlite3.connect(str(db))
    c = conn.cursor()
    c.execute("DELETE FROM alert_history")
    count = c.rowcount
    conn.commit()
    conn.close()
    return count


# ---------------------------------------------------------------------------
# Webhook dispatch
# ---------------------------------------------------------------------------

def send_webhook(
    url: str,
    payload: Dict[str, Any],
    timeout: int = 10,
) -> bool:
    """POST JSON payload to *url*. Returns True on success."""
    if not url:
        return False
    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "CandlePatterns-AlertBot/1.0")
        with urlopen(req, timeout=timeout) as resp:  # nosec B310
            logger.info("Webhook sent to %s — status %s", url, resp.status)
            return resp.status < 400
    except (URLError, OSError, ValueError) as exc:
        logger.warning("Webhook failed for %s: %s", url, exc)
        return False


# ---------------------------------------------------------------------------
# Email dispatch (SMTP)
# ---------------------------------------------------------------------------

# Email configuration — loaded from preferences or set programmatically.
# Keys: smtp_host, smtp_port, smtp_user, smtp_password, smtp_from, smtp_use_tls
_EMAIL_CONFIG: Dict[str, Any] = {}


def configure_email(
    smtp_host: str = "localhost",
    smtp_port: int = 587,
    smtp_user: str = "",
    smtp_password: str = "",
    smtp_from: str = "",
    smtp_use_tls: bool = True,
) -> None:
    """Set SMTP configuration for email alerts.

    Call once at startup or from the Settings tab.  Credentials are kept
    only in process memory — never persisted to disk.
    """
    _EMAIL_CONFIG.update({
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "smtp_user": smtp_user,
        "smtp_password": smtp_password,
        "smtp_from": smtp_from or smtp_user,
        "smtp_use_tls": smtp_use_tls,
    })


def send_email(
    to_addr: str,
    subject: str,
    body: str,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """Send an email alert. Returns True on success.

    Uses *config* dict if provided, otherwise falls back to module-level
    ``_EMAIL_CONFIG`` set via :func:`configure_email`.
    """
    if not to_addr:
        return False

    cfg = config or _EMAIL_CONFIG
    host = cfg.get("smtp_host", "localhost")
    port = int(cfg.get("smtp_port", 587))
    user = cfg.get("smtp_user", "")
    password = cfg.get("smtp_password", "")
    from_addr = cfg.get("smtp_from", "") or user
    use_tls = cfg.get("smtp_use_tls", True)

    if not from_addr:
        logger.warning("Email alert skipped — no smtp_from or smtp_user configured")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(body, "plain"))

    try:
        if use_tls:
            server = smtplib.SMTP(host, port, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            server.ehlo()

        if user and password:
            server.login(user, password)

        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        logger.info("Email alert sent to %s", to_addr)
        return True
    except (smtplib.SMTPException, OSError) as exc:
        logger.warning("Email alert failed for %s: %s", to_addr, exc)
        return False


# ---------------------------------------------------------------------------
# Check & Trigger — called by the live scanner
# ---------------------------------------------------------------------------

def check_and_trigger(
    df,
    symbol: str = "",
    db_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Evaluate all enabled alert rules against *df* and trigger matches.

    Parameters
    ----------
    df : pd.DataFrame
        Current OHLCV data.
    symbol : str
        Active symbol (used to filter symbol-specific rules).

    Returns
    -------
    list[dict]
        List of triggered alert info dicts.
    """
    from .patterns import find_sequence_occurrences

    rules = list_alert_rules(db_path=db_path)
    triggered = []

    for rule in rules:
        if not rule["enabled"]:
            continue
        # If rule has a symbol filter, skip if it doesn't match
        if rule["symbol"] and symbol and rule["symbol"].upper() != symbol.upper():
            continue

        for seq_str in rule["sequences"]:
            try:
                matches = find_sequence_occurrences(df, seq_str)
                if matches:
                    msg = (
                        f"Pattern '{seq_str}' matched {len(matches)} time(s)"
                        f"{' on ' + symbol if symbol else ''}"
                    )
                    severity = "warning" if len(matches) >= 3 else "info"

                    alert_id = record_alert(
                        rule_id=rule["id"],
                        rule_name=rule["name"],
                        sequence=seq_str,
                        symbol=symbol,
                        match_count=len(matches),
                        message=msg,
                        severity=severity,
                        db_path=db_path,
                    )

                    # Fire webhook if configured
                    if rule["webhook_url"]:
                        send_webhook(rule["webhook_url"], {
                            "alert_id": alert_id,
                            "rule": rule["name"],
                            "sequence": seq_str,
                            "symbol": symbol,
                            "match_count": len(matches),
                            "message": msg,
                            "timestamp": datetime.datetime.now(
                                datetime.timezone.utc
                            ).isoformat(),
                        })

                    # Fire email if configured
                    if rule.get("email_to"):
                        send_email(
                            to_addr=rule["email_to"],
                            subject=f"[CandlePatterns Alert] {rule['name']} — {seq_str}",
                            body=(
                                f"Alert: {rule['name']}\n"
                                f"Sequence: {seq_str}\n"
                                f"Symbol: {symbol or 'N/A'}\n"
                                f"Matches: {len(matches)}\n"
                                f"Severity: {severity}\n"
                                f"Time: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
                            ),
                        )

                    triggered.append({
                        "alert_id": alert_id,
                        "rule_name": rule["name"],
                        "sequence": seq_str,
                        "match_count": len(matches),
                        "severity": severity,
                        "message": msg,
                    })
            except Exception as exc:
                logger.warning("Alert check failed for rule '%s' seq '%s': %s",
                               rule["name"], seq_str, exc)

    return triggered


def get_unread_count(db_path: Optional[Path] = None) -> int:
    """Return the number of unacknowledged alerts."""
    db = db_path or _ALERTS_DB
    _init_alerts_db(db)
    conn = sqlite3.connect(str(db))
    count = conn.execute(
        "SELECT COUNT(*) FROM alert_history WHERE acknowledged = 0"
    ).fetchone()[0]
    conn.close()
    return count

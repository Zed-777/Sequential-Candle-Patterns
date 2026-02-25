"""
Sequence Watchlist & Saved Libraries.

Persists user-created sequence collections to a JSON file so they
survive across sessions.  Each watchlist entry stores:

- A label (e.g. "My Bull Setup")
- One or more sequence strings
- Optional symbol / interval context
- Created-at / last-used timestamps
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path("data/watchlist.json")


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _load_raw(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load watchlist from %s: %s", path, exc)
        return []


def _save_raw(entries: List[Dict[str, Any]], path: Path) -> None:
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2)


# --------------------------------------------------------------------- public


def list_watchlist(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all watchlist entries, newest first."""
    p = Path(path) if path else _DEFAULT_PATH
    entries = _load_raw(p)
    entries.sort(key=lambda e: e.get("created_at", 0), reverse=True)
    return entries


def add_to_watchlist(
    label: str,
    sequences: List[str],
    symbol: str = "",
    interval: str = "",
    notes: str = "",
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new watchlist entry.  Returns the created entry dict."""
    if not label or not label.strip():
        raise ValueError("Watchlist label must not be empty.")
    if not sequences:
        raise ValueError("At least one sequence is required.")

    p = Path(path) if path else _DEFAULT_PATH
    entries = _load_raw(p)

    entry: Dict[str, Any] = {
        "id": int(time.time() * 1000),
        "label": label.strip(),
        "sequences": [s.strip() for s in sequences if s.strip()],
        "symbol": symbol.strip(),
        "interval": interval.strip(),
        "notes": notes.strip(),
        "created_at": time.time(),
        "last_used": None,
    }

    entries.append(entry)
    _save_raw(entries, p)
    logger.info("Added watchlist entry '%s' (%d sequences)", label, len(entry["sequences"]))
    return entry


def remove_from_watchlist(entry_id: int, path: Optional[str] = None) -> bool:
    """Remove entry by id.  Returns True if found and removed."""
    p = Path(path) if path else _DEFAULT_PATH
    entries = _load_raw(p)
    before = len(entries)
    entries = [e for e in entries if e.get("id") != entry_id]
    if len(entries) == before:
        return False
    _save_raw(entries, p)
    return True


def update_last_used(entry_id: int, path: Optional[str] = None) -> bool:
    """Touch *last_used* timestamp for an entry."""
    p = Path(path) if path else _DEFAULT_PATH
    entries = _load_raw(p)
    for e in entries:
        if e.get("id") == entry_id:
            e["last_used"] = time.time()
            _save_raw(entries, p)
            return True
    return False


def clear_watchlist(path: Optional[str] = None) -> int:
    """Remove all entries.  Returns count removed."""
    p = Path(path) if path else _DEFAULT_PATH
    entries = _load_raw(p)
    count = len(entries)
    _save_raw([], p)
    return count


def get_watchlist_entry(entry_id: int, path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a single watchlist entry by id."""
    p = Path(path) if path else _DEFAULT_PATH
    for e in _load_raw(p):
        if e.get("id") == entry_id:
            return e
    return None


def update_watchlist_entry(
    entry_id: int,
    label: Optional[str] = None,
    sequences: Optional[List[str]] = None,
    symbol: Optional[str] = None,
    interval: Optional[str] = None,
    notes: Optional[str] = None,
    path: Optional[str] = None,
) -> bool:
    """Update fields of an existing watchlist entry.  Returns True on success."""
    p = Path(path) if path else _DEFAULT_PATH
    entries = _load_raw(p)
    for e in entries:
        if e.get("id") != entry_id:
            continue
        if label is not None:
            e["label"] = label.strip()
        if sequences is not None:
            e["sequences"] = [s.strip() for s in sequences if s.strip()]
        if symbol is not None:
            e["symbol"] = symbol.strip()
        if interval is not None:
            e["interval"] = interval.strip()
        if notes is not None:
            e["notes"] = notes.strip()
        _save_raw(entries, p)
        return True
    return False


def export_watchlist(path: Optional[str] = None) -> str:
    """Return the watchlist as a formatted JSON string (for copy/paste)."""
    p = Path(path) if path else _DEFAULT_PATH
    entries = _load_raw(p)
    return json.dumps(entries, indent=2)


def import_watchlist(json_str: str, merge: bool = True, path: Optional[str] = None) -> int:
    """Import watchlist entries from a JSON string.

    Parameters
    ----------
    json_str : str
        JSON array of watchlist entries.
    merge : bool
        If True, merge with existing entries (skip duplicates by id).
        If False, replace the whole watchlist.
    path : str | None
        Custom file path.

    Returns
    -------
    int
        Number of entries imported.
    """
    try:
        incoming = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    if not isinstance(incoming, list):
        raise ValueError("Expected a JSON array of watchlist entries.")

    p = Path(path) if path else _DEFAULT_PATH

    if merge:
        existing = _load_raw(p)
        existing_ids = {e.get("id") for e in existing}
        added = 0
        for entry in incoming:
            if entry.get("id") not in existing_ids:
                existing.append(entry)
                added += 1
        _save_raw(existing, p)
        return added
    else:
        _save_raw(incoming, p)
        return len(incoming)

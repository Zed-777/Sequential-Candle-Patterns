"""
User Profiles & Preferences Module.

Persists user settings and preferences to a JSON file so they
survive across sessions. Includes:

- Default sequences and symbols
- Chart display preferences (theme, colours)
- Scanner defaults (hold period, lookahead)
- Dashboard layout preferences
- Recently used symbols and sequences
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path("data/preferences.json")

# Default preference values
_DEFAULTS: Dict[str, Any] = {
    "version": 1,
    "theme": "light",
    "default_sequences": ["3R -> 2G", "5R -> 3G", "2R -> Doji -> 2G"],
    "default_symbol": "AAPL",
    "default_period": "6mo",
    "default_interval": "1d",
    "hold_period": 5,
    "lookahead": 3,
    "initial_capital": 10000,
    "chart_style": "candlestick",
    "show_volume": True,
    "auto_discover_on_load": True,
    "discovery_max_results": 25,
    "heatmap_bucket_size": 10,
    "reverse_threshold": 1.5,
    "reverse_direction": "up",
    "reverse_lookback": 5,
    "multi_tf_intervals": ["1h", "1d"],
    "multi_tf_lookback": 5,
    "recent_symbols": [],
    "recent_sequences": [],
    "alert_sound_enabled": False,
    "live_refresh_interval": 60,
    "live_refresh_enabled": False,
    "max_recent_items": 10,
    "updated_at": 0.0,
}


def _ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_preferences(path: Optional[str] = None) -> Dict[str, Any]:
    """Load preferences from disk, merging with defaults for any missing keys.

    Parameters
    ----------
    path : str | None
        Path to preferences file. Uses ``data/preferences.json`` by default.

    Returns
    -------
    dict
        Complete preferences dict (all default keys guaranteed present).
    """
    p = Path(path) if path else _DEFAULT_PATH
    prefs = dict(_DEFAULTS)  # start with defaults

    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as fh:
                stored = json.load(fh)
            if isinstance(stored, dict):
                prefs.update(stored)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load preferences from %s: %s", p, exc)

    return prefs


def save_preferences(prefs: Dict[str, Any], path: Optional[str] = None) -> None:
    """Save preferences to disk.

    Parameters
    ----------
    prefs : dict
        Preferences dict to save.
    path : str | None
        Target path. Uses ``data/preferences.json`` by default.
    """
    p = Path(path) if path else _DEFAULT_PATH
    _ensure_dir(p)
    prefs["updated_at"] = time.time()
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(prefs, fh, indent=2)


def get_preference(key: str, path: Optional[str] = None) -> Any:
    """Get a single preference value."""
    prefs = load_preferences(path)
    return prefs.get(key, _DEFAULTS.get(key))


def set_preference(key: str, value: Any, path: Optional[str] = None) -> None:
    """Set a single preference value and save."""
    prefs = load_preferences(path)
    prefs[key] = value
    save_preferences(prefs, path)


def reset_preferences(path: Optional[str] = None) -> Dict[str, Any]:
    """Reset all preferences to defaults and save."""
    prefs = dict(_DEFAULTS)
    save_preferences(prefs, path)
    return prefs


def add_recent_symbol(symbol: str, path: Optional[str] = None) -> None:
    """Add a symbol to the recent symbols list (deduped, max 10)."""
    prefs = load_preferences(path)
    recents = prefs.get("recent_symbols", [])
    max_items = prefs.get("max_recent_items", 10)
    # Remove if already present, then prepend
    recents = [s for s in recents if s.upper() != symbol.upper()]
    recents.insert(0, symbol.upper())
    prefs["recent_symbols"] = recents[:max_items]
    save_preferences(prefs, path)


def add_recent_sequence(sequence: str, path: Optional[str] = None) -> None:
    """Add a sequence to the recent sequences list (deduped, max 10)."""
    prefs = load_preferences(path)
    recents = prefs.get("recent_sequences", [])
    max_items = prefs.get("max_recent_items", 10)
    recents = [s for s in recents if s.strip() != sequence.strip()]
    recents.insert(0, sequence.strip())
    prefs["recent_sequences"] = recents[:max_items]
    save_preferences(prefs, path)


def get_recent_symbols(path: Optional[str] = None) -> List[str]:
    """Return the recently used symbols list."""
    return load_preferences(path).get("recent_symbols", [])


def get_recent_sequences(path: Optional[str] = None) -> List[str]:
    """Return the recently used sequences list."""
    return load_preferences(path).get("recent_sequences", [])


def export_preferences(path: Optional[str] = None) -> str:
    """Export preferences as a JSON string (for backup/sharing)."""
    prefs = load_preferences(path)
    return json.dumps(prefs, indent=2)


def import_preferences(json_str: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Import preferences from a JSON string, merging with defaults."""
    try:
        imported = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    if not isinstance(imported, dict):
        raise ValueError("Preferences must be a JSON object")

    prefs = dict(_DEFAULTS)
    prefs.update(imported)
    save_preferences(prefs, path)
    return prefs

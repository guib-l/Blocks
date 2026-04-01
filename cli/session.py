"""
Persistent session configuration for the blocks CLI.
Stored in ~/.blocks/session.json.
"""

import json
import sys
from pathlib import Path

SESSION_FILE = Path.home() / ".blocks" / "session.json"

DEFAULTS = {
    "author": "",
    "directory": "myblock/",
    "email": "",
}


def load() -> dict:
    """Load session config, falling back to defaults on any error."""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save(data: dict) -> None:
    """Persist session config to disk."""
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def set_values(**kwargs) -> dict:
    """Update specific keys in the session config and save."""
    cfg = load()
    cfg.update(kwargs)
    save(cfg)
    return cfg

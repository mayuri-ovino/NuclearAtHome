"""Load config/settings.toml and refuse any value still marked TODO.

Every physics value, threshold and calibration constant starts as a TODO-LIT,
TODO-DECIDE or TODO-CALIBRATE placeholder. require() raises TodoValue for those,
so no code path can run on an undecided value.
"""
from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "config" / "settings.toml"


class TodoValue(Exception):
    """A setting the code needs is missing or still a TODO placeholder."""


def load(path: Path | None = None) -> dict:
    """Read the settings file (NAH_SETTINGS overrides the default path)."""
    path = path or Path(os.environ.get("NAH_SETTINGS", DEFAULT_PATH))
    with open(path, "rb") as handle:
        settings = tomllib.load(handle)
    if os.environ.get("NAH_SCIENCE_DIR"):  # local hosting: a user-writable science directory
        settings["storage"]["science_dir"] = os.environ["NAH_SCIENCE_DIR"]
    return settings


def _has_todo(value: Any) -> bool:
    if isinstance(value, str):
        return value.upper().startswith("TODO")
    if isinstance(value, list):
        return any(_has_todo(item) for item in value)
    if isinstance(value, dict):
        return any(_has_todo(item) for item in value.values())
    return False


def require(settings: dict, dotted: str) -> Any:
    """Return settings['a']['b'] for 'a.b', or raise TodoValue if missing or TODO."""
    value: Any = settings
    for key in dotted.split("."):
        if not isinstance(value, dict) or key not in value:
            raise TodoValue(f"setting {dotted} is missing")
        value = value[key]
    if _has_todo(value):
        raise TodoValue(f"setting {dotted} is still {value!r}; decide it in docs/interfaces first")
    return value

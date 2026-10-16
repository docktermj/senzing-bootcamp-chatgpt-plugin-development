"""Shared Codex automatic-continuation state; never starts or modifies a bootcamp."""

from __future__ import annotations

import json
from pathlib import Path


def truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().strip("\"'").lower() in {"1", "true", "yes", "on"}


def preference(key: str) -> bool:
    try:
        lines = Path("config/bootcamp_preferences.yaml").read_text(encoding="utf-8").splitlines()
    except (OSError, ValueError):
        return False
    result = False
    for line in lines:
        if not line or line[:1].isspace() or line.startswith("#") or ":" not in line:
            continue
        name, value = line.split(":", 1)
        if name.strip() == key:
            result = truthy(value.split("#", 1)[0])
    return result


def active_progress() -> dict[str, object] | None:
    try:
        progress = json.loads(Path("config/bootcamp_progress.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(progress, dict):
        return None
    module = progress.get("current_module")
    if not isinstance(module, str) or not module.strip() or preference("bootcamp_complete"):
        return None
    return progress

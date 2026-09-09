#!/usr/bin/env python3
"""Keep an active Codex bootcamp turn open until it reaches its next question."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


POINTER = "👉"


def truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().strip("\"'").lower() in {"1", "true", "yes", "on"}


def preference(key: str) -> bool:
    try:
        lines = Path("config/bootcamp_preferences.yaml").read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for line in lines:
        if not line or line[:1].isspace() or line.lstrip().startswith("#") or ":" not in line:
            continue
        name, value = line.split(":", 1)
        if name == key:
            return truthy(value.split("#", 1)[0])
    return False


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}

    if payload.get("stop_hook_active") is True:
        return 0
    if not Path("config/bootcamp_progress.json").is_file():
        return 0
    if truthy(os.environ.get("SENZING_BOOTCAMP_DISABLE_STOP_NUDGE", "")):
        return 0
    if preference("disable_stop_nudge") or preference("bootcamp_complete"):
        return 0

    final_text = payload.get("last_assistant_message")
    if not isinstance(final_text, str) or not final_text.strip() or POINTER in final_text:
        return 0

    reason = (
        "The Senzing Bootcamp is active, but your last response ended without its next Socratic "
        "question. Do not wait for another bootcamper prompt. Read config/bootcamp_progress.json, "
        "load the matching Senzing Bootcamp module skill and shared ground rules, and continue all "
        "automatic and non-yielding work now. Use concise commentary while working. End only when "
        "you reach exactly one question defined by the shipped skill; render that 👉 question and "
        "its options as the final response, with nothing after it. Never invent a continuation "
        "question and never repeat a question already present in your last response."
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

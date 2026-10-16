#!/usr/bin/env python3
"""Keep an active Codex bootcamp turn open until it reaches its next question."""

from __future__ import annotations

import json
import os
import sys

from bootcamp_state import active_progress, preference, truthy


POINTER = "👉"


def main() -> int:
    if active_progress() is None:
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    if payload.get("stop_hook_active") is True:
        return 0
    if truthy(os.environ.get("SENZING_BOOTCAMP_DISABLE_STOP_NUDGE", "")):
        return 0
    if preference("disable_stop_nudge"):
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

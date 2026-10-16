#!/usr/bin/env python3
"""Validate native Codex edit targets and preserve the bootcamp's secret-write guard."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys


INVALID_MSG = "Write blocked: malformed or unsupported edit input; no safe target set could be established."
OUTSIDE_MSG = "Write blocked: that path is outside the Bootcamp project. Use a project-relative path."
TEMP_MSG = "Write blocked: use a project-relative path, not a system temp or Downloads directory."
SECRET_MSG = "Write blocked: a possible hardcoded secret was detected. Use environment variables instead."
SECRET_PATTERN = (
    r"BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY"
    r"|AKIA[0-9A-Z]{16}"
    r"|AQAAAD[A-Za-z0-9+/=]{16,}"
)
HEADERS = ("*** Add File: ", "*** Delete File: ", "*** Update File: ")


def patch_targets(command: str) -> list[str]:
    lines = command.strip().splitlines()
    if not lines or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
        raise ValueError(INVALID_MSG)
    targets = []
    index = 1
    while index < len(lines) - 1:
        header = next((prefix for prefix in HEADERS if lines[index].startswith(prefix)), None)
        if header is None:
            raise ValueError(INVALID_MSG)
        targets.append(lines[index][len(header):].strip())
        index += 1
        if header == "*** Update File: " and index < len(lines) - 1 and lines[index].startswith("*** Move to: "):
            targets.append(lines[index][len("*** Move to: "):].strip())
            index += 1
        body_start = index
        while index < len(lines) - 1 and not lines[index].startswith(HEADERS):
            line = lines[index]
            if header == "*** Add File: ":
                if not line.startswith("+"):
                    raise ValueError(INVALID_MSG)
            elif header == "*** Update File: ":
                if not (line == "" or line.startswith((" ", "+", "-", "@@ "))
                        or line in {"@@", "*** End of File"}):
                    raise ValueError(INVALID_MSG)
            else:
                raise ValueError(INVALID_MSG)
            index += 1
        if header == "*** Update File: " and index == body_start:
            raise ValueError(INVALID_MSG)
    if not targets or any(not target or "\0" in target for target in targets):
        raise ValueError(INVALID_MSG)
    return targets


def edit_targets(payload: dict) -> list[str]:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        raise ValueError(INVALID_MSG)
    name = payload.get("tool_name")
    if name == "apply_patch":
        command = tool_input.get("command")
        if not isinstance(command, str) or "\0" in command:
            raise ValueError(INVALID_MSG)
        return patch_targets(command)
    if name in {"Write", "Edit"}:
        target = tool_input.get("file_path")
        if isinstance(target, str) and target.strip() and "\0" not in target:
            return [target]
    raise ValueError(INVALID_MSG)


def validate_target(target: str, workspace: Path) -> None:
    if any(token in target.upper() for token in ("%TEMP%", "%TMP%")):
        raise ValueError(TEMP_MSG)
    if os.name != "nt" and (re.match(r"^[A-Za-z]:[\\/]", target) or target.startswith("\\\\")):
        raise ValueError(OUTSIDE_MSG)
    destination = Path(os.path.expanduser(target)).resolve()
    if destination.is_relative_to(workspace):
        return
    normalized = str(destination).replace("\\", "/").lower()
    temporary = normalized.startswith(("/tmp/", "/var/tmp/", "/private/tmp/", "/private/var/folders/"))
    temporary = temporary or any(part in normalized for part in ("/downloads/", "/appdata/local/temp/", "/windows/temp/"))
    for name in ("TMPDIR", "TEMP", "TMP"):
        value = os.environ.get(name)
        if value and destination.is_relative_to(Path(value).resolve()):
            temporary = True
    raise ValueError(TEMP_MSG if temporary else OUTSIDE_MSG)


def main() -> int:
    if not Path("config/bootcamp_progress.json").is_file():
        return 0
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError(INVALID_MSG)
        targets = edit_targets(payload)
        workspace = Path.cwd().resolve()
        for target in targets:
            validate_target(target, workspace)
        if re.search(SECRET_PATTERN, raw):
            raise ValueError(SECRET_MSG)
    except (OSError, ValueError, TypeError, RuntimeError) as error:
        message = str(error) if str(error) in {INVALID_MSG, OUTSIDE_MSG, TEMP_MSG, SECRET_MSG} else INVALID_MSG
        print(message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

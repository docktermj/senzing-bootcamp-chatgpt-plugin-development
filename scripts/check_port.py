#!/usr/bin/env python3
"""Static release checks for the generated Codex port."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/senzing-bootcamp"
errors: list[str] = []

manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
version = (ROOT / "UPSTREAM_VERSION").read_text().strip()
if manifest.get("version") != version:
    errors.append("plugin manifest version does not match UPSTREAM_VERSION")
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    errors.append("release version must be stable SemVer without a cachebuster")
commit = (ROOT / "UPSTREAM_COMMIT").read_text().strip()
if not re.fullmatch(r"[0-9a-f]{40}", commit):
    errors.append("UPSTREAM_COMMIT must contain the full source commit")

required = [
    PLUGIN / ".mcp.json",
    PLUGIN / "skills/start-bootcamp/SKILL.md",
    PLUGIN / "skills/bootcamp-onboarding/SKILL.md",
    PLUGIN / "skills/graduation/SKILL.md",
]
for path in required:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")

for path in PLUGIN.rglob("*"):
    if not path.is_file() or path.suffix not in {".md", ".json", ".py"}:
        continue
    text = path.read_text(errors="replace")
    if "${CLAUDE_PLUGIN_ROOT}" in text or ".claude-plugin" in text:
        errors.append(f"unported runtime path in {path.relative_to(ROOT)}")
    if "/model opus" in text or "/model sonnet" in text:
        errors.append(f"unported Claude model command in {path.relative_to(ROOT)}")

if errors:
    print("Port checks failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print(f"Port checks passed for {version}")

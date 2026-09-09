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
    PLUGIN / "skills/package-bootcamp/SKILL.md",
    PLUGIN / "skills/bootcamp-onboarding/SKILL.md",
    PLUGIN / "skills/graduation/SKILL.md",
    PLUGIN / "docs/codex-interaction-contract.md",
]
for path in required:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")

ground_rules = (PLUGIN / "skills/bootcamp-onboarding/ground-rules.md").read_text()
for required_contract_text in (
    "## Codex turn execution (mandatory)",
    "../../docs/codex-interaction-contract.md",
    "continue in the same turn until the next skill-defined `👉` question",
):
    if required_contract_text not in ground_rules:
        errors.append(f"ground rules missing Codex interaction contract: {required_contract_text}")

interaction_contract_path = PLUGIN / "docs/codex-interaction-contract.md"
if interaction_contract_path.is_file():
    interaction_contract = interaction_contract_path.read_text()
    for required_contract_text in (
        "Commentary is a progress update, never a bootcamp turn boundary",
        "A final response containing only status is a contract violation",
        "exactly one `👉` question",
    ):
        if required_contract_text not in interaction_contract:
            errors.append(f"Codex interaction contract missing invariant: {required_contract_text}")

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

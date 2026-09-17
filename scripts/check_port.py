#!/usr/bin/env python3
"""Static release checks for the generated Codex port."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/senzing-bootcamp"
errors: list[str] = []

invariants_path = ROOT / "specs/INVARIANTS.md"
if not invariants_path.is_file():
    errors.append("missing Codex invariants ledger: specs/INVARIANTS.md")
else:
    invariants_text = invariants_path.read_text()
    definitions = re.findall(r"(?m)^- \*\*CINV-(\d{3})\*\* — (.+)$", invariants_text)
    definition_ids = [int(identifier) for identifier, _ in definitions]
    if definition_ids != list(range(1, len(definition_ids) + 1)):
        errors.append("CINV definitions must be unique, sequential, and append-only")
    for identifier, statement in definitions:
        if " MUST " not in f" {statement} " and " ALWAYS " not in f" {statement} ":
            errors.append(f"CINV-{identifier} is not phrased as a testable MUST/ALWAYS condition")
    index_match = re.search(
        r"(?ms)^## Index by subject\n(.*?)(?=^## Release source and provenance\n)",
        invariants_text,
    )
    indexed_ids = (
        [int(value) for value in re.findall(r"CINV-(\d{3})", index_match.group(1))]
        if index_match else []
    )
    if sorted(indexed_ids) != definition_ids or len(indexed_ids) != len(set(indexed_ids)):
        errors.append("each CINV definition must appear exactly once in the subject index")
    if "specs/INVARIANTS.md" not in (ROOT / "docs/PORTING.md").read_text():
        errors.append("porting workflow does not require review of the Codex invariants ledger")

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
    PLUGIN / "hooks/hooks.json",
    PLUGIN / "scripts/socratic-controller.py",
    PLUGIN / "scripts/stop-nudge.py",
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

hooks_path = PLUGIN / "hooks/hooks.json"
if hooks_path.is_file():
    hooks = json.loads(hooks_path.read_text())
    configured_events = hooks.get("hooks", {})
    expected_events = {
        "SessionStart", "UserPromptSubmit", "PreToolUse", "Stop", "PreCompact", "SessionEnd"
    }
    missing_events = expected_events - set(configured_events)
    if missing_events:
        errors.append(f"missing lifecycle hook events: {sorted(missing_events)}")
    commands: list[str] = []
    for groups in configured_events.values():
        for group in groups:
            for handler in group.get("hooks", []):
                command = handler.get("command", "")
                commands.append(command)
                if not handler.get("statusMessage"):
                    errors.append(f"hook has no visible statusMessage: {command}")
                if "${PLUGIN_ROOT}" not in command:
                    errors.append(f"hook does not use Codex PLUGIN_ROOT: {command}")
    if not any("socratic-controller.py" in command for command in commands):
        errors.append("UserPromptSubmit does not run the Socratic controller")
    hooks_documentation = (PLUGIN / "hooks/README.md").read_text()
    if "socratic-controller.py" not in hooks_documentation:
        errors.append("hook documentation does not name the Socratic controller")


def run_hook(script_name: str, workspace: Path, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PLUGIN_ROOT"] = str(PLUGIN.resolve())
    return subprocess.run(
        ["python3", str(PLUGIN / "scripts" / script_name)],
        cwd=workspace,
        env=env,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


with tempfile.TemporaryDirectory(prefix="senzing-codex-hooks-") as temp:
    workspace = Path(temp)
    (workspace / "config").mkdir()
    (workspace / "config/bootcamp_progress.json").write_text(
        json.dumps({"current_module": "business_problem", "current_step": 4}) + "\n"
    )
    controller = run_hook("socratic-controller.py", workspace, {"prompt": "3"})
    if controller.returncode != 0:
        errors.append(f"Socratic controller failed: {controller.stderr.strip()}")
    else:
        try:
            controller_output = json.loads(controller.stdout)
            context = controller_output["hookSpecificOutput"]["additionalContext"]
        except (KeyError, TypeError, ValueError):
            context = ""
        if "module-01-business-problem/SKILL.md" not in context or "exactly one" not in context:
            errors.append("Socratic controller did not rehydrate the active module and question contract")

    stopped = run_hook("stop-nudge.py", workspace, {"last_assistant_message": "Setup completed."})
    try:
        stop_output = json.loads(stopped.stdout)
    except ValueError:
        stop_output = {}
    if stopped.returncode != 0 or stop_output.get("decision") != "block":
        errors.append("Stop hook did not continue a status-only active bootcamp turn")

    question = run_hook(
        "stop-nudge.py", workspace, {"last_assistant_message": "👉 **Which option do you choose?**"}
    )
    if question.returncode != 0 or question.stdout.strip():
        errors.append("Stop hook did not allow a turn that ends with a bootcamp question")

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

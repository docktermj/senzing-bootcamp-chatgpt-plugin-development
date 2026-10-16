#!/usr/bin/env python3
"""Plan runtime checks and validate evidence records; never simulate a bootcamp run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASES = (
    ("mcp", {"capabilities": "live_mcp", "curriculum-contracts": "live_mcp"}),
    ("mechanisms", {"script-execution": "direct_script", "hook-lifecycle": "codex_host"}),
    ("conversation", {"turn-cycle": "codex_host", "resume-transition": "codex_host",
                      "module-paths": "codex_host", "artifact-review": "codex_host",
                      "terminal-completion": "codex_host"}),
)
STATUSES = {"PASS", "FAIL", "ADVISORY", "BLOCKED", "NOT_RUN"}


def snapshot(root: Path) -> str:
    inputs = {}
    plugin = root / "plugins/senzing-bootcamp"
    for path in sorted(plugin.rglob("*")):
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ValueError(f"Symlink runtime input: {relative}")
        if path.is_file():
            inputs[relative.as_posix()] = [hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777]
    if not inputs:
        raise ValueError("Shipped runtime tree is empty")
    for name in ("RELEASE_VERSION", "PARENT_VERSION", "PARENT_COMMIT", "docs/test-checklist.md"):
        inputs[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()


def validate_turns(root: Path, turns: list) -> list[str]:
    errors = []
    if len(turns) < 2:
        return ["Turn-cycle PASS needs at least two consecutive observed host turns"]
    for number, turn in enumerate(turns, 1):
        if not turn.get("input") or not turn.get("processed_answer") or not turn.get("transcript_ref"):
            errors.append(f"Turn {number} lacks input, answer-processing observation, or transcript")
        question = turn.get("question", "")
        options = turn.get("options", [])
        final = turn.get("final", "")
        if (not question.startswith("👉") or final.count("👉") != 1
                or final.strip() != "\n".join([question, *options]).strip()):
            errors.append(f"Turn {number} does not end at exactly its defined question and options")
        if turn.get("intermediate_yields") is not False:
            errors.append(f"Turn {number} lacks a non-yielding continuation observation")
        if turn.get("automatic_steps") and not turn.get("commentary"):
            errors.append(f"Turn {number} has automatic work without observed commentary")
        origin = turn.get("question_origin", {})
        name = origin.get("path", "")
        path = root / name
        if (not name.startswith("plugins/senzing-bootcamp/skills/") or path.is_symlink()
                or not path.resolve().is_relative_to((root / "plugins/senzing-bootcamp/skills").resolve())
                or not path.is_file()):
            errors.append(f"Turn {number} lacks an existing shipped question origin")
            continue
        lines = path.read_text().splitlines()
        line = origin.get("line")
        if (not isinstance(line, int) or line < 1 or line > len(lines)
                or not origin.get("template") or origin["template"] != lines[line - 1].strip()):
            errors.append(f"Turn {number} question origin does not match the shipped source line")
        if not turn.get("question_match_observation"):
            errors.append(f"Turn {number} lacks an observation matching the rendered question to its template")
    return errors


def validate_record(root: Path, record: dict) -> dict:
    errors = []
    if record.get("snapshot_sha256") != snapshot(root):
        errors.append("Runtime evidence is missing or stale for the shipped snapshot")
    environment = record.get("environment", {})
    for name in ("codex_build", "platform", "workspace", "tested_at", "mcp_server_version"):
        if not environment.get(name):
            errors.append(f"Runtime environment lacks {name}")
    plugin_version = json.loads((root / "plugins/senzing-bootcamp/.codex-plugin/plugin.json").read_text())["version"]
    if environment.get("installed_plugin_version") != plugin_version:
        errors.append("Observed installed plugin version does not match the shipped candidate")
    phases = {}
    for phase in record.get("phases", []):
        identifier = phase.get("id")
        if identifier in phases:
            errors.append(f"Duplicate phase: {identifier}")
        phases[identifier] = phase
    known = {identifier for identifier, _ in PHASES}
    for identifier in phases.keys() - known:
        errors.append(f"Unknown phase: {identifier}")
    results = {}
    for identifier, required in PHASES:
        phase_error_start = len(errors)
        checks = {}
        for check in phases.get(identifier, {}).get("checks", []):
            name = check.get("id")
            if name in checks:
                errors.append(f"Duplicate check: {identifier}/{name}")
            checks[name] = check
        for name in checks.keys() - required.keys():
            errors.append(f"Unknown check: {identifier}/{name}")
        statuses = []
        for name, evidence_type in required.items():
            check = checks.get(name, {})
            status = check.get("status", "NOT_RUN")
            statuses.append(status)
            if status not in STATUSES:
                errors.append(f"Unsupported status: {identifier}/{name}")
            if status in {"PASS", "FAIL"}:
                evidence = check.get("evidence", [])
                if (check.get("evidence_type") != evidence_type or not evidence
                        or any(not entry.get("reference") or not entry.get("observed") for entry in evidence)):
                    errors.append(f"{identifier}/{name} needs actual {evidence_type} evidence")
                if any(result != "PASS" for result in results.values()):
                    errors.append(f"{identifier}/{name} ran without a passed prerequisite phase")
                if evidence_type == "live_mcp" and (not check.get("tool") or "request" not in check
                                                     or not check.get("response_summary")):
                    errors.append(f"{identifier}/{name} lacks its live tool request/response record")
                if name == "capabilities" and check.get("tool") != "get_capabilities":
                    errors.append("Discovery evidence must come from live get_capabilities")
                if status == "PASS" and name == "turn-cycle":
                    errors.extend(validate_turns(root, check.get("turns", [])))
            if status == "ADVISORY":
                if identifier == "mcp":
                    errors.append("Unavailable live MCP is a prerequisite blocker, not an advisory pass")
                if not all(check.get(field) for field in ("reason", "impact", "follow_up")):
                    errors.append(f"{identifier}/{name} lacks advisory reason, impact, or follow-up")
            if status in {"BLOCKED", "NOT_RUN"} and not check.get("reason"):
                errors.append(f"{identifier}/{name} lacks a blocker/not-run reason")
        results[identifier] = (
            "BLOCKED" if len(errors) > phase_error_start else
            "PASS" if all(status == "PASS" for status in statuses) else
            "FAIL" if "FAIL" in statuses else
            "ADVISORY" if all(status in {"PASS", "ADVISORY"} for status in statuses) else "BLOCKED"
        )
    for finding in record.get("findings", []):
        if (finding.get("route") not in {"local", "parent-bound"} or not finding.get("reason")
                or not finding.get("evidence") or not finding.get("source") or not finding.get("disposition")):
            errors.append("Runtime finding lacks routing, reason, source, evidence, or disposition")
    return {"record_valid": not errors, "dry_run_passed": not errors and all(value == "PASS" for value in results.values()),
            "phases": results, "errors": errors, "findings": record.get("findings", []),
            "assurance": "Validates recorded evidence structure, not the truth of host/tool observations"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    try:
        if args.record:
            result = validate_record(ROOT, json.loads(args.record.read_text()))
            print(json.dumps(result, indent=2))
            if not result["record_valid"]:
                raise SystemExit(1)
            if not result["dry_run_passed"]:
                raise SystemExit(2)
        else:
            print(json.dumps({"snapshot_sha256": snapshot(ROOT), "phases": [
                {"id": identifier, "checks": [{"id": name, "evidence_type": origin, "status": "NOT_RUN"}
                                              for name, origin in checks.items()]}
                for identifier, checks in PHASES], "dry_run_passed": False}, indent=2))
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        raise SystemExit(f"Runtime evidence blocked: {error}") from error


if __name__ == "__main__":
    main()

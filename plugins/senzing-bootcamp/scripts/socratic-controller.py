#!/usr/bin/env python3
"""Rehydrate the active Socratic bootcamp controller on every user prompt."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


MODULE_SKILLS = {
    "bootcamp_preparation": "bootcamp-preparation",
    "preparation": "bootcamp-preparation",
    "entity_resolution_concepts": "module-00-entity-resolution-concepts",
    "business_problem": "module-01-business-problem",
    "sdk_setup": "module-02-sdk-setup",
    "system_verification": "module-03-system-verification",
    "truthset_visualization": "module-03b-truthset-visualization",
    "truth_set_visualization": "module-03b-truthset-visualization",
    "data_collection": "module-04-data-collection",
    "data_quality_mapping": "module-05-data-quality-mapping",
    "data_quality_mapping_transformation": "module-05-data-quality-mapping",
    "data_processing": "module-06-data-processing",
    "query_visualize_discover": "module-07-query-visualize-discover",
    "graduation": "graduation",
}


def normalized(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def plugin_root() -> Path:
    configured = os.environ.get("PLUGIN_ROOT") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[1]


def active_skill(progress: dict[str, object]) -> str:
    module = normalized(progress.get("current_module"))
    if not module:
        return "bootcamp-onboarding"
    if module in MODULE_SKILLS:
        return MODULE_SKILLS[module]
    for key, skill in MODULE_SKILLS.items():
        if key in module or module in key:
            return skill
    return "bootcamp-onboarding"


def main() -> int:
    progress_path = Path("config/bootcamp_progress.json")
    if not progress_path.is_file():
        return 0
    try:
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        progress = {}
    if not isinstance(progress, dict):
        progress = {}

    root = plugin_root()
    skill_name = active_skill(progress)
    skill_path = root / "skills" / skill_name / "SKILL.md"
    ground_rules = root / "skills" / "bootcamp-onboarding" / "ground-rules.md"
    interaction_contract = root / "docs" / "codex-interaction-contract.md"
    step = progress.get("current_step")
    step_context = f" The recorded current step is {step!r}." if step not in (None, "") else ""
    context = (
        "A Senzing Bootcamp is active. Treat this prompt as the bootcamper's response to the "
        "pending Socratic question unless it clearly invokes an anytime bootcamp control. Before "
        "responding, read and follow the active skill at "
        f"{skill_path}, the shared rules at {ground_rules}, and the Codex interaction contract at "
        f"{interaction_contract}.{step_context} Process the answer first. During automatic work, "
        "send concise commentary so the bootcamper can see that Codex is working. Do not yield on "
        "commentary, a command result, a generated scenario, a status report, a file write, or a "
        "phase boundary. Continue in this same turn until the active shipped skill reaches its next "
        "defined question. The final response must end with exactly one skill-defined 👉 question "
        "and its options, with nothing after it. Never invent a continuation prompt."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

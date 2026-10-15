#!/usr/bin/env python3
"""Report whether an escalated issue's tagged fix has landed; never mutate GitHub or Git."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"(?:v)?\d+\.\d+\.\d+")
SHA = re.compile(r"[0-9a-f]{40}")


def git(checkout: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(checkout), *arguments],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def landed_provenance(checkout: Path) -> dict[str, str]:
    reference = "refs/remotes/origin/main"
    version = git(checkout, "show", f"{reference}:PARENT_VERSION")
    commit = git(checkout, "show", f"{reference}:PARENT_COMMIT")
    manifest = json.loads(git(checkout, "show", f"{reference}:.build-manifest.json"))
    plugin = json.loads(git(
        checkout, "show", f"{reference}:plugins/senzing-bootcamp/.codex-plugin/plugin.json",
    ))
    if (manifest.get("upstream_version") != version
            or manifest.get("upstream_commit") != commit or plugin.get("version") != version):
        raise ValueError("Landed provenance, build manifest, and plugin version disagree")
    return {"version": version, "commit": commit}


def evaluate(
    issue: dict[str, str], tag: str, parent: Path, source: Path, landed: dict[str, str],
) -> dict[str, str]:
    def decision(status: str, reason: str) -> dict[str, str]:
        return {"status": status, "reason": reason, "tag": tag}

    if not SEMVER.fullmatch(tag):
        return decision("blocked", "Select an exact stable SemVer tag")
    if issue.get("state") != "closed":
        return decision("awaiting_parent", "Parent issue is not closed")
    if issue.get("state_reason") == "not_planned":
        return decision("human_decision", "Parent declined the fix; keep the local issue open")
    if issue.get("state_reason") != "completed":
        return decision("blocked", "Parent closure is not confirmed as completed")
    closing_commit = issue.get("closing_commit", "")
    if not SHA.fullmatch(closing_commit):
        return decision("blocked", "A verified parent closing commit is required")
    if not SEMVER.fullmatch(landed.get("version", "")) or not SHA.fullmatch(landed.get("commit", "")):
        return decision("blocked", "Landed provenance is invalid")
    try:
        parent_commit = git(parent, "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
        source_commit = git(source, "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
        git(parent, "rev-parse", "--verify", f"{closing_commit}^{{commit}}")
        ancestry = subprocess.run(
            ["git", "-C", str(parent), "merge-base", "--is-ancestor", closing_commit, parent_commit],
            capture_output=True, text=True, check=False,
        )
        if ancestry.returncode == 1:
            if git(parent, "rev-parse", "--is-shallow-repository") == "true":
                return decision("blocked", "Fetch complete parent history before deciding ancestry")
            return decision("awaiting_release", "The checked parent tag does not contain the closing commit")
        if ancestry.returncode != 0:
            return decision("blocked", "Closing-commit ancestry could not be verified")
        parent_tree = git(parent, "rev-parse", "--verify", f"{parent_commit}:plugins/senzing-bootcamp")
        source_tree = git(source, "rev-parse", "--verify", f"{source_commit}:plugins/senzing-bootcamp")
        if parent_tree != source_tree:
            return decision("blocked", "Development and production tagged plugin trees differ; correspondence needs review")
        if landed["version"].removeprefix("v") != tag.removeprefix("v"):
            return decision("awaiting_landing", "Check the tag recorded in landed PARENT_VERSION, or land this release first")
        if landed["commit"] != source_commit:
            return decision("blocked", "Landed PARENT_COMMIT does not match the production tag")
    except (OSError, subprocess.CalledProcessError) as error:
        return decision("blocked", f"Required tag, commit, or plugin tree could not be verified: {error}")
    return {
        **decision("ready_to_close", "The verified tagged fix and matching provenance have landed"),
        "comment": f"Parity landed from parent tag {tag} (production commit {source_commit}); "
                   f"parent closing commit {closing_commit} is an ancestor of that tag.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-json", type=Path, required=True,
                        help="Parent snapshot: state, state_reason, closing_commit (full SHA)")
    parser.add_argument("--tag", required=True)
    parser.add_argument("--parent-checkout", type=Path, required=True)
    parser.add_argument("--source-checkout", type=Path, required=True)
    args = parser.parse_args()
    try:
        issue = json.loads(args.issue_json.read_text())
        if not isinstance(issue, dict):
            raise ValueError("Parent issue snapshot must be a JSON object")
        result = evaluate(issue, args.tag, args.parent_checkout, args.source_checkout, landed_provenance(ROOT))
    except (OSError, TypeError, ValueError, subprocess.CalledProcessError) as error:
        result = {"status": "blocked", "reason": str(error), "tag": args.tag}
    print(json.dumps(result, indent=2))
    if result["status"] == "blocked":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

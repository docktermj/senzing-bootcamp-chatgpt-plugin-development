#!/usr/bin/env python3
"""Report public payload divergence from committed snapshots without writing either checkout."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

if __package__:
    from . import propagate_to_public as propagation
else:
    import propagate_to_public as propagation


ROOT = Path(__file__).resolve().parents[1]


def snapshot(repo: Path, reference: str) -> tuple[str, dict[str, bytes], dict[str, str]]:
    commit = propagation.git(repo, "rev-parse", "--verify", "--end-of-options", f"{reference}^{{commit}}").decode().strip()
    files: dict[str, bytes] = {}
    modes: dict[str, str] = {}
    for entry in propagation.git(repo, "ls-tree", "-rz", commit).split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, object_id = metadata.decode().split()
        path = raw_path.decode()
        if not propagation.is_payload_path(path):
            continue
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"Unsupported payload file type at {path}")
        files[path] = propagation.git(repo, "cat-file", "blob", object_id)
        modes[path] = mode
    return commit, files, modes


def digest(data: bytes | None) -> str:
    return "absent" if data is None else hashlib.sha256(data).hexdigest()


def compare_payloads(
    expected: dict[str, bytes], public: dict[str, bytes],
    expected_modes: dict[str, str] | None = None, public_modes: dict[str, str] | None = None,
) -> list[dict]:
    findings = []
    for path in sorted(expected.keys() | public.keys()):
        before, after = expected.get(path), public.get(path)
        before_mode, after_mode = (expected_modes or {}).get(path), (public_modes or {}).get(path)
        if before == after and before_mode == after_mode:
            continue
        change = "public-added" if before is None else "public-removed" if after is None else "modified"
        fingerprint = hashlib.sha256((path + "\0" + digest(after) + "\0" + str(after_mode)).encode()).hexdigest()
        diff = "Binary content differs; inspect the pinned snapshots and content hashes."
        try:
            before_text, after_text = (before or b"").decode(), (after or b"").decode()
            if "\0" not in before_text + after_text:
                lines = list(difflib.unified_diff(
                    before_text.splitlines(True), after_text.splitlines(True),
                    fromfile=f"expected-public/{path}", tofile=f"public/{path}",
                ))
                diff = "".join(lines[:100])[:20000]
                if len(lines) > 100 or sum(map(len, lines[:100])) > 20000:
                    diff += "\n[Diff truncated; inspect the pinned snapshots for full evidence.]\n"
        except UnicodeDecodeError:
            pass
        if before_mode != after_mode:
            diff = f"File mode: expected {before_mode}, public {after_mode}\n" + diff
        findings.append({"path": path, "change": change, "expected_sha256": digest(before),
                         "public_sha256": digest(after), "fingerprint": f"retrofit-public:{fingerprint}",
                         "expected_mode": before_mode, "public_mode": after_mode,
                         "diff": diff})
    return findings


def matching_issues(finding: dict, issues: list[dict]) -> list[dict]:
    return [{"url": issue.get("url", issue.get("html_url")), "state": issue.get("state"),
             "title": issue.get("title")}
            for issue in issues if finding["fingerprint"] in (issue.get("body") or "")]


def report(
    development: Path, public: Path, development_ref: str = "HEAD", public_ref: str = "HEAD",
    issues: list[dict] | None = None,
) -> dict:
    if development.resolve() == public.resolve():
        raise ValueError("Development and public checkouts must be separate")
    for repo, slug in ((development, propagation.DEVELOPMENT_SLUG), (public, propagation.PUBLIC_SLUG)):
        origin = propagation.git(repo, "remote", "get-url", "origin").decode().strip()
        if propagation.remote_slug(origin) != slug:
            raise ValueError(f"Checkout origin must be {slug}")
    development_commit, built, built_modes = snapshot(development, development_ref)
    public_commit, shipped, shipped_modes = snapshot(public, public_ref)
    missing = propagation.REQUIRED - built.keys()
    if missing:
        raise ValueError("Development snapshot lacks required payload files: " + ", ".join(sorted(missing)))
    version = json.loads(built["plugins/senzing-bootcamp/.codex-plugin/plugin.json"])["version"]
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Development snapshot must have an exact stable local release version")
    expected = propagation.publication_payload(built, version)
    findings = compare_payloads(expected, shipped, built_modes, shipped_modes)
    for finding in findings:
        finding["matching_issues"] = matching_issues(finding, issues or [])
    return {"development_commit": development_commit, "public_commit": public_commit,
            "local_version": version, "working_tree_policy": "Committed snapshots only; dirty files are not read",
            "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-repo", type=Path, required=True)
    parser.add_argument("--development-ref", default="HEAD")
    parser.add_argument("--public-ref", default="HEAD")
    parser.add_argument("--issues-json", type=Path, help="Optional existing-issue array for fingerprint matching")
    args = parser.parse_args()
    try:
        issues = json.loads(args.issues_json.read_text()) if args.issues_json else []
        if not isinstance(issues, list) or any(not isinstance(issue, dict) for issue in issues):
            raise ValueError("--issues-json must contain an array of issue objects")
        result = report(ROOT, args.public_repo, args.development_ref, args.public_ref, issues)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Retrofit comparison blocked: {error}") from error
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

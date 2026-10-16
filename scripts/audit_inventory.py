#!/usr/bin/env python3
"""Inventory shipped audit inputs and validate review coverage, without claiming semantic correctness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKS = ("consistency", "references-and-routes", "onboarding-promises", "host-interaction",
          "invariant-coverage", "ownership-and-routing")
CONTEXT = ("tools/bootcamp-transform/contract.yaml", "specs/INVARIANTS.md", ".build-manifest.json",
           "RELEASE_VERSION", "PARENT_VERSION", "PARENT_COMMIT")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scoped(root: Path, name: str) -> Path:
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Audit input escapes the repository or is a symlink: {name}")
    return path


def shipped_file(path: Path) -> bool:
    return "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}


def inventory(root: Path) -> dict:
    context = {name: sha256(scoped(root, name).read_bytes()) for name in CONTEXT}
    contract_text = scoped(root, CONTEXT[0]).read_text()
    contract = json.loads("\n".join(line for line in contract_text.splitlines()
                                    if not line.lstrip().startswith("#")))
    plugin = scoped(root, contract["output_root"])
    build = json.loads(scoped(root, ".build-manifest.json").read_bytes())
    overlay_sources: dict[str, str] = {}
    for overlay in contract.get("overlays", []):
        source = scoped(root, overlay["source"])
        if not source.is_dir():
            raise ValueError(f"Missing overlay directory: {overlay['source']}")
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Overlay contains a symlink: {path.relative_to(root)}")
            if path.is_file() and shipped_file(path.relative_to(source)):
                scoped(root, path.relative_to(root).as_posix())
                destination = plugin / overlay.get("destination", ".") / path.relative_to(source)
                if not destination.resolve().is_relative_to(plugin.resolve()):
                    raise ValueError("Overlay destination escapes the shipped tree")
                overlay_sources[destination.relative_to(plugin).as_posix()] = path.relative_to(root).as_posix()
    files = []
    alerts = []
    for path in sorted(plugin.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Shipped tree contains a symlink: {path.relative_to(root)}")
        if not path.is_file() or not shipped_file(path.relative_to(plugin)):
            continue
        scoped(root, path.relative_to(root).as_posix())
        name = path.relative_to(plugin).as_posix()
        data = path.read_bytes()
        digest = sha256(data)
        try:
            data.decode("utf-8")
            kind = "text" if b"\0" not in data else "binary"
        except UnicodeDecodeError:
            kind = "binary"
        source = overlay_sources.get(name)
        source_hash = sha256(scoped(root, source).read_bytes()) if source else None
        if source and source_hash != digest:
            alerts.append(f"Overlay output differs from its source: {name}")
        if build.get("files", {}).get(name, {}).get("output") != digest:
            alerts.append(f"Shipped file differs from build manifest or is unrecorded: {name}")
        files.append({"path": path.relative_to(root).as_posix(), "sha256": digest,
                      "kind": kind, "bytes": len(data), "mode": path.stat().st_mode & 0o777,
                      "layer": "overlay" if source else "generated",
                      "overlay_source": source, "overlay_sha256": source_hash})
    names = {path["path"].removeprefix(contract["output_root"].rstrip("/") + "/") for path in files}
    for name in sorted(overlay_sources.keys() - names):
        alerts.append(f"Overlay contribution missing from shipped tree: {name}")
    for name in sorted(build.get("files", {}).keys() - names):
        alerts.append(f"Build-manifest file missing from shipped tree: {name}")
    if not files:
        raise ValueError("Shipped plugin tree is empty")
    snapshot = {"context": context, "files": files}
    return {**snapshot, "snapshot_sha256": sha256(json.dumps(snapshot, sort_keys=True).encode()),
            "required_checks": list(CHECKS), "structural_alerts": alerts,
            "invariant_disposition_register": contract["invariant_disposition_register"]}


def validate_coverage(snapshot: dict, review: dict) -> list[str]:
    errors = []
    if review.get("snapshot_sha256") != snapshot["snapshot_sha256"]:
        errors.append("Review snapshot is missing or stale")
    findings = {}
    for finding in review.get("findings", []):
        identifier = finding.get("id")
        if not identifier or identifier in findings:
            errors.append("Finding IDs must be present and unique")
        findings[identifier] = finding
        disposition = finding.get("disposition", {})
        if (finding.get("route") not in {"local", "parent-bound"} or not finding.get("reason")
                or not finding.get("source") or not finding.get("evidence")
                or disposition.get("kind") not in {"filed", "duplicate", "handoff", "blocked"}):
            errors.append("Finding lacks ownership, source, evidence, reason, or disposition")
        elif disposition["kind"] in {"filed", "duplicate"} and not disposition.get("url"):
            errors.append(f"Finding lacks an issue link: {identifier}")
        elif disposition["kind"] in {"handoff", "blocked"} and not disposition.get("reason"):
            errors.append(f"Finding lacks a handoff/blocker reason: {identifier}")
        if finding.get("route") == "local" and disposition.get("kind") == "handoff":
            errors.append(f"Local finding needs filing, deduplication, or an explicit blocker: {identifier}")
    records = {}
    for entry in review.get("files", []):
        name = entry.get("path")
        if name in records:
            errors.append(f"Duplicate file coverage: {name}")
        records[name] = entry
    expected = {entry["path"]: entry for entry in snapshot["files"]}
    for name, item in expected.items():
        entry = records.get(name, {})
        if (entry.get("sha256") != item["sha256"] or not entry.get("evidence")
                or entry.get("status") not in {"reviewed", "finding"}):
            errors.append(f"Missing, stale, deferred, or unsupported file review: {name}")
        if entry.get("status") == "finding" and entry.get("finding_id") not in findings:
            errors.append(f"File review lacks its finding: {name}")
    for name in records.keys() - expected.keys():
        errors.append(f"Review names an unshipped file: {name}")
    checks = {}
    register = snapshot["invariant_disposition_register"]
    for entry in review.get("checks", []):
        identifier = entry.get("id")
        if identifier in checks:
            errors.append(f"Duplicate check coverage: {identifier}")
        checks[identifier] = entry
        if entry.get("status") == "finding" and entry.get("finding_id") not in findings:
            errors.append(f"Check review lacks its finding: {identifier}")
        if entry.get("status") == "unexpressible":
            invariant = entry.get("invariant")
            dispositions = register.get("preserved_restated", []) + register.get("discounted", [])
            matches = [item for item in dispositions if item.get("id") == invariant
                       and any(limitation.get("check") == identifier and limitation.get("reason")
                               for limitation in item.get("audit_limitations", []))]
            if not matches or not entry.get("evidence"):
                errors.append(f"Unexpressible check lacks an explicit invariant-register limitation: {identifier}")
            if invariant == "INV-052" and any(item.get("id") == invariant for item in register.get("discounted", [])):
                errors.append("INV-052 cannot be discounted")
        elif entry.get("status") not in {"reviewed", "finding"} or not entry.get("evidence"):
            errors.append(f"Check is deferred or lacks review evidence: {identifier}")
    for identifier in CHECKS:
        entry = checks.get(identifier, {})
        if entry.get("status") not in {"reviewed", "finding"} or not entry.get("evidence"):
            errors.append(f"Required semantic review is incomplete: {identifier}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-json", type=Path)
    args = parser.parse_args()
    try:
        snapshot = inventory(ROOT)
        if args.review_json:
            review = json.loads(args.review_json.read_text())
            errors = validate_coverage(snapshot, review)
            result = {"snapshot_sha256": snapshot["snapshot_sha256"], "coverage_complete": not errors,
                      "coverage_errors": errors, "structural_alerts": snapshot["structural_alerts"],
                      "findings": review.get("findings", []),
                      "assurance": "Coverage validation does not establish semantic correctness or runtime readiness"}
            print(json.dumps(result, indent=2))
            if errors:
                raise SystemExit(1)
        else:
            print(json.dumps(snapshot, indent=2))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise SystemExit(f"Audit coverage blocked: {error}") from error


if __name__ == "__main__":
    main()

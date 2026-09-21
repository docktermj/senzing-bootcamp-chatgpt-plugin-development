#!/usr/bin/env python3
"""Build the Codex plugin by executing its declarative transformation contract."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "tools" / "bootcamp-transform" / "contract.yaml"
SEMVER = re.compile(r"^(?:v)?(\d+)\.(\d+)\.(\d+)$")


class ContractError(ValueError):
    """A deterministic contract or source-tree violation."""


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    """Load the dependency-free JSON form of the repository's YAML 1.2 contract."""
    source = "\n".join(
        line for line in path.read_text().splitlines() if not line.lstrip().startswith("#")
    )
    try:
        contract = json.loads(source)
    except json.JSONDecodeError as error:
        raise ContractError(f"E_INVALID_CONTRACT: {path}: {error}") from error
    if contract.get("contract_version") != 1:
        raise ContractError("E_INVALID_CONTRACT: contract_version must be 1")
    if not contract.get("rules"):
        raise ContractError("E_INVALID_CONTRACT: at least one file rule is required")
    for rule in contract["rules"]:
        if rule.get("kind") not in {"copy", "ignore"}:
            raise ContractError(f"E_INVALID_CONTRACT: unsupported file rule {rule.get('kind')!r}")
        if not rule.get("reason"):
            raise ContractError(f"E_INVALID_CONTRACT: file rule {rule.get('id')!r} needs a reason")
    return contract


def latest_tag(contract: dict[str, Any]) -> str:
    upstream_url = str(contract["upstream"]["repository"])
    output = run("git", "ls-remote", "--tags", "--refs", upstream_url)
    tags: list[tuple[tuple[int, int, int], str]] = []
    for line in output.splitlines():
        tag = line.rsplit("refs/tags/", 1)[-1]
        match = SEMVER.fullmatch(tag)
        if match:
            tags.append((tuple(map(int, match.groups())), tag))
    if not tags:
        raise SystemExit("No stable SemVer tags found upstream")
    return max(tags)[1]


def clone_tag(contract: dict[str, Any], tag: str, destination: Path) -> Path:
    upstream_url = str(contract["upstream"]["repository"])
    run("git", "clone", "--depth", "1", "--branch", tag, upstream_url, str(destination))
    return destination


def _matches(path: str, patterns: str | list[str]) -> bool:
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def plan_upstream(upstream_plugin: Path, contract: dict[str, Any]) -> list[tuple[Path, dict[str, Any]]]:
    """Classify every upstream file exactly once before any output is written."""
    plan: list[tuple[Path, dict[str, Any]]] = []
    for source_path in sorted(path for path in upstream_plugin.rglob("*") if path.is_file()):
        relative = source_path.relative_to(upstream_plugin)
        relative_name = relative.as_posix()
        matches = [rule for rule in contract["rules"] if _matches(relative_name, rule["match"])]
        if not matches:
            raise ContractError(f"E_UNMATCHED_FILE: {relative_name}")
        if len(matches) != 1:
            identifiers = ", ".join(str(rule.get("id", "<unnamed>")) for rule in matches)
            raise ContractError(f"E_AMBIGUOUS_FILE: {relative_name}: {identifiers}")
        plan.append((relative, matches[0]))
    return plan


def version_for(source: Path, contract: dict[str, Any]) -> str:
    upstream = contract["upstream"]
    manifest = source / upstream["source_root"] / upstream["version_file"]
    version = str(json.loads(manifest.read_text())["version"])
    if not SEMVER.fullmatch(version):
        raise SystemExit(f"Upstream manifest version is not stable SemVer: {version}")
    return version


def validate_invariant_register(version: str, contract: dict[str, Any]) -> None:
    """A new upstream release cannot inherit invariant judgments without review."""
    register = contract.get("invariant_disposition_register", {})
    if register.get("source_version") != version:
        raise ContractError(
            "E_INVARIANT_REVIEW: upstream version changed; re-review every INV-NNN disposition "
            "and update invariant_disposition_register"
        )


def _regex_flags(names: str) -> re.RegexFlag:
    flags = re.RegexFlag(0)
    for name in names:
        try:
            flags |= {"i": re.I, "m": re.M, "s": re.S, "x": re.X}[name]
        except KeyError as error:
            raise ContractError(f"E_INVALID_CONTRACT: unsupported regex flag {name!r}") from error
    return flags


def _add_notice(path: Path, text: str, notice: str) -> str:
    if path.suffix == ".md":
        if text.startswith("---\n"):
            marker = text.find("\n---\n", 4)
            if marker != -1:
                marker += len("\n---\n")
                return text[:marker] + f"\n<!-- {notice} -->\n" + text[marker:]
        return f"<!-- {notice} -->\n\n" + text
    if path.suffix == ".py":
        lines = text.splitlines(keepends=True)
        insertion = 1 if lines and lines[0].startswith("#!") else 0
        lines.insert(insertion, f"# {notice}\n")
        return "".join(lines)
    return text


def _apply_text_operation(path: Path, text: str, operation: dict[str, Any]) -> str:
    kind = operation["kind"]
    if kind == "literal":
        return text.replace(operation["old"], operation["new"])
    if kind == "regex":
        return re.sub(
            operation["pattern"], operation["replacement"], text,
            count=int(operation.get("count", 0)), flags=_regex_flags(operation.get("flags", "")),
        )
    if kind == "section":
        pattern = re.compile(
            rf"(?ms)^{re.escape(operation['start'])}\n.*?(?=^{re.escape(operation['end'])}\n)"
        )
        updated, count = pattern.subn(operation["replacement"].rstrip() + "\n\n", text, count=1)
        if count != 1:
            raise ContractError(
                f"E_TRANSFORM_MISMATCH: {path}: expected section {operation['start']!r}"
            )
        return updated
    if kind == "insert-before-first-heading":
        if operation["unless_contains"] in text:
            return text
        marker = text.find("\n## ")
        if marker == -1:
            raise ContractError(f"E_TRANSFORM_MISMATCH: {path}: expected a section heading")
        return text[:marker] + operation["value"] + text[marker:]
    raise ContractError(f"E_INVALID_CONTRACT: unsupported text operation {kind!r}")


def apply_text_transforms(destination: Path, contract: dict[str, Any]) -> None:
    for transform in contract.get("text_transforms", []):
        for path in sorted(file for file in destination.rglob("*") if file.is_file()):
            relative_name = path.relative_to(destination).as_posix()
            if not _matches(relative_name, transform["match"]):
                continue
            original = path.read_text()
            text = original
            for operation in transform.get("operations", []):
                text = _apply_text_operation(path, text, operation)
            if text != original and transform.get("notice_on_change"):
                text = _add_notice(path, text, transform["notice_on_change"])
            path.write_text(text)


def _replace_strings(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [_replace_strings(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: _replace_strings(item, old, new) for key, item in value.items()}
    return value


def _nodes_at_path(value: Any, parts: list[str]) -> list[Any]:
    nodes = [value]
    for part in parts:
        selected: list[Any] = []
        for node in nodes:
            if part == "*":
                if isinstance(node, dict):
                    selected.extend(node.values())
                elif isinstance(node, list):
                    selected.extend(node)
            elif isinstance(node, dict) and part in node:
                selected.append(node[part])
            elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
                selected.append(node[int(part)])
        nodes = selected
    return nodes


def _apply_json_operation(value: Any, operation: dict[str, Any]) -> Any:
    kind = operation["kind"]
    if kind == "replace-strings":
        return _replace_strings(value, operation["old"], operation["new"])
    nodes = _nodes_at_path(value, operation["path"])
    if not nodes:
        raise ContractError(f"E_TRANSFORM_MISMATCH: JSON path {operation['path']!r} matched nothing")
    if kind == "set-field-by-substring":
        for node in nodes:
            if not isinstance(node, dict):
                continue
            source = str(node.get(operation["source_field"], ""))
            for needle, replacement in operation["mapping"].items():
                if needle in source:
                    node[operation["target_field"]] = replacement
                    break
        return value
    if kind == "prepend":
        for node in nodes:
            if not isinstance(node, list):
                raise ContractError("E_TRANSFORM_MISMATCH: JSON prepend target is not a list")
            node.insert(0, operation["value"])
        return value
    raise ContractError(f"E_INVALID_CONTRACT: unsupported JSON operation {kind!r}")


def apply_json_transforms(destination: Path, contract: dict[str, Any]) -> None:
    for transform in contract.get("json_transforms", []):
        path = destination / transform["match"]
        if not path.is_file():
            raise ContractError(f"E_TRANSFORM_MISMATCH: missing JSON transform target {transform['match']}")
        value: Any = json.loads(path.read_text())
        for operation in transform.get("operations", []):
            value = _apply_json_operation(value, operation)
        path.write_text(json.dumps(value, indent=2) + "\n")


def _expand(value: Any, variables: dict[str, str]) -> Any:
    if isinstance(value, str):
        for name, replacement in variables.items():
            value = value.replace(f"${{{name}}}", replacement)
        return value
    if isinstance(value, list):
        return [_expand(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: _expand(item, variables) for key, item in value.items()}
    return value


def execute_contract(
    upstream_plugin: Path, destination: Path, repository_root: Path,
    contract: dict[str, Any], plan: list[tuple[Path, dict[str, Any]]], variables: dict[str, str],
) -> None:
    """Execute a preflighted contract into an empty destination."""
    destination.mkdir(parents=True)
    for relative, rule in plan:
        if rule["kind"] == "ignore":
            continue
        if rule["kind"] != "copy":
            raise ContractError(f"E_INVALID_CONTRACT: unsupported file rule {rule['kind']!r}")
        target = destination / rule.get("destination", relative.as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(upstream_plugin / relative, target)

    apply_text_transforms(destination, contract)
    apply_json_transforms(destination, contract)

    for artifact in contract.get("generated_artifacts", []):
        target = destination / artifact["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        value = _expand(artifact["value"], variables)
        if artifact["format"] != "json":
            raise ContractError(f"E_INVALID_CONTRACT: unsupported artifact format {artifact['format']!r}")
        target.write_text(json.dumps(value, indent=2) + "\n")

    for overlay in contract.get("overlays", []):
        source = repository_root / overlay["source"]
        target = destination / overlay.get("destination", ".")
        shutil.copytree(source, target, dirs_exist_ok=True)


def _source_commit(source: Path) -> str:
    try:
        return run("git", "rev-parse", "HEAD", cwd=source).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def build(
    source: Path, expected_tag: str | None, *, repository_root: Path = ROOT,
    contract_path: Path = CONTRACT_PATH,
) -> str:
    contract = load_contract(contract_path)
    version = version_for(source, contract)
    validate_invariant_register(version, contract)
    normalized_tag = expected_tag.removeprefix("v") if expected_tag else None
    if normalized_tag and normalized_tag != version:
        raise SystemExit(f"Tag {expected_tag} contains manifest version {version}")

    upstream_plugin = source / contract["upstream"]["source_root"]
    plan = plan_upstream(upstream_plugin, contract)
    commit = _source_commit(source)
    variables = {"UPSTREAM_VERSION": version, "UPSTREAM_COMMIT": commit}
    target = repository_root / contract["output_root"]
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="codex-port-", dir=target.parent) as temp:
        staged = Path(temp) / "plugin"
        execute_contract(upstream_plugin, staged, repository_root, contract, plan, variables)
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(staged, target)

    for artifact in contract.get("provenance_artifacts", []):
        path = repository_root / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_expand(artifact["value"], variables))
    return version


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Stable SemVer tag; defaults to latest upstream tag")
    parser.add_argument("--source-dir", type=Path, help="Use an already checked-out upstream tree")
    args = parser.parse_args()
    contract = load_contract()

    try:
        if args.source_dir:
            version = build(args.source_dir.resolve(), args.tag)
        else:
            tag = args.tag or latest_tag(contract)
            if not SEMVER.fullmatch(tag):
                raise SystemExit("--tag must be a stable SemVer tag such as 0.5.2")
            with tempfile.TemporaryDirectory(prefix="senzing-bootcamp-") as temp:
                source = clone_tag(contract, tag, Path(temp) / "upstream")
                version = build(source, tag)
    except ContractError as error:
        raise SystemExit(str(error)) from error
    print(f"Built Senzing Bootcamp Codex plugin {version}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validate Codex invariant supersession syntax and reciprocal links."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFINITION = re.compile(r"^- \*\*(CINV-\d{3})\*\* — (.+)$")
LINK = re.compile(r" *- \*\*(Superseded by|Supersedes):\*\* (CINV-\d{3})(?: — .+)?")


def analyze_invariants(text: str) -> tuple[dict[str, str], list[str]]:
    entries: dict[str, list[tuple[int, str]]] = {}
    errors: list[str] = []
    current = None
    for line_number, line in enumerate(text.splitlines(), 1):
        match = DEFINITION.fullmatch(line)
        if match:
            current = match.group(1)
            if current in entries:
                errors.append(f"line {line_number}: duplicate definition {current}")
            entries.setdefault(current, []).append((line_number, match.group(2)))
        elif line.startswith("## "):
            current = None
        elif current is not None:
            entries[current].append((line_number, line))
    if not entries:
        errors.append("No CINV definitions found")

    successors: dict[str, str] = {}
    predecessors: dict[str, set[str]] = {identifier: set() for identifier in entries}
    for identifier, lines in entries.items():
        links: set[tuple[str, str]] = set()
        for line_number, line in lines:
            match = LINK.fullmatch(line)
            if not match:
                if (re.search(r"\bsupersed\w*", line, re.I) or "~~" in line
                        or re.search(r"\breplac\w*\b.*\b(?:CINV|INV)-", line, re.I)
                        or re.match(r"\s*(?:- )?(?:\*\*)?Status:", line, re.I)):
                    errors.append(f"line {line_number}: {identifier} uses non-conforming supersession/status syntax")
                continue
            kind, target = match.groups()
            if (kind, target) in links:
                errors.append(f"line {line_number}: duplicate {kind} link on {identifier}")
            links.add((kind, target))
            if target == identifier:
                errors.append(f"line {line_number}: {identifier} cannot supersede itself")
            if target not in entries:
                errors.append(f"line {line_number}: {identifier} references missing {target}")
            if kind == "Superseded by":
                if identifier in successors:
                    errors.append(f"line {line_number}: {identifier} must have only one successor")
                successors[identifier] = target
            else:
                predecessors[identifier].add(target)

    for identifier, successor in successors.items():
        if successor in entries and identifier not in predecessors[successor]:
            errors.append(f"{identifier} names {successor}, which lacks Supersedes: {identifier}")
    for identifier, replaced in predecessors.items():
        for predecessor in sorted(replaced):
            if predecessor in entries and successors.get(predecessor) != identifier:
                errors.append(f"{identifier} names {predecessor}, which lacks Superseded by: {identifier}")

    checked: set[str] = set()
    for identifier in entries:
        path: list[str] = []
        positions: dict[str, int] = {}
        current = identifier
        while current in entries and current not in checked:
            if current in positions:
                cycle = path[positions[current]:] + [current]
                errors.append("Supersession cycle: " + " -> ".join(cycle))
                break
            positions[current] = len(path)
            path.append(current)
            if current not in successors:
                break
            current = successors[current]
        checked.update(path)

    statuses = {identifier: "superseded" if identifier in successors else "active"
                for identifier in entries}
    return statuses, errors


def main() -> None:
    statuses, errors = analyze_invariants((ROOT / "specs/INVARIANTS.md").read_text())
    if errors:
        print("Invariant checks failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    active = sum(status == "active" for status in statuses.values())
    print(f"Invariant checks passed: {active} active, {len(statuses) - active} superseded")


if __name__ == "__main__":
    main()

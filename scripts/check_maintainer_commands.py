#!/usr/bin/env python3
"""Check the bidirectional mapping between maintainer commands and repository-local skills."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOTS = ("maintainer-skills", ".agents/skills")
TARGET = re.compile(r"`((?:maintainer-skills|\.agents/skills)/[^`\n]+/SKILL\.md)`")


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        return {}
    return {
        name: value.strip().strip("\"'")
        for name, value in re.findall(r"(?m)^([\w-]+):[ \t]*([^\n]*)$", match.group(1))
    }


def check_maintainer_commands(root: Path) -> list[str]:
    errors: list[str] = []
    skills: dict[str, list[Path]] = {}
    for directory in SKILL_ROOTS:
        for path in sorted((root / directory).glob("*/SKILL.md")):
            name = path.parent.name
            skills.setdefault(name, []).append(path)
            metadata = frontmatter(path.read_text())
            if metadata.get("name") != name:
                errors.append(f"{path.relative_to(root)}: skill name must match directory {name}")
    commands = {path.stem: path for path in sorted((root / "commands").glob("*.md"))}
    for name, paths in skills.items():
        if len(paths) != 1:
            locations = ", ".join(str(path.relative_to(root)) for path in paths)
            errors.append(f"duplicate maintainer skill {name}: {locations}")
        if name not in commands:
            errors.append(f"maintainer skill {name} has no commands/{name}.md")
    for name, path in commands.items():
        text = path.read_text()
        metadata = frontmatter(text)
        for field in ("description", "argument-hint"):
            if not metadata.get(field):
                errors.append(f"{path.relative_to(root)}: missing frontmatter {field}")
        targets = TARGET.findall(text)
        if len(targets) != 1:
            errors.append(f"{path.relative_to(root)}: name exactly one explicit repository-local SKILL.md target")
        elif root / targets[0] not in skills.get(name, []):
            errors.append(f"{path.relative_to(root)}: target {targets[0]} does not resolve to skill {name}")
        if name not in skills:
            errors.append(f"command {name} has no matching maintainer skill")
    return errors


def main() -> None:
    errors = check_maintainer_commands(ROOT)
    if errors:
        print("Maintainer command checks failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Maintainer command checks passed")


if __name__ == "__main__":
    main()

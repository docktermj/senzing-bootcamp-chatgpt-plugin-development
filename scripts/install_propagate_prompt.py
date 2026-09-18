#!/usr/bin/env python3
"""Install the repository's deprecated Codex custom-prompt shim locally."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="copy the prompt into Codex home")
    parser.add_argument("--force", action="store_true", help="replace an existing differing prompt")
    args = parser.parse_args()

    source = Path(__file__).resolve().parents[1] / "commands/propagate-to-public.md"
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    target = codex_home / "prompts/propagate-to-public.md"
    if target.exists() and target.read_bytes() == source.read_bytes():
        print(f"Already installed: {target}")
        return 0
    if target.exists() and not args.force:
        parser.error(f"existing prompt differs: {target}; inspect it before using --force")
    if not args.install:
        print(f"Would install {source} -> {target}")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"Installed {target}; restart Codex or open a new chat to load /prompts:propagate-to-public")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

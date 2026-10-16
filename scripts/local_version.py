#!/usr/bin/env python3
"""Set or restore a Codex-local build suffix without changing release SemVer."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "plugins/senzing-bootcamp/.codex-plugin/plugin.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--restore", action="store_true", help="restore RELEASE_VERSION")
    mode.add_argument("--candidate", help="exact local release candidate for manual testing")
    args = parser.parse_args()
    base = (ROOT / "RELEASE_VERSION").read_text().strip()
    data = json.loads(MANIFEST.read_text())
    if args.candidate:
        if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", args.candidate):
            parser.error("--candidate must be an exact stable SemVer version")
        data["version"] = args.candidate
    elif args.restore:
        data["version"] = base
    else:
        stamp = dt.datetime.now(dt.UTC).strftime("local-%Y%m%d-%H%M%S")
        data["version"] = f"{base}+codex.{stamp}"
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
    print(data["version"])


if __name__ == "__main__":
    main()

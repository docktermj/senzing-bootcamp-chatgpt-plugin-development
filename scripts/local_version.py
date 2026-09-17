#!/usr/bin/env python3
"""Set or restore a Codex-local build suffix without changing release SemVer."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "plugins/senzing-bootcamp/.codex-plugin/plugin.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore", action="store_true", help="restore the exact upstream version")
    args = parser.parse_args()
    base = (ROOT / "UPSTREAM_VERSION").read_text().strip()
    data = json.loads(MANIFEST.read_text())
    if args.restore:
        data["version"] = base
    else:
        stamp = dt.datetime.now(dt.UTC).strftime("local-%Y%m%d-%H%M%S")
        data["version"] = f"{base}+codex.{stamp}"
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
    print(data["version"])


if __name__ == "__main__":
    main()

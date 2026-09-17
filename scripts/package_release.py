#!/usr/bin/env python3
"""Create a deterministic plugin zip after all release checks pass."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/senzing-bootcamp"


def main() -> None:
    subprocess.run(["python3", str(ROOT / "scripts/check_port.py")], check=True)
    version = (ROOT / "UPSTREAM_VERSION").read_text().strip()
    output_dir = ROOT / "dist"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / f"senzing-bootcamp-codex-plugin-{version}.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        files = (
            p for p in PLUGIN.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        )
        for path in sorted(files):
            info = zipfile.ZipInfo(path.relative_to(PLUGIN).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    print(output)


if __name__ == "__main__":
    main()

"""Run the full suite in an explicitly selected real optional-dependency environment."""

import importlib.util
import os
import sys
import unittest
from pathlib import Path


def main():
    mode = os.environ.get("CODEX_PDF_MODE")
    if mode not in {"present", "absent"}:
        raise SystemExit("Set CODEX_PDF_MODE to present or absent")
    available = importlib.util.find_spec("fpdf") is not None
    if available != (mode == "present"):
        raise SystemExit(f"fpdf2 availability does not match required {mode} environment")
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    suite = unittest.defaultTestLoader.discover(str(root / "scripts"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    rich_skips = [reason for _, reason in result.skipped if "fpdf2 is absent" in reason]
    if mode == "absent" and not rich_skips:
        raise SystemExit("Absent environment must exercise a stated fpdf2 skip; no rich-path guard was measured")
    if mode == "present" and rich_skips:
        raise SystemExit("Present environment unexpectedly skipped the rich PDF renderer")
    print(f"Optional PDF environment: {mode}; tests={result.testsRun}; skips={len(result.skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

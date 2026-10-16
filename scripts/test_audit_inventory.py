"""Audit snapshot and coverage accounting tests, not tests of semantic correctness."""

import copy
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import audit_inventory as audit


class AuditInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.contract = {
            "output_root": "plugins/demo", "overlays": [{"source": "port/overlay", "destination": "."}],
            "invariant_disposition_register": {"preserved_restated": [], "discounted": []},
        }
        self.write("tools/bootcamp-transform/contract.yaml", json.dumps(self.contract).encode())
        for name in ("specs/INVARIANTS.md", "RELEASE_VERSION", "PARENT_VERSION", "PARENT_COMMIT"):
            self.write(name, b"fixture\n")
        self.write("plugins/demo/skills/start/SKILL.md", b"Guidance\n")
        self.write("plugins/demo/.mcp.json", b"{}\n")
        self.write("plugins/demo/docs/host.md", b"Host contract\n")
        self.write("port/overlay/docs/host.md", b"Host contract\n")
        self.write("plugins/demo/docs/image.png", b"\xff\0")
        self.build = {"files": {name: {"output": audit.sha256(data)} for name, data in (
            ("skills/start/SKILL.md", b"Guidance\n"), (".mcp.json", b"{}\n"),
            ("docs/host.md", b"Host contract\n"), ("docs/image.png", b"\xff\0"),
        )}}
        self.write(".build-manifest.json", json.dumps(self.build).encode())

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def review(self, snapshot):
        return {
            "snapshot_sha256": snapshot["snapshot_sha256"],
            "files": [{"path": item["path"], "sha256": item["sha256"], "status": "reviewed",
                       "evidence": "Fixture review observation"} for item in snapshot["files"]],
            "checks": [{"id": identifier, "status": "reviewed", "evidence": "Fixture cross-file observation"}
                       for identifier in audit.CHECKS],
            "findings": [],
        }

    def test_inventory_includes_hidden_binary_and_overlay_files_without_writes(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        snapshot = audit.inventory(self.root)
        self.assertEqual(len(snapshot["files"]), 4)
        by_path = {item["path"]: item for item in snapshot["files"]}
        self.assertEqual(by_path["plugins/demo/docs/host.md"]["layer"], "overlay")
        self.assertEqual(by_path["plugins/demo/docs/image.png"]["kind"], "binary")
        self.assertEqual(snapshot["structural_alerts"], [])
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)

    def test_missing_overlay_output_and_changed_build_are_visible(self):
        (self.root / "plugins/demo/docs/host.md").unlink()
        self.write("plugins/demo/.mcp.json", b"changed")
        alerts = audit.inventory(self.root)["structural_alerts"]
        self.assertTrue(any("Overlay contribution missing" in alert for alert in alerts))
        self.assertTrue(any("differs from build manifest" in alert for alert in alerts))

    def test_caches_are_excluded_but_unexpected_payload_is_reported(self):
        self.write("plugins/demo/__pycache__/cache.pyc", b"cache")
        self.write("plugins/demo/extra.md", b"unrecorded")
        snapshot = audit.inventory(self.root)
        self.assertFalse(any("__pycache__" in item["path"] for item in snapshot["files"]))
        self.assertTrue(any("extra.md" in alert for alert in snapshot["structural_alerts"]))

    def test_complete_coverage_is_distinct_from_readiness(self):
        snapshot = audit.inventory(self.root)
        self.assertEqual(audit.validate_coverage(snapshot, self.review(snapshot)), [])
        self.assertNotIn("production_ready", snapshot)
        self.assertTrue(audit.validate_coverage(snapshot, {}))

    def test_missing_stale_and_deferred_file_reviews_fail(self):
        snapshot = audit.inventory(self.root)
        review = self.review(snapshot)
        for alteration in ("missing", "stale", "deferred"):
            changed = copy.deepcopy(review)
            if alteration == "missing":
                changed["files"].pop()
            elif alteration == "stale":
                changed["files"][0]["sha256"] = "outdated"
            else:
                changed["files"][0]["status"] = "deferred"
            with self.subTest(alteration=alteration):
                self.assertTrue(audit.validate_coverage(snapshot, changed))
        self.write("port/overlay/docs/host.md", b"new host contract")
        self.assertTrue(audit.validate_coverage(audit.inventory(self.root), review))

    def test_duplicate_and_unreviewed_checks_fail(self):
        snapshot = audit.inventory(self.root)
        review = self.review(snapshot)
        review["checks"].append(review["checks"][0])
        review["checks"][1]["status"] = "passed"
        self.assertTrue(audit.validate_coverage(snapshot, review))

    def test_unexpressible_check_requires_register_entry(self):
        snapshot = audit.inventory(self.root)
        review = self.review(snapshot)
        review["checks"].append({"id": "parent-hook-check", "invariant": "INV-158",
                                 "status": "unexpressible", "evidence": "Host construction is unavailable"})
        self.assertTrue(audit.validate_coverage(snapshot, review))
        snapshot["invariant_disposition_register"]["preserved_restated"].append({
            "id": "INV-158", "mechanism": "Host-native alternative",
            "audit_limitations": [{"check": "parent-hook-check", "reason": "Host construction is unavailable"}],
        })
        self.assertEqual(audit.validate_coverage(snapshot, review), [])

    def test_finding_reviews_require_routing_and_real_disposition_fields(self):
        snapshot = audit.inventory(self.root)
        review = self.review(snapshot)
        review["files"][0].update(status="finding", finding_id="finding-1")
        self.assertTrue(audit.validate_coverage(snapshot, review))
        review["findings"].append({"id": "finding-1", "route": "local", "reason": "Overlay behavior",
                                   "source": "port/overlay/docs/host.md", "evidence": "Contradictory instructions",
                                   "disposition": {"kind": "blocked", "reason": "Issue API is unavailable"}})
        self.assertEqual(audit.validate_coverage(snapshot, review), [])
        review["findings"][0]["route"] = "unknown"
        self.assertTrue(audit.validate_coverage(snapshot, review))

    def test_symlink_inputs_are_not_silently_omitted(self):
        (self.root / "plugins/demo/link").symlink_to(self.root / "port/overlay", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            audit.inventory(self.root)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Contract-engine tests; run with python3 -m unittest scripts.test_sync_parent."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import sync_parent as sync


def tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class TransformationContractTests(unittest.TestCase):
    def test_non_tag_references_are_rejected_before_reading_or_writing(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for tag in ("main", "HEAD", "0.5.3-rc.1"):
                with self.subTest(tag=tag):
                    with self.assertRaisesRegex(SystemExit, "stable SemVer tag"):
                        sync.build(root / "missing-source", tag, repository_root=root / "output")
                    self.assertFalse((root / "output").exists())

    def test_cli_rejects_non_tag_references(self):
        for tag in ("main", "HEAD"):
            for source_args in ([], ["--source-dir", "missing-source"]):
                with self.subTest(tag=tag, source_args=source_args):
                    result = subprocess.run(
                        [sys.executable, sync.__file__, "--tag", tag, *source_args],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("stable SemVer tag", result.stderr)

    def test_parent_child_governance_skills_keep_cross_repo_writes_scoped(self):
        root = Path(sync.__file__).resolve().parents[1]
        parity = (root / "maintainer-skills/parity-check/SKILL.md").read_text()
        escalation = (root / "maintainer-skills/escalate-to-parent/SKILL.md").read_text()
        feedback = (root / "maintainer-skills/feedback-to-issues/SKILL.md").read_text()
        self.assertIn("PARENT_VERSION", parity)
        self.assertIn("tagged", parity)
        self.assertIn("only workflow authorized", escalation)
        self.assertIn("never writes to another repository", feedback)

    def test_uniform_framework_covers_all_nine_components(self):
        root = Path(sync.__file__).resolve().parents[1]
        framework = (root / "docs/UNIFORM_PORTING_FRAMEWORK.md").read_text()
        for component in ("A. Tagged provenance", "B. Declarative contract", "C. Invariant dispositions",
                          "D. Host-native invariants", "E. Mechanical checks", "F. Reconciliation",
                          "G. Recorded host tests", "H. Determinism", "I. Cross-repo governance"):
            self.assertIn(component, framework)

    def test_reconciliation_reports_an_overlay_conflict(self):
        report = sync.reconciliation_report(
            {"files": {"hooks/hooks.json": {"generated": "old", "output": "old"}}},
            {"hooks/hooks.json": "old"},
            {"hooks/hooks.json": "new"},
            {"hooks/hooks.json"},
        )
        self.assertEqual(report, [("conflict", "hooks/hooks.json")])

    def test_new_upstream_version_requires_invariant_register_review(self):
        contract = {"invariant_disposition_register": {"source_version": "1.2.3"}}
        sync.validate_invariant_register("1.2.3", contract)
        with self.assertRaisesRegex(sync.ContractError, "E_INVARIANT_REVIEW"):
            sync.validate_invariant_register("1.2.4", contract)

    def test_repository_contract_is_the_only_home_for_transform_rules(self):
        contract = sync.load_contract()
        updater = Path(sync.__file__).read_text()
        self.assertNotIn("REPLACEMENTS =", updater)
        self.assertTrue(contract["rules"])
        self.assertTrue(contract["text_transforms"])
        self.assertTrue(contract["overlays"])
        self.assertTrue(contract["generated_artifacts"])

    def test_unmatched_upstream_file_names_itself_and_writes_nothing(self):
        version = sync.load_contract()["invariant_disposition_register"]["source_version"]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            plugin = source / "plugins/senzing-bootcamp"
            manifest = plugin / ".claude-plugin/plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"version": version}))
            (plugin / "unexpected.txt").write_text("new upstream file")

            output = root / "repository/plugins/senzing-bootcamp"
            output.mkdir(parents=True)
            sentinel = output / "sentinel.txt"
            sentinel.write_text("unchanged")

            with self.assertRaisesRegex(sync.ContractError, "E_UNMATCHED_FILE: unexpected.txt"):
                sync.build(source, version, repository_root=root / "repository")

            self.assertEqual(sentinel.read_text(), "unchanged")
            self.assertFalse((root / "repository/PARENT_VERSION").exists())
            self.assertFalse((root / "repository/PARENT_COMMIT").exists())

    def test_execution_is_deterministic_and_overlay_wins(self):
        contract = {
            "contract_version": 1,
            "rules": [
                {"id": "copy", "kind": "copy", "match": ["skills/**"]},
                {"id": "ignore", "kind": "ignore", "match": ["commands/**"]},
            ],
            "text_transforms": [
                {
                    "id": "host-language",
                    "match": ["*.md"],
                    "operations": [
                        {"kind": "literal", "old": "Claude plugin", "new": "Codex plugin"}
                    ],
                }
            ],
            "generated_artifacts": [
                {"path": "generated.json", "format": "json", "value": {"version": "${RELEASE_VERSION}"}}
            ],
            "overlays": [{"source": "overlay", "destination": "."}],
        }
        variables = {"PARENT_VERSION": "1.2.3", "PARENT_COMMIT": "a" * 40, "RELEASE_VERSION": "4.0.0"}
        with TemporaryDirectory() as directory:
            root = Path(directory)
            upstream = root / "upstream"
            (upstream / "skills/demo").mkdir(parents=True)
            (upstream / "skills/demo/SKILL.md").write_text("Claude plugin\n")
            (upstream / "commands").mkdir()
            (upstream / "commands/start.md").write_text("ignored\n")
            (root / "overlay").mkdir()
            (root / "overlay/generated.json").write_text("overlay wins\n")
            plan = sync.plan_upstream(upstream, contract)

            first = root / "first"
            second = root / "second"
            sync.execute_contract(upstream, first, root, contract, plan, variables)
            sync.execute_contract(upstream, second, root, contract, plan, variables)

            self.assertEqual(tree_bytes(first), tree_bytes(second))
            self.assertEqual((first / "skills/demo/SKILL.md").read_text(), "Codex plugin\n")
            self.assertEqual((first / "generated.json").read_text(), "overlay wins\n")
            self.assertFalse((first / "commands/start.md").exists())

    def test_parent_rebuild_preserves_independent_local_release_version(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source_manifest = source / "plugins/senzing-bootcamp/.claude-plugin/plugin.json"
            source_manifest.parent.mkdir(parents=True)
            source_manifest.write_text(json.dumps({"version": "1.2.3"}))
            repository = root / "repository"
            repository.mkdir()
            (repository / "RELEASE_VERSION").write_text("4.0.0\n")
            contract = {
                "contract_version": 1,
                "upstream": {"source_root": "plugins/senzing-bootcamp", "version_file": ".claude-plugin/plugin.json"},
                "invariant_disposition_register": {"source_version": "1.2.3"},
                "rules": [{"id": "ignore", "kind": "ignore", "match": [".claude-plugin/**"], "reason": "generated"}],
                "output_root": "plugins/senzing-bootcamp",
                "generated_artifacts": [{"path": ".codex-plugin/plugin.json", "format": "json",
                                         "value": {"version": "${RELEASE_VERSION}"}}],
                "provenance_artifacts": [{"path": "PARENT_VERSION", "value": "${PARENT_VERSION}\n"}],
            }
            contract_path = root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            for iteration in range(2):
                with self.subTest(iteration=iteration):
                    self.assertEqual(sync.build(source, "1.2.3", repository_root=repository,
                                                contract_path=contract_path), "4.0.0")
                    self.assertEqual((repository / "PARENT_VERSION").read_text(), "1.2.3\n")
                    built = json.loads((repository / "plugins/senzing-bootcamp/.codex-plugin/plugin.json").read_text())
                    self.assertEqual(built["version"], "4.0.0")
                    if iteration == 0:
                        first = tree_bytes(repository)
                    else:
                        self.assertEqual(tree_bytes(repository), first)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Contract-engine tests; run with python3 -m unittest scripts.test_sync_upstream."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import sync_upstream as sync


def tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class TransformationContractTests(unittest.TestCase):
    def test_parent_child_governance_skills_keep_cross_repo_writes_scoped(self):
        root = Path(sync.__file__).resolve().parents[1]
        parity = (root / "maintainer-skills/parity-check/SKILL.md").read_text()
        escalation = (root / "maintainer-skills/escalate-to-parent/SKILL.md").read_text()
        feedback = (root / "maintainer-skills/feedback-to-issues/SKILL.md").read_text()
        self.assertIn("UPSTREAM_VERSION", parity)
        self.assertIn("tagged", parity)
        self.assertIn("only workflow authorized", escalation)
        self.assertIn("never writes to another repository", feedback)

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
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            plugin = source / "plugins/senzing-bootcamp"
            manifest = plugin / ".claude-plugin/plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"version": "0.5.3"}))
            (plugin / "unexpected.txt").write_text("new upstream file")

            output = root / "repository/plugins/senzing-bootcamp"
            output.mkdir(parents=True)
            sentinel = output / "sentinel.txt"
            sentinel.write_text("unchanged")

            with self.assertRaisesRegex(sync.ContractError, "E_UNMATCHED_FILE: unexpected.txt"):
                sync.build(source, "0.5.3", repository_root=root / "repository")

            self.assertEqual(sentinel.read_text(), "unchanged")
            self.assertFalse((root / "repository/UPSTREAM_VERSION").exists())
            self.assertFalse((root / "repository/UPSTREAM_COMMIT").exists())

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
                {"path": "generated.json", "format": "json", "value": {"version": "${UPSTREAM_VERSION}"}}
            ],
            "overlays": [{"source": "overlay", "destination": "."}],
        }
        variables = {"UPSTREAM_VERSION": "1.2.3", "UPSTREAM_COMMIT": "a" * 40}
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


if __name__ == "__main__":
    unittest.main()

"""Synthetic evidence records test accounting only; these tests do not run Codex conversations."""

import copy
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import dry_run_evidence as evidence


class DryRunEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.skill = "plugins/senzing-bootcamp/skills/fixture/SKILL.md"
        path = self.root / self.skill
        path.parent.mkdir(parents=True)
        path.write_text("👉 Choose the first option?\n👉 Choose the next option?\n")
        manifest = self.root / "plugins/senzing-bootcamp/.codex-plugin/plugin.json"
        manifest.parent.mkdir()
        manifest.write_text(json.dumps({"version": "0.0.1"}))
        for name in ("RELEASE_VERSION", "PARENT_VERSION", "PARENT_COMMIT", "docs/test-checklist.md"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture")
        self.record = {
            "snapshot_sha256": evidence.snapshot(self.root),
            "environment": {"codex_build": "fixture", "platform": "fixture", "workspace": "fixture",
                            "tested_at": "2026-10-16", "mcp_server_version": "fixture", "installed_plugin_version": "0.0.1"},
            "phases": [{"id": identifier, "checks": [self.check(name, origin) for name, origin in checks.items()]}
                       for identifier, checks in evidence.PHASES], "findings": [],
        }

    def check(self, name, origin):
        check = {"id": name, "status": "PASS", "evidence_type": origin,
                 "evidence": [{"reference": "synthetic-test-fixture", "observed": "Fixture observation"}]}
        if origin == "live_mcp":
            check.update(tool="get_capabilities" if name == "capabilities" else "fixture-owning-route",
                         request={}, response_summary="Fixture response")
        if name == "turn-cycle":
            check["turns"] = [
                {"input": "yes", "processed_answer": "Fixture answer processed", "transcript_ref": "fixture",
                 "question": question, "options": ["1. Option"], "final": question + "\n1. Option",
                 "intermediate_yields": False, "automatic_steps": ["Fixture automatic work"],
                 "commentary": ["Fixture working update"], "question_match_observation": "Fixture origin matches",
                 "question_origin": {"path": self.skill, "line": number, "template": question}}
                for number, question in enumerate(("👉 Choose the first option?", "👉 Choose the next option?"), 1)
            ]
        return check

    def test_complete_record_is_structurally_valid_not_proof_of_observations(self):
        result = evidence.validate_record(self.root, self.record)
        self.assertTrue(result["record_valid"])
        self.assertTrue(result["dry_run_passed"])
        self.assertIn("not the truth", result["assurance"])

    def test_direct_script_cannot_substitute_for_host_observations(self):
        self.record["phases"][1]["checks"][1]["evidence_type"] = "direct_script"
        result = evidence.validate_record(self.root, self.record)
        self.assertFalse(result["dry_run_passed"])
        self.assertTrue(any("codex_host" in error for error in result["errors"]))

    def test_failed_mcp_blocks_dependent_phases(self):
        self.record["phases"][0]["checks"][0]["status"] = "FAIL"
        result = evidence.validate_record(self.root, self.record)
        self.assertEqual(result["phases"]["mcp"], "FAIL")
        self.assertTrue(any("prerequisite" in error for error in result["errors"]))

    def test_failed_run_with_unexecuted_dependents_is_a_valid_nonpass_record(self):
        self.record["phases"][0]["checks"][0]["status"] = "FAIL"
        for phase in self.record["phases"][1:]:
            for check in phase["checks"]:
                check.update(status="NOT_RUN", reason="Live MCP prerequisite failed")
        result = evidence.validate_record(self.root, self.record)
        self.assertTrue(result["record_valid"])
        self.assertFalse(result["dry_run_passed"])

    def test_missing_trace_or_invented_question_template_cannot_pass(self):
        record = copy.deepcopy(self.record)
        record["phases"][0]["checks"][0]["evidence"] = []
        self.assertFalse(evidence.validate_record(self.root, record)["dry_run_passed"])
        record = copy.deepcopy(self.record)
        record["phases"][2]["checks"][0]["turns"][0]["question_origin"]["template"] = "Invented source"
        self.assertFalse(evidence.validate_record(self.root, record)["dry_run_passed"])

    def test_unavailable_host_phase_is_advisory_never_pass(self):
        for phase in self.record["phases"][1:]:
            for check in phase["checks"]:
                check.update(status="ADVISORY", reason="Host observation unavailable",
                             impact="Live behavior remains unverified", follow_up="Run in supported host")
        result = evidence.validate_record(self.root, self.record)
        self.assertTrue(result["record_valid"])
        self.assertFalse(result["dry_run_passed"])
        self.assertEqual(result["phases"]["conversation"], "ADVISORY")

    def test_unavailable_mcp_is_a_blocker(self):
        check = self.record["phases"][0]["checks"][0]
        check.update(status="ADVISORY", reason="Network unavailable", impact="No live contracts", follow_up="Retry")
        self.assertFalse(evidence.validate_record(self.root, self.record)["record_valid"])

    def test_status_only_final_missing_origin_and_intermediate_yield_fail(self):
        baseline = self.record["phases"][2]["checks"][0]["turns"][0]
        for change in ({"final": "Setup completed."}, {"intermediate_yields": True},
                       {"commentary": []}, {"question_origin": {"path": "missing", "line": 1}},
                       {"final": baseline["final"] + "\nTell me when to continue."}):
            record = copy.deepcopy(self.record)
            record["phases"][2]["checks"][0]["turns"][0].update(change)
            with self.subTest(change=change):
                self.assertFalse(evidence.validate_record(self.root, record)["dry_run_passed"])

    def test_missing_check_stale_snapshot_and_wrong_installed_version_fail(self):
        self.record["phases"][0]["checks"].pop()
        self.record["environment"]["installed_plugin_version"] = "other-version"
        (self.root / self.skill).write_text("Changed shipped question")
        result = evidence.validate_record(self.root, self.record)
        self.assertFalse(result["dry_run_passed"])
        self.assertTrue(any("stale" in error for error in result["errors"]))
        self.assertTrue(any("installed" in error for error in result["errors"]))

    def test_duplicate_phases_and_unrouted_findings_fail(self):
        self.record["phases"].append(self.record["phases"][0])
        self.record["findings"].append({"evidence": "Observed defect"})
        result = evidence.validate_record(self.root, self.record)
        self.assertFalse(result["record_valid"])
        self.assertTrue(any("Duplicate phase" in error for error in result["errors"]))
        self.assertTrue(any("routing" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()

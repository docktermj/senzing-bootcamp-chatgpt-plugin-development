"""Read-only snapshot comparison and repeat-filing evidence tests."""

import unittest
from unittest.mock import patch

from scripts import propagate_to_public as propagation
from scripts import retrofit_from_public as retrofit
from scripts import test_propagate_to_public as propagation_tests


class RetrofitTests(unittest.TestCase):
    def setUp(self):
        self.fixture = propagation_tests.PropagationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.development = self.fixture.source
        propagation.git(self.development, "remote", "add", "origin", f"git@github.com:{propagation.DEVELOPMENT_SLUG}.git")
        self.public = self.fixture.public_checkout()
        payload, _ = propagation.tagged_payload("0.5.3")
        (self.public / "plugins/senzing-bootcamp/obsolete.md").unlink()
        for name, data in payload.items():
            path = self.public / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.commit_public()

    def commit_public(self):
        propagation.git(self.public, "add", ".")
        propagation.git(self.public, "commit", "-m", "public review")

    def report(self):
        before_development = self.fixture.files(self.development)
        before_public = self.fixture.files(self.public)
        original_git = propagation.git

        def read_only(repo, *arguments, **kwargs):
            self.assertTrue(arguments[0] in {"rev-parse", "ls-tree", "cat-file"}
                            or arguments[:2] == ("remote", "get-url"), arguments)
            return original_git(repo, *arguments, **kwargs)

        with patch.object(propagation, "git", side_effect=read_only):
            result = retrofit.report(self.development, self.public)
        self.assertEqual(self.fixture.files(self.development), before_development)
        self.assertEqual(self.fixture.files(self.public), before_public)
        return result

    def test_expected_public_rewrites_are_not_divergence(self):
        result = self.report()
        self.assertEqual(result["findings"], [])
        self.assertEqual(len(result["development_commit"]), 40)
        self.assertEqual(len(result["public_commit"]), 40)

    def test_added_removed_and_modified_payload_files_are_reported(self):
        (self.public / "plugins/senzing-bootcamp/extra.md").write_text("Public addition\n")
        (self.public / "plugins/senzing-bootcamp/.mcp.json").unlink()
        (self.public / "README.md").write_text("Public correction\n")
        self.commit_public()
        findings = {item["path"]: item for item in self.report()["findings"]}
        self.assertEqual(findings["README.md"]["change"], "modified")
        self.assertEqual(findings["plugins/senzing-bootcamp/.mcp.json"]["change"], "public-removed")
        self.assertEqual(findings["plugins/senzing-bootcamp/extra.md"]["change"], "public-added")
        self.assertIn("Public correction", findings["README.md"]["diff"])

    def test_committed_snapshot_does_not_read_dirty_working_files(self):
        (self.public / "README.md").write_text("Uncommitted public edit")
        (self.development / "README.md").write_text("Uncommitted development edit")
        self.assertEqual(self.report()["findings"], [])

    def test_public_governance_files_are_outside_propagation_scope(self):
        (self.public / ".github/workflow.yml").write_text("Public workflow change")
        self.commit_public()
        self.assertEqual(self.report()["findings"], [])

    def test_file_mode_changes_are_reported(self):
        path = "plugins/senzing-bootcamp/scripts/socratic-controller.py"
        propagation.git(self.public, "update-index", "--chmod=+x", path)
        propagation.git(self.public, "commit", "-m", "executable correction")
        findings = self.report()["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["path"], path)
        self.assertNotEqual(findings[0]["expected_mode"], findings[0]["public_mode"])

    def test_binary_evidence_and_fingerprint_are_stable(self):
        first = retrofit.compare_payloads({"image.png": b"before"}, {"image.png": b"\xff\0"})[0]
        second = retrofit.compare_payloads({"image.png": b"new baseline"}, {"image.png": b"\xff\0"})[0]
        self.assertIn("Binary", first["diff"])
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertNotEqual(first["expected_sha256"], second["expected_sha256"])

    def test_matching_issues_includes_open_and_closed_without_automatically_refiling(self):
        finding = retrofit.compare_payloads({"README.md": b"before"}, {"README.md": b"after"})[0]
        issues = [{"url": "open-url", "state": "open", "body": finding["fingerprint"]},
                  {"url": "closed-url", "state": "closed", "body": finding["fingerprint"]},
                  {"url": "unrelated", "body": None}]
        matches = retrofit.matching_issues(finding, issues)
        self.assertEqual([item["url"] for item in matches], ["open-url", "closed-url"])

    def test_wrong_repository_and_unsupported_file_types_block(self):
        with self.assertRaisesRegex(ValueError, "separate"):
            retrofit.report(self.development, self.development)
        target = self.public / "plugins/senzing-bootcamp/unsafe"
        target.symlink_to("README.md")
        self.commit_public()
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            retrofit.report(self.development, self.public)
        propagation.git(self.public, "remote", "set-url", "origin", "https://github.com/example/other")
        with self.assertRaisesRegex(ValueError, "origin"):
            retrofit.report(self.development, self.public)


if __name__ == "__main__":
    unittest.main()

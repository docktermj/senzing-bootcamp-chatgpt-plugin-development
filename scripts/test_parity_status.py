"""Closure eligibility tests using real Git commit and tag ancestry."""

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.parity_status import evaluate, git, landed_provenance


class ParityStatusTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.parent = self.root / "parent"
        self.parent.mkdir()
        git(self.parent, "init")
        git(self.parent, "config", "user.email", "test@example.com")
        git(self.parent, "config", "user.name", "Test")
        git(self.parent, "config", "commit.gpgsign", "false")
        git(self.parent, "config", "tag.gpgsign", "false")
        self.payload = self.parent / "plugins/senzing-bootcamp/fix.txt"
        self.payload.parent.mkdir(parents=True)
        self.payload.write_text("before")
        self.commit("before")
        git(self.parent, "tag", "1.0.0")
        self.payload.write_text("fixed")
        self.closing = self.commit("fix")
        git(self.parent, "tag", "-a", "1.0.1", "-m", "release")
        self.issue = {"state": "closed", "state_reason": "completed", "closing_commit": self.closing}
        self.landed = {"version": "1.0.1", "commit": self.closing}

    def commit(self, message):
        git(self.parent, "add", ".")
        git(self.parent, "commit", "-m", message)
        return git(self.parent, "rev-parse", "HEAD")

    def status(self, **changes):
        arguments = {"issue": self.issue, "tag": "1.0.1", "parent": self.parent,
                     "source": self.parent, "landed": self.landed, **changes}
        return evaluate(**arguments)["status"]

    def test_landed_tagged_fix_is_ready_and_comment_names_tag(self):
        result = evaluate(self.issue, "1.0.1", self.parent, self.parent, self.landed)
        self.assertEqual(result["status"], "ready_to_close")
        self.assertIn("1.0.1", result["comment"])
        self.assertIn(self.closing, result["comment"])

    def test_closed_parent_without_released_fix_stays_open(self):
        self.assertEqual(self.status(tag="1.0.0"), "awaiting_release")

    def test_released_fix_without_landing_stays_open(self):
        self.assertEqual(self.status(landed={**self.landed, "version": "1.0.0"}), "awaiting_landing")

    def test_closing_commit_on_another_branch_does_not_qualify(self):
        git(self.parent, "checkout", "--detach", "1.0.0")
        self.payload.write_text("different fix")
        other_commit = self.commit("other fix")
        self.assertEqual(self.status(issue={**self.issue, "closing_commit": other_commit}), "awaiting_release")

    def test_declined_fix_requires_human(self):
        self.assertEqual(self.status(issue={**self.issue, "state_reason": "not_planned"}), "human_decision")

    def test_reopened_parent_stays_open(self):
        self.assertEqual(self.status(issue={**self.issue, "state": "open"}), "awaiting_parent")

    def test_missing_or_unknown_evidence_blocks(self):
        for closing in ("", "a" * 40):
            with self.subTest(closing=closing):
                self.assertEqual(self.status(issue={**self.issue, "closing_commit": closing}), "blocked")
        self.assertEqual(self.status(issue={**self.issue, "state_reason": "unknown"}), "blocked")
        self.assertEqual(self.status(landed={**self.landed, "commit": "b" * 40}), "blocked")

    def test_moving_and_missing_tags_block(self):
        for tag in ("main", "HEAD", "1.0.1-rc.1", "9.9.9"):
            with self.subTest(tag=tag):
                self.assertEqual(self.status(tag=tag), "blocked")

    def test_different_production_payload_blocks(self):
        source = self.root / "production"
        subprocess.run(["git", "clone", str(self.parent), str(source)], check=True, capture_output=True)
        git(source, "-c", "tag.gpgsign=false", "tag", "-f", "1.0.1", "1.0.0")
        self.assertEqual(self.status(source=source), "blocked")

    def test_landing_reads_remote_main_not_feature_worktree(self):
        (self.parent / "PARENT_VERSION").write_text("1.0.1\n")
        (self.parent / "PARENT_COMMIT").write_text(self.closing + "\n")
        (self.parent / "RELEASE_VERSION").write_text("2.0.0\n")
        (self.parent / ".build-manifest.json").write_text(json.dumps({
            "upstream_version": "1.0.1", "upstream_commit": self.closing,
            "release_version": "2.0.0",
        }))
        plugin_manifest = self.parent / "plugins/senzing-bootcamp/.codex-plugin/plugin.json"
        plugin_manifest.parent.mkdir()
        plugin_manifest.write_text(json.dumps({"version": "2.0.0"}))
        landed_commit = self.commit("landed")
        git(self.parent, "update-ref", "refs/remotes/origin/main", landed_commit)
        (self.parent / "PARENT_VERSION").write_text("9.9.9")
        self.assertEqual(landed_provenance(self.parent), self.landed)
        plugin_manifest.write_text(json.dumps({"version": "9.9.9"}))
        inconsistent = self.commit("inconsistent metadata")
        git(self.parent, "update-ref", "refs/remotes/origin/main", inconsistent)
        with self.assertRaisesRegex(ValueError, "disagree"):
            landed_provenance(self.parent)


if __name__ == "__main__":
    unittest.main()

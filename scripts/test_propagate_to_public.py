#!/usr/bin/env python3
"""Focused release-payload guard tests; run with python3 -m unittest scripts.test_propagate_to_public."""

import unittest
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import propagate_to_public as release


class PropagationTests(unittest.TestCase):
    def test_remote_slug_requires_exact_github_repository(self):
        self.assertEqual(
            release.remote_slug("git@github.com:Senzing/senzing-bootcamp-chatgpt-plugin.git"),
            release.PUBLIC_SLUG,
        )
        self.assertEqual(
            release.remote_slug("https://github.com/Senzing/senzing-bootcamp-chatgpt-plugin-development.git"),
            "Senzing/senzing-bootcamp-chatgpt-plugin-development",
        )
        self.assertEqual(release.remote_slug("/tmp/unrelated"), "")

    def test_tagged_release_is_public_only_and_versioned(self):
        payload, commit = release.tagged_payload("0.5.3")
        self.assertEqual(len(commit), 40)
        self.assertTrue(release.REQUIRED <= payload.keys())
        self.assertTrue(
            all(path in {"README.md", release.MARKETPLACE} or path.startswith(release.PLUGIN)
                for path in payload)
        )
        self.assertNotIn(release.DEVELOPMENT_SLUG.encode(), b"\n".join(payload.values()))

    def test_branch_name_is_not_a_release(self):
        with self.assertRaisesRegex(ValueError, "SemVer"):
            release.tagged_payload("main")

    def test_british_spelling_blocks_release(self):
        payload, _ = release.tagged_payload("0.5.3")
        payload["README.md"] += b"\nThe colour of the diagram.\n"
        with self.assertRaisesRegex(ValueError, "British spelling"):
            release.validate_payload(payload)

    def test_development_reference_blocks_release(self):
        payload, _ = release.tagged_payload("0.5.3")
        payload["README.md"] += release.DEVELOPMENT_SLUG.encode()
        with self.assertRaisesRegex(ValueError, "development repository"):
            release.validate_payload(payload)

    def test_deletions_are_scoped_to_plugin_payload(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugins/senzing-bootcamp").mkdir(parents=True)
            (root / "plugins/senzing-bootcamp/obsolete.md").write_text("old")
            (root / ".github").mkdir()
            (root / ".github/workflow.yml").write_text("keep")
            _, deleted = release.changes(root, {"README.md": b"public"})
            self.assertEqual(deleted, ["plugins/senzing-bootcamp/obsolete.md"])
            self.assertTrue((root / ".github/workflow.yml").exists())

    def test_destination_requires_named_checked_out_review_branch(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "remote", "add", "origin",
                            "git@github.com:Senzing/senzing-bootcamp-chatgpt-plugin.git"],
                           check=True, capture_output=True)
            with self.assertRaisesRegex(ValueError, "never main"):
                release.destination(root, "main", False)
            with self.assertRaisesRegex(ValueError, "review branch 3-docktermj-1"):
                release.destination(root, "3-docktermj-1", False)


if __name__ == "__main__":
    unittest.main()

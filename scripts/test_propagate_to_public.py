#!/usr/bin/env python3
"""Focused release-payload guard tests; run with python3 -m unittest scripts.test_propagate_to_public."""

import unittest
import subprocess
import contextlib
import io
import json
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import propagate_to_public as release


class PropagationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.initialize(self.source, "development")
        payload = {path: b"fixture\n" for path in release.REQUIRED}
        payload["plugins/senzing-bootcamp/.codex-plugin/plugin.json"] = json.dumps({
            "version": "0.5.3", "homepage": f"https://github.com/{release.DEVELOPMENT_SLUG}",
            "repository": f"https://github.com/{release.DEVELOPMENT_SLUG}",
        }).encode()
        payload[release.MARKETPLACE] = json.dumps({
            "name": "development", "interface": {"displayName": "Development"},
            "plugins": [{"source": {"source": "local", "path": "./plugins/senzing-bootcamp"}}],
        }).encode()
        payload["README.md"] = f"https://github.com/{release.DEVELOPMENT_SLUG}\n".encode()
        for name, data in payload.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        release.git(self.source, "add", ".")
        release.git(self.source, "commit", "-m", "tagged fixture")
        release.git(self.source, "tag", "0.5.3")
        source_patch = patch.object(release, "SOURCE", self.source)
        source_patch.start()
        self.addCleanup(source_patch.stop)

    def initialize(self, repo, branch):
        release.git(repo, "init", "-b", branch)
        release.git(repo, "config", "user.name", "Test")
        release.git(repo, "config", "user.email", "test@example.com")
        release.git(repo, "config", "commit.gpgsign", "false")
        release.git(repo, "config", "tag.gpgsign", "false")

    def public_checkout(self):
        repo = self.root / "public"
        repo.mkdir()
        self.initialize(repo, "22-docktermj-1")
        for name in ("README.md", "LICENSE", ".github/workflow.yml",
                     "plugins/senzing-bootcamp/obsolete.md"):
            path = repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("original\n")
        release.git(repo, "add", ".")
        release.git(repo, "commit", "-m", "public fixture")
        release.git(repo, "tag", "existing")
        release.git(repo, "remote", "add", "origin", f"git@github.com:{release.PUBLIC_SLUG}.git")
        return repo

    def run_operation(self, repo, *options):
        original_git = release.git

        def read_only_git(checkout, *arguments, **kwargs):
            permitted = (
                arguments[0] in {"rev-parse", "ls-tree", "show", "status", "check-ref-format"}
                or arguments[:2] in {("tag", "--list"), ("branch", "--show-current"),
                                      ("remote", "get-url")}
            )
            self.assertTrue(permitted, f"Propagation attempted a mutating or network Git call: {arguments}")
            return original_git(checkout, *arguments, **kwargs)

        arguments = ["propagate-to-public", "--tag", "0.5.3", "--public-repo", str(repo),
                     "--branch", "22-docktermj-1", *options]
        with patch("sys.argv", arguments), patch.object(release, "git", side_effect=read_only_git):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return release.main()

    def files(self, root):
        return {path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*") if path.is_file()}

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
                release.destination(root, "main")
            with self.assertRaisesRegex(ValueError, "review branch 3-docktermj-1"):
                release.destination(root, "3-docktermj-1")

    def test_preview_leaves_working_tree_index_and_refs_unchanged(self):
        repo = self.public_checkout()
        before = self.files(repo)
        source_before = self.files(self.source)
        self.assertEqual(self.run_operation(repo), 0)
        self.assertEqual(self.files(repo), before)
        self.assertEqual(self.files(self.source), source_before)

    def test_apply_updates_only_payload_and_never_stages_commits_or_contacts_remote(self):
        repo = self.public_checkout()
        before = self.files(repo)
        source_before = self.files(self.source)
        payload, _ = release.tagged_payload("0.5.3")
        self.assertEqual(self.run_operation(repo, "--apply"), 0)
        after = self.files(repo)
        for name, data in payload.items():
            self.assertEqual(after[name], data)
        self.assertNotIn("plugins/senzing-bootcamp/obsolete.md", after)
        for name, data in before.items():
            if name.startswith(".git/") or name in {"LICENSE", ".github/workflow.yml"}:
                self.assertEqual(after[name], data)
        self.assertEqual({name for name in after if name.startswith(".git/")},
                         {name for name in before if name.startswith(".git/")})
        self.assertEqual(release.git(repo, "diff", "--cached"), b"")
        self.assertEqual(self.files(self.source), source_before)

    def test_removed_publication_flags_are_rejected_without_changes(self):
        repo = self.public_checkout()
        before = self.files(repo)
        for arguments in (("--push-branch",), ("--confirm-tag", "0.5.3")):
            with self.subTest(arguments=arguments):
                with self.assertRaises(SystemExit) as stopped:
                    self.run_operation(repo, *arguments)
                self.assertEqual(stopped.exception.code, 2)
                self.assertEqual(self.files(repo), before)

    def test_dirty_public_index_is_preserved_and_rejected(self):
        repo = self.public_checkout()
        (repo / "README.md").write_text("review in progress\n")
        release.git(repo, "add", "README.md")
        before = self.files(repo)
        self.assertEqual(self.run_operation(repo, "--apply"), 1)
        self.assertEqual(self.files(repo), before)


if __name__ == "__main__":
    unittest.main()

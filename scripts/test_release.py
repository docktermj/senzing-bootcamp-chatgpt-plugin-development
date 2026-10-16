"""Release gates and atomic ref transactions exercised in disposable Git repositories."""

import hashlib
import contextlib
import io
import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import release
from scripts import local_version


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        release.git(self.root, "init", "-b", "21-test-1")
        for name, value in (("user.name", "Test"), ("user.email", "test@example.com"),
                            ("commit.gpgsign", "false"), ("tag.gpgsign", "false")):
            release.git(self.root, "config", name, value)
        release.git(self.root, "remote", "add", "origin", sorted(release.ORIGINS)[0])
        manifest = release.json_bytes({"name": "senzing-bootcamp", "version": "0.5.3"})
        self.write("RELEASE_VERSION", b"0.5.3\n")
        self.write("PARENT_VERSION", b"0.4.0\n")
        self.write("PARENT_COMMIT", ("a" * 40 + "\n").encode())
        self.write(release.PLUGIN_MANIFEST, manifest)
        digest = hashlib.sha256(manifest).hexdigest()
        self.write(".build-manifest.json", release.json_bytes({
            "release_version": "0.5.3", "upstream_version": "0.4.0", "upstream_commit": "a" * 40,
            "files": {".codex-plugin/plugin.json": {"generated": digest, "output": digest}},
        }))
        self.write(release.MARKETPLACE, release.json_bytes({"plugins": [{
            "name": "senzing-bootcamp", "source": {"source": "local", "path": "./plugins/senzing-bootcamp"},
        }]}))
        self.write("CHANGELOG.md", b"# Changelog\n\n## [0.5.3]\n\n- Earlier release.\n")
        self.write("docs/test-checklist.md", "\n".join(
            f"| TC-{number:02} | Yes | Check |" for number in range(1, 14)
        ).encode())
        self.record = self.root / "docs/test-records/0.5.4.md"
        self.write("docs/test-records/0.5.4.md", self.record_text().encode())
        self.commit()
        self.original = self.files()
        self.head = release.git(self.root, "rev-parse", "HEAD")
        self.index = (self.root / ".git/index").read_bytes()

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def record_text(self):
        return (
            "# Test record\n**Release candidate:** 0.5.4\n**Tested on:** 2026-10-15\n"
            "**Tester:** Fixture tester\n**Codex version/build:** Test host\n**Platform:** Test OS\n"
            "**Plugin build:** 0.5.4\n**Hooks reviewed and trusted:** PASS\n"
            "**Exact-version checks:** PASS 0.5.4 TC-03 TC-05 TC-06 TC-07 TC-08 observed in fixture\n"
            + "\n".join(f"| TC-{number:02} | PASS | Fixture observation | Tester 2026-10-15 |"
                        for number in range(1, 14)) + "\n"
        )

    def commit(self):
        release.git(self.root, "add", ".")
        release.git(self.root, "commit", "-m", "fixture")

    def files(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*")
                if path.is_file() and ".git" not in path.relative_to(self.root).parts}

    def plan(self, version="0.5.4"):
        return release.plan_release(self.root, version, "- Tested release.", "21-test-1")

    def apply(self):
        with patch.object(release, "run_checks"):
            return release.apply_release(self.root, "0.5.4", "- Tested release.", "21-test-1")

    def assert_no_release(self):
        self.assertEqual(release.git(self.root, "rev-parse", "HEAD"), self.head)
        self.assertEqual(release.git(self.root, "tag", "--list", "0.5.4"), b"")

    def test_preview_is_read_only_and_preserves_parent_provenance(self):
        updates = self.plan()
        self.assertEqual(self.files(), self.original)
        self.assertEqual((self.root / ".git/index").read_bytes(), self.index)
        self.assertEqual(updates["RELEASE_VERSION"], b"0.5.4\n")
        self.assertNotIn("PARENT_VERSION", updates)
        self.assertNotIn("PARENT_COMMIT", updates)
        self.assertNotIn(release.MARKETPLACE, updates)
        self.assert_no_release()

    def test_apply_commits_all_metadata_and_tag_together(self):
        commit = self.apply()
        self.assertEqual(release.git(self.root, "rev-parse", "HEAD").decode().strip(), commit)
        self.assertEqual(release.git(self.root, "rev-parse", "refs/tags/0.5.4").decode().strip(), commit)
        self.assertIn(b"## [0.5.4]", release.git(self.root, "show", "0.5.4:CHANGELOG.md"))
        self.assertEqual(release.git(self.root, "show", "0.5.4:RELEASE_VERSION"), b"0.5.4\n")
        self.assertEqual((self.root / "PARENT_VERSION").read_bytes(), b"0.4.0\n")
        self.assertEqual(release.git(self.root, "status", "--porcelain"), b"")
        manifest = (self.root / release.PLUGIN_MANIFEST).read_bytes()
        build = json.loads((self.root / ".build-manifest.json").read_bytes())
        self.assertEqual(build["files"][".codex-plugin/plugin.json"]["output"], hashlib.sha256(manifest).hexdigest())
        self.assertFalse((self.root / ".git/release-transaction").exists())

    def test_missing_or_nonpassing_record_blocks_without_release(self):
        for record in (None, self.record_text().replace("| TC-03 | PASS", "| TC-03 | SKIP"),
                       self.record_text().replace("**Exact-version checks:** PASS", "**Exact-version checks:** NOT RUN"),
                       self.record_text().replace("0.5.4", "0.5.40"),
                       self.record_text() + "| TC-03 | PASS | duplicate | Tester 2026-10-15 |\n"):
            with self.subTest(record=record):
                if record is None:
                    self.record.unlink()
                else:
                    self.record.write_text(record)
                self.commit()
                self.head = release.git(self.root, "rev-parse", "HEAD")
                with self.assertRaises(ValueError):
                    self.plan()
                self.assert_no_release()

    def test_invalid_or_existing_versions_block(self):
        for version in ("main", "HEAD", "0.5.4-rc.1", "00.5.4", "0.5.3", "0.4.0"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.plan(version)
        release.git(self.root, "tag", "0.5.4")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.plan()

    def test_failed_validation_does_not_prepare_refs_or_files(self):
        with patch.object(release, "run_checks", side_effect=ValueError("check failed")):
            with self.assertRaisesRegex(ValueError, "check failed"):
                release.apply_release(self.root, "0.5.4", "notes", "21-test-1")
        self.assert_no_release()
        self.assertEqual(self.files(), self.original)

    def test_ref_lock_failure_rolls_back_both_refs(self):
        lock = self.root / ".git/refs/tags/0.5.4.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text("fixture lock")
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply()
        self.assert_no_release()
        self.assertEqual(self.files(), self.original)
        lock.unlink()
        release.recover(self.root, "21-test-1")
        self.assert_no_release()

    def test_interrupted_materialization_can_be_recovered(self):
        original_replace = release.os.replace
        count = 0

        def interrupt(source, destination):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated interruption")
            original_replace(source, destination)

        with patch.object(release.os, "replace", side_effect=interrupt):
            with self.assertRaisesRegex(OSError, "simulated interruption"):
                self.apply()
        self.assertEqual(release.git(self.root, "rev-parse", "HEAD"),
                         release.git(self.root, "rev-parse", "refs/tags/0.5.4"))
        self.assertIn(b"## [0.5.4]", release.git(self.root, "show", "HEAD:CHANGELOG.md"))
        release.recover(self.root, "21-test-1")
        self.assertEqual(release.git(self.root, "status", "--porcelain"), b"")

    def test_recovery_preserves_unrelated_edits(self):
        with patch.object(release, "materialize", side_effect=OSError("interrupted")):
            with self.assertRaises(OSError):
                self.apply()
        (self.root / "CHANGELOG.md").write_text("Human edit")
        with self.assertRaisesRegex(ValueError, "changed during release"):
            release.recover(self.root, "21-test-1")
        self.assertEqual((self.root / "CHANGELOG.md").read_text(), "Human edit")

    def test_public_origin_and_dirty_checkout_are_rejected(self):
        (self.root / "unrelated.txt").write_text("Keep")
        with self.assertRaisesRegex(ValueError, "clean checkout"):
            self.plan()
        (self.root / "unrelated.txt").unlink()
        release.git(self.root, "remote", "set-url", "origin", "git@github.com:Senzing/senzing-bootcamp-chatgpt-plugin.git")
        with self.assertRaisesRegex(ValueError, "development repository"):
            self.plan()

    def test_commit_creation_failure_leaves_no_partial_release(self):
        original_git = release.git

        def fail_commit(root, *arguments, **kwargs):
            if arguments[0] == "commit-tree":
                raise subprocess.CalledProcessError(128, "git commit-tree", stderr=b"signing failed")
            return original_git(root, *arguments, **kwargs)

        with patch.object(release, "git", side_effect=fail_commit):
            with self.assertRaises(subprocess.CalledProcessError):
                self.apply()
        self.assert_no_release()
        self.assertEqual(self.files(), self.original)
        self.assertFalse((self.root / ".git/release-transaction").exists())

    def test_local_candidate_restore_uses_release_not_parent_version(self):
        with patch.object(local_version, "ROOT", self.root), patch.object(
            local_version, "MANIFEST", self.root / release.PLUGIN_MANIFEST,
        ), contextlib.redirect_stdout(io.StringIO()):
            with patch("sys.argv", ["local_version.py", "--candidate", "0.5.4"]):
                local_version.main()
            self.assertEqual(json.loads((self.root / release.PLUGIN_MANIFEST).read_text())["version"], "0.5.4")
            with patch("sys.argv", ["local_version.py", "--restore"]):
                local_version.main()
        self.assertEqual(json.loads((self.root / release.PLUGIN_MANIFEST).read_text())["version"], "0.5.3")
        self.assertEqual((self.root / "PARENT_VERSION").read_text(), "0.4.0\n")

    def test_existing_marketplace_version_assertion_moves_with_release(self):
        path = self.root / release.MARKETPLACE
        marketplace = json.loads(path.read_bytes())
        marketplace["plugins"][0]["version"] = "0.5.3"
        path.write_bytes(release.json_bytes(marketplace))
        self.commit()
        self.apply()
        self.assertEqual(json.loads(path.read_bytes())["plugins"][0]["version"], "0.5.4")

    def test_check_temporary_files_stay_inside_repository(self):
        locations = []

        def check_command(arguments, **kwargs):
            location = Path(kwargs["env"]["TMPDIR"])
            self.assertTrue(location.is_relative_to(self.root / ".git"))
            self.assertTrue(location.is_dir())
            self.assertEqual(kwargs["cwd"], self.root)
            locations.append(location)

        with patch.object(release.subprocess, "run", side_effect=check_command):
            release.run_checks(self.root)
        self.assertEqual(len(locations), 3)
        self.assertFalse(any(path.exists() for path in locations))

    def test_recovery_does_not_remove_someone_elses_index_lock(self):
        with patch.object(release, "materialize", side_effect=OSError("interrupted")):
            with self.assertRaises(OSError):
                self.apply()
        lock = self.root / ".git/index.lock"
        lock.write_text("Another Git operation")
        with self.assertRaises(ValueError):
            release.recover(self.root, "21-test-1")
        self.assertEqual(lock.read_text(), "Another Git operation")


if __name__ == "__main__":
    unittest.main()

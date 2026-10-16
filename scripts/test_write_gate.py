"""Direct-script native edit safety tests; not evidence of actual host hook firing."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "plugins/senzing-bootcamp/scripts/write-gate.py"


class WriteGateTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(prefix="codex-write-gate-")
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name) / "project with spaces"
        self.workspace.mkdir()
        (self.workspace / "config").mkdir()
        self.progress = self.workspace / "config/bootcamp_progress.json"
        self.progress.write_text(json.dumps({"current_module": "business_problem"}))

    def run_gate(self, payload):
        return subprocess.run(
            [sys.executable, str(GATE)], cwd=self.workspace,
            input=payload if isinstance(payload, str) else json.dumps(payload),
            capture_output=True, text=True, check=False,
        )

    def native(self, body):
        return self.run_gate({"tool_name": "apply_patch", "tool_input": {
            "command": "*** Begin Patch\n" + body + "\n*** End Patch",
        }})

    def test_native_add_inside_project_and_spaced_paths_are_allowed(self):
        for target in ("notes.txt", "folder with spaces/notes.txt", str(self.workspace / "absolute.txt"),
                       '"quoted folder"/notes.txt'):
            with self.subTest(target=target):
                self.assertEqual(self.native("*** Add File: " + target + "\n+hello").returncode, 0)

    def test_native_outside_add_update_and_delete_are_blocked(self):
        for operation, body in (("Add", "\n+hello"), ("Update", "\n@@\n-old\n+new"), ("Delete", "")):
            for target in (str(self.workspace.parent / "outside.txt"), "../outside.txt", "nested/../../outside.txt"):
                with self.subTest(operation=operation, target=target):
                    result = self.native("*** " + operation + " File: " + target + body)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("Write blocked:", result.stderr)

    def test_mixed_patch_checks_every_target(self):
        result = self.native("*** Add File: inside.txt\n+hello\n*** Add File: ../outside.txt\n+hello")
        self.assertEqual(result.returncode, 2)

    def test_moves_check_source_and_destination(self):
        for source, target, expected in (("old.txt", "new folder/new.txt", 0),
                                         ("old.txt", "../new.txt", 2), ("../old.txt", "new.txt", 2)):
            with self.subTest(source=source, target=target):
                body = "*** Update File: " + source + "\n*** Move to: " + target + "\n@@\n-old\n+new"
                self.assertEqual(self.native(body).returncode, expected)

    def test_native_update_context_eof_and_delete_are_allowed(self):
        body = "*** Update File: old.txt\n@@ heading\n context\n-old\n+new\n*** End of File\n*** Delete File: unused.txt"
        self.assertEqual(self.native(body).returncode, 0)

    def test_added_patch_like_text_is_not_treated_as_a_target(self):
        self.assertEqual(self.native("*** Add File: notes.txt\n+*** Add File: ../not-a-target.txt").returncode, 0)

    def test_malformed_or_unsupported_inputs_block_explicitly(self):
        payloads = ["not json", "null", "[]", {}, {"tool_name": "apply_patch", "tool_input": {}},
                    {"tool_name": "apply_patch", "tool_input": {"command": 4}},
                    {"tool_name": "Bash", "tool_input": {"command": "echo hello"}},
                    {"tool_name": "Write", "tool_input": {"file_path": []}},
                    {"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** End Patch"}}]
        for payload in payloads:
            with self.subTest(payload=payload):
                result = self.run_gate(payload)
                self.assertEqual(result.returncode, 2)
                self.assertIn("malformed or unsupported", result.stderr)

    def test_malformed_patch_structure_blocks(self):
        for body in ("*** Add File: \n+text", "*** Delete File: old.txt\n+text",
                     "*** Update File: old.txt", "*** Add File: file.txt\nnot added content",
                     "*** Move to: target.txt", "*** Add File: file.txt\n+text\n*** Unknown: ../escape",
                     "*** Update File: old.txt\n*** Move to: \n@@\n+x", "*** Add File: bad\0path\n+x"):
            with self.subTest(body=body):
                self.assertEqual(self.native(body).returncode, 2)

    def test_legacy_write_and_edit_are_preserved(self):
        for name in ("Write", "Edit"):
            for target, expected in (("notes with spaces.txt", 0), ("../outside.txt", 2)):
                with self.subTest(name=name, target=target):
                    result = self.run_gate({"tool_name": name, "tool_input": {"file_path": target, "content": "hello"}})
                    self.assertEqual(result.returncode, expected)

    def test_secret_scan_covers_native_and_legacy_payloads(self):
        for secret in ("-----BEGIN PRIVATE KEY-----", "AKIA" + "A" * 16, "AQAAAD" + "A" * 20):
            with self.subTest(secret_class=secret[:6]):
                for result in (self.native("*** Add File: file.txt\n+" + secret),
                               self.run_gate({"tool_name": "Write", "tool_input": {"file_path": "file.txt", "content": secret}})):
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("possible hardcoded secret", result.stderr)
                    self.assertNotIn(secret, result.stderr)

    def test_inactive_workspace_is_not_affected(self):
        self.progress.unlink()
        self.assertEqual(self.native("*** Add File: ../outside.txt\n+hello").returncode, 0)
        self.assertEqual(self.run_gate("invalid").returncode, 0)

    def test_symlink_escape_is_blocked(self):
        (self.workspace / "outside-link").symlink_to(self.workspace.parent, target_is_directory=True)
        self.assertEqual(self.native("*** Add File: outside-link/file.txt\n+hello").returncode, 2)

    @unittest.skipIf(os.name == "nt", "Case-sensitive POSIX path probe")
    def test_case_distinct_outside_directory_is_not_exempted(self):
        outside = self.workspace.parent / self.workspace.name.upper() / "file.txt"
        self.assertEqual(self.native("*** Add File: " + str(outside) + "\n+hello").returncode, 2)

    def test_unexpanded_temp_targets_are_blocked(self):
        for target in ("%TEMP%/file.txt", "%tmp%/file.txt"):
            self.assertEqual(self.native("*** Add File: " + target + "\n+hello").returncode, 2)

    def test_overlay_and_shipped_secret_pattern_match_parent_helper(self):
        def module(path, name):
            spec = importlib.util.spec_from_file_location(name, path)
            loaded = importlib.util.module_from_spec(spec)
            previous = sys.dont_write_bytecode
            try:
                sys.dont_write_bytecode = True
                spec.loader.exec_module(loaded)
            finally:
                sys.dont_write_bytecode = previous
            return loaded
        helper = module(GATE.parent / "secret_patterns.py", "secret_patterns")
        for path in (GATE, ROOT / "port/overlay/scripts/write-gate.py"):
            self.assertEqual(module(path, "write_gate").SECRET_PATTERN, helper.SECRET_PATTERN)
        self.assertEqual(GATE.read_bytes(), (ROOT / "port/overlay/scripts/write-gate.py").read_bytes())


if __name__ == "__main__":
    unittest.main()

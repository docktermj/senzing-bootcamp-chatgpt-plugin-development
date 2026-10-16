"""Direct-script lifecycle regressions; actual trusted Codex-host observations remain separate."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/senzing-bootcamp"
GUARDS = ("socratic-controller.py", "stop-nudge.py", "session-start.py")


class BootcampStateTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(prefix="codex-lifecycle-")
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name)
        (self.workspace / "config").mkdir()
        self.progress = self.workspace / "config/bootcamp_progress.json"
        self.preferences = self.workspace / "config/bootcamp_preferences.yaml"

    def run_hook(self, script, payload=None, environment=None):
        variables = {**os.environ, "PLUGIN_ROOT": str(PLUGIN), "SENZING_BOOTCAMP_DISABLE_STOP_NUDGE": "0"}
        variables.update(environment or {})
        return subprocess.run(
            [sys.executable, str(PLUGIN / "scripts" / script)], cwd=self.workspace,
            input=json.dumps(payload if payload is not None else {
                "prompt": "yes", "last_assistant_message": "Setup completed.",
            }), env=variables, capture_output=True, text=True, check=False,
        )

    def active(self, module="business_problem", step=4):
        self.progress.write_text(json.dumps({"current_module": module, "current_step": step}))

    def assert_silent(self, scripts=GUARDS):
        before = {path.relative_to(self.workspace): path.read_bytes()
                  for path in self.workspace.rglob("*") if path.is_file()}
        for script in scripts:
            with self.subTest(script=script):
                result = self.run_hook(script)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "")
        after = {path.relative_to(self.workspace): path.read_bytes()
                 for path in self.workspace.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_missing_progress_is_silent_and_nonmutating(self):
        self.assert_silent()

    def test_unrecorded_and_invalid_progress_states_are_silent(self):
        for content in ("", "{}", "{broken", "[]", "null", "true", "7", '"module"',
                        '{"current_module": null}', '{"current_module": ""}',
                        '{"current_module": "  "}', '{"current_module": 3}',
                        '{"current_module": {}}', '{"current_step": 4}'):
            with self.subTest(content=content):
                self.progress.write_text(content)
                self.assert_silent()

    def test_invalid_utf8_progress_is_silent(self):
        self.progress.write_bytes(b"\xff\xfe")
        self.assert_silent()

    def test_progress_directory_instead_of_file_is_silent(self):
        self.progress.mkdir()
        self.assert_silent()

    def test_completion_marker_stands_down_all_continuation_guards(self):
        self.active("graduation", 7)
        for value in ("true", "True", "yes", "on", "1", '"true"', "'true'", "true # done"):
            with self.subTest(value=value):
                self.preferences.write_text("bootcamp_complete: " + value + "\n")
                self.assert_silent()

    def test_completed_unrelated_prompt_does_not_restart_or_inject(self):
        self.active("query_visualize_discover", 10)
        self.preferences.write_text("bootcamp_complete: true\n")
        for prompt in ("Help with my production project.", "yes", "resume the bootcamp", "start a new bootcamp"):
            with self.subTest(prompt=prompt):
                result = self.run_hook("socratic-controller.py", {"prompt": prompt})
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
        self.assert_silent()

    def test_active_terse_answers_keep_recorded_skill_and_step(self):
        self.active()
        for prompt in ("3", "yes", "no"):
            with self.subTest(prompt=prompt):
                result = self.run_hook("socratic-controller.py", {"prompt": prompt})
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)["hookSpecificOutput"]
                self.assertEqual(output["hookEventName"], "UserPromptSubmit")
                context = output["additionalContext"]
                self.assertIn("module-01-business-problem/SKILL.md", context)
                self.assertIn("recorded current step is 4", context)
                self.assertIn("Process the answer first", context)
                self.assertIn("exactly one", context)

    def test_explicitly_recorded_preparation_remains_active(self):
        self.active("bootcamp_preparation", 2)
        result = self.run_hook("socratic-controller.py")
        self.assertIn("bootcamp-preparation/SKILL.md", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_false_completion_and_nested_or_commented_flags_do_not_disable(self):
        self.active()
        for content in ("bootcamp_complete: false\n", "bootcamp_complete: off\n",
                        "bootcamp_complete: no\n", "bootcamp_complete: 0\n",
                        "other:\n  bootcamp_complete: true\n", "# bootcamp_complete: true\n"):
            with self.subTest(content=content):
                self.preferences.write_text(content)
                self.assertIn("A Senzing Bootcamp is active", self.run_hook("socratic-controller.py").stdout)
                self.assertEqual(json.loads(self.run_hook("stop-nudge.py").stdout)["decision"], "block")

    def test_active_stop_still_blocks_status_only_and_releases_questions_and_loops(self):
        self.active()
        blocked = self.run_hook("stop-nudge.py")
        self.assertEqual(blocked.returncode, 0)
        self.assertEqual(json.loads(blocked.stdout)["decision"], "block")
        for payload in ({"last_assistant_message": "👉 **Which option?**"},
                        {"last_assistant_message": "Setup completed.", "stop_hook_active": True}):
            with self.subTest(payload=payload):
                released = self.run_hook("stop-nudge.py", payload)
                self.assertEqual((released.returncode, released.stdout), (0, ""))

    def test_stop_opt_out_does_not_disable_controller(self):
        self.active()
        self.preferences.write_text("disable_stop_nudge: true\n")
        self.assertEqual(self.run_hook("stop-nudge.py").stdout, "")
        self.assertIn("A Senzing Bootcamp is active", self.run_hook("socratic-controller.py").stdout)
        self.preferences.unlink()
        self.assertEqual(self.run_hook("stop-nudge.py", environment={
            "SENZING_BOOTCAMP_DISABLE_STOP_NUDGE": "1",
        }).stdout, "")

    def test_active_session_resume_retains_module_and_checkpoint_behavior(self):
        self.active()
        result = self.run_hook("session-start.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("offer to resume from the last recorded module", result.stdout)
        self.assertTrue((self.workspace / "docs/progress/recap_checkpoint.md").is_file())
        self.assertEqual(json.loads(self.progress.read_text())["current_module"], "business_problem")

    def test_malformed_stop_payload_never_crashes(self):
        self.active()
        for payload in ([], 3, "not an object"):
            with self.subTest(payload=payload):
                result = self.run_hook("stop-nudge.py", payload)
                self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        for raw in ("not json", "null"):
            result = subprocess.run([sys.executable, str(PLUGIN / "scripts/stop-nudge.py")],
                                    cwd=self.workspace, input=raw, capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_explicit_start_entry_and_fresh_preparation_are_preserved(self):
        entry = (PLUGIN / "skills/start-bootcamp/SKILL.md").read_text()
        self.assertIn("For an unfinished or unrecorded project", entry)
        self.assertIn("../bootcamp-onboarding/SKILL.md", entry)
        self.assertIn("For a completed project only", entry)
        self.assertIn("Which fresh project directory", entry)
        self.assertIn("do not overwrite", entry)
        onboarding = (PLUGIN / "skills/bootcamp-onboarding/SKILL.md").read_text()
        self.assertIn("## Codex completed-run guard", onboarding)
        self.assertIn("../start-bootcamp/SKILL.md", onboarding)
        self.assertLess(onboarding.index("## Codex completed-run guard"),
                        onboarding.index("## Before anything else"))
        preparation = (PLUGIN / "skills/bootcamp-preparation/SKILL.md").read_text()
        self.assertIn("Which bootcamp would you like?", preparation)
        self.assertIn("How much detail would you like", preparation)

    def test_hook_registration_and_overlay_outputs_remain_present(self):
        hooks = json.loads((PLUGIN / "hooks/hooks.json").read_text())["hooks"]
        handlers = hooks["UserPromptSubmit"][0]["hooks"]
        self.assertTrue(any("socratic-controller.py" in handler["command"] for handler in handlers))
        for name in ("bootcamp_state.py", "socratic-controller.py", "stop-nudge.py"):
            with self.subTest(name=name):
                self.assertEqual((PLUGIN / "scripts" / name).read_bytes(),
                                 (ROOT / "port/overlay/scripts" / name).read_bytes())


if __name__ == "__main__":
    unittest.main()

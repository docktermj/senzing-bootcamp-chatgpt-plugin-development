"""Reproduce audit findings with direct scripts, without applying any patch or running host hooks."""

import json
import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "plugins/senzing-bootcamp/scripts"


def main():
    observations = []
    with tempfile.TemporaryDirectory(prefix="senzing-audit-repro-") as directory:
        workspace = Path(directory)
        (workspace / "config").mkdir()
        progress = workspace / "config/bootcamp_progress.json"
        progress.write_text(json.dumps({"current_module": "business_problem", "current_step": 4}))
        environment = {**os.environ, "PLUGIN_ROOT": str(SCRIPTS.parent),
                       "SENZING_BOOTCAMP_DISABLE_STOP_NUDGE": "0"}

        def run(identifier, script, payload):
            result = subprocess.run(
                ["python3", str(SCRIPTS / script)], cwd=workspace, env=environment,
                input=json.dumps(payload), text=True, capture_output=True, check=False,
            )
            observations.append({"case": identifier, "evidence_type": "direct_script",
                                 "exit_code": result.returncode, "stdout": result.stdout,
                                 "stderr": result.stderr})

        outside = workspace.parent / (workspace.name + "-outside-not-created.txt")
        run("legacy-file-path-outside-control", "write-gate.py", {
            "hook_event_name": "PreToolUse", "cwd": str(workspace), "tool_name": "Write",
            "tool_input": {"file_path": str(outside), "content": "harmless probe"},
        })
        run("native-patch-outside", "write-gate.py", {
            "hook_event_name": "PreToolUse", "cwd": str(workspace), "tool_name": "apply_patch",
            "tool_input": {"command": "*** Begin Patch\n*** Add File: " + str(outside)
                           + "\n+harmless probe\n*** End Patch"},
        })
        if outside.exists():
            raise RuntimeError("Unexpected outside artifact; this probe never applies a patch")
        progress.write_text("{}")
        run("empty-progress-controller", "socratic-controller.py", {"prompt": "yes"})
        run("empty-progress-stop", "stop-nudge.py", {
            "last_assistant_message": "An ordinary non-bootcamp response.",
        })
        progress.write_text(json.dumps({"current_module": "graduation", "current_step": 7}))
        (workspace / "config/bootcamp_preferences.yaml").write_text("bootcamp_complete: true\n")
        run("graduated-controller", "socratic-controller.py", {
            "prompt": "Help me with my production project.",
        })
        run("graduated-stop-control", "stop-nudge.py", {
            "last_assistant_message": "Graduation complete.",
        })
    print(json.dumps({"assurance": "Direct scripts only; not an actual Codex-host dry run",
                      "observations": observations}, indent=2))


if __name__ == "__main__":
    main()

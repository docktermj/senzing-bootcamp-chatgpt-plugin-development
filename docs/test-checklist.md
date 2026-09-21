# Host-behavior test checklist

Static port checks prove that the hook definitions and controller code are present. They cannot
prove that a Codex host fires a hook, displays its working state, or continues a non-yielding
turn. This checklist is the release gate for those host-behavior assumptions.

Run every **critical** check in a new Codex desktop task against a cache-busted local build. Review
and trust the currently bundled hooks before starting. Record the outcome of every check in
[`test-records/`](test-records/) using the release version as its filename. A missing, skipped, or
failed critical check blocks release under CINV-022; do not replace it with an assumption that the
static suite passed.

## Recording rules

1. Copy [`test-records/TEMPLATE.md`](test-records/TEMPLATE.md) to
   `test-records/X.Y.Z.md` before testing the exact-version release candidate.
2. For each check, record `PASS`, `FAIL`, `SKIP`, or `NOT RUN`, the tester/date, and concise
   observable evidence. `SKIP` and `NOT RUN` are not passing outcomes.
3. Record the Codex version, platform, plugin version, build mode, and hook-trust result at the top
   of the record. This makes host assumptions auditable when Codex changes.
4. Restore the non-cache-busted version, then repeat enough of the hook checks to establish that
   the exact release build—not only the iteration build—was tested.

## Checks

| ID | Critical | Host-behavior check and expected observation | CINV exercised |
| --- | --- | --- | --- |
| TC-01 | Yes | **Test setup.** Install a cache-busted local build, review and trust its hooks, then create a new Codex task. Record the build version and trust prompt/result. | CINV-009, CINV-021 |
| TC-02 | Yes | **Fresh start.** Start the bootcamp with no progress file and confirm the expected first module/question is shown. | CINV-010, CINV-011, CINV-021 |
| TC-03 | Yes | **Terse-answer hook firing.** Answer two active questions with terse values such as `3` and `yes`. Each prompt must invoke the controller and advance or respond from the recorded active module without asking to “continue the bootcamp.” | CINV-010, CINV-011, CINV-021 |
| TC-04 | Yes | **Resume.** In a new task with a recorded module and step, submit an ordinary answer and confirm the controller rehydrates that exact active module/step. Also exercise an empty progress file safely. | CINV-010, CINV-011, CINV-018, CINV-021 |
| TC-05 | Yes | **Non-yielding continuation.** Trigger automatic work (for example, a generated scenario, command, artifact, checkpoint, summary, or phase boundary). Confirm commentary may appear while work runs, but the same turn continues through all automatic steps to the next skill-defined question. | CINV-012, CINV-015, CINV-021 |
| TC-06 | Yes | **Stop continuation.** Cause or observe a status-only/non-question assistant response while the bootcamp is active. Confirm the Stop hook continues it rather than ending the turn. | CINV-013, CINV-020, CINV-021 |
| TC-07 | Yes | **Stop release.** Complete a normal turn ending in exactly one `👉` question. Confirm the Stop hook releases that turn and does not loop or append another question. | CINV-013, CINV-014, CINV-020, CINV-021 |
| TC-08 | Yes | **Visible working state.** While each bundled behavior-changing hook is exercised, observe a concise visible working-state label/status message in the supported Codex interface. | CINV-015, CINV-016, CINV-021 |
| TC-09 | Yes | **Feedback.** Capture feedback without external submission and confirm it is saved or reported by the expected local path/flow. | CINV-018, CINV-021 |
| TC-10 | Yes | **Notes.** Capture a note and confirm the active bootcamp retains it without affecting an unrelated task. | CINV-018, CINV-021 |
| TC-11 | Yes | **Checkpointing and transition.** Complete a checkpoint and transition into the next module; verify progress records the new module/step and a new task resumes it. | CINV-011, CINV-012, CINV-021 |
| TC-12 | Yes | **Module-specific paths.** Exercise Module 1’s generated-scenario path and Module 2’s existing-install and configuration-seeding paths. Record any unavailable dependency and its user-facing behavior. | CINV-012, CINV-019, CINV-021 |
| TC-13 | Yes | **Graduation.** Complete or use a controlled completed fixture to run graduation. Confirm recap/production artifacts are generated and the bootcamp reaches its intended finished state. | CINV-012, CINV-021 |

The checklist is deliberately broader than a static test: TC-03, TC-05, TC-06, TC-07, and TC-08
directly verify the host assumptions that `check_port.py` cannot observe. TC-01 through TC-13 map
every CINV-021 manual scenario to a recorded step.

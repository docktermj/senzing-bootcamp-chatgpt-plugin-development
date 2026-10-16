---
name: start-bootcamp
description: Start or resume the guided Senzing entity-resolution bootcamp in Codex. Use when the user explicitly asks to start, begin, continue, or resume the bootcamp.
---

# Start or resume the Senzing Bootcamp

Read and follow `../../docs/codex-interaction-contract.md`. Before onboarding, check the
top-level `bootcamp_complete` preference in `config/bootcamp_preferences.yaml`. If it is true,
the existing bootcamp is finished: do not invoke normal resume, clear the completion marker,
overwrite progress, or repeat graduation. For a resume request, explain that this run is already
complete and point to its artifacts only after confirming they exist. This is a terminal reply
and needs no invented continuation question.

For a completed project only, and only when the user explicitly requests a new bootcamp, ask:

👉 **Which fresh project directory should I use for the new bootcamp?**

Wait for the real answer, preserve the completed project, and use the selected fresh workspace
for onboarding. If it already contains bootcamp progress, do not overwrite it: explain the
conflict and repeat the directory question. Do not infer a request for a new run from an unrelated
prompt. Automatic hooks never create a new run themselves.

For an unfinished or unrecorded project, follow `../bootcamp-onboarding/SKILL.md` normally.
Whether this is a fresh start or a resume is decided by the
contents of `config/bootcamp_progress.json`, not merely by its existence. Intermediate commentary
never ends a bootcamp turn; continue until the active shipped skill supplies the next `👉` question.

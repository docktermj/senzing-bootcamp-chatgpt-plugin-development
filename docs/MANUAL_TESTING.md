# Manual test gate

Manual testing happens before a release tag is published.

1. Build the selected upstream tag with `python3 scripts/sync_upstream.py --tag X.Y.Z`.
2. Validate with `python3 scripts/check_port.py` and the plugin validator.
3. In the Codex desktop app, open the plugin from the repository marketplace link supplied by the
   maintainer, choose **Install**, review and trust the bundled lifecycle hooks, and then start a
   new task. A separate Codex CLI installation is not required for desktop testing. If the hook
   trust prompt is declined or absent, treat strict Socratic parity as untested.
4. During iteration, ask Codex to run `python3 scripts/local_version.py`, reinstall the plugin from
   its details page, and always start a new task.
5. Test a fresh start, an empty progress file, resume with a recorded module, note capture, feedback
   capture without external submission, MCP-unavailable behavior, module transition/checkpointing,
   and graduation artifact generation. In particular, exercise Module 1's generated-scenario path
   and Module 2's existing-install and configuration-seeding paths. Confirm that intermediate
   commentary may report automatic work, but the same turn continues and its final response ends
   on exactly one skill-defined `👉` question rather than a status-only message.
   Also answer at least two questions with terse replies such as `3` and `yes`; confirm the next
   turn rehydrates the recorded module without requiring “continue the bootcamp.”
6. Run `python3 scripts/local_version.py --restore`. Confirm the manifest and `UPSTREAM_VERSION`
   exactly equal `X.Y.Z`, then run `python3 scripts/package_release.py`.

The release should remain blocked if any critical scenario fails or if the compatibility audit
finds a Claude-only runtime assumption in an active skill.

## Optional CLI path

Maintainers who already have the `codex` command may instead run:

```bash
codex plugin marketplace add <repository-root>
codex plugin add senzing-bootcamp@personal
```

These commands are optional and are not a prerequisite for using the Codex desktop app.

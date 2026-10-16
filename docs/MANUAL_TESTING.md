# Manual test gate

Manual testing happens before a release tag is published. The complete, recorded host-behavior
gate is [`test-checklist.md`](test-checklist.md). Create a versioned record from
[`test-records/TEMPLATE.md`](test-records/TEMPLATE.md) and record every step; a critical check that
is failed, skipped, or not run blocks the release.

1. Build the selected parent tag with `python3 scripts/sync_parent.py --tag PARENT_TAG`.
   Select the local release candidate `X.Y.Z` independently of that parent tag.
2. Validate with `python3 scripts/check_port.py` and the plugin validator.
3. In the Codex desktop app, open the plugin from the repository marketplace link supplied by the
   maintainer, choose **Install**, review and trust the bundled lifecycle hooks, and then start a
   new task. A separate Codex CLI installation is not required for desktop testing. If the hook
   trust prompt is declined or absent, treat strict Socratic parity as untested.
4. During iteration, ask Codex to run `python3 scripts/local_version.py`, reinstall the plugin from
   its details page, and always start a new task.
5. Execute and record every checklist step, including fresh start, empty-progress handling, resume,
   terse answers, non-yielding continuation, Stop continuation/release, visible working state,
   notes, feedback, checkpointing, transitions, module-specific paths, and graduation.
6. Run `python3 scripts/local_version.py --candidate X.Y.Z` and repeat the required exact-version
   hook checks, recording the version and observed results in the test record. Restore the
   checkout with `python3 scripts/local_version.py --restore`, commit the completed record, and
   use the `release` operation to preview and apply the local version/changelog/commit/tag update.
   Confirm the manifest and `RELEASE_VERSION` equal `X.Y.Z`, then package. `PARENT_VERSION` remains
   the selected source tag throughout.

The release should remain blocked if any critical scenario fails or if the compatibility audit
finds a Claude-only runtime assumption in an active skill.

## Optional CLI path

Maintainers who already have the `codex` command may instead run:

```bash
codex plugin marketplace add <repository-root>
codex plugin add senzing-bootcamp@personal
```

These commands are optional and are not a prerequisite for using the Codex desktop app.

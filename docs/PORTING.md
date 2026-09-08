# Porting and release design

## Version contract

`scripts/sync_upstream.py` discovers the highest stable SemVer tag in the
`docktermj/senzing-bootcamp-claude-plugin-development` repository,
checks out that tag, verifies that its plugin manifest contains the same version, and generates the
Codex plugin. Prereleases and the head of `main` are intentionally ignored. `UPSTREAM_VERSION`,
`UPSTREAM_COMMIT`, and the Codex manifest provide source provenance.

Use `--tag X.Y.Z` to reproduce a specific release. Use `--source-dir` for offline tests against an
already checked-out tag.

## Ownership boundary

- Upstream owns curriculum skills, examples, and bootcamp helper scripts.
- This repository owns Codex packaging, entry skills, host-language adaptation, and release tests.
- `port/overlay/` wins over generated upstream content.
- Claude hooks and command files are not shipped. Their user-facing workflows are represented by
  skills; lifecycle enforcement needs explicit Codex regression tests.

## Update workflow

1. Run `python3 scripts/sync_upstream.py`.
2. Review the generated diff and the compatibility audit.
3. Run `python3 scripts/check_port.py` and the upstream-derived script tests that are safe locally.
4. Install the repo marketplace and plugin locally; use a cache-busted build version for iteration.
5. Start a new Codex task and execute the manual scenarios in `docs/MANUAL_TESTING.md`.
6. Restore the exact upstream version, rebuild, validate, package, tag, and publish.

The scheduled GitHub workflow detects a newer upstream release by producing a failing diff. It does
not publish or merge generated changes automatically; translation changes require human review.

The sync and release paths use one converter. “Initial creation” is simply the first sync into an
empty repository; maintaining separate creation and update skills would duplicate policy and drift.

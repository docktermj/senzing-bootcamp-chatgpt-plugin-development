# Porting and release design

Every update MUST preserve the Codex implementation guarantees in
[`../specs/INVARIANTS.md`](../specs/INVARIANTS.md) as well as the applicable upstream curriculum
invariants. A failed `CINV-NNN` is a release blocker.

## Version contract

`scripts/sync_upstream.py` discovers the highest stable SemVer tag in the production
`Senzing/senzing-bootcamp-claude-plugin` repository,
checks out that tag, verifies that its plugin manifest contains the same version, and generates the
Codex plugin. Prereleases and the head of `main` are intentionally ignored. `UPSTREAM_VERSION`,
`UPSTREAM_COMMIT`, and the Codex manifest provide source provenance.

Use `--tag X.Y.Z` to reproduce a specific release. Use `--source-dir` for offline tests against an
already checked-out tag.

## Transformation contract

[`../tools/bootcamp-transform/contract.yaml`](../tools/bootcamp-transform/contract.yaml) is the
single source of truth for upstream file handling and Codex adaptation. It declares every copy and
ignore rule, literal and regular-expression substitution, structured JSON edit, generated artifact,
and downstream overlay. `scripts/sync_upstream.py` is a host-neutral executor for those operations;
it does not carry a parallel list of porting decisions.

Before writing generated output, the updater classifies every upstream plugin file. Each file MUST
match exactly one copy or explicit ignore rule. A new unclassified file stops the build with
`E_UNMATCHED_FILE` and leaves the existing plugin and provenance files unchanged. This makes an
upstream addition a required review decision instead of silently passing it through.

The contract uses JSON syntax, which is valid YAML 1.2, so the updater remains dependency-free.

## Ownership boundary

- Upstream owns curriculum skills, examples, and bootcamp helper scripts.
- This repository owns Codex packaging, entry skills, host-language adaptation, and release tests.
- Codex-specific transformation decisions are authored in the transformation contract; larger
  downstream-owned files live in `port/overlay/`.
- Contract-declared overlays are applied last and win over transformed or generated content.
- Claude command files are represented by Codex skills. The version-matched lifecycle hooks are
  shipped and adapted to Codex's plugin root and stable hook fields; the Codex-only Socratic
  controller restores the active module on every user prompt. Hook trust and lifecycle behavior
  require explicit Codex regression tests.

## Update workflow

1. Run `python3 scripts/sync_upstream.py`.
2. Review the generated diff and the compatibility audit. If the build reports
   `E_UNMATCHED_FILE`, add one reviewed contract rule with an inline reason where appropriate.
3. Review every affected `CINV-NNN` in `specs/INVARIANTS.md`, then run
   `python3 scripts/check_port.py`, `python3 -m unittest scripts.test_sync_upstream`, and the
   upstream-derived script tests that are safe locally.
4. Install the repo marketplace and plugin locally; use a cache-busted build version for iteration.
5. Start a new Codex task and execute the manual scenarios in `docs/MANUAL_TESTING.md`.
6. Restore the exact upstream version, rebuild, validate, package, tag, and publish.

The scheduled GitHub workflow detects a newer upstream release by producing a failing diff. It does
not publish or merge generated changes automatically; translation changes require human review.

The sync and release paths use one converter. “Initial creation” is simply the first sync into an
empty repository; maintaining separate creation and update skills would duplicate policy and drift.

# Porting and release design

Every update MUST preserve the Codex implementation guarantees in
[`../specs/INVARIANTS.md`](../specs/INVARIANTS.md) as well as the applicable upstream curriculum
invariants. A failed `CINV-NNN` is a release blocker.

[`UNIFORM_PORTING_FRAMEWORK.md`](UNIFORM_PORTING_FRAMEWORK.md) maps the shared Claude-to-host
framework and its Codex release gates. It is the maintainer entry point for evaluating an update.

`tools/bootcamp-transform/contract.yaml` contains the invariant-disposition register. Every
upstream `INV-NNN` is honored unless it has an explicit `preserved_restated` Codex mechanism or a
justified `discounted` disposition (`conflictsWith` plus `resolution`). A newer upstream version
fails the build with `E_INVARIANT_REVIEW` until a maintainer re-reviews the register; security,
portability, and correctness guarantees such as `INV-052` must never be discounted.

## Version contract

`scripts/sync_parent.py` discovers the highest stable SemVer tag in the production
`Senzing/senzing-bootcamp-claude-plugin` repository,
checks out that tag, verifies that its plugin manifest contains the same version, and generates the
Codex plugin. Prereleases and the head of `main` are intentionally ignored. `PARENT_VERSION`,
`PARENT_COMMIT`, and the Codex manifest provide source provenance.

Use `--tag X.Y.Z` to reproduce a specific release. Use `--source-dir` for offline tests against an
already checked-out tag.

## Transformation contract

[`../tools/bootcamp-transform/contract.yaml`](../tools/bootcamp-transform/contract.yaml) is the
single source of truth for upstream file handling and Codex adaptation. It declares every copy and
ignore rule, literal and regular-expression substitution, structured JSON edit, generated artifact,
and downstream overlay. `scripts/sync_parent.py` is a host-neutral executor for those operations;
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

1. Run `python3 scripts/sync_parent.py`.
2. Review the generated diff and the compatibility audit. If the build reports
   `E_UNMATCHED_FILE`, add one reviewed contract rule with an inline reason where appropriate.
3. Review every affected `CINV-NNN` in `specs/INVARIANTS.md`, then run
   `python3 scripts/check_port.py`, `python3 -m unittest scripts.test_sync_parent`, and the
   upstream-derived script tests that are safe locally.
4. Install the repo marketplace and plugin locally; use a cache-busted build version for iteration.
5. Start a new Codex task, execute the host-behavior checklist in `docs/test-checklist.md`, and
   commit its per-version outcome record from `docs/test-records/` with the release evidence.
6. Restore the exact upstream version, rebuild, validate, package, tag, and publish.

The scheduled GitHub workflow detects a newer upstream release by producing a failing diff. It does
not publish or merge generated changes automatically; translation changes require human review.

## Parent/child governance

Every maintainer command in `commands/` names an explicit repository-local skill path. The
skill/command mapping must agree in both directions; CI runs
`python3 scripts/check_maintainer_commands.py` to reject missing counterparts, incorrect targets,
and duplicate skill names across the two intentional locations:

- `maintainer-skills/` holds workflows invoked through explicit local file references.
- `.agents/skills/` holds `propagate-to-public` for automatic repository skill discovery.

Keeping propagation in `.agents/skills/` preserves its existing discoverability. The checker uses
the union of both locations, so the split does not exempt any skill from having a command.
The new feedback entry is `commands/feedback-to-issues.md`, targeting
`maintainer-skills/feedback-to-issues/SKILL.md`. These entries are maintained prompts, not
automatically registered bare slash commands.

Use `/parity-check` as the only parent-to-child propagation path: it compares the pinned
provenance with a **tagged** parent release and files local parity work. Use
`/escalate-to-parent` as the only cross-repository issue path for canonical curriculum problems;
the child and parent issues must cross-reference each other. Port behavior remains local.

Escalated local issues carry the durable `awaiting-parity` label. `parity-check` verifies a
completed parent's closing commit is contained in the checked stable tag and that the matching
production provenance has landed in local `origin/main` before commenting with the tag and
closing the issue. It processes this queue even when no new release delta exists. A declined
parent fix or unverifiable evidence leaves the local issue open for human review. After merging
a parity PR, run `parity-check` again to finish the escalation loop.

The sync and release paths use one converter. “Initial creation” is simply the first sync into an
empty repository; maintaining separate creation and update skills would duplicate policy and drift.

## Implement a tracked issue

Use the repository-local `implement-github-issue` operation with an explicitly selected issue:
read [`../commands/implement-github-issue.md`](../commands/implement-github-issue.md) and follow
[`../maintainer-skills/implement-github-issue/SKILL.md`](../maintainer-skills/implement-github-issue/SKILL.md).
For example, ask Codex to follow that skill for issue 16. Repository-local command entries are
maintained prompts; they are not automatically registered as bare Codex slash commands.

The operation asks for an issue when omitted, requires explicit approval of readiness before
editing, and requires a second approval of the diff and local CI results before pushing a branch
and opening a PR. It records decisions on the issue and stops at an open PR for human review.
Parity PRs include the verified `PARENT_VERSION` and `PARENT_COMMIT` update with the generated
fix, so provenance advances when the fix lands and the issue closes.

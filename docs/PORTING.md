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
`PARENT_COMMIT`, and the build manifest provide source provenance. `RELEASE_VERSION` independently
sets the local Codex manifest version; a parent sync preserves it. A new checkout without that
file bootstraps its initial local version from the selected parent version.

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

### Codex example PDF

The contract's `verified-binary` artifact packages the reviewed Codex PDF from `port/artifacts/`,
not the unchanged Claude binary. Its input record covers adapted Markdown, renderer, brand tokens,
logo and every referenced screenshot; any mismatch fails the sync before replacing shipped output.
Ordinary sync, tests and packaging require only the standard library, not fpdf2.

To refresh after an intentional example/input change, install the optional
`requirements-example-pdf.txt` into a maintainer environment and run
`python3 scripts/example_pdf.py --refresh --source-dir <pinned-parent-checkout> --tag <PARENT_VERSION>`.
The command verifies exact pinned source provenance and prepares the adapted source in a temporary
tree with this artifact omitted, without changing the shipped plugin. Review that source/input diff.
The renderer uses a fixed PDF creation timestamp and
does not silently downgrade to the stdlib path, which would lose image fidelity. Regenerate twice
and compare bytes; render and inspect every page before accepting the PDF/input-record diff.
The example is a historical run, not evidence of a new host/SDK test. Keep its recorded facts.

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
6. Restore the local release version, rebuild, validate, and package. Use `release` to create the
   next local release commit/tag after completing its test record, then review publication manually.

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

## Public propagation boundary

Before propagating, use `commands/retrofit-from-public.md` and its repository-local skill to
identify public review changes that could be overwritten. The helper compares pinned committed
snapshots after applying forward publication transformations in memory. It writes to neither
checkout, does not apply inverse rewrites, and excludes public governance files outside the
propagation payload. Dirty files are not part of the comparison.

The workflow assigns every divergence a local or parent-bound verdict with a reason. It searches
existing issues before filing actionable local findings and hands parent-bound evidence to the
separate escalation workflow. Fingerprints aid repeat-run deduplication, while semantic review
distinguishes a closed issue from a new unresolved delta. Importing a fix happens later through
`implement-github-issue`, at the owning transformation, overlay, or parent source.

`propagate-to-public` reads an exact tagged development release and requires a clean public
checkout already on the maintainer's named review branch. Its default preview is read-only;
`--apply` updates only the allowlisted public working-tree files. Both modes leave the Git index,
commit history, branches, tags, and remotes unchanged. Propagation never stages, commits, pushes,
creates or switches branches, opens PRs, or creates releases. The maintainer reviews and tests the
diff before performing those publication steps manually. A checkout with an existing diff must be
handled manually before propagation can run again.

## Local release transaction

`commands/release.md` delegates to `maintainer-skills/release/SKILL.md`. Select the next local
SemVer, release notes, and an existing review branch in this development checkout. Complete and
commit `docs/test-records/X.Y.Z.md` with genuine host observations before release. Missing,
skipped, failed, incomplete, or duplicate critical results block the operation. The historical
0.5.3 record is unverified and cannot authorize another release.

```bash
python3 scripts/release.py --version X.Y.Z --branch BRANCH --notes "Release notes"
python3 scripts/release.py --version X.Y.Z --branch BRANCH --notes "Release notes" --apply
```

Preview is read-only. After explicit approval, apply updates `RELEASE_VERSION`, the generated
manifest and its build hashes, the changelog, and any existing marketplace version assertion.
The current marketplace uses a local source and resolves the plugin manifest without a separate
version field. Release leaves parent provenance unchanged, runs local automated checks, prepares
a commit, and atomically updates the branch and creates its tag using `git update-ref --stdin`.
It does not push or write to the public checkout. Worktree Git layouts with external metadata are
rejected to keep release writes inside this repository.

An interruption after the ref transaction can leave the files/index behind the consistent
release commit and tag. Keep `.git/release-transaction` and run
`python3 scripts/release.py --branch BRANCH --recover` to finish materialization. Recovery refuses
conflicting edits or moved refs; resolve those manually rather than resetting or moving tags.
The release skill also requires the plugin/skill validators and manual checklist; automated
tests cannot establish host-behavior results.

## Live runtime dry run

`commands/dry-run.md` delegates to `maintainer-skills/dry-run/SKILL.md`. Run live MCP contract
probes first, then direct script execution and observed host hooks, then real bootcamp
conversations and generated-artifact review. Failed prerequisites block later phases. Direct
script tests never prove Codex hook invocation, and unavailable host checks are advisory
degradations with explicit impact/follow-up, never passes.

Use a dedicated workspace and retain actual tool, transcript, operator, and artifact evidence.
The evidence helper validates phase order, source types, candidate hashes, and question-origin
records; its synthetic unit tests do not establish runtime success. The Socratic turn cycle must
be observed across real turns against the shipped interaction contract. Findings are deduplicated
and routed locally or through parent escalation. This operation does not publish or waive the
manual release checklist.

## Static production readiness audit

`commands/production-readiness-audit.md` delegates to its repository-local maintainer skill.
Audit the complete shipped tree, including overlay contributions, for instruction consistency,
reference/route completeness, fulfilled onboarding promises, interaction-contract coherency,
invariant coverage, and ownership. The inventory helper tracks file/context hashes and review
coverage; mechanical checks and coverage validation do not substitute for reading the curriculum.

File deduplicated local findings and hand parent-bound findings to `escalate-to-parent`, with
evidence and routing reasons. Record unexpressible inherited checks as explicit limitations in
the invariant-disposition register, preserving required mechanisms or discount justifications.
Deferred reviews and filing blockers remain visible. Live host behavior is evaluated separately
through `dry-run` and the manual checklist; a complete static coverage record is not a release pass.

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

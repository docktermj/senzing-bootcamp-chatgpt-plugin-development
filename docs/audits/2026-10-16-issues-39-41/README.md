# Issues 39 and 41: Gate 2 publication review

Local implementation and validation completed on 2026-10-16. Gate 1 was approved for these
two issues only. No implementation commit, push, PR or merge has been performed. Gate 2 is
pending. These audit artifacts are review evidence, not proposed files in either issue PR.

## Destination and provenance

- Destination: `docktermj/senzing-bootcamp-chatgpt-plugin-development`, base `main`.
- Reviewed base: `04ded7494d3e5ac0c1c543b964128acc5ef83d00`.
- Parent remains `0.5.3`, commit `7e2d484f6cfe9af864762e0a0c95119d483cbb08`.
- Local release remains `0.5.3`. These are local Codex fixes, not parent parity imports.
- No Senzing SDK/API facts were changed. INV-080 live verification is not applicable to
  these host-policy and rendering changes; the PDF remains a historical example.

## Complete diffs

- `issue-39.patch`: tracked diff plus every untracked implementation file, including tests.
- `issue-41.patch`: tracked diff plus every untracked implementation file, including both
  binary assets, input verification record, renderer tooling, dependency pins and tests.
- `issue-39-files.txt` and `issue-41-files.txt`: exact proposed file inventories.
- Patches include Git binary deltas so the PDF changes are not omitted from review.

## Issue 39

Branch: `39-docktermj-1`.

Worktree: `/home/senzing/.codex/worktrees/issue-39-model-guidance/senzing-bootcamp-chatgpt-plugin-development`.

Owning changes are the transformation contract and Codex model-selection overlay. Generated
ground rules, graduation instructions, model-selection documentation and build manifest are
regenerated from those sources. New static regressions run in CI and the port checker.

The replacement restores the module-start apparatus and exemptions, one canonical twelve-row
stage table, independent live model/effort comparison, per-dial fallback, above-table exemption,
symmetric optional step-down offers, pinned switch/done gates and all three acceptance branches.
Graduation delegates to the same policy. Role resolution avoids fixed model IDs, assumed hidden
settings, invented controls and price claims. Only the user changes host settings.

Invariant review: INV-063/069/098/114/137/138/139/140/141/236 have explicit preserved-restated
mechanisms and static guards. Apparatus/verbosity, selection, recap and interface guarantees
remain represented. No invariants are discounted. Actual host interaction is not established
by static checks and remains a manual checklist obligation.

Proposed PR title: **fix: preserve Codex module-start model guidance**

Proposed PR body:

```markdown
## Summary
- Restore module-start and graduation model/effort guarantees at the owning contract/overlay.
- Preserve setup exemptions, canonical stage recommendations and user-controlled host settings.
- Add eight static regression tests, negative controls and CI/port-check integration.

## Validation
- All commands in the current test workflow pass locally.
- Full unittest discovery: 126 tests pass.
- Two exact-parent rebuilds produce identical plugin trees and build manifests.
- Two package builds produce identical ZIP bytes; git diff --check passes.
- Parent and local release pins remain 0.5.3.
- Manual Codex host interaction was not run; static coverage is not runtime evidence.

Closes #39
```

## Issue 41

Branch: `41-docktermj-1`.

Worktree: `/home/senzing/.codex/worktrees/issue-41-example-pdf/senzing-bootcamp-chatgpt-plugin-development`.

Owning changes are the verified-binary contract artifact, pre-rendered Codex PDF/input record,
stdlib verification and refresh tooling, optional pinned rendering dependencies and porting
documentation. The shipped PDF and build manifest are regenerated. Normal sync and packaging
remain stdlib-only. Refresh verifies pinned provenance, uses the adapted source and rich renderer,
fixes the creation timestamp and refuses a lossy stdlib fallback.

The input inventory covers adapted Markdown, renderer, brand tokens, logo and every referenced
screenshot. Stale inputs, incomplete inventories, changed binaries and compressed Claude-only
host instructions fail verification. Tests exercise actual contract copying and rejection paths.

Invariant review: source ownership, deterministic output, reviewed binary synchronization,
overlay-last precedence and exact pinned provenance are preserved. No parent curriculum or
renderer is patched and no invariant is discounted. The 32-page PDF was visually reviewed;
all 13 referenced screenshots were embedded. Two independent renders are byte-identical.
Inherited screenshot clipping and historical count/terminology inconsistencies are not repaired
by this local host-adaptation fix. This is not evidence of a new bootcamp/SDK/host run.

Proposed PR title: **fix: synchronize the Codex example recap PDF**

Proposed PR body:

```markdown
## Summary
- Replace the unchanged Claude PDF with a Codex PDF rendered from adapted example Markdown.
- Verify the binary and complete input inventory before copying during dependency-free sync.
- Add reproducible refresh tooling, optional pinned dependencies, documentation and eight tests.

## Validation
- All commands in the current test workflow pass locally.
- Full unittest discovery: 126 tests pass.
- Two pinned-parent rebuilds and package builds are byte-identical.
- Two rich PDF renders are byte-identical; all 32 pages visually reviewed and 13 screenshots embedded.
- Binary/content/input checks and git diff --check pass; parent/release pins remain 0.5.3.
- Existing historical content and inherited screenshot defects remain; no new host/SDK run claimed.

Closes #41
```

## Evidence and next step

`issue39-final-validation.log` and `issue41-final-validation.log` record the actual current workflow
commands and full discovery results. `issue39-tree-*.sha256` and `issue41-tree-*.sha256` are matching
rebuild inventories; the ZIP checksum files were successfully rechecked after the second packages.
These are local CI mirrors, not GitHub Actions results. No remote CI exists for these unpublished
branches yet.

Recommended next step: approve Gate 2 for committing these exact diffs, pushing the two named
branches and opening the two proposed PRs against main. Then check remote CI and review each PR.
Human review and merge remain separate; do not close either issue before its fix lands.

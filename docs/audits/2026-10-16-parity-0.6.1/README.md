# Read-only 0.6.1 parity assessment and implementation plan

Follow-up: the maintainer accepted the manifest-only mapping. `READINESS.md` records the subsequent
semantic scope review, live MCP evidence and Gate 1 proposal; it supersedes the initial pending
readiness status below. Implementation approval has not yet been given.

## Verified provenance

- Child landed main: `686d8fb5e7018ac569b464533043b4aa9cacb399`.
- Current parent pin: `0.5.3`, production commit `7e2d484f6cfe9af864762e0a0c95119d483cbb08`.
- Target stable production tag: `0.6.1`, commit `d3d99523f88957cd9dda2d29375892bf2c557663`.
- Canonical development tag: `0.6.1`, commit `7cfdcd88a3f51623e826171cd64a3a409308c7d1`.
- Production plugin tree: `94adeccea222d30c661d39341d0c2caa458d89e9`.
- Development plugin tree: `9e2a18175bbd2b382f57cf0bd6f556c4a25e86dd`.
- Both manifests declare 0.6.1. Neither tag was changed; no parent write occurred.

## Mapping exception requiring human review

The tagged plugin trees are not byte-identical. Their complete diff changes only the manifest's
`homepage` and `repository` URLs from the development repository to the production repository.
All other tagged plugin content is identical. See `tagged-mapping.patch`.

This is a production-publication metadata mapping, not a curriculum difference, but the current
parity policy/helper requires identical trees for automatic escalation closure. Do not claim
that strict correspondence check passes or bypass it silently. Human acceptance of this mapping
is needed before implementation readiness approval. Do not modify either stable parent tag.
If automatic closure later needs an exception, it requires a separately reviewed, tightly scoped
policy/helper change; it is not necessary to close any current escalation now.

## Delta inventory

The production 0.5.3-to-0.6.1 delta changes 49 plugin files. There is one new plugin file,
`scripts/generate_recap_video.py`. Repository website/workflow changes are outside the plugin
import boundary. `plugin-files.txt` inventories every changed plugin path; `parent-plugin.patch`
contains the complete plugin diff, including binary changes.

Principal areas needing review:

- Optional graduation video, per-module b-roll, aggregate-only privacy limits and dependencies.
- SDK setup, EULA order, existing installations, language-binding routes and Windows commands.
- Generated-data collision/type checks, mapping gates, sandbox returns and quality iterations.
- Samples/subsets, load budgeting, reconciliation, first-source order and How-state audit.
- Visualization, packaging, feedback, screenshot/PDF helpers and graduation production outputs.
- Updated parent model guidance: preserve the Codex-native canonical policy and user-controlled
  settings from local issue 39 rather than copying Claude models or commands.

First-line invariant triage finds 46 new IDs, INV-301 through INV-346, and 25 changed existing
invariant first lines. This is not a completed semantic disposition review: the full 459-line
invariant diff, continuations, supersessions and inherited guarantees still need review.

## Read-only checks actually run

- Current contract classifies all 84 target plugin files, including the new video script.
- Register validation correctly refuses 0.6.1 with `E_INVARIANT_REVIEW`.
- A temporary output-only contract preview completes the current text transformations but fails
  `E_STALE_BINARY_ARTIFACT` because the example Markdown changed. No pin or shipped output changed.
- The unchanged example PDF cannot be reused: refresh it from adapted 0.6.1 source and review
  every page. Renderer/Markdown inputs changed, so renew the complete input record as well.
- All eight live linked parent issues 671–678 are open. Each read-only parity helper evaluation
  returns `awaiting_parent`. Local issues 40 and 42–48 remain open and labeled `awaiting-parity`.
- No escalation is eligible for closure. No closing-commit ancestry claim was made.
- Local open/closed issue search found no existing 0.6.1 parity work issue.

These checks are comparison evidence, not full CI, runtime verification or implementation readiness.
No SDK/product assertions from the release have yet been independently reverified with live MCP.

## Proposed staged approach

1. Resolve the manifest-only mapping review. Complete the semantic invariant review and obtain
   fresh evidence from the owning Senzing MCP routes for affected product/API claims; unsupported
   negative claims must be narrowed, not inferred from unrelated empty results. Record results.
2. Present issue-specific Gate 1 readiness approval covering the complete tagged import, owning
   contract/overlay changes, Codex compatibility, validation and any unresolved upstream limitations.
   Do not edit implementation or provenance before that approval.
3. Use an isolated issue-number/username/sequence branch. Update the reviewed contract register
   to exact production 0.6.1 provenance, preserve local lifecycle/model adapters, adapt new host
   surfaces and refresh the Codex example PDF through its owning verified-binary mechanism.
4. Sync the complete exact production tag, changing PARENT_VERSION, PARENT_COMMIT and generated
   manifest/plugin together. Keep RELEASE_VERSION at 0.5.3; a local release is separate work.
5. Validate every current CI command, targeted/negative regressions, classification/host leakage,
   two deterministic sync/package builds, two PDF renders and all-page visual review. Verify
   video handling/privacy and optional dependency/failure paths; disclose unrun host/OS checks.
6. Present the complete new-file/binary-inclusive diff for Gate 2. Only after approval commit,
   push and open a PR. Use a closing keyword for the new parity work issue only, not the eight
   awaiting-parity escalations. Human review/merge then lands fix and provenance together.
7. Re-run parity-check on landed origin/main. Keep remaining parent fixes for stable 0.7.0 or
   the exact later containing release; never import unfinished parent development.

## Scope status

Comparison complete; implementation readiness is conditional on mapping review, live Senzing
fact verification and semantic invariant review. No implementation files, branch, pins, commits,
PRs, parent issues or escalation closure were changed by this assessment. Only audit evidence
and a new local parity tracking issue are intended outputs.

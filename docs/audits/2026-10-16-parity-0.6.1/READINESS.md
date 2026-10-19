# Issue 51 readiness review

Date: 2026-10-16. This is a readiness assessment and proposed implementation scope, not a
completed implementation, release certification or approval to edit implementation files.

## Verdict

Ready to request Gate 1 for a complete tagged 0.6.1 import with Codex-owned adaptations and
targeted regression coverage. The maintainer accepted the two manifest URL differences as the
expected production mapping. That acceptance does not change either tag or relax the strict
automatic escalation-closure helper. All eight escalations remain awaiting their parent fixes.

Use production commit `d3d99523f88957cd9dda2d29375892bf2c557663`, not the development commit.
Update PARENT_VERSION/PARENT_COMMIT, the contract register and generated manifest/plugin together.
Keep RELEASE_VERSION at 0.5.3; release and public propagation remain separate operations.

## Material compatibility findings

The current contract classifies all 84 plugin files. Its preview detects stale PDF inputs as
intended, and the version gate requires an explicit invariant review. Neither is a reason to
waive a guard: the implementation must refresh the owned binary and reviewed dispositions.

Two additional Codex transformation gaps are present in temporary preview output:

1. Prefix substitutions for `Opus 5` and `Sonnet 5` leave `.5` tails when the parent names 5.5,
   including the introductory ground-rules paragraph and Truth Set visualization instructions.
   The contract must match the complete parent model token and preserve native model-role
   wording, not copy time-sensitive Claude names into the port.
2. The feedback template now uses `claude-opus-5-5[1m]`, which the old exact example substitution
   misses. Adapt that example to configured Codex model/effort wording at the owning contract.

Retain issue 39's canonical stage table and live-dial/acceptance procedure, graduation delegation,
issue 41's verified-binary mechanism, and the existing completed/inactive-run lifecycle guards.
Add negative controls for the new model spelling and leaked suffixes. Do not fix parent-owned
share-package, teardown, visualization, PDF fallback or curriculum defects locally.

## Invariant semantic scope review

Descriptions below are review descriptions, not quotations or substitutes for authoritative
parent prose. They identify import obligations and conditional scope, not observed runtime passes.
The full tagged source, invariant diff and original context remain the evidence.

### New runtime/general guarantees

| IDs | Import obligation |
| --- | --- |
| INV-320 | Fix all multi-source subset budgets before loading; zero-budget sources do not start or fail. |
| INV-321 | External defect reports contain neither identifiers nor bootcamper data; license requests are separately scoped. |
| INV-322 | Machine-composed local artifacts exclude host/personal identifiers; certificate naming has its own rules. |
| INV-323 | Shareable findings use loaded names/aliases, never invented transliterations. |
| INV-324 | Remaining license capacity uses an SDK measurement, not registry sums; unknown stays unknown. |
| INV-325 | Every capped choice writes the single defined load_subset record before loading. |
| INV-326 | Samples record measured size/strategy without replacing collected counts. |
| INV-327 | First-source selection shares the later ordering heuristic and records the actual choice. |
| INV-328 | Category/option answers never become fabricated quantities for later MCP calls. |
| INV-329 | Recap SDK version comes from the installed product reading; missing means Unknown. |
| INV-330 | How visualization reports final-state signs without assigning undocumented meanings. |
| INV-331 | SQLite heads-ups compare actual loadable volume to the live MCP threshold, not production-tier answers. |
| INV-334 | Audit every multi-record entity, report measured denominator and distinguish all four outcomes. |
| INV-335 | Organization-suffix candidates are a plugin heuristic, reported per source and retyped only by user decision. |
| INV-336 | Apply the recorded type decision before mapping advances; use justified derived type, not a suffix discriminator. |
| INV-338 | EULA consent precedes every SDK install/update path; declining an update preserves the working install. |
| INV-339 | Existing installations skip the package install, not project bindings or environment setup. |
| INV-340 | Offer video once, use aggregates, verify produced output, preserve nonblocking failure/decline behavior. |
| INV-341 | Completion replaces one aggregate-only b-roll entry per module; preparation remains exempt. |
| INV-342 | Video validates first, restricts image paths, preserves existing output on failure and never truncates narration. |
| INV-343 | Discriminators are a conditional remedy, not a default mapping construct. |
| INV-344 | Per-source loops ask per-source questions; loading and sandbox decisions occur at their owning stage. |
| INV-345 | Explain synthesized gaps and regeneration before the pinned quality question; no silent regeneration. |

These remain parent-owned. Import the complete owning instructions/helpers from the tag and guard
their preservation across Codex transformations; do not reimplement their SDK calls from memory.

### New parent-development guarantees

These bind conditional maintainer/development subjects, not a mandate to copy `.claude/`, frozen
parent specs, private tests or user-level skills into the participant plugin. Preserve their
scope and record native mechanisms where the child has the corresponding subject. Do not mark
an absent parent-only mechanism as a passing child runtime test or silently discount a guarantee.

| IDs | Reviewed subject/native consideration |
| --- | --- |
| INV-301 | Atomic version records/tag; native local release remains governed by CINV-030/032. |
| INV-302, INV-303 | Maintainer command/documentation/skill correspondence and resolution; existing native checker uses derived sets. |
| INV-304 | Explicit propagation roots exclude maintainer state; retain native marketplace and allowlist rules. |
| INV-305, INV-306 | Optional PDF dependency declaration and genuine present/absent test configurations, with honest skips. |
| INV-307 | Parent frozen archive/live exceptions; do not import or assume that archive layout for child specs. |
| INV-308 | Verification distinguishes empty, skipped and unresolved; no silent denominator loss or duplicate scope definitions. |
| INV-309 | Account for durable rules in issue-driven development; importing existing parent guarantees does not mint new IDs. |
| INV-310 | Permanent record operations stop before publication; content and publication approvals remain separate. |
| INV-311 | Derived artifacts name source/regeneration and unknowns; descriptions are not authoritative prose. |
| INV-312 | Cross-repository comparison files local issues and does not silently apply source changes. Implementation is the separate approved issue path. |
| INV-313 | Derive supersession only from explicit reciprocal markers; partial supersession is not a third status. |
| INV-314 | External records require exact-text assent per record; no unattended self-authorization. |
| INV-315 | Distinguish rule quotations, descriptions and unparsed records in verification. |
| INV-316 | Named maintainer commands resolve or carry a point-of-use nonshipping marker; both directions matter for a register. |
| INV-317 | Findings need durable tracking before repair, not only a transient report. |
| INV-318 | A command never grants its own findings unattended approval. |
| INV-319 | Local intake and parent escalation have separate write owners. |
| INV-332 | Only the maintainer declines valid work; inability to implement is blocked, not declined. |
| INV-333 | Costly unspecified work requires a choice; this review does not authorize a host walkthrough or local release. |
| INV-337 | User-level governing skills must not acquire duplicate repo definitions; apply only where that governance arrangement exists. |
| INV-346 | Phrase guards survive line wraps and report match-start lines; line-scoped reads need a reason. |

### Changed inherited guarantees

- INV-084, INV-175, INV-186: full-ready files only, early-safe env scripts/PowerShell dot-sourcing and production registry projection.
- INV-091, INV-154, INV-270: fail without vendored D3, disclose capped graph populations and compare combination rows rather than all legend rows.
- INV-132, INV-149, INV-160, INV-204, INV-213, INV-222, INV-234, INV-291: exact live tool contracts, coverage-not-behavior negatives, retrieval terminal steps, capabilities-only probes,
  owner-checked absence claims, language-specific binding sources, chunk assembly and accurately scoped search evidence.
- INV-157, INV-229, INV-237: every PDF fallback's character handling, checkpoint-derived verification keys and shared Java filenames.
- INV-239, INV-251, INV-281: synthesized collision/regeneration rules, clarified prompt lineage and distinct closed feedback vocabularies.
- INV-209: shipped Markdown negative-evidence markers stay inside HTML comments, not bootcamper-facing body text.
- INV-202, INV-207, INV-216, INV-217: reference/path and archived workflow clarifications remain scoped to their authoritative subjects.

All 46 new IDs and 25 changed existing first-line entries have a reviewed subject above. This is
not a replacement for register/source assertions during implementation. Retain unchanged inherited
guarantees, existing explicit restatements and all CINV rules; add no unexplained discounts.
The new-source register must name the production tag/commit and native mechanisms explicitly.

## Live Senzing evidence

`mcp-readiness.json` preserves 28 route calls plus get_capabilities, including requests and full
responses, against server 1.39.1. No real records, credentials, feedback submission, SDK installation
or resolution were used. Selected findings and their effect on the proposed import:

- sdk_guide install for Linux apt/yum, macOS and Windows confirms EULA variables and platform paths.
  Preserve the first-EULA flow and dynamic route lookup, not an install command reconstructed from memory.
- search_docs returns the 4.4.0 Migration & Action Required section, and the exact Homebrew/Scoop
  upgrade routes return their documented commands. SDK version still must be measured locally.
- get_sdk_reference confirms get_version/get_license signatures, recordLimit's schema, How final-state
  fields and binding-specific signatures. get_stats returns an empty schema beside callable signatures:
  only that coverage is empty; it does not establish that a runtime response lacks fields.
- search_docs for RECORD_TYPE returns the Entity Specification's cross-type rule and organization-name
  guidance. The broader initial query did not verify that claim; the refined owning query did.
- sdk_guide confirms Python-by-runtime-path, local C# packages, Rust git and TypeScript GitHub routes.
  Current Linux/macOS replies now describe C# packages, unlike the parent's explicitly dated old note.
  The parent flow already says to re-read the live route first; do not promote the historical negative
  to a current absence or edit the frozen parent release to update it.
- A synthetic metadata-only mapping sequence reached validated step 4 using current master-slot and
  derived-field schema shapes. This verifies schema acceptance only, not mapper execution or suffix
  retyping correctness. No sample data file was read or manufactured as Senzing output.
- sdk_guide load with 501 records returns the production route; preserve null/category handling and
  live volume guidance. The broad SQLite search did not independently establish a threshold and is
  not used to assert one; the install route carries the scoped environment volume warning.

Historical rank/index stamps, OS observations and old MCP coverage statements in the parent are
not newly measured runtime evidence. Do not claim every historical query remains identically ranked,
or that these documentation calls establish an installed SDK/host outcome. Retain runtime MCP-first
instructions and record any further issue-specific discrepancy rather than patching parent facts locally.

## Approved-scope proposal for Gate 1

- Owning implementation paths: transformation contract, Codex model-selection overlay if needed,
  scripts/tests/CI for import checks and optional helper dependencies, porting documentation,
  verified example-PDF source/record, provenance pins and generated plugin/build manifest.
- Import all 49 tagged plugin deltas, including optional graduation video, through sync_parent;
  preserve all existing local overlays and known privacy/safety limitations tracked upstream.
- Fix the two demonstrated host-language gaps at the contract, not generated files only.
- Preserve source-scoped governance; do not perform a wholesale parent-maintainer-tooling transplant,
  relax parity_status tree equality, create parent issues, close escalations or publish a release.
- Re-review/record dispositions and add focused regression coverage for model spelling, source
  version/pins, inherited optional video schema/path/exit behavior, b-roll/privacy instructions,
  mapping/collection returns, installed-SDK version capture, sample/subset reconciliation and offline D3.
- Run current workflow commands, full discovery and applicable upstream-derived runtime tests in
  real fpdf2-present/absent configurations. Declare optional dependencies and count/report skips
  honestly; do not pretend a skipped rich render or an unavailable OS ran.
- Rebuild/sync/package twice from exact source, compare complete generated trees and manifest/ZIP
  bytes, refresh/render PDF twice, inspect every page and verify referenced images.
- Use existing host checklist for later release qualification. Manual Codex hook firing, real SDK
  outcomes and Windows PowerShell 5.1 behavior remain NOT RUN unless actually observed.
- Stop with complete local diffs and validation evidence for Gate 2; no commit/push/PR yet.

No new implementation branch has been created and no tracked implementation or pin has changed.
Baseline validation on unchanged merged main: 35 focused model-guidance, example-PDF, parity-status
and invariant tests pass; the maintainer command checker passes. These are not 0.6.1 implementation results.
The planned branch will use issue 51, the authenticated maintainer username and the next unused
sequence after checking local/remote branches and PR history at implementation time.

# Parent 0.6.1 import review

Reviewed 2026-10-16 for local issue 51, against merged Codex main
`686d8fb5e7018ac569b464533043b4aa9cacb399`.

## Source and ownership

The exact production source is Senzing/senzing-bootcamp-claude-plugin tag 0.6.1,
commit `d3d99523f88957cd9dda2d29375892bf2c557663`. Development tag 0.6.1 resolves to
`7cfdcd88a3f51623e826171cd64a3a409308c7d1`. The tagged plugin trees differ only in the
Claude manifest's homepage/repository URLs. The maintainer accepted that production metadata
mapping; neither tag is modified and automatic escalation-closure tree equality is not relaxed.

The import covers all 49 changed plugin files from production 0.5.3, including the new optional
video renderer. Repository websites, parent private tests and parent maintainer tooling are not
participant payload. All inherited content remains parent-owned; local work is host adaptation,
provenance, validation and the reviewed Codex example PDF.

Parent provenance advances to 0.6.1 while the local RELEASE_VERSION remains 0.5.3. This is not a
local release or public propagation. Local issues 40 and 42–48 remain awaiting-parent/parity;
no automatic closing keywords for them belong in this import.
The example's version assertion is transformed from the local release variable before PDF
verification/rendering, rather than inheriting the parent's distinct plugin version.

## Invariant dispositions

The prose in the tagged development `specs/INVARIANTS.md` is authoritative. Descriptions here
are scope/mechanism explanations, not quotations or assertions that runtime outcomes occurred.
The contract honors inherited guarantees by default, retains explicit Codex restatements and
discounts none. Parent-development-only conditions remain scoped to their source subjects:
importing a participant plugin does not copy the parent's frozen archive or user-level skills.

New runtime obligations are retained in the tagged owning skills/helpers:

- INV-320, INV-324, INV-325, INV-326, INV-327: fixed source budgets, measured remaining capacity,
  explicit subsets/samples, two-stage reconciliation and one first-source ordering rule.
- INV-321, INV-322, INV-323: defect-report privacy, local host-identifier privacy and loaded names
  rather than fabricated transliterations in shareable reports.
- INV-328, INV-329, INV-330, INV-331, INV-334: categories are not counts, installed SDK version is
  measured locally, How signs are reported without invented semantics, and load-volume/audit gates
  use actual measured denominators.
- INV-335, INV-336, INV-338, INV-339: type-candidate decisions precede mapping; EULA precedes
  installation; existing SDKs still receive project bindings and environment setup.
- INV-340, INV-341, INV-342: optional aggregate-only video/b-roll, pinned consent, nonblocking
  failures, offline local paths, separate exit codes and no truncated narration.
- INV-343, INV-344, INV-345: conditional discriminators, per-source questions and disclosed
  synthesized-data regeneration rather than silent changes.

New parent-development subjects are considered explicitly, not treated as shipped runtime tests:

- INV-301: native local atomic release/version behavior remains under CINV-030/032.
- INV-302, INV-303, INV-304, INV-316: native command resolution/documentation and reviewed public
  roots remain under the maintainer/propagation checks, not parent .claude directory copying.
- INV-305, INV-306: declared optional renderer dependencies, a real present/absent CI matrix and
  honest skips; the absent runner checks importability and a measured rich-path skip.
- INV-307, INV-309, INV-310, INV-337: preserve source-scoped archive, invariant-accounting,
  separated publication and governing-skill conditions; do not transplant parent governance.
- INV-308, INV-311, INV-313, INV-315, INV-346: verification/derived records remain honest about
  unknowns and scope, supersession comes from markers, and new phrase guards normalize whitespace.
- INV-312, INV-314, INV-317, INV-318, INV-319, INV-332, INV-333: local comparison/intake,
  explicit approvals, durable findings, human-only unattended/decline decisions and no guessed
  costly defaults. Implementation follows the separate approved local issue path.

Changed inherited subjects also retain their owning behavior:

- INV-084, INV-175, INV-186: full-ready inputs, early-safe environment scripts and projected
  production registries.
- INV-091, INV-154, INV-270: offline D3 refusal, cap disclosures and combination-key legend checks.
- INV-132, INV-149, INV-160, INV-204, INV-213, INV-222, INV-234, INV-291: exact live MCP contracts,
  coverage-not-behavior negatives, retrieval, language routes, chunks and scoped search evidence.
- INV-157, INV-229, INV-237: every PDF fallback, derived verification keys and shared Java names.
- INV-239, INV-251, INV-281: collisions/regeneration, prompt lineage and feedback vocabularies.
- INV-209: negative-evidence markers remain HTML comments in shipped Markdown.
- INV-202, INV-207, INV-216, INV-217: source reference/archive/actor clarifications retain scope.

## Evidence and validation boundaries

Readiness used live Senzing MCP server 1.39.1: installation/EULA/language routes, 4.4.0 release
notes, product version/license signatures and recordLimit, How response fields, RECORD_TYPE,
mapping schemas and production load routing. A metadata-only synthetic mapping reached validated
step 4; it is not mapper/SDK execution. No user records or credentials were submitted.

Current install replies now document C# sources that old, explicitly dated parent notes did not.
The owning flow re-reads live routes first. Historical comments, ranks and OS observations are
not promoted to current facts or rewritten locally as curriculum fixes.

The import adds local preservation tests and optional helper-runtime checks. Static policy tests
do not establish actual host hook firing, live SDK resolution or Windows PowerShell 5.1 results.
Release still requires version-specific host evidence under CINV-021/022/032.

Known inherited share-package leakage, failed-stop purge conflict, screenshot timing, PDF fallback
tail loss, graph/snapshot defects and quality/UAT examples remain tracked for a later stable parent
release. This import does not certify the entire curriculum defect-free.

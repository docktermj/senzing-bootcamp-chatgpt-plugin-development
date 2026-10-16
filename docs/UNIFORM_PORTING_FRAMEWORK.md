# Uniform Claude-to-host porting framework

This development repository is a child of the canonical Claude bootcamp. It transforms a tagged
parent release into Codex behavior; it does not fork curriculum ownership. The following framework
is intentionally host-agnostic so another child can reuse the same gates with different host
terminology and mechanisms.

| Component | Codex implementation | Release gate |
| --- | --- | --- |
| A. Tagged provenance | `PARENT_VERSION`, `PARENT_COMMIT`, and `sync_parent.py` | Stable parent tag and full commit only; never `HEAD`. |
| B. Declarative contract | `tools/bootcamp-transform/contract.yaml` | Every upstream file is matched once or fails `E_UNMATCHED_FILE`. |
| C. Invariant dispositions | `invariant_disposition_register` in the contract | Every upstream `INV-NNN` is honored, preserved/restated, or justified as discounted; re-review blocks a new source version. |
| D. Host-native invariants | `specs/INVARIANTS.md` (`CINV-NNN`) | Both parent `INV-NNN` and Codex `CINV-NNN` are evaluated on every update. |
| E. Mechanical checks | `scripts/check_port.py`, `scripts/check_maintainer_commands.py` | Port checks pass; maintainer commands and skills agree in both directions across both documented skill locations. |
| F. Reconciliation | `.build-manifest.json` and `sync_parent.py` | A pre-write three-way report names added, modified, removed, preserved, and conflict paths. |
| G. Recorded host tests | `docs/test-checklist.md`, `docs/test-records/` | Every critical manual host-behavior result is recorded per release. |
| H. Determinism | `.github/workflows/check-parent.yaml` | Rebuild leaves no diff in generated output, provenance, or the build manifest. |
| I. Cross-repo governance | `commands/`, `maintainer-skills/` | `/parity-check` files tagged parent deltas; `/implement-github-issue` implements a selected local issue through two approval gates to an open PR; `/escalate-to-parent` is the sole child-to-parent write path. |

`PARENT_VERSION` records the exact stable SemVer parent tag, and `PARENT_COMMIT` records its full
commit SHA. The family uses parent/child terminology for plugin provenance because "upstream"
already identifies the Senzing MCP server and the destination for server-defect feedback.

`RELEASE_VERSION` is independent of parent provenance and drives the local plugin version and
packaging. The `release` command requires completed version-specific host-test evidence and
updates version assertions, the changelog commit, and a local tag in one atomic branch/tag
transaction. It keeps a recovery journal for interrupted file/index materialization and performs
no public-repository writes or publication. The current marketplace resolves the local manifest
and has no separate version assertion.

The parent owns curriculum and all `INV-NNN` identifiers. A child never copies or renumbers them.
If a host lacks a parent mechanism, preserve the guarantee with a host-native construction where
possible; otherwise document the advisory degradation in the disposition register and release
evidence. A failed gate is a release blocker, not advisory.

Public propagation is a separate working-tree operation. It supports only preview and apply
against a clean checkout on an existing, explicitly named review branch. Apply leaves the Git
index unchanged and stops for manual review and testing. Commits, pushes, branches, PRs, tags,
and releases are separate human publication steps, never actions of `propagate-to-public`.

`retrofit-from-public` is the read-only inverse review: compare pinned public payload snapshots
with the normalized development build, triage every divergence, and file deduplicated local
issues. Parent-bound findings are handed to `escalate-to-parent`. It writes no checkout files;
implementation and inverse self-reference conversion belong to the separate issue workflow.

`production-readiness-audit` adds the static consistency, coherency, and completeness review of
the entire shipped plugin, overlays included. Its inventory/coverage helper makes omitted or
stale reviews visible; semantic conclusions require reading the instructions. Findings are
deduplicated and routed locally or to the parent, and unexpressible inherited checks are recorded
in the invariant-disposition register. Runtime evidence remains a separate gate.

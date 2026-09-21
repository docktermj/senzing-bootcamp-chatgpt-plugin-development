# Uniform Claude-to-host porting framework

This development repository is a child of the canonical Claude bootcamp. It transforms a tagged
parent release into Codex behavior; it does not fork curriculum ownership. The following framework
is intentionally host-agnostic so another child can reuse the same gates with different host
terminology and mechanisms.

| Component | Codex implementation | Release gate |
| --- | --- | --- |
| A. Tagged provenance | `UPSTREAM_VERSION`, `UPSTREAM_COMMIT`, and `sync_upstream.py` | Stable parent tag and full commit only; never `HEAD`. |
| B. Declarative contract | `tools/bootcamp-transform/contract.yaml` | Every upstream file is matched once or fails `E_UNMATCHED_FILE`. |
| C. Invariant dispositions | `invariant_disposition_register` in the contract | Every upstream `INV-NNN` is honored, preserved/restated, or justified as discounted; re-review blocks a new source version. |
| D. Host-native invariants | `specs/INVARIANTS.md` (`CINV-NNN`) | Both parent `INV-NNN` and Codex `CINV-NNN` are evaluated on every update. |
| E. Mechanical checks | `scripts/check_port.py` | Ledger, provenance, files, residual-host references, and static hook behavior checks pass. |
| F. Reconciliation | `.build-manifest.json` and `sync_upstream.py` | A pre-write three-way report names added, modified, removed, preserved, and conflict paths. |
| G. Recorded host tests | `docs/test-checklist.md`, `docs/test-records/` | Every critical manual host-behavior result is recorded per release. |
| H. Determinism | `.github/workflows/check-upstream.yaml` | Rebuild leaves no diff in generated output, provenance, or the build manifest. |
| I. Cross-repo governance | `commands/`, `maintainer-skills/` | `/parity-check` pulls tagged parent changes into local issues; `/escalate-to-parent` is the sole child-to-parent write path. |

The parent owns curriculum and all `INV-NNN` identifiers. A child never copies or renumbers them.
If a host lacks a parent mechanism, preserve the guarantee with a host-native construction where
possible; otherwise document the advisory degradation in the disposition register and release
evidence. A failed gate is a release blocker, not advisory.

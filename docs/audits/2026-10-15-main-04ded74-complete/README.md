# Complete static audit — merged main, 2026-10-15

**Static review coverage complete: 87/87 shipped files and 6/6 semantic categories.**
Coverage validation passes, with zero structural alerts. **This is not a production-readiness or runtime pass.** Findings remain unresolved in the audited payload.

## Scope and provenance

- Audited main commit: `04ded7494d3e5ac0c1c543b964128acc5ef83d00`.
- Release and pinned parent version: `0.5.3`; production parent commit `7e2d484f6cfe9af864762e0a0c95119d483cbb08`.
- Inventory digest: `3920dd4ab0e3c9a1359689e8437475ec1c152f00c0a831873260b0bd3872377f`.
- All 71 text files read in full, including the complete vendored D3 bundle. All 15 PNG assets visually inspected; the complete 32-page PDF rendered and visually inspected.
- Full associated parent invariant ledger, local CINV ledger, actual disposition register, contract and all 12 winning overlays reviewed.
- Three parallel reviewers were explicitly authorized. Their complete-file observations, bounded-read evidence and crosschecks are retained beside the consolidated `review.json`; unchanged-byte observations from earlier checkpoints were reused only after context reassessment.
- Earlier checkpoint directories remain unchanged. No shipped implementation, parent pin, register, branch or commit changed.

## Findings

**27 recorded findings: 2 local, 25 parent-bound.** Ten have verified child tracking issues and 17 match existing parent issues. All seven newly approved parent-bound escalations are complete; no handoffs remain. Closed parent issues do **not** establish that fixes landed in pinned 0.5.3.

### Local and already escalated

- **F-003 — [#39](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/39):** Codex section replacements delete expressible module/graduation model-switch and gate guarantees. Graduation evidence and corrected line location added to the issue.
- **F-006 — [#41](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/41):** Bundled PDF still teaches Claude controls and differs from adapted Markdown. Local binary host-adaptation/synchronization defect.
- **F-004 — [child #40](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/40) → [parent #671](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/671):** Contradictory screenshot checkpoint/embedding timing. Cross-links and `awaiting-parity` label verified; keep child open until a containing parent tag lands.

### New parent-bound escalations

| ID | Finding | Impact | Child → parent |
|---|---|---|---|
| F-023 | Share archive includes `production/data/senzing-ready/` inputs while promising no source data | **P1 privacy:** do not rely on the share profile's exclusion promise without inspecting its contents | [#42](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/42) → [#672](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/672) |
| F-020 | Truth Set teardown both permits and forbids purge after an unverified stop | Irreversible cleanup instruction conflict | [#43](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/43) → [#673](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/673) |
| F-024 | Stdlib PDF renderers silently truncate code/table values despite high pre-render retention | Keepsake findings/identifiers/commands can lose content | [#44](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/44) → [#674](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/674) |
| F-026 | Offline Records lookup indexes only capped graph nodes | Real browsable entities outside cap falsely appear missing | [#45](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/45) → [#675](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/675) |
| F-025 | Source filtering hides graph circles but leaves sibling labels visible | Misleading filtered view | [#46](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/46) → [#676](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/676) |
| F-021 | Quality example scores disagree with the weighted formula | First example crosses a decision-gate band | [#47](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/47) → [#677](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/677) |
| F-022 | High UAT with low match accuracy has no readiness branch | Ordinary outcome leaves workflow unspecified | [#48](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/48) → [#678](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/678) |

These seven are confirmed internal/code findings, not speculative Senzing product facts. Safe synthetic probes corroborated privacy, PDF-loss and snapshot-index findings. After explicit user approval, both repositories' open/closed issues were refreshed before writes. Local #42–#48 and parent #672–#678 were created, both cross-links verified, and child issues labeled `awaiting-parity` without replacing labels. All remain open until a verified containing parent tag lands locally. `escalations.json` records the verified issue/comment URLs. Raw reviewer reports preserve the earlier pre-intake observations; the consolidated review and escalation record supersede their pending-handoff dispositions.

### Existing parent matches

- **F-007:** Stale undocumented-flag claim — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/387).
- **F-008:** Discover/teardown instruction gaps — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/166).
- **F-009:** Completion question with identical answer routes — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/488).
- **F-010:** Example program/record count drift — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/616).
- **F-011:** Silent-capture copy drift — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/523).
- **F-005:** Match-key label clipping — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/463).
- **F-012:** SDK environment script cannot be sourced before config creation — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/328).
- **F-013:** Install precedes EULA consent — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/192).
- **F-014:** Engine configuration write procedure contradicts itself — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/505).
- **F-015:** System verification count/criteria/report schema disagree — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/282).
- **F-016:** Truth Set fallback cannot satisfy completion gate — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/512).
- **F-017:** PhaseC reopens settled SQLite subset choice — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/164).
- **F-018:** PhaseD describes a removed Relationship Network tab — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/225).
- **F-019:** Switch-to-PostgreSQL answer has no active migration route — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/528).
- **F-027:** Package introduction unconditionally points to optional absent keepsakes/revisit guide — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/321).
- **F-028:** Capped Entity Graph still describes its subset as the whole relationship population — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/327).
- **F-029:** Container Python visualization route points to host-only plugin assets — [existing issue](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/490).

The active renderer confirms F-005 is the same algorithm defect as parent #463, closing its earlier asset-only triage gap. F-029 matches parent #490's missing project-staging route; no actual container failure was observed.

## Validation and evidence boundaries

- `python3 scripts/audit_inventory.py --review-json docs/audits/2026-10-15-main-04ded74-complete/review.json`: **pass**, `coverage_complete: true`, no coverage errors or structural alerts.
- `check_port.py`, `check_invariants.py`, `check_maintainer_commands.py`: **pass**.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: **118 tests passed**.
- Prior #35/#36 safe direct-script probes still confirm outside-target rejection and empty/completed lifecycle behavior; no actual host hook firing claimed.
- Synthetic probe results are in `synthetic-observations.json`; PDF/model dictionaries are fixtures, never simulated Senzing entity-resolution results.
- **Actual host walkthrough, real SDK/datastore workflow, multi-platform execution and live graduation remain NOT RUN.** Static review and direct probes cannot replace the separate dry-run/manual checklist.
- **No unexpressible inherited check identified; no invariant-disposition register changes or advisory waivers.**

## Unverified leads, not confirmed findings

Golden-record terminology could not be corroborated by the live MCP searches used; irrelevant results are not absence evidence. Helper leads remain for normal-render missing-visualization coverage reporting, explicit CLI output-boundary intent, and capture redirect/subresource locality. No remote-fetch failure, exfiltration or product correctness claim follows from those leads.

The live SDK schema probe for F-007 did corroborate the documented `WHY_KEY_DETAILS` requirement; the flags route separately states its relations dependency. Selected response evidence is retained in `mcp-verification.json`.

## Recommended next action

1. Prioritize the canonical **privacy fix, [parent #672](https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/issues/672)**, tracked locally by [#42](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/42). Escalation is complete; do not implement a generated-only child workaround.
2. Implement local #39 and #41 separately from this audit.
3. Evaluate a verified containing parent release through parity-check; many inherited findings already have canonical fixes but are still present in this pinned payload.
4. Run the real host dry-run/manual checklist after fixes. Do not release on static coverage alone.


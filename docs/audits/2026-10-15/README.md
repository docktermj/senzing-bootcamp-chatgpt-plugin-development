# Production-readiness audit: initial checkpoint

**Status: INCOMPLETE. Not production-ready approval.**

## Scope and coverage

- Audited merged commit: `d70f7577f5cc59ea82b36f31200d01637b2e8d3a` (PR #34).
- Local release version: `0.5.3`; pinned parent version: `0.5.3`.
- Parent production source commit: `7e2d484f6cfe9af864762e0a0c95119d483cbb08`.
- Inventory digest: `2dbbf0f0b6f5c43dceeeb81b01d8fe5317b653dc9abd702aac5f9b49ca738606`.
- All 86 shipped files inventoried; no build-manifest/overlay structural alerts.
- 27 shipped text files read in full, including all 10 winning overlay contributions. Three of those files carry confirmed findings. The other 59 files remain deferred, including partly read curriculum and all binary visual references. Per-file observations/hashes are in `review.json`.
- None of the six whole-curriculum semantic categories is complete. Partial observations are retained without turning them into passing coverage.
- Checkout was clean before this audit. Only the requested audit artifacts are added; no shipped implementation or invariant register is changed, and nothing is committed or released.

## Confirmed local findings

### F-001 — Native edit payload is not inspected by the boundary gate

[Issue #35: Adapt the project-boundary write gate to Codex apply_patch payloads](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/35) — recommended first priority.

The shipped `scripts/write-gate.py:61` extracts `tool_input.file_path` and intentionally skips location validation when it is absent. Codex supplies native patch text in `tool_input.command`. The `Write|Edit` matcher itself is supported through aliases; changing only that matcher does not repair the parser. This contract was checked against the [official OpenAI hook documentation](https://learn.chatgpt.com/docs/hooks#pretooluse).

Direct isolated script probes show the legacy outside `file_path` control returns exit 2, while the corresponding native patch command returns exit 0 without a block. No patch is applied or outside file created. This establishes a missing plugin safety check, not a host-sandbox bypass or an observed host hook execution. The owning fix is a Codex-specific overlay/contract adaptation followed by regeneration and native-payload regression tests.

### F-002 — Active-state instructions survive terminal completion

[Issue #36: Align Socratic lifecycle guards with completed and unrecorded bootcamp state](https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development/issues/36).

The Codex controller (`scripts/socratic-controller.py:52`) only tests progress-file existence, then requires a pending-question flow. It ignores `bootcamp_complete: true`, while the Codex Stop hook (`scripts/stop-nudge.py:47`) honors that marker and graduation (`skills/graduation/SKILL.md:1111`) explicitly ends without another question. The controller therefore injects active/graduation/question instructions into a later unrelated prompt in the completed fixture. Empty `{}` also receives an active assertion and Stop block, unlike the inherited recorded-module resume/checkpoint guard (`scripts/recap_checkpoint.py:54`).

These are direct-script observations and static contradictions, not a completed host walkthrough. Local controller/Stop overlays own this adaptation. CINV-010's requirement to invoke the controller when a progress file exists must be distinguished from always injecting active pending-question instructions; any invariant clarification belongs in a separately reviewed fix.

## Deduplication and routing

All open and closed local issue pages were retrieved with pagination. Relevant closed review-operation/checklist issues #6, #19 and #20 were compared with the concrete defects; they introduce mechanisms for finding bugs but do not track these fixes. Results were refreshed before filing. Both new issue URLs were returned by successful GitHub writes and verified by issue reads.

Both findings are local Codex lifecycle/input-adapter problems; neither asserts a Senzing product fact, so live product-fact verification is not applicable to their filing. No parent issue was created or claimed. Broader curriculum and Senzing-claim review is still deferred.

## Supporting checks and limits

The merged candidate passes `scripts/check_port.py`, `scripts/check_maintainer_commands.py`, and `scripts/check_invariants.py` (29 active and 3 superseded local invariants). These structural checks do not detect the two defects above and do not close semantic coverage.

The local CINV ledger and transformation disposition register were read. The exact production-parent Git tree was inspected through its pinned commit with `truncated: false`; the complete authoritative parent invariant ledger has not yet been located and reconciled for that release. The full inherited guarantee review remains deferred, not waived. No check has been classified as an unexpressible host construction and no `audit_limitations` or invariant-disposition change was made.

`docs/test-records/0.5.3.md` explicitly records all 13 critical host checks as NOT RUN. This audit does not replace that record. No actual Codex-host lifecycle/conversation observation, SDK execution, or visual artifact rendering was performed. The isolated script fixtures are labeled direct-script evidence throughout.

## Artifacts and continuation

- `inventory.json`: complete hash-bound input inventory and overlay mapping.
- `review.json`: 27 reviewed/finding file rows, 59 deferred rows, six deferred semantic categories, and verified issue dispositions.
- `reproduce_findings.py` / `observations.json`: safe direct-script reproduction and its recorded output; no patch is applied.
- `coverage-validation.json`: current coverage result. An incomplete result and exit code 1 are expected; do not treat this as a passed audit.

Continue by reading all remaining phase files, helper scripts and examples in full, inspecting all binary artifacts with the appropriate tools, locating the pinned canonical parent guarantees, and completing the six cross-curriculum reviews. Then revalidate coverage against the unchanged snapshot, or re-inventory and reassess if inputs change. Address #35 before treating the plugin write boundary as a working safety net. Run the actual host dry run/manual checklist before release. Implementation, commits and publication require their separate workflow approvals.

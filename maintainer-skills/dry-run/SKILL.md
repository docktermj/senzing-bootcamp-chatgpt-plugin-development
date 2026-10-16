---
name: dry-run
description: Exercise the Senzing Bootcamp against the live MCP server and Codex host in ordered runtime phases, including the Socratic turn cycle, and file deduplicated local or parent-bound findings. Unavailable host checks remain advisory, never passes.
---

# Dry run

This Phase 3 operation observes the bootcamp behaving against the live Senzing MCP server and
actual Codex host. Static audit, synthetic test data about conversations, and direct script calls
cannot substitute for that evidence. Use `docs/test-checklist.md`, the shipped interaction
contract, controller, hook configuration, and current skills as the test specification.

## Prepare the observed run

Obtain a dedicated scratch workspace and evidence-record path, separate from development sources
and any real bootcamper project. Ask for missing choices with `👉`. Confirm the workspace may be
used for test-generated files and retain its evidence/artifacts; do not overwrite a real project,
replace a database, or install global dependencies without appropriate authorization. Use only
public sample data or controlled synthetic input, never real PII, credentials, or sensitive data
in MCP calls. Synthetic input is allowed; synthetic Senzing results or fabricated host observations
are not. Actual entity resolution requires the actual SDK and instance.

Identify the exact installed candidate, host build/platform, trusted hooks, parent provenance,
and shipped snapshot with `python3 scripts/dry_run_evidence.py`. Follow `docs/MANUAL_TESTING.md`
for cache-busted iteration and exact-candidate testing. Verify installed contents correspond to
the shipped candidate; a version label alone is not proof of identical payloads. Do not mix
evidence from a different build, workspace, host, or changed snapshot without rerunning it.

Read [references/evidence-format.md](references/evidence-format.md) before recording results.
Begin every check as NOT_RUN with a reason. Record actual requests, outputs, host observations,
timestamps, transcript/tool references, and artifact paths as checks execute. Keep direct-script
evidence separate from host-triggered events. Unit tests for the evidence validator are not
evidence that this dry run passed.

## Phase 1: live MCP contracts

Call the connected live Senzing `get_capabilities` first; record the actual tool response, server
version, request (including an empty object when appropriate), and discovery result. Discover
the current owning routes from that response; do not hardcode a server version or tool count.

Read the selected curriculum paths and exercise their required read-only MCP contracts against
the live server. Compare names, arguments, returned schemas, access steps, generated guidance,
and resource availability with what the bootcamp actually consumes. Follow the owning route
before making an absence claim (INV-213). Record each route probe and its result in
`curriculum-contracts`, with per-route evidence rather than a blanket assertion.

Do not send feedback, request a license, or invoke other externally consequential actions merely
to probe a contract. Inspect their declared interfaces and identify any unexercised behavior in
the record. External feedback requires the separate exact-message approval flow. Use only
MCP-grounded guidance for Senzing code and commands, never substitute hand-written ER results.

Unavailable MCP or a failed required contract blocks dependent phases; it is not an advisory
pass. Resolve the cause, file the finding, and rerun the failed phase before continuing. Keep
later checks NOT_RUN/BLOCKED with the dependency reason.

## Phase 2: hooks and scripts

After Phase 1 passes, execute bundled helpers with controlled inputs in the scratch workspace.
Record command, cwd, relevant environment, exit code, output, and created artifacts under
`script-execution`. Exercise active and inactive bootcamp contexts, empty progress, terse-answer
controller routing, Stop continuation/release/loop prevention, and applicable module helpers.
These are real script runs, but they are not proof that Codex invoked a hook.

Separately observe host-triggered lifecycle events with the actual candidate installed and hooks
reviewed/trusted. Follow TC-01 through TC-08, including visible working labels, per-answer context,
and Stop behavior. Record actual hook UI/log/transcript evidence under `hook-lifecycle` with
`codex_host` origin. Do not manually execute a hook and call that a host-triggered event.

If the host or available observation tools cannot exercise a check, record ADVISORY with the
specific limitation, affected guarantee, impact, and follow-up needed. Ask the operator for real
observations when that can resolve the gap; missing automation alone does not prove the host
lacks the feature. Never infer a pass from static definitions. A failed or incomplete prerequisite
blocks dependent conversations; record the later phase as blocked or advisory as appropriate.

## Phase 3: conversational walk

Use real bootcamper turns in the actual Codex host, following the installed shipped skills. If a
separate chat is needed, obtain explicit user authorization to create it before using the chat
creation tool; when already authorized, proceed without asking again. Supply the candidate,
workspace, and test purpose. If the user prefers manual operation, guide them through a real host
session and record their attributed observations. Never invent a conversation transcript,
generate both sides and present it as observed, or silently count a simulation as a pass.

Exercise at least two consecutive genuine question/answer cycles, including terse answers and
automatic work. For each record the incoming answer, processed-answer observation, active skill
and step, state before/after, concise commentary, automatic actions, and final question/options.
Identify the question's shipped path, exact source line/template, and any justified rendering
substitutions. Observe that automatic work continues in the same turn without intermediate
yielding, the next question has a defined origin, and nothing follows its options. Use the
`turn-cycle` evidence fields; compare the actual transcript with the interaction contract.

Also exercise resume/empty progress and checkpoints/module transitions; Module 1's generated
scenario and Module 2's existing-install/configuration paths; feedback/notes without unsolicited
external submission; and graduation/terminal completion. Record TC-09 through TC-13 plus relevant
earlier checks. Use genuine progress or explicitly documented controlled fixtures, not claimed
completion of modules that were never exercised. SDK-dependent paths require a real instance;
missing dependencies remain blocked, not approximated ER output.

Generate the actual reports, visualizations, and recap/production artifacts in the scratch
workspace. Inspect produced PDFs/images with appropriate rendering tools and verify layout and
content, not merely file existence. Record artifact paths, rendering observations, and failures
under `artifact-review`. Runtime-only failures are findings even when static checks passed.

## Route findings and hand off

For each confirmed finding, show evidence, affected guarantee, owning source, and a **local** or
**parent-bound** verdict with its reason. Local covers Codex packaging, hooks, lifecycle,
interaction, validation, and release tooling. Curriculum, content, Senzing facts, and parent-owned
behavior go to `escalate-to-parent`. Split mixed causes and re-verify relevant Senzing claims with
their live owning route before filing.

Search all relevant open/closed issues before filing, comparing behavior and evidence. File
unmatched local findings with exact build/server/host context, reproducible observed steps,
expected versus actual behavior, source ownership, and acceptance criteria. Hand parent-bound
evidence to the separate escalation workflow using an existing tracking issue when available;
if intake or authorization is missing, record a pending handoff rather than claiming it was filed.
Confirm actual issue URLs after tool calls; inspect remote state before retrying ambiguous writes.

Validate the record with `python3 scripts/dry_run_evidence.py --record /path/to/record.json`.
The helper checks phase order, evidence types, snapshot freshness, and recorded question origins;
it cannot prove that the supplied observations are true. Verify them against actual tool/host
traces. Exit 1 means invalid evidence; exit 2 means a valid record has a non-passing phase.
Advisories and skipped/deferred work remain unverified and cannot satisfy critical release gates.

Finish with actual phase outcomes, live server/host/build identities, issue links, advisory
degradations and blockers, artifact/record paths, and the recommended next action. State whether
the dry run passed, failed, or remains incomplete. Do not declare production readiness, publish,
or convert this record automatically into a passing release checklist. Prefix guidance questions
with `👉` and leave implementation to the separate issue workflow.

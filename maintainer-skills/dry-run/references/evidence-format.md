# Runtime evidence record

The JSON artifact contains `snapshot_sha256` from `scripts/dry_run_evidence.py`, `environment`,
`phases`, and `findings`. Environment requires actual `codex_build`, `platform`, `workspace`,
`tested_at`, `mcp_server_version`, and `installed_plugin_version`. The installed version must match
the candidate manifest; separately inspect installed contents and record the supporting evidence.

Use phase/check IDs and expected evidence origins from the helper's plan. Checks require `id`
and `status`: PASS, FAIL, ADVISORY, BLOCKED, or NOT_RUN. Never prefill a passing runtime record.

- PASS/FAIL require the expected `evidence_type` and an `evidence` array whose entries have
  `reference` (real tool/host log, transcript, operator observation, or artifact location) and
  `observed` (the actual result). Live MCP checks also require `tool`, `request`, and
  `response_summary`. An empty request object is valid for live discovery.
- ADVISORY requires `reason`, `impact`, and `follow_up`. This describes unavailable host behavior,
  not a pass. MCP unavailability blocks dependent phases instead of becoming an advisory success.
- BLOCKED/NOT_RUN require `reason`. Later phases must not contain executed PASS/FAIL checks until
  prerequisite phases passed. Record each unavailable later phase explicitly.

A passing `turn-cycle` check additionally needs at least two consecutive observed `turns`. Each
has `input`, `processed_answer`, `transcript_ref`, `question`, `options` (array), `final`,
`intermediate_yields` (false when no intermediate yield was observed), `automatic_steps`, and
`commentary`. Include active skill/step and before/after state evidence. `final` must contain only
that question and its options, with one `👉` question.

`question_origin` has a shipped `path`, 1-based `line`, and exact stripped source-line `template`.
`question_match_observation` describes how the actual rendered question matches that template,
including any resolved variables. The validator verifies the source exists and the template is
current; an auditor must still compare the transcript and context to establish the semantic match.

Findings require `route` (local or parent-bound), `reason`, owning `source`, `evidence`, and a
`disposition` with an actual issue/duplicate URL or an explicit pending handoff/blocker. Do not
treat a written URL as proof an issue was filed; confirm the tool result.

The helper's `record_valid` is structural evidence validation. `dry_run_passed` means all required
checks were recorded as passing with valid structure. Neither authenticates external observations
or authorizes release. Preserve raw trace references and report the real limitations alongside
the summary. Synthetic unit-test records are never evidence for the actual plugin run.

# Codex port invariants

This is the canonical list of invariants for the Senzing Bootcamp ChatGPT/Codex Plugin. They are
implementation-specific guarantees that MUST remain true when a versioned Senzing Bootcamp Claude
Plugin release is transformed into the Codex plugin.

The upstream curriculum's `INV-NNN` invariants remain authoritative for bootcamp content and
outcomes. This file does not copy or renumber them. It uses the separate permanent namespace
`CINV-NNN` for Codex packaging, lifecycle, interaction, and release behavior.

Every upstream update review MUST evaluate both sets:

1. Preserve the Claude release's applicable `INV-NNN` behavior.
2. Preserve every `CINV-NNN` below while adapting that release to Codex.

## Maintaining this file

1. Never delete, reuse, or renumber an existing `CINV-NNN` identifier. Mark an obsolete invariant
   as superseded and name its replacement.
2. Edit an existing invariant only to clarify its wording without changing its meaning. Record a
   changed guarantee as a new invariant.
3. Add new invariants using the next unused, zero-padded identifier and add the identifier to
   exactly one subject in the index in the same change.
4. Phrase every invariant as one testable MUST or ALWAYS condition.
5. Update `scripts/check_port.py` when a new invariant can be checked mechanically.
6. Treat a failed invariant as a release blocker, not as advisory documentation.

## Index by subject

- **Release source and provenance:** CINV-001, CINV-002, CINV-003, CINV-004
- **Generation and ownership:** CINV-005, CINV-006, CINV-007
- **Socratic runtime:** CINV-008, CINV-009, CINV-010, CINV-011, CINV-012, CINV-013, CINV-014
- **Codex host behavior:** CINV-015, CINV-016, CINV-017, CINV-018, CINV-019
- **Validation and release:** CINV-020, CINV-021, CINV-022, CINV-023

## Release source and provenance

- **CINV-001** — The updater MUST select the highest stable SemVer tag from the production
  `Senzing/senzing-bootcamp-claude-plugin` repository by default; it MUST NOT build implicitly from
  `main`, another branch head, or the development fork.
- **CINV-002** — The Codex plugin release version MUST exactly match the selected Claude plugin
  manifest version. A temporary local cache-buster MAY extend that version only during manual
  testing and MUST be removed before packaging.
- **CINV-003** — `UPSTREAM_VERSION`, `UPSTREAM_COMMIT`, and the generated Codex manifest MUST record
  reproducible source provenance, including the full commit for the selected production tag.
- **CINV-004** — Rebuilding from the same upstream tag and downstream source tree MUST produce the
  same plugin contents and deterministic release archive.

## Generation and ownership

- **CINV-005** — Upstream MUST remain the owner of curriculum skills, examples, helper scripts, and
  bootcamp outcomes; the Codex repository MUST transform the selected release rather than maintain
  an independent curriculum fork.
- **CINV-006** — Codex-specific behavior MUST be authored in `port/overlay/` or encoded in
  `scripts/sync_upstream.py`; direct edits made only inside `plugins/senzing-bootcamp/` MUST NOT be
  relied upon because regeneration replaces them.
- **CINV-007** — Downstream overlays MUST be applied after upstream copying and host-language
  transformation, and therefore MUST win deterministically when a downstream-owned path overlaps
  generated upstream content.

## Socratic runtime

- **CINV-008** — The generated plugin MUST ship `hooks/hooks.json`, and Codex MUST discover the
  lifecycle hooks through the supported default plugin-hook location without requiring an
  unsupported manifest field.
- **CINV-009** — Installation and manual-test instructions MUST tell the bootcamper to review and
  trust the current bundled hooks; the plugin MUST NOT claim mechanical Socratic parity when those
  hooks are untrusted or disabled.
- **CINV-010** — While `config/bootcamp_progress.json` exists, a `UserPromptSubmit` hook MUST run the
  downstream Socratic controller on every bootcamper prompt, including terse answers such as
  `yes`, `no`, and a number.
- **CINV-011** — The Socratic controller MUST read `current_module` and `current_step`, route to the
  matching shipped module skill, and inject the active skill, shared ground rules, and Codex
  interaction contract as developer context before the answer is processed.
- **CINV-012** — After processing a bootcamper answer, Codex MUST execute every automatic and
  non-yielding step in the same turn until it reaches the next question defined by a shipped skill;
  a command result, generated artifact, summary, checkpoint, status report, or phase boundary MUST
  NOT end the turn.
- **CINV-013** — During an active, incomplete bootcamp, the `Stop` hook MUST continue a turn whose
  last assistant message contains no `👉` question, MUST use Codex's stable
  `last_assistant_message` field, and MUST release its own continuation when `stop_hook_active` is
  true so it cannot loop.
- **CINV-014** — Every ordinary yielding bootcamp turn MUST end with exactly one `👉` question taken
  from the active shipped skill, followed immediately by its answer options when present and by
  nothing else; the plugin MUST NOT invent a continuation question.

## Codex host behavior

- **CINV-015** — While automatic work is running, Codex MUST provide concise intermediate
  commentary often enough for the bootcamper to know it is working; commentary MUST NOT be treated
  as the end of the bootcamp turn.
- **CINV-016** — Every bundled hook handler MUST provide a concise `statusMessage` so hook activity
  has a visible working-state label in supported Codex interfaces.
- **CINV-017** — Hook commands MUST resolve scripts with the Codex `${PLUGIN_ROOT}` variable, quote
  the script path, remain inside the plugin root, and avoid parsing the transcript when a stable
  event field provides the required value.
- **CINV-018** — Every behavior-changing bootcamp hook MUST be gated by the project-local active
  bootcamp signal so installing the plugin does not alter unrelated Codex tasks.
- **CINV-019** — Host-specific instructions MUST use current Codex terminology and visible controls;
  they MUST NOT invent a Codex command, claim to change a host-owned model or reasoning setting, or
  retain a Claude-only runtime path.

## Validation and release

- **CINV-020** — Automated port checks MUST verify the hook event set, script existence,
  `${PLUGIN_ROOT}` command form, visible status messages, active-module routing for a terse answer,
  Stop continuation for a status-only response, and Stop release for a response ending in `👉`.
- **CINV-021** — Manual testing MUST use a cache-busted local build in a new Codex task with the
  current hooks reviewed and trusted, and MUST exercise fresh start, resume, terse answers,
  non-yielding runs, visible progress, feedback, notes, checkpointing, module transitions, and
  graduation.
- **CINV-022** — Publishing MUST remain blocked until the exact-version build has passed the plugin
  validator, every skill validator, port checks, applicable upstream-derived tests, and all critical
  manual scenarios.
- **CINV-023** — The packaged archive MUST exclude transient Python caches and local-development
  state while including all generated skills, scripts, documentation, MCP configuration, manifest,
  and trusted-hook definitions required at runtime.

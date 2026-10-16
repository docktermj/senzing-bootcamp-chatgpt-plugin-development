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

1. Never delete, reuse, or renumber an existing `CINV-NNN` identifier. Record supersession only
   with the exact reciprocal metadata bullets below, each on its own line under its definition.
2. Edit an existing invariant only to clarify its wording without changing its meaning. Record a
   changed guarantee as a new invariant.
3. Add new invariants using the next unused, zero-padded identifier and add the identifier to
   exactly one subject in the index in the same change.
4. Phrase every invariant as one testable MUST or ALWAYS condition.
5. Update `scripts/check_port.py` when a new invariant can be checked mechanically.
6. Treat a failed invariant as a release blocker, not as advisory documentation.

On the replaced definition:

```markdown
  - **Superseded by:** CINV-030 — local release versions are independent of parent provenance
```

On its successor:

```markdown
  - **Supersedes:** CINV-002
```

Use zero-padded, three-digit `CINV-NNN` identifiers. Both links are required, and every target
must exist. A definition has status `superseded` only when it carries `Superseded by:`; otherwise
it is `active`. There is no third state. Prose, a status field, or strikethrough does not establish
supersession. A definition has at most one successor; a successor may have multiple separate
`Supersedes:` bullets. Self-links and cycles are invalid. Run `python3 scripts/check_invariants.py`;
`scripts/check_port.py` and CI enforce the same check.

This mechanism applies only to this ledger's `CINV-NNN` namespace. The
`invariant_disposition_register` in `tools/bootcamp-transform/contract.yaml` records how inherited
parent `INV-NNN` guarantees are honored, preserved/restated, or discounted; it is not a
supersession record and is outside this check. Parent supersessions arrive through tagged parity
updates and are handled in that register, never through local `Supersedes:` links to `INV-NNN`.

## Index by subject

- **Release source and provenance:** CINV-001, CINV-002, CINV-003, CINV-004, CINV-030, CINV-031
- **Generation and ownership:** CINV-005, CINV-006, CINV-007
- **Socratic runtime:** CINV-008, CINV-009, CINV-010, CINV-011, CINV-012, CINV-013, CINV-014
- **Codex host behavior:** CINV-015, CINV-016, CINV-017, CINV-018, CINV-019
- **Validation and release:** CINV-020, CINV-021, CINV-022, CINV-023, CINV-032
- **Public propagation:** CINV-024, CINV-025, CINV-026, CINV-027, CINV-028, CINV-029

## Release source and provenance

- **CINV-001** — The updater MUST select the highest stable SemVer tag from the production
  `Senzing/senzing-bootcamp-claude-plugin` repository by default; it MUST NOT build implicitly from
  `main`, another branch head, or the development fork.
- **CINV-002** — The Codex plugin release version MUST exactly match the selected Claude plugin
  manifest version. A temporary local cache-buster MAY extend that version only during manual
  testing and MUST be removed before packaging.
  - **Superseded by:** CINV-030 — local release versions are independent of parent provenance
- **CINV-003** — `PARENT_VERSION`, `PARENT_COMMIT`, and the generated Codex manifest MUST record
  reproducible source provenance, including the full commit for the selected production tag.
  - **Superseded by:** CINV-031 — source provenance and local release version are recorded separately
- **CINV-004** — Rebuilding from the same upstream tag and downstream source tree MUST produce the
  same plugin contents and deterministic release archive.

## Generation and ownership

- **CINV-005** — Upstream MUST remain the owner of curriculum skills, examples, helper scripts, and
  bootcamp outcomes; the Codex repository MUST transform the selected release rather than maintain
  an independent curriculum fork.
- **CINV-006** — Codex-specific behavior MUST be authored in `port/overlay/`
  or encoded in `scripts/sync_parent.py`; direct edits made only inside
  `plugins/senzing-bootcamp/` MUST NOT be relied upon because regeneration replaces them.
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

## Public propagation

- **CINV-024** — Public propagation MUST read an exact versioned development release tag and MUST
  NOT read `main`, `HEAD`, or the development working tree as its payload source.
- **CINV-025** — Public propagation MUST include all bootcamper runtime files and the public
  marketplace/README while excluding maintainer-only files and preserving public governance files.
- **CINV-026** — Public propagation MUST reject a payload that retains a reference to this
  development repository or uses British rather than American English.
- **CINV-027** — Public propagation MUST verify the public checkout identity and version, support
  review before publication, and require an explicit matching tag confirmation before pushing.
  - **Superseded by:** CINV-029 — propagation stops at the public working tree; publication is manual
- **CINV-028** — Public propagation MUST target an explicitly named, checked-out review branch;
  it MUST NOT stage, commit, tag, push, or merge directly on public `main`.
- **CINV-029** — Public propagation MUST verify the public checkout identity and tagged source
  version, support read-only preview and allowlisted working-tree apply on an existing review
  branch, and leave the Git index, commits, branches, tags, and remotes unchanged; staging,
  commits, pushes, branch creation or switching, PRs, tags, and releases are manual operations.
  - **Supersedes:** CINV-027

## Local release versioning

- **CINV-030** — The Codex plugin version MUST match `RELEASE_VERSION`, independently of the
  parent tag; temporary manual-test versions MUST be restored before packaging or release.
  - **Supersedes:** CINV-002
- **CINV-031** — `PARENT_VERSION` and `PARENT_COMMIT` MUST retain exact tagged parent provenance,
  independently of local release bumps; the build manifest MUST agree with both that provenance
  and `RELEASE_VERSION`.
  - **Supersedes:** CINV-003
- **CINV-032** — A local release MUST update its version assertions, changelog commit, and exact
  SemVer tag through an atomic branch/tag ref transaction, include a completed version-specific
  host-test record, and perform no publication or writes outside this repository; interrupted
  working-tree materialization MUST retain a recoverable journal and preserve conflicting edits.

# Codex port notes

This downstream package is generated from the matching stable SemVer tag of the Senzing Bootcamp
Claude plugin. Curriculum, examples, and helper scripts are upstream-derived. Codex-specific entry
skills, packaging, and host behavior are maintained by this repository.

Claude command files are represented as model-invocable Codex skills. Lifecycle hooks are shipped
under `hooks/hooks.json` and discovered by Codex. They restore the persistent controller that a
Socratic workflow needs: `UserPromptSubmit` rehydrates the active module on every answer, and
`Stop` keeps a status-only response from becoming a turn boundary. The remaining upstream hooks
provide resume, checkpointing, write-safety, feedback, compaction, and session-end behavior.

Codex requires the bootcamper to review and trust non-managed plugin hooks before they run. If hook
trust is declined, the skill instructions remain a best-effort fallback, but strict turn-by-turn
behavioral equivalence is not guaranteed. Treat the progress file as the durable source of truth.

`<plugin-root>` means the installed `senzing-bootcamp` plugin directory. Resolve it from the active
skill file: an upstream curriculum skill is at `<plugin-root>/skills/<skill>/SKILL.md`.

Model names and controls are host-specific and change over time. Recommend a capable Codex model
and a medium-or-higher reasoning effort for long modules, but never claim the plugin changed the
user's model or reasoning setting.

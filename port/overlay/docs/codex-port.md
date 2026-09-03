# Codex port notes

This downstream package is generated from the matching stable SemVer tag of the Senzing Bootcamp
Claude plugin. Curriculum, examples, and helper scripts are upstream-derived. Codex-specific entry
skills, packaging, and host behavior are maintained by this repository.

Claude command files are represented as model-invocable Codex skills. Claude lifecycle hooks are
not copied: checkpointing, resume, write-safety, feedback, and graduation behavior must therefore
be invoked explicitly by the active skill. Treat the progress file as the durable source of truth.

`<plugin-root>` means the installed `senzing-bootcamp` plugin directory. Resolve it from the active
skill file: an upstream curriculum skill is at `<plugin-root>/skills/<skill>/SKILL.md`.

Model names and controls are host-specific and change over time. Recommend a capable Codex model
and a medium-or-higher reasoning effort for long modules, but never claim the plugin changed the
user's model or reasoning setting.

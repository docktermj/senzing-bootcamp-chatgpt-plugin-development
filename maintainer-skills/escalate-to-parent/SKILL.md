---
name: escalate-to-parent
description: File a canonical curriculum issue in the Claude parent repository with two-way child cross-references.
---

# Escalate to parent

This is the only workflow authorized to create an issue outside this repository. Use it only for
curriculum, content, Senzing-fact, or parent-owned behavior problems. Codex packaging, hooks,
lifecycle, interaction, and release-process problems stay local.

1. Read the child issue and confirm it is parent-bound; otherwise stop.
2. Search parent issues first, then create or reuse one in
   `docktermj/senzing-bootcamp-claude-plugin-development` with the child issue URL, evidence, and
   pinned provenance.
3. Update the child with `Parent issue: #<number> (<URL>)` and the parent with the child URL.
4. The parent fixes canonically; `/parity-check` imports its tagged release. Never push changes
   from the parent into this child.

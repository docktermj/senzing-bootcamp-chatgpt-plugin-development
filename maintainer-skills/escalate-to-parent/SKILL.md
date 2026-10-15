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
3. Ensure the local `awaiting-parity` label exists (description: "Escalated to the parent; awaiting
   a verified tagged fix to land locally"). Add it to the child issue without replacing other
   labels. Record `Parent issue: #<number> (<URL>)` on the child and the child URL on the parent.
   When reusing an escalation, preserve the existing references and avoid duplicate comments.
   Verify the label and both references were saved before reporting success; report any partial
   failure. The label is the durable queue marker, independent of edits to the issue's prose.
4. The parent fixes canonically; `/parity-check` imports its tagged release. Never push changes
   from the parent into this child.

Keep the local issue open while the parent works, after the parent closes, and while the fix is
released but not yet landed here. A parent closure alone never closes the local issue. A declined
or `not_planned` parent outcome requires a human decision. `parity-check` verifies the tagged fix
and landed provenance before commenting and closing the local tracking issue.

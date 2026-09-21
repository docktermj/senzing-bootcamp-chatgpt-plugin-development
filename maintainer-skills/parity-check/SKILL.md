---
name: parity-check
description: Compare this Codex child port against a tagged Claude parent release and file local parity issues.
---

# Parity check

The parent is `docktermj/senzing-bootcamp-claude-plugin-development`. This is a pull-only child:
never write to the parent or compare against `main` or `HEAD`.

1. Read `UPSTREAM_VERSION` and `UPSTREAM_COMMIT`. Resolve the requested parent release tag; if none
   is supplied, select the latest stable SemVer tag. Reject branches, `HEAD`, prereleases, and
   untagged commits.
2. If the tag equals `UPSTREAM_VERSION`, report that the child is current and file nothing.
3. Compare the tagged parent release with pinned provenance. Do not modify this checkout.
4. Search local open parity issues and parent escalations. Link/close an existing matching issue
   rather than filing a duplicate.
5. File local issues for actionable deltas, naming the parent tag/commit, affected behavior, Codex
   adaptation, and any parent issue URL. This skill writes only to this child repository.
6. `/implement-github-issue` advances provenance only after implemented parity issues close.

Senzing-fact reductions are reasoned about only in the parent and arrive through this workflow;
children must not create a `delegate-to-mcp-server` workflow.

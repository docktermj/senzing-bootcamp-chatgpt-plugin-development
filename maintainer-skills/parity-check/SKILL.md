---
name: parity-check
description: Compare this Codex child port against a tagged Claude parent release, file parity issues, and close escalations after verified tagged fixes land.
---

# Parity check

The parent is `docktermj/senzing-bootcamp-claude-plugin-development`. This is a pull-only child:
never write to the parent or compare against `main` or `HEAD`.

1. Read `PARENT_VERSION` and `PARENT_COMMIT`. Resolve the requested parent release tag; if none
   is supplied, select the latest stable SemVer tag. Reject branches, `HEAD`, prereleases, and
   untagged commits.
2. If the tag equals `PARENT_VERSION`, skip filing release deltas, but always process the
   awaiting-parity queue below. An unchanged tag can still resolve a pending escalation.
3. Compare the tagged parent release with pinned provenance. Do not modify this checkout.
4. Search local open parity issues and parent escalations. Reuse and link an existing matching
   issue rather than filing a duplicate. Matching a report is not grounds for closing it.
5. File local issues for actionable deltas, naming the parent tag/commit, affected behavior, Codex
   adaptation, and any parent issue URL. This skill writes only to this child repository.
6. `/implement-github-issue` includes the verified parent provenance update in the parity PR.
   The fix and provenance land together when a human merges that PR and the local issue closes;
   this comparison alone never advances provenance or closes an issue awaiting the fix.

Senzing-fact reductions are reasoned about only in the parent and arrive through this workflow;
children must not create a `delegate-to-mcp-server` workflow.

## Process awaiting-parity escalations

Query all open local issues labeled `awaiting-parity`, including all result pages. For each,
resolve the recorded parent issue URL from its body or comments and verify it belongs to the
canonical parent. If missing or ambiguous, retain the label, leave the issue open, and report
the required repair. Never infer a parent issue from an unqualified number alone.

Read the parent issue's current state, closure reason, and closing event. An open or reopened
parent stays pending. A `not_planned`/declined closure is reported with both issue links for a
human decision; keep the child open and labeled. Unknown closure reasons block automatic closure.
For a completed parent issue, obtain its verified closing commit from the issue timeline or its
merged closing PR. Use the merge/squash commit that actually landed in the parent, not a PR head
or a guessed last commit. Missing or ambiguous closing evidence blocks closure.

Fetch the parent's exact tag and sufficient history to check whether the closing commit is its
ancestor. Parent issue closure without this ancestry proof stays pending. Resolve the same stable
release in the production source named by the transformation contract, verifying repository
identities and tagged plugin correspondence. If the two tagged plugin trees differ, report the
mapping blocker for human review rather than treating matching version strings as proof.

Fetch the child repository's current `origin/main`. Landed provenance must come from that ref,
never a feature branch, the working tree, or a PR merely being open. Use the read-only helper:

```bash
python3 scripts/parity_status.py --issue-json /path/to/parent-issue.json \
  --tag X.Y.Z --parent-checkout /path/to/development-parent \
  --source-checkout /path/to/production-parent
```

The JSON snapshot has `state`, `state_reason`, and `closing_commit` (full SHA), obtained from the
live parent evidence above. The helper checks tag ancestry, tagged plugin tree correspondence,
and matching provenance/build/plugin metadata in `origin/main`; it makes no mutations. Refresh
the snapshot on each run. Its statuses mean:

- `awaiting_parent` / `awaiting_release`: retain the label and wait for the parent or its release.
- `awaiting_landing`: keep the issue open and link or file the local parity work. If a newer
  release is already landed, rerun against the exact landed `PARENT_VERSION` tag to prove the fix
  is still included; do not close based only on version ordering.
- `human_decision` / `blocked`: report the reason and issue links; never close automatically.
- `ready_to_close`: the fix is in the checked tag and its matching production provenance has
  landed. Recheck that the parent has not reopened or been declined and the child still has the
  label, then post the helper's tag/commit comment with the parent issue URL and close the child
  as completed. Remove `awaiting-parity` only after successful closure.

Before retrying a partial comment/close operation, read the child again: reuse the existing
matching confirmation comment, finish only the missing step, and avoid duplicate comments.
Never close because the parent closed or because a parity report was filed. Report completed
closures and human decisions; ordinary pending items remain open. Re-run this queue after a
human merges the corresponding parity PR.

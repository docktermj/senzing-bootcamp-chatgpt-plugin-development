---
description: Preview or create an atomic local release with completed version-specific test evidence
argument-hint: VERSION=<X.Y.Z> BRANCH=<existing-review-branch> NOTES=<release-notes> ACTION=preview|apply|recover
---

Read and follow `maintainer-skills/release/SKILL.md` from this repository.

Requested version: $VERSION
Existing release branch: $BRANCH
Release notes: $NOTES
Action: $ACTION

Default to preview. Ask for missing required inputs, prefixing questions with `👉`.
Apply requires approval of the concrete release preview. Recovery uses the existing transaction
on the named branch. Reject other actions. This operation creates only local releases.

---
description: Preview or apply a tagged Senzing Bootcamp plugin to the public working tree
argument-hint: TAG=<version> PUBLIC_REPO=<absolute-path> BRANCH=<existing-review-branch> ACTION=preview|apply
---

Read and follow `.agents/skills/propagate-to-public/SKILL.md` and use its vetted
`scripts/propagate-to-public` command for this maintainer request.

Release tag: $TAG
Public checkout: $PUBLIC_REPO
Review branch: $BRANCH
Requested action: $ACTION

If the tag, public checkout, or review branch is missing, ask for it. The source MUST be the exact
versioned release tag, never `main`, `HEAD`, or the current development working
tree. Verify the public checkout, its origin, and its checked-out branch before changing anything.
The named review branch must already exist and be checked out. Never create or switch branches,
stage files, commit, push, open a PR, create a release, or tag as part of this operation.

If ACTION is omitted, do a read-only preview and report the proposed payload.
For ACTION=apply, preview first, then update only the public working tree on BRANCH for review
and testing. The Git index remains unchanged. Reject any other ACTION without making changes.

Both modes require a clean public checkout. If an earlier apply left a diff, report that the
maintainer must review and handle it manually before another propagation. Stop and
report any failed validation, unexpected path, changed public governance file,
or unreviewed difference. Report what changed in the working tree, including the source tag and
commit. The maintainer handles testing, staging, commits, branches, pushes, PRs, tags, and releases
manually after reviewing the diff.

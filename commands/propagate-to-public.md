---
description: Preview, stage, or push a tagged Senzing Bootcamp plugin on a public review branch
argument-hint: TAG=<version> PUBLIC_REPO=<absolute-path> BRANCH=<review-branch> ACTION=preview|apply|push-branch
---

Use the repository-local `propagate-to-public` skill and its vetted
`scripts/propagate-to-public` command for this maintainer request.

Release tag: $TAG
Public checkout: $PUBLIC_REPO
Review branch: $BRANCH
Requested action: $ACTION

If the tag, public checkout, or review branch is missing, ask for it. The source MUST be the exact
versioned release tag, never `main`, `HEAD`, or the current development working
tree. Verify the public checkout, its origin, and its checked-out branch before changing anything.
Never stage, commit, tag, or push on public `main`.

If ACTION is omitted, do a read-only preview and report the proposed payload.
For ACTION=apply, preview first, then stage the payload on BRANCH for testing,
without a commit or push. For ACTION=push-branch, confirm the exact tagged build
has passed release checks and manual bootcamp testing, inspect the public diff,
then use `--push-branch --confirm-tag` with the same tag. An explicit
ACTION=push-branch with exact TAG and BRANCH authorizes pushing only that review
branch, subject to the skill's safety gates. Do not treat ACTION=preview or
ACTION=apply as authorization to push.

If the public checkout already has a staged propagation diff, inspect it and use
the script's push-branch mode; its preview mode requires a clean checkout. Stop and
report any failed validation, unexpected path, changed public governance file,
or unreviewed difference. Report what was staged or pushed, including the source
tag and commit. The maintainer handles testing and manually merges into `main`.

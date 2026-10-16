---
name: release
description: Preview or create a local Senzing Bootcamp development release with atomic version/changelog/commit/tag updates and a required completed host-test record. Does not publish or propagate to the public repository.
---

# Release

Use `scripts/release.py` in `docktermj/senzing-bootcamp-chatgpt-plugin-development`. It changes
only this repository and creates a local lightweight SemVer tag. It never pushes, opens a PR,
creates a GitHub release, or writes to the public repository. Public propagation is a later,
separate operation after human review and testing.

## Prepare evidence and preview

Obtain the exact next stable local release version, release notes, and an existing, checked-out
review branch from the maintainer. Ask for missing inputs with `👉`; do not select a version or
create/switch branches as part of this operation. `main`/`master`, detached HEAD, dirty checkouts,
existing tags, and non-increasing versions are blocked. Linked worktrees are unsupported because
their Git metadata lives outside this checkout.

`RELEASE_VERSION` is the local version; `PARENT_VERSION` and `PARENT_COMMIT` remain immutable
source provenance during release. The manifest and build-manifest release version move together.
The marketplace resolves the local plugin manifest and currently has no independent version
field; do not invent one. An existing version assertion in its plugin entry is updated if present.

Before applying a release, complete the host checklist against the intended version. Use
`python3 scripts/local_version.py --candidate X.Y.Z` for the exact candidate, then restore with
`python3 scripts/local_version.py --restore`. Record genuine observations in
`docs/test-records/X.Y.Z.md` using the template, including all critical PASS results, evidence,
tester/date, hook trust, host/build metadata, and the repeated exact-version hook checks. Never
fabricate a pass, copy another version's results as evidence, or treat the historical unverified
0.5.3 record as passing. Commit the completed record on the review branch before release.

Run the plugin and skill validators as required by CINV-022 and the full local CI mirror. The
release script also runs the script tests, maintainer command check, and port check before its
transaction. Record all validation evidence; unavailable or failed required checks block release.

Preview with:

```bash
python3 scripts/release.py --version X.Y.Z --branch BRANCH --notes "Release notes"
```

Read the complete diff, version-specific record, repository identity, branch, parent provenance,
and proposed tag. The preview changes no files, commits, or tags. Ask
"👉 Do you approve creating this local release commit and tag?" and wait for explicit approval
of this preview. A request to preview or silence does not approve apply.

## Apply and recover

After approval, run the same command with `--apply`. The script prepares all release changes in
an alternate index inside `.git`, constructs the commit, and creates the branch update and tag
in one Git ref transaction with an expected-parent lease. The tag and release commit therefore
always agree on version, changelog, and test record. Parent provenance is preserved. Required
checks or signing failures before the transaction leave the released refs and working files
unchanged. Git objects prepared before a failed transaction may remain unreachable locally.

After the transaction the script materializes the committed files and index. An interruption
can leave these files behind the already-consistent branch/tag. A journal inside
`.git/release-transaction` retains the exact old/new file and index bytes. Stop other editing
and run:

```bash
python3 scripts/release.py --branch BRANCH --recover
```

Recovery finishes materialization if the refs committed, or clears the journal if neither ref
moved. It refuses conflicting human edits, moved refs, or an unexpected index; report those
cases for manual recovery. Never delete the journal, move tags, reset the checkout, or retry apply
to hide a partial failure. Inspect actual refs and the journal before reporting the outcome.

Finish with the local version, commit, tag, preserved parent tag/commit, validation results, and
the next human review step. Clearly state that the release remains local. Do not push or invoke
`propagate-to-public` automatically.

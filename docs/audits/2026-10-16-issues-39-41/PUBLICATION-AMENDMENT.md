# Publication amendment

The user approved publication of the original reviewed diffs on 2026-10-16. Before committing,
the staged whitespace check caught an extra EOF blank line in each of three new Python files.
The earlier unstaged check had not covered untracked files. No commit, push or PR was made.

Corrections relative to the originally approved diff:

- Issue 39: remove one EOF blank line in `scripts/test_model_guidance.py`.
- Issue 41: remove one EOF blank line in `scripts/example_pdf.py` and
  `scripts/test_example_pdf.py`.
- Issue 41: refresh `port/artifacts/bootcamp_recap.example.json` generator SHA256 from
  `a37b99112e37fa5d615ef464b10d88c07090593c4a8239e3dcc8aab7ff52bf16` to
  `35beabd2c5c9a70c635f18fbd8612ea68481e33939c9e01a45e73696fb5aa29e`.

No executable behavior, PDF bytes, manifest output, parent pin or release pin changed from the
previous review. The PDF SHA256 remains
`23910c26aa3f90993305a1aa1b0c2173077d76e106acb41b04abb5a1319fd79c`.
Both package checksums still match the previous deterministic builds.

Every current workflow command and full unittest discovery were rerun successfully in each
worktree: 126 tests per branch. Both staged complete diffs now pass `git diff --cached --check`.
The complete revised diffs, including new files and binary data, are `issue-39-revised.patch`
and `issue-41-revised.patch`. The original patches are retained for comparison.

Branches, destination, proposed PR titles/bodies, invariant review and limitations remain exactly
as recorded in README.md. Changes are staged but uncommitted. Gate 2 requires renewed approval
for these corrected diffs before committing, pushing and opening the two PRs.

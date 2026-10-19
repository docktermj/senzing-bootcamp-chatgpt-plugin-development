# Issue 51: Gate 2 publication review

Local implementation is complete on branch `51-docktermj-1`, based on reviewed main
`686d8fb5e7018ac569b464533043b4aa9cacb399`. No files are staged, committed or pushed and no PR
has been created. Gate 1 was approved and recorded on issue 51; Gate 2 remains pending.

Worktree: `/home/senzing/.codex/worktrees/issue-39-model-guidance/senzing-bootcamp-chatgpt-plugin-development`.
This reuses the clean merged issue-39 checkout; the implementation branch is issue 51, not 39.
The primary checkout remains unchanged main with the pre-existing and new audit evidence untracked.
These audit files are review evidence and are not proposed PR payload.

## Complete diff and scope

`issue-51.patch` includes every tracked change, all new files and Git binary deltas.
SHA256: `d7329e5d0bbb166db2831331346e0f73b14b44c8740ab226ce7778905f3cabc0`.
`files.txt` inventories all 62 changed/new files; `tracked-stat.txt` summarizes tracked changes only.
`parent-delta-coverage.json` accounts for each of the 49 parent plugin delta paths.

- Exact production tag 0.6.1: `d3d99523f88957cd9dda2d29375892bf2c557663`.
- PARENT_VERSION/PARENT_COMMIT, reviewed contract register, build manifest and generated plugin
  advance together. RELEASE_VERSION and the Codex manifest remain 0.5.3.
- All 84 target parent files classify. Claude manifest/graduate command are explicitly ignored;
  the Codex-owned model-selection overlay wins. The new video renderer is included.
- Contract fixes consume complete parent model tokens and adapt the revised feedback example.
  Existing native canonical guidance, graduation delegation and lifecycle/write-safety overlays survive.
- A contract text variable binds example version assertions to RELEASE_VERSION, preventing a
  misleading 0.6.1 cover on a 0.5.3 local plugin. The executor expands text-transform variables.
- PDF refresh accepts only the exact reviewed tag/checkout/manifest/register commit. It can prepare
  the new binary before current pins advance, without weakening stale-input verification or manually
  updating provenance. The refreshed owned binary/record is included with regenerated output.
- Seventeen new regressions cover import/version/provenance, model negative controls, policy
  preservation, refresh rejection, video validation/local paths/preserved output/frame drawing and
  both actual PDF renderers. A pre-existing unmatched-file fixture now derives the reviewed version
  so it tests classification rather than failing prematurely on a hardcoded old version.
- CI adds a real optional-dependency matrix, declared dependencies and full-discovery runner that
  verifies availability and honest rich-path skips. Porting and source-scope review docs are included.

## Invariants and ownership

`docs/parent-0.6.1-review.md` in the diff records reviewed source provenance, every new invariant
subject and changed existing subjects. Existing explicit Codex restatements are retained; no
invariant is discounted. Parent-development-only conditions keep their source scope and are not
misrepresented as copied or runtime-tested child machinery. CINV provenance, regeneration,
overlay precedence, host safety, version independence and deterministic packaging remain checked.

The immutable development and production plugin trees differ only in manifest homepage/repository
URLs, explicitly accepted by the maintainer. No tag is modified, no parent maintainer tooling is
transplanted and parity_status's strict automatic closure check is not relaxed.

Local issues 40 and 42–48 remain open/awaiting-parity. Their linked parent issues were open during
readiness. This PR must not claim their fixes or close them. No new local release or public
propagation is performed. Live Senzing readiness evidence remains in the preceding parity audit;
no new SDK call implementation was invented locally.

## Validation results

- Every current inline CI validation command passes in both fresh virtual environments; the
  conditional rich-install command was run separately and is logged in `issue51-rich-install.log`.
- Full discovery, present: 151 tests, no skips. Absent: 151 tests, two expected documented skips
  (rich PDF rendering and Pillow frame drawing); both paths run the stdlib PDF test.
- The tagged parent's actual video tests, with only REPO_ROOT rebound before module execution,
  run against the imported child renderer: 131 tests, one expected rich-environment skip because
  imageio-ffmpeg is installed; absent: 131 tests, 42 documented optional-dependency skips.
- The rich skip's actual missing-ffmpeg CLI case was additionally run in the existing Pillow/no-
  imageio environment: one test passes, no skip. Missing-capability exit behavior is not unmeasured.
- Upstream test source SHA256: `e618f6f860224371d08636949b8d36685a286a1c0f6f74a3efbd5e312358b4b2`.
  Source tag remains unchanged. Initial diagnostic failures caused by rebinding the test's VIDEO
  global after its default arguments were bound were corrected in the temporary adapter; they
  were not parent defects. The final logs reflect the root-only pre-import adapter.
- Two final exact-parent syncs produce identical plugin-tree/pin/manifest inventories. Two final
  packages produce identical ZIP bytes. Two final PDF renders are byte-identical.
- The 32-page refreshed PDF was visually reviewed, including the corrected 0.5.3 cover and
  certificate. All 13 referenced screenshots remain embedded. PDF SHA256:
  `54e3539b19b42a1d22caedb62cbc3e6f56ad0ad72f4db61dc05c4c1129da4c7e`.
- Tracked and every untracked proposed file pass whitespace checks. Index remains empty.

Logs and checksum inventories alongside this report are the actual evidence, not remote CI.
No GitHub Actions results exist for the unpublished branch yet.

## Remaining limitations

Manual Codex hook firing/conversational behavior, live SDK resolution, Windows PowerShell 5.1 and
native macOS/Windows speech behavior were not run. Static instructions and synthetic helper tests
do not certify them. Version-specific critical host tests still block a subsequent release.

The example is a historical run, not a new SDK session. Inherited screenshot clipping, historical
count/terminology inconsistencies and pre-existing generic model-control wording in historical Q&A
remain limitations; they are not silently rewritten as curriculum fixes. The eight escalations
and other pinned inherited defects are not repaired by importing 0.6.1. No production-readiness
or complete runtime parity claim is made.

## Proposed publication

Destination: `docktermj/senzing-bootcamp-chatgpt-plugin-development`, base `main`.
Branch: `51-docktermj-1`.
PR title: **feat: import stable parent 0.6.1 for Codex**

Proposed PR body:

```markdown
## Summary
- Import the complete stable production parent 0.6.1 plugin delta at d3d99523f88957cd9dda2d29375892bf2c557663.
- Advance parent pins, reviewed invariant register and generated provenance together; keep local release 0.5.3.
- Preserve Codex lifecycle/model overlays, adapt complete model tokens and feedback examples, and refresh the verified Codex example PDF.
- Bind example version metadata to the independent local release and allow refresh against the exact reviewed target before sync.
- Add 17 regressions, optional renderer dependency declarations and a real present/absent CI matrix.

## Validation
- All current CI validation commands pass locally in both dependency environments.
- Full discovery: 151 tests; present has no skips, absent has two declared optional skips.
- Tagged upstream video suite: 131 tests in each environment; one present/42 absent optional skips. The present missing-ffmpeg skip was separately exercised successfully with Pillow and no imageio-ffmpeg.
- Two exact-parent rebuild/package builds and two PDF renders are byte-identical; all 32 PDF pages reviewed and 13 screenshots embedded.
- Complete proposed files pass whitespace checks. No actual Codex host/SDK or native Windows/macOS speech pass is claimed.

## Provenance and boundaries
- Development tag 0.6.1 is 7cfdcd88a3f51623e826171cd64a3a409308c7d1; production tag is d3d99523f88957cd9dda2d29375892bf2c557663.
- Their only plugin-tree difference is manifest homepage/repository URLs, accepted as production metadata mapping; neither tag or automatic parity-closure policy is altered.
- Issues #40 and #42–#48 remain awaiting parent fixes/parity. Known historical example and inherited defects remain; this is not a release or public propagation.

Closes #51
```

Recommended next step: approve Gate 2 for committing this exact reviewed diff, pushing the named
branch and opening the proposed PR. Check remote CI and review before human merge. Re-run parity
queue processing after the provenance lands; do not close pending escalations based on this PR alone.

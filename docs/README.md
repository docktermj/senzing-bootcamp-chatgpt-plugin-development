# Senzing Bootcamp ChatGPT Plugin

A version-pinned Codex IDE port of the
[Senzing Bootcamp Claude Plugin](https://github.com/Senzing/senzing-bootcamp-claude-plugin).
It guides a bootcamper through a hands-on Senzing entity-resolution curriculum while using the
hosted Senzing MCP server for current, grounded product guidance.

The Codex port ships trusted lifecycle hooks as well as skills. The per-prompt controller restores
the active module on every answer, and the Stop hook keeps the Socratic workflow from yielding on a
status-only response. Manual testing must include reviewing and trusting these hooks.

The generated plugin is in `plugins/senzing-bootcamp`. Its version always matches the latest stable
SemVer upstream tag used to build it; `main` is never used as an implicit source.

## Maintainer quick start

```bash
python3 scripts/sync_upstream.py
python3 scripts/check_port.py
python3 /home/senzing/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/senzing-bootcamp
```

See `docs/PORTING.md` for the synchronization and ownership model and
`specs/INVARIANTS.md` for permanent Codex implementation guarantees, and
`docs/MANUAL_TESTING.md` for the pre-release test gate, and `docs/test-checklist.md` plus
`docs/test-records/` for the recorded host-behavior evidence.

The Codex desktop app is sufficient for manual testing. The optional `codex` terminal program is
only needed by maintainers who prefer a command-line installation workflow.

## Propagate a tagged release to a review branch

Use the repository-local `$propagate-to-public` skill in Codex or run the command below. It reads
only the specified development release tag; it does not copy the current working tree. The public
checkout must be clean, on the named review branch, and have
`Senzing/senzing-bootcamp-chatgpt-plugin` as `origin`. Never propagate directly to `main`.

```bash
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin --branch 3-docktermj-1
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin --branch 3-docktermj-1 --apply
```

The first command is a read-only preview. The second stages a reviewable diff on the branch
without committing or pushing. After testing, if the maintainer explicitly asks to share the
branch:

```bash
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin --branch 3-docktermj-1 --push-branch --confirm-tag 0.5.3
```

This creates a commit and pushes **only the review branch**. It does not tag or touch public
`main`; the maintainer tests and manually merges or pulls into `main`. The command mirrors only
the plugin payload, marketplace manifest, and bootcamper README; public governance files and
development-only files remain untouched.

To install the optional local slash-command shim, run
`python3 scripts/install_propagate_prompt.py --install` and restart Codex or open a new chat.
Then invoke, for example,
`/prompts:propagate-to-public TAG=0.5.3 PUBLIC_REPO=/path/to/senzing-bootcamp-chatgpt-plugin BRANCH=3-docktermj-1 ACTION=preview`.
Set `ACTION=apply` to stage or `ACTION=push-branch` to share the reviewed branch. The prompt is
maintained in `commands/propagate-to-public.md` but must be installed into the user's Codex home;
Codex does not load repository-local custom prompts or support a bare `/propagate-to-public`
alias. The shared, non-deprecated alternative remains `$propagate-to-public`.

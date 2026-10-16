# Senzing Bootcamp ChatGPT Plugin

A version-pinned Codex IDE port of the
[Senzing Bootcamp Claude Plugin](https://github.com/Senzing/senzing-bootcamp-claude-plugin).
It guides a bootcamper through a hands-on Senzing entity-resolution curriculum while using the
hosted Senzing MCP server for current, grounded product guidance.

The Codex port ships trusted lifecycle hooks as well as skills. The per-prompt controller restores
the active module on every answer, and the Stop hook keeps the Socratic workflow from yielding on a
status-only response. Manual testing must include reviewing and trusting these hooks.

The generated plugin is in `plugins/senzing-bootcamp`. Its local version is `RELEASE_VERSION`;
`PARENT_VERSION` and `PARENT_COMMIT` record the stable parent tag used to build it. Local releases
do not change that provenance, and `main` is never used as an implicit parent source.

## Maintainer quick start

```bash
python3 scripts/sync_parent.py
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

## Propagate a tagged release to the public working tree

First create a local development release using `commands/release.md` and
`maintainer-skills/release/SKILL.md`. The release operation requires a completed version-specific
host-test record, previews its changes, and updates the release commit and tag atomically after
approval. It leaves publication to the maintainer. See `docs/PORTING.md` for the release and
recovery procedure.

Use the repository-local `$propagate-to-public` skill in Codex or run the command below. It reads
only the specified development release tag; it does not copy the current working tree. The public
checkout must be clean, already on the named review branch, and have
`Senzing/senzing-bootcamp-chatgpt-plugin` as `origin`. Never propagate directly to `main`.

```bash
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin --branch 3-docktermj-1
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin --branch 3-docktermj-1 --apply
```

The first command is a read-only preview. The second writes a reviewable diff to the public
working tree and stops, leaving the Git index unchanged. The command never stages files,
commits, creates or switches branches, pushes, opens PRs, tags, or creates releases. The
maintainer reviews and tests the diff, then performs publication manually. The command mirrors only
the plugin payload, marketplace manifest, and bootcamper README; public governance files and
development-only files remain untouched.

To install the optional local slash-command shim, run
`python3 scripts/install_propagate_prompt.py --install` and restart Codex or open a new chat.
Then invoke, for example,
`/prompts:propagate-to-public TAG=0.5.3 PUBLIC_REPO=/path/to/senzing-bootcamp-chatgpt-plugin BRANCH=3-docktermj-1 ACTION=preview`.
Set `ACTION=apply` to update the working tree for review. Only `preview` and `apply` are supported.
The prompt is
maintained in `commands/propagate-to-public.md` but must be installed into the user's Codex home;
Codex does not load repository-local custom prompts or support a bare `/propagate-to-public`
alias. The shared, non-deprecated alternative remains `$propagate-to-public`.

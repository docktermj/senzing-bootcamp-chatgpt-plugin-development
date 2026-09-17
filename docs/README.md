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
`docs/MANUAL_TESTING.md` for the pre-release test gate.

The Codex desktop app is sufficient for manual testing. The optional `codex` terminal program is
only needed by maintainers who prefer a command-line installation workflow.

## Publish a tagged release

Use the repository-local `$propagate-to-public` skill in Codex or run the command below. It reads
only the specified development release tag; it does not copy the current working tree. The public
checkout must be clean, on `main`, and have `Senzing/senzing-bootcamp-chatgpt-plugin` as `origin`.

```bash
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin --apply
```

The first command is a read-only preview. The second stages a reviewable public diff without
committing or pushing. After reviewing that diff and explicitly deciding to publish the same tag:

```bash
scripts/propagate-to-public --tag 0.5.3 --public-repo /path/to/senzing-bootcamp-chatgpt-plugin --publish --confirm-tag 0.5.3
```

Publication creates a matching public commit and tag, then atomically pushes both. The command
mirrors only the plugin payload, marketplace manifest, and bootcamper README; public governance
files and development-only files remain untouched. A bare repository-shared `/propagate-to-public`
slash command is not available in Codex. Use `$propagate-to-public` or the `/skills` selector.

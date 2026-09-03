# Senzing Bootcamp ChatGPT Plugin

A version-pinned Codex IDE port of the
[Senzing Bootcamp Claude Plugin](https://github.com/Senzing/senzing-bootcamp-claude-plugin).
It guides a bootcamper through a hands-on Senzing entity-resolution curriculum while using the
hosted Senzing MCP server for current, grounded product guidance.

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
`docs/MANUAL_TESTING.md` for the pre-release test gate.

The Codex desktop app is sufficient for manual testing. The optional `codex` terminal program is
only needed by maintainers who prefer a command-line installation workflow.

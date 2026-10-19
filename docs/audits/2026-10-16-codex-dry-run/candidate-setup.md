# Cache-busted candidate setup

Prepared 2026-10-16 15:28:50 UTC from merged main e374ed651fae431782fa60690201610f285f2e45.

- Local test manifest version: `0.5.3+codex.local-20261016-152850`.
- `RELEASE_VERSION` remains `0.5.3`; parent provenance remains `0.6.1`.
- This is a temporary local build suffix, not a release, commit, push, or tag.
- The prior `record.json` describes the preflight snapshot before this manifest change; it is historical evidence and cannot certify this candidate. A fresh record and live probes are required after installation.

## Installation prerequisite

`codex plugin marketplace list` failed with exit 1: configured `personal` points to `/home/senzing/github.com-local/docktermj/senzing-bootcamp-chatgpt-plugin-development`, where no supported marketplace manifest was found.

The candidate marketplace root is `/home/senzing/github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development`; its `.agents/plugins/marketplace.json` declares `personal` and the local plugin source. Point the marketplace to this root before reinstalling. Do not reinstall from a remote unchanged release and assume it contains this local candidate.

In the desktop Plugins panel, reinstall the local candidate and review/trust its lifecycle hooks. Report the installed version and whether the hook trust prompt appeared. Installed contents must then be compared with the candidate inventory, not merely its version label.

The user authorized a separate scratch-workspace chat, conditional on reinstall and hook trust. No chat has been created yet, because these prerequisites are not verified. The authorized workspace is `/tmp/senzing-codex-dry-run-2026-10-16/`.

After testing, restore the manifest with `python3 scripts/local_version.py --restore`. Do not commit the local build suffix as a release version.

---
name: propagate-to-public
description: Publish a tagged Senzing Bootcamp ChatGPT plugin development release to the Senzing public plugin repository. Maintainer-only release workflow; never use for a bootcamper session or an untagged working tree.
---

# Propagate to public

This is a maintainer skill. Its source is an exact SemVer tag in this development repository, never `main`, `HEAD`, or the current working tree. Its destination is a clean checkout whose `origin` is exactly `Senzing/senzing-bootcamp-chatgpt-plugin`. Do not include this skill in the public payload.

## Shipped manifest

- Mirror `plugins/senzing-bootcamp/**`, including skills, hooks, scripts, MCP configuration, examples, and plugin manifest. Exclude Python caches, test caches, tests, and editor files.
- Publish `.agents/plugins/marketplace.json` with the public marketplace name and the tagged plugin source path.
- Publish a bootcamper-facing root `README.md` with the public marketplace URL and tagged example links.
- Preserve the public repository's `.github/`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.vscode/`, `.gitignore`, and `CHANGELOG.md`.
- Exclude the development repository's `docs/`, `specs/`, `port/`, top-level `scripts/`, tests, CI, upstream provenance files, and any other path not in the allowlist.

## Release procedure

1. Obtain the exact development release tag from the maintainer or verify the intended latest versioned release. Never infer a release from a branch. Confirm the tag and `plugin.json` version match.
2. Confirm the release's automated checks and manual bootcamp testing were completed. A release tag alone is not evidence that the bootcamp was tested.
3. Locate the public checkout. Do not guess an absent destination or clone into an arbitrary directory. Confirm it is the intended public repository and clean.
4. Run `python3 scripts/propagate_to_public.py --tag VERSION --public-repo PATH` for a read-only preview. Inspect the reported additions, changes, and scoped deletions. The command validates required runtime files, development-repository references, and American English spelling.
5. If the preview passes, run with `--apply` to stage the shippable tree in the public checkout. Inspect its diff and, where practical, install/test the staged plugin in Codex.
6. Publish only after the maintainer explicitly requests publication of that exact tag: run with `--publish --confirm-tag VERSION`. The command checks the source tag against the development remote, creates a public commit and matching public tag, then pushes both atomically. Do not push an unreviewed diff or bypass a validation failure.
7. Report the source tag and commit, public commit/tag, validation results, and any push failure. If publication fails after a local commit, do not delete or rewrite it automatically; report the state for recovery.

The deterministic script owns all file operations. Do not hand-copy the payload, broaden its delete scope, use a development branch, or remove a check to make a release pass. A newly needed runtime path requires updating the allowlist and its tests together.
Read the proposed public prose once for American English beyond the automated common-spelling check.

Codex's repository-shared invocation is `$propagate-to-public` (or the `/skills` selector). A bare `/propagate-to-public` custom prompt cannot be installed from a repository; Codex's custom prompts are deprecated and user-local.

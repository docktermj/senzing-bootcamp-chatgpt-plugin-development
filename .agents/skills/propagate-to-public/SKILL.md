---
name: propagate-to-public
description: Stage a tagged Senzing Bootcamp ChatGPT plugin development release on a public review branch for testing and manual merge. Maintainer-only; never use for a bootcamper session or an untagged working tree.
---

# Propagate to public

This is a maintainer skill. Its source is an exact SemVer tag in this development repository, never `main`, `HEAD`, or the current working tree. Its destination is a clean checkout whose `origin` is exactly `Senzing/senzing-bootcamp-chatgpt-plugin`, checked out on the maintainer's named review branch. Never stage, commit, tag, or push directly on public `main`. Do not include this skill in the public payload.

## Shipped manifest

- Mirror `plugins/senzing-bootcamp/**`, including skills, hooks, scripts, MCP configuration, examples, and plugin manifest. Exclude Python caches, test caches, tests, and editor files.
- Publish `.agents/plugins/marketplace.json` with the public marketplace name and the tagged plugin source path.
- Publish a bootcamper-facing root `README.md` with the public marketplace URL and tagged example links.
- Preserve the public repository's `.github/`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.vscode/`, `.gitignore`, and `CHANGELOG.md`.
- Exclude the development repository's `docs/`, `specs/`, `port/`, top-level `scripts/`, tests, CI, upstream provenance files, and any other path not in the allowlist.

## Release procedure

1. Obtain the exact development release tag from the maintainer or verify the intended latest versioned release. Never infer a release from a branch. Confirm the tag and `plugin.json` version match.
2. Confirm the release's automated checks and manual bootcamp testing were completed. A release tag alone is not evidence that the bootcamp was tested.
3. Locate the public checkout and obtain the exact review branch name. Do not guess either. Confirm the checkout is clean and the named branch is checked out. If it is on `main`, switch only when safe and authorized. For the current release, the maintainer specified `3-docktermj-1`.
4. Run `python3 scripts/propagate_to_public.py --tag VERSION --public-repo PATH --branch BRANCH` for a read-only preview. Inspect additions, changes, and scoped deletions. The command validates required runtime files, development-repository references, and American English spelling.
5. If the preview passes, run with `--apply` to stage the shippable tree **on that branch**. Inspect the staged diff and let the maintainer test the branch. Do not commit, push, tag, or merge as part of the default propagation step.
6. Only if the maintainer explicitly asks to share the reviewed branch, run with `--push-branch --confirm-tag VERSION`. This commits and pushes only the named review branch. It does not create a public tag or touch `main`.
7. Report the source tag and commit, review branch, validation results, and what remains local versus pushed. The maintainer performs testing and manually merges or pulls the branch into `main`; do not do that for them.

The deterministic script owns all file operations. Do not hand-copy the payload, broaden its delete scope, use a development branch, or remove a check to make a release pass. A newly needed runtime path requires updating the allowlist and its tests together.
Read the proposed public prose once for American English beyond the automated common-spelling check.

Codex's repository-shared invocation is `$propagate-to-public` (or the `/skills` selector). The repository also maintains `commands/propagate-to-public.md` as an optional local custom-prompt shim. Install it with `python3 scripts/install_propagate_prompt.py --install`, then invoke `/prompts:propagate-to-public TAG=VERSION PUBLIC_REPO=/absolute/path BRANCH=name ACTION=preview|apply|push-branch`. Custom prompts are deprecated and user-local; a bare `/propagate-to-public` command cannot be installed from a repository.

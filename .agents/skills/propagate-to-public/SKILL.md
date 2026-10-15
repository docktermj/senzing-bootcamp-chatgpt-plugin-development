---
name: propagate-to-public
description: Preview or apply a tagged Senzing Bootcamp development release to the public working tree for manual review and testing. Maintainer-only; never use for a bootcamper session or an untagged working tree.
---

# Propagate to public

This is a maintainer skill. Its source is an exact SemVer tag in this development repository, never `main`, `HEAD`, or the current working tree. Its destination is a clean checkout whose `origin` is exactly `Senzing/senzing-bootcamp-chatgpt-plugin`, already checked out on the maintainer's named review branch. This operation stops at the public working tree: it never stages files, commits, creates or switches branches, pushes, opens a PR, tags, or creates a release. Do not include this skill in the public payload.

## Shipped manifest

- Mirror `plugins/senzing-bootcamp/**`, including skills, hooks, scripts, MCP configuration, examples, and plugin manifest. Exclude Python caches, test caches, tests, and editor files.
- Publish `.agents/plugins/marketplace.json` with the public marketplace name and the tagged plugin source path.
- Publish a bootcamper-facing root `README.md` with the public marketplace URL and tagged example links.
- Preserve the public repository's `.github/`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.vscode/`, `.gitignore`, and `CHANGELOG.md`.
- Exclude the development repository's `docs/`, `specs/`, `port/`, top-level `scripts/`, tests, CI, upstream provenance files, and any other path not in the allowlist.

## Release procedure

1. Obtain the exact development release tag from the maintainer or verify the intended latest versioned release. Never infer a release from a branch. Confirm the tag and `plugin.json` version match.
2. Confirm the release's automated checks and manual bootcamp testing were completed. A release tag alone is not evidence that the bootcamp was tested.
3. Locate the public checkout and obtain the exact existing review branch name. Do not guess either. Confirm the checkout is clean and the named branch is checked out. If it is on another branch or `main`, stop and ask the maintainer to prepare the checkout separately; propagation never switches or creates branches.
4. Run `python3 scripts/propagate_to_public.py --tag VERSION --public-repo PATH --branch BRANCH` for a read-only preview. Inspect additions, changes, and scoped deletions. The command validates required runtime files, development-repository references, and American English spelling.
5. If the preview passes and apply was requested, run with `--apply` to update only the allowlisted files in the public working tree. Inspect the unstaged diff and leave the Git index unchanged. Both modes require a clean checkout; an existing propagation diff must be handled manually before rerunning.
6. Report the source tag and commit, review branch, validation results, and working-tree changes. Stop here. The maintainer reviews and tests the diff, then performs staging, commits, pushes, PRs, tags, releases, and merges manually as separate steps. There is no publication mode in this operation.

The deterministic script owns all file operations. Do not hand-copy the payload, broaden its delete scope, use a development branch, or remove a check to make a release pass. A newly needed runtime path requires updating the allowlist and its tests together.
Read the proposed public prose once for American English beyond the automated common-spelling check.

Codex's repository-shared invocation is `$propagate-to-public` (or the `/skills` selector). The repository also maintains `commands/propagate-to-public.md` as an optional local custom-prompt shim. Install it with `python3 scripts/install_propagate_prompt.py --install`, then invoke `/prompts:propagate-to-public TAG=VERSION PUBLIC_REPO=/absolute/path BRANCH=name ACTION=preview|apply`. Custom prompts are deprecated and user-local; a bare `/propagate-to-public` command cannot be installed from a repository.

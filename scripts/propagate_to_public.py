#!/usr/bin/env python3
"""Stage or push a tagged bootcamper payload on a public review branch."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
PLUGIN = "plugins/senzing-bootcamp/"
MARKETPLACE = ".agents/plugins/marketplace.json"
PUBLIC_SLUG = "Senzing/senzing-bootcamp-chatgpt-plugin"
DEVELOPMENT_SLUG = "docktermj/senzing-bootcamp-chatgpt-plugin-development"
REQUIRED = {
    "plugins/senzing-bootcamp/.codex-plugin/plugin.json",
    "plugins/senzing-bootcamp/.mcp.json",
    "plugins/senzing-bootcamp/hooks/hooks.json",
    "plugins/senzing-bootcamp/skills/start-bootcamp/SKILL.md",
    "plugins/senzing-bootcamp/skills/bootcamp-onboarding/SKILL.md",
    "plugins/senzing-bootcamp/skills/graduation/SKILL.md",
    "plugins/senzing-bootcamp/scripts/socratic-controller.py",
    MARKETPLACE,
    "README.md",
}
BRITISH = re.compile(
    r"\b(?:colour|colours|behaviour|behaviours|centre|centres|organise|"
    r"organised|organisation|organisations|analyse|analysed|optimise|"
    r"optimisation|modelling|catalogue|prioritise|recognise|favourite|"
    r"favour|labour|theatre|licence|visualise|normalise|customise|"
    r"initialise|authorise|specialise|utilise)\b",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".yaml", ".yml", ".sh", ".txt"}
DEV_ONLY_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".venv", ".history", ".idea", "tests"}
DEV_ONLY_NAMES = {".DS_Store", ".coverage"}


def git(repo: Path, *args: str, input_data: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], input=input_data, capture_output=True
    )
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip() or f"git {args[0]} failed")
    return result.stdout


def remote_slug(url: str) -> str:
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?/?", url)
    return match.group(1) if match else ""


def tagged_payload(tag: str) -> tuple[dict[str, bytes], str]:
    if not re.fullmatch(r"(?:v)?[0-9]+\.[0-9]+\.[0-9]+", tag):
        raise ValueError("--tag must be an exact stable SemVer tag, such as 0.5.3")
    if tag not in git(SOURCE, "tag", "--list", tag).decode().splitlines():
        raise ValueError(f"tag {tag!r} is not present locally; fetch and verify the release tag first")
    commit = git(SOURCE, "rev-parse", f"refs/tags/{tag}^{{commit}}").decode().strip()
    entries = git(SOURCE, "ls-tree", "-rz", f"refs/tags/{tag}").split(b"\0")
    payload: dict[str, bytes] = {}
    for entry in entries:
        if not entry:
            continue
        meta, raw_path = entry.split(b"\t", 1)
        mode = meta.split(b" ", 1)[0]
        path = raw_path.decode()
        if path not in {MARKETPLACE, "README.md"} and not path.startswith(PLUGIN):
            continue
        if mode not in {b"100644", b"100755"}:
            raise ValueError(f"unsupported tagged file type: {path}")
        parts = set(Path(path).parts)
        if parts & DEV_ONLY_PARTS or Path(path).name in DEV_ONLY_NAMES or path.endswith((".pyc", ".pyo", ".swp")):
            continue
        payload[path] = git(SOURCE, "show", f"refs/tags/{tag}:{path}")
    missing = REQUIRED - payload.keys()
    if missing:
        raise ValueError(f"tag {tag} lacks required runtime files: {', '.join(sorted(missing))}")
    version = json.loads(payload["plugins/senzing-bootcamp/.codex-plugin/plugin.json"])["version"]
    if version != tag.removeprefix("v"):
        raise ValueError(f"plugin version {version!r} does not match tag {tag!r}")

    readme = payload["README.md"].decode()
    readme = readme.replace("https//github.com/Senzing/...", f"https://github.com/{PUBLIC_SLUG}")
    readme = readme.replace('choose "Personal" tab', 'choose the "Senzing" marketplace')
    readme = readme.replace('choose "Personal" tab.', 'choose the "Senzing" marketplace.')
    readme = readme.replace('From a terminal window, start ChatGPT.\n   Example:\n\n    ```console\n    chatgpt\n    ```\n\n    - In macOS, start "ChatGPT" and open a new project on an empty directory.\n\n', 'Open the Codex desktop app.\n\n')
    readme = readme.replace(
        "https://raw.githubusercontent.com/docktermj/senzing-bootcamp-claude-plugin-development/refs/heads/main/",
        f"https://raw.githubusercontent.com/{PUBLIC_SLUG}/refs/tags/{tag}/",
    )
    payload["README.md"] = readme.encode()
    marketplace = json.loads(payload[MARKETPLACE])
    marketplace["name"] = "senzing"
    marketplace["interface"]["displayName"] = "Senzing"
    payload[MARKETPLACE] = (json.dumps(marketplace, indent=2) + "\n").encode()

    for path, data in payload.items():
        if Path(path).suffix not in TEXT_SUFFIXES and Path(path).name not in {"SKILL.md", ".mcp.json"}:
            continue
        if path == MARKETPLACE:
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"non-UTF-8 text: {path}") from exc
        content = content.replace(DEVELOPMENT_SLUG, PUBLIC_SLUG)
        if path == "README.md":
            content = content.replace(
                f"https://raw.githubusercontent.com/{PUBLIC_SLUG}/refs/heads/main/",
                f"https://raw.githubusercontent.com/{PUBLIC_SLUG}/refs/tags/{tag}/",
            )
        payload[path] = content.encode()
    validate_payload(payload)
    return payload, commit


def validate_payload(payload: dict[str, bytes]) -> None:
    for path, data in payload.items():
        if DEVELOPMENT_SLUG.encode() in data or b"senzing-bootcamp-chatgpt-plugin-development" in data:
            raise ValueError(f"development repository reference remains in {path}")
        if path.endswith(".min.js") or Path(path).suffix not in TEXT_SUFFIXES:
            continue
        content = data.decode("utf-8")
        match = BRITISH.search(content)
        if match:
            raise ValueError(f"British spelling {match.group()!r} in {path}; use American English")
    manifest = json.loads(payload["plugins/senzing-bootcamp/.codex-plugin/plugin.json"])
    for key in ("homepage", "repository"):
        if manifest.get(key) != f"https://github.com/{PUBLIC_SLUG}":
            raise ValueError(f"plugin manifest {key} is not the public repository")
    marketplace = json.loads(payload[MARKETPLACE])
    if marketplace.get("name") != "senzing":
        raise ValueError("public marketplace name is invalid")
    if len(marketplace.get("plugins", [])) != 1 or marketplace["plugins"][0]["source"] != {"source": "local", "path": "./plugins/senzing-bootcamp"}:
        raise ValueError("marketplace does not point at the shipped plugin")
    if f"https://github.com/{PUBLIC_SLUG}" not in payload["README.md"].decode():
        raise ValueError("README lacks the public marketplace URL")
    if "https//" in payload["README.md"].decode() or "chatgpt\n" in payload["README.md"].decode():
        raise ValueError("README has an incomplete URL or obsolete chatgpt command")


def destination(repo: Path, branch: str, allow_staged: bool) -> None:
    if not (repo / ".git").exists() or repo.resolve() == SOURCE:
        raise ValueError("--public-repo must be a separate public Git checkout")
    if remote_slug(git(repo, "remote", "get-url", "origin").decode().strip()) != PUBLIC_SLUG:
        raise ValueError(f"destination origin must be {PUBLIC_SLUG}")
    if branch in {"main", "master"}:
        raise ValueError("propagation requires a review branch, never main or master")
    git(repo, "check-ref-format", "--branch", branch)
    if git(repo, "branch", "--show-current").decode().strip() != branch:
        raise ValueError(f"public checkout must be on review branch {branch}")
    status = git(repo, "status", "--porcelain", "-z")
    if status and not allow_staged:
        raise ValueError("public checkout must be clean")
    if allow_staged and status:
        if git(repo, "diff", "--name-only") or git(repo, "ls-files", "--others", "--exclude-standard"):
            raise ValueError("public checkout has unstaged or untracked changes")
        changed_paths = git(repo, "diff", "--cached", "--name-only", "-z").decode().split("\0")
        if any(path and path not in {MARKETPLACE, "README.md"} and not path.startswith(PLUGIN) for path in changed_paths):
            raise ValueError("public checkout has unrelated staged changes")
    for path in (repo / PLUGIN, repo / ".agents", repo / ".agents/plugins", repo / MARKETPLACE, repo / "README.md"):
        if path.is_symlink():
            raise ValueError(f"destination contains a symlink at {path}")
    plugin_root = repo / PLUGIN
    if plugin_root.exists() and any(path.is_symlink() for path in plugin_root.rglob("*")):
        raise ValueError("destination plugin contains a symlink")


def changes(repo: Path, payload: dict[str, bytes]) -> tuple[list[str], list[str]]:
    existing = {
        path.relative_to(repo).as_posix(): path
        for path in (repo / PLUGIN).rglob("*") if path.is_file()
    }
    for name in (MARKETPLACE, "README.md"):
        path = repo / name
        if path.is_file():
            existing[name] = path
    changed = [name for name, data in payload.items() if name not in existing or existing[name].read_bytes() != data]
    deleted = sorted(name for name in existing if name not in payload and name.startswith(PLUGIN))
    return sorted(changed), deleted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="exact development release tag")
    parser.add_argument("--public-repo", type=Path, required=True, help="existing public checkout")
    parser.add_argument("--branch", required=True, help="checked-out public review branch; main is forbidden")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="mirror into public working tree without committing")
    mode.add_argument("--push-branch", action="store_true", help="commit and push only the review branch")
    parser.add_argument("--confirm-tag", help="required to push; must equal --tag")
    args = parser.parse_args()
    try:
        if args.push_branch and args.confirm_tag != args.tag:
            raise ValueError("--push-branch requires --confirm-tag equal to --tag")
        repo = args.public_repo.resolve()
        destination(repo, args.branch, args.push_branch)
        payload, commit = tagged_payload(args.tag)
        if args.push_branch:
            source_origin = git(SOURCE, "remote", "get-url", "origin").decode().strip()
            if remote_slug(source_origin) != DEVELOPMENT_SLUG:
                raise ValueError(f"source origin must be {DEVELOPMENT_SLUG}")
            remote_tag = git(SOURCE, "ls-remote", "--tags", "origin", f"refs/tags/{args.tag}").decode().split()
            local_tag = git(SOURCE, "rev-parse", f"refs/tags/{args.tag}").decode().strip()
            if not remote_tag or remote_tag[0] != local_tag:
                raise ValueError("local development tag differs from the remote versioned release")
            if git(repo, "tag", "--list", args.tag).strip():
                raise ValueError(f"public tag {args.tag} already exists")
            if git(repo, "ls-remote", "--tags", "origin", f"refs/tags/{args.tag}").strip():
                raise ValueError(f"remote public tag {args.tag} already exists")
            remote_head = git(repo, "ls-remote", "--heads", "origin", args.branch).decode().split()
            if not remote_head:
                raise ValueError(f"public origin has no review branch {args.branch}")
            if remote_head[0] != git(repo, "rev-parse", "HEAD").decode().strip():
                raise ValueError("public review branch has moved; update the checkout before pushing")
        changed, deleted = changes(repo, payload)
        print(f"source tag: {args.tag}\nsource commit: {commit}\npublic checkout: {repo}\nreview branch: {args.branch}")
        print(f"payload: {len(payload)} files; changes: {len(changed)}; scoped deletions: {len(deleted)}")
        for name in changed:
            print(f"  update {name}")
        for name in deleted:
            print(f"  delete {name}")
        if not (args.apply or args.push_branch):
            print("Preview only; public checkout unchanged.")
            return 0
        if not changed and not deleted and not git(repo, "diff", "--cached", "--name-only"):
            raise ValueError("no payload changes to stage or push; inspect the existing public branch")
        for name in deleted:
            (repo / name).unlink()
        for name in changed:
            path = repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload[name])
        git(repo, "add", "-A", "--", PLUGIN.removesuffix("/"), MARKETPLACE, "README.md")
        print(git(repo, "status", "--short").decode(), end="")
        if not args.push_branch:
            print("Staged for review; nothing committed or pushed.")
            return 0
        git(repo, "commit", "-m", f"Release Senzing Bootcamp ChatGPT plugin {args.tag}")
        git(repo, "push", "origin", f"HEAD:refs/heads/{args.branch}")
        print(f"Pushed review commit {git(repo, 'rev-parse', 'HEAD').decode().strip()} to {args.branch}; main and tags unchanged")
        return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the Codex plugin from a versioned Senzing Claude-plugin tag."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "senzing-bootcamp"
OVERLAY = ROOT / "port" / "overlay"
UPSTREAM_URL = "https://github.com/Senzing/senzing-bootcamp-claude-plugin.git"
SEMVER = re.compile(r"^(?:v)?(\d+)\.(\d+)\.(\d+)$")


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout


def latest_tag() -> str:
    output = run("git", "ls-remote", "--tags", "--refs", UPSTREAM_URL)
    tags: list[tuple[tuple[int, int, int], str]] = []
    for line in output.splitlines():
        tag = line.rsplit("refs/tags/", 1)[-1]
        match = SEMVER.fullmatch(tag)
        if match:
            tags.append((tuple(map(int, match.groups())), tag))
    if not tags:
        raise SystemExit("No stable SemVer tags found upstream")
    return max(tags)[1]


def clone_tag(tag: str, destination: Path) -> Path:
    run("git", "clone", "--depth", "1", "--branch", tag, UPSTREAM_URL, str(destination))
    return destination


def version_for(source: Path) -> str:
    manifest = source / "plugins/senzing-bootcamp/.claude-plugin/plugin.json"
    version = str(json.loads(manifest.read_text())["version"])
    if not SEMVER.fullmatch(version):
        raise SystemExit(f"Upstream manifest version is not stable SemVer: {version}")
    return version


REPLACEMENTS = (
    ("${CLAUDE_PLUGIN_ROOT}", "<plugin-root>"),
    ("CLAUDE_PLUGIN_ROOT", "plugin-root path"),
    (".claude-plugin", ".codex-plugin"),
    ("Claude Code CLI", "Codex CLI"),
    ("Claude Desktop", "Codex desktop app"),
    ("the Claude web app", "Codex cloud"),
    ("a Claude IDE extension", "the Codex IDE"),
    ("your Claude IDE extension", "the Codex IDE"),
    ("Claude Code", "Codex"),
    ("Claude interface", "Codex interface"),
    ("Claude plugin", "Codex plugin"),
    ("Claude session", "Codex task"),
    ("Claude-interface", "Codex-interface"),
    ("Claude app", "Codex app"),
    ("Claude IDE extension", "Codex IDE"),
    ("Opus 5", "a high-capability Codex model"),
    ("Sonnet 5", "a balanced Codex model"),
    ("Haiku 4.5", "a fast Codex model"),
    ("Fable 5", "the highest-capability available Codex model"),
    ("`/model opus` + `/effort high`", "a high-capability Codex model at high reasoning effort"),
    ("`/model sonnet` + `/effort medium`", "a balanced Codex model at medium reasoning effort"),
    ("`/model sonnet` + `/effort high`", "a balanced Codex model at high reasoning effort"),
    ("`/model opus`", "the model control"),
    ("`/model sonnet`", "the model control"),
    ("the bootcamper's Claude", "the bootcamper's Codex"),
    ("This is the Claude-plugin port", "This is the Codex-plugin port"),
    ('e.g. "claude-opus-5[1m] / high"', 'e.g. "configured Codex model / high"'),
)


def port_text(path: Path) -> None:
    original = path.read_text()
    text = original
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if text != original:
        notice = "Adapted for Codex from the version-matched Senzing upstream release."
        if path.suffix == ".md":
            if text.startswith("---\n"):
                marker = text.find("\n---\n", 4)
                if marker != -1:
                    marker += len("\n---\n")
                    text = text[:marker] + f"\n<!-- {notice} -->\n" + text[marker:]
            else:
                text = f"<!-- {notice} -->\n\n" + text
        elif path.suffix == ".py":
            lines = text.splitlines(keepends=True)
            insertion = 1 if lines and lines[0].startswith("#!") else 0
            lines.insert(insertion, f"# {notice}\n")
            text = "".join(lines)
    path.write_text(text)


def replace_section(path: Path, start: str, end: str, replacement: str) -> None:
    text = path.read_text()
    pattern = re.compile(rf"(?ms)^{re.escape(start)}\n.*?(?=^{re.escape(end)}\n)")
    updated, count = pattern.subn(replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise SystemExit(f"Expected one section from {start!r} to {end!r} in {path}")
    path.write_text(updated)


def copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def build(source: Path, expected_tag: str | None) -> str:
    version = version_for(source)
    normalized_tag = expected_tag.removeprefix("v") if expected_tag else None
    if normalized_tag and normalized_tag != version:
        raise SystemExit(f"Tag {expected_tag} contains manifest version {version}")

    upstream_plugin = source / "plugins/senzing-bootcamp"
    PLUGIN.mkdir(parents=True, exist_ok=True)
    for name in ("skills", "scripts", "docs", "hooks"):
        copy_tree(upstream_plugin / name, PLUGIN / name)
    shutil.copy2(upstream_plugin / ".mcp.json", PLUGIN / ".mcp.json")

    for path in PLUGIN.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json"}:
            port_text(path)

    # Codex discovers hooks/hooks.json automatically. Use its native plugin-root variable and add
    # visible status messages; do not rely on prose-only substitutes for lifecycle enforcement.
    hooks_path = PLUGIN / "hooks/hooks.json"
    hooks = json.loads((upstream_plugin / "hooks/hooks.json").read_text())
    hook_status = {
        "session-start.py": "Restoring Senzing Bootcamp context",
        "feedback-capture.py": "Checking bootcamp controls",
        "checkpoint-tick.py": "Preserving bootcamp progress",
        "write-gate.py": "Checking bootcamp write safety",
        "stop-nudge.py": "Checking for the next bootcamp question",
        "precompact-recap.py": "Preserving the bootcamp recap",
        "session-end.py": "Preserving the bootcamp session",
    }
    for groups in hooks.get("hooks", {}).values():
        for group in groups:
            for handler in group.get("hooks", []):
                command = handler.get("command", "")
                handler["command"] = command.replace("${CLAUDE_PLUGIN_ROOT}", "${PLUGIN_ROOT}")
                for script_name, status_message in hook_status.items():
                    if script_name in command:
                        handler["statusMessage"] = status_message
                        break
    controller = {
        "type": "command",
        "command": 'python3 "${PLUGIN_ROOT}/scripts/socratic-controller.py"',
        "statusMessage": "Continuing the Senzing Bootcamp",
        "additionalContextLimit": 4000,
    }
    prompt_groups = hooks.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
    if prompt_groups:
        prompt_groups[0].setdefault("hooks", []).insert(0, controller)
    else:
        prompt_groups.append({"hooks": [controller]})
    hooks_path.write_text(json.dumps(hooks, indent=2) + "\n")
    hooks_readme = PLUGIN / "hooks/README.md"
    hooks_text = hooks_readme.read_text()
    hooks_text = hooks_text.replace(
        "| `UserPromptSubmit` | `scripts/feedback-capture.py`",
        "| `UserPromptSubmit` | `scripts/socratic-controller.py` | to restore the active module "
        "on every answer and keep automatic work moving until the next Socratic question. |\n"
        "| `UserPromptSubmit` | `scripts/feedback-capture.py`",
    )
    hooks_text = hooks_text.replace(
        "Environment-variable substitution (`<plugin-root>`) is performed by Claude\n"
        "Code identically on all three platforms.",
        "Codex substitutes `${PLUGIN_ROOT}` in each hook command on all three platforms.",
    )
    hooks_text = hooks_text.replace(
        "- **Hooks ship with the plugin.** There is no hook-install step (this replaces the\n"
        "  Kiro `install_hooks.py` / `.kiro/hooks/` workflow).",
        "- **Hooks ship with the plugin.** Codex discovers `hooks/hooks.json` automatically; there "
        "is no hook-install step. Because bundled hooks are non-managed, the bootcamper must "
        "review and trust the current definitions before Codex runs them.",
    )
    hooks_text = hooks_text.replace(
        "Detection scans the whole\n  current turn and biases toward silence if the turn's text is "
        "not yet on disk, and the\n  block reason tells the model to repeat nothing it has already "
        "asked — so a false block\n  can never surface as a duplicate question.",
        "Detection uses Codex's stable `last_assistant_message` Stop-hook field, and the block "
        "reason tells the model to repeat nothing it has already asked.",
    )
    hooks_text = hooks_text.replace(
        "question, and it biases toward silence when the transcript cannot be read\n"
        "decisively — a missed nudge is far cheaper than a duplicated question.",
        "question. It reads Codex's stable `last_assistant_message` field rather than parsing the "
        "unstable transcript format.",
    )
    hooks_text = re.sub(
        r"A `claude-code-guide` investigation.*?finding is recorded here so it is not re-investigated\.",
        "The Codex interface controls tool-result rendering. The plugin cannot suppress that "
        "host-owned UI, so it minimizes administrative write frequency and uses concise commentary "
        "to keep the bootcamper informed.",
        hooks_text,
        flags=re.S,
    )
    hooks_readme.write_text(hooks_text)

    ground_rules = PLUGIN / "skills/bootcamp-onboarding/ground-rules.md"
    ground_text = ground_rules.read_text()
    contract_heading = "## Codex turn execution (mandatory)"
    if contract_heading not in ground_text:
        first_heading = ground_text.find("\n## ")
        if first_heading == -1:
            raise SystemExit(f"Expected a section heading in {ground_rules}")
        contract = """
## Codex turn execution (mandatory)

Read and follow `../../docs/codex-interaction-contract.md` before executing a bootcamp step. Codex
commentary is intermediate progress, not a turn boundary. After status-only or other non-yielding
work, continue in the same turn until the next skill-defined `👉` question. Before every final
response, perform that document's turn-close audit.
"""
        ground_text = ground_text[:first_heading] + contract + ground_text[first_heading:]
    ground_text = ground_text.replace(
        "**Model/effort tuning.** Model/effort is a session-level choice the bootcamper controls with\n"
        "  `/model` and `/effort` (it persists for the session; per-skill frontmatter would not — see\n"
        "  `../../docs/model-selection.md`).",
        "**Model/effort tuning.** Model and reasoning effort are host-level choices the bootcamper "
        "controls with the visible Codex controls (see `../../docs/model-selection.md`).",
    )
    ground_text = ground_text.replace(
        "the plugin ships\n  skills, hooks and commands, none of which reach their interface.",
        "the plugin ships skills, lifecycle hooks, scripts, and an MCP configuration, none of "
        "which reach their interface.",
    )
    ground_rules.write_text(ground_text)
    replace_section(
        ground_rules,
        "## Naming the Codex interface (INV-158)",
        "## Visual deliverables (Senzing brand)",
        """## Naming the Codex interface (INV-158)

Call the desktop application the **Codex desktop app**, its coding workspace the **Codex IDE**,
and the terminal client the **Codex CLI**. When the exact host is unknown, say **your Codex
interface**. Do not invent interface-specific commands or controls.""",
    )
    replace_section(
        ground_rules,
        "## Module start banners and transitions",
        "## Closing questions",
        """## Module start banners and transitions

At each selected module boundary, show its banner, journey map, before/after framing, numbered step
overview, and estimated time before doing module work. Read `../../docs/model-selection.md` before
giving model guidance. A model change is optional and controlled by the bootcamper; never claim to
have changed it. Use the visible Codex model and reasoning controls when available, and do not
invent Codex CLI slash commands.

Ask at most one 👉 question in a turn. If a model-change question is warranted, it consumes that
turn's question; resume the module after the bootcamper answers. Checkpoint only work actually
completed, using the progress rules above. Skip unselected optional modules and preserve the module
order recorded in the bootcamp preferences.""",
    )
    graduation = PLUGIN / "skills/graduation/SKILL.md"
    replace_section(
        graduation,
        "## Best-value model/effort prompt",
        "## Pre-checks",
        """## Best-value model/effort prompt

Graduation is a long, correctness-sensitive stage. Read `../../docs/model-selection.md` and, when
helpful, offer a capable Codex model at high reasoning effort using the host's visible controls.
The switch is optional, the plugin cannot perform it, and the question consumes the turn's single
👉 question. If the bootcamper declines, continue without pressure. If current settings cannot be
observed, say so rather than guessing.""",
    )

    onboarding = PLUGIN / "skills/bootcamp-onboarding/onboarding-flow.md"
    text = onboarding.read_text()
    text = re.sub(
        r"(?ms)\*\*Resolve the manifest in this order.*?Every other step needing the plugin version resolves it the same way.*?\n\n",
        "**Resolve the manifest as `<this-skill-dir>/../../.codex-plugin/plugin.json`.** This "
        "skill-relative path identifies the installed plugin deterministically. Never search the "
        "filesystem for another manifest. Use `Unknown` if that exact file cannot be read.\n\n",
        text,
        count=1,
    )
    text = re.sub(
        r"\(The Kiro Power installed Agent Hooks here.*?no hook-install step\.\)",
        "Codex discovers the bundled lifecycle hooks in `hooks/hooks.json`; the bootcamper must "
        "review and trust them when enabling the plugin. See `../../docs/codex-port.md`.",
        text,
        count=1,
        flags=re.S,
    )
    onboarding.write_text(text)

    phase3 = PLUGIN / "skills/module-05-data-quality-mapping/phase3-test-load.md"
    phase3_text = phase3.read_text()
    phase3_text = re.sub(
        r"(?ms)## Hooks\n\nIn the Codex plugin, bootcamp hooks ship.*?(?=^## |\Z)",
        "## Lifecycle checks\n\nCodex discovers the bundled bootcamp hooks after the "
        "bootcamper reviews and trusts them. The skill still performs closing-question, "
        "checkpoint, and write-safety checks explicitly according to the bootcamp ground rules; "
        "the hooks are the mechanical safety net.\n\n",
        phase3_text,
        count=1,
    )
    phase3.write_text(phase3_text)

    shutil.copytree(OVERLAY, PLUGIN, dirs_exist_ok=True)
    manifest = {
        "name": "senzing-bootcamp",
        "version": version,
        "description": "Guided bootcamp for learning Senzing entity resolution with Codex, from first demo to production deployment.",
        "author": {"name": "Senzing", "url": "https://senzing.com"},
        "homepage": "https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development",
        "repository": "https://github.com/docktermj/senzing-bootcamp-chatgpt-plugin-development",
        "license": "Apache-2.0",
        "keywords": ["senzing", "bootcamp", "entity-resolution", "tutorial", "guided-learning"],
        "skills": "./skills/",
        "mcpServers": "./.mcp.json",
        "interface": {
            "displayName": "Senzing Bootcamp",
            "shortDescription": "Learn Senzing entity resolution in Codex.",
            "longDescription": "A guided, hands-on Senzing entity-resolution bootcamp for the Codex IDE.",
            "developerName": "Senzing",
            "category": "Developer Tools",
            "capabilities": ["Interactive", "Write"],
            "websiteURL": "https://senzing.com",
            "defaultPrompt": [
                "Start the Senzing Bootcamp.",
                "Resume my Senzing Bootcamp.",
                "Check my bootcamp progress."
            ]
        }
    }
    manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    (ROOT / "UPSTREAM_VERSION").write_text(version + "\n")
    try:
        commit = run("git", "rev-parse", "HEAD", cwd=source).strip()
    except subprocess.CalledProcessError:
        commit = "unknown"
    (ROOT / "UPSTREAM_COMMIT").write_text(commit + "\n")
    return version


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Stable SemVer tag; defaults to latest upstream tag")
    parser.add_argument("--source-dir", type=Path, help="Use an already checked-out upstream tree")
    args = parser.parse_args()

    if args.source_dir:
        version = build(args.source_dir.resolve(), args.tag)
    else:
        tag = args.tag or latest_tag()
        if not SEMVER.fullmatch(tag):
            raise SystemExit("--tag must be a stable SemVer tag such as 0.5.2")
        with tempfile.TemporaryDirectory(prefix="senzing-bootcamp-") as temp:
            source = clone_tag(tag, Path(temp) / "upstream")
            version = build(source, tag)
    print(f"Built Senzing Bootcamp Codex plugin {version}")


if __name__ == "__main__":
    main()

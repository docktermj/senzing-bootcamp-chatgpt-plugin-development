"""Generate and verify the Codex-owned, pre-rendered example recap PDF."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


EXAMPLE = "docs/examples/bootcamp_recap.example.md"
ASSET = "port/artifacts/bootcamp_recap.example.pdf"
RECORD = "port/artifacts/bootcamp_recap.example.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("artifact path escapes its declared root")
    return path


def pdf_content(data):
    streams = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        try:
            streams.append(zlib.decompress(match.group(1)))
        except zlib.error:
            streams.append(match.group(1))
    return b"\n".join(streams)


def expected_inputs(plugin):
    paths = {EXAMPLE, "scripts/generate_recap_pdf.py", "scripts/brand_tokens.py",
             "scripts/senzing_logo_light.png"}
    source = plugin / EXAMPLE
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", source.read_text()):
        paths.add(contained(plugin, (source.parent / target).relative_to(plugin)).relative_to(plugin.resolve()).as_posix())
    return paths


def verify(plugin, repository, artifact):
    record = json.loads(contained(repository, artifact["verification"]).read_text())
    source = contained(repository, artifact["source"])
    if (not isinstance(record, dict) or record.get("schema_version") != 1
            or not isinstance(record.get("inputs"), dict)
            or digest(source) != record.get("pdf_sha256")
            or digest(Path(__file__)) != record.get("generator_sha256")):
        raise ValueError("example PDF digest or input inventory is invalid")
    if set(record.get("inputs", {})) != expected_inputs(plugin):
        raise ValueError("example PDF input inventory is incomplete or unexpected")
    for relative, expected in record["inputs"].items():
        if digest(contained(plugin, relative)) != expected:
            raise ValueError(f"stale example PDF input: {relative}; refresh the Codex example PDF")
    if EXAMPLE not in record["inputs"]:
        raise ValueError("example PDF verification must include its Markdown source")
    content = pdf_content(source.read_bytes())
    if not source.read_bytes().startswith(b"%PDF-") or b"Codex plugin" not in content:
        raise ValueError("example PDF lacks Codex attribution")
    if re.search(rb"Claude plugin|/model|/effort|Opus|Sonnet", content):
        raise ValueError("example PDF retains Claude-only host instructions")
    return source


def generate(repository, plugin=None):
    import fpdf
    import PIL

    if fpdf.__version__ != "2.8.5":
        raise ValueError("refresh requires fpdf2==2.8.5; see requirements-example-pdf.txt")
    if PIL.__version__ != "10.2.0":
        raise ValueError("refresh requires Pillow==10.2.0; see requirements-example-pdf.txt")
    plugin = plugin or repository / "plugins/senzing-bootcamp"
    source = plugin / EXAMPLE
    renderer_path = plugin / "scripts/generate_recap_pdf.py"
    sys.path.insert(0, str(renderer_path.parent))
    try:
        specification = importlib.util.spec_from_file_location("codex_example_renderer", renderer_path)
        renderer = importlib.util.module_from_spec(specification)
        sys.modules[specification.name] = renderer
        specification.loader.exec_module(renderer)
        text = source.read_text()
        recap = renderer.parse_recap(text)
        audit = renderer.audit_recap(recap, text)
        if audit.fatal or audit.warnings:
            raise ValueError(f"example recap audit failed: {audit.fatal + audit.warnings}")
        renderer.set_image_context(source)
        if renderer.unresolvable_image_targets(text):
            raise ValueError("example references missing images")
        paths = expected_inputs(plugin)
        stamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
        original = fpdf.FPDF

        class DeterministicPDF(original):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.set_creation_date(stamp)

        output = repository / ASSET
        output.parent.mkdir(parents=True, exist_ok=True)
        with patch.object(fpdf, "FPDF", DeterministicPDF):
            if not renderer.render_with_fpdf2(recap, output):
                raise ValueError("rich example PDF render failed; no stdlib downgrade is allowed")
        expected_images = renderer.recap_image_targets(text)
        if any(renderer._IMAGE_OUTCOMES.get(target) != "embedded" for target in expected_images):
            raise ValueError("example render did not embed every referenced image")
        record = {"schema_version": 1, "renderer": "fpdf2==2.8.5; Pillow==10.2.0",
                  "generator_sha256": digest(Path(__file__)),
                  "creation_date": stamp.isoformat(), "pdf_sha256": digest(output),
                  "inputs": {relative: digest(plugin / relative) for relative in sorted(paths)}}
        (repository / RECORD).write_text(json.dumps(record, indent=2) + "\n")
        verify(plugin, repository, {"source": ASSET, "verification": RECORD})
        print(f"Rendered {output}; {len(expected_images)} recap images embedded")
    finally:
        sys.path.pop(0)


def refresh_source(source, tag, contract):
    if __package__:
        from . import sync_parent as sync
    else:
        import sync_parent as sync
    if not sync.SEMVER.fullmatch(tag):
        raise ValueError("refresh requires an exact stable parent tag")
    version = tag.removeprefix("v")
    if sync.version_for(source, contract) != version:
        raise ValueError("refresh tag and source manifest version disagree")
    sync.validate_invariant_register(version, contract)
    commit = sync._source_commit(source)
    tagged_commit = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"],
        text=True,
    ).strip()
    if commit != tagged_commit or commit != contract["invariant_disposition_register"].get("source_commit"):
        raise ValueError("refresh source must match the exact reviewed parent tag and commit")
    return version, commit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--tag")
    arguments = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    if arguments.refresh:
        if not arguments.source_dir or not arguments.tag:
            parser.error("--refresh requires --source-dir and the exact pinned --tag")
        if __package__:
            from . import sync_parent as sync
        else:
            import sync_parent as sync
        contract = sync.load_contract(repository / "tools/bootcamp-transform/contract.yaml")
        source = arguments.source_dir.resolve()
        version, commit = refresh_source(source, arguments.tag, contract)
        upstream = source / contract["upstream"]["source_root"]
        plan = sync.plan_upstream(upstream, contract)
        authoring = {**contract, "generated_artifacts": [item for item in contract["generated_artifacts"]
                     if item["format"] != "verified-binary"]}
        variables = {"PARENT_VERSION": version, "PARENT_COMMIT": commit,
                     "RELEASE_VERSION": (repository / "RELEASE_VERSION").read_text().strip()}
        with tempfile.TemporaryDirectory(prefix="codex-example-pdf-") as directory:
            plugin = Path(directory) / "plugin"
            sync.execute_contract(upstream, plugin, repository, authoring, plan, variables)
            generate(repository, plugin)
    else:
        verify(repository / "plugins/senzing-bootcamp", repository,
               {"source": ASSET, "verification": RECORD})
        print("Codex example PDF source, inputs and binary verified")


if __name__ == "__main__":
    main()

"""Dependency-free binary example synchronization and negative-control tests."""

import json
import re
import shutil
import unittest
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import example_pdf
from scripts import sync_parent as sync


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/senzing-bootcamp"


class ExamplePDFTests(unittest.TestCase):
    def setUp(self):
        self.artifact = next(item for item in sync.load_contract()["generated_artifacts"]
                             if item["format"] == "verified-binary")

    def test_actual_binary_matches_all_declared_adapted_inputs(self):
        source = example_pdf.verify(PLUGIN, ROOT, self.artifact)
        self.assertEqual(source.read_bytes(), (PLUGIN / self.artifact["path"]).read_bytes())
        record = json.loads((ROOT / self.artifact["verification"]).read_text())
        self.assertGreaterEqual(len(record["inputs"]), 17)
        self.assertIn("scripts/generate_recap_pdf.py", record["inputs"])
        self.assertIn("scripts/brand_tokens.py", record["inputs"])

    def test_compressed_content_is_checked_not_only_the_pdf_header(self):
        content = example_pdf.pdf_content((PLUGIN / self.artifact["path"]).read_bytes())
        self.assertIn(b"Codex plugin", content)
        self.assertNotRegex(content, rb"Claude plugin|/model|/effort|Opus|Sonnet")
        markdown = (PLUGIN / example_pdf.EXAMPLE).read_text()
        version = re.search(r"\*\*Plugin version:\*\* ([^\n]+)", markdown).group(1)
        self.assertIn(version.encode(), content)
        self.assertGreaterEqual((PLUGIN / self.artifact["path"]).read_bytes().count(b"/Subtype /Image"), 13)

    def copy_fixture(self, directory):
        repository = Path(directory)
        plugin = repository / "plugin"
        record = json.loads((ROOT / self.artifact["verification"]).read_text())
        for relative in record["inputs"]:
            destination = plugin / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PLUGIN / relative, destination)
        for relative in (self.artifact["source"], self.artifact["verification"]):
            destination = repository / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        return repository, plugin

    def test_changed_markdown_renderer_or_image_blocks_stale_copy(self):
        for relative in (example_pdf.EXAMPLE, "scripts/generate_recap_pdf.py",
                         "docs/examples/visualizations/truthset_verification-match-keys.png"):
            with self.subTest(relative=relative), TemporaryDirectory() as directory:
                repository, plugin = self.copy_fixture(directory)
                target = plugin / relative
                target.write_bytes(target.read_bytes() + b"mutation")
                with self.assertRaisesRegex(ValueError, "stale example PDF input"):
                    example_pdf.verify(plugin, repository, self.artifact)

    def test_missing_input_cannot_be_waived_by_removing_its_hash(self):
        with TemporaryDirectory() as directory:
            repository, plugin = self.copy_fixture(directory)
            path = repository / self.artifact["verification"]
            record = json.loads(path.read_text())
            del record["inputs"]["scripts/brand_tokens.py"]
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "inventory"):
                example_pdf.verify(plugin, repository, self.artifact)

    def test_changed_binary_is_rejected(self):
        with TemporaryDirectory() as directory:
            repository, plugin = self.copy_fixture(directory)
            source = repository / self.artifact["source"]
            source.write_bytes(source.read_bytes() + b"mutation")
            with self.assertRaisesRegex(ValueError, "digest"):
                example_pdf.verify(plugin, repository, self.artifact)

    def test_rehashed_claude_instruction_still_fails_content_check(self):
        with TemporaryDirectory() as directory:
            repository, plugin = self.copy_fixture(directory)
            source = repository / self.artifact["source"]
            payload = zlib.compress(b"Claude plugin /model opus")
            source.write_bytes(source.read_bytes() + b"\nstream\n" + payload + b"\nendstream\n")
            path = repository / self.artifact["verification"]
            record = json.loads(path.read_text())
            record["pdf_sha256"] = example_pdf.digest(source)
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "Claude-only"):
                example_pdf.verify(plugin, repository, self.artifact)

    def test_artifact_input_cannot_escape_plugin_root(self):
        with TemporaryDirectory() as directory:
            repository, plugin = self.copy_fixture(directory)
            path = repository / self.artifact["verification"]
            record = json.loads(path.read_text())
            record["inputs"]["../../outside"] = "0" * 64
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                example_pdf.verify(plugin, repository, self.artifact)

    def test_contract_copies_verified_binary_and_rejects_a_stale_input(self):
        with TemporaryDirectory() as directory:
            repository, plugin = self.copy_fixture(directory)
            record = json.loads((repository / self.artifact["verification"]).read_text())
            plan = [(Path(relative), {"kind": "copy"}) for relative in record["inputs"]]
            contract = {"generated_artifacts": [self.artifact]}
            built = repository / "built"
            sync.execute_contract(plugin, built, repository, contract, plan, {})
            self.assertEqual((built / self.artifact["path"]).read_bytes(),
                             (repository / self.artifact["source"]).read_bytes())
            source = plugin / example_pdf.EXAMPLE
            source.write_text(source.read_text() + "changed input")
            with self.assertRaisesRegex(sync.ContractError, "E_STALE_BINARY_ARTIFACT"):
                sync.execute_contract(plugin, repository / "stale", repository, contract, plan, {})


if __name__ == "__main__":
    unittest.main()

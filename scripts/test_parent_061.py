"""Tagged-import regressions; static policy checks do not establish live host behavior."""

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import example_pdf
from scripts import sync_parent as sync


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/senzing-bootcamp"
SCRIPTS = PLUGIN / "scripts"
COMMIT = "d3d99523f88957cd9dda2d29375892bf2c557663"


def policy(path):
    return " ".join((PLUGIN / path).read_text().split())


def load_helper(name):
    specification = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    sys.path.insert(0, str(SCRIPTS))
    try:
        specification.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


class ParentImportTests(unittest.TestCase):
    def test_provenance_agrees_without_bumping_local_release(self):
        contract = sync.load_contract()
        register = contract["invariant_disposition_register"]
        manifest = json.loads((ROOT / ".build-manifest.json").read_text())
        self.assertEqual((ROOT / "PARENT_VERSION").read_text().strip(), "0.6.1")
        self.assertEqual((ROOT / "PARENT_COMMIT").read_text().strip(), COMMIT)
        self.assertEqual(register["source_version"], "0.6.1")
        self.assertEqual(register["source_commit"], COMMIT)
        self.assertEqual(manifest["upstream_commit"], COMMIT)
        self.assertEqual(manifest["upstream_version"], "0.6.1")
        self.assertEqual(manifest["release_version"], (ROOT / "RELEASE_VERSION").read_text().strip())
        self.assertEqual(register["discounted"], [])
        self.assertTrue((ROOT / register["review"]).is_file())
        self.assertIn("**Plugin version:** " + manifest["release_version"],
                      (PLUGIN / example_pdf.EXAMPLE).read_text())

    def test_example_version_uses_the_local_release_variable_not_a_fixed_bump(self):
        contract = sync.load_contract()
        transform = next(item for item in contract["text_transforms"] if item["id"] == "local-example-version")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            relative = Path(example_pdf.EXAMPLE)
            target = source / relative
            target.parent.mkdir(parents=True)
            target.write_text("**Plugin version:** 0.6.1\n")
            built = root / "built"
            sync.execute_contract(source, built, ROOT, {"text_transforms": [transform]},
                                  [(relative, {"kind": "copy"})], {"RELEASE_VERSION": "9.8.7"})
            self.assertEqual((built / relative).read_text(), "**Plugin version:** 9.8.7\n")

    def test_full_model_tokens_and_feedback_examples_are_transformed(self):
        transform = next(item for item in sync.load_contract()["text_transforms"]
                         if item["id"] == "global-host-language")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "fixture.md"
            path.write_text('Opus 5.5; Sonnet 5.5; Fable 5.1; Opus 5. e.g. "claude-opus-5-5[1m] / high"')
            sync.apply_text_transforms(root, {"text_transforms": [transform]})
            result = path.read_text()
            self.assertNotRegex(result, r"Opus|Sonnet|Fable|claude-|model\.\d")
            self.assertIn("configured Codex model / high", result)
            self.assertIn("highest-capability available Codex model", result)

    def test_shipped_text_has_no_new_host_token_leaks(self):
        for path in PLUGIN.rglob("*"):
            if path.suffix not in {".md", ".py", ".json"}:
                continue
            with self.subTest(path=path.relative_to(PLUGIN)):
                self.assertNotRegex(path.read_text(), r"claude-(?:opus|sonnet|fable)|Codex model\.\d")

    def test_broll_and_graduation_keep_privacy_and_decline_rules(self):
        completion = policy("skills/bootcamp-onboarding/module-completion.md")
        graduation = policy("skills/graduation/SKILL.md")
        for phrase in ("docs/video/broll.json", "INV-341", "aggregates", "captured_at"):
            self.assertIn(phrase, completion)
        for phrase in ("INV-340", "docs/video/storyboard.json", "Step 1c", "Match Keys",
                       "Feature Scores", "Cross-Source"):
            self.assertIn(phrase, graduation)
        self.assertRegex(graduation, r"(?i)on no.{0,200}(?:nothing|no |skip)")

    def test_mapping_returns_and_per_source_gates_are_preserved(self):
        combined = " ".join(policy(str(path.relative_to(PLUGIN))) for path in
                            (PLUGIN / "skills/module-05-data-quality-mapping").glob("*.md"))
        for phrase in ("collection_return", "quality_iteration", "INV-335", "INV-336",
                       "INV-343", "INV-344", "INV-345"):
            self.assertIn(phrase, combined)
        self.assertIn("mapping_status", combined)
        self.assertIn("test_load", combined)

    def test_reconciliation_counts_and_subset_records_survive(self):
        combined = " ".join(policy(str(path.relative_to(PLUGIN))) for path in
                            (PLUGIN / "skills/module-06-data-processing").glob("*.md"))
        for phrase in ("load_subset", "sample:", "INV-320", "INV-324", "INV-325",
                       "expected_delta", "HOW_RESULTS.FINAL_STATE", "checked N of M"):
            self.assertIn(phrase, combined)

    def test_installed_sdk_version_and_eula_existing_install_route_survive(self):
        setup = policy("skills/module-02-sdk-setup/SKILL.md")
        graduation = policy("skills/graduation/SKILL.md")
        for phrase in ("sdk_version_measured_at", "sdk_version", "INV-338", "INV-339",
                       "senzing-env.ps1", "Phase 3"):
            self.assertIn(phrase, setup)
        self.assertIn("sdk_version", graduation)
        self.assertIn("Unknown", graduation)


class RefreshProvenanceTests(unittest.TestCase):
    def check_source(self, tag="0.6.1", version="0.6.1", reviewed=COMMIT, checked=COMMIT, tagged=COMMIT):
        contract = {"invariant_disposition_register": {"source_version": "0.6.1", "source_commit": reviewed}}
        with patch.object(sync, "version_for", return_value=version), \
                patch.object(sync, "_source_commit", return_value=checked), \
                patch.object(example_pdf.subprocess, "check_output", return_value=tagged + "\n"):
            return example_pdf.refresh_source(Path("/synthetic-parent"), tag, contract)

    def test_reviewed_target_can_refresh_before_current_pins_advance(self):
        self.assertEqual(self.check_source(), ("0.6.1", COMMIT))

    def test_branch_prerelease_and_manifest_mismatch_are_rejected(self):
        for tag in ("main", "HEAD", "0.7.0-rc1"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                self.check_source(tag=tag)
        with self.assertRaises(ValueError):
            self.check_source(version="0.5.3")

    def test_wrong_checkout_or_reviewed_commit_is_rejected(self):
        for arguments in ({"checked": "1" * 40}, {"reviewed": "2" * 40}, {"tagged": "3" * 40}):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self.check_source(**arguments)


class VideoRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.video = load_helper("generate_recap_video")

    def storyboard(self):
        return {"video": {"bootcamper": "Synthetic Graduate", "graduation_date": "2026-10-16"},
                "scenes": [{"type": "title_card", "duration": 1, "narration": "Synthetic example.",
                            "module": "Business Problem", "highlight": "Two sources"}]}

    def test_valid_storyboard_and_all_exit_codes(self):
        self.assertEqual(self.video.validate_storyboard(self.storyboard(), ROOT), [])
        self.assertEqual([self.video.EXIT_RENDERED, self.video.EXIT_INVALID_STORYBOARD,
                          self.video.EXIT_MISSING_CAPABILITY, self.video.EXIT_RENDER_FAILED], [0, 1, 2, 3])

    def test_local_path_policy_rejects_urls_absolute_paths_and_symlink_escape(self):
        with TemporaryDirectory() as directory, TemporaryDirectory() as outside:
            root = Path(directory)
            self.assertIsNone(self.video.project_relative_problem("missing.png", root))
            for target in ("https://example.invalid/image.png", "/outside.png", "../outside.png", "C:\\outside.png"):
                self.assertIsNotNone(self.video.project_relative_problem(target, root))
            (root / "escape").symlink_to(outside, target_is_directory=True)
            self.assertIsNotNone(self.video.project_relative_problem("escape/image.png", root))

    def test_invalid_storyboard_preserves_existing_video(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            storyboard = root / "storyboard.json"
            storyboard.write_text("{}")
            output = root / "existing.mp4"
            output.write_bytes(b"existing-video")
            result = subprocess.run([sys.executable, str(SCRIPTS / "generate_recap_video.py"),
                                     "--project-root", str(root), "--storyboard", str(storyboard),
                                     "--output", str(output)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("video", result.stderr)
            self.assertEqual(output.read_bytes(), b"existing-video")

    @unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow is absent; install requirements-dev.txt for video frame tests")
    def test_frame_drawing_uses_the_actual_imported_renderer(self):
        image = self.video.render_scene_frame(self.storyboard(), 0, 0.5, project_root=ROOT)
        self.assertEqual(image.size, (1920, 1080))
        self.assertEqual(image.mode, "RGB")


class PDFRendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = load_helper("generate_discoveries_pdf")

    def document(self):
        return self.renderer.parse_discoveries("# Synthetic Report\n\n## Evidence\n\nA synthetic artifact, not SDK output.\n")

    def test_stdlib_renderer_emits_a_pdf(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "stdlib.pdf"
            self.assertTrue(self.renderer.render_with_stdlib(self.document(), output))
            self.assertTrue(output.read_bytes().startswith(b"%PDF-"))

    @unittest.skipUnless(importlib.util.find_spec("fpdf"), "fpdf2 is absent; install requirements-dev.txt to measure the rich renderer")
    def test_rich_renderer_emits_a_pdf(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "rich.pdf"
            self.assertTrue(self.renderer.render_with_fpdf2(self.document(), output))
            self.assertTrue(output.read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()

"""Static model-guidance preservation tests; no host conversation pass implied."""

import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import sync_parent as sync


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/senzing-bootcamp"
GROUND = "skills/bootcamp-onboarding/ground-rules.md"
GRADUATION = "skills/graduation/SKILL.md"
STAGES = [
    "Onboarding", "Bootcamp preparation", "Entity Resolution Concepts",
    "Discover the Business Problem", "SDK setup", "System verification",
    "Truth Set visualization", "Data collection", "Data Quality, Mapping, and Transformation",
    "Data processing", "Query, Visualize and Discover", "Bootcamp graduation",
]
REQUIRED = [
    "**Best-value model/effort prompt.**",
    "**Compare model and effort separately against live settings**",
    "**Only for an unreadable dial**",
    "**Above the entire table is satisfied, per dial.**",
    "**No dial differs:**", "**A dial differs:**", "**On no:**", "**On yes:**",
    "**Not yet set or still unobservable:**", "**Already at the recommendation:**",
    "**Already deliberately set to another value:**",
    "Branches 2 and 3 skip the done gate; branch 1 keeps it.",
    "Are you done modifying the model and effort?",
    "reply no to keep your current model and effort.",
    "reply no to keep your current model.",
    "reply no to keep your current effort.",
    "about resource use, not a capability the stage requires",
]


def missing_guarantees(text):
    normalized = " ".join(text.split())
    return [phrase for phrase in REQUIRED if phrase not in normalized]


class ModelGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.contract = sync.load_contract(ROOT / "tools/bootcamp-transform/contract.yaml")
        self.ground = (PLUGIN / GROUND).read_text()
        self.graduation = (PLUGIN / GRADUATION).read_text()

    def test_generated_policy_carries_comparison_and_all_answer_branches(self):
        self.assertEqual(missing_guarantees(self.ground), [])

    def test_old_generic_replacement_is_a_negative_control(self):
        old = "A model change is optional. If a question is warranted, resume after the answer."
        self.assertTrue(missing_guarantees(old))
        for phrase in REQUIRED:
            with self.subTest(phrase=phrase):
                normalized = " ".join(self.ground.split())
                self.assertIn(phrase, missing_guarantees(normalized.replace(phrase, "")))

    def test_real_contract_restores_the_policy_not_only_generated_output(self):
        fixture = (
            "# Rules\n\n## Naming the Codex interface (INV-158)\nOld\n"
            "## Visual deliverables (Senzing brand)\nVisual\n"
            "## Module start banners and transitions\nOld module policy\n"
            "## Closing questions\nKeep this closing rule\n"
        )
        transform = next(item for item in self.contract["text_transforms"] if item["id"] == "ground-rules")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / GROUND
            target.parent.mkdir(parents=True)
            target.write_text(fixture)
            sync.apply_text_transforms(root, {"text_transforms": [transform]})
            result = target.read_text()
            self.assertEqual(missing_guarantees(result), [])
            self.assertIn("Keep this closing rule", result)
            self.assertNotIn("Old module policy", result)

    def test_stage_table_has_every_stage_once_and_flat_final_recommendation(self):
        rows = re.findall(r"(?m)^  \| (.+?) \| (balanced|high-capability) \| (medium|high) \|$", self.ground)
        self.assertEqual([row[0] for row in rows], STAGES)
        self.assertEqual(len({row[0] for row in rows}), len(STAGES))
        self.assertEqual({row[1:] for row in rows[-4:]}, {("high-capability", "high")})
        self.assertEqual(rows[5][1:], ("balanced", "high"))

    def test_setup_exemptions_journey_order_and_estimates_survive(self):
        for phrase in (
            "do NOT run the module-start apparatus",
            "Bootcamp preparation is fully exempt",
            "Module 0, when it runs, DOES append",
            "selected_modules", "minimal", "concise",
            "hard to estimate for this module",
            "setup stages never present the",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.ground)

    def test_graduation_uses_the_single_canonical_procedure(self):
        for phrase in (
            "../bootcamp-onboarding/ground-rules.md",
            "**Bootcamp graduation**", "Guidance is unconditional",
            "three branches", "already recommended or deliberately",
            "On decline, continue into Pre-checks",
        ):
            self.assertIn(phrase, self.graduation)
        self.assertNotIn("when\nhelpful, offer", self.graduation)

    def test_role_adapter_does_not_claim_hidden_settings_or_fixed_model_ids(self):
        adapter = (ROOT / "port/overlay/docs/model-selection.md").read_text()
        for phrase in (
            "reliable current context", "comparison is unavailable",
            "retain the current supported setting", "not an observed model ID",
            "actual selected values",
        ):
            self.assertIn(phrase, adapter)
        policy = self.ground[self.ground.index("## Module start banners and transitions"):]
        self.assertNotRegex(policy, r"gpt-\d|Opus|Sonnet|`/(?:effort|model)\b")
        self.assertNotRegex(adapter, r"gpt-\d|Opus|Sonnet")

    def test_register_restates_the_native_mechanisms_without_discounts(self):
        register = self.contract["invariant_disposition_register"]
        entries = {entry["id"]: entry for entry in register["preserved_restated"]}
        for identifier in ("063", "069", "098", "114", "137", "138", "139", "140", "141", "236"):
            self.assertIn("scripts.test_model_guidance", entries["INV-" + identifier]["mechanism"])
        self.assertEqual(register["discounted"], [])


if __name__ == "__main__":
    unittest.main()

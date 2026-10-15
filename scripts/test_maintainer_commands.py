"""Regression tests for command and skill discovery across both intentional locations."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.check_maintainer_commands import check_maintainer_commands


class MaintainerCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def skill(self, name, directory="maintainer-skills"):
        path = self.root / directory / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nname: {name}\ndescription: Test skill\n---\n")
        return path

    def command(self, name, target=None):
        path = self.root / "commands" / f"{name}.md"
        path.parent.mkdir(exist_ok=True)
        target = target or f"maintainer-skills/{name}/SKILL.md"
        path.write_text(f"---\ndescription: Test command\nargument-hint: INPUT=<value>\n---\nRead `{target}`.\n")
        return path

    def test_both_skill_locations_are_supported(self):
        self.skill("feedback")
        self.command("feedback")
        self.skill("propagate", ".agents/skills")
        self.command("propagate", ".agents/skills/propagate/SKILL.md")
        self.assertEqual(check_maintainer_commands(self.root), [])

    def test_skill_without_command_fails(self):
        self.skill("feedback")
        self.assertTrue(any("has no commands/feedback.md" in error
                            for error in check_maintainer_commands(self.root)))

    def test_command_without_skill_fails(self):
        self.command("feedback")
        self.assertTrue(any("no matching maintainer skill" in error
                            for error in check_maintainer_commands(self.root)))

    def test_wrong_target_fails_even_when_command_and_skill_names_match(self):
        self.skill("feedback")
        self.skill("other")
        self.command("other")
        self.command("feedback", "maintainer-skills/other/SKILL.md")
        self.assertTrue(any("does not resolve to skill feedback" in error
                            for error in check_maintainer_commands(self.root)))

    def test_duplicate_skill_names_across_locations_fail(self):
        self.skill("feedback")
        self.skill("feedback", ".agents/skills")
        self.command("feedback")
        self.assertTrue(any("duplicate maintainer skill feedback" in error
                            for error in check_maintainer_commands(self.root)))

    def test_stale_location_and_ambiguous_targets_fail(self):
        self.skill("feedback", ".agents/skills")
        command = self.command("feedback")
        self.assertTrue(check_maintainer_commands(self.root))
        self.command("feedback", ".agents/skills/feedback/SKILL.md")
        with command.open("a") as stream:
            stream.write("Read `maintainer-skills/feedback/SKILL.md` too.\n")
        self.assertTrue(any("exactly one" in error for error in check_maintainer_commands(self.root)))

    def test_metadata_and_explicit_target_are_required(self):
        skill = self.skill("feedback")
        skill.write_text("---\nname: other\n---\n")
        command = self.command("feedback")
        command.write_text("Use feedback.\n")
        errors = check_maintainer_commands(self.root)
        self.assertTrue(any("skill name must match" in error for error in errors))
        self.assertTrue(any("missing frontmatter" in error for error in errors))
        self.assertTrue(any("exactly one" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

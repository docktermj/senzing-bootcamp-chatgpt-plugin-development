"""Supersession validation against complete and broken invariant graphs."""

import unittest

from scripts.check_invariants import analyze_invariants


def definition(identifier, *lines):
    return f"- **{identifier}** — A guarantee MUST hold.\n" + "\n".join(lines) + "\n"


class InvariantTests(unittest.TestCase):
    def test_reciprocal_pair_has_only_active_and_superseded_status(self):
        text = definition("CINV-001", "  - **Superseded by:** CINV-002 — clarified guarantee")
        text += definition("CINV-002", "  - **Supersedes:** CINV-001")
        statuses, errors = analyze_invariants(text)
        self.assertEqual(errors, [])
        self.assertEqual(statuses, {"CINV-001": "superseded", "CINV-002": "active"})

    def test_chain_and_multiple_predecessors_are_supported(self):
        text = definition("CINV-001", "  - **Superseded by:** CINV-003")
        text += definition("CINV-002", "  - **Superseded by:** CINV-003")
        text += definition("CINV-003", "  - **Supersedes:** CINV-001", "  - **Supersedes:** CINV-002",
                           "  - **Superseded by:** CINV-004")
        text += definition("CINV-004", "  - **Supersedes:** CINV-003")
        statuses, errors = analyze_invariants(text)
        self.assertEqual(errors, [])
        self.assertEqual(statuses["CINV-003"], "superseded")
        self.assertEqual(statuses["CINV-004"], "active")

    def test_missing_reciprocal_link_fails_in_both_directions(self):
        for marker, message in (("Superseded by", "lacks Supersedes"), ("Supersedes", "lacks Superseded by")):
            with self.subTest(marker=marker):
                text = definition("CINV-001", f"  - **{marker}:** CINV-002") + definition("CINV-002")
                self.assertTrue(any(message in error for error in analyze_invariants(text)[1]))

    def test_nonexistent_targets_fail_in_both_directions(self):
        for marker in ("Superseded by", "Supersedes"):
            with self.subTest(marker=marker):
                text = definition("CINV-001", f"  - **{marker}:** CINV-999")
                self.assertTrue(any("missing CINV-999" in error for error in analyze_invariants(text)[1]))

    def test_alternate_syntax_and_foreign_namespace_fail(self):
        for line in ("  - **Superseded by:** CINV-2", "  - **Superseded by:** INV-002",
                     "  - **superseded by:** CINV-002", "  Superseded by CINV-002",
                     "  This rule was replaced by CINV-002.", "  - **Status:** superseded",
                     "  - **Status:** unclear", "  ~~obsolete guarantee~~",
                     "  - **Supersedes:** CINV-002, CINV-003"):
            with self.subTest(line=line):
                self.assertTrue(any("non-conforming" in error
                                    for error in analyze_invariants(definition("CINV-001", line))[1]))

    def test_duplicate_links_and_multiple_successors_fail(self):
        text = definition("CINV-001", "  - **Superseded by:** CINV-002", "  - **Superseded by:** CINV-002")
        text += definition("CINV-002", "  - **Supersedes:** CINV-001")
        self.assertTrue(any("duplicate" in error for error in analyze_invariants(text)[1]))
        text = definition("CINV-001", "  - **Superseded by:** CINV-002", "  - **Superseded by:** CINV-003")
        text += definition("CINV-002") + definition("CINV-003")
        self.assertTrue(any("one successor" in error for error in analyze_invariants(text)[1]))

    def test_self_links_and_cycles_fail(self):
        text = definition("CINV-001", "  - **Superseded by:** CINV-001", "  - **Supersedes:** CINV-001")
        self.assertTrue(any("itself" in error for error in analyze_invariants(text)[1]))
        text = definition("CINV-001", "  - **Superseded by:** CINV-002", "  - **Supersedes:** CINV-002")
        text += definition("CINV-002", "  - **Superseded by:** CINV-001", "  - **Supersedes:** CINV-001")
        self.assertTrue(any("cycle" in error for error in analyze_invariants(text)[1]))

    def test_maintenance_examples_are_not_invariant_metadata(self):
        text = "## Maintaining this file\n  - **Superseded by:** CINV-999\n"
        text += definition("CINV-001") + "## Other guidance\nSuperseded by CINV-999\n"
        statuses, errors = analyze_invariants(text)
        self.assertEqual(errors, [])
        self.assertEqual(statuses, {"CINV-001": "active"})

    def test_duplicate_and_missing_definitions_fail(self):
        self.assertTrue(analyze_invariants("")[1])
        self.assertTrue(any("duplicate definition" in error
                            for error in analyze_invariants(definition("CINV-001") * 2)[1]))


if __name__ == "__main__":
    unittest.main()

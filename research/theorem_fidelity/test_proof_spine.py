"""Offline tests for source-level Unique Games proof-spine checking."""
import json
import unittest
from pathlib import Path

from proof_spine import (ANCHORS, BASE, EDGES, active_imports,
                         active_placeholders, paths_and_pin, audit)

PIN = Path(__file__).with_name("proof_spine_pin.json")


class UniqueGamesProofSpineTests(unittest.TestCase):
    def test_pinned_paths_cover_all_proof_anchors(self):
        pin = json.loads(PIN.read_text("utf-8"))
        paths = paths_and_pin(pin)
        self.assertEqual(set(ANCHORS),
                         {p.removeprefix(BASE) for p in pin["sources"]})
        self.assertEqual(len(paths), 11)
        self.assertGreaterEqual(sum(map(len, ANCHORS.values())), 20)

    def test_direct_edges_are_pinned_and_acyclic(self):
        seen = set()
        def visit(node, pending):
            if node in pending:
                raise AssertionError("cycle in selected proof-spine edges")
            if node in seen:
                return
            for dep in EDGES.get(node, ()):
                self.assertIn(dep, ANCHORS)
                visit(dep, pending | {node})
            seen.add(node)
        visit("Theorem.lean", set())
        self.assertTrue(set(EDGES).issubset(seen))

    def test_comment_and_string_import_spoofing(self):
        content = r'''import OAI.Computability.UniqueGames.Theorem
/- import OAI.Computability.UniqueGames.Inverse.ShortcodeTheorem
   /- import OAI.Computability.UniqueGames.Gadgets.Final -/ -/
-- import OAI.Computability.UniqueGames.Inverse.ShortcodeFromGrassmannLemmas
def fake : String := "import OAI.Computability.UniqueGames.Reduction.FromMatrixGap"
'''
        imports = active_imports(content)
        self.assertEqual(imports, {"OAI.Computability.UniqueGames.Theorem"})

    def test_only_active_placeholders_fail(self):
        self.assertFalse(active_placeholders("/- sorry /- admit -/ -/\n-- sorry"))
        self.assertFalse(active_placeholders('def documentation : String := "admit"'))
        self.assertTrue(active_placeholders("theorem broken : True := by\n  sorry"))

    def test_pin_conflict_rejected(self):
        pin = json.loads(PIN.read_text("utf-8"))
        pin["sources"][BASE + "Unexpected.lean"] = "0" * 40
        with self.assertRaises(ValueError):
            paths_and_pin(pin)

    def test_source_set_required_for_audit(self):
        pin = json.loads(PIN.read_text("utf-8"))
        with self.assertRaises(ValueError):
            audit({}, pin)


if __name__ == "__main__":
    unittest.main()

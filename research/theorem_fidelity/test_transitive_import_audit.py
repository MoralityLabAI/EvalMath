"""Offline regression tests for import closure provenance."""
import json
import tempfile
import unittest
from pathlib import Path
from transitive_import_audit import without_noncode, scan


class TransitiveImportAuditTests(unittest.TestCase):
    def test_nested_comments_and_strings(self):
        src = '''public import OAI.Good OAI.AlsoGood
/- import OAI.Bad /- sorry -/ -/
-- import OAI.Nope
def s : String := "axiom\\\"sorry"
'''
        x = without_noncode(src)
        self.assertIn('import OAI.Good OAI.AlsoGood', x)
        for token in ('import OAI.Bad', 'import OAI.Nope', 'sorry', 'axiom'):
            self.assertNotIn(token, x)

    def test_closure_and_transitive_placeholder(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'OAI').mkdir()
            (root / 'OAI/A.lean').write_text(
                'import OAI.B\n/- sorry -/\ntheorem foo : True := by trivial\n')
            (root / 'OAI/B.lean').write_text(
                'import OAI.C\ntheorem bar : True := by sorry\n')
            (root / 'OAI/C.lean').write_text(
                'import OAI.A\n-- axiom nope\n')
            result = scan(root, 'OAI.A')
            self.assertEqual(result['local_modules'], 3)
            self.assertEqual(result['direct_local_edges'], 3)
            self.assertIn('placeholder', result['flagged_modules']['OAI.B'])
            self.assertNotIn('OAI.C', result['flagged_modules'])
            self.assertEqual(result, json.loads(json.dumps(result)))

    def test_rejects_missing_import(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'OAI').mkdir()
            (root / 'OAI/A.lean').write_text('import OAI.Missing\n')
            with self.assertRaises(FileNotFoundError):
                scan(root, 'OAI.A')

    def test_malformed_module_name(self):
        with self.assertRaises(ValueError):
            scan(Path('.'), 'Mathlib.Theorem')

    def test_unterminated_lean(self):
        with self.assertRaises(ValueError):
            without_noncode('theorem t : True := by\n /- comment')


if __name__ == '__main__':
    unittest.main()

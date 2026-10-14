"""Check the output of `lake env lean axioms_check.lean`.

Usage: python scripts/check_lean_axioms.py <axioms output file> <axioms_check.lean>

Every `#print axioms` line in axioms_check.lean must produce exactly one report, and each report may
name only `propext`, `Classical.choice` and `Quot.sound`. Lean wraps long axiom lists over several
lines, so reports are joined before parsing. Exit status is non-zero on any failure.
"""
import re
import sys
from pathlib import Path

ALLOWED = {"propext", "Classical.choice", "Quot.sound"}

output = Path(sys.argv[1]).read_text(encoding="utf-8")
listed = [line.split()[2] for line in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
          if line.startswith("#print axioms")]
reports = {}
for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", output, re.DOTALL):
    reports[m.group(1)] = {a.strip() for a in m.group(2).replace("\n", " ").split(",") if a.strip()}
for m in re.finditer(r"'([^']+)' does not depend on any axioms", output):
    reports[m.group(1)] = set()
errors = [line for line in output.splitlines() if "error" in line.lower() or "sorry" in line.lower()]
missing = [name for name in listed if name not in reports]
bad = {name: sorted(axioms - ALLOWED) for name, axioms in reports.items() if axioms - ALLOWED}
print(f"{len(listed)} theorems listed, {len(reports)} reported, {len(missing)} missing, "
      f"{len(bad)} with non-standard axioms, {len(errors)} error lines")
for name in missing:
    print("missing:", name)
for name, extra in bad.items():
    print("non-standard:", name, extra)
for line in errors[:10]:
    print("error:", line)
sys.exit(1 if missing or bad or errors else 0)

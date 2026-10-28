"""Replay the exploratory reference and generate a deterministic source receipt."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent
SOURCES = (
    "README.md", "RESEARCH.md", "reference.py", "test_reference.py", "verify.py",
    "compactification_theory_handoff/note/intervention-preserving-compactification.md",
    "compactification_theory_handoff/experiments/interventional-compactification/README.md",
)
EXPECTED = {
    "test_reference.CompactificationTests.test_exact_quotient",
    "test_reference.CompactificationTests.test_observationally_perfect_but_causally_wrong",
    "test_reference.CompactificationTests.test_near_fiber_falsifier",
    "test_reference.CompactificationTests.test_finite_horizon_bound_tight_for_additive_error",
    "test_reference.CompactificationTests.test_statistical_bound",
}


def case_ids(suite: unittest.TestSuite) -> list[str]:
    ids = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            ids.extend(case_ids(item))
        else:
            ids.append(item.id())
    return ids


def make_receipt() -> dict:
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_reference.py")
    ids = case_ids(suite)
    if len(ids) != len(EXPECTED) or set(ids) != EXPECTED:
        raise RuntimeError(f"test inventory changed: {sorted(ids)}")
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    sys.stderr.write(log.getvalue())
    if (not result.wasSuccessful() or result.testsRun != len(EXPECTED)
            or result.skipped or result.expectedFailures or result.unexpectedSuccesses):
        raise RuntimeError("reference replay failed or a case was skipped")
    return {
        "schema": "evalmath.interventional_compactification.reference.v2",
        "evidence": "synthetic floating-point sanity checks",
        "test_count": result.testsRun,
        "checks": [{"id": name, "status": "passed"} for name in sorted(ids)],
        "source_sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in SOURCES
        },
        "lean_compilation": "not_performed",
        "real_model_experiments": "not_performed",
        "repository_wide_ci": "not_verified_by_this_receipt",
        "rigorous_rounding_certificate": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare without rewriting")
    args = parser.parse_args()
    receipt = make_receipt()
    path = ROOT / "receipt.json"
    if args.check:
        expected = json.loads(path.read_text(encoding="utf-8"))
        if expected != receipt:
            raise RuntimeError("receipt mismatch; review the source changes before regeneration")
        print("Receipt matches: 5/5 reference tests and all source hashes.")
    else:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

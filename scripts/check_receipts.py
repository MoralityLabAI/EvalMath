"""Regenerate every committed receipt and compare it with the committed copy.

Usage:
    python scripts/check_receipts.py            # every receipt except the slow ones
    python scripts/check_receipts.py --all      # also the multigen full sweep and gold calibration (~40 min)
    python scripts/check_receipts.py --only lattice selection_kl

Each verifier writes a JSON receipt recording its checks and the SHA-256 of its source files. A receipt
reproduces when the regenerated JSON equals the committed one after dropping `generated_at_utc`. The
script also checks that every committed receipt's recorded source hashes match the files in this
checkout, and that every check in it is true. Exit status is non-zero if anything fails.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# name: (verifier, committed receipt, extra arguments, slow)
RECEIPTS = {
    "agency_unknown": ("scripts/verify_agency_unknown.py",
                       "output/agency_unknown/unknown_v1.json", [], False),
    "agency_persistence": ("scripts/verify_agency_persistence.py",
                           "output/agency_persistence/persistence_v1.json", [], False),
    "agency_worlds": ("scripts/verify_agency_worlds.py",
                      "output/agency_worlds/agency_v1.json", [], False),
    "design_calculus": ("scripts/verify_evaluation_design_calculus.py",
                        "output/evaluation_design_calculus/v0_verification.json", [], False),
    "prime_atlas": ("scripts/verify_prime_eval_atlas.py",
                    "output/evaluation_design_calculus/prime_atlas_verification.json", [], False),
    "game_testbed": ("scripts/verify_evaluation_game_testbed.py",
                     "output/evaluation_game_testbed/confirmation_v1_1.json", [], False),
    "game_feedback": ("scripts/verify_evaluation_game_feedback.py",
                      "output/evaluation_game_feedback/feedback_v0_2.json", [], False),
    "rsi_atlas": ("scripts/verify_rsi_claims_atlas.py", "output/rsi_claims_atlas/atlas_verification.json", [], False),
    "signal": ("scripts/verify_evaluation_feedback_signal.py",
               "output/evaluation_feedback_signal/signal_v0_1.json", [], False),
    "lattice": ("scripts/verify_evaluation_feedback_lattice.py",
                "output/evaluation_feedback_lattice/lattice_v0_7.json", [], False),
    "composition": ("scripts/verify_evaluation_feedback_composition.py",
                    "output/evaluation_feedback_composition/composition_v0_1.json", [], False),
    "judge": ("scripts/verify_evaluation_judge_measurement.py",
              "output/evaluation_judge_measurement/judge_v0_1.json", [], False),
    "leak_topology": ("scripts/verify_evaluation_leak_topology.py",
                      "output/evaluation_leak_topology/leak_topology_v0_1.json", [], False),
    "selection_kl": ("scripts/verify_evaluation_selection_kl.py",
                     "output/evaluation_selection_kl/selection_kl_v0_4.json", [], False),
    "gold_calibration": ("scripts/verify_evaluation_gold_calibration.py",
                         "output/evaluation_gold_calibration/gold_v0_4.json",
                         ["--sampling-size", "400", "--sampling-size", "742", "--joint-size", "4000",
                          "--coverage-size", "16", "--workers", "4"], True),
    "multigen": ("scripts/verify_evaluation_feedback_multigen.py",
                 "output/evaluation_feedback_multigen/multigen_v0_6.json", ["--full-sweep"], True),
}


def source_hashes(receipt: dict) -> dict:
    for key in ("source_sha256", "sources", "source_hashes"):
        value = receipt.get(key)
        if isinstance(value, dict):
            return value
    return {}


FLOAT_TOLERANCE = 1e-12  # relative; floats in receipts are display values of library functions


def differences(a, b, path="", out=None, limit=8):
    """Paths where two receipts differ. Exact values (strings, integers, fractions written as strings,
    booleans) must match exactly; floats may differ by FLOAT_TOLERANCE relative, because exp, log and
    erfc are not correctly rounded and can differ in the last bit between platforms' math libraries."""
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out.append(f"{path}/{key} (present on one side only)")
            else:
                differences(a[key], b[key], f"{path}/{key}", out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path} (length {len(a)} vs {len(b)})")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                differences(x, y, f"{path}[{i}]", out, limit)
    elif isinstance(a, float) and isinstance(b, float):
        if abs(a - b) > FLOAT_TOLERANCE * max(1.0, abs(a), abs(b)):
            out.append(f"{path} ({a!r} vs {b!r})")
    elif a != b:
        out.append(f"{path} ({str(a)[:80]!r} vs {str(b)[:80]!r})")
    return out


def annotate(level: str, title: str, message: str) -> None:
    """Under GitHub Actions, also emit an annotation, which the public API shows without a login."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::{level} title={title}::{message.replace(chr(10), ' ')[:900]}", flush=True)


def all_checks_true(receipt: dict):
    checks = receipt.get("checks")
    if isinstance(checks, dict):
        return all(v is True for v in checks.values()), len(checks)
    return receipt.get("all_passed", True) is not False, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all", action="store_true", help="include the slow receipts")
    parser.add_argument("--only", nargs="*", help="names to check (default: all fast ones)")
    parser.add_argument("--no-regenerate", action="store_true", help="only check hashes and checks of committed receipts")
    args = parser.parse_args()
    names = args.only or [n for n, spec in RECEIPTS.items() if args.all or not spec[3]]
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""))
    failures = 0
    for name in names:
        verifier, receipt_path, extra, _ = RECEIPTS[name]
        committed = json.loads((ROOT / receipt_path).read_text(encoding="utf-8"))
        ok_checks, n_checks = all_checks_true(committed)
        hashes = source_hashes(committed)
        stale = [rel for rel, digest in hashes.items()
                 if not (ROOT / rel).exists() or hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != digest]
        line = f"{name:17s} checks {n_checks:3d} {'all true' if ok_checks else 'FAILING'}; sources {len(hashes)} " \
               f"{'match' if not stale else 'STALE: ' + ', '.join(stale)}"
        reproduced = None
        if not args.no_regenerate:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "receipt.json"
                run = subprocess.run([sys.executable, str(ROOT / verifier), *extra, "--output", str(out)],
                                     cwd=ROOT, env=env, capture_output=True, text=True)
                if run.returncode != 0 or not out.exists():
                    reproduced = False
                    line += f"; verifier FAILED (exit {run.returncode}): {run.stderr.strip()[-300:]}"
                else:
                    fresh = json.loads(out.read_text(encoding="utf-8"))
                    a, b = dict(committed), dict(fresh)
                    a.pop("generated_at_utc", None)
                    b.pop("generated_at_utc", None)
                    if a == b:
                        reproduced = True
                        line += "; regenerates identically"
                    else:
                        diff = differences(a, b)
                        reproduced = not diff
                        line += ("; regenerates within float tolerance" if reproduced
                                 else f"; REGENERATED DIFFERS at {diff}")
        ok = ok_checks and not stale and reproduced is not False
        if not ok:
            annotate("error", f"receipt {name}", line)
        failures += not ok
        print(("ok   " if ok else "FAIL ") + line, flush=True)
    annotate("notice" if not failures else "error", "receipts",
             f"{len(names) - failures} of {len(names)} receipts verified")
    print(f"{len(names) - failures} of {len(names)} receipts verified")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

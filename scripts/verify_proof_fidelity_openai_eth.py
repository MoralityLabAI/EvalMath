"""Verify a pinned external theorem/Lean fidelity crosswalk; no network or Lean build.

Use --output PATH to write an immutable receipt. Exit nonzero on any drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from spiral_ln.proof_fidelity import FidelityError, run_audit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "configs/openai_eth_fidelity.json"
SOURCE_PATHS = (
    "src/spiral_ln/proof_fidelity.py",
    "scripts/verify_proof_fidelity_openai_eth.py",
    "configs/openai_eth_fidelity.json",
    "paper/proof_fidelity_openai_eth.md",
    "tests/test_proof_fidelity_openai_eth.py",
)


def make_report(root: Path = ROOT) -> dict:
    config = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    result = run_audit(root, config)
    result["schema_version"] = "0.2"
    result["source_sha256"] = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_PATHS
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = make_report()
    except (FidelityError, OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"proof fidelity: {exc}\n")
    report["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(output)
    else:
        print(output, end="")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

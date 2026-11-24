"""Regenerate the finite compiler census; archive integrity is checked separately."""
import argparse
import hashlib
import json
from pathlib import Path
from spiral_ln.evaluation_cpf02 import census

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("src/spiral_ln/evaluation_cpf02.py", "tests/test_evaluation_cpf02.py",
           "scripts/verify_evaluation_cpf02.py", "paper/cpf02_canonical_circuit_bridge.md",
           "lean/FeedbackChannel/CPF02/Canonical.lean")


def report():
    result = census()
    assert result == {"field_program_checks": {"0": 12, "1": 720, "2": 64800},
                      "maximum_charged_gates": {"0": 2, "1": 6, "2": 10}}
    return {"schema": "CPF-02.0", "scope": "finite compiler census, not upstream proof verification",
            "checks": {"formal_polynomial_equality": True, "gate_budget": True}, "census": result,
            "source_sha256": {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.dumps(report(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")

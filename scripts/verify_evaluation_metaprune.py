"""Regenerate MP-01 source-bound local verification receipt; no model calls."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from spiral_ln.evaluation_metaprune import four_state_examples, optimal_choice

ROOT = Path(__file__).resolve().parents[1]
FILES = ["paper/metaprune_decision_value.md",
         "src/spiral_ln/evaluation_metaprune.py",
         "tests/test_evaluation_metaprune.py",
         "scripts/verify_evaluation_metaprune.py"]
def main():
    prior, experiments = four_state_examples()
    value, choice = optimal_choice(prior, experiments, 1)
    assert (value, choice) == (Fraction(11,20), "reveal")
    result = {
        "scope": "exact four-hypothesis toy; no model or laboratory observation",
        "budget": 1, "optimal_first_action": choice,
        "optimal_value": str(value),
        "source_sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()
                          for f in FILES},
    }
    destination = ROOT / "output/metaprune_decision_value/local_receipt.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print(destination)
if __name__ == "__main__":
    main()

"""Score candidate JSONL against evaluator-owned COL-EVAL-01 gold."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from spiral_ln.evaluation_collatz_basin import score_predictions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    gold = [json.loads(line) for line in args.gold.read_text().splitlines() if line.strip()]
    predictions = [json.loads(line) for line in args.predictions.read_text().splitlines() if line.strip()]
    report = score_predictions(gold, predictions)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()

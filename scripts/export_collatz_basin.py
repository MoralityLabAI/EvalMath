"""Export public COL-EVAL-01 prompts separately from evaluator-owned gold."""
from __future__ import annotations

import argparse
import hashlib
import json
from math import gcd
from pathlib import Path

from spiral_ln.evaluation_collatz_basin import enumerate_core, parameter_split, quotient_labels


def export(max_d: int, out: Path, splits: tuple[str, ...]) -> dict:
    if type(max_d) is not int or not 1 <= max_d <= 4093:
        raise ValueError("max_d must lie in 1..4093 for this bounded public fixture")
    if not splits or set(splits) - {"train", "dev"}:
        raise ValueError("this exporter exposes public train/dev only")
    out.mkdir(parents=True, exist_ok=True)
    root_counts, case_counts = {}, {}
    for split in sorted(set(splits)):
        prompts, gold = [], []
        roots = []
        for d in range(1, max_d + 1, 4):
            if gcd(d, 6) != 1 or parameter_split(d) != split:
                continue
            roots.append(d)
            core, quotient = enumerate_core(d), quotient_labels(d)
            for n in core.states:
                case_id = f"COL:{d}:{n}"
                prompts.append({"id": case_id, "root_id": f"d:{d}", "split": split,
                                "task": "eventual_basin", "input": {"d": d, "n": n},
                                "answer_schema": {"cycle_minimum": "positive odd integer"}})
                gold.append({"id": case_id, "cycle_minimum": core.basin[n],
                             "depth": core.depth[n], "quotient": quotient[n % d],
                             "gcd": gcd(n, d)})
        for name, values in (("prompts", prompts), ("gold", gold)):
            (out / f"{split}.{name}.jsonl").write_text("".join(json.dumps(v, sort_keys=True) + "\n" for v in values))
        root_counts[split], case_counts[split] = len(roots), len(prompts)
    report = {"schema": "COL-EVAL-01/export/v1", "max_parameter": max_d,
              "parameter_roots": root_counts, "cases": case_counts,
              "gold_is_evaluator_owned": True, "holdout_exported": False,
              "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(out.glob("*.jsonl"))}}
    (out / "manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-d", type=int, default=1021)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--split", action="append", choices=["train", "dev"])
    args = p.parse_args()
    print(json.dumps(export(args.max_d, args.output, tuple(args.split or ["train", "dev"])), indent=2))


if __name__ == "__main__":
    main()

"""Replay COG02/03 attempts using an independent verifier and frozen run registry."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spiral_ln.cogentic_ledger import evaluate, paired_manifest
from spiral_ln.evaluation_finite_sample import evaluate_manifest


def read_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tasks", type=Path, required=True)
    p.add_argument("--attempts", type=Path, required=True)
    p.add_argument("--protocol", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--compare", action="append", default=[], metavar="CANDIDATE:BASELINE")
    a = p.parse_args()
    protocol = json.loads(a.protocol.read_text())
    expected_tasks = protocol.get("expected_tasks_file_sha256")
    if expected_tasks is not None and hashlib.sha256(a.tasks.read_bytes()).hexdigest() != expected_tasks:
        raise ValueError("task file differs from frozen protocol")
    # A larger input may include calibration traces. Filtering is declared by
    # the registered splits; the complete expected root product stays in scope.
    tasks = read_rows(a.tasks)
    events = [r for r in read_rows(a.attempts) if r["split"] in protocol["splits"]]
    report = evaluate(tasks, events, protocol)
    report["input_files"] = {name: {"filename": path.name,
                                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                             for name, path in [("tasks", a.tasks), ("attempts", a.attempts),
                                                ("protocol", a.protocol)]}
    report["source_sha256"] = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in ["src/spiral_ln/cogentic_ledger.py", "scripts/score_cogentic_ledger.py",
                     "src/spiral_ln/evaluation_finite_sample.py"]}
    report["paired_comparisons"] = []
    for contrast in a.compare:
        candidate, baseline = contrast.split(":")
        for split in protocol["splits"]:
            manifest = paired_manifest(report, candidate, baseline, split,
                                       comparisons=len(a.compare) * len(protocol["splits"]))
            report["paired_comparisons"].append(evaluate_manifest(manifest))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    for row in report["summary"]:
        print(json.dumps({k: row[k] for k in ["arm", "split", "independent_roots", "seed_runs",
                                             "solved_runs", "verifier_calls", "missing_runs"]}))


if __name__ == "__main__":
    main()

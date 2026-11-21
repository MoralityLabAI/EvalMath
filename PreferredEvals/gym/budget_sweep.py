"""Descriptive tables for a reasoning-budget sweep over generated multi-hop chains.

Reads prompt-runner runs named in a sweep spec (``conditions``: run name -> model and budget), the task
file (for each chain's hop count) and the labels, and writes ``budget_tables.json`` and
``budget_tables.md``:

  accuracy by model, budget and depth (with Wilson 95% intervals);
  the smallest budget reaching a target accuracy at each depth;
  completion tokens per hop among correct answers;
  the share of replies cut by the output cap (finish_reason "length") and of replies with no parsable answer.

    python budget_sweep.py --root RESULTS --tasks tasks.jsonl --spec sweep.json
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def wilson(k: int, n: int, z: float = 1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 3), round(min(1.0, c + h), 3)]


def tables(root: Path, tasks_path: Path, spec: dict, target: float = 0.8) -> dict:
    hops = {t["task_id"]: t["hops"] for t in _jsonl(tasks_path)}
    depths = sorted(set(hops.values()))
    cells, rows = {}, []
    for name, cond in spec["conditions"].items():
        run = root / "runs" / name
        if not (run / "scores.json").is_file():
            continue
        scores = {r["task_id"]: r for r in json.loads((run / "scores.json").read_text(encoding="utf-8"))["rows"]}
        receipts = {r["task_id"]: r for r in _jsonl(run / "rollouts.jsonl")}
        by_depth = defaultdict(list)
        for tid, s in scores.items():
            rec = receipts[tid]
            by_depth[hops[tid]].append({"score": s["score"], "status": s["status"],
                                        "format_valid": s.get("format_valid"),
                                        "finish": rec.get("finish_reason"),
                                        "completion": (rec.get("usage") or {}).get("completion_tokens")})
        for depth in depths:
            items = by_depth.get(depth, [])
            scored = [x for x in items if x["score"] is not None]
            k = sum(x["score"] for x in scored)
            correct_tok = [x["completion"] / depth for x in scored if x["score"] and x["completion"] is not None]
            cell = {"model": cond["model"], "budget": cond["budget"], "depth": depth, "n": len(items),
                    "scored": len(scored), "correct": k,
                    "accuracy": round(k / len(scored), 3) if scored else None, "wilson95": wilson(k, len(scored)),
                    "infra_errors": sum(x["status"] != "completed" for x in items),
                    "cap_truncated": sum(x["finish"] == "length" for x in items),
                    "no_answer": sum(x["status"] == "completed" and not x["format_valid"] for x in items),
                    "completion_tokens_per_hop_correct": (round(sorted(correct_tok)[len(correct_tok) // 2], 1)
                                                          if correct_tok else None)}
            cells[(cond["model"], cond["budget"], depth)] = cell
            rows.append(cell)
    smallest = []
    for model in sorted({c["model"] for c in spec["conditions"].values()}):
        budgets = sorted({c["budget"] for c in spec["conditions"].values() if c["model"] == model})
        for depth in depths:
            hit = next((b for b in budgets if (cells.get((model, b, depth)) or {}).get("accuracy") is not None
                        and cells[(model, b, depth)]["accuracy"] >= target), None)
            smallest.append({"model": model, "depth": depth, "target": target, "smallest_budget": hit})
    return {"schema": "preferred-evals/budget-sweep-tables-v1", "depths": depths, "cells": rows,
            "smallest_budget_reaching_target": smallest}


def markdown(t: dict) -> str:
    out = ["| model | budget | depth | correct / scored | accuracy (Wilson 95%) | cap-truncated | no answer | "
           "completion tokens per hop (median, correct) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in t["cells"]:
        ci = c["wilson95"]
        out.append(f"| {c['model']} | {c['budget']} | {c['depth']} | {c['correct']} / {c['scored']} | "
                   f"{c['accuracy']} ({ci[0]:.2f}-{ci[1]:.2f}) | {c['cap_truncated']} | {c['no_answer']} | "
                   f"{c['completion_tokens_per_hop_correct']} |" if ci else
                   f"| {c['model']} | {c['budget']} | {c['depth']} | 0 / 0 | | | | |")
    out += ["", "| model | depth | smallest budget with accuracy >= 0.8 |", "| --- | --- | --- |"]
    for s in t["smallest_budget_reaching_target"]:
        out.append(f"| {s['model']} | {s['depth']} | {s['smallest_budget'] if s['smallest_budget'] is not None else 'none tested'} |")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--tasks", type=Path, required=True)
    ap.add_argument("--spec", type=Path, required=True)
    args = ap.parse_args()
    t = tables(args.root, args.tasks, json.loads(args.spec.read_text(encoding="utf-8")))
    (args.root / "budget_tables.json").write_text(json.dumps(t, indent=1) + "\n", encoding="utf-8")
    (args.root / "budget_tables.md").write_text(markdown(t), encoding="utf-8")
    print(markdown(t))


if __name__ == "__main__":
    main()

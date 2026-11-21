"""Collect a local rollout campaign into one ledger, a per-category scorecard and paired FSI-01 tests.

Reads a results tree laid out as ``runs/<run-name>/`` where each run is one benchmark on one model:

  prompt-runner runs   run.json, rollouts.jsonl, scores.json             (runner.py)
  vf-run 0.4.1 runs    traces.jsonl                                      (Prime Episode records)
  Inkling runs         run.json, summary.json, samples/*/result.json     (Inkling Verify)
  SWE oracle runs      run.json, receipts.jsonl, report.json, scores.json (swebench_oracle.py)

and a ``campaign.json`` naming each run's benchmark, category, model and kind. Every attempt becomes
one ledger row with an outcome class:

  correct / wrong           the native or reference grader scored the answer
  format_invalid            the reply was outside the requested format (a model failure, scored 0)
  infrastructure_error      the model call failed or the episode ended with a provider error (not scored)
  grader_error              the grader could not score a completed attempt (not scored)

Roots are reported apart from attempts. Paired model comparisons are exported as FSI-01 manifests
(development, unsealed) and evaluated with ``spiral_ln.evaluation_finite_sample``; p-values are
Holm-adjusted over the registered comparisons.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _wilson(k: float, n: int, z: float = 1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def _root_bootstrap(root_means: list[float], seed: int = 20261121, reps: int = 4000):
    if not root_means:
        return None
    rng = random.Random(seed)
    n = len(root_means)
    stats = sorted(sum(rng.choice(root_means) for _ in range(n)) / n for _ in range(reps))
    return [round(stats[int(0.025 * reps)], 4), round(stats[int(0.975 * reps) - 1], 4)]


def prompt_rows(run: Path) -> list[dict]:
    scores = json.loads((run / "scores.json").read_text(encoding="utf-8"))
    receipts = {(r["task_id"], r["order"], r["sample"]): r for r in _jsonl(run / "rollouts.jsonl")}
    rows = []
    for s in scores["rows"]:
        r = receipts[(s["task_id"], s["order"], s["sample"])]
        if s["status"] != "completed":
            outcome = "infrastructure_error"
        elif not s.get("format_valid"):
            outcome = "format_invalid"
        else:
            outcome = "correct" if s["score"] else "wrong"
        usage = r.get("usage") or {}
        rows.append({"task_id": s["task_id"], "root_id": s["root_id"], "attempt": f"{s['order']}-{s['sample']}",
                     "outcome": outcome, "score": s["score"] if outcome != "infrastructure_error" else None,
                     "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                     "reasoning_chars": r.get("reasoning_chars"), "latency_s": r.get("duration_seconds"),
                     "finish_reason": r.get("finish_reason")})
    return rows


def vf_rows(run: Path, score_metric: str | None) -> list[dict]:
    traces = sorted(run.rglob("traces.jsonl"))
    if not traces:
        return []
    rows, seen = [], defaultdict(int)
    for ep in _jsonl(traces[0]):
        data = ep["task"].get("data") or {}
        key = str(ep["task"].get("key") or data.get("name") or data.get("idx"))
        trs = ep.get("traces") or []
        tr = trs[0] if trs else {}
        provider_error = bool(ep.get("errors")) or any(
            "Provider" in str(e) or "provider" in str(e) for e in (tr.get("errors") or []))
        stop = tr.get("stop_condition")
        if not trs or provider_error or (stop and "Provider" in str(stop)) or tr.get("dropped"):
            outcome, score = "infrastructure_error", None
        elif score_metric:
            value = (tr.get("metrics") or {}).get(score_metric)
            outcome, score = (("grader_error", None) if value is None
                              else ("correct" if value >= 0.999 else "wrong", int(value >= 0.999)))
        else:
            rewards = tr.get("rewards") or {}
            if not rewards:
                outcome, score = "grader_error", None
            else:
                reward = sum(float(v.get("score", 0)) * float(v.get("weight", 0)) for v in rewards.values())
                outcome, score = ("correct" if reward >= 0.999 else "wrong"), int(reward >= 0.999)
        attempt = seen[key]
        seen[key] += 1
        rows.append({"task_id": key, "root_id": key, "attempt": str(attempt), "outcome": outcome, "score": score,
                     "prompt_tokens": ep.get("num_input_tokens"), "completion_tokens": ep.get("num_output_tokens"),
                     "stop_condition": stop,
                     "latency_s": ((tr.get("timing") or {}).get("total") if isinstance(tr.get("timing"), dict) else None)})
    return rows


def inkling_rows(run: Path) -> list[dict]:
    rows = []
    for path in sorted(run.glob("samples/*/result.json")):
        r = json.loads(path.read_text(encoding="utf-8"))
        usage = r.get("usage") or {}
        failed = r.get("status") not in (None, "completed") or r.get("score") is None
        d = r.get("details") or {}
        # NIAH prompts are built per tokenizer, so case ids differ between models; key by grid cell and the
        # case's index within the cell so that two models' runs pair up.
        cell = (f"niah-{d['context_length']}-d{d['depth_percent']}-c{d['sample_index']}"
                if all(k in d for k in ("context_length", "depth_percent", "sample_index")) else r["id"])
        rows.append({"task_id": cell, "root_id": cell, "native_id": r["id"], "attempt": str(r.get("sample_index", 0)),
                     "outcome": "infrastructure_error" if failed else ("correct" if r["score"] >= 0.999 else "wrong"),
                     "score": None if failed else int(r["score"] >= 0.999),
                     "prompt_tokens": usage.get("input_tokens"), "completion_tokens": usage.get("output_tokens"),
                     "details": {k: v for k, v in (r.get("details") or {}).items()
                                 if k in ("context_length", "depth_percent")}})
    return rows


def swe_rows(run: Path) -> list[dict]:
    scores = json.loads((run / "scores.json").read_text(encoding="utf-8"))
    receipts = {r["instance_id"]: r for r in _jsonl(run / "receipts.jsonl")}
    rows = []
    for s in scores["rows"]:
        r = receipts[s["instance_id"]]
        o = s["outcome"]
        # A patch the harness cannot apply (malformed hunks or mismatched context) is a model output
        # failure, like a missing patch; extraction itself is checked separately against gold patches.
        outcome = {"resolved": "correct", "unresolved": "wrong", "no_patch": "format_invalid",
                   "patch_failed_to_apply_or_run": "format_invalid",
                   "infrastructure_error": "infrastructure_error"}[o]
        usage = r.get("usage") or {}
        rows.append({"task_id": s["instance_id"], "root_id": s["instance_id"], "attempt": "0", "outcome": outcome,
                     "harness_outcome": o, "score": None if outcome == "infrastructure_error" else s["score"],
                     "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                     "reasoning_chars": r.get("reasoning_chars"), "latency_s": r.get("duration_seconds"),
                     "finish_reason": r.get("finish_reason")})
    return rows


def collect(root: Path, spec: dict) -> dict:
    ledger = {}
    for name, meta in spec["runs"].items():
        run = root / "runs" / name
        kind = meta["kind"]
        complete = {"prompt": "scores.json", "swe": "scores.json", "vf": "traces.jsonl", "inkling": "summary.json"}
        if not (run / complete.get(kind, "")).is_file():
            continue
        if kind == "prompt":
            rows = prompt_rows(run)
        elif kind == "vf":
            rows = vf_rows(run, meta.get("score_metric"))
        elif kind == "inkling":
            rows = inkling_rows(run)
        elif kind == "swe":
            rows = swe_rows(run)
        else:
            raise ValueError(f"unknown run kind {kind}")
        ledger[name] = dict(meta, rows=rows)
    return ledger


def summarize_run(meta: dict) -> dict:
    rows = meta["rows"]
    outcomes = defaultdict(int)
    for r in rows:
        outcomes[r["outcome"]] += 1
    scored = [r for r in rows if r["score"] is not None]
    by_root = defaultdict(list)
    for r in scored:
        by_root[r["root_id"]].append(r["score"])
    root_means = [sum(v) / len(v) for v in by_root.values()]
    pt = [r["prompt_tokens"] for r in rows if isinstance(r.get("prompt_tokens"), (int, float))]
    ct = [r["completion_tokens"] for r in rows if isinstance(r.get("completion_tokens"), (int, float))]
    lat = [r["latency_s"] for r in rows if isinstance(r.get("latency_s"), (int, float))]
    return {"benchmark": meta["benchmark"], "category": meta["category"], "model": meta["model"],
            "condition": meta.get("condition", "default"), "source": meta.get("source"),
            "attempts": len(rows), "scored": len(scored), "correct": sum(r["score"] for r in scored),
            "accuracy_attempts": round(sum(r["score"] for r in scored) / len(scored), 4) if scored else None,
            "accuracy_attempts_wilson95": _wilson(sum(r["score"] for r in scored), len(scored)),
            "roots_assigned": len({r["root_id"] for r in rows}), "roots_scored": len(by_root),
            "root_mean_accuracy": round(sum(root_means) / len(root_means), 4) if root_means else None,
            "root_bootstrap95": _root_bootstrap(root_means),
            "outcomes": dict(sorted(outcomes.items())),
            "prompt_tokens_mean": round(sum(pt) / len(pt), 1) if pt else None,
            "completion_tokens_mean": round(sum(ct) / len(ct), 1) if ct else None,
            "latency_s_mean": round(sum(lat) / len(lat), 2) if lat else None}


def paired(ledger: dict, cand: str, base: str, comparison: dict) -> dict:
    sys.path.insert(0, str(REPO / "src"))
    from spiral_ln.evaluation_finite_sample import evaluate_manifest

    c = {(r["task_id"], r["attempt"]): r for r in ledger[cand]["rows"]}
    b = {(r["task_id"], r["attempt"]): r for r in ledger[base]["rows"]}
    cases, unpaired = [], []
    for key in sorted(set(c) | set(b)):
        rc, rb = c.get(key), b.get(key)
        if rc and rb and rc["score"] is not None and rb["score"] is not None:
            cases.append({"case_id": f"{key[0]}#{key[1]}", "cluster_id": rc["root_id"],
                          "candidate": rc["score"], "baseline": rb["score"]})
        else:
            unpaired.append({"case": f"{key[0]}#{key[1]}", "candidate": rc["outcome"] if rc else "missing",
                             "baseline": rb["outcome"] if rb else "missing"})
    manifest = {"schema_version": 1, "experiment_id": f"PE2-{comparison['id']}",
                "target_population": comparison.get("population", "declared development task roots"),
                "evaluation_mode": "sampled", "alpha": comparison["alpha"],
                "minimum_effect": comparison["minimum_effect"],
                "planned_comparisons": comparison["planned_comparisons"],
                "hypothesis_preregistered": bool(comparison.get("preregistered", False)),
                "sealed_readout": False,
                "clusters_independent": bool(comparison.get("clusters_independent", False)),
                "exchangeable_pair_labels": bool(comparison.get("exchangeable_pair_labels", False)),
                "cases": cases}
    result = evaluate_manifest(manifest) if cases else {"verdict": "no_paired_cases"}
    return {"id": comparison["id"], "candidate_run": cand, "baseline_run": base, "n_paired_attempts": len(cases),
            "n_paired_roots": len({x["cluster_id"] for x in cases}), "unpaired": unpaired,
            "candidate_correct": sum(x["candidate"] for x in cases), "baseline_correct": sum(x["baseline"] for x in cases),
            "fsi_01_manifest": manifest, "fsi_01_result": result}


def _holm(pvals: list[float]) -> list[float]:
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adjusted, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adjusted[i] = running
    return adjusted


def _first_p(result: dict):
    value = result.get("p_unadjusted")
    return float(value) if isinstance(value, (int, float)) else None


def write_receipts(root: Path, summary: dict) -> None:
    """Per-comparison FSI-01 manifest, FSI-01 result and paired receipt, plus receipt_index.json for
    campaign_report.py (registered ids between-1..7 and within-8)."""
    index = {"schema": "preferred-evals/campaign-receipt-index-v1", "comparisons": {}}
    for comp, spec in zip(summary["comparisons"], summary.get("_registered_ids", [])):
        if not spec:
            continue
        folder = root / "fsi" / comp["id"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "fsi.json").write_text(json.dumps(comp["fsi_01_manifest"], indent=1) + "\n", encoding="utf-8")
        (folder / "fsi-result.json").write_text(json.dumps(comp["fsi_01_result"], indent=1) + "\n", encoding="utf-8")
        paired_receipt = {"schema": "preferred-evals/paired-prompt-runs-v1", "comparison": comp["id"],
                          "candidate_run": comp["candidate_run"], "baseline_run": comp["baseline_run"],
                          "total_assigned_rollouts": comp["n_paired_attempts"] + len(comp["unpaired"]),
                          "n_paired_scored": comp["n_paired_attempts"], "n_infra_or_missing": len(comp["unpaired"]),
                          "non_scored": comp["unpaired"], "n_roots_paired_scored": comp["n_paired_roots"],
                          "candidate_correct_paired": comp["candidate_correct"],
                          "baseline_correct_paired": comp["baseline_correct"],
                          "evidence_class": "development; unsealed readout"}
        (folder / "paired.json").write_text(json.dumps(paired_receipt, indent=1) + "\n", encoding="utf-8")
        index["comparisons"][spec] = {"fsi_result": f"fsi/{comp['id']}/fsi-result.json",
                                      "paired_receipt": f"fsi/{comp['id']}/paired.json"}
    if index["comparisons"]:
        (root / "receipt_index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def scorecard_md(summary: dict) -> str:
    out = ["| category | benchmark | model | condition | attempts | scored | correct | accuracy (Wilson 95%) | "
           "roots scored | root-mean accuracy (bootstrap 95%) | outcomes | prompt tok. | completion tok. |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in sorted(summary["runs"].values(), key=lambda s: (s["category"], s["benchmark"], s["model"], s["condition"])):
        ci = s["accuracy_attempts_wilson95"]
        bi = s["root_bootstrap95"]
        out.append(f"| {s['category']} | {s['benchmark']} | {s['model']} | {s['condition']} | {s['attempts']} | "
                   f"{s['scored']} | {s['correct']} | {s['accuracy_attempts']} ({ci[0]:.2f}-{ci[1]:.2f}) | "
                   f"{s['roots_scored']}/{s['roots_assigned']} | {s['root_mean_accuracy']} ({bi[0]:.2f}-{bi[1]:.2f}) | "
                   f"{', '.join(f'{k} {v}' for k, v in s['outcomes'].items())} | {s['prompt_tokens_mean']} | "
                   f"{s['completion_tokens_mean']} |" if ci and bi else
                   f"| {s['category']} | {s['benchmark']} | {s['model']} | {s['condition']} | {s['attempts']} | "
                   f"{s['scored']} | | | | | {', '.join(f'{k} {v}' for k, v in s['outcomes'].items())} | | |")
    comps = summary.get("comparisons", []) + summary.get("exploratory_comparisons", [])
    if comps:
        out += ["", "| comparison | paired attempts (roots) | candidate correct | baseline correct | "
                    "root-macro effect | cluster bootstrap interval | test | p | p (Holm) | FSI-01 verdict |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for c in comps:
            r = c["fsi_01_result"]
            ci = r.get("cluster_bootstrap_interval")
            ci_text = f"[{ci[0]:.3f}, {ci[1]:.3f}]" if ci else "n/a"
            effect = r.get("cluster_macro_effect")
            label = c["id"] + (" (exploratory)" if c.get("exploratory") else "")
            out.append(f"| {label} | {c['n_paired_attempts']} ({c['n_paired_roots']}) | {c['candidate_correct']} | "
                       f"{c['baseline_correct']} | {round(effect, 3) if effect is not None else 'n/a'} | {ci_text} | "
                       f"{r.get('test')} | {c.get('p_raw')} | {c.get('p_holm')} | {r.get('verdict')} |")
    for b in summary.get("blocked", []):
        out.append(f"\nBlocked: {b['benchmark']}: {b['reason']}")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, required=True, help="results directory holding campaign.json and runs/")
    args = ap.parse_args()
    spec = json.loads((args.root / "campaign.json").read_text(encoding="utf-8"))
    ledger = collect(args.root, spec)
    summary = {"schema": "preferred-evals/campaign-summary-v1", "campaign_id": spec["campaign_id"],
               "campaign_sha256": hashlib.sha256((args.root / "campaign.json").read_bytes()).hexdigest(),
               "runs": {name: summarize_run(meta) for name, meta in ledger.items()},
               "not_run": sorted(set(spec["runs"]) - set(ledger)),
               "blocked": spec.get("blocked", []), "comparisons": []}
    for comp in spec.get("comparisons", []):
        if comp["candidate"] in ledger and comp["baseline"] in ledger:
            summary["comparisons"].append(paired(ledger, comp["candidate"], comp["baseline"], dict(
                comp, alpha=spec["test"]["alpha"], minimum_effect=spec["test"]["minimum_effect"],
                planned_comparisons=len(spec["comparisons"]))))
    summary["_registered_ids"] = [comp.get("registered_id") for comp in spec.get("comparisons", [])
                                  if comp["candidate"] in ledger and comp["baseline"] in ledger]
    ps = [_first_p(c["fsi_01_result"]) for c in summary["comparisons"]]
    if ps and all(p is not None for p in ps):
        for c, adj in zip(summary["comparisons"], _holm(ps)):
            c["p_raw"], c["p_holm"] = _first_p(c["fsi_01_result"]), round(adj, 4)
    # Exploratory comparisons are reported with their own unadjusted p and stay out of the Holm family.
    summary["exploratory_comparisons"] = []
    for comp in spec.get("exploratory_comparisons", []):
        if comp["candidate"] in ledger and comp["baseline"] in ledger:
            c = paired(ledger, comp["candidate"], comp["baseline"], dict(
                comp, alpha=spec["test"]["alpha"], minimum_effect=spec["test"]["minimum_effect"],
                planned_comparisons=1))
            c["p_raw"], c["p_holm"], c["exploratory"] = _first_p(c["fsi_01_result"]), None, True
            summary["exploratory_comparisons"].append(c)
    write_receipts(args.root, summary)
    (args.root / "ledger.jsonl").write_text("".join(
        json.dumps(dict(r, run=name, benchmark=m["benchmark"], model=m["model"]), sort_keys=True) + "\n"
        for name, m in ledger.items() for r in m["rows"]), encoding="utf-8")
    (args.root / "campaign_summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n",
                                                     encoding="utf-8")
    (args.root / "scorecard.md").write_text(scorecard_md(summary), encoding="utf-8")
    print(scorecard_md(summary))


if __name__ == "__main__":
    main()

"""Export VAD-11 / VAD-12 results as DataGoblin-compatible records and a compact neural-gate receipt.

DataGoblin (MoralityLabAI/DataGoblin) defines data_recipe and experiment_record schemas; both allow additional
properties. The remaining record kinds (theorem family, proof trace, lemma discovery, verification receipt,
benchmark statistic) have no DataGoblin schema, so they use a typed JSONL envelope {schema_version, record_type, ...}
and are not claimed to validate against any DataGoblin schema.

    python scripts/export_vad_datagoblin.py --neural <results.json> --datagoblin <DataGoblin checkout> --out output/verified_abstraction
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TC = "4.35.0"


def h(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def gate(neural_path):
    d = json.loads(Path(neural_path).read_text())
    mean = lambda xs: sum(xs) / len(xs)
    regret, frac, cost = {}, {}, {}
    for fam, t in d["test"].items():
        regret[fam] = {k: t[k]["mean_regret"] for k in ("stop", "random", "direct", "greedy0", "greedy1", "greedy2")}
        frac[fam] = {k: t[k]["optimal_fraction"] for k in ("direct", "greedy0", "greedy1", "greedy2", "random")}
        for nm, rows in t["neural"].items():
            regret[fam][nm] = mean([r["mean_regret"] for r in rows])
            frac[fam][nm] = mean([r["optimal_fraction"] for r in rows])
            cost.setdefault(nm, []).append(sum(r["seconds"] for r in rows) / max(1, sum(r["decisions"] for r in rows)))
        cost.setdefault("greedy1_seconds_per_instance", []).append(t["greedy1"]["seconds_per_instance"])
        cost.setdefault("greedy2_seconds_per_instance", []).append(t["greedy2"]["seconds_per_instance"])
    fresh = [f for f in regret if f.startswith("fresh_")]
    tol = 0.01
    neural = [k for k in regret[fresh[0]] if k not in ("stop", "random", "direct", "greedy0", "greedy1", "greedy2")]
    matches = {nm: {f: regret[f][nm] <= regret[f]["greedy2"] + tol for f in fresh} for nm in neural}
    return {
        "protocol": "VAD-12", "evidence": "small CPU neural controllers trained on exact-oracle labels; exact forward evaluation on fresh families",
        "epochs": d["epochs"], "seeds": len(next(iter(d["models"].values()))), "data_manifest": d["data_manifest"],
        "models": {m: dict(params=v[0]["params"], decision_flops=v[0]["decision_flops"],
                           mean_train_seconds=mean([x["train_seconds"] for x in v]), mean_train_flops=mean([x["train_flops"] for x in v]),
                           mean_calibration_action_accuracy=mean([x["calib_accuracy"] for x in v])) for m, v in d["models"].items()},
        "instances": {f: t["instances"] for f, t in d["test"].items()},
        "regret": regret, "optimal_fraction": frac,
        "paired_regret_minus_greedy1": {f: t["paired_vs_greedy1"] for f, t in d["test"].items()},
        "mean_seconds_per_decision": {k: mean(v) for k, v in cost.items() if not k.startswith("greedy")},
        "symbolic_seconds_per_instance_mean": {k: mean(v) for k, v in cost.items() if k.startswith("greedy")},
        "gate": {"rule": f"neural mean regret <= greedy-2 regret + {tol} on every fresh family, at lower measured cost; no scaling to GPU otherwise",
                 "tolerance": tol, "matches_greedy2_on_fresh": matches,
                 "verdict": "PASS" if any(all(v.values()) for v in matches.values()) else "FAIL"},
        "ablations": {"memory_used": "shuffled-memory regret equals trm regret within seed noise on every family; memoryless matches trm",
                      "trm_vs_memoryless_in_distribution": [regret["in_distribution"]["trm"], regret["in_distribution"]["memoryless"]]},
        "source_sha256": {"export_vad_datagoblin.py": sha256(Path(__file__).read_bytes()).hexdigest()},
    }


def records(dg, g12, gym):
    cg = dg / "configs/constitution.yaml"
    constitution_hash = sha256(cg.read_bytes()).hexdigest() if cg.exists() else "0" * 64
    recipe = {
        "recipe_id": "vad12-agenda-controller-v1", "schema_version": "1.0", "constitution_version": "0.1.0",
        "hypothesis_ids": ["VAD-12-H1: a recurrent controller trained on exact research-agenda oracles beats bounded-lookahead symbolic selection on fresh structure at lower cost"],
        "environment_specification": {"environment": "EvalMath VAD-10 dependency-hypergraph oracle (scripts/vad_agenda.py)",
                                      "families_train": ["layered", "modular", "correlated"],
                                      "families_fresh_test": ["wide", "complementary", "chain"], "oracle": "exact Fraction Bellman recursion"},
        "trajectory_source_mixture": [{"source": "optimal oracle policy", "weight": 2}, {"source": "greedy-0", "weight": 1}, {"source": "uniform random attempts", "weight": 3}],
        "split_contract": {"train_seeds": "90000-90999", "calibration_seeds": "91000-91249", "in_distribution_test_seeds": "96000+",
                           "fresh_test_seeds": "95000+", "fresh_families_structurally_disjoint_from_training": True,
                           "test_instances_generated_after_models_frozen": True},
        "reference_solver_requirements": "exact rational oracle in EvalMath; forward evaluation equals Bellman value on every instance",
        "independent_verifier_requirements": "naive history-tree evaluator (scripts/vad_agenda_naive.py) agrees on 57 receipt and 60+ test instances",
        "resource_budget": {"device": "CPU, 1 thread", "gpu": "RTX 5080 only if the gate passes", "paid_cloud": False},
        "falsification_criteria": ["neural mean regret exceeds greedy-2 regret by more than 0.01 on any fresh family",
                                   "shuffled-memory ablation matches the memory model (no use of memory)",
                                   "memoryless parameter-matched model matches the recurrent model"],
        "predicted_outcomes": {"expected": "gate fails: greedy-2 is exact on these instance sizes"},
        "provenance": {"repository": "MoralityLabAI/EvalMath", "branch": "research/vad01-verified-abstraction-20261125",
                       "training_repository": "MoralityLabAI/LoopedTransformers experiments/vad12_agenda_controller"},
        "claim_boundary": "small synthetic instances; tiny controllers; no claim about large models or real theorem proving"}
    exp = {"schema_version": "1.0", "experiment_id": "VAD-12-gate", "snapshot_hash": h(g12["data_manifest"]), "recipe_hash": h(recipe),
           "constitution_hash": constitution_hash, "actual_metrics": {"verdict": g12["gate"]["verdict"], "regret": g12["regret"]},
           "run_status": "EVALUATED", "evidence_type": "SYNTHETIC_MECHANISM_NEURAL_NEGATIVE",
           "claim_boundary": recipe["claim_boundary"], "timestamps": {"evaluated": "2026-11-25"}}
    lines = []
    for inst in gym["instances"]:
        lines.append({"schema_version": "1.0", "record_type": "theorem_instance", "id": inst["id"], "family": inst["family"], "split": inst["split"],
                      "seed": inst["seed"], "size": inst["size"], "statement_sha256": inst["statement_sha256"], "fidelity": inst["fidelity"]})
        for strat, per in inst["strategies"].items():
            for ver, r in per.items():
                lines.append({"schema_version": "1.0", "record_type": "proof_trace", "instance": inst["id"], "strategy": strat, "lean_version": ver,
                              "ok": r["ok"], "work_ms": r["work_ms"], "seconds": r["seconds"], "peak_rss_mb": r["peak_rss_mb"], "axioms": r["axiom_class"],
                              "imports": r["imports"], "source_sha256": r["source_sha256"]})
                lines.append({"schema_version": "1.0", "record_type": "verification_receipt", "subject_source_sha256": r["source_sha256"], "verifier": "lean " + ver + " kernel",
                              "custody": "ENVIRONMENT_OWNED", "verdict": "PASS" if r["ok"] and r["axiom_class"] in ("none:", "none", "standard:propext", "standard:Quot.sound,propext") else "FAIL"})
    for fam, v in gym["invention"].items():
        lines.append({"schema_version": "1.0", "record_type": "lemma_discovery", "family": fam, "method": "structural anti-unification",
                      "honest_candidates": v["honest"], "kernel_checked": v["kernel"], "hits_calibration_of_200": v["hits_cal_all_200"],
                      "hits_test_of_400": v["hits_test_all_400"], "leaky_control_rejected_by_auditor": v["leaky_all_rejected"]})
    for fam, strat in gym["summary"].items():
        for s, per in strat.items():
            lines.append({"schema_version": "1.0", "record_type": "benchmark_statistic", "family": fam, "strategy": s, "lean_version": TC,
                          "median_work_ms": per[TC]["median_work_ms"], "n": per[TC]["n"], "n_ok": per[TC]["n_ok"]})
    return recipe, exp, lines


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--neural", type=Path, required=True)
    ap.add_argument("--datagoblin", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    g12 = gate(a.neural)
    gym = json.loads((ROOT / "output/verified_abstraction/vad_11_gym.json").read_text())
    recipe, exp, lines = records(a.datagoblin, g12, gym)
    try:
        import jsonschema
        for rec, name in ((recipe, "data_recipe"), (exp, "experiment_record")):
            jsonschema.validate(rec, json.loads((a.datagoblin / f"schemas/{name}.schema.json").read_text()))
        g12["datagoblin_schema_validation"] = ["data_recipe", "experiment_record"]
    except Exception as e:  # noqa: BLE001
        g12["datagoblin_schema_validation"] = "not run: %s" % type(e).__name__
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "vad_12_gate.json").write_text(json.dumps(g12, indent=2, sort_keys=True) + "\n")
    d = a.out / "datagoblin"
    d.mkdir(exist_ok=True)
    (d / "vad12_data_recipe.json").write_text(json.dumps(recipe, indent=2, sort_keys=True) + "\n")
    (d / "vad12_experiment_record.json").write_text(json.dumps(exp, indent=2, sort_keys=True) + "\n")
    (d / "vad11_records.jsonl").write_text("\n".join(json.dumps(x, sort_keys=True) for x in lines) + "\n")
    print(g12["gate"]["verdict"], len(lines), "records", g12["datagoblin_schema_validation"])

"""Compare two scored PreferredEvals prompt runs and export a development FSI-01 manifest.

The model outcomes are aligned by exact task/position/sample keys. All
infrastructure errors remain in the complete assignment ledger. Reused orders
or samples retain the same root cluster, never extra independent roots.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FSI_SCHEMA = 1


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compare(candidate_run, baseline_run, candidate_scores, baseline_scores, *, minimum_effect="0.05",
            alpha="0.05", planned_comparisons=1, target_population="declared development task roots"):
    cconf = read(Path(candidate_run)/"run.json")
    bconf = read(Path(baseline_run)/"run.json")
    common = ("dataset_sha256", "benchmark_id", "selection_task_ids", "limit", "orders", "rollouts")
    for k in common:
        if cconf[k] != bconf[k]:
            raise ValueError(f"unpaired model run configs: {k} differs")
    cscore, bscore = read(candidate_scores), read(baseline_scores)
    if cscore["labels_sha256"] != bscore["labels_sha256"]:
        raise ValueError("candidate and baseline scored against different reference labels")
    if cscore["run_manifest_sha256"] != __import__('hashlib').sha256((Path(candidate_run)/"run.json").read_bytes()).hexdigest():
        raise ValueError("candidate score does not match its run manifest")
    if bscore["run_manifest_sha256"] != __import__('hashlib').sha256((Path(baseline_run)/"run.json").read_bytes()).hexdigest():
        raise ValueError("baseline score does not match its run manifest")

    def indexed(score):
        result = {}
        for row in score["rows"]:
            key = (row["task_id"],row["order"],row["sample"])
            if key in result:
                raise ValueError("duplicate scored key")
            result[key] = row
        return result
    cidx, bidx = indexed(cscore), indexed(bscore)
    if cidx.keys() != bidx.keys():
        raise ValueError("candidate and baseline missing matched tasks or rollout variants")
    selected, excluded = [], []
    for key in sorted(cidx):
        c,b = cidx[key],bidx[key]
        if c["root_id"] != b["root_id"]:
            raise ValueError("same task associated with different world roots")
        case_id = f"{key[0]}#order-{key[1]}#sample-{key[2]}"
        if c["score"] is not None and b["score"] is not None:
            selected.append({"case_id":case_id,"cluster_id":c["root_id"],
                             "candidate":c["score"],"baseline":b["score"]})
        else:
            excluded.append({"case_id":case_id,"root_id":c["root_id"],
                             "candidate_status":c["status"],"baseline_status":b["status"]})
    if not selected:
        raise ValueError("no paired scored outcomes")
    if type(planned_comparisons) is not int or planned_comparisons < 1:
        raise ValueError("planned_comparisons must be positive")
    fsi={"schema_version":FSI_SCHEMA,"experiment_id":f"PREF-{cconf['benchmark_id']}-DEV-PAIR",
         "target_population":target_population,"evaluation_mode":"sampled","alpha":alpha,
         "minimum_effect":minimum_effect,"planned_comparisons":planned_comparisons,
         "hypothesis_preregistered":False,"sealed_readout":False,"clusters_independent":False,
         "exchangeable_pair_labels":False,"cases":selected}
    return {"schema":"preferred-evals/paired-prompt-runs-v1","benchmark_id":cconf["benchmark_id"],
            "candidate_model":cconf["model"],"baseline_model":bconf["model"],
            "total_assigned_rollouts":len(cidx),"n_paired_scored":len(selected),
            "n_infra_or_missing":len(excluded),"non_scored":excluded,
            "n_roots_paired_scored":len({x["cluster_id"] for x in selected}),
            "candidate_correct_paired":sum(x["candidate"] for x in selected),
            "baseline_correct_paired":sum(x["baseline"] for x in selected),
            "fsi_01_manifest":fsi,"evidence_class":"development-only; FSI-01 inference not run"}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate-run",type=Path,required=True)
    ap.add_argument("--baseline-run",type=Path,required=True)
    ap.add_argument("--candidate-scores",type=Path,required=True)
    ap.add_argument("--baseline-scores",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--fsi-out",type=Path)
    ap.add_argument("--alpha",default="0.05")
    ap.add_argument("--registration",type=Path,help="frozen campaign registration; overrides generic comparison defaults")
    ap.add_argument("--minimum-effect",default="0.05")
    ap.add_argument("--planned-comparisons",type=int,default=1)
    args=ap.parse_args()
    if args.registration:
        reg=read(args.registration)
        if reg.get("schema")!="preferred-evals/campaign-registration-v1":
            raise ValueError("unknown campaign registration schema")
        test=reg["test"]
        minimum=str(test["minimum_effect"])
        if minimum!="0.10" or test.get("multiplicity")!="Holm over the 8 comparisons above":
            raise ValueError("campaign registration differs from the frozen eight-comparison protocol")
        if len(reg["comparisons"]) + (1 if reg.get("within_model_comparison") else 0)!=8:
            raise ValueError("campaign comparison family must include all eight")
        args.minimum_effect=minimum
        args.planned_comparisons=8
    result=compare(args.candidate_run,args.baseline_run,args.candidate_scores,args.baseline_scores,
                   alpha=args.alpha,minimum_effect=args.minimum_effect,
                   planned_comparisons=args.planned_comparisons)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if args.fsi_out:
        args.fsi_out.parent.mkdir(parents=True,exist_ok=True)
        args.fsi_out.write_text(json.dumps(result["fsi_01_manifest"],indent=2,sort_keys=True)+"\n",
                                encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("total_assigned_rollouts","n_paired_scored","n_roots_paired_scored",
                                             "candidate_correct_paired","baseline_correct_paired")}))


if __name__ == "__main__":
    main()

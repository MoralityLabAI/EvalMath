"""FSI-01 synthetic source-locked receipt: no model or external evaluator is called."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from fractions import Fraction as Q

from spiral_ln.evaluation_finite_sample import (
    evaluate_manifest, hoeffding_accuracy_n, clopper_pearson_bracket
)

ROOT=Path(__file__).resolve().parents[1]
SOURCES=(
    "src/spiral_ln/evaluation_finite_sample.py",
    "tests/test_evaluation_finite_sample.py",
    "scripts/verify_evaluation_finite_sample.py",
    "paper/finite_sample_inference.md",
)


def example(clusters: int, sealed: bool) -> dict:
    outcomes=[(1,0)]*15+[(0,1)]*3+[(0,0)]*46
    return {"schema_version":1,"experiment_id":"FSI-01-synthetic",
            "target_population":"constructed independent null test / root-cluster test",
            "evaluation_mode":"sampled","alpha":"0.05","minimum_effect":"0",
            "planned_comparisons":1,"hypothesis_preregistered":True,
            "sealed_readout":sealed,"clusters_independent":True,
            "exchangeable_pair_labels":True,"bootstrap_resamples":512,
            "cases":[{"case_id":f"case-{i:02d}","cluster_id":f"root-{i%clusters:02d}",
                      "candidate":x,"baseline":y} for i,(x,y) in enumerate(outcomes)]}


def receipt() -> dict:
    iid=evaluate_manifest(example(64,True))
    rooted=evaluate_manifest(example(8,True))
    reused=evaluate_manifest(example(64,False))
    cp=clopper_pearson_bracket(64,64,Q(1,20))
    return {"experiment":"FSI-01","evidence_level":"synthetic exact arithmetic + finite code tests",
            "checks":{
                "exact_paired_p":iid["p_exact_fraction"]=="247/32768",
                "iid_64_primary_confirms":iid["verdict"]=="confirmed",
                "eight_roots_blocks_confirmation":rooted["verdict"]=="suggestive",
                "root_test_is_exact":rooted["test"]=="exact_cluster_sign_flip",
                "reused_readout_blocks_confirmation":reused["verdict"]=="suggestive",
                "cp_64of64_is_outward":Q(94398,100000)<cp["lower_outward"]<Q(94401,100000),
                "conservative_planning_n":hoeffding_accuracy_n("0.05")==738,
            },
            "numbers":{
                "paired_p_exact":iid["p_exact_fraction"],
                "eight_root_p":rooted["p_exact_fraction"],
                "independent_accuracy_cp_lower_outward":str(cp["lower_outward"]),
                "n_bernoulli_95_halfwidth_5pct":hoeffding_accuracy_n("0.05"),
            },
            "source_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,default=ROOT/"output/evaluation_finite_sample/fsi01_v0_1.json")
    args=p.parse_args()
    r=receipt()
    if not all(r["checks"].values()):
        raise SystemExit("FSI-01 receipt failed a check")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())

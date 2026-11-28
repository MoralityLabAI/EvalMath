"""VAD-09D attribution: separate the value of planning depth, of probes, and of knowing the law (exact, H=3).

Adds the missing no-probe law-known planner and the planner/probe decomposition requested in review.
"""
import argparse
import json
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

from verify_vad_voi import ETA, MENU, Planner, build, prior_belief, transition

HERE = Path(__file__).resolve().parent


def law_known(acts, names, H, p_rev=F(1, 2)):
    res = {}
    for lw in (0, 1):
        sub = {k: (tuple(acts[k][0][2 * lw + mo] for mo in (0, 1)) + (F(0), F(0)),
                   tuple(tuple(o[2 * lw + mo] for mo in (0, 1)) + (F(0), F(0)) for o in acts[k][1])) for k in names}
        res[lw] = Planner(sub, ETA).value((1 - p_rev, p_rev, F(0), F(0)), H)
    return (res[0] + res[1]) / 2


def run(H=3):
    acts = build()
    b0 = prior_belief(F(1, 2), F(1, 2))
    rec = json.loads((HERE.parent / "output/verified_abstraction/vad_09d.json").read_text())["nominal"]
    nominal = {k: F(v) for k, v in rec.items() if k not in ("first_action_optimal", "first_action_optimal_no_probes", "qevals_optimal")}
    both = F(json.loads((HERE.parent / "output/verified_abstraction/vad_09d.json").read_text())["oracles"]["both_known"])
    law_noprobe = law_known(acts, MENU, H)
    law_probe = law_known(acts, tuple(acts), H)
    out = {
        "protocol": "VAD-09D-attribution", "evidence": "exact finite menu control; no learned model", "H": H,
        "law_known_planner_no_probes": str(law_noprobe), "law_known_planner_with_probes": str(law_probe),
        "decomposition_float": {
            "myopic_filter": float(nominal["myopic_no_probes"]),
            "planning_depth_gain_no_probes": float(nominal["finite_horizon_no_probes"] - nominal["myopic_no_probes"]),
            "probe_gain_given_planner": float(nominal["finite_horizon_with_probes"] - nominal["finite_horizon_no_probes"]),
            "law_knowledge_gain_no_probes": float(law_noprobe - nominal["finite_horizon_no_probes"]),
            "law_knowledge_gain_with_probes": float(law_probe - nominal["finite_horizon_with_probes"]),
            "mode_oracle_over_no_probe_planner": float(both - nominal["finite_horizon_no_probes"]),
            "mode_oracle_over_probe_planner": float(both - nominal["finite_horizon_with_probes"]),
        },
        "source_sha256": sha256((HERE / "verify_vad_voi_attr.py").read_bytes()).hexdigest(),
        "dependency_sha256": sha256((HERE / "verify_vad_voi.py").read_bytes()).hexdigest(),
    }
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    r = run()
    a.out.write_text(json.dumps(r, indent=2, sort_keys=True) + chr(10))
    print(json.dumps(r["decomposition_float"], indent=1))

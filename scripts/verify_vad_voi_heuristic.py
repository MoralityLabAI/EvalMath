"""VAD-09D: does a probe-then-myopic heuristic recover the probe-using optimum? (exact, H=3)

Suggested in review: if it does, the planning-overhead allowance of 09D is entirely the probe's value.
"""
import argparse
import json
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

from verify_vad_voi import ETA, MENU, Planner, build, prior_belief

HERE = Path(__file__).resolve().parent


def run(H=3):
    acts = build()
    b0 = prior_belief(F(1, 2), F(1, 2))
    pl = Planner(acts, ETA)
    myo = lambda b, h: max(MENU, key=lambda k: (pl.q(b, k, 1), -MENU.index(k)))
    probe_then_myopic = pl.run_policy(b0, H, lambda b, h: "probe_mode" if h == H else myo(b, h))
    law_probe_then_myopic = pl.run_policy(b0, H, lambda b, h: "probe_law" if h == H else myo(b, h))
    rec = json.loads((HERE.parent / "output/verified_abstraction/vad_09d.json").read_text())["nominal"]
    opt = F(rec["finite_horizon_with_probes"])
    return {"protocol": "VAD-09D-heuristic", "evidence": "exact finite menu control", "H": H,
            "probe_mode_then_myopic": str(probe_then_myopic), "probe_law_then_myopic": str(law_probe_then_myopic),
            "probe_using_optimum": str(opt), "probe_then_myopic_equals_optimum": probe_then_myopic == opt,
            "float": {"probe_mode_then_myopic": float(probe_then_myopic), "probe_law_then_myopic": float(law_probe_then_myopic), "optimum": float(opt)},
            "source_sha256": sha256((HERE / "verify_vad_voi_heuristic.py").read_bytes()).hexdigest(),
            "dependency_sha256": sha256((HERE / "verify_vad_voi.py").read_bytes()).hexdigest()}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    r = run()
    a.out.write_text(json.dumps(r, indent=2, sort_keys=True) + chr(10))
    print(json.dumps(r["float"]), r["probe_then_myopic_equals_optimum"])

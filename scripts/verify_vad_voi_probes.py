"""VAD-09D probe study: priced mode probe versus priced law probe (exact, H<=3)."""
import argparse
import json
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

from verify_vad_voi import ETA, MENU, Planner, build, prior_belief

HERE = Path(__file__).resolve().parent


def probe_study(horizons=(2,), costs=(F(1, 2), F(1), F(2), F(4), F(6)), restricted_h3=True):
    """Value of a priced mode probe versus a priced law probe, and the cost at which each stops paying."""
    rows = []
    for H in horizons:
        for c in costs:
            acts = build(probe_cost=c)
            res = {"H": H, "probe_cost": str(c)}
            for label, names in (("none", MENU), ("mode_only", MENU + ("probe_mode",)), ("law_only", MENU + ("probe_law",)),
                                 ("both", MENU + ("probe_mode", "probe_law"))):
                pl = Planner(acts, ETA, names=names)
                b0 = prior_belief(F(1, 2), F(1, 2))
                res[label] = str(pl.value(b0, H))
                res[label + "_first"] = pl.choose(b0, H)
            rows.append(res)
    if restricted_h3:
        small = ("cut2", "p0", "p50", "p100")
        for c in (F(1), F(3)):
            acts = build(probe_cost=c)
            res = {"H": 3, "probe_cost": str(c), "menu": list(small)}
            for label, extra in (("none", ()), ("mode_only", ("probe_mode",)), ("law_only", ("probe_law",)), ("both", ("probe_mode", "probe_law"))):
                pl = Planner(acts, ETA, names=small + extra)
                b0 = prior_belief(F(1, 2), F(1, 2))
                res[label] = str(pl.value(b0, 3))
                res[label + "_first"] = pl.choose(b0, 3)
            rows.append(res)
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    a_ = p.parse_args()
    rows = probe_study()
    rec = {"protocol": "VAD-09D-probes", "evidence": "exact finite menu control; no learned model",
           "source_sha256": sha256((HERE / "verify_vad_voi_probes.py").read_bytes()).hexdigest(),
           "dependency_sha256": sha256((HERE / "verify_vad_voi.py").read_bytes()).hexdigest(), "rows": rows}
    a_.out.write_text(json.dumps(rec, indent=2, sort_keys=True) + chr(10))
    for r in rows:
        print({k: (str(float(F(v)))[:8] if k in ("none", "mode_only", "law_only", "both") else v) for k, v in r.items()})

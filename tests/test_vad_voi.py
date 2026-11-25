"""VAD-09D: receipt digests, ordering of information structures, and an independent horizon-1/2 check."""
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
import verify_vad_voi as v


def test_receipt_digest_and_ordering():
    rec = json.loads((root / "output/verified_abstraction/vad_09d.json").read_text())
    assert hashlib.sha256((root / "scripts/verify_vad_voi.py").read_bytes()).hexdigest() == rec["source_sha256"]["verify_vad_voi.py"]
    n = {k: F(x) for k, x in rec["nominal"].items() if k not in ("first_action_optimal", "first_action_optimal_no_probes", "qevals_optimal")}
    assert n["blind_fixed_action"] <= n["myopic_no_probes"] <= n["finite_horizon_no_probes"] <= n["finite_horizon_with_probes"]
    assert n["receding_h2"] <= n["finite_horizon_with_probes"]
    assert F(rec["oracles"]["both_known"]) >= n["finite_horizon_with_probes"]
    assert rec["oracles"]["both_known"] == rec["oracles"]["mode_known_law_unknown"]


def test_one_family_value_is_best_expected_immediate_action():
    acts = v.build()
    b0 = v.prior_belief(F(1, 2), F(1, 2))
    pl = v.Planner(acts)
    best = max(sum(b * x for b, x in zip(b0, acts[k][0])) for k in acts)
    assert pl.value(b0, 1) == best
    # two families, brute force over actions and merged outcomes with the transition
    pl2 = v.Planner(acts, names=v.MENU)
    val = pl2.value(b0, 2)
    manual = F(0)
    top = None
    for k in v.MENU:
        r, outs = acts[k]
        q = sum(b * x for b, x in zip(b0, r))
        for o in outs:
            z = sum(b * x for b, x in zip(b0, o))
            if z:
                post = v.transition(tuple(b * x / z for b, x in zip(b0, o)), v.ETA)
                q += z * max(sum(b * x for b, x in zip(post, acts[k2][0])) for k2 in v.MENU)
        top = q if top is None or q > top else top
    assert val == top

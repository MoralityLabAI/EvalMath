"""VAD-10: exact research-agenda oracle, greedy-optimality class, counterexamples, random sweeps."""
import argparse
import json
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

import vad_agenda as g
import vad_agenda_naive as naive

HERE = Path(__file__).resolve().parent
POLICIES = {"direct": g.policy_direct, "greedy0": g.policy_lookahead(0),
            "greedy1": g.policy_lookahead(1), "greedy2": g.policy_lookahead(2),
            "optimal": g.policy_lookahead(None), "random": g.policy_random}


def table(inst):
    o, v = g.solve(inst)
    row = {"stop": str(o.terminal(o.start, o.i.prior)), "optimal_value": str(v)}
    for name, pol in POLICIES.items():
        row[name] = str(g.evaluate(inst, o, pol))
    assert F(row["optimal"]) == v, "forward evaluation of the optimal policy differs from the Bellman value"
    return o, v, row


def strategic_scan():
    out = []
    for num in range(0, 41):
        p = F(num, 40)
        o, v, row = table(g.strategic_intermediate(p_direct=p))
        out.append(dict(p_direct=str(p), optimal=row["optimal"], direct=row["direct"], greedy0=row["greedy0"],
                        first=str(o.best_action(o.start, o.i.prior, o.i.budget)[0])))
    cross = next((r["p_direct"] for i, r in enumerate(out) if all(F(x["direct"]) == F(x["optimal"]) for x in out[i:])), None)
    return out, cross


def mislead_scan():
    rows = []
    assumed, template = g.misleading_signal()
    oa = g.Oracle(assumed)
    ign = g.Instance(**{**assumed.__dict__, "experiments": ()})
    oi = g.Oracle(ign)
    for num in range(0, 21):
        r = F(num, 20)  # true P(hi | route A exists); P(hi | route B exists) = 1 - r
        true = g.Instance(**{**template.__dict__, "experiments": (g.Experiment(1, ((r, 1 - r), (1 - r, r))),)})
        ot, vt = g.solve(true)
        rows.append(dict(true_reliability=str(r),
                         trusting=str(g.evaluate(true, oa, POLICIES["optimal"])),
                         ignoring=str(g.evaluate(true, oi, POLICIES["optimal"])),
                         true_optimal=str(vt),
                         assumed_claim=str(oa.value(oa.start, assumed.prior, assumed.budget))))
    return rows


def sweep(kind, seeds, naive_every=3):
    names = ["direct", "greedy0", "greedy1", "greedy2", "random"]
    agg = {n: dict(optimal=0, regret=F(0), max_regret=F(0)) for n in names}
    nodes = {"greedy0": 0, "greedy1": 0, "greedy2": 0, "optimal": 0}
    qev = {"optimal": 0, "greedy0": 0, "greedy1": 0, "greedy2": 0}
    checked = 0
    for s in seeds:
        inst = g.correlated_instance(s) if kind == "correlated" else g.random_instance(s, kind)
        o, v = g.solve(inst)
        nodes["optimal"] += o.nodes
        qev["optimal"] += o.qevals
        for n in names:
            val = g.evaluate(inst, o, POLICIES[n])
            assert val <= v
            a = agg[n]
            a["optimal"] += val == v
            a["regret"] += v - val
            a["max_regret"] = max(a["max_regret"], v - val)
        for k in (0, 1, 2):
            o2 = g.Oracle(inst)
            g.evaluate(inst, o2, g.policy_lookahead(k))
            nodes["greedy%d" % k] += o2.nodes
            qev["greedy%d" % k] += o2.qevals
        if inst.budget <= 3 and not inst.experiments and s % naive_every == 0:
            assert naive.opt(inst) == v
            checked += 1
    n = len(seeds)
    return {"instances": n, "naive_checks": checked,
            "policies": {k: dict(optimal_fraction=str(F(a["optimal"], n)), mean_regret=str(a["regret"] / n),
                                 max_regret=str(a["max_regret"])) for k, a in agg.items()},
            "mean_nodes": {k: str(F(x, n)) for k, x in nodes.items()},
            "mean_qevals_one_episode": {k: str(F(x, n)) for k, x in qev.items()}}


def run(scale=1):
    r = {"protocol": "VAD-10", "evidence": "exact finite oracle; seeded finite sweeps; no learned model",
         "source_sha256": {n: sha256((HERE / n).read_bytes()).hexdigest()
                           for n in ("vad_agenda.py", "vad_agenda_naive.py", "verify_vad_agenda.py")}}
    cases = {}
    for name, inst in (("strategic", g.strategic_intermediate()), ("complementary", g.complementary()),
                       ("knapsack", g.knapsack()), ("failed_attempt", g.failed_attempt_information())):
        cases[name] = table(inst)[2]
    for k in range(2, 7):
        cases["chain%d" % k] = table(g.chain(k))[2]
    r["cases"] = cases
    o = g.Oracle(g.strategic_intermediate())
    r["strategic_decomposition"] = {
        str(a): {k: str(x) for k, x in o.decompose(o.start, o.i.prior, o.i.budget, a).items()}
        for a in o.actions(o.start, o.i.prior, o.i.budget) if a != g.STOP}
    o = g.Oracle(g.failed_attempt_information())
    r["failed_attempt_decomposition"] = {k: str(x) for k, x in o.decompose(o.start, o.i.prior, 2, ("att", 0)).items()}
    need = {}
    for k in range(2, 7):
        inst = g.chain(k)
        o, v = g.solve(inst)
        need[k] = next(j for j in range(0, k + 1) if g.evaluate(inst, o, g.policy_lookahead(j)) == v)
    r["chain_lookahead_needed"] = need
    r["strategic_scan"], r["direct_equals_optimal_from_p"] = strategic_scan()
    r["misleading_scan"] = mislead_scan()
    r["trust_beats_ignoring_from_reliability"] = next(x["true_reliability"] for i, x in enumerate(r["misleading_scan"]) if all(F(y["trusting"]) > F(y["ignoring"]) for y in r["misleading_scan"][i:]))
    r["sweeps"] = {k: sweep(k, list(range(70000, 70000 + n)))
                   for k, n in (("modular", 150 // scale), ("layered", 150 // scale), ("correlated", 60 // scale))}
    return r


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    res = run()
    a.out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("cases", "chain_lookahead_needed", "direct_equals_optimal_from_p")}, indent=1))
    print(json.dumps(res["sweeps"], indent=1))

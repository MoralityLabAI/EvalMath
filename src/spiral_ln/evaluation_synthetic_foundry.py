"""Exact synthetic fixtures for the EvalMath Synthetic Foundry (ESF-01).

Original operator-authored implementation; no teacher output is an input.
Gold is recomputed from public finite problem specifications. This is a
development data generator, not a statistical confirmation or rights grant.
"""
from __future__ import annotations

import hashlib
import itertools as it
import json
import math
import random
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path

SCHEMA = "evalmath.esf01.v1"
FAMILIES = {
    "judge": ("paper/rl_training_signal_limits.md", "conditional judge error"),
    "cpf": ("paper/correlated_proof_fidelity.md", "joint false authorization"),
    "audit": ("paper/noisy_authorization_audit_budget.md", "binary audit value"),
    "disclosure": ("paper/adaptive_disclosure.md", "one-hot interval identification"),
    "selection": ("paper/selection_risk_continuations.md", "adaptive false authorization"),
    "covert": ("paper/covert_feedback_risk.md", "bounded covert feedback"),
    "capacity": ("paper/leak_capacity.md", "finite margin collisions"),
    "patch": ("paper/evaluation_feedback_lattice.md", "expected patches to one hit"),
    "reuse": ("paper/evaluation_feedback_multigen.md", "iid running maximum"),
    "bpd": ("paper/bpd_interventional_separation.md", "routed mechanism separation"),
    "paired": ("paper/nw01_recurrent_paired_information.md", "paired-world accuracy and Brier"),
    "revocation": ("paper/dynamic_filtration_validity.md", "provenance-dependent terminal decisions"),
}
PROFILES = ("baseline", "boundary", "structural_shift")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, (tuple, list)):
        return [serial(x) for x in value]
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    return value


def make_case(family, rng, profile="baseline"):
    """Bounded generator; structural_shift changes cardinalities, not just wording."""
    if family not in FAMILIES or profile not in PROFILES:
        raise ValueError("unknown family/profile")
    edge = profile == "boundary"
    shift = profile == "structural_shift"
    d = rng.randint(11, 47) if shift else rng.randint(7, 29)
    p = lambda: F(rng.randint(0 if edge else 1, d if edge else d - 1), d)
    if family == "judge":
        # Four cells: true-correct/judge-correct, true-correct/judge-wrong,
        # true-wrong/judge-correct, true-wrong/judge-wrong.
        w = [rng.randint(0 if edge else 1, d) for _ in range(4)]
        if not w[2] + w[3]:
            w[2] = 1
        return {"joint_counts": w}
    if family == "cpf":
        a, b, c = p(), p(), p()
        lo, hi = max(F(0), a+b-1), min(a, b)
        r = lo if edge and rng.randrange(2) else hi if edge else lo+(hi-lo)*p()
        return serial({"a": a, "b": b, "r": r, "audit_pass_given_both": c})
    if family == "audit":
        return serial({"p": p(), "sensitivity": p(), "false_positive": p()})
    if family == "disclosure":
        return {"n": rng.randint(8, 18) if shift else rng.randint(2, 8),
                "budget": rng.randint(0 if edge else 1, 4 if shift else 3)}
    if family in {"selection", "covert"}:
        n = rng.randint(5, 7) if shift else rng.randint(3, 5)
        m = rng.randint(3, 5)
        return {"weights": [rng.randint(1, d) for _ in range(n)],
                "events": [[bool(rng.randrange(2)) for _ in range(n)] for _ in range(m)],
                "transcript": [rng.randrange(3 if shift else 2) for _ in range(n)],
                "messages": rng.randint(1, min(m, 3)) if family == "covert" else 1}
    if family == "capacity":
        grid = list(it.product(range(3 if shift else 2), range(2)))
        support = sorted(rng.sample(grid, rng.randint(2, len(grid))))
        return {"support": [list(x) for x in support], "faces": [[0], [1]],
                "sizes": [rng.randint(1, 3 if shift else 2) for _ in support]}
    if family == "patch":
        ncat = rng.randint(3, 4) if shift else rng.randint(1, 3)
        cats = [(n := rng.randint(1, 7), rng.randint(0, n)) for _ in range(ncat)]
        if not any(k for _, k in cats):
            cats[0] = (cats[0][0], 1)
        return {"categories": serial(cats)}
    if family == "reuse":
        return serial({"n": rng.randint(6, 12) if shift else rng.randint(2, 7),
                       "p": p(), "candidates": rng.randint(1, 6), "generations": rng.randint(1, 5)})
    if family == "bpd":
        n = rng.randint(4, 5) if shift else rng.randint(2, 4)
        rows = [{"name": f"q{i}", "outcomes": [rng.randrange(3) for _ in range(n)],
                 "cost": rng.randint(1, 4), "routed": bool(rng.randrange(3))}
                for i in range(rng.randint(3, 7))]
        return {"hypotheses": n, "probes": rows}
    if family == "paired":
        return serial({"p_hidden_prediction": p(), "n_pairs": rng.randint(1, d),
                       "authenticated_residual_available": bool(rng.randrange(2))})
    # Two provenance-tagged histories with equal bit marginal. Later continuation
    # reveals which of two bits is requested. A memory is a fixed partition.
    n = 4
    return serial({"weights": [rng.randint(1, d) for _ in range(n)],
                   "bits": list(it.product(range(2), repeat=2)),
                   "continuation_weights": [rng.randint(1, d) for _ in range(3)],
                   "states": rng.randint(1, 4)})


def _groups(labels):
    cells = defaultdict(list)
    for i, label in enumerate(labels):
        cells[label].append(i)
    return tuple(tuple(v) for v in cells.values())


def solve(family, x):
    """Reference solver plus an independent native/exhaustive check where applicable."""
    if family == "judge":
        a, b, c, d = x["joint_counts"]
        n = a+b+c+d
        acc, err, shared = F(a+b,n), F(b+d,n), F(d,c+d)
        observed = F(a+d,n)
        assert observed == acc-err+2*(1-acc)*shared
        return serial({"true_accuracy": acc, "judge_error": err,
                       "conditional_error_on_wrong": shared, "observed_accuracy": observed,
                       "ceiling_reached": observed >= 1-err})
    if family == "cpf":
        from spiral_ln.evaluation_cpf import bounds, coupling, residual
        a,b,r,c = map(F, (x["a"],x["b"],x["r"],x["audit_pass_given_both"]))
        lo,hi = bounds(a,b)
        cells = coupling(a,b,r)
        assert cells == (r,a-r,b-r,1-a-b+r) and min(cells) >= 0 and sum(cells)==1
        assert residual(r,c)==r*c
        return serial({"lower":lo,"upper":hi,"cells":cells,"residual":r*c})
    if family == "audit":
        p,t,f = map(F,(x["p"],x["sensitivity"],x["false_positive"]))
        masses=((p*(1-t),(1-p)*(1-f)),(p*t,(1-p)*f))
        r0=min(p,1-p)
        r1=sum(min(row) for row in masses)
        brute=min(sum(masses[y][a] for y,a in enumerate(rule)) for rule in it.product(range(2),repeat=2))
        assert r1==brute
        return serial({"before_error":r0,"after_error":r1,"audit_value":r0-r1})
    if family == "disclosure":
        from spiral_ln.evaluation_adaptive_disclosure import one_hot_interval_law
        n,b=x["n"],x["budget"]
        counts=one_hot_interval_law(n,b)
        # Enumerate adaptive splits using intervals, independent of the closed law.
        queries=tuple(sum(1<<i for i in range(a,z)) for a in range(n) for z in range(a+1,n+1))
        @lru_cache(None)
        def dp(mask,k):
            if not mask:return 0
            if not k:return 1
            return max([1]+[dp(mask&q,k-1)+dp(mask&~q,k-1)
                             for q in queries if mask&q and mask&~q])
        assert dp((1<<n)-1,b)==counts["adaptive"]
        return serial({**counts,"adaptive_success":F(counts["adaptive"],n),
                       "fixed_success":F(counts["fixed"],n)})
    if family in {"selection","covert"}:
        from spiral_ln.evaluation_selection_risk import NullModel, risk_for_fibres
        from spiral_ln.evaluation_covert_feedback import covert_risk
        w=x["weights"]; ev=x["events"]; groups=_groups(x["transcript"]); m=x["messages"]
        model=NullModel(tuple(w),tuple(map(tuple,ev)),(tuple(x["transcript"]),))
        base=risk_for_fibres(model,groups)
        cover=covert_risk(model,m,groups)["risk"]
        # Independent enumeration of terminal label maps (small finite worlds).
        def value(g,k):
            return max(sum(max(sum(w[i] for i,l in zip(g,lab) if l==j and e[i])
                               for e in ev) for j in range(k))
                       for lab in it.product(range(k),repeat=len(g)))
        assert base==F(sum(value(g,1) for g in groups),sum(w))
        assert cover==F(sum(value(g,m) for g in groups),sum(w))
        return serial({"public_risk":base,"risk_with_messages":cover,
                       "full_information_risk":F(sum(w[i] for i in range(len(w))
                                                       if any(e[i] for e in ev)),sum(w))})
    if family == "capacity":
        from spiral_ln.evaluation_leak_capacity import collision_counts_direct, collision_counts_lattice
        s=tuple(map(tuple,x["support"])); f=tuple(map(tuple,x["faces"])); cap=tuple(x["sizes"])
        a=collision_counts_direct(s,f,cap); b=collision_counts_lattice(s,f,cap)
        assert a==b
        joint,separate=a
        return serial({"joint_pairs":joint,"margin_pairs":separate,
                       "collision_exists":separate>joint,"collision_ratio":F(separate,joint)})
    if family == "patch":
        cats=tuple(map(tuple,x["categories"]))
        @lru_cache(None)
        def dp(state):
            vals=[]
            for i,(n,h) in enumerate(state):
                if not n or not h:continue
                if h==n:vals.append(F(1));continue
                child=state[:i]+((n-1,h),)+state[i+1:]
                vals.append(1+F(n-h,n)*dp(child))
            return min(vals)
        closed=min(F(n+1,h+1) for n,h in cats if h)
        assert dp(cats)==closed
        return serial({"optimal_expected_patches":closed,
                       "optimal_first_categories":[i for i,(n,h) in enumerate(cats)
                                                   if h and F(n+1,h+1)==closed]})
    if family == "reuse":
        n=x["n"]; p=F(x["p"]); draws=x["candidates"]*x["generations"]+1
        probs=[math.comb(n,k)*p**k*(1-p)**(n-k) for k in range(n+1)]
        cdf=list(it.accumulate(probs))
        pmf=[v**draws-(cdf[i-1]**draws if i else 0) for i,v in enumerate(cdf)]
        val=sum(F(i,n)*v for i,v in enumerate(pmf))
        assert sum(pmf)==1 and val==sum((1-cdf[i]**draws)/n for i in range(n))
        return serial({"draws":draws,"expected_reported_accuracy":val,"phantom_gain":val-p})
    if family == "bpd":
        from spiral_ln.evaluation_bpd import Probe, minimum_test_collection, exhaustive_batch, quotient
        probes=tuple(Probe(r["name"],tuple(r["outcomes"]),r["cost"],r["routed"]) for r in x["probes"])
        a=minimum_test_collection(probes); b=exhaustive_batch(probes)
        assert (a is None)==(b is None) and (a is None or a[0]==b[0])
        return serial({"minimum_cost":None if a is None else a[0],
                       "equivalence_classes":quotient(probes),"identifiable":a is not None})
    if family == "paired":
        p=F(x["p_hidden_prediction"])
        brier=(p*p+(1-p)**2)/2
        assert brier==F(1,4)+(p-F(1,2))**2
        return serial({"public_accuracy":F(1,2),"public_brier":brier,
                       "accuracy_with_observation":F(1) if x["authenticated_residual_available"] else F(1,2)})
    if family == "revocation":
        # Exact fixed-memory capacity oracle in a declared 4-history construction.
        w=x["weights"]; bits=x["bits"]; cw=x["continuation_weights"]; k=x["states"]
        targets=[(a^b,b,a) for a,b in bits]
        def mass(labels):
            return sum(cw[j]*max(sum(w[i] for i in g if targets[i][j]==t) for t in (0,1))
                       for g in _groups(labels) for j in range(3))
        best=max(mass(labels) for labels in it.product(range(k),repeat=len(w)))
        total=sum(w)*sum(cw)
        return serial({"minimum_regret":F(total-best,total),"optimal_success":F(best,total)})
    raise ValueError("unknown family")


def task(family, x, profile):
    source, title=FAMILIES[family]
    prompt=f"EvalMath {title}. Use exact rational arithmetic. Return the requested quantities as JSON. "
    prompts={
        "judge":"From the four joint counts (correct/judge-correct, correct/judge-wrong, wrong/judge-correct, wrong/judge-wrong), compute true accuracy, judge error, conditional error on wrong, observed accuracy and whether it reaches the judge ceiling.",
        "cpf":"Compute Frechet lower/upper bounds for the intersection, four atom masses in order both/A only/B only/neither and residual false authorization after the conditional audit.",
        "audit":"Compute Bayes error before and after the audit and its value under symmetric loss.",
        "disclosure":"Find the optimal number of identifiable locations and success rates with fixed and adaptive interval queries for a uniform one-hot location.",
        "selection":"Compute optimal public post-selection risk and full-information risk. There is one covert symbol, so risk with messages equals public risk.",
        "covert":"Compute public risk, maximum risk with the declared number of hidden symbols per public fibre, and full-information risk.",
        "capacity":"Count ordered binary-record pairs colliding in exact cell counts versus observed margins, and state whether distinct feasible cell-count vectors can collide and the ratio.",
        "patch":"Find the minimum expected patches to one hit, with uniform sampling without replacement within a selected category, and all optimal first categories.",
        "reuse":"Under independent equal-quality binomial candidates and reuse of one fixed eval, compute total draws including the initial record, expected reported maximum accuracy and phantom gain.",
        "bpd":"Find whether routed probes separate all mechanisms, minimum nonadaptive separating cost (null if impossible), and observational equivalence classes. Unrouted probes are missing.",
        "paired":"Compute paired public-only accuracy, Brier score for the given prediction and accuracy with the authenticated observation (or public-only if unavailable).",
        "revocation":"The history bits have the supplied masses. Continuation requests XOR, bit 2 or bit 1 with weights in that order; memory is fixed before the request. Enumerate the best partition with at most the given states; return minimum regret and optimal success.",
    }
    y=solve(family,x)
    key=digest({"family":family,"input":x})
    return ({"schema":SCHEMA,"task_id":key,"family":family,"profile":profile,
             "source":source,"prompt":prompt+prompts[family],"input":x,
             "requested_fields":sorted(y)},
            {"task_id":key,"answer":y,"evidence":"exact_finite_fixture"})


def generate(families, profile, count, seed, split):
    """Split by exact problem identity; no claim of family-disjoint confirmation."""
    if count<1 or count>20000 or split not in {"discovery","development"}:
        raise ValueError("bounded count and public development split required")
    rng=random.Random(seed); public=[]; gold=[]; seen=set()
    for family in families:
        accepted=0
        for _ in range(max(1000,count*100)):
            x=make_case(family,rng,profile)
            key=digest({"family":family,"input":x})
            assigned="development" if int(key[:8],16)%5==0 else "discovery"
            if assigned!=split or key in seen:continue
            a,b=task(family,x,profile)
            seen.add(key); public.append(a); gold.append(b); accepted+=1
            if accepted>=count:break
        if not accepted:
            raise ValueError(f"no distinct {family} fixtures in split")
    return public,gold


def write_pack(out, public, gold, *, seed, split, profile):
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    def write(name,rows):
        p=out/name
        with p.open("x",encoding="utf-8") as h:
            for row in rows:h.write(canonical(row)+"\n")
        return hashlib.sha256(p.read_bytes()).hexdigest()
    p=write("tasks.jsonl",public); g=write("evaluator_gold.jsonl",gold)
    meta={"schema":SCHEMA,"split":split,"profile":profile,"seed":seed,
          "actual_count":len(public),"family_counts":dict(Counter(r["family"] for r in public)),
          "tasks_sha256":p,"gold_sha256":g,"teacher_data_included":False,
          "evidence":"exact finite development fixtures; source-family and rights review still required",
          "training_admission":"pending independent corpus review",
          "generator_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/"manifest.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return meta

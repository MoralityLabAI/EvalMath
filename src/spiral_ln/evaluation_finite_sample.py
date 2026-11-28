"""Small-n binary-evaluation evidence gate (FSI-01).

Exact integer/rational binomial and paired tests, a rational-outward bracket
for Clopper--Pearson, and explicitly approximate cluster bootstrap intervals.
The gate can check the *declared* experimental provenance but cannot establish
independence, a representative sample, or the truth of an exhaustive audit.

Input is a JSON manifest: see paper/finite_sample_inference.md.
No model is evaluated by this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
from statistics import NormalDist
from typing import Mapping, Sequence


def _fraction(v: object, field: str, *, minimum: Q = Q(0), maximum: Q = Q(1)) -> Q:
    if isinstance(v, bool) or not isinstance(v, (str, int, Q)):
        raise ValueError(f"{field} must be a decimal string, int or Fraction")
    try:
        q = Q(v)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{field} must be a rational number") from exc
    if not minimum <= q <= maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return q


def _positive_int(value: object, field: str, *, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{field} must be an integer >= {minimum}")
    return value


def _require_bool(data: Mapping, key: str) -> bool:
    if type(data.get(key)) is not bool:
        raise ValueError(f"{key} must be an explicitly declared boolean")
    return data[key]


def _require_str(data: Mapping, key: str) -> str:
    v = data.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{key} requires a non-empty string")
    return v


def binomial_two_sided(k: int, n: int) -> Q:
    """Exact equal-tail conditional test for k successes in n fair flips.

    Applies to McNemar discordances when each pair is independent, or to
    other fair binary sign experiments satisfying that null.
    """
    _positive_int(n, "n", minimum=0)
    if type(k) is not int or k < 0 or k > n:
        raise ValueError("k must lie in [0,n]")
    if n == 0:
        return Q(1)
    num = 2 * sum(math.comb(n, j) for j in range(min(k, n - k) + 1))
    return Q(min(num, 2**n), 2**n)


def exact_mcnemar(candidate: Sequence[int], baseline: Sequence[int]) -> dict[str, object]:
    if len(candidate) != len(baseline) or len(candidate) == 0:
        raise ValueError("paired arrays must have the same positive length")
    if any(type(x) is not int or x not in (0, 1) for x in (*candidate, *baseline)):
        raise ValueError("paired outcomes must be binary integers")
    wins = sum(x == 1 and y == 0 for x, y in zip(candidate, baseline))
    losses = sum(x == 0 and y == 1 for x, y in zip(candidate, baseline))
    p = binomial_two_sided(wins, wins + losses)
    return {"candidate_only": wins, "baseline_only": losses, "ties": len(candidate) - wins - losses,
            "discordant": wins + losses, "p_exact": p}


def _binomial_cdf(n: int, k: int, p: Q) -> Q:
    if k < 0:
        return Q(0)
    if k >= n:
        return Q(1)
    return sum((Q(math.comb(n, j)) * p**j * (1-p)**(n-j) for j in range(k+1)), Q(0))


def clopper_pearson_bracket(k: int, n: int, alpha: Q, bits: int = 18) -> dict[str, object]:
    """Outward rational enclosure for exact two-sided CP interval endpoints.

    Returned lower is <= the true lower and upper >= the true upper.
    Endpoints themselves can be irrational. The result is valid on iid
    Bernoulli draws; clustering invalidates nominal case-level coverage.
    """
    _positive_int(n, "n")
    if type(k) is not int or not 0 <= k <= n:
        raise ValueError("k must be in [0,n]")
    if not Q(0) < alpha < Q(1):
        raise ValueError("alpha must lie strictly inside (0,1)")
    _positive_int(bits, "bits")
    h = alpha/2
    if k == 0:
        low_bound = Q(0)
    else:
        a,b = Q(0), Q(1)
        for _ in range(bits):
            m = (a+b)/2
            if 1 - _binomial_cdf(n, k-1, m) < h:
                a=m
            else:
                b=m
        low_bound=a
    if k == n:
        high_bound=Q(1)
    else:
        a,b=Q(0),Q(1)
        for _ in range(bits):
            m=(a+b)/2
            if _binomial_cdf(n, k, m) >= h:
                a=m
            else:
                b=m
        high_bound=b
    return {"lower_outward":low_bound,"upper_outward":high_bound,
            "resolution":Q(1,2**bits),"alpha":alpha}


def holm_adjust(p_values: Sequence[Q]) -> list[Q]:
    """Exact familywise Holm step-down adjustment, preserving input order."""
    if not p_values:
        raise ValueError("at least one p-value is required")
    vals = [_fraction(v, "p-value") for v in p_values]
    order = sorted(range(len(vals)), key=lambda i:(vals[i],i))
    out = [Q(0)] * len(vals)
    running = Q(0)
    for j,i in enumerate(order):
        running = min(Q(1), max(running, (len(vals)-j)*vals[i]))
        out[i]=running
    return out


def signflip_cluster_p(effects: Sequence[Q], *, seed: int = 20261117,
                       simulations: int = 20000, exact_limit: int = 18) -> tuple[Q, str]:
    """Two-sided cluster sign-flip p under an independent symmetric sign null.

    For <= exact_limit clusters, enumerate all sign vectors exactly.
    Otherwise Monte Carlo sign flipping with +1 correction; numerator is
    random, and the p-value is labelled Monte Carlo rather than exact.
    """
    if not effects:
        raise ValueError("at least one independent cluster is required")
    if any(not isinstance(x, Q) for x in effects):
        raise ValueError("cluster effects must be rational")
    n = len(effects)
    obs = abs(sum(effects))
    if n <= exact_limit:
        extreme = sum(abs(sum(s * x for s,x in zip(signs,effects))) >= obs
                      for signs in product((-1,1), repeat=n))
        return Q(extreme,2**n), "exact_cluster_sign_flip"
    _positive_int(simulations, "simulations")
    rng=random.Random(seed)
    extreme=0
    for _ in range(simulations):
        value = sum(x if rng.getrandbits(1) else -x for x in effects)
        extreme += abs(value) >= obs
    return Q(extreme+1,simulations+1), "monte_carlo_cluster_sign_flip"


def _quantile_sorted(v: Sequence[float], q: float) -> float:
    pos = q*(len(v)-1)
    i=int(pos)
    return v[i] + (v[min(i+1,len(v)-1)]-v[i])*(pos-i)


def cluster_bootstrap_ci(effects: Sequence[Q], alpha: Q, *,
                         seed: int = 20261117, resamples: int = 4096) -> tuple[float,float] | None:
    """Approximate percentile interval over independent clusters, equal macro weight.

    This is a descriptive interval; coverage can be poor with very few
    clusters and does not substitute for the cluster sign-flip test.
    """
    if len(effects) < 2:
        return None
    _positive_int(resamples,"resamples")
    rng=random.Random(seed)
    values=[float(x) for x in effects]
    g=len(values)
    means=sorted(sum(values[rng.randrange(g)] for _ in range(g))/g
                 for _ in range(resamples))
    a=float(alpha)/2
    return (_quantile_sorted(means,a),_quantile_sorted(means,1-a))


def hoeffding_accuracy_n(half_width: object, alpha: object = "0.05") -> int:
    """Conservative iid Bernoulli sample size for P(|p_hat-p|>h) <= alpha."""
    h = _fraction(half_width,"half_width")
    a = _fraction(alpha,"alpha")
    if h <= 0 or a <= 0 or a >= 1:
        raise ValueError("half_width and alpha must be strictly positive; alpha < 1")
    return math.ceil(math.log(2/float(a)) / (2*float(h)**2))


def _check_cases(raw: object) -> tuple[list[int],list[int],dict[str,list[Q]]]:
    if not isinstance(raw,list) or not raw:
        raise ValueError("cases must be a nonempty array")
    ids=set()
    cand,base,groups=[],[],{}
    for row in raw:
        if not isinstance(row,dict):
            raise ValueError("each case must be a JSON object")
        cid=_require_str(row,"case_id")
        cluster=_require_str(row,"cluster_id")
        if cid in ids:
            raise ValueError("duplicate case_id: "+cid)
        ids.add(cid)
        a,b=row.get("candidate"),row.get("baseline")
        if type(a) is not int or a not in (0,1) or type(b) is not int or b not in (0,1):
            raise ValueError("candidate and baseline must be 0/1 integers")
        cand.append(a); base.append(b)
        groups.setdefault(cluster,[]).append(Q(a-b))
    return cand,base,groups


def evaluate_manifest(manifest: Mapping[str,object]) -> dict[str,object]:
    """Compute a scoped evidence verdict from a frozen paired-binary manifest.

    Confirmation requires explicit provenance claims. These are attestations,
    not machine-verified independence or proof of domain coverage.
    """
    if not isinstance(manifest, Mapping):
        raise ValueError("manifest must be a JSON object")
    if manifest.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    name=_require_str(manifest,"experiment_id")
    target=_require_str(manifest,"target_population")
    mode=manifest.get("evaluation_mode")
    if mode not in ("sampled","exhaustive"):
        raise ValueError("evaluation_mode must be sampled or exhaustive")
    a=_fraction(manifest.get("alpha"),"alpha")
    if not 0 < a < 1:
        raise ValueError("alpha must be in (0,1)")
    floor=_fraction(manifest.get("minimum_effect"),"minimum_effect")
    comparisons=_positive_int(manifest.get("planned_comparisons"),"planned_comparisons")
    min_units=_positive_int(manifest.get("min_independent_clusters",20),"min_independent_clusters", minimum=2)
    seed=_positive_int(manifest.get("resample_seed",20261117),"resample_seed",minimum=0)
    boot=_positive_int(manifest.get("bootstrap_resamples",4096),"bootstrap_resamples")
    mc=_positive_int(manifest.get("signflip_simulations",20000),"signflip_simulations")
    cand,base,clusters=_check_cases(manifest.get("cases"))
    n=len(cand); g=len(clusters)
    flat=exact_mcnemar(cand,base)
    effects=[sum(v,Q(0))/len(v) for v in clusters.values()]
    point=sum(effects,Q(0))/g
    diff=Q(sum(cand)-sum(base),n)
    out={"schema_version":1,"experiment_id":name,"target_population":target,
         "evaluation_mode":mode,"n_cases":n,"n_clusters":g,
         "candidate_correct":sum(cand),"baseline_correct":sum(base),
         "candidate_accuracy":float(Q(sum(cand),n)),"baseline_accuracy":float(Q(sum(base),n)),
         "case_weighted_effect":float(diff),"cluster_macro_effect":float(point),
         "case_effect_exact":str(diff),"cluster_effect_exact":str(point),
         "candidate_only":flat["candidate_only"],"baseline_only":flat["baseline_only"],
         "discordant":flat["discordant"],"ties":flat["ties"],
         "minimum_effect":float(floor),"alpha":float(a),"planned_comparisons":comparisons}
    if mode == "exhaustive":
        domain_size=_positive_int(manifest.get("declared_domain_size"),"declared_domain_size")
        sha=_require_str(manifest,"coverage_audit_sha256")
        if not re.fullmatch("[0-9a-f]{64}",sha):
            raise ValueError("coverage_audit_sha256 must be a lowercase SHA-256")
        if domain_size != n:
            raise ValueError("declared_domain_size differs from number of unique cases")
        out.update({"verdict":"exact_finite_result","declared_domain_size":domain_size,
                    "coverage_audit_sha256":sha,
                    "inference_note":"Exact counts only for the declared audited finite domain; coverage audit is external; no population inference."})
        return out
    registered=_require_bool(manifest,"hypothesis_preregistered")
    sealed=_require_bool(manifest,"sealed_readout")
    independent=_require_bool(manifest,"clusters_independent")
    exchangeable=_require_bool(manifest,"exchangeable_pair_labels")
    # A cluster is the independent resampling unit. Never use case-level
    # McNemar inference when repeated cases share a root/seed/source.
    family_alpha=a/comparisons  # familywise alpha for reported intervals and lower bounds
    cp=None
    if independent and n == g:
        c=clopper_pearson_bracket(sum(cand),n,family_alpha)
        b=clopper_pearson_bracket(sum(base),n,family_alpha)
        cp={"candidate":[float(c["lower_outward"]),float(c["upper_outward"])],
            "baseline":[float(b["lower_outward"]),float(b["upper_outward"])],
            "method":"outward_exact_Clopper_Pearson_iid_cases"}
    ci=cluster_bootstrap_ci(effects,family_alpha,seed=seed,resamples=boot)
    # Non-asymptotic, one-sided Hoeffding bounds for the equal-cluster-macro
    # mean of independent differences in [-1,1]. Valid for effect floors > 0,
    # assuming the declared cluster sampling target; intentionally conservative.
    t=math.sqrt(2*math.log(1/float(family_alpha))/g) if independent else None
    guaranteed_lower=max(-1.0,float(point)-t) if t is not None else None
    guaranteed_upper=min(1.0,float(point)+t) if t is not None else None
    if independent and exchangeable:
        if n == g:
            p=flat["p_exact"]
            test="exact_McNemar_independent_pairs"
        else:
            p,test=signflip_cluster_p(effects,seed=seed,simulations=mc)
    else:
        p=None;test="unavailable_without_independence_and_exchangeability"
    padj=min(Q(1),p*comparisons) if p is not None else None
    audited=registered and sealed and independent and exchangeable and g>=min_units
    if (audited and p is not None and ci is not None and padj <= a and
        ((floor == 0 and ci[0] > 0) or
         (floor > 0 and guaranteed_lower is not None and guaranteed_lower > float(floor)))):
        verdict="confirmed"
    elif audited and guaranteed_upper is not None and guaranteed_upper < float(floor):
        verdict="refuted"
    elif point > floor:
        verdict="suggestive"
    else:
        verdict="inconclusive"
    reasons=[]
    if not registered: reasons.append("hypothesis_not_preregistered")
    if not sealed: reasons.append("readout_used_in_selection_or_unsealed")
    if not independent: reasons.append("cluster_independence_unattested")
    if not exchangeable: reasons.append("paired_label_exchangeability_unattested")
    if g < min_units: reasons.append("insufficient_independent_clusters_for_policy")
    if ci is None: reasons.append("cluster_interval_unavailable")
    if padj is not None and padj > a: reasons.append("adjusted_test_not_significant")
    if ci is not None and ci[0] <= float(floor): reasons.append("cluster_interval_crosses_effect_floor")
    if floor > 0 and (guaranteed_lower is None or guaranteed_lower <= float(floor)):
        reasons.append("nonasymptotic_effect_floor_bound_not_met")
    if verdict=="refuted": reasons.append("cluster_interval_excludes_preregistered_effect_floor_from_above")
    out.update({"verdict":verdict,"gate_reasons":reasons,
                "hypothesis_preregistered":registered,"sealed_readout":sealed,
                "clusters_independent":independent,"exchangeable_pair_labels":exchangeable,
                "min_independent_clusters":min_units,"cluster_bootstrap_interval":list(ci) if ci else None,
                "cluster_bootstrap_method":"approximate_equal_cluster_percentile_resampling",
                "familywise_alpha":float(family_alpha),
                "hoeffding_one_sided_effect_bounds":[guaranteed_lower,guaranteed_upper],
                "cluster_bootstrap_resamples":boot,"resample_seed":seed,
                "test":test,"p_unadjusted":float(p) if p is not None else None,
                "p_exact_fraction":str(p) if p is not None and test.startswith("exact") else None,
                "p_bonferroni":float(padj) if padj is not None else None,
                "accuracy_intervals":cp,
                "scope_note":"Independent representative clusters and symmetric paired-label null are declared assumptions; clustered bootstrap has weak small-G coverage. Floors above zero require conservative Hoeffding lower bounds. Bonferroni covers the stated preplanned family only. Reuse requires an untouched sealed confirmation readout."})
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--require-confirmed",action="store_true",
                        help="exit 2 unless the verdict is confirmed or exact_finite_result")
    args=parser.parse_args(argv)
    manifest_bytes=args.manifest.read_bytes()
    doc=json.loads(manifest_bytes)
    report=evaluate_manifest(doc)
    report["manifest_sha256"]=hashlib.sha256(manifest_bytes).hexdigest()
    serialized=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(serialized,encoding="utf-8")
    else:
        print(serialized,end="")
    if args.require_confirmed and report["verdict"] not in ("confirmed","exact_finite_result"):
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())

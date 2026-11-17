"""Independent finite enumerations and fail-closed evidence-gate tests."""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product
from math import comb

import pytest

from spiral_ln.evaluation_finite_sample import (
    binomial_two_sided, clopper_pearson_bracket, cluster_bootstrap_ci,
    evaluate_manifest, exact_mcnemar, hoeffding_accuracy_n,
    holm_adjust, signflip_cluster_p,
)


def manifest(n=64,clusters=64,*,gain=15,loss=3,seal=True,register=True,
             independent=True,exchangeable=True,comparisons=1,floor="0"):
    assert n % clusters == 0 and gain + loss <= n
    types = [(1,0)] * gain + [(0,1)] * loss + [(0,0)] * (n - gain - loss)
    return {"schema_version":1,"experiment_id":"FSI-TEST","target_population":"toy Bernoulli tasks",
            "evaluation_mode":"sampled","alpha":"0.05","minimum_effect":floor,
            "planned_comparisons":comparisons,"hypothesis_preregistered":register,
            "sealed_readout":seal,"clusters_independent":independent,
            "exchangeable_pair_labels":exchangeable,
            "bootstrap_resamples":512,"signflip_simulations":2000,
            "cases":[{"case_id":f"x{i}","cluster_id":f"g{i%clusters}",
                      "candidate":int(a),"baseline":int(b)}
                     for i,(a,b) in enumerate(types)]}


def test_binomial_two_sided_exact_enumerated_null():
    for n in range(0,8):
        for k in range(n+1):
            low=min(k,n-k)
            all_bits=list(product((0,1),repeat=n))
            extreme=sum(sum(bits) <= low or sum(bits)>=n-low for bits in all_bits)
            assert binomial_two_sided(k,n)==Q(extreme,2**n)
    assert binomial_two_sided(15,18)==Q(247,32768)
    assert binomial_two_sided(0,0)==1
    with pytest.raises(ValueError): binomial_two_sided(-1,3)


def test_mcnemar_has_discordant_only_exact_p():
    a=[1]*15+[0]*3+[0]*46
    b=[0]*15+[1]*3+[0]*46
    r=exact_mcnemar(a,b)
    assert (r["candidate_only"],r["baseline_only"],r["ties"])==(15,3,46)
    assert r["p_exact"]==Q(247,32768)
    assert exact_mcnemar([1]*4,[1]*4)["p_exact"]==1
    with pytest.raises(ValueError):exact_mcnemar([True],[0])


def test_clopper_pearson_encloses_true_tail_endpoints():
    for n in range(1,9):
        for k in range(n+1):
            c=clopper_pearson_bracket(k,n,Q(1,20),bits=9)
            lo,hi=c["lower_outward"],c["upper_outward"]
            assert 0<=lo<=hi<=1
            if k:
                p=sum(Q(comb(n,j))*lo**j*(1-lo)**(n-j) for j in range(k,n+1))
                assert p <= Q(1,40)
            else: assert lo==0
            if k<n:
                p=sum(Q(comb(n,j))*hi**j*(1-hi)**(n-j) for j in range(k+1))
                assert p <= Q(1,40)
            else: assert hi==1
    c=clopper_pearson_bracket(64,64,Q(1,20),bits=18)
    assert .94398<float(c["lower_outward"])<.94401
    assert c["upper_outward"]==1


def test_holm_monotonic_with_exact_fractions():
    assert holm_adjust([Q(1,100),Q(2,100),Q(9,10)])==[
        Q(3,100),Q(4,100),Q(9,10)]
    assert holm_adjust([Q(1,5),Q(1,5)])==[Q(2,5),Q(2,5)]
    with pytest.raises(ValueError): holm_adjust([])


def test_signflip_matches_brute_integer_combinations():
    effects=[Q(1,2),Q(1,3),Q(-1,4)]
    expected=sum(abs(sum(a*b for a,b in zip(s,effects))) >= abs(sum(effects))
                 for s in product((-1,1),repeat=3))
    p,method=signflip_cluster_p(effects)
    assert method=="exact_cluster_sign_flip" and p==Q(expected,8)
    assert signflip_cluster_p([Q(1)]*8)[0]==Q(2,2**8)
    p1,m1=signflip_cluster_p([Q(1)]*20,seed=123,simulations=250)
    p2,m2=signflip_cluster_p([Q(1)]*20,seed=123,simulations=250)
    assert (p1,m1)==(p2,m2)
    assert m1=="monte_carlo_cluster_sign_flip" and p1>=Q(1,251)


def test_bootstrap_clusters_reproducibly():
    vals=[Q(1,8),Q(5,8),Q(1,8),Q(0),Q(1,4),Q(1,4),Q(1,4),Q(-1,8)]
    a=cluster_bootstrap_ci(vals,Q(1,20),seed=33,resamples=512)
    b=cluster_bootstrap_ci(vals,Q(1,20),seed=33,resamples=512)
    assert a==b and a[0] < a[1]
    assert cluster_bootstrap_ci([Q(1,2)],Q(1,20)) is None


def test_sealed_64_independent_can_confirm_primary_positive():
    m=manifest()
    r=evaluate_manifest(m)
    assert r["n_cases"]==64 and r["n_clusters"]==64
    assert r["verdict"]=="confirmed"
    assert r["p_exact_fraction"]==str(Q(247,32768))
    assert r["p_bonferroni"]<.01
    assert r["accuracy_intervals"] is not None
    assert r["cluster_bootstrap_interval"][0]>0


def test_8_roots_do_not_count_as_64_independent_cases():
    r=evaluate_manifest(manifest(clusters=8))
    assert r["n_clusters"]==8
    assert r["verdict"]=="suggestive"
    assert r["test"]=="exact_cluster_sign_flip"
    assert r["accuracy_intervals"] is None
    assert "insufficient_independent_clusters_for_policy" in r["gate_reasons"]


def test_reuse_and_unregistered_gate_even_when_nominally_significant():
    for m in (manifest(seal=False),manifest(register=False),manifest(independent=False),
              manifest(exchangeable=False),manifest(comparisons=32)):
        r=evaluate_manifest(m)
        assert r["verdict"]!="confirmed"
    reused=evaluate_manifest(manifest(seal=False))
    assert "readout_used_in_selection_or_unsealed" in reused["gate_reasons"]
    assert reused["p_unadjusted"] is not None
    assert evaluate_manifest(manifest(comparisons=32))["p_bonferroni"]>.05


def test_exhaustive_scope_requires_audit_attestation():
    m=manifest(n=8,clusters=8,gain=4,loss=1)
    m["evaluation_mode"]="exhaustive"
    m["declared_domain_size"]=8
    m["coverage_audit_sha256"]="a"*64
    r=evaluate_manifest(m)
    assert r["verdict"]=="exact_finite_result"
    assert "no population inference" in r["inference_note"]
    m["declared_domain_size"]=9
    with pytest.raises(ValueError,match="declared_domain_size"):
        evaluate_manifest(m)


def test_rejects_silent_missing_provenance_and_duplicates():
    m=manifest()
    del m["sealed_readout"]
    with pytest.raises(ValueError,match="sealed_readout"):
        evaluate_manifest(m)
    m=manifest()
    m["cases"][1]["case_id"]=m["cases"][0]["case_id"]
    with pytest.raises(ValueError,match="duplicate"):
        evaluate_manifest(m)
    m=manifest()
    m["alpha"]=0.05
    with pytest.raises(ValueError,match="decimal string"):
        evaluate_manifest(m)
    m=manifest()
    m["cases"][0]["candidate"]=True
    with pytest.raises(ValueError,match="0/1"):
        evaluate_manifest(m)


def test_conservative_planning_avoids_pseudoreplication():
    assert hoeffding_accuracy_n("0.05","0.05")==738
    assert hoeffding_accuracy_n("0.10","0.05")==185
    with pytest.raises(ValueError): hoeffding_accuracy_n(0.05,0.05)


def test_positive_effect_floor_requires_nonautsymmetric_risk_bound():
    r=evaluate_manifest(manifest(floor="0.10"))
    assert r["verdict"]=="suggestive"
    assert "nonasymptotic_effect_floor_bound_not_met" in r["gate_reasons"]
    assert r["hoeffding_one_sided_effect_bounds"][0] < .1


def test_family_alpha_scales_reported_intervals():
    a=evaluate_manifest(manifest(comparisons=1))
    b=evaluate_manifest(manifest(comparisons=32))
    assert b["familywise_alpha"]==a["familywise_alpha"]/32
    assert b["accuracy_intervals"]["candidate"][0] < a["accuracy_intervals"]["candidate"][0]
    assert b["accuracy_intervals"]["candidate"][1] > a["accuracy_intervals"]["candidate"][1]

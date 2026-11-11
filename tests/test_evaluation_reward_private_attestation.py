"""RHT-25: independent exact controls for sealed persistent-state attestation."""
from fractions import Fraction as Q
from itertools import product
import random

import pytest

from spiral_ln.evaluation_reward_stateful_awareness import (
    IntegrityProbe, StatefulAwarenessGame, PolicyNode, EXPLOIT,
    terminal_traces, visible_trace_distance, uniform_public_equivalence,
)
from spiral_ln.evaluation_reward_private_attestation import (
    SealedAttestor, audit_public_alias, attested_trace_law, audit_budget,
)


def constant_integrity(name, probability, *, outcomes=("ack",)):
    """Every probe sets a single terminal hidden bit, independent of old bit."""
    if outcomes != ("ack",):
        raise ValueError("use binary fixture below")
    # Each row is one observation with a binary next-integrity pair.
    rows=tuple(((1-probability,probability),) for _ in range(4))
    return IntegrityProbe(name, outcomes, rows)


def evaluator(compromise=Q(0), *, prior=Q(1,2)):
    probe=constant_integrity("silent",compromise)
    return StatefulAwarenessGame(prior,Q(2),Q(1),Q(2),1,(probe,))


ONE_PROBE=PolicyNode("probe",0,(EXPLOIT,))


def test_silent_hidden_alias_becomes_separately_attestable():
    honest=evaluator(Q(0))
    tampered=evaluator(Q(1))
    assert uniform_public_equivalence(honest,tampered)
    assert visible_trace_distance(honest,tampered,ONE_PROBE)==0
    auditor=SealedAttestor(Q(1,4),Q(3,4))
    expected=((0,Q(0),Q(1,2)),(1,Q(1,2),Q(1,4)),
              (2,Q(1,2),Q(1,4)),(3,Q(11,16),Q(5,32)),
              (4,Q(11,16),Q(5,32)),(5,Q(203,256),Q(53,512)))
    for n,tv,error in expected:
        cert=audit_public_alias(honest,tampered,ONE_PROBE,auditor,n)
        assert cert.public_tv==0
        assert cert.hidden_integrity_separation==1
        assert cert.compromised_exploit_difference==1
        assert cert.report_channel_tv==cert.observed_joint_tv==tv
        assert cert.equal_prior_model_error==error
        assert cert.limiting_error==0
        assert (cert.model_a_false_alarm+cert.model_b_miss_probability)/2==error
        assert cert.public_transcripts==1
    assert audit_budget(honest,tampered,ONE_PROBE,auditor,Q(1,5),
                        max_reports=5).minimum_reports==3


def test_persistent_hidden_integrity_creates_irreducible_mixture_error():
    a=evaluator(Q(1,4))
    b=evaluator(Q(3,4))
    auditor=SealedAttestor(Q(1,4),Q(3,4))
    cert=audit_public_alias(a,b,ONE_PROBE,auditor,3)
    assert cert.hidden_integrity_separation==Q(1,2)
    assert cert.report_channel_tv==Q(11,16)
    assert cert.observed_joint_tv==Q(11,32)
    assert cert.equal_prior_model_error==Q(21,64)
    assert cert.limiting_error==Q(1,4)
    budget=audit_budget(a,b,ONE_PROBE,auditor,Q(1,5),max_reports=20)
    assert budget.minimum_reports is None
    assert budget.limiting_error==Q(1,4)
    assert all(v>=Q(1,4) for v in budget.error_frontier)
    # The WRONG independent-resampling model predicts a different value:
    # Binomial(n, (1-s)*f+s*t) instead of a mixture of two binomials.
    naive=lambda x: tuple(Q(3 if k in (1,2) else 1)
            *x**k*(1-x)**(3-k) for k in range(4))
    x,y=naive(Q(3,8)),naive(Q(5,8))
    assert sum((abs(i-j) for i,j in zip(x,y)),Q(0))/2==Q(47,128)
    assert cert.observed_joint_tv!=Q(47,128)


def test_public_trace_conditioning_exposes_cancelled_aggregate_risk():
    # Both models compromise on exactly half the episodes overall.
    # Model A compromises on outcome 'left', B on 'right'.
    rows_a=tuple(((Q(0),Q(1,2)),(Q(1,2),Q(0))) for _ in range(4))
    rows_b=tuple(((Q(1,2),Q(0)),(Q(0),Q(1,2))) for _ in range(4))
    a=StatefulAwarenessGame(Q(1,2),2,1,2,1,
        (IntegrityProbe("probe",("left","right"),rows_a),))
    b=StatefulAwarenessGame(Q(1,2),2,1,2,1,
        (IntegrityProbe("probe",("left","right"),rows_b),))
    fixed=PolicyNode("probe",0,(EXPLOIT,EXPLOIT))
    assert uniform_public_equivalence(a,b)
    assert visible_trace_distance(a,b,fixed)==0
    traces_a=terminal_traces(a,fixed)
    traces_b=terminal_traces(b,fixed)
    assert sum((t.deployment_compromised for t in traces_a),Q(0))==Q(1,2)
    assert sum((t.deployment_compromised for t in traces_b),Q(0))==Q(1,2)
    auditor=SealedAttestor(Q(1,4),Q(3,4))
    cert=audit_public_alias(a,b,fixed,auditor,1)
    assert cert.compromised_exploit_difference==0
    assert cert.hidden_integrity_separation==1
    assert cert.observed_joint_tv==Q(1,2)
    assert cert.equal_prior_model_error==Q(1,4)
    assert cert.public_transcripts==2


def test_perfect_or_uninformative_sealed_attestation():
    honest,tampered=evaluator(Q(0)),evaluator(Q(1))
    perfect=SealedAttestor(Q(0),Q(1))
    noisy=SealedAttestor(Q(2,5),Q(2,5))
    assert audit_public_alias(honest,tampered,ONE_PROBE,perfect,0).equal_prior_model_error==Q(1,2)
    assert audit_public_alias(honest,tampered,ONE_PROBE,perfect,1).equal_prior_model_error==0
    assert audit_budget(honest,tampered,ONE_PROBE,perfect,Q(0),
                        max_reports=2).minimum_reports==1
    for n in (0,1,2,5,12):
        cert=audit_public_alias(honest,tampered,ONE_PROBE,noisy,n)
        assert cert.observed_joint_tv==0
        assert cert.equal_prior_model_error==cert.limiting_error==Q(1,2)
    plan=audit_budget(honest,tampered,ONE_PROBE,noisy,Q(1,4),max_reports=6)
    assert plan.minimum_reports is None


def test_deployment_and_evaluation_are_separately_conditioned():
    # In E, a probe never compromises under either model; in D it differs.
    rows_a=tuple(((Q(1),Q(0)),) for _ in range(4))
    rows_b=tuple(((Q(1),Q(0)),) if old_world==0 else ((Q(0),Q(1)),)
                 for old_world in (0,0,1,1))
    a=StatefulAwarenessGame(Q(1,2),2,1,2,1,
        (IntegrityProbe("probe",("ack",),rows_a),))
    b=StatefulAwarenessGame(Q(1,2),2,1,2,1,
        (IntegrityProbe("probe",("ack",),rows_b),))
    attestor=SealedAttestor(Q(1,4),Q(3,4))
    ev=audit_public_alias(a,b,ONE_PROBE,attestor,3,world="evaluation")
    de=audit_public_alias(a,b,ONE_PROBE,attestor,3,world="deployment")
    assert ev.hidden_integrity_separation==ev.observed_joint_tv==0
    assert ev.equal_prior_model_error==Q(1,2)
    assert de.hidden_integrity_separation==1
    assert de.observed_joint_tv==Q(11,16)


def test_independent_exhaustive_binary_report_sequences():
    rng=random.Random(251125)
    for _ in range(30):
        s_a=Q(rng.randrange(9),8)
        s_b=Q(rng.randrange(9),8)
        attestor=SealedAttestor(Q(rng.randrange(9),8),Q(rng.randrange(9),8))
        a,b=evaluator(s_a),evaluator(s_b)
        for n in range(5):
            ca=audit_public_alias(a,b,ONE_PROBE,attestor,n)
            # Independent oracle enumerates ordered bit strings, samples
            # one integrity bit per episode, and then draws conditional
            # independent noisy reports from that SAME bit.
            sequence_tv=Q(0)
            by_count_a=[Q(0)]*(n+1)
            by_count_b=[Q(0)]*(n+1)
            for bits in product((0,1),repeat=n):
                k=sum(bits)
                p0=p1=Q(1)
                for bit in bits:
                    p0*=attestor.false_positive if bit else 1-attestor.false_positive
                    p1*=attestor.sensitivity if bit else 1-attestor.sensitivity
                pa=(1-s_a)*p0+s_a*p1
                pb=(1-s_b)*p0+s_b*p1
                sequence_tv+=abs(pa-pb)/2
                by_count_a[k]+=pa
                by_count_b[k]+=pb
            assert ca.observed_joint_tv==sequence_tv
            law_a=attested_trace_law(a,ONE_PROBE,attestor,n,"deployment")
            law_b=attested_trace_law(b,ONE_PROBE,attestor,n,"deployment")
            assert list(law_a.values())==by_count_a
            assert list(law_b.values())==by_count_b
            assert ca.equal_prior_model_error==(1-sequence_tv)/2


def test_validation_public_alias_requirement_and_report_budget():
    good=evaluator(Q(0))
    other=evaluator(Q(1))
    private=SealedAttestor(Q(1,4),Q(3,4))
    with pytest.raises(ValueError,match="attestor rates"):
        SealedAttestor(Q(-1,2),Q(1,2))
    with pytest.raises(ValueError,match="exact rational"):
        SealedAttestor(0.1,Q(1,2))
    with pytest.raises(ValueError,match="report count"):
        private.count_law(True,False)
    with pytest.raises(ValueError,match="report count"):
        audit_public_alias(good,other,ONE_PROBE,private,65)
    with pytest.raises(ValueError,match="Boolean"):
        private.count_law(1,1)
    with pytest.raises(ValueError,match="target error"):
        audit_budget(good,other,ONE_PROBE,private,Q(-1,2))
    with pytest.raises(ValueError,match="world must be"):
        audit_public_alias(good,other,ONE_PROBE,private,1,world="invalid")
    # Identical policy grammar with different observable laws should reject
    # use of the simplified factorization theorem.
    two_a=tuple(((Q(1,2),Q(0)),(Q(1,2),Q(0))) for _ in range(4))
    two_b=tuple(((Q(3,4),Q(0)),(Q(1,4),Q(0))) for _ in range(4))
    g_a=StatefulAwarenessGame(Q(1,2),2,1,2,1,
        (IntegrityProbe("probe",("left","right"),two_a),))
    g_b=StatefulAwarenessGame(Q(1,2),2,1,2,1,
        (IntegrityProbe("probe",("left","right"),two_b),))
    with pytest.raises(ValueError,match="public transcript alias"):
        audit_public_alias(g_a,g_b,PolicyNode("probe",0,(EXPLOIT,EXPLOIT)),
                           private,1)

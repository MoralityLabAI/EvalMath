"""RHT-22 independent alpha envelope, exhaustive-policy and transfer controls."""
from fractions import Fraction as Q
from itertools import product
import random

import pytest

from spiral_ln.evaluation_reward_training_awareness import EvaluationCueGame
from spiral_ln.evaluation_reward_training_awareness_sequential import (
    EvaluationProbe, bayes_update, solve_belief, solve_initial_cues,
    policy_type_metrics, alpha_vectors, robust_prior_envelope,
)


def reference_initial():
    return EvaluationCueGame(
        ("deployment_looking", "evaluation_looking"),
        (Q(1,4), Q(3,4)), (Q(3,4), Q(1,4)), Q(1,8), Q(8), Q(1)
    )


def perfect_probe(cost=Q(0)):
    return EvaluationProbe("perfect", ("deploy", "eval"),
                           (Q(0), Q(1)), (Q(1), Q(0)), cost)


def imperfect_probe(cost=Q(0)):
    return EvaluationProbe("imperfect", ("deploy", "eval"),
                           (Q(1,4), Q(3,4)), (Q(3,4), Q(1,4)), cost)


def policies(depth, probes):
    """Independent full enumeration of all possible finite contingent plans."""
    out = [("protect",), ("exploit",)]
    if depth:
        child = policies(depth-1, probes)
        for i, probe in enumerate(probes):
            for branch in product(child, repeat=len(probe.observations)):
                out.append(("probe", i, branch))
    return out


def independent_value(tree, e, d, r, g, delta, probes):
    if tree[0] == "protect":
        return e*r+(e+d)*delta
    if tree[0] == "exploit":
        return d*g
    q = probes[tree[1]]
    return -(e+d)*q.cost + sum((
        independent_value(child,e*qe,d*qd,r,g,delta,probes)
        for child,qe,qd in zip(tree[2],q.evaluation,q.deployment)
    ),Q(0))


def test_zero_horizon_exact_rht20_regression():
    game = reference_initial()
    cert = solve_initial_cues(game, (), 0)
    assert cert.initial_actions == ("exploit", "protect")
    assert cert.evaluation_protection == Q(3,4)
    assert cert.deployment_protection == Q(1,4)
    assert cert.subjective_optimal_value == cert.subjective_no_probe_value
    assert cert.initial_cue_tv == cert.complete_transcript_tv == Q(1,2)
    assert cert.coupling_tv_upper_bound == Q(1,2)
    assert cert.expected_probes_evaluation == cert.expected_probes_deployment == 0


def test_perfect_probe_makes_evaluation_protection_one_and_deployment_zero():
    cert = solve_initial_cues(reference_initial(), (perfect_probe(),), 1)
    assert cert.initial_actions == ("probe", "probe")
    assert (cert.evaluation_protection, cert.deployment_protection) == (1,0)
    assert cert.initial_cue_tv == Q(1,2)
    assert cert.complete_transcript_tv == cert.coupling_tv_upper_bound == 1
    assert cert.subjective_optimal_value == Q(15,8)
    assert cert.subjective_optimal_value > cert.subjective_no_probe_value
    assert cert.expected_probes_evaluation == cert.expected_probes_deployment == 1


def test_imperfect_probe_yields_strict_adaptive_value_gain_and_sealed_transfer():
    cert = solve_initial_cues(reference_initial(), (imperfect_probe(),), 1)
    assert cert.initial_actions == ("probe", "protect")
    assert cert.subjective_optimal_value - cert.subjective_no_probe_value == Q(3,128)
    assert (cert.evaluation_protection, cert.deployment_protection) == (Q(15,16),Q(7,16))
    assert (cert.expected_probes_evaluation, cert.expected_probes_deployment) == (Q(1,4),Q(3,4))
    assert cert.complete_transcript_tv == Q(1,2)
    assert cert.coupling_tv_upper_bound == Q(3,4)


def test_identical_kernels_and_positive_cost_do_not_trigger_probing():
    game = reference_initial()
    no_info = EvaluationProbe("null",("a","b"),(Q(1,3),Q(2,3)),(Q(1,3),Q(2,3)),Q(1,10))
    cert = solve_initial_cues(game,(no_info,),3)
    assert cert.initial_actions == ("exploit","protect")
    assert cert.subjective_optimal_value == cert.subjective_no_probe_value
    assert cert.complete_transcript_tv == cert.initial_cue_tv
    assert cert.conditional_probe_tv_cap == 0
    assert cert.transcript_leaves_checked == 2


def test_bayes_update_exact_posterior_martingale_including_zeros():
    q = imperfect_probe()
    p=Q(2,5)
    updates=[bayes_update(p,1-p,q,i) for i in range(2)]
    assert sum((e+d for e,d,_ in updates),Q(0)) == 1
    assert sum(((e+d)*post for e,d,post in updates),Q(0)) == p
    assert bayes_update(Q(0),Q(0),q,0)==(0,0,None)
    assert bayes_update(Q(1),Q(0),perfect_probe(),0)==(0,0,None)


def test_full_finite_contingent_policy_census_independent_bellman():
    rng=random.Random(20261111)
    for nprobes in (1,2):
        for depth in (0,1,2):
            for _ in range(5):
                probes=[]
                for j in range(nprobes):
                    u,v=rng.randrange(5),rng.randrange(5)
                    probes.append(EvaluationProbe(str(j),("0","1"),
                        (Q(u,4),1-Q(u,4)),(Q(v,4),1-Q(v,4)),
                        Q(rng.randrange(3),5)))
                qs=tuple(probes)
                w_e,w_d=Q(rng.randrange(1,8),16),Q(rng.randrange(1,8),16)
                r,g,delta=Q(rng.randrange(1,7)),Q(rng.randrange(1,7)),Q(rng.randrange(-2,3),3)
                node,_=solve_belief(w_e,w_d,protect_reward=r,exploit_gain=g,
                                    future_delta=delta,probes=qs,horizon=depth)
                oracle=max(independent_value(t,w_e,w_d,r,g,delta,qs)
                           for t in policies(depth,qs))
                assert node.value==oracle


def test_alpha_vectors_agree_with_exact_belief_dp_on_random_priors():
    rng=random.Random(3101)
    for depth in (0,1,2):
        for _ in range(15):
            u,v=rng.randrange(5),rng.randrange(5)
            qs=(EvaluationProbe("q",("no","yes"),(Q(u,4),1-Q(u,4)),
                 (Q(v,4),1-Q(v,4)),Q(rng.randrange(3),8)),)
            r,g,delta=Q(rng.randrange(1,5)),Q(rng.randrange(1,5)),Q(rng.randrange(-2,3),4)
            vecs=alpha_vectors(qs,depth,protect_reward=r,exploit_gain=g,
                               future_delta=delta)
            for p in (Q(0),Q(1,7),Q(1,2),Q(6,7),Q(1)):
                n,_=solve_belief(p,1-p,protect_reward=r,exploit_gain=g,
                                 future_delta=delta,probes=qs,horizon=depth)
                assert n.value==max(v.at_prior(p) for v in vecs)


def test_prior_envelope_has_strict_interior_worst_case():
    game=EvaluationCueGame(("only",),(Q(1),),(Q(1),),Q(1,2),Q(1),Q(1))
    raw=robust_prior_envelope(game,(),0,(Q(0),Q(1)))
    assert raw.minimum_optimal_value==Q(1,2)
    assert raw.worst_prior==Q(1,2)
    assert raw.prior_endpoints_only_minimum==1
    observed=robust_prior_envelope(game,(perfect_probe(Q(1,4)),),1,(Q(0),Q(1)))
    assert observed.minimum_optimal_value==Q(3,4)
    assert observed.prior_endpoints_only_minimum==1
    assert observed.worst_prior==Q(1,4)
    for p in (Q(0),Q(1,10),Q(1,4),Q(1,2),Q(3,4),Q(9,10),Q(1)):
        atp=EvaluationCueGame(game.cues,game.evaluation,game.deployment,p,1,1)
        cert=solve_initial_cues(atp,(perfect_probe(Q(1,4)),),1)
        assert cert.subjective_optimal_value>=observed.minimum_optimal_value


def test_multi_initial_cue_global_prior_breakpoints_exact():
    game=reference_initial()
    for qs,depth in [((),0),((imperfect_probe(Q(1,8)),),1),((perfect_probe(Q(1,5)),),2)]:
        cert=robust_prior_envelope(game,qs,depth,(Q(0),Q(1)))
        assert cert.minimum_optimal_value <= cert.prior_endpoints_only_minimum
        for p in (Q(i,25) for i in range(26)):
            atp=EvaluationCueGame(game.cues,game.evaluation,game.deployment,
                                  p,game.protect_reward,game.exploit_gain)
            exact=solve_initial_cues(atp,qs,depth)
            assert cert.minimum_optimal_value<=exact.subjective_optimal_value


def test_random_full_transcript_tv_respects_coupling_upper_bound():
    rng=random.Random(21)
    for _ in range(40):
        u,v=rng.randrange(5),rng.randrange(5)
        e=(Q(u,4),1-Q(u,4));d=(Q(v,4),1-Q(v,4))
        q0,q1=rng.randrange(5),rng.randrange(5)
        p=Q(rng.randrange(9),8)
        game=EvaluationCueGame(("a","b"),e,d,p,Q(3),Q(2))
        qs=(EvaluationProbe("q",("n","y"),(Q(q0,4),1-Q(q0,4)),
                 (Q(q1,4),1-Q(q1,4)),Q(rng.randrange(3),10)),)
        cert=solve_initial_cues(game,qs,2)
        assert abs(cert.evaluation_protection-cert.deployment_protection)<=cert.complete_transcript_tv
        assert cert.complete_transcript_tv<=cert.coupling_tv_upper_bound<=1
        assert cert.subjective_optimal_value>=cert.subjective_no_probe_value


def test_caps_and_bad_kernels_fail_closed():
    with pytest.raises(ValueError,match="normalized"):
        EvaluationProbe("bad",("yes",),(Q(1,2),),(Q(1),))
    with pytest.raises(ValueError,match="nonnegative"):
        EvaluationProbe("bad",("yes",),(Q(1),),(Q(1),),Q(-1))
    with pytest.raises(ValueError,match="unique"):
        EvaluationProbe("bad",("x","x"),(Q(1,2),Q(1,2)),(Q(1,2),Q(1,2)))
    with pytest.raises(ValueError,match="exact rational"):
        EvaluationProbe("bad",("yes",),(1.0,),(Q(1),))
    with pytest.raises(ValueError,match="state cap"):
        solve_belief(Q(1,2),Q(1,2),protect_reward=1,exploit_gain=1,
                     probes=(imperfect_probe(),),horizon=3,max_states=1)
    with pytest.raises(ValueError,match="alpha vector cap"):
        alpha_vectors((perfect_probe(),),2,protect_reward=1,exploit_gain=1,
                      max_vectors=1)
    with pytest.raises(ValueError,match="alpha proposal cap"):
        alpha_vectors((imperfect_probe(),),2,protect_reward=1,exploit_gain=1,
                      max_proposals=1)
    with pytest.raises(ValueError,match="transcript cap"):
        solve_initial_cues(reference_initial(),(perfect_probe(),),1,max_transcript_leaves=1)
    with pytest.raises(ValueError,match="invalid prior interval"):
        robust_prior_envelope(reference_initial(),(),0,(Q(1,2),Q(1,4)))


def test_existing_rht21_active_solver_crosscheck():
    """Independent RHT-21 implementation must agree on the shared grammar."""
    from spiral_ln.evaluation_reward_active_awareness import (
        ObservationLaw, Probe, ActiveEvaluationGame,
        optimize_active_policy, certify_active_transfer,
    )
    rng = random.Random(220011)
    for horizon in (0, 1, 2):
        for _ in range(20):
            a, b, c, d = (rng.randrange(5) for _ in range(4))
            cue_e = (Q(a, 4), 1-Q(a, 4))
            cue_d = (Q(b, 4), 1-Q(b, 4))
            probe_e = (Q(c, 4), 1-Q(c, 4))
            probe_d = (Q(d, 4), 1-Q(d, 4))
            p = Q(rng.randrange(9), 8)
            r, g = Q(rng.randrange(1, 7)), Q(rng.randrange(1, 7))
            delta = Q(rng.randrange(-2, 3), 4)
            cost = Q(rng.randrange(4), 10)
            initial = EvaluationCueGame(
                ("cue0", "cue1"), cue_e, cue_d, p, r, g,
                (delta, delta),
            )
            independent_probe = EvaluationProbe(
                "test", ("obs0", "obs1"), probe_e, probe_d, cost,
            )
            ours = solve_initial_cues(initial, (independent_probe,), horizon)
            other = ActiveEvaluationGame(
                p, r, g, horizon,
                (Probe("test", ObservationLaw(
                    "observations", ("obs0", "obs1"), probe_e, probe_d,
                ), cost),),
                ObservationLaw("initial", initial.cues, cue_e, cue_d),
                terminal_future_delta=delta,
            )
            optimum = optimize_active_policy(other)
            transfer = certify_active_transfer(other, optimum.policy)
            assert ours.subjective_optimal_value == optimum.subjective_value
            assert ours.evaluation_protection == transfer.evaluation_protection
            assert ours.deployment_protection == transfer.deployment_protection
            assert ours.complete_transcript_tv == transfer.exact_transcript_tv
            assert ours.coupling_tv_upper_bound == transfer.transcript_tv_bound
            assert ours.expected_probes_evaluation == transfer.evaluation_expected_probes
            assert ours.expected_probes_deployment == transfer.deployment_expected_probes

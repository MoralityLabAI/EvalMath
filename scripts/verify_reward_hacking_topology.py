"""RHT-01..13 exact theorem and adversarial-UGC-source cross-check receipt.

The receipt is deterministic and fingerprints all claim-bearing source files,
and can be compared to independently run finite oracles. This script does
not train, run, or certify any real agent or human reward model.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

from spiral_ln.evaluation_leak_topology import (
    graph_from_sizes, cycle_rank, box
)
from spiral_ln.evaluation_reward_hacking_topology import (
    cycle_periods,hidden_gold_width,circulation_oracle,minimum_gold_audit,
    proxy_optimization_regret,ugc_reachable_records,reconstruct_gold
)
from spiral_ln.evaluation_reward_ugc_fixture import bipartite_goodhart_fixture
from spiral_ln.evaluation_reward_hacking_flow import maximum_hidden_width_flow
from spiral_ln.evaluation_reward_hacking_multimap import (
    MultiMapSignals, gold_alias_report, minimum_private_audit,
    reachable_gold_alias,
)
from spiral_ln.evaluation_reward_hacking_audit_optimizer import (
    maximum_hidden_gold_dp, minimum_private_gold_audit_lazy,
)
from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    one_hot_ugc_disclosure_game, public_attack_risks,
    protected_auditor_optimum, MixedAuditNode,
    mixed_disclosure_attack_risk,
)
from spiral_ln.evaluation_reward_hacking_joint_audit import (
    optimum_joint_audit, one_hot_sealed_zero_harm_frontier,
    evaluate_joint_audit,
)
from spiral_ln.evaluation_reward_hacking_retry import (
    RetryAuditChannel,optimal_adaptive_retry,
    conditional_harm_bound,marginal_harm_bound,
    disjoint_marginal_failure_law,
)
from spiral_ln.evaluation_reward_hacking_retry_guard import (
    certify_retry_control,select_retry_control,
)
from spiral_ln.evaluation_reward_hacking_stateful import (
    MutableEvaluator,optimal_stateful_attack,
    worst_state_false_approval_rate,conditional_stateful_harm_bound,
)
from spiral_ln.evaluation_reward_hacking_stateful_guard import (
    choose_stateful_attestor,benign_stateful_profile,
    required_preprobe_detection_for_baseline_hazard,
)
from spiral_ln.evaluation_reward_transition_closure import (
    TimedRewardEdge,TimedRewardGame,certify_relative_reward,
    robust_transition_certify,
)
from spiral_ln.evaluation_reward_stochastic_closure import (
    stochastic_robust_certificate,optimize_stochastic_policy,
    expected_markov_coboundary,
)
from spiral_ln.evaluation_reward_stochastic_fixture import (
    evaluator_pomdp,fair_martingale_noise_game,
    time_expanded_support_graph,
)
from spiral_ln.evaluation_reward_hacking_guard import (
    minimal_epsilon_gold_audit,robust_proxy_guard
)
from spiral_ln.evaluation_reward_path_gauge import (
    RewardPathGame,RewardTransition,boundary_relative_certificate,
    potential_if_exact,policy_rank_reversal
)
from spiral_ln.unique_games_topology import Edge,TranslationGame


SOURCE_PATHS = (
    "src/spiral_ln/evaluation_reward_hacking_topology.py",
    "src/spiral_ln/evaluation_reward_path_gauge.py",
    "src/spiral_ln/evaluation_reward_hacking_guard.py",
    "src/spiral_ln/evaluation_reward_ugc_fixture.py",
    "src/spiral_ln/evaluation_reward_hacking_flow.py",
    "src/spiral_ln/evaluation_reward_hacking_multimap.py",
    "src/spiral_ln/evaluation_reward_hacking_audit_optimizer.py",
    "src/spiral_ln/evaluation_reward_hacking_adaptive_feedback.py",
    "src/spiral_ln/evaluation_reward_hacking_joint_audit.py",
    "src/spiral_ln/evaluation_reward_hacking_retry.py",
    "src/spiral_ln/evaluation_reward_hacking_retry_guard.py",
    "src/spiral_ln/evaluation_reward_hacking_stateful.py",
    "src/spiral_ln/evaluation_reward_hacking_stateful_guard.py",
    "src/spiral_ln/evaluation_reward_transition_closure.py",
    "src/spiral_ln/evaluation_reward_stochastic_closure.py",
    "src/spiral_ln/evaluation_reward_stochastic_fixture.py",
    "tests/test_evaluation_reward_hacking_topology.py",
    "tests/test_evaluation_reward_path_gauge.py",
    "tests/test_evaluation_reward_hacking_guard.py",
    "tests/test_evaluation_reward_ugc_fixture.py",
    "tests/test_evaluation_reward_hacking_flow.py",
    "tests/test_evaluation_reward_hacking_multimap.py",
    "tests/test_evaluation_reward_hacking_audit_optimizer.py",
    "tests/test_evaluation_reward_hacking_adaptive_feedback.py",
    "tests/test_evaluation_reward_hacking_joint_audit.py",
    "tests/test_evaluation_reward_hacking_retry.py",
    "tests/test_evaluation_reward_hacking_retry_guard.py",
    "tests/test_evaluation_reward_hacking_stateful.py",
    "tests/test_evaluation_reward_hacking_stateful_guard.py",
    "tests/test_evaluation_reward_transition_closure.py",
    "tests/test_evaluation_reward_stochastic_closure.py",
    "paper/reward_hacking_cohomology.md",
    "scripts/verify_reward_hacking_topology.py",
)


def receipt() -> dict:
    g = graph_from_sizes(((0,0),(0,1),(1,0),(1,1)),(1,1,1,1))
    t = (1,0,0,1)
    periods = cycle_periods(g,t)
    width = hidden_gold_width(g,t)
    independent_width, independent_circulation = circulation_oracle(g,t)
    flow_width=maximum_hidden_width_flow(g,t)
    cert = minimum_gold_audit(g,t)
    assert cycle_rank(g)==1 and abs(periods[0][1])==2
    assert width["maximum_width"]==independent_width==flow_width.maximum_hidden_width==2
    assert cert["count"]==1
    assert all(reconstruct_gold(g,x,cert["formula"])
               == sum((Q(ti)*xi for ti,xi in zip(t,x)),Q(0))
               for x in box(g["sizes"]))

    g_ugc = TranslationGame(4,1,(
        Edge(0,1,1),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0)))
    reachable=ugc_reachable_records(g_ugc,g)
    exploit=proxy_optimization_regret(
        g,(1,0,0,0),(1,1,0,0),
        allowed_candidates=tuple(reachable))
    assert exploit.worst_true_regret==1
    assert exploit.selected_proxy_score==3
    assert exploit.worst_selected_true_utility==0
    epsilon_audit=minimal_epsilon_gold_audit(g,t,0)
    assert epsilon_audit["count"]==cert["count"]==1
    guarded=robust_proxy_guard(
        g,tuple(reachable),(1,1,0,0),((1,0,0,0),),
        max_regret=0,minimum_gold=1,
    )
    assert guarded.passed and guarded.worst_case_regret==0
    assert guarded.selected_proxy_score==3
    assert guarded.minimum_gold_level==1
    simple_bipartite=bipartite_goodhart_fixture()
    assert simple_bipartite["unguarded"].selected_proxy_score==7
    assert simple_bipartite["unguarded"].true_optimum==2
    assert simple_bipartite["unguarded"].worst_selected_true_utility==1
    assert simple_bipartite["guarded"].selected_proxy_score==5
    assert simple_bipartite["guarded"].minimum_gold_level==2
    large_graph=graph_from_sizes(
        tuple((i,j) for i in range(6) for j in range(6)),
        tuple((i%3)+1 for i in range(36))
    )
    large_weights=tuple(Q(((i*13)%11)-5,7) for i in range(36))
    large_flow=maximum_hidden_width_flow(large_graph,large_weights)
    assert large_flow.maximum_hidden_width>0
    assert cycle_rank(large_graph)==25

    higher_cells=((0,0,0),(0,0,1),(0,1,1),(1,0,1),(1,1,0))
    higher_faces=((0,),(1,),(2,))
    protected_gold=(0,1,0,0,0)
    unit=MultiMapSignals(higher_cells,(1,)*5,higher_faces)
    activated=MultiMapSignals(higher_cells,(1,2,1,1,1),higher_faces)
    before_activation=gold_alias_report(unit,protected_gold)
    after_activation=gold_alias_report(activated,protected_gold)
    higher_audit=minimum_private_audit(activated,protected_gold)
    assert before_activation["rational_nullity"]==1
    assert before_activation["bounded_integer_rank"]==0
    assert before_activation["maximum_hidden_gold_width"]==0
    assert after_activation["bounded_integer_rank"]==1
    assert after_activation["maximum_hidden_gold_width"]==2
    assert higher_audit["count"]==1

    little_grid=MultiMapSignals(
        ((0,0),(0,1),(1,0),(1,1)),(1,1,1,1),((0,),(1,)),
    )
    flat_game=TranslationGame(4,1,(
        Edge(0,1,0),Edge(1,2,0),Edge(2,3,0),Edge(3,0,0)))
    gold_d=(1,0,0,1)
    reachable_frustrated=tuple(reachable)
    reachable_flat=tuple(ugc_reachable_records(flat_game,g))
    bad_reach=reachable_gold_alias(little_grid,gold_d,reachable_frustrated)
    flat_reach=reachable_gold_alias(little_grid,gold_d,reachable_flat)
    assert bad_reach["maximum_hidden_gold_width"]==0
    assert flat_reach["maximum_hidden_gold_width"]==2
    primitive_audit=minimum_private_gold_audit_lazy(
        activated,protected_gold,cell_costs=(9,1,3,5,4),
    )
    assert primitive_audit.audited_cells==(1,)
    assert primitive_audit.count==1 and primitive_audit.cost==1
    assert primitive_audit.remaining_gold_width==0

    multimap_cells=tuple(
        (a,b,c) for a in range(2) for b in range(2) for c in range(3)
    )
    pairwise_faces=((0,1),(0,2),(1,2))
    large_multimap=MultiMapSignals(
        multimap_cells,(3,)*len(multimap_cells),pairwise_faces,
    )
    multim_gold=tuple(
        2 if v==(0,0,0) else 1 if v==(0,0,1) else 0
        for v in multimap_cells
    )
    multilinear_width=maximum_hidden_gold_dp(
        large_multimap,multim_gold,max_states=30000,
    )
    multim_audit=minimum_private_gold_audit_lazy(
        large_multimap,multim_gold,max_states=30000,
    )
    loose_audit=minimum_private_gold_audit_lazy(
        large_multimap,multim_gold,tolerance=Q(3),max_states=30000,
    )
    assert large_multimap.rational_nullity==2
    assert multilinear_width.maximum_width==6
    assert multim_audit.count==2 and multim_audit.remaining_gold_width==0
    assert loose_audit.count==1 and loose_audit.remaining_gold_width<=3
    reachable_bad_audit=minimum_private_gold_audit_lazy(
        little_grid,gold_d,reachable_records=reachable_frustrated
    )
    reachable_flat_audit=minimum_private_gold_audit_lazy(
        little_grid,gold_d,reachable_records=reachable_flat
    )
    assert reachable_bad_audit.count==0 and reachable_flat_audit.count==1

    seven_worlds=one_hot_ugc_disclosure_game(7)
    public_feedback=public_attack_risks(seven_worlds,3)
    private_feedback=protected_auditor_optimum(seven_worlds,1)
    assert public_feedback["baseline"]==Q(1,7)
    assert public_feedback["fixed"]==Q(6,7)
    assert public_feedback["adaptive"]==1
    assert private_feedback["risk"]==0

    three_worlds=one_hot_ugc_disclosure_game(3)
    q0=three_worlds.queries.index(
        tuple(int(r==0 and c==0) for r,c in three_worlds.space.cells)
    )
    q1=three_worlds.queries.index(
        tuple(int(r==0 and c==1) for r,c in three_worlds.space.cells)
    )
    stop=MixedAuditNode()
    private_root=MixedAuditNode(
        q0,"sealed",((0,stop),(1,stop))
    )
    identity_leak=MixedAuditNode(
        q0,"sealed",(
            (0,MixedAuditNode(q0,"public",((0,stop),))),
            (1,MixedAuditNode(q1,"public",((0,stop),))),
        )
    )
    hidden_risk=mixed_disclosure_attack_risk(three_worlds,private_root)
    leaked_risk=mixed_disclosure_attack_risk(three_worlds,identity_leak)
    assert hidden_risk["risk"]==Q(1,3)
    assert leaked_risk["risk"]==Q(2,3)

    joint=optimum_joint_audit(
        three_worlds,max_queries=1,
        minimum_benign_safe_authorization=Q(2,3),
        maximum_public_attack_risk=Q(1,3),
        maximum_expected_query_cost=Q(1),
        maximum_authorized_unsafe_risk=Q(0),
    )
    assert joint is not None
    assert joint.authorized_unsafe_risk==0
    assert joint.benign_safe_authorization==Q(2,3)
    assert joint.public_attack_risk_without_veto==Q(1,3)
    assert joint.expected_query_cost==1
    assert joint.policy.visibility=="sealed"
    rechecked=evaluate_joint_audit(
        three_worlds,joint.policy,
        dict(joint.allowed_actions_by_private_trace),max_depth=1,
    )
    assert rechecked.authorized_unsafe_risk==joint.authorized_unsafe_risk
    assert rechecked.benign_safe_authorization==joint.benign_safe_authorization

    zero_harm_frontier=tuple(
        one_hot_sealed_zero_harm_frontier(7,b)
        for b in range(4)
    )
    assert tuple(f.maximum_zero_harm_benign_liveness
                 for f in zero_harm_frontier)==(0,Q(4,7),Q(6,7),Q(1))
    assert tuple(f.posterior_collision_probability
                 for f in zero_harm_frontier)==(
                     Q(1),Q(25,49),Q(13,49),Q(1,7),
                 )

    retry_game=one_hot_ugc_disclosure_game(3)
    audit_noiseless_safe=RetryAuditChannel(Q(1,5),Q(0))
    adaptive_2=optimal_adaptive_retry(retry_game,2,audit_noiseless_safe)
    adaptive_3=optimal_adaptive_retry(retry_game,3,audit_noiseless_safe)
    assert adaptive_2.harmful_authorization_probability==Q(14,75)
    assert adaptive_2.best_fixed_harm_probability==Q(2,15)
    assert adaptive_3.harmful_authorization_probability==Q(131,375)
    assert adaptive_3.best_fixed_harm_probability==Q(1,5)
    assert conditional_harm_bound((Q(1,5),)*5)==Q(2101,3125)
    assert marginal_harm_bound((Q(1,5),)*5)==1
    assert disjoint_marginal_failure_law((Q(1,5),)*5)==(Q(1,5),)*5+(Q(0),)

    calibrated=RetryAuditChannel(Q(1,5),Q(1,10))
    no_repeat=RetryAuditChannel(Q(1,5),Q(1,10),forbid_repeated_action=True)
    lockout=RetryAuditChannel(Q(1,5),Q(1,10),lockout_after_rejection=True)
    stop_after_approval=RetryAuditChannel(
        Q(1,5),Q(1,10),stop_after_any_approval=True
    )
    retry_controls=(calibrated,no_repeat,lockout,stop_after_approval)
    proposed=select_retry_control(
        retry_game,2,retry_controls,
        maximum_cumulative_harm=Q(7,50),
        minimum_benign_any_safe_approval=Q(9,10),
        minimum_benign_expected_authorizations=Q(3,2),
    )
    tighter=select_retry_control(
        retry_game,2,retry_controls,
        maximum_cumulative_harm=Q(13,100),
        minimum_benign_any_safe_approval=Q(9,10),
        minimum_benign_expected_authorizations=Q(3,2),
    )
    assert proposed is not None and proposed.channel==no_repeat
    assert tighter is not None and tighter.channel==lockout
    assert proposed.worst_adaptive_harm==Q(2,15)
    assert tighter.worst_adaptive_harm==Q(19,150)
    assert proposed.benign_expected_safe_authorizations==Q(9,5)
    assert tighter.benign_expected_safe_authorizations==Q(171,100)

    weak_stateful=MutableEvaluator()
    medium_stateful=MutableEvaluator(
        alarm_if_compromised_before_probe=Q(1,2),
        alarm_if_intact_before_probe=Q(1,20),
    )
    strong_stateful=MutableEvaluator(
        alarm_if_compromised_before_probe=Q(3,4),
        alarm_if_intact_before_probe=Q(1,10),
    )
    weak_attack=optimal_stateful_attack(retry_game,2,weak_stateful)
    assert weak_attack.max_harm==Q(13,60)
    assert weak_attack.first_action=="tamper"
    safe_drift=optimal_stateful_attack(
        retry_game,2,MutableEvaluator(
            allow_tamper=False,compromise_after_safe_approval=1,
        ),
    )
    guarded_drift=optimal_stateful_attack(
        retry_game,2,MutableEvaluator(
            allow_tamper=False,compromise_after_safe_approval=1,
            alarm_if_compromised_before_probe=Q(3,4),
        ),
    )
    assert safe_drift.max_harm==Q(29,75)
    assert guarded_drift.max_harm==Q(14,75)
    assert required_preprobe_detection_for_baseline_hazard(weak_stateful)==Q(3,4)
    assert worst_state_false_approval_rate(strong_stateful)==Q(1,5)
    assert conditional_stateful_harm_bound(strong_stateful,2)==Q(9,25)

    attestor_bank=(weak_stateful,medium_stateful,strong_stateful)
    common_attestor=dict(
        minimum_benign_safe_authorization=Q(9,10),
        minimum_benign_expected_safe_authorizations=Q(17,10),
    )
    selected_medium=choose_stateful_attestor(
        retry_game,2,attestor_bank,
        maximum_cumulative_harm=Q(7,40),**common_attestor
    )
    selected_strong=choose_stateful_attestor(
        retry_game,2,attestor_bank,
        maximum_cumulative_harm=Q(4,25),**common_attestor
    )
    assert selected_medium is not None and selected_medium.channel==medium_stateful
    assert selected_strong is not None and selected_strong.channel==strong_stateful
    assert selected_medium.attack_harm==Q(5149,30000)
    assert selected_medium.benign_expected_safe_authorizations==Q(741,400)
    assert selected_strong.attack_harm==Q(393,2500)
    assert selected_strong.benign_expected_safe_authorizations==Q(171,100)

    time_game=TimedRewardGame(
        layers=(0,1,1,2,2),start=0,terminals=(3,4),
        edges=(
            TimedRewardEdge(0,1,Q(0),Q(0),"remain-intact"),
            TimedRewardEdge(0,2,Q(0),Q(0),"compromise-evaluator"),
            TimedRewardEdge(1,3,Q(2),Q(2),"intact-safe"),
            TimedRewardEdge(1,4,Q(0),Q(1),"intact-bad"),
            TimedRewardEdge(2,3,Q(2),Q(0),"corrupt-good-underreported"),
            TimedRewardEdge(2,4,Q(0),Q(3),"corrupt-bad-overreported"),
        )
    )
    time_cert=certify_relative_reward(time_game)
    assert not time_cert.relative_exact
    assert (time_cert.minimum_discrepancy,time_cert.maximum_discrepancy)==(
        Q(-2),Q(3)
    )
    assert time_cert.discrepancy_width==5
    assert time_cert.worst_proxy_selected_regret==2
    assert time_cert.sum_absolute_fundamental_periods>=5
    uncertainty=robust_transition_certify(
        time_game,(0,0,1,0,1,0),(0,0,3,0,3,0),
        maximum_allowed_regret=3,minimum_required_true_return=0
    )
    assert uncertainty.maximum_width==6
    assert uncertainty.maximum_proxy_regret==3
    assert uncertainty.guaranteed_proxy_gold_floor==0
    assert uncertainty.passes

    stochastic_game=evaluator_pomdp()
    nominal_gold=(Q(1),Q(-2),Q(1,4))
    stochastic_box=((Q(1),Q(2)),(Q(-3),Q(-2)),(Q(0),Q(1,4)))
    stochastic=stochastic_robust_certificate(
        stochastic_game,stochastic_box,nominal=nominal_gold,
    )
    assert stochastic.reward_interval_vertices_checked==8
    assert 0<stochastic.nominal_regret<=stochastic.robust_max_regret
    assert stochastic.robust_max_regret<=stochastic.robust_policy_discrepancy_width
    proxy_choice=optimize_stochastic_policy(
        stochastic_game,nominal_gold,objective="proxy_worst_gold"
    )
    gold_choice=optimize_stochastic_policy(
        stochastic_game,nominal_gold,objective="gold_max"
    )
    assert stochastic_game.actions[proxy_choice.policy.action]=="tamper"
    assert stochastic_game.actions[gold_choice.policy.action]!="tamper"
    path_outer=certify_relative_reward(
        time_expanded_support_graph(stochastic_game,nominal_gold)
    )
    assert path_outer.discrepancy_width>=stochastic.nominal_policy_discrepancy_width
    fair_noise=fair_martingale_noise_game(horizon=2)
    markov=expected_markov_coboundary(fair_noise,(Q(0),))
    fair_path=certify_relative_reward(
        time_expanded_support_graph(fair_noise,(Q(0),))
    )
    assert markov.valid
    assert markov.expected_gap_all_fixed_horizon_policies==0
    assert fair_path.discrepancy_width==4 and not fair_path.relative_exact

    benign=RewardPathGame(4,0,(2,3),(
        RewardTransition(0,1,Q(0),Q(1)),
        RewardTransition(1,2,Q(4),Q(5)),
        RewardTransition(1,3,Q(1),Q(2)),
        RewardTransition(0,2,Q(3),Q(5)),
        RewardTransition(0,3,Q(0),Q(2))))
    bad_boundary=RewardPathGame(3,0,(1,2),(
        RewardTransition(0,1,Q(2),Q(2)),
        RewardTransition(0,2,Q(0),Q(3))))
    assert boundary_relative_certificate(benign)["common_path_offset"]==2
    assert potential_if_exact(bad_boundary) is not None
    assert boundary_relative_certificate(bad_boundary) is None
    assert policy_rank_reversal(bad_boundary,(0,),(1,))

    root=Path(__file__).resolve().parents[1]
    return {
        "schema":"RHT-01.8",
        "claim_level":"exact algebraic identity and bounded finite world census",
        "model_training_or_external_reward_validation":False,
        "feedback_geometry":{
            "cycle_rank":cycle_rank(g),
            "nonzero_gold_cycle_period":str(periods[0][1]),
            "invisible_gold_fibre_width":str(width["maximum_width"]),
            "independent_max_circulation":str(independent_width),
            "exact_flow_width":str(flow_width.maximum_hidden_width),
            "exact_flow_augmentations":flow_width.cancelled_negative_cycles,
            "min_targeted_extra_cell_disclosures":cert["count"],
            "zero_tolerance_private_audit_count":epsilon_audit["count"],
        },
        "ugc_reward_hack":{
            "reachable_cell_records":len(reachable),
            "best_reported_score":str(exploit.selected_proxy_score),
            "worst_selected_true_utility":str(exploit.worst_selected_true_utility),
            "true_best":str(exploit.true_optimum),
            "worst_true_regret":str(exploit.worst_true_regret),
        },
        "guarded_ugc_selection":{
            "passed":guarded.passed,
            "selected_proxy_score":str(guarded.selected_proxy_score),
            "worst_case_true_regret":str(guarded.worst_case_regret),
            "minimum_gold_level":str(guarded.minimum_gold_level),
            "condition":"true gold belongs to protected frozen uncertainty set",
        },
        "simple_bipartite_game":{
            "vertices":simple_bipartite["constraint_game"].vertices,
            "edges":len(simple_bipartite["constraint_game"].edges),
            "unaltered_gold_observable_from_margins":True,
            "proxy_optimum":str(simple_bipartite["unguarded"].selected_proxy_score),
            "gold_at_proxy_optimum":str(simple_bipartite["unguarded"].worst_selected_true_utility),
            "gold_optimum":str(simple_bipartite["unguarded"].true_optimum),
            "gold_guarded_proxy_score":str(simple_bipartite["guarded"].selected_proxy_score),
            "gold_guarded_utility":str(simple_bipartite["guarded"].minimum_gold_level),
        },
        "higher_order_activation":{
            "three_map_cells":len(higher_cells),
            "rational_feedback_nullity":before_activation["rational_nullity"],
            "unit_capacity_integer_difference_rank":before_activation["bounded_integer_rank"],
            "unit_capacity_hidden_gold_width":str(before_activation["maximum_hidden_gold_width"]),
            "raised_second_cell_capacity":2,
            "raised_capacity_integer_difference_rank":after_activation["bounded_integer_rank"],
            "raised_capacity_hidden_gold_width":str(after_activation["maximum_hidden_gold_width"]),
            "additional_private_audits_at_capacity_two":higher_audit["count"],
        },
        "stochastic_reward_closure":{
            "hidden_ugc_worlds":3,
            "evaluator_integrity_states":2,
            "alarm_absorbing_state":True,
            "horizon":stochastic_game.horizon,
            "shared_gold_features":list(stochastic_game.gold_parameters),
            "gold_interval_vertices_checked":stochastic.reward_interval_vertices_checked,
            "nominal_theta":[str(x) for x in nominal_gold],
            "nominal_proxy_optimal_first_action":stochastic_game.actions[
                proxy_choice.policy.action
            ],
            "nominal_gold_optimal_first_action":stochastic_game.actions[
                gold_choice.policy.action
            ],
            "nominal_proxy_return":str(stochastic.nominal_proxy),
            "nominal_true_gold_at_proxy":str(stochastic.nominal_gold_at_proxy),
            "nominal_optimal_true_gold":str(stochastic.nominal_optimal_gold),
            "nominal_regret":str(stochastic.nominal_regret),
            "nominal_policy_discrepancy_width":str(
                stochastic.nominal_policy_discrepancy_width
            ),
            "robust_max_regret":str(stochastic.robust_max_regret),
            "robust_policy_discrepancy_width":str(
                stochastic.robust_policy_discrepancy_width
            ),
            "guaranteed_proxy_gold_floor":str(
                stochastic.guaranteed_proxy_gold_floor
            ),
            "worst_gold_parameter_vertex":[
                str(x) for x in stochastic.worst_gold_parameters
            ],
            "worst_gold_occupancy":[
                str(x) for x in stochastic.worst_gold_witness_occupancy
            ],
            "worst_proxy_occupancy":[
                str(x) for x in stochastic.worst_proxy_witness_occupancy
            ],
            "nominal_path_support_width":str(path_outer.discrepancy_width),
            "belief_dp_states_visited":stochastic.belief_dp_states_visited,
            "martingale_reward_null_control":{
                "conditional_expected_coboundary_valid":markov.valid,
                "expected_policy_discrepancy":str(
                    markov.expected_gap_all_fixed_horizon_policies
                ),
                "realized_pathwise_discrepancy_width":str(
                    fair_path.discrepancy_width
                ),
            },
            "scope":"fixed stochastic kernel and observable proxy; hidden mutable evaluator; time-shared interval gold features; mandatory horizon; no trained agent",
        },
        "time_expanded_relative_reward":{
            "vertices":len(time_game.layers),
            "transition_edges":len(time_game.edges),
            "completed_paths":len(time_game.complete_paths()),
            "nominal_relative_exact":time_cert.relative_exact,
            "nominal_discrepancy_width":str(time_cert.discrepancy_width),
            "nominal_proxy_selection_regret":str(
                time_cert.worst_proxy_selected_regret
            ),
            "nominal_fundamental_periods":[
                [i,str(p)] for i,p in time_cert.fundamental_periods
            ],
            "sum_absolute_fundamental_periods":str(
                time_cert.sum_absolute_fundamental_periods
            ),
            "uncertain_gold":{
                "licence":"independent [1,3] per good-outcome edge, fixed zero elsewhere",
                "maximum_discrepancy_width":str(uncertainty.maximum_width),
                "maximum_proxy_regret":str(uncertainty.maximum_proxy_regret),
                "gold_floor":str(uncertainty.guaranteed_proxy_gold_floor),
                "robust_certificate_passed":uncertainty.passes,
                "product_DP_states":uncertainty.states_visited,
                "gold_witness":[str(v) for v in uncertainty.witness_gold_rewards],
            },
            "scope":"all productive complete paths, true reward externally specified, deterministic support graph, no state probabilities",
        },
        "mutable_reward_evaluator":{
            "gold_worlds":3,
            "intact_false_accept":"1/5",
            "compromised_false_accept":"4/5",
            "tamper_success":"3/4",
            "two_call_intentional_tamper":{
                "adaptive_harm":str(weak_attack.max_harm),
                "best_fixed_harm":str(weak_attack.best_fixed_harm),
                "first_actor_action":weak_attack.first_action,
            },
            "two_call_incidental_safe_approval_drift":{
                "without_preprobe_attestation":str(safe_drift.max_harm),
                "with_three_quarters_compromised_detection":str(guarded_drift.max_harm),
            },
            "root_attestation":{
                "sufficient_detection_to_restore_baseline_hazard":str(
                    required_preprobe_detection_for_baseline_hazard(weak_stateful)
                ),
                "three_quarters_detection_worst_conditional_hazard":str(
                    worst_state_false_approval_rate(strong_stateful)
                ),
                "two_probe_hazard_upper_bound":str(
                    conditional_stateful_harm_bound(strong_stateful,2)
                ),
            },
            "two_sided_detector_selection":{
                "harm_cap_7_over_40":{
                    "chosen_compromised_detection":"1/2",
                    "chosen_intact_false_alarm":"1/20",
                    "optimal_attack_risk":str(selected_medium.attack_harm),
                    "benign_safe_authorizations":str(
                        selected_medium.benign_expected_safe_authorizations
                    ),
                },
                "harm_cap_4_over_25":{
                    "chosen_compromised_detection":"3/4",
                    "chosen_intact_false_alarm":"1/10",
                    "optimal_attack_risk":str(selected_strong.attack_harm),
                    "benign_safe_authorizations":str(
                        selected_strong.benign_expected_safe_authorizations
                    ),
                },
            },
            "scope":"fixed gold-reference world; hidden binary mutable judge integrity; conditional independent attestation and verdict rates; actor-visible alarms/verdicts; no actual model",
        },
        "sequential_reward_audit":{
            "worlds":3,
            "false_authorization_per_unsafe_attempt":"1/5",
            "perfect_safe_approval_two_attempts":{
                "adaptive_harm":str(adaptive_2.harmful_authorization_probability),
                "best_fixed_harm":str(adaptive_2.best_fixed_harm_probability),
                "adaptive_policy_first_action":adaptive_2.first_action,
            },
            "perfect_safe_approval_three_attempts":{
                "adaptive_harm":str(adaptive_3.harmful_authorization_probability),
                "best_fixed_harm":str(adaptive_3.best_fixed_harm_probability),
            },
            "five_attempts":{
                "history_conditional_bound":str(
                    conditional_harm_bound((Q(1,5),)*5)
                ),
                "marginal_only_bound":str(
                    marginal_harm_bound((Q(1,5),)*5)
                ),
            },
            "two_sided_retry_controls":{
                "licensed_false_reject":"1/10",
                "maximum_harm_7_over_50_choice":"forbid_repeated_action",
                "maximum_harm_7_over_50_risk":str(proposed.worst_adaptive_harm),
                "maximum_harm_7_over_50_expected_safe_approvals":str(
                    proposed.benign_expected_safe_authorizations
                ),
                "maximum_harm_13_over_100_choice":"lockout_after_rejection",
                "maximum_harm_13_over_100_risk":str(tighter.worst_adaptive_harm),
                "maximum_harm_13_over_100_expected_safe_approvals":str(
                    tighter.benign_expected_safe_authorizations
                ),
            },
            "assumptions":"fixed UGC latent world, licensed gold, history-conditional stationary independent veto noise, public approval and rejection, bounded retries",
        },
        "joint_audit_veto":{
            "three_worlds":{
                "maximum_authorized_unsafe_risk":str(joint.authorized_unsafe_risk),
                "minimum_benign_safe_authorization":str(joint.benign_safe_authorization),
                "pre_veto_public_leak_risk":str(joint.public_attack_risk_without_veto),
                "expected_query_cost":str(joint.expected_query_cost),
                "first_query_visibility":joint.policy.visibility,
                "trees_enumerated":joint.trees_enumerated,
                "gate_assignments_checked":joint.gate_assignments_checked,
            },
            "seven_world_zero_harm":{
                "max_sealed_queries":[f.max_queries for f in zero_harm_frontier],
                "benign_safe_authorization":[str(f.maximum_zero_harm_benign_liveness)
                                             for f in zero_harm_frontier],
                "posterior_collision":[str(f.posterior_collision_probability)
                                       for f in zero_harm_frontier],
                "private_leaf_sizes":[list(f.private_leaf_sizes)
                                      for f in zero_harm_frontier],
                "scope":"single attempted action, sealed queries, terminal audited veto, frozen gold",
            },
        },
        "adaptive_disclosure":{
            "ugc_vertices":9,
            "ugc_constraint_edges":14,
            "proxy_tied_reference_worlds":7,
            "initial_public_actor_risk":str(public_feedback["baseline"]),
            "three_fixed_interval_queries_actor_risk":str(public_feedback["fixed"]),
            "three_adaptive_interval_queries_actor_risk":str(public_feedback["adaptive"]),
            "one_sealed_auditor_query_with_action_control_risk":str(private_feedback["risk"]),
            "query_identity_sidechannel_three_worlds_before":str(hidden_risk["risk"]),
            "query_identity_sidechannel_three_worlds_after":str(leaked_risk["risk"]),
            "source_scope":"frozen proxy-maximizing roster with independently licensed world-specific gold",
        },
        "audit_optimizer":{
            "rank_one_weighted_private_audit_cells":list(primitive_audit.audited_cells),
            "rank_one_weighted_private_audit_cost":str(primitive_audit.cost),
            "multiway_cells":len(multimap_cells),
            "multiway_feedback_kernel_nullity":large_multimap.rational_nullity,
            "multiway_all_candidate_differences":7**len(multimap_cells),
            "multiway_DP_width":str(multilinear_width.maximum_width),
            "multiway_DP_states":multilinear_width.visited_states,
            "multiway_zero_tolerance_audit_cells":list(multim_audit.audited_cells),
            "multiway_zero_tolerance_audit_cost":str(multim_audit.cost),
            "multiway_obstruction_rounds":multim_audit.rounds,
            "multiway_tolerance_three_audit_count":loose_audit.count,
            "flat_UGC_reachable_private_audits":reachable_flat_audit.count,
            "frustrated_UGC_reachable_private_audits":reachable_bad_audit.count,
        },
        "ugc_reachable_fibres":{
            "full_capacity_box_hidden_width":"2",
            "frustrated_cycle_reachable_width":str(bad_reach["maximum_hidden_gold_width"]),
            "flat_cycle_reachable_width":str(flat_reach["maximum_hidden_gold_width"]),
            "frustrated_reachable_records":bad_reach["reachable_records"],
            "flat_reachable_records":flat_reach["reachable_records"],
        },
        "large_flow":{
            "edges":36,
            "cycle_rank":25,
            "maximum_hidden_gold_width":str(large_flow.maximum_hidden_width),
            "cancelled_negative_cycles":large_flow.cancelled_negative_cycles,
            "method":"exact negative-cycle cancellation with integer capacities",
        },
        "relative_gauge":{
            "safe_terminal_equal_potential":True,
            "acyclic_terminal_misranking":True,
        },
        "source_sha256":{
            p:hashlib.sha256((root/p).read_bytes()).hexdigest()
            for p in SOURCE_PATHS
        },
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,default=None)
    args=ap.parse_args()
    text=json.dumps(receipt(),sort_keys=True,indent=2)+"\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open("x",encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text,end="")


if __name__=="__main__":
    main()

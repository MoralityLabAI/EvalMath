"""Exact risk certificates, independent policy enumeration and audit minimisation."""
import random
from fractions import Fraction as Q

import pytest

from spiral_ln.evaluation_selection_risk import (
    AuditMachine, NullModel, QueryNode, adaptive_optimum, compress_contingency,
    contingency_histogram, dependent_five_percent_models, distinguish,
    exhaustive_two_round_optimum, fixed_fibres, fixed_optimum, full_information_risk,
    hidden_prepeek_risk, no_feedback_risk, one_step_profile, partition_refinement,
    policy_fibres, policy_risk, root_and_amendment_machine, run_events,
    selection_mass, state_bits, transcript, risk_projection, projection_risk,
    projection_output, projection_event, projection_query, projection_postquery_risk,
)


def risk_advantage_fixture():
    """Three tests calibrated at <=5%, with a two-query adaptive advantage."""
    return NullModel(
        (1, 1, 1, 1, 36),
        ((False, True, False, False, False),
         (False, False, True, True, False),
         (True, False, False, False, False)),
        ((1, 1, 0, 1, 0),
         (0, 0, 0, 1, 0),
         (1, 0, 0, 1, 0)),
    )


def test_correlated_and_disjoint_risks_have_identical_marginals():
    shared, disjoint = dependent_five_percent_models()
    assert shared.marginals() == disjoint.marginals() == (Q(1, 20), Q(1, 20))
    assert no_feedback_risk(shared) == no_feedback_risk(disjoint) == Q(1, 20)
    assert adaptive_optimum(shared, 1)["risk"] == Q(1, 20)
    assert adaptive_optimum(disjoint, 1)["risk"] == Q(1, 10)
    assert one_step_profile(shared, 0) != one_step_profile(disjoint, 0)
    assert full_information_risk(shared) == Q(1, 20)
    assert full_information_risk(disjoint) == Q(1, 10)
    assert exhaustive_two_round_optimum(shared) == Q(1, 20)
    assert exhaustive_two_round_optimum(disjoint) == Q(1, 10)


def test_exact_calibrated_adaptive_gain_reaches_union_limit():
    model = risk_advantage_fixture()
    assert model.marginals() == (Q(1, 40), Q(1, 20), Q(1, 40))
    assert no_feedback_risk(model) == Q(1, 20)
    assert full_information_risk(model) == Q(1, 10)
    fixed = fixed_optimum(model, 2)
    adaptive = adaptive_optimum(model, 2)
    assert fixed["risk"] == Q(3, 40)
    assert adaptive["risk"] == Q(1, 10)
    assert fixed["schedules_checked"] == 10
    assert exhaustive_two_round_optimum(model) == Q(1, 10)
    assert policy_risk(model, adaptive["tree"]) == adaptive["risk"]
    assert len(policy_fibres(model, adaptive["tree"])) >= 3
    assert selection_mass(model, tuple(range(len(model.weights)))) == 2


def test_exact_hidden_peeking_formula():
    assert hidden_prepeek_risk(1, Q(1, 20)) == Q(1, 20)
    answer = hidden_prepeek_risk(20, Q(1, 20))
    assert answer == 1 - Q(19, 20) ** 20
    assert Q(64, 100) < answer < Q(65, 100)
    assert hidden_prepeek_risk(20, Q(0)) == 0
    assert hidden_prepeek_risk(20, Q(1)) == 1


def test_exhaustive_two_rounds_matches_independent_policy_enumerator():
    rng = random.Random(7319)
    for n in range(2, 7):
        for _ in range(60):
            events = tuple(tuple(bool(rng.getrandbits(1)) for _ in range(n))
                           for _ in range(3))
            queries = tuple(tuple(rng.randrange(3) for _ in range(n))
                            for _ in range(3))
            model = NullModel(tuple(rng.randrange(1, 8) for _ in range(n)),
                              events, queries)
            exact = adaptive_optimum(model, 2)["risk"]
            oracle = exhaustive_two_round_optimum(model)
            fixed = fixed_optimum(model, 2)["risk"]
            assert exact == oracle
            assert no_feedback_risk(model) <= fixed <= exact <= full_information_risk(model)
            assert adaptive_optimum(model, 0)["risk"] == no_feedback_risk(model)


def test_contingency_histogram_is_continuation_sufficient_for_fixed_contract():
    rng = random.Random(821)
    for n in range(2, 11):
        for _ in range(24):
            model = NullModel(
                tuple(rng.randrange(1, 6) for _ in range(n)),
                tuple(tuple(bool(rng.randrange(2)) for _ in range(n)) for _ in range(2)),
                tuple(tuple(rng.randrange(2) for _ in range(n)) for _ in range(2)),
            )
            small = compress_contingency(model)
            assert small.total == model.total
            assert small.marginals() == model.marginals()
            assert contingency_histogram(small) == contingency_histogram(model)
            for k in range(3):
                assert adaptive_optimum(small, k)["risk"] == adaptive_optimum(model, k)["risk"]
                assert fixed_optimum(small, k)["risk"] == fixed_optimum(model, k)["risk"]
    model = NullModel((1, 2, 3, 4), ((False, False, True, True),), ((0, 0, 1, 1),))
    assert len(compress_contingency(model).weights) == 2


def test_every_fibre_partition_keeps_exact_null_worlds():
    model = risk_advantage_fixture()
    for schedule in ((), (0,), (1, 1), (0, 2)):
        groups = fixed_fibres(model, schedule)
        assert sorted(i for group in groups for i in group) == list(range(5))
    tree = adaptive_optimum(model, 2)["tree"]
    for i in range(5):
        assert transcript(model, tree, i) in policy_fibres(model, tree)


def test_three_root_amendment_machine_has_24_minimal_states():
    for roots in range(1, 5):
        machine = root_and_amendment_machine(roots)
        classes = partition_refinement(machine)
        assert len(classes) == 3 * (1 << roots)
        assert all(len(cls) == 1 for cls in classes)
        assert state_bits(len(classes)) == roots + 2
    machine = root_and_amendment_machine(3)
    # Every state pair must have an explicit distinguishing continuation.
    for a in range(24):
        for b in range(a + 1, 24):
            suffix = distinguish(machine, a, b)
            assert suffix is not None
            assert run_events(machine, a, suffix)[1] != run_events(machine, b, suffix)[1]


def test_current_GO_and_eligibility_do_not_preserve_future_amendment():
    machine = root_and_amendment_machine(3)
    pre = run_events(machine, 0, ("GRANT_0",))[0]
    seen = run_events(machine, 0, ("GRANT_0", "VIEW"))[0]
    assert machine.outputs[pre] == machine.outputs[seen] == ("GO", "eligible")
    assert distinguish(machine, pre, seen) == ("AMEND",)
    assert run_events(machine, pre, ("AMEND",))[1] == ("GO", "eligible")
    assert run_events(machine, seen, ("AMEND",))[1] == ("GO", "exploratory")
    before = run_events(machine, 0, ("GRANT_0", "AMEND", "VIEW"))[1]
    after = run_events(machine, 0, ("GRANT_0", "VIEW", "AMEND"))[1]
    assert before == ("GO", "eligible") and after == ("GO", "exploratory")


def test_revocable_roots_require_identity_to_survive_rollback():
    machine = root_and_amendment_machine(3)
    a = run_events(machine, 0, ("GRANT_0",))[0]
    b = run_events(machine, 0, ("GRANT_1",))[0]
    assert machine.outputs[a] == machine.outputs[b] == ("GO", "eligible")
    assert distinguish(machine, a, b) is not None
    assert run_events(machine, a, ("REVOKE_0",))[1][0] == "STOP"
    assert run_events(machine, b, ("REVOKE_0",))[1][0] == "GO"


def test_machine_minimizer_can_merge_validly_redundant_states():
    machine = AuditMachine(("flip",), (("good",), ("good",), ("bad",)),
                           ((2,), (2,), (2,)))
    assert partition_refinement(machine) == ((0, 1), (2,))
    assert distinguish(machine, 0, 1) is None
    assert distinguish(machine, 0, 2) == ()


def test_malformed_models_and_policy_are_rejected():
    for args in (
        ((), ((True,),), ((0,),)),
        ((0,), ((True,),), ((0,),)),
        ((1,), (), ((0,),)),
        ((1,), ((1,),), ((0,),)),
        ((1,), ((True,),), ()),
        ((1,), ((True,),), ((False,),)),
        ((1,), ((True,),), ((0, 1),)),
    ):
        with pytest.raises(ValueError):
            NullModel(*args)
    m = NullModel((1, 1), ((True, False),), ((0, 1),))
    for bad in (-1, True, 1.5):
        with pytest.raises(ValueError):
            adaptive_optimum(m, bad)
        with pytest.raises(ValueError):
            fixed_optimum(m, bad)
    with pytest.raises(ValueError):
        policy_risk(m, QueryNode(0, ((0, QueryNode()),)))
    with pytest.raises(ValueError):
        transcript(m, QueryNode(7, ((0, QueryNode()),)), 0)
    with pytest.raises(ValueError):
        root_and_amendment_machine(0)
    with pytest.raises(ValueError):
        run_events(root_and_amendment_machine(1), 0, ("REWRITE_HISTORY",))
    with pytest.raises(ValueError):
        hidden_prepeek_risk(0, Q(1, 20))
    with pytest.raises(ValueError):
        state_bits(0)


def test_joint_projection_preserves_conditional_risk_and_amendment_status():
    machine = root_and_amendment_machine(3)
    active = run_events(machine, 0, ("GRANT_0",))[0]
    for null in (*dependent_five_percent_models(), risk_advantage_fixture()):
        original = risk_projection(null, machine, active)
        compressed = risk_projection(compress_contingency(null), machine, active)
        assert original == compressed
        assert projection_risk(original) == no_feedback_risk(null)
        assert projection_output(original, machine) == (("GO", "eligible"), no_feedback_risk(null))
        for q, query in enumerate(null.queries):
            responses = projection_query(original, machine, q)
            assert set(responses) == set(query)
            total = sum(null.weights)
            weighted_risk = sum(
                sum(null.weights[i] for i, value in enumerate(query) if value == response)
                * projection_risk(state)
                for response, state in responses.items()
            ) / total
            assert weighted_risk == projection_postquery_risk(original, q)
            for response, state in responses.items():
                assert projection_output(state, machine)[0] == ("GO", "eligible")
                amendment = projection_event(state, machine, "AMEND")
                assert projection_output(amendment, machine)[0] == ("GO", "exploratory")
                assert projection_risk(amendment) == projection_risk(state)
                for second in range(len(null.queries)):
                    deeper = projection_query(state, machine, second)
                    assert all(projection_output(x, machine)[0][0] == "GO" for x in deeper.values())
    first = risk_projection(dependent_five_percent_models()[0], machine, active)
    # A prospective amendment before looking preserves eligibility under the contract.
    prior_amend = projection_event(first, machine, "AMEND")
    assert all(projection_output(x, machine)[0][1] == "eligible"
               for x in projection_query(prior_amend, machine, 0).values())


def test_invalid_projection_query_and_machine_rejected():
    machine = root_and_amendment_machine(1)
    p = risk_projection(dependent_five_percent_models()[0], machine)
    with pytest.raises(ValueError):
        projection_query(p, machine, 1)
    with pytest.raises(ValueError):
        projection_postquery_risk(p, -1)
    with pytest.raises(ValueError):
        projection_event(p, machine, "FAKE")

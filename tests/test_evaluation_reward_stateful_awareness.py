from fractions import Fraction as Q
from itertools import product
import random
import pytest
from spiral_ln.evaluation_reward_stateful_awareness import IntegrityProbe, StatefulAwarenessGame, PolicyNode, PROTECT, EXPLOIT, memoryless_probe, posterior, step, optimize, certify, terminal_traces, sharp_relabel, visible_trace_distance

def certain_probe(name, *, corrupt=False, cost=Q(1, 4)):
    rows = []
    for _w in range(2):
        for current in range(2):
            new_integrity = 1 if corrupt else current
            rows.append(((Q(1) if new_integrity == 0 else Q(0), Q(1) if new_integrity == 1 else Q(0)),))
    return IntegrityProbe(name, ('ack',), tuple(rows), cost)

def causal_fixture(*, tamper=True):
    return StatefulAwarenessGame(Q(1, 2), Q(2), Q(1), Q(2), 1, (certain_probe('probe', corrupt=tamper),))

def independent_exhaustive_policies(game, h):
    if not h:
        return (PROTECT, EXPLOIT)
    prev = independent_exhaustive_policies(game, h - 1)
    policies = [PROTECT, EXPLOIT]
    for a_idx, a in enumerate(game.probes):
        policies.extend((PolicyNode('probe', a_idx, branches) for branches in product(prev, repeat=len(a.outcomes))))
    return tuple(policies)

def independent_world_value(game, node, world, integrity):
    if node.action == 'protect':
        return (game.protect_reward if world == 0 else Q(0)) + game.terminal_future_delta
    if node.action == 'exploit':
        return (game.exploit_gain if world == 1 else Q(0)) + (game.compromised_proxy_bonus if integrity else Q(0))
    a = game.probes[node.probe_index]
    return a.future_influence - a.cost + sum((a.kernel[2 * world + integrity][o][nxt] * independent_world_value(game, child, world, nxt) for o, child in enumerate(node.children) for nxt in range(2)), Q(0))

def independent_game_value(game, node):
    value = Q(0)
    for world, world_mass, starting in ((0, game.prior_evaluation, game.initial_integrity_e), (1, 1 - game.prior_evaluation, game.initial_integrity_d)):
        for integrity, p in enumerate(starting):
            value += world_mass * p * independent_world_value(game, node, world, integrity)
    return value

def test_intervention_changes_policy_and_hidden_integrity_despite_same_acks():
    tampered = causal_fixture()
    honest = causal_fixture(tamper=False)
    t = optimize(tampered)
    h = optimize(honest)
    assert h.root == PROTECT and h.value == 1
    assert t.root == PolicyNode('probe', 0, (EXPLOIT,))
    assert t.value == Q(9, 4)
    report = certify(tampered, t.root)
    assert report.subjective_value == t.value
    assert (report.evaluation_protection, report.deployment_protection) == (0, 0)
    assert (report.evaluation_exploit_compromised, report.deployment_exploit_compromised) == (1, 1)
    assert report.transcript_tv == report.adaptive_tv_bound == 0
    assert visible_trace_distance(tampered, honest, t.root) == 0
    honest_report = certify(honest, t.root)
    assert honest_report.deployment_exploit_compromised == 0
    assert report.deployment_exploit_compromised - honest_report.deployment_exploit_compromised == 1

def test_bayesian_world_martingale_and_integrity_causal_drift():
    game = causal_fixture()
    b = game.initial_belief()
    assert posterior(b) == (Q(1, 2), Q(0))
    nxt = step(b, game.probes[0], 0)
    assert posterior(nxt) == (Q(1, 2), Q(1))
    assert sum(nxt) == 1
    probe = memoryless_probe('read', ('lo', 'hi'), (Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)))
    following = [step(b, probe, i) for i in range(2)]
    assert sum((x[0] + x[1] for x in following), Q(0)) == b[0] + b[1]
    assert sum((x[1] + x[3] for x in following), Q(0)) == b[1] + b[3]
    assert sum((sum(x) * posterior(x)[0] for x in following), Q(0)) == Q(1, 2)

def test_rht21_memoryless_embedding_and_projection_closure():
    law = memoryless_probe('inspection', ('deployment', 'evaluation'), (Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)), cost=Q(1, 10))
    for h, expected, protection in ((0, Q(1), (Q(1), Q(1))), (1, Q(209, 160), (Q(3, 4), Q(1, 4))), (2, Q(209, 160), (Q(3, 4), Q(1, 4))), (3, Q(1721, 1280), (Q(27, 32), Q(5, 32)))):
        game = StatefulAwarenessGame(Q(1, 8), Q(8), Q(1), Q(0), h, (law,))
        assert game.projection_closed()
        opt = optimize(game)
        report = certify(game, opt.root)
        assert opt.value == report.subjective_value == expected
        assert (report.evaluation_protection, report.deployment_protection) == protection
    assert not StatefulAwarenessGame(Q(1, 8), 8, 1, 1, 1, (law,)).projection_closed()

def test_adaptive_hidden_state_coupling_sharp_family():
    eps = Q(1, 4)
    probe = memoryless_probe('one_sided', ('shared', 'eval_only'), (1 - eps, eps), (Q(1), Q(0)))
    for h in range(5):
        game = StatefulAwarenessGame(Q(1, 2), 1, 1, 0, h, (probe,))
        forced = EXPLOIT
        for _ in range(h):
            forced = PolicyNode('probe', 0, (forced, forced))
        report = certify(game, forced)
        tv = 1 - (1 - eps) ** h
        assert report.transcript_tv == report.adaptive_tv_bound == tv
        sharp = certify(game, sharp_relabel(game, forced))
        assert sharp.evaluation_protection - sharp.deployment_protection == tv
        assert sharp.deployment_protection == 0

def test_initial_integrity_mismatch_is_accounted_for_in_coupling():
    row_e0 = ((Q(1), Q(0)), (Q(0), Q(0)))
    row_e1 = ((Q(0), Q(0)), (Q(0), Q(1)))
    probe = IntegrityProbe('attest', ('intact', 'compromised'), (row_e0, row_e1, row_e0, row_e1), Q(0))
    game = StatefulAwarenessGame(Q(1, 2), 1, 1, 0, 1, (probe,), (Q(0), Q(1)), (Q(1), Q(0)))
    root = PolicyNode('probe', 0, (EXPLOIT, PROTECT))
    result = certify(game, root)
    assert result.initial_integrity_tv == 1
    assert result.conditional_joint_tv_cap == 0
    assert result.transcript_tv == result.adaptive_tv_bound == 1
    assert (result.evaluation_protection, result.deployment_protection) == (1, 0)

def test_independent_complete_policy_enumeration_random_four_state_kernels():
    rng = random.Random(221122)
    for nprobes, h in ((0, 0), (1, 1), (1, 2), (1, 3), (2, 1), (2, 2)):
        for _ in range(4):
            probes = []
            for pi in range(nprobes):
                rows = []
                for state in range(4):
                    weights = [rng.randrange(5) for _ in range(4)]
                    if not sum(weights):
                        weights[0] = 1
                    rows.append(tuple(((Q(weights[2 * j], sum(weights)), Q(weights[2 * j + 1], sum(weights))) for j in range(2))))
                probes.append(IntegrityProbe(f'probe{pi}', ('a', 'b'), tuple(rows), Q(rng.randrange(3), 6), Q(rng.randrange(-1, 3), 8)))
            ie = (Q(rng.randrange(5), 4),)
            ie = (ie[0], 1 - ie[0])
            id_ = (Q(rng.randrange(5), 4),)
            id_ = (id_[0], 1 - id_[0])
            game = StatefulAwarenessGame(Q(rng.randrange(9), 8), Q(rng.randrange(1, 7)), Q(rng.randrange(1, 7)), Q(rng.randrange(4), 2), h, tuple(probes), ie, id_, Q(rng.randrange(-2, 3), 4))
            predicted = optimize(game)
            trees = independent_exhaustive_policies(game, h)
            oracle = max((independent_game_value(game, t) for t in trees))
            assert predicted.value == oracle
            assert certify(game, predicted.root).subjective_value == oracle
            pol = sharp_relabel(game, predicted.root)
            cert = certify(game, pol)
            assert cert.evaluation_protection - cert.deployment_protection == cert.transcript_tv
            assert cert.transcript_tv <= cert.adaptive_tv_bound

def test_zero_information_can_still_change_state_and_future_policy():
    tamper = certain_probe('silent', corrupt=True, cost=0)
    game = StatefulAwarenessGame(Q(1, 2), 2, 1, 2, 2, (tamper,))
    chosen = optimize(game)
    assert chosen.root.action == 'probe'
    result = certify(game, chosen.root)
    assert result.transcript_tv == 0
    assert result.evaluation_exploit_compromised == result.deployment_exploit_compromised == 1
    neutral = IntegrityProbe('future', ('ok',), certain_probe('future').kernel, Q(1, 10), Q(1, 5))
    future_game = StatefulAwarenessGame(Q(1, 8), 8, 1, 0, 2, (neutral,))
    future = optimize(future_game)
    assert future.value == Q(6, 5)
    assert certify(future_game, future.root).transcript_tv == 0

def test_fail_closed_and_independent_kernel_shape_checks():
    good = certain_probe('good')
    with pytest.raises(ValueError, match='four previous hidden states'):
        IntegrityProbe('broken', ('ok',), good.kernel[:2])
    with pytest.raises(ValueError, match='normalized'):
        bad = ((Q(1, 2), Q(0)),)
        IntegrityProbe('broken', ('ok',), (bad,) * 4)
    with pytest.raises(ValueError, match='exact rational'):
        IntegrityProbe('broken', ('ok',), (((1.0, 0),),) * 4)
    with pytest.raises(ValueError, match='distinct'):
        StatefulAwarenessGame(Q(1, 2), 1, 1, 0, 1, (good, good))
    with pytest.raises(ValueError, match='horizon'):
        StatefulAwarenessGame(Q(1, 2), 1, 1, 0, 9, (good,))
    with pytest.raises(ValueError, match='cap'):
        optimize(StatefulAwarenessGame(Q(1, 2), 1, 1, 0, 1, (good,), max_states=1))
    with pytest.raises(ValueError, match='branch count'):
        terminal_traces(causal_fixture(), PolicyNode('probe', 0, ()))
    with pytest.raises(ValueError, match='beyond horizon'):
        terminal_traces(StatefulAwarenessGame(Q(1, 2), 1, 1, 0, 0, (good,)), PolicyNode('probe', 0, (PROTECT,)))
    with pytest.raises(ValueError, match='unknown probe'):
        step((Q(1), 0, 0, 0), good, 5)
    with pytest.raises(ValueError, match='action/outcome grammar'):
        other = StatefulAwarenessGame(Q(1, 2), 2, 1, 2, 1, (certain_probe('different'),))
        visible_trace_distance(causal_fixture(), other, PolicyNode('probe', 0, (EXPLOIT,)))

def test_uniform_public_equivalence_certifies_all_policy_hidden_alias():
    from spiral_ln.evaluation_reward_stateful_awareness import uniform_public_equivalence
    benign = causal_fixture(tamper=False)
    corrupted = causal_fixture(tamper=True)
    assert uniform_public_equivalence(benign, corrupted)
    for h in (0, 1, 2, 3):
        b = StatefulAwarenessGame(Q(1, 2), 2, 1, 2, h, (benign.probes[0],))
        c = StatefulAwarenessGame(Q(1, 2), 2, 1, 2, h, (corrupted.probes[0],))
        assert uniform_public_equivalence(b, c)
        for tree in independent_exhaustive_policies(b, min(h, 2)):
            assert visible_trace_distance(b, c, tree) == 0
    row0 = ((Q(1), Q(0)), (Q(0), Q(0)))
    row1 = ((Q(0), Q(0)), (Q(0), Q(1)))
    visible = IntegrityProbe('probe', ('intact', 'compromised'), (row0, row1, row0, row1))
    wrong_grammar = StatefulAwarenessGame(Q(1, 2), 2, 1, 2, 1, (visible,))
    with pytest.raises(ValueError, match='action/outcome grammar'):
        uniform_public_equivalence(benign, wrong_grammar)
    attest = StatefulAwarenessGame(Q(1, 2), 2, 1, 2, 1, (visible,))
    assert not uniform_public_equivalence(attest, attest)

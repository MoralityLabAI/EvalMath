"""MIT-12: generators, exact labels, sham, certificate soundness, parameter counts, rollout consistency."""
import sys
from fractions import Fraction as F
from pathlib import Path
from random import Random
from collections import Counter
import pytest

ROOT = Path(__file__).resolve().parents[1]
GYM = ROOT / 'gyms' / 'MathematicalInstrumentTransfer'
sys.path.insert(0, str(GYM))
sys.path.insert(0, str(ROOT / 'src'))
import compact_controller as cc
from spiral_ln.evaluation_adaptive_precision import Env, Solver
from spiral_ln.evaluation_depth_precision import groups_of

SEEDS = {'random': 100003, 'palette': 100007, 'higher': 100011}


def env_sig(env):
    return (env.w, env.qs, env.budget)


@pytest.mark.parametrize('family', cc.FAMILIES)
def test_generator_determinism(family):
    e1, m1 = cc.make_root(family, SEEDS[family])
    e2, m2 = cc.make_root(family, SEEDS[family])
    e3, _ = cc.make_root(family, SEEDS[family] + 2)
    assert env_sig(e1) == env_sig(e2) and m1 == m2
    assert env_sig(e1) != env_sig(e3)


def test_split_ranges_disjoint():
    seeds = {s: {x for _, x in cc.root_list(s, 150)} for s in cc.SPLITS}
    assert not (seeds['train'] & seeds['dev']) and not (seeds['dev'] & seeds['eval']) and not (seeds['train'] & seeds['eval'])
    assert len(cc.root_list('eval', 60)) == 180


def small_env(seed):
    r = Random(seed)
    n, budget = 6, 4
    w = [r.choice((1, 2)) for _ in range(n)]
    qs = []
    for cost, ny in ((1, 2), (2, 3)):
        types = [cc._composition(r, 6, ny) for _ in range(3)]
        pick = [r.randrange(3) for _ in range(n)]
        qs.append((cost, [[types[pick[i]][y] for i in range(n)] for y in range(ny)]))
    return Env(w, qs, budget)


@pytest.mark.parametrize('seed', [1, 2, 3])
def test_labels_match_solver_qvalues(seed):
    env = small_env(seed)
    orc = cc.Oracle(env)
    sol = Solver(env)
    checked = 0
    for st in cc.enumerate_states(orc, Random(seed))[:12]:
        r = orc.rec(st)
        # recover a strategy-coordinate state: the quotient state equals Solver's state only at the root
        if st[2] != env.budget:
            continue
        groups, live = groups_of(env, env.w, 0, (1 << len(env.qs)) - 1)
        qv = sol.qvalues(env.w, 0, (1 << len(env.qs)) - 1, env.budget)
        for a, v in zip(r['actions'], r['q']):
            key = ('g', min(groups[a[1]][3])) if a[0] == 'g' else a
            assert qv[key] == v
            checked += 1
        assert max(qv.values()) == r['best']
    assert checked > 0


def test_labels_match_solver_after_a_query():
    env = small_env(7)
    orc, sol = cc.Oracle(env), Solver(env)
    ctx = orc.ctx
    root = ctx.root_state()
    imm, kids = cc.step(ctx, root, ('q', 0))
    # strategy-coordinate counterpart: posterior after outcome y of instrument 0
    for y, (w, child) in zip(range(len(env.qs[0][1])), kids):
        m = tuple(x * env.qs[0][1][y][i] for i, x in enumerate(env.w))
        total = sum(m)
        assert total == w
        full = (1 << len(env.qs)) - 1
        avail = full & ~1
        b = env.budget - env.qs[0][0]
        groups, live = groups_of(env, m, 0, avail)
        r = orc.rec(child)
        qv = sol.qvalues(m, 0, avail, b)
        for a, v in zip(r['actions'], r['q']):
            key = ('g', min(groups[a[1]][3])) if a[0] == 'g' else a
            assert qv[key] == v


def test_action_order_matches_planner():
    for fam in cc.FAMILIES:
        env, _ = cc.make_root(fam, SEEDS[fam])
        orc = cc.Oracle(env)
        for st in cc.enumerate_states(orc, Random(1), 20):
            r = orc.rec(st)
            assert len(r['actions']) == len(r['q']) == len(r['lb2']) == len(r['ub2']) == len(r['lb3'])
            for lo, hi, q in zip(r['lb2'], r['ub2'], r['q']):
                assert lo <= q <= hi
            assert max(r['lb3']) <= r['best'] <= max(r['ub2'])


def test_sham_preserves_masses_and_marginals():
    changed = 0
    for fam in cc.FAMILIES:
        env, _ = cc.make_root(fam, SEEDS[fam])
        orc = cc.Oracle(env)
        for st in cc.enumerate_states(orc, Random(2), 30):
            fs = cc.to_float(st)
            st2, gmap, ch = cc.shuffle_state(fs)
            changed += ch
            gs, live, b = fs
            gs2 = st2[0]
            assert st2[1] == live and st2[2] == b
            assert sum(n for _, _, n in gs) == sum(n for _, _, n in gs2)
            assert Counter(m for m, _, n in gs for _ in range(n)) == Counter(m for m, _, n in gs2 for _ in range(n))
            for pos in range(len(live)):
                a = Counter((m, col) for m, s, n in gs for col in [s[pos]] for _ in range(n))
                c = Counter((m, col) for m, s, n in gs2 for col in [s[pos]] for _ in range(n))
                assert a == c                       # per-instrument (mass, column) multiset preserved
            assert len(gmap) == len(gs) and all(0 <= g < len(gs2) for g in gmap)
    assert changed > 0


def test_certificate_never_accepts_suboptimal_at_eta_zero():
    n = 0
    for fam in cc.FAMILIES:
        env, _ = cc.make_root(fam, SEEDS[fam])
        orc = cc.Oracle(env)
        src = cc.Source(env, orc)
        for st in cc.enumerate_states(orc, Random(3), 40):
            r = orc.rec(st)
            for ai in range(len(r['actions'])):
                if cc.certified(src, st, ai, F(0)):
                    assert r['q'][ai] == r['best']
                    n += 1
                if cc.certified(src, st, ai, F(1, 100)):
                    assert r['best'] - r['q'][ai] <= F(1, 100)
    assert n > 0


def test_play_value_consistency():
    for fam in cc.FAMILIES:
        env, _ = cc.make_root(fam, SEEDS[fam])
        orc = cc.Oracle(env)
        src = cc.Source(env, orc)
        root = orc.ctx.root_state()
        r = orc.rec(root)
        v, _ = cc.play(src, cc.make_decider(src, dict(kind='base', name='exact', eta=None)))
        assert v == r['best']
        for ai in range(len(r['actions'])):
            exact = cc.make_decider(src, dict(kind='base', name='exact', eta=None))

            def decide(st, ai=ai, exact=exact):
                alist, a, info = exact(st)
                return (alist, ai, info) if st == root else (alist, a, info)
            v2, _ = cc.play(src, decide)
            assert v2 == r['q'][ai]


def test_certified_execution_is_exact_optimal_at_eta_zero():
    for fam in cc.FAMILIES:
        env, _ = cc.make_root(fam, SEEDS[fam])
        orc = cc.Oracle(env)
        src = cc.Source(env, orc)
        opt = orc.rec(orc.ctx.root_state())['best']
        for name in ('direct', 'greedy'):
            v, nodes = cc.play(src, cc.make_decider(src, dict(kind='base', name=name, eta=F(0))))
            assert v == opt
            s = cc.summarize(v, nodes, orc)
            assert s['exec_opt'] == 1.0 and 0.0 <= s['accept'] <= 1.0


def test_parameter_counts():
    pc = cc.param_counts()
    assert pc['trm'] == pc['trm_sham'] == 3153
    assert pc['rel'] == pc['rel_sham'] == 2705
    assert pc['scalar'] == 2321 and pc['router'] == 548
    assert pc['rel'] / 2 <= pc['trm'] <= 2 * pc['rel']
    torch = pytest.importorskip('torch')
    assert cc.nparams(cc.TRM(2)) == cc.nparams(cc.TRM(4)) == pc['trm']
    assert cc.nparams(cc.Router()) == pc['router']
    import numpy as np
    assert cc.nparams(cc.MLPRanker(cc.NSCAL + cc.NREL, np.zeros(22), np.ones(22))) == pc['rel']
    assert cc.nparams(cc.MLPRanker(cc.NSCAL, np.zeros(14), np.ones(14))) == pc['scalar']


def test_feature_shapes_and_forward():
    torch = pytest.importorskip('torch')
    import numpy as np
    env, _ = cc.make_root('higher', SEEDS['higher'])
    orc = cc.Oracle(env)
    st = cc.enumerate_states(orc, Random(4), 5)[0]
    f = cc.state_features(orc.ctx, st)
    a = len(f['actions'])
    assert np.array(f['scalar']).shape == (a, cc.NSCAL) and np.array(f['rel']).shape == (a, cc.NREL)
    assert np.array(f['rel_sham']).shape == (a, cc.NREL)
    S, A = f['tok']
    assert np.array(S).shape[1] == cc.NS and np.array(A).shape == (a, cc.NA)
    net = cc.TRM(2)
    out = net(torch.tensor([S], dtype=torch.float32), torch.ones(1, len(S), dtype=torch.bool),
              torch.tensor([A], dtype=torch.float32), torch.ones(1, a, dtype=torch.bool))
    assert out.shape == (1, a)

"""MIT-09/10/11: certified precision, decision certificates, depth-precision planner."""
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'gyms' / 'MathematicalInstrumentTransfer'))

from spiral_ln.evaluation_adaptive_precision import (Env, Solver, LEVELS, quantize, envelope, tv, box,
    deployed_value, instrument_errors, global_certificate, run_controller, bellman_oracle, enumerate_oracle)
from spiral_ln.evaluation_decision_certificate import policy_certificate, posterior_tv_bound, online_controller
from spiral_ln.evaluation_depth_precision import Planner, groups_of, merge_classes, configuration
from spiral_ln.evaluation_noisy_instrument_quotient import Quotient, approximate_policy_value


def vec(r, m, den):
    cuts = sorted(r.randint(0, den) for _ in range(m - 1))
    pts = [0] + cuts + [den]
    return tuple(F(pts[i + 1] - pts[i], den) for i in range(m))


def root(seed, n=(4, 6), k=(2, 3), B=(2, 4)):
    r = Random(seed)
    nn, kk, bb = r.randint(*n), r.randint(*k), r.randint(*B)
    qs = []
    for _ in range(kk):
        m = r.choice((2, 2, 3))
        cols = [vec(r, m, r.choice((7, 11, 13, 97))) for _ in range(nn)]
        qs.append((r.choice((1, 1, 2)), [[c[y] for c in cols] for y in range(m)]))
    return Env([r.randint(1, 5) for _ in range(nn)], qs, bb)


def test_quantize_exact_rounding_lemma_and_envelope():
    r = Random(1)
    for _ in range(400):
        m = r.randint(2, 6)
        p = vec(r, m, r.choice((3, 7, 97, 1009)))
        for bits in LEVELS[:-1]:
            q = quantize(p, bits)
            u = F(1, 1 << bits)
            assert sum(q) == 1 and all((x * (1 << bits)).denominator == 1 for x in q)
            assert all(abs(a - b) < u for a, b in zip(p, q))
            # raised entries have positive fractional part
            for a, b in zip(p, q):
                if b * (1 << bits) > (a * (1 << bits)).__floor__():
                    assert (a * (1 << bits)).denominator != 1
            e = envelope(q, bits)
            assert tv(p, q) <= e <= F(m // 2) * u
    assert quantize((F(1, 3), F(2, 3)), 1) == (F(1, 2), F(1, 2))
    assert quantize((F(1), F(0)), 1) == (F(1), F(0))
    assert envelope((F(1), F(0)), None) == 0


def test_envelope_is_tight_for_some_preimage():
    # q = (1/2, 1/2) at 1 bit: p = (1/2 + t, 1/2 - t), t < 1/2, rounds to q iff fractional rule holds.
    q = (F(1, 2), F(1, 2))
    assert envelope(q, 1) == F(1, 2)
    p = (F(49, 100), F(51, 100))
    assert quantize(p, 1) == q and tv(p, q) == F(1, 100)


def test_solver_matches_quotient_and_reference_executor():
    for s in range(16):
        e = root(100 + s)
        assert Solver(e).optimum() == Quotient(e.w, e.qs, e.budget).solve()
        for prof in [(1,) * len(e.qs), (2,) * len(e.qs), (8,) * len(e.qs)]:
            a = e.quantized(prof)
            vpi, vt, va, _ = deployed_value(e, a)
            assert (vpi, va) == approximate_policy_value(e.w, e.qs, a.w, a.qs, e.budget)


def test_certificates_sound_and_ordered():
    for s in range(12):
        e = root(200 + s)
        for prof in product((1, 2, 4), repeat=len(e.qs)):
            a = e.quantized(prof)
            vpi, vt, _, _ = deployed_value(e, a)
            pri, retro = instrument_errors(e, prof)
            g, gr = global_certificate(a, pri)[1], global_certificate(a, retro)[1]
            pc = policy_certificate(e, prof)
            assert vt - vpi <= gr <= g
            assert vt - vpi <= pc['certificate'] <= g
            assert pc['certificate'] == min(pc['global_bound'], pc['stepwise'])


def test_full_precision_certificates_are_zero():
    e = root(300)
    full = (None,) * len(e.qs)
    assert policy_certificate(e, full)['certificate'] == 0
    assert global_certificate(e, instrument_errors(e, full)[0]) == (0, 0)


def test_bellman_oracle_matches_enumeration():
    for s in range(6):
        e = root(400 + s)
        table = {}
        for prof in product(LEVELS, repeat=len(e.qs)):
            a = e.quantized(prof)
            table[prof] = global_certificate(a, instrument_errors(e, prof)[0])[1]
        for eta in (F(1, 50), F(1, 5)):
            f = lambda p: table[p] <= eta
            assert bellman_oracle(e, f)[0] == enumerate_oracle(e, f)[0]


def test_controllers_meet_target():
    e = root(500)
    for order in ('uniform', 'random', 'greedy', 'costnorm', 'margin'):
        res = run_controller(e, F(1, 20), order)
        vpi, vt, _, _ = deployed_value(e, e.quantized(res['profile']))
        assert res['certificate'] <= F(1, 20) and vt - vpi <= F(1, 20)
    oc = online_controller(e, F(1, 20))
    assert Solver(e).optimum() - oc['value'] <= oc['certificate'] <= F(1, 20)


def test_posterior_box_bound_equals_vertex_maximum():
    r = Random(7)
    for _ in range(60):
        n = r.randint(2, 5)
        m = tuple(F(r.randint(0, 9), 10) for _ in range(n))
        if sum(m) == 0:
            continue
        lo = tuple(max(F(0), x - F(r.randint(0, 3), 20)) for x in m)
        hi = tuple(min(F(1), x + F(r.randint(0, 3), 20)) for x in m)
        best = F(0)
        for pick in product((0, 1), repeat=n):
            t = tuple(h if s else l for s, l, h in zip(pick, lo, hi))
            if sum(t) > 0:
                best = max(best, tv(tuple(x / sum(t) for x in t), tuple(x / sum(m) for x in m)))
        assert posterior_tv_bound(m, lo, hi) == best


def test_drift_witness_breaks_unsafe_rules():
    from decision_certificates import drift_witness
    w = drift_witness()
    assert w['regret'] == '1/40'
    assert w['claims']['plugin'] == w['claims']['local'] == w['claims']['rootonly'] == '0/1'
    assert F(w['claims']['sound']) >= F(1, 40)


def test_equal_scalar_accuracy_different_regret():
    from decision_certificates import equal_accuracy_witness
    w = equal_accuracy_witness()
    assert w['distinct_regrets'] == ['0/1', '1/96', '1/48', '1/32']


def test_planner_exact_bounds_and_merge():
    for s in range(6):
        e = root(600 + s, n=(5, 7), k=(2, 3), B=(3, 4))
        opt = Quotient(e.w, e.qs, e.budget).solve()
        g, live = groups_of(e, e.w, 0, (1 << len(e.qs)) - 1)
        assert Planner(e, None).value(g, live, e.budget, None, False) == opt
        assert Planner(e, None, quotient=False).value(*groups_of(e, e.w, 0, (1 << len(e.qs)) - 1, False),
                                                      e.budget, None, False) == opt
        for d in (1, 2):
            p = Planner(e, d)
            assert p.value(g, live, e.budget, d, False) <= opt <= p.value(g, live, e.budget, d, True)
        merged, d0, err, _ = merge_classes(e, None)
        assert d0 == 0 and all(x == 0 for x in err)
        for bits, depth, cap in ((1, 1, None), (4, 2, 3), (None, None, None), (2, None, 2)):
            res = configuration(e, bits, depth, cap, True, opt)
            assert 0 <= res['regret'] <= res['certificate']
        assert configuration(e, None, None, None, True, opt)['certificate'] == 0

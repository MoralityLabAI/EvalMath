"""MIT-10 open development run: unsafe local certification rules and scalar-accuracy aliasing.

1. For every root and precision profile, compare each certification rule's claimed bound with
   the exact deployed regret. A claim below the regret is a counterexample to that rule.
   A tie-prone generator (likelihoods next to grid boundaries) and a constructed drift witness
   supply exact counterexamples for the drift-blind rules.
2. Equal scalar accuracy: two approximations of one environment whose every likelihood column
   is moved by exactly delta in total variation (identical max, mean and per-column TV) can
   deploy different policies with different regret. Exhaustive over sign patterns.
3. Posterior drift: the sound bound d(h) by decision depth along deployed policies.

    python decision_certificates.py --output mit10
"""
import argparse, hashlib, json, sys, time
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from spiral_ln.evaluation_adaptive_precision import Env, LEVELS, Solver, deployed_value, tv
from spiral_ln.evaluation_decision_certificate import (View, policy_certificate, step_gap, children)
from certified_precision import make, frac

RULES = ('sound', 'plugin', 'local', 'rootonly')


def env_json(env):
    return dict(weights=[frac(x) for x in env.w], budget=env.budget,
                queries=[dict(cost=c, rows=[[frac(x) for x in r] for r in rows]) for c, rows in env.qs])


def rule_scan(families, roots):
    out = {r: dict(cases=0, violations=0, witness=None, max_excess=F(0)) for r in RULES}
    for fi, fam in enumerate(families):
        for i in range(roots):
            env = make(fam, 920000 + 1000 * fi + i)
            for prof in product(LEVELS[:4], repeat=len(env.qs)):
                vpi, vt, _, _ = deployed_value(env, env.quantized(prof))
                reg = vt - vpi
                for rule in RULES:
                    c = policy_certificate(env, prof, rule)['certificate']
                    o = out[rule]
                    o['cases'] += 1
                    if c < reg:
                        o['violations'] += 1
                        if reg - c > o['max_excess']:
                            o['max_excess'] = reg - c
                            o['witness'] = dict(family=fam, seed=920000 + 1000 * fi + i, profile=list(prof),
                                                claimed=frac(c), regret=frac(reg), env=env_json(env))
    assert out['sound']['violations'] == 0
    for o in out.values():
        o['max_excess'] = frac(o['max_excess'])
    return out


def drift_witness():
    """Constructed counterexample to drift-blind rules (plugin, local, rootonly).

    Four equal-prior strategies, one 4-outcome instrument of cost 1, budget 2. Every column of
    the approximation is within entrywise radius 3/50 of the truth. The root query beats direct
    guessing by a margin every rule certifies; after outcome 1 the approximate posterior ranks
    strategy 0 above strategy 1 while the true posterior ranks 1 above 0.
    """
    c = lambda *v: [F(x) for x in v]
    true_cols = [c('7/10', '3/10', 0, 0), c(0, '2/5', '3/5', 0), c(0, 0, 1, 0), c(0, 0, 0, 1)]
    appr_cols = [c('16/25', '9/25', 0, 0), c(0, '17/50', '33/50', 0), c(0, 0, 1, 0), c(0, 0, 0, 1)]
    rows = lambda cols: [[col[y] for col in cols] for y in range(4)]
    truth = Env([1] * 4, [(1, rows(true_cols))], 2)
    approx = Env([1] * 4, [(1, rows(appr_cols))], 2)
    r = F(3, 50)
    assert all(abs(a - b) <= r for ca, cb in zip(true_cols, appr_cols) for a, b in zip(ca, cb))
    vpi, vt, _, _ = deployed_value(truth, approx)
    claims = {rule: frac(policy_certificate(None, None, rule, approx=approx, radius=[r])['certificate'])
              for rule in RULES}
    return dict(radius=frac(r), regret=frac(vt - vpi), optimum=frac(vt), deployed=frac(vpi), claims=claims,
                env=env_json(truth), approx=env_json(approx))


def tieprone(seed):
    r = Random(seed)
    n, k, B = r.randint(3, 5), r.randint(1, 2), r.randint(2, 3)
    w = [r.randint(8, 10) for _ in range(n)]
    qs = []
    for _ in range(k):
        col = []
        for i in range(n):
            L = r.choice((2, 3, 4))
            p = F(2 * r.randint(0, (1 << L) - 1) + 1, 2 ** (L + 1)) + F(r.randint(-3, 3), 97 * 2 ** L)
            col.append(min(F(1), max(F(0), p)))
        qs.append((1, [col, [1 - x for x in col]]))
    return Env(w, qs, B)


def tie_scan(seeds):
    """Rule violations on roots whose likelihoods sit next to grid boundaries."""
    out = {r: dict(cases=0, violations=0, witnesses=[]) for r in RULES}
    for s in range(seeds):
        env = tieprone(930000 + s)
        for prof in product((1, 2, 4, 8), repeat=len(env.qs)):
            vpi, vt, _, _ = deployed_value(env, env.quantized(prof))
            reg = vt - vpi
            for rule in RULES:
                out[rule]['cases'] += 1
                if reg == 0:
                    continue
                c = policy_certificate(env, prof, rule)['certificate']
                if c < reg:
                    out[rule]['violations'] += 1
                    out[rule]['witnesses'].append(dict(seed=930000 + s, profile=list(prof), claimed=frac(c),
                                                       regret=frac(reg), env=env_json(env)))
    assert out['sound']['violations'] == 0
    return out


def equal_accuracy_witness(delta=F(1, 16)):
    """Exhaustive search over sign patterns on a fixed 6-strategy, two-instrument root."""
    w = [1] * 6
    p1 = [F(13, 16), F(12, 16), F(11, 16), F(5, 16), F(4, 16), F(3, 16)]
    p2 = [F(12, 16), F(4, 16), F(13, 16), F(3, 16), F(11, 16), F(5, 16)]
    truth = Env(w, [(1, [p1, [1 - x for x in p1]]), (1, [p2, [1 - x for x in p2]])], 3)
    opt = Solver(truth).optimum()
    best = None
    seen = {}
    for signs in product((-1, 1), repeat=12):
        a1 = [x + s * delta for x, s in zip(p1, signs[:6])]
        a2 = [x + s * delta for x, s in zip(p2, signs[6:])]
        approx = Env(w, [(1, [a1, [1 - x for x in a1]]), (1, [a2, [1 - x for x in a2]])], 3)
        tvs = sorted(tv((x, 1 - x), (y, 1 - y)) for x, y in zip(p1 + p2, a1 + a2))
        assert tvs == [delta] * 12
        vpi, _, va, _ = deployed_value(truth, approx)
        root = Solver(approx).policy(approx.w, 0, 3, 3)
        seen.setdefault(opt - vpi, (signs, root, va))
    regs = sorted(seen)
    lo, hi = regs[0], regs[-1]
    return dict(delta=frac(delta), optimum=frac(opt), distinct_regrets=[frac(r) for r in regs],
                low=dict(regret=frac(lo), signs=list(seen[lo][0]), root_action=list(seen[lo][1]),
                         predicted=frac(seen[lo][2])),
                high=dict(regret=frac(hi), signs=list(seen[hi][0]), root_action=list(seen[hi][1]),
                          predicted=frac(seen[hi][2])),
                env=env_json(truth), sign_patterns=2 ** 12,
                note='every column moved by exactly delta in TV in both approximations')


def drift_by_depth(families, roots):
    """Mean and max sound posterior-TV bound d(h) at each decision depth of deployed policies."""
    acc = {}
    for fi, fam in enumerate(families):
        for i in range(roots):
            env = make(fam, 920000 + 1000 * fi + i)
            for lv in LEVELS[:5]:
                prof = (lv,) * len(env.qs)
                view = View(env, prof)

                def go(m, lo, hi, g, a, b, depth):
                    if b <= 0 or sum(hi) == 0 or sum(m) == 0:
                        return
                    act, _, d = step_gap(view, m, lo, hi, g, a, b)
                    if act is None:
                        return
                    acc.setdefault((lv, depth), []).append(d)
                    for c in children(view, act, m, lo, hi, g, a, b):
                        go(*c, depth + 1)
                e = view.env
                go(e.w, e.w, e.w, 0, (1 << len(e.qs)) - 1, e.budget, 0)
    return {f'{lv}|{depth}': dict(histories=len(v), mean=float(sum(v) / len(v)), max=frac(max(v)))
            for (lv, depth), v in sorted(acc.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--roots', type=int, default=16)
    ap.add_argument('--tie-seeds', type=int, default=1500)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    fams = ('random', 'margin', 'slack')
    res = dict(rules=rule_scan(fams, a.roots), tie_rules=tie_scan(a.tie_seeds), drift_witness=drift_witness(),
               equal_accuracy=equal_accuracy_witness(),
               drift=drift_by_depth(fams, a.roots))
    res['meta'] = dict(schema='mit10-open-dev-v1', roots_per_family=a.roots, families=fams,
                       levels_scanned=[1, 2, 4, 8], elapsed_s=time.perf_counter() - t0,
                       sources={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
                           'src/spiral_ln/evaluation_adaptive_precision.py',
                           'src/spiral_ln/evaluation_decision_certificate.py',
                           'gyms/MathematicalInstrumentTransfer/decision_certificates.py')},
                       evidence='exact finite synthetic development roots; counterexamples are exact witnesses')
    (a.output / 'mit10_result.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'witness'} for k, v in res['rules'].items()}, indent=1))
    print('tie scan', {k: (v['cases'], v['violations']) for k, v in res['tie_rules'].items()})
    print('drift witness', res['drift_witness']['regret'], res['drift_witness']['claims'])
    eq = res['equal_accuracy']
    print('equal accuracy regrets', eq['distinct_regrets'], 'roots', eq['low']['root_action'], eq['high']['root_action'])
    print(json.dumps(res['drift'], indent=0)[:1500])


if __name__ == '__main__':
    main()

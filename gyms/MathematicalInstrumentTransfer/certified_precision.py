"""MIT-09 open development run: certified adaptive precision on exact synthetic roots.

Per root, every precision profile is scored once (a priori global certificate, retrospective
global certificate, decision certificate, exact deployed regret). Controllers then run with
their own certificate as the stopping rule; oracles search the precision lattice.
Exact rationals throughout; wall-clock and memory are diagnostics, outside exact receipts.

    python certified_precision.py --output mit09 [--roots 32] [--workers 6]
"""
import argparse, hashlib, json, sys, time
from fractions import Fraction as F
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from random import Random
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from spiral_ln.evaluation_adaptive_precision import (Env, LEVELS, Solver, deployed_value, instrument_errors,
    global_certificate, run_controller, bellman_oracle, enumerate_oracle, memory_bits)
from spiral_ln.evaluation_decision_certificate import policy_certificate, online_controller

ETAS = (F(1, 100), F(1, 20), F(1, 5))
ORDERS = ('uniform', 'random', 'greedy', 'costnorm', 'margin')
FAMILIES = ('random', 'margin', 'slack')


def col(r, m, den):
    cuts = sorted(r.randint(0, den) for _ in range(m - 1))
    pts = [0] + cuts + [den]
    return [F(pts[i + 1] - pts[i], den) for i in range(m)]


def rows_of(cols):
    return [[c[y] for c in cols] for y in range(len(cols[0]))]


def make(family, seed):
    r = Random(seed)
    if family == 'random':
        n, k, B = r.randint(4, 6), r.randint(2, 3), r.randint(2, 4)
        w = [r.randint(1, 5) for _ in range(n)]
        qs = []
        for _ in range(k):
            m = r.choice((2, 2, 3))
            den = r.choice((7, 11, 13, 97))
            qs.append((r.choice((1, 1, 2)), rows_of([col(r, m, den) for _ in range(n)])))
        return Env(w, qs, B)
    if family == 'margin':
        # Two binary instruments whose split masses nearly tie; a third weak instrument.
        n, B = 6, 3
        w = [1] * n
        base = [F(r.randint(60, 97), 97) if i < 3 else F(r.randint(0, 37), 97) for i in range(n)]
        perm = list(range(n)); r.shuffle(perm)
        second = [min(F(1), max(F(0), base[perm[i]] + F(r.choice((-1, 1)) * r.randint(1, 4), 1009)))
                  for i in range(n)]
        weak = [F(r.randint(40, 57), 97) for _ in range(n)]
        qs = [(1, rows_of([[p, 1 - p] for p in v])) for v in (base, second, weak)]
        return Env(w, qs, B)
    # slack: one decisive instrument, noisy near-uninformative others (non-dyadic).
    n, B = r.randint(5, 6), 3
    w = [r.randint(1, 4) for _ in range(n)]
    good = [F(r.randint(11, 13), 13) if i % 2 else F(r.randint(0, 2), 13) for i in range(n)]
    qs = [(1, rows_of([[p, 1 - p] for p in good]))]
    for _ in range(r.randint(1, 2)):
        qs.append((1, rows_of([[F(r.randint(45, 52), 97), 0] for _ in range(n)])))
        qs[-1] = (1, [[c for c in qs[-1][1][0]], [1 - c for c in qs[-1][1][0]]])
    return Env(w, qs, B)


def frac(x):
    return None if x is None else f'{x.numerator}/{x.denominator}'


def run_root(args):
    family, idx, seed = args
    env = make(family, seed)
    k = len(env.qs)
    table = {}
    t0 = time.perf_counter()
    for prof in product(LEVELS, repeat=k):
        approx = env.quantized(prof)
        vpi, vt, va, states = deployed_value(env, approx)
        pri, retro = instrument_errors(env, prof)
        pc = policy_certificate(env, prof)
        table[prof] = dict(regret=vt - vpi, glob=global_certificate(approx, pri)[1],
                           retro=global_certificate(approx, retro)[1], policy=pc['certificate'],
                           histories=pc['histories'], states=states, memory=memory_bits(env, prof))
    table_s = time.perf_counter() - t0
    out = dict(family=family, root=idx, seed=seed, n=env.n, instruments=k, budget=env.budget,
               profiles=len(table), table_s=table_s, optimum=frac(Solver(env).optimum()), etas={})
    for eta in ETAS:
        res = {}
        crit = dict(glob=lambda p: table[p]['glob'] <= eta, policy=lambda p: table[p]['policy'] <= eta,
                    hindsight=lambda p: table[p]['regret'] <= eta)
        for name, fe in crit.items():
            c, p = bellman_oracle(env, fe)
            c2, _ = enumerate_oracle(env, fe)
            assert c == c2, (family, idx, name)
            res[f'oracle_{name}'] = dict(cost=c, profile=p, regret=frac(table[p]['regret']),
                                         cert=frac(table[p]['glob' if name == 'glob' else 'policy']))
        for stop in ('glob', 'policy'):
            certify = (lambda e, p, a: table[p][stop])
            for order in ORDERS:
                for s in ((0, 1, 2) if order == 'random' else (0,)):
                    t1 = time.perf_counter()
                    # Controllers pay for computing their certificate: recompute it live.
                    live = (lambda e, p, a: (global_certificate(a, instrument_errors(e, p)[0])[1]
                                             if stop == 'glob' else policy_certificate(e, p)['certificate']))
                    r = run_controller(env, eta, order, live, seed=1000 * idx + s)
                    p = r['profile']
                    res[f'{order}{s if order == "random" else ""}_{stop}'] = dict(
                        cost=r['cost'], profile=p, regret=frac(table[p]['regret']), cert=frac(r['certificate']),
                        retro=frac(table[p]['retro']), steps=r['steps'], wall_s=time.perf_counter() - t1,
                        memory=table[p]['memory'], states=table[p]['states'])
        t1 = time.perf_counter()
        oc = online_controller(env, eta)
        res['online_margin'] = dict(cost=frac(oc['expected_cost']), regret=frac(Solver(env).optimum() - oc['value']),
                                    cert=frac(oc['certificate']), wall_s=time.perf_counter() - t1,
                                    refinements=oc['refinements'], decisions=oc['decisions'], views=oc['views'])
        out['etas'][frac(eta)] = res
    # Certificate tightness over all profiles (soundness is asserted).
    rows = list(table.values())
    assert all(r['regret'] <= r['retro'] <= r['glob'] for r in rows), (family, idx)
    assert all(r['regret'] <= r['policy'] for r in rows), (family, idx)
    out['tightness'] = dict(
        regret_positive=sum(r['regret'] > 0 for r in rows),
        policy_below_global=sum(r['policy'] < r['glob'] for r in rows),
        policy_zero=sum(r['policy'] == 0 for r in rows),
        mean_regret=float(mean(r['regret'] for r in rows)), mean_glob=float(mean(r['glob'] for r in rows)),
        mean_retro=float(mean(r['retro'] for r in rows)), mean_policy=float(mean(r['policy'] for r in rows)))
    out['profiles_detail'] = [dict(profile=list(p), **{k2: (frac(v) if isinstance(v, F) else v) for k2, v in t.items()})
                              for p, t in table.items()]
    return out


def tofloat(x):
    if x is None:
        return None
    if isinstance(x, str):
        a, b = x.split('/')
        return int(a) / int(b)
    return float(x)


def summarize(results):
    lines = ['| family | eta | method | mean cost | cost/oracle_policy | mean regret | max regret | regret>eta | mean cert | mean wall ms |',
             '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    summary = {}
    for fam in FAMILIES:
        rs = [r for r in results if r['family'] == fam]
        for eta in map(frac, ETAS):
            methods = list(rs[0]['etas'][eta].keys())
            for m in methods:
                vals = [r['etas'][eta][m] for r in rs]
                costs = [tofloat(v['cost']) for v in vals]
                ratio = mean(tofloat(v['cost']) / r['etas'][eta]['oracle_policy']['cost'] for v, r in zip(vals, rs))
                regs = [tofloat(v['regret']) for v in vals]
                certs = [tofloat(v['cert']) for v in vals if v.get('cert') is not None]
                walls = [v['wall_s'] * 1000 for v in vals if 'wall_s' in v]
                e = tofloat(eta)
                row = dict(mean_cost=mean(costs), cost_ratio=ratio, mean_regret=mean(regs), max_regret=max(regs),
                           over_eta=sum(x > e + 1e-15 for x in regs), mean_cert=mean(certs) if certs else None,
                           mean_wall_ms=mean(walls) if walls else None)
                summary[f'{fam}|{eta}|{m}'] = row
                lines.append(f"| {fam} | {eta} | {m} | {row['mean_cost']:.1f} | {ratio:.3f} | {row['mean_regret']:.5f} | "
                             f"{row['max_regret']:.5f} | {row['over_eta']} | "
                             f"{'' if row['mean_cert'] is None else f'{row['mean_cert']:.4f}'} | "
                             f"{'' if row['mean_wall_ms'] is None else f'{row['mean_wall_ms']:.1f}'} |")
    return summary, '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--roots', type=int, default=32)
    ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    jobs = [(fam, i, 910000 + 1000 * fi + i) for fi, fam in enumerate(FAMILIES) for i in range(a.roots)]
    t0 = time.perf_counter()
    with Pool(a.workers) as pool:
        results = pool.map(run_root, jobs, chunksize=1)
    summary, table = summarize(results)
    src = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
        'src/spiral_ln/evaluation_adaptive_precision.py', 'src/spiral_ln/evaluation_decision_certificate.py',
        'gyms/MathematicalInstrumentTransfer/certified_precision.py')}
    meta = dict(schema='mit09-open-dev-v1', roots=len(results), families=FAMILIES, etas=[frac(e) for e in ETAS],
                levels=[str(l) for l in LEVELS], elapsed_s=time.perf_counter() - t0, sources=src,
                evidence='exact finite synthetic development roots; open; no sealed split; timings exploratory')
    (a.output / 'mit09_rows.json').write_text(json.dumps(dict(meta=meta, results=results), default=str) + '\n')
    (a.output / 'mit09_summary.json').write_text(json.dumps(dict(meta=meta, summary=summary), indent=1) + '\n')
    (a.output / 'mit09_table.md').write_text(table)
    print(table)
    print(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()

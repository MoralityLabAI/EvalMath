"""MIT-11 open development run: depth x precision x class-cap frontier with certified regret.

Per root and configuration (bits, depth, class cap, quotient on/off) records exact deployed regret,
certified regret, planner states and wall-clock. Builds Pareto frontiers over configurations, a
matched-state-budget allocation analysis with and without quotient compression, and exact
witnesses for (a) precision with no decision value and (b) one additional bit changing the action.

    python depth_precision.py --output mit11 [--roots 12] [--workers 6]
"""
import argparse, hashlib, json, sys, time
from fractions import Fraction as F
from multiprocessing import Pool
from pathlib import Path
from random import Random
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from spiral_ln.evaluation_adaptive_precision import Env, Solver
from spiral_ln.evaluation_depth_precision import configuration
from spiral_ln.evaluation_noisy_instrument_quotient import Quotient

BITS = (1, 2, 4, 8, 16, None)
DEPTHS = (1, 2, 3, None)
CAPS = (None, 6, 3)
FAMILIES = ('palette', 'structured', 'random')


def make(family, seed):
    r = Random(seed)
    if family == 'palette':
        n, k, B = 12, r.randint(4, 5), r.randint(4, 5)
        w = [1] * n
        pal = (F(1, 4), F(3, 4))
    elif family == 'structured':
        n, k, B = r.randint(10, 12), r.randint(4, 5), r.randint(4, 5)
        w = [r.choice((1, 1, 2)) for _ in range(n)]
        pal = (F(1, 8), F(3, 8), F(5, 8), F(7, 8))
    else:
        n, k, B = r.randint(7, 9), r.randint(3, 4), r.randint(3, 5)
        w = [r.randint(1, 4) for _ in range(n)]
        pal = None
    qs = []
    for _ in range(k):
        if pal is None:
            den = r.choice((13, 97))
            cols = [F(r.randint(0, den), den) for _ in range(n)]
        else:
            cols = [min(F(1), max(F(0), r.choice(pal) + F(r.randint(-2, 2), 97))) for _ in range(n)]
        qs.append((r.choice((1, 1, 2)), [cols, [1 - x for x in cols]]))
    return Env(w, qs, B)


def frac(x):
    return None if x is None else f'{x.numerator}/{x.denominator}'


def run_root(job):
    family, idx, seed = job
    env = make(family, seed)
    opt = Quotient(env.w, env.qs, env.budget).solve()
    assert opt == Solver(env).optimum() if env.n <= 9 else True
    rows = []
    for bits in BITS:
        for depth in DEPTHS:
            for cap in CAPS:
                for quot in ((True, False) if cap is None else (True,)):
                    r = configuration(env, bits, depth, cap, quot, opt)
                    rows.append(dict(bits=bits, depth=depth, cap=cap, quotient=quot, classes=r['classes'],
                                     regret=frac(r['regret']), certificate=frac(r['certificate']), D=frac(r['D']),
                                     search_gap=frac(r['search_gap']), states=r['states'], wall_s=r['wall_s'],
                                     root_action=list(r['root_action'])))
                    assert r['regret'] <= r['certificate']
    # Consecutive-bit scan at exact depth, no cap: decision value of one more bit.
    scan = []
    for b in list(range(1, 13)) + [None]:
        r = configuration(env, b, None, None, True, opt)
        scan.append(dict(bits=b, regret=frac(r['regret']), certificate=frac(r['certificate']),
                         root_action=list(r['root_action'])))
    return dict(family=family, root=idx, seed=seed, n=env.n, instruments=len(env.qs), budget=env.budget,
                optimum=frac(opt), rows=rows, bit_scan=scan)


def fl(x):
    if x is None:
        return None
    a, b = x.split('/')
    return int(a) / int(b)


def pareto(points):
    """Indices of points not dominated in (cost, loss), both minimized."""
    keep = []
    for i, (c, l, _) in enumerate(points):
        if not any((c2 <= c and l2 <= l) and (c2 < c or l2 < l) for c2, l2, _ in points):
            keep.append(i)
    return keep


def analyse(results):
    out = {}
    for fam in FAMILIES:
        rs = [r for r in results if r['family'] == fam]
        keys = [(x['bits'], x['depth'], x['cap'], x['quotient']) for x in rs[0]['rows']]
        agg = []
        for t, key in enumerate(keys):
            vals = [r['rows'][t] for r in rs]
            agg.append(dict(bits=key[0], depth=key[1], cap=key[2], quotient=key[3],
                            mean_regret=mean(fl(v['regret']) for v in vals), max_regret=max(fl(v['regret']) for v in vals),
                            mean_cert=mean(fl(v['certificate']) for v in vals),
                            mean_states=mean(v['states'] for v in vals), mean_wall_ms=1000 * mean(v['wall_s'] for v in vals)))
        quot = [a for a in agg if a['quotient']]
        fr_cert = [quot[i] for i in pareto([(a['mean_wall_ms'], a['mean_cert'], a) for a in quot])]
        fr_reg = [quot[i] for i in pareto([(a['mean_wall_ms'], a['mean_regret'], a) for a in quot])]
        # Matched state budgets: best certified configuration per root under a state cap.
        alloc = {}
        for mode in (True, False):
            for budget in (100, 300, 1000, 3000):
                picks = []
                for r in rs:
                    cand = [x for x in r['rows'] if x['quotient'] == mode and x['cap'] is None and x['states'] <= budget]
                    if not cand:
                        continue
                    best = min(cand, key=lambda x: (fl(x['certificate']), x['states']))
                    picks.append((best['bits'], best['depth'], fl(best['certificate']), fl(best['regret'])))
                alloc[f"{'quotient' if mode else 'expanded'}|{budget}"] = dict(
                    roots=len(picks), choices=sorted({(str(b), str(d)) for b, d, _, _ in picks}),
                    mean_cert=mean(p[2] for p in picks) if picks else None,
                    mean_regret=mean(p[3] for p in picks) if picks else None)
        # Witnesses from the consecutive-bit scan.
        negligible, one_bit = [], []
        for r in rs:
            sc = r['bit_scan']
            if all(fl(s['regret']) == 0 for s in sc):
                negligible.append(dict(seed=r['seed'], certs=[s['certificate'] for s in sc]))
            for a, b in zip(sc, sc[1:]):
                if a['bits'] is not None and b['bits'] == a['bits'] + 1 and a['root_action'] != b['root_action'] \
                        and fl(a['regret']) > fl(b['regret']):
                    one_bit.append(dict(seed=r['seed'], bits=a['bits'], regret_before=a['regret'],
                                        regret_after=b['regret'], action_before=a['root_action'],
                                        action_after=b['root_action']))
        st_q = mean(a['mean_states'] for a in agg if a['quotient'] and a['cap'] is None)
        st_e = mean(a['mean_states'] for a in agg if not a['quotient'])
        out[fam] = dict(roots=len(rs), configs=agg, frontier_cert=fr_cert, frontier_regret=fr_reg,
                        allocation=alloc, negligible_precision=negligible, one_bit_changes=one_bit,
                        mean_states_quotient=st_q, mean_states_expanded=st_e)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--roots', type=int, default=12)
    ap.add_argument('--workers', type=int, default=6)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    jobs = [(fam, i, 940000 + 1000 * fi + i) for fi, fam in enumerate(FAMILIES) for i in range(a.roots)]
    t0 = time.perf_counter()
    with Pool(a.workers) as pool:
        results = pool.map(run_root, jobs, chunksize=1)
    an = analyse(results)
    meta = dict(schema='mit11-open-dev-v1', roots=len(results), families=FAMILIES, bits=[str(b) for b in BITS],
                depths=[str(d) for d in DEPTHS], caps=[str(c) for c in CAPS], elapsed_s=time.perf_counter() - t0,
                sources={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
                    'src/spiral_ln/evaluation_adaptive_precision.py', 'src/spiral_ln/evaluation_depth_precision.py',
                    'gyms/MathematicalInstrumentTransfer/depth_precision.py')},
                evidence='exact finite synthetic development roots; open; timings exploratory, one CPU, shared machine')
    (a.output / 'mit11_rows.json').write_text(json.dumps(dict(meta=meta, results=results)) + '\n')
    (a.output / 'mit11_analysis.json').write_text(json.dumps(dict(meta=meta, analysis=an), indent=1, default=str) + '\n')
    for fam, v in an.items():
        print(fam, 'states quotient %.0f expanded %.0f' % (v['mean_states_quotient'], v['mean_states_expanded']))
        print(' frontier(cert):', [(c['bits'], c['depth'], c['cap'], round(c['mean_wall_ms'], 1), round(c['mean_cert'], 4)) for c in v['frontier_cert']])
        print(' frontier(regret):', [(c['bits'], c['depth'], c['cap'], round(c['mean_wall_ms'], 1), round(c['mean_regret'], 5)) for c in v['frontier_regret']])
        print(' alloc:', {k: (x['choices'], x['mean_cert']) for k, x in v['allocation'].items()})
        print(' negligible', len(v['negligible_precision']), 'one-bit', len(v['one_bit_changes']), v['one_bit_changes'][:2])
    print(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()

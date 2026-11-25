"""MIT-09/10/11 exact receipt: certified precision, decision certificates, depth-precision planner.

Runs the regression tests, then recomputes exact rows on fixed development seeds: lattice oracles
and controller costs (MIT-09), the drift and equal-accuracy witnesses (MIT-10), and the bit-scan
and planner certificates (MIT-11). Wall-clock is excluded from the receipt.
"""
import argparse
import hashlib
import json
import runpy
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GYM = ROOT / 'gyms' / 'MathematicalInstrumentTransfer'
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(GYM))
from spiral_ln.evaluation_adaptive_precision import (LEVELS, Solver, deployed_value, instrument_errors,
    global_certificate, run_controller, bellman_oracle, enumerate_oracle)
from spiral_ln.evaluation_decision_certificate import policy_certificate, online_controller
from spiral_ln.evaluation_depth_precision import configuration
from spiral_ln.evaluation_noisy_instrument_quotient import Quotient
import certified_precision as cp
import decision_certificates as dc
import depth_precision as dp

SOURCES = ('src/spiral_ln/evaluation_adaptive_precision.py', 'src/spiral_ln/evaluation_decision_certificate.py',
           'src/spiral_ln/evaluation_depth_precision.py', 'gyms/MathematicalInstrumentTransfer/certified_precision.py',
           'gyms/MathematicalInstrumentTransfer/decision_certificates.py',
           'gyms/MathematicalInstrumentTransfer/depth_precision.py', 'tests/test_certified_precision.py',
           'scripts/verify_certified_precision.py', 'lean/FeedbackChannel/CertifiedPrecision.lean')
ONE_BIT_SEED = ('palette', 940001)
ETA = F(1, 20)


def s(x):
    return f'{x.numerator}/{x.denominator}'


def mit09_rows():
    rows = []
    for fi, fam in enumerate(cp.FAMILIES):
        for i in range(4):
            env = cp.make(fam, 910000 + 1000 * fi + i)
            table = {}
            for prof in product(LEVELS, repeat=len(env.qs)):
                a = env.quantized(prof)
                vpi, vt, _, _ = deployed_value(env, a)
                table[prof] = (vt - vpi, global_certificate(a, instrument_errors(env, prof)[0])[1],
                               policy_certificate(env, prof)['certificate'])
            assert all(r <= g and r <= p for r, g, p in table.values())
            crit = {'glob': lambda p: table[p][1] <= ETA, 'policy': lambda p: table[p][2] <= ETA,
                    'hindsight': lambda p: table[p][0] <= ETA}
            row = dict(family=fam, seed=910000 + 1000 * fi + i)
            for name, f in crit.items():
                c, p = bellman_oracle(env, f)
                assert c == enumerate_oracle(env, f)[0]
                row[f'oracle_{name}'] = c
            row['uniform_glob'] = run_controller(env, ETA, 'uniform')['cost']
            oc = online_controller(env, ETA)
            row['online_cost'] = s(oc['expected_cost'])
            row['online_regret'] = s(Solver(env).optimum() - oc['value'])
            row['online_certificate'] = s(oc['certificate'])
            rows.append(row)
    return rows


def mit11_rows():
    fam, seed = ONE_BIT_SEED
    env = dp.make(fam, seed)
    opt = Quotient(env.w, env.qs, env.budget).solve()
    scan = []
    for b in list(range(1, 9)) + [None]:
        r = configuration(env, b, None, None, True, opt)
        scan.append(dict(bits=b, regret=s(r['regret']), certificate=s(r['certificate']), root=list(r['root_action'])))
    grid = []
    for bits, depth, cap in ((1, 1, None), (4, 2, None), (16, 3, None), (None, 1, None), (None, None, 6), (8, None, None)):
        r = configuration(env, bits, depth, cap, True, opt)
        assert r['regret'] <= r['certificate']
        grid.append(dict(bits=bits, depth=depth, cap=cap, regret=s(r['regret']), certificate=s(r['certificate']),
                         states=r['states'], classes=r['classes']))
    return dict(family=fam, seed=seed, optimum=s(opt), bit_scan=scan, grid=grid)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, default=ROOT / 'output/evaluation_instrument_transfer/mit09_v0_1.json')
    a = p.parse_args()
    t = runpy.run_path(str(ROOT / 'tests/test_certified_precision.py'))
    checks = {}
    for name in sorted(t):
        if name.startswith('test_'):
            t[name]()
            checks[name] = True
    m9 = mit09_rows()
    m10 = dict(drift=dc.drift_witness(), equal_accuracy=dc.equal_accuracy_witness())
    m11 = mit11_rows()
    receipt = dict(schema='mit09-11-v0.1',
                   evidence='algebraic arguments (paper), Lean supporting lemmas, exact finite synthetic checks',
                   checks=checks, source_sha256={k: hashlib.sha256((ROOT / k).read_bytes()).hexdigest() for k in SOURCES},
                   eta=s(ETA), levels=[str(x) for x in LEVELS], mit09=m9,
                   mit10=dict(drift_regret=m10['drift']['regret'], drift_claims=m10['drift']['claims'],
                              equal_accuracy_regrets=m10['equal_accuracy']['distinct_regrets']),
                   mit11=m11,
                   row_manifest_sha256=hashlib.sha256(json.dumps([m9, m10, m11], sort_keys=True, default=str,
                                                                 separators=(',', ':')).encode()).hexdigest())
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=2, sort_keys=True, default=str) + '\n')
    print(f'{len(checks)} checks; {len(m9)} MIT-09 roots; MIT-10 witnesses; MIT-11 bit scan seed {m11["seed"]}')


if __name__ == '__main__':
    main()

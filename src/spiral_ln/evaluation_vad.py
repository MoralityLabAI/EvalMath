"""VAD-01A: finite GF(2) cache-amortization oracle. Standard library only."""
import hashlib
import json
from pathlib import Path
from itertools import combinations
from random import Random
from fractions import Fraction

D, SEEDS, HORIZONS = 20, range(32), (4, 8, 16, 32, 64)


def weight(x):
    return x.bit_count()


def proof_cost(t, a=0):
    # One unit per generator reference for producer, one for checker.
    return 2 * min(weight(t), 1 + weight(t ^ a)) if a else 2 * weight(t)


def mask(indices):
    return sum(1 << i for i in indices)


def roots(rng, motif, n, exclude=()):
    available = [i for i in range(D) if not motif >> i & 1]
    seen, out = set(exclude), []
    while len(out) < n:
        t = motif | mask(rng.sample(available, 10 - weight(motif)))
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def discover(dev):
    candidates = sorted({a & b for a, b in combinations(dev, 2)} - {0})
    # One abstract unit per intersection and per candidate-root score probe.
    charge = len(list(combinations(dev, 2))) + len(candidates) * len(dev)
    def value(a):
        return sum(proof_cost(t) - proof_cost(t, a) for t in dev) - 2 * weight(a)
    best = max(candidates, key=lambda a: (value(a), -a), default=0)
    return (best if best and value(best) > 0 else 0), charge


def exact_check():
    # Independent enumeration of all subsets of the primitive/cached generators.
    checked = 0
    for a in range(64):
        generators = [1 << i for i in range(6)] + ([a] if a else [])
        best = [99] * 64
        for subset in range(1 << len(generators)):
            v, count = 0, 0
            for i, g in enumerate(generators):
                if subset >> i & 1:
                    v ^= g
                    count += 1
            best[v] = min(best[v], 2 * count)
        for t in range(64):
            assert best[t] == proof_cost(t, a), (t, a)
            checked += 1
    return checked


def run():
    records = []
    for regime in ('shared', 'shifted', 'null'):
        for seed in SEEDS:
            basis = Random(1000 + seed).sample(range(D), 12)
            m, other = mask(basis[:6]), mask(basis[6:])
            dev_m = m if regime != 'null' else 0
            test_m = {'shared': m, 'shifted': other, 'null': 0}[regime]
            dev = roots(Random(2000 + seed), dev_m, 4)
            a, discovery = discover(dev)
            held = roots(Random(3000 + seed), test_m, max(HORIZONS), dev)
            assert not set(dev) & set(held)
            for n in HORIZONS:
                targets = held[:n]
                base = sum(proof_cost(t) for t in targets)
                total = discovery + 2 * weight(a) + sum(proof_cost(t, a) for t in targets)
                oracle = 2 * weight(test_m) + sum(proof_cost(t, test_m) for t in targets)
                records.append(dict(regime=regime, seed=seed, horizon=n, cache=a, discovery=discovery,
                                    baseline=base, selected=total, privileged_oracle=oracle))
    summary = []
    for regime in ('shared', 'shifted', 'null'):
        for n in HORIZONS:
            rows = [r for r in records if r['regime'] == regime and r['horizon'] == n]
            b, s, o = [sum(r[k] for r in rows) for k in ('baseline', 'selected', 'privileged_oracle')]
            summary.append(dict(regime=regime, horizon=n, baseline=b, selected=s, oracle=o,
                                gain=str(Fraction(b, s)), profitable=sum(r['selected'] < r['baseline'] for r in rows)))
    return dict(protocol='VAD-01A', evidence='finite exact synthetic control',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                exhaustive_cost_checks=exact_check(), families=32, summary=summary, records=records)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))

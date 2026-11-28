"""VAD-02: exact XOR library costs and charged joint-vs-greedy selection."""
from collections import deque
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, permutations
from math import comb
from pathlib import Path
from random import Random
import json


@lru_cache(None)
def residuals(library):
    rows = [(0, 0)]
    for a in library:
        rows += [(v ^ a, k + 1) for v, k in rows]
    return tuple(rows)


def cost(t, library=()):
    return 2 * min(k + (t ^ v).bit_count() for v, k in residuals(library))


@lru_cache(None)
def build(library):
    if not library:
        return 0
    return min(build(library[:i] + library[i+1:]) +
               cost(a, library[:i] + library[i+1:])
               for i, a in enumerate(library))


def bfs(d, library):
    generators = tuple(1 << i for i in range(d)) + library
    dist = {0: 0}
    q = deque([0])
    while q:
        v = q.popleft()
        for a in generators:
            w = v ^ a
            if w not in dist:
                dist[w] = dist[v] + 2
                q.append(w)
    return dist


def perm_build(d, library):
    return min(sum(bfs(d, order[:i])[a] for i, a in enumerate(order))
               for order in permutations(library))


def exhaustive():
    ncost = nbuild = 0
    for k in range(4):
        for lib in combinations(range(1, 16), k):
            oracle = bfs(4, lib)
            assert all(cost(t, lib) == oracle[t] for t in range(16))
            assert build(lib) == perm_build(4, lib)
            ncost += 16
            nbuild += 1
    return ncost, nbuild


def mask(seq):
    return sum(1 << x for x in seq)


def sample_roots(rng, motif, forbidden, n, excluded=()):
    choices = [i for i in range(24) if not (motif | forbidden) >> i & 1]
    seen, out = set(excluded), []
    while len(out) < n:
        t = motif | mask(rng.sample(choices, 8 - motif.bit_count()))
        if t not in seen:
            seen.add(t)
            out.append(t)
    return tuple(out)


def family(seed, regime):
    rng = Random(5000 + seed)
    order = rng.sample(range(24), 24)
    m, noise, shift = mask(order[:4]), mask(order[4:7]), mask(order[7:11])
    pair = (mask(order[:2]) | noise, mask(order[2:4]) | noise)
    decoys = set()
    while len(decoys) < 4:
        decoys.add(mask(rng.sample(order[4:], 5)))
    pool = tuple(sorted(set(pair) | decoys))
    assert len(pool) == 6
    dev = sample_roots(Random(6000 + seed), m, noise, 8)
    motif, forbidden = {'shared': (m, noise), 'shifted': (shift, m | noise),
                        'null': (0, 0)}[regime]
    held = sample_roots(Random(7000 + seed), motif, forbidden, 256, dev)
    assert not set(dev) & set(held)
    return pool, dev, held, tuple(sorted(pair))


def select(pool, dev, method):
    scores = {(): 0}
    charged = 0

    def score(lib):
        nonlocal charged
        if lib not in scores:
            k = len(lib)
            # Residual probes for every development root plus all subset-DP
            # construction probes; do not count cached score probes twice.
            charged += len(dev) * (1 << k) + sum(
                comb(k, j) * j * (1 << (j-1)) for j in range(1, k+1))
            saving = sum(cost(t) - cost(t, lib) for t in dev)
            scores[lib] = Fraction(256 * saving, len(dev)) - build(lib)
        return scores[lib]

    def best(libs):
        return min(libs, key=lambda lib: (-score(lib), len(lib), lib))

    if method == 'joint':
        chosen = best([()] + [lib for k in (1, 2) for lib in combinations(pool, k)])
    elif method == 'greedy':
        chosen = ()
        for _ in range(2):
            nxt = best([chosen] + [tuple(sorted(chosen + (a,))) for a in pool if a not in chosen])
            if score(nxt) <= score(chosen):
                break
            chosen = nxt
    else:
        raise ValueError(method)
    return chosen, charged


def run():
    checks = exhaustive()
    assert cost(7) == cost(7, (25,)) == cost(7, (30,)) == 6
    assert cost(7, (25, 30)) == 4
    assert build((7, 15)) == 10
    rows = []
    for regime in ('shared', 'shifted', 'null'):
        for seed in range(32):
            pool, dev, held, pair = family(seed, regime)
            for method in ('greedy', 'joint'):
                lib, search = select(pool, dev, method)
                for n in (32, 64, 128, 256):
                    total = search + build(lib) + sum(cost(t, lib) for t in held[:n])
                    rows.append(dict(regime=regime, seed=seed, method=method, horizon=n,
                                     baseline=sum(cost(t) for t in held[:n]), total=total,
                                     search=search, build=build(lib), library=lib, pair_found=lib == pair))
    summary = []
    for regime in ('shared', 'shifted', 'null'):
        for method in ('greedy', 'joint'):
            for n in (32, 64, 128, 256):
                rr = [r for r in rows if (r['regime'], r['method'], r['horizon']) == (regime, method, n)]
                base, total = [sum(r[k] for r in rr) for k in ('baseline', 'total')]
                summary.append(dict(regime=regime, method=method, horizon=n, baseline=base,
                                    total=total, gain=str(Fraction(base, total)),
                                    profitable=sum(r['total'] < r['baseline'] for r in rr),
                                    pair_found=sum(r['pair_found'] for r in rr)))
    return dict(protocol='VAD-02', evidence='finite exact synthetic control',
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                shortest_path_checks=checks[0], build_order_checks=checks[1],
                summary=summary, records=rows)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))

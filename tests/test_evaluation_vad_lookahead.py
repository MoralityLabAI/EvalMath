import json
from hashlib import sha256
from collections import deque
from itertools import combinations
from math import comb
from pathlib import Path
from random import Random

import pytest

from spiral_ln.evaluation_vad_lookahead import (
    BUDGET, MASK, cost, family, roots, run, select, signature_pairs, unrank,
)


def test_pair_cost_against_bfs():
    for lib in [()] + [(x,) for x in range(1, 16)] + list(combinations(range(1, 16), 2)):
        dist = {0: 0}
        q = deque([0])
        while q:
            x = q.popleft()
            for a in (1, 2, 4, 8) + lib:
                y = x ^ a
                if y not in dist:
                    dist[y] = dist[x] + 2
                    q.append(y)
        assert all(cost(t, lib) == dist[t] for t in range(16))


def test_signature_index_against_direct_filter():
    rng = Random(53)
    for _ in range(64):
        pool = tuple(rng.sample(range(1, 256), 24))
        dev = tuple(rng.sample(range(256), 4))
        expected = [tuple(sorted((a, b))) for a, b in combinations(pool, 2)
                    if all(not any(((a ^ b ^ t) >> i) & 1 for t in dev)
                           for i in range(28) if len({(t >> i) & 1 for t in dev}) == 1)]
        actual, _ = signature_pairs(pool, dev, comb(len(pool), 2))
        assert actual == expected
        assert signature_pairs(pool, dev, BUDGET)[0] == expected[:BUDGET]
        assert signature_pairs(pool, dev, 0) == ([], 0)


def test_pair_unranking():
    for size in (2, 3, 16, 32, 64):
        assert [unrank(size, r)[:2] for r in range(comb(size, 2))] == list(combinations(range(size), 2))


def test_split_and_capacity_guard():
    for regime in ('shared', 'shifted', 'null', 'noisy_shared'):
        pool, dev, held, pair = family(0, 64, regime)
        assert len(pool) == len(set(pool)) == 64
        assert set(pair) <= set(pool)
        assert len(held) == len(set(held)) == 1024
        assert not set(dev) & set(held)
        assert select(pool, dev, 'signature', 42)[2] <= BUDGET
    with pytest.raises(ValueError, match='capacity'):
        roots(Random(0), 0, MASK ^ 255, 2)


def test_receipt():
    path = Path(__file__).resolve().parents[1] / 'output/verified_abstraction/vad_03a.json'
    expected = json.loads(path.read_text())
    actual = run()
    encoded = (json.dumps(actual, indent=2, sort_keys=True) + '\n').encode()
    assert len(actual['records']) == expected['records'] == 6144
    assert len(actual['summary']) == expected['summary_cells'] == 192
    assert actual['source_sha256'] == expected['source_sha256']
    assert sha256(encoded).hexdigest() == expected['full_receipt_sha256']
    assert [s for s in actual['summary'] if s['size']==64 and s['horizon']==1024] == expected['headline_cells']

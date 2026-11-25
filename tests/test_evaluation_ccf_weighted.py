from fractions import Fraction as F
from itertools import product
from random import Random

from spiral_ln.evaluation_ccf import partitions, risks
from spiral_ln.evaluation_ccf_weighted import frontier, selection, triangle_fixture


def independent_frontier(n, contexts, weights, k):
    points = set()
    total = sum(weights.values())
    for labels in product(range(k), repeat=n):
        fn = fp = 0
        for (c, x), w in weights.items():
            bit = contexts[c][x]
            if any(labels[x] == labels[y] and bit != z for y, z in contexts[c].items()):
                fn += w * bit
                fp += w * (1 - bit)
        points.add((F(fn, total), F(fp, total)))
    return frozenset(p for p in points if not any(q != p and q[0] <= p[0] and q[1] <= p[1] for q in points))


def census():
    rng = Random(20261125)
    count = tradeoffs = 0
    for _ in range(128):
        contexts = tuple({i: rng.randrange(2) for i in range(5) if rng.randrange(4)} or {0: 0}
                         for _ in range(4))
        weights = {(c, x): rng.randrange(1, 10) for c, ctx in enumerate(contexts) for x in ctx}
        for k in (1, 2, 3):
            actual = frontier(5, contexts, weights, k)
            assert actual == independent_frontier(5, contexts, weights, k)
            count += 1
            tradeoffs += len(actual) > 1
    return count, tradeoffs


def independent_selection(contexts, labels, joint, visibility):
    # Enumerate complete policies on reachable public transcript classes.
    rows = []
    for pair, mass in joint.items():
        if not mass:
            continue
        transcript = () if visibility == 'none' else pair if visibility == 'world' else tuple((c, labels[x]) for c, x in pair)
        errors = tuple(int(contexts[c][x] == 0 and any(v == 1 and labels[y] == labels[x]
                       for y, v in contexts[c].items())) for c, x in pair)
        rows.append((transcript, mass, errors))
    transcripts = list(dict.fromkeys(t for t, _, _ in rows))
    best = max(sum(w * err[policy[transcripts.index(t)]] for t, w, err in rows)
               for policy in product((0, 1), repeat=len(transcripts)))
    return F(best, sum(joint.values()))


def witness(hidden=False):
    contexts, weights, joint = triangle_fixture(hidden)
    for j in (0, 1):
        assert all(sum(w for pair, w in joint.items() if pair[j] == x) == m for x, m in weights.items())
    results = {}
    for p in partitions(3):
        if len(set(p)) > 2:
            continue
        passive = risks(contexts, p, weights)[1]
        values = tuple(selection(contexts, p, joint, v) for v in ('none', 'receipt', 'world'))
        assert values == tuple(independent_selection(contexts, p, joint, v) for v in ('none', 'receipt', 'world'))
        assert passive == values[0] <= values[1] <= values[2]
        results[''.join(map(str, p))] = values
    return results


def test_weighted_census():
    assert census()[0] == 384


def test_selection_changes_optimal_encoding():
    r = witness()
    assert r['001'] == (F(1, 10), F(1, 5), F(1, 5))
    assert r['011'] == (F(3, 20), F(3, 20), F(3, 20))
    assert min(r, key=lambda p: r[p][0]) == '001'
    assert min(r, key=lambda p: r[p][1]) == '011'
    assert min(r, key=lambda p: r[p][2]) == '011'


def test_hidden_mismatch():
    r = witness(True)
    assert r['001'] == (F(1, 10), F(1, 10), F(1, 5))

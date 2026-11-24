from fractions import Fraction as F
from itertools import product
from random import Random

from spiral_ln.evaluation_ccf_robust import codes, compromise_fixture, minimax, selection, sharp_flag_union


def policy_oracle(contexts, p, law, visibility):
    """Enumerate complete selector policies; compute errors directly."""
    rows = []
    for row, w in law.items():
        if not w:
            continue
        t = {'none': (), 'contexts': tuple(c for c, x in row),
             'receipt': tuple((c, p[x]) for c, x in row), 'world': row}[visibility]
        errors = tuple(int(contexts[c][x] == 0 and any(
            p[x] == p[y] and z == 1 for y, z in contexts[c].items())) for c, x in row)
        rows.append((t, w, errors))
    ts = list(dict.fromkeys(t for t, _, _ in rows))
    n = len(rows[0][2])
    return F(max(sum(w * err[pol[ts.index(t)]] for t, w, err in rows)
                 for pol in product(range(n), repeat=len(ts))), sum(law.values()))


def census():
    rng = Random(20261125)
    count = 0
    for _ in range(96):
        contexts = ({0: rng.randrange(2), 1: rng.randrange(2)},
                    {1: rng.randrange(2), 2: rng.randrange(2)})
        candidates = [(c, x) for c, ctx in enumerate(contexts) for x in ctx]
        n = rng.randrange(1, 5)
        laws = []
        for _ in range(2):
            law = {}
            for _ in range(4):
                row = tuple(rng.choice(candidates) for _ in range(n))
                law[row] = law.get(row, 0) + rng.randrange(1, 6)
            laws.append(law)
        for v in ('none', 'contexts', 'receipt', 'world'):
            opt, ps, table = minimax(contexts, 3, 2, laws, v)
            for p, vals in table.items():
                assert vals == tuple(policy_oracle(contexts, p, law, v) for law in laws)
                count += len(vals)
            other = min(max(policy_oracle(contexts, p, law, v) for law in laws)
                        for p in product(range(2), repeat=3))
            assert opt == other
        for p in codes(3, 2):
            for law in laws:
                vs = [selection(contexts, p, law, v) for v in ('none', 'contexts', 'receipt', 'world')]
                assert vs == sorted(vs)
    return count


def test_policy_census():
    assert census() == 3072


def test_compromise():
    ctx, masses, laws = compromise_fixture()
    for law in laws:
        for j in (0, 1):
            assert {x: sum(w for row, w in law.items() if row[j] == x) for x in masses} == masses
    best, ps, table = minimax(ctx, 3, 2, laws)
    assert table[(0, 0, 1)] == (F(1, 10), F(1, 5))
    assert table[(0, 1, 1)] == (F(1, 5), F(1, 10))
    assert table[(0, 1, 0)] == (F(3, 20), F(3, 20))
    assert best == F(3, 20) and ps == ((0, 1, 0),)
    for j, p in enumerate(((0, 0, 1), (0, 1, 1))):
        assert p == min(table, key=lambda q: table[q][j])
    for a in range(11):
        mix = {r: a * laws[0].get(r, 0) + (10-a) * laws[1].get(r, 0) for r in laws[0].keys() | laws[1].keys()}
        for p, vals in table.items():
            assert selection(ctx, p, mix) <= F(a, 10)*vals[0] + F(10-a, 10)*vals[1]


def test_sharp_union():
    for n in range(1, 9):
        for den in range(1, 13):
            for num in range(den+1):
                p = F(num, den)
                law = sharp_flag_union(n, p)
                w = sum(law.values())
                assert all(F(sum(m * row[j] for row, m in law.items()), w) == p for j in range(n))
                assert F(sum(m for row, m in law.items() if any(row)), w) == min(1, n*p)

from itertools import product
from spiral_ln.mic02 import FAMILIES, N, oracle, replay, root, score, start, walk


def test_replays():
    for f in FAMILIES:
        for seed in range(8):
            row = replay(f, seed)
            assert len(row['scores']) == 5
            assert all(row['oracle'] <= x <= row['initial'] for x in row['scores'])
            assert all(sorted(o) == list(range(N)) for o in row['orders'])


def test_derandomization_expectation():
    for seed in range(8):
        d = root('derandomization', seed)
        for p in product((-1, 0, 1), repeat=N):
            completions = [q for q in product((0, 1), repeat=N) if all(x == -1 or x == y for x, y in zip(p, q))]
            assert score('derandomization', d, p) * len(completions) == sum(score('derandomization', d, q) for q in completions)


def test_recurrence_minimality():
    for seed in range(12):
        d = root('recurrence', seed)
        p = walk('recurrence', d, list(reversed(range(N))))
        assert score('recurrence', d, p) == oracle('recurrence', d)
        m, b = d
        for i in range(N):
            assert 10 * (p[i] - 1) < 10 * b[i] + sum(m[i][j] * p[j] for j in range(N))
        assert sum(p) <= sum(start('recurrence', d))


def test_invalid_certificates():
    for f in FAMILIES:
        d = root(f, 1)
        try:
            score(f, d, (99,) * (N - 1))
        except ValueError:
            pass
        else:
            raise AssertionError('accepted malformed state')
    for f in ('recurrence', 'counting'):
        try:
            score(f, root(f, 1), (0,) * N)
        except ValueError:
            pass
        else:
            raise AssertionError('accepted infeasible state')

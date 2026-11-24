"""CCF-01C: exact minimax over a finite family of candidate laws."""
from collections import defaultdict
from fractions import Fraction
from itertools import product


def codes(n, k):
    """Restricted-growth labels with at most k labels, n,k >= 1."""
    if n < 1 or k < 1:
        raise ValueError('positive state and label counts required')
    def extend(p):
        if len(p) == n:
            yield p
        else:
            for z in range(min(k, max(p) + 2)):
                yield from extend(p + (z,))
    yield from extend((0,))


def selection(contexts, labels, law, visibility='receipt'):
    """Finite integer-mass law on ordered, equal-length candidate tuples.

    Candidate is (context index, state index). Publish exactly one candidate.
    The complete decoder accepts iff some feasible state in its cell is 1.
    """
    if not law or visibility not in ('none', 'contexts', 'receipt', 'world'):
        raise ValueError('empty law or invalid visibility')
    n = len(next(iter(law)))
    if n < 1:
        raise ValueError('empty candidate tuple')
    upper = {(c, labels[x]) for c, ctx in enumerate(contexts)
             for x, bit in ctx.items() if bit == 1}
    cells = defaultdict(lambda: [0] * n)
    total = 0
    for row, mass in law.items():
        if len(row) != n or not isinstance(mass, int) or mass < 0:
            raise ValueError('invalid law row')
        if not mass:
            continue
        if visibility == 'none':
            t = ()
        elif visibility == 'contexts':
            t = tuple(c for c, x in row)
        elif visibility == 'receipt':
            t = tuple((c, labels[x]) for c, x in row)
        else:
            t = row
        for j, (c, x) in enumerate(row):
            cells[t][j] += mass * int(contexts[c][x] == 0 and (c, labels[x]) in upper)
        total += mass
    if total == 0:
        raise ValueError('zero total mass')
    return Fraction(sum(max(v) for v in cells.values()), total)


def minimax(contexts, nstates, k, laws, visibility='receipt'):
    """Return optimum value, all optimal codes, and scenario-risk table."""
    laws = tuple(laws)
    if not laws:
        raise ValueError('empty scenario family')
    table = {p: tuple(selection(contexts, p, law, visibility) for law in laws)
             for p in codes(nstates, k)}
    best = min(map(max, table.values()))
    return best, tuple(p for p, v in table.items() if max(v) == best), table


def compromise_fixture():
    contexts = ({0: 0, 1: 1}, {1: 0, 2: 1}, {0: 0, 2: 1})
    masses = {(0, 0): 2, (1, 1): 2, (2, 0): 3,
              (0, 1): 4, (1, 2): 4, (2, 2): 5}
    def couple(a, b):
        law = {(x, x): w for x, w in masses.items()}
        law[a, a] -= 2
        law[b, b] -= 2
        law[a, b] = law[b, a] = 2
        return {r: w for r, w in law.items() if w}
    return contexts, masses, (couple((1, 1), (0, 1)), couple((0, 0), (1, 2)))


def sharp_flag_union(n, p):
    """Construct rational flag coupling attaining min(1,n*p).

    Uniform circle grid, p as a Fraction. Shift by one nth of the circle.
    """
    p = Fraction(p)
    if n < 1 or not 0 <= p <= 1:
        raise ValueError('invalid n or p')
    size = n * p.denominator
    length = p.numerator * n
    law = defaultdict(int)
    for z in range(size):
        row = tuple(int((z + j * p.denominator) % size < length) for j in range(n))
        law[row] += 1
    return dict(law)

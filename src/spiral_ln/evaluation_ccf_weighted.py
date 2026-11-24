"""Exact weighted CCF-01B objectives and two-candidate selection."""
from collections import defaultdict
from fractions import Fraction

from spiral_ln.evaluation_ccf import envelope, partitions, risks


def pareto(points):
    return frozenset(a for a in points if not any(
        b != a and b[0] <= a[0] and b[1] <= a[1] for b in points))


def frontier(n, contexts, weights, k):
    return pareto({risks(contexts, p, weights) for p in partitions(n)
                   if len(set(p)) <= k})


def selection(contexts, labels, joint, visibility):
    """joint maps ordered candidate-pair tuples to nonnegative integer masses.

    Each candidate is (context, state). Exactly one index must be selected.
    visibility is fixed before selection: none, receipt, or world.
    Returns optimal unconditional false-authorization mass, using U.
    """
    upper = envelope(contexts, labels)
    cells = defaultdict(lambda: [0, 0])
    total = 0
    for pair, mass in joint.items():
        if mass < 0 or len(pair) != 2:
            raise ValueError('invalid joint law')
        if visibility == 'none':
            t = ()
        elif visibility == 'receipt':
            t = tuple((c, labels[x]) for c, x in pair)
        elif visibility == 'world':
            t = pair
        else:
            raise ValueError('unknown visibility')
        for j, (c, x) in enumerate(pair):
            cells[t][j] += mass * (upper[c, labels[x]][1] - contexts[c][x])
        total += mass
    return Fraction(sum(max(v) for v in cells.values()), total)


def triangle_fixture(hidden=False):
    contexts = ({0: 0, 1: 1}, {1: 0, 2: 1}, {0: 0, 2: 1})
    weights = dict(zip(((0, 0), (1, 1), (2, 0), (0, 1), (1, 2), (2, 2)),
                       (2, 3, 4, 3, 4, 4)))
    a, b = (0, 0), (0, 1) if hidden else (2, 2)
    joint = {(x, x): w for x, w in weights.items()}
    joint[a, a] -= 2
    joint[b, b] -= 2
    joint[a, b] = joint[b, a] = 2
    return contexts, weights, joint

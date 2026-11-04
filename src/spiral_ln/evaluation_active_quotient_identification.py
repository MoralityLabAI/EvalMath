"""QI-01: exact budgeted identifiability of goal-preserving quotients.

Deterministic oracle: a finite family of binary hit/hold tables, with each
microstate/action cell individually addressable and queried before its
binary response. The goal is distinct; an exact zero-TV quotient needs as
many transient classes as distinct action-response rows.

No real-model inference or biological claim is made. A separate positive
Bernoulli likelihood calculation witnesses a noisy identification limit.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product


def _binary_worlds(worlds):
    worlds = tuple(tuple(tuple(row) for row in world) for world in worlds)
    if not worlds or not worlds[0] or not worlds[0][0]:
        raise ValueError("nonempty models, states, and actions required")
    n = len(worlds[0])
    d = len(worlds[0][0])
    if any(len(w) != n or any(len(row) != d or
                              any(type(x) is not int or x not in (0, 1)
                                  for x in row) for row in w)
           for w in worlds):
        raise ValueError("all candidate worlds must be aligned binary tables")
    return worlds, n, d


def exact_transient_classes(world):
    """One exact goal-visible class for every distinct action-rate vector."""
    return len(set(tuple(row) for row in world))


def decision_tree(worlds, max_transient_classes, probes=None):
    """Optimal worst-case zero-error property decision over all candidate worlds.

    Return (minimum depth, canonical decision tree), or None if permitted
    probes cannot distinguish worlds with different property labels.
    Tree nodes: ('answer',bool) or ('query',(state,action),zero,one).
    """
    worlds, n, d = _binary_worlds(worlds)
    if type(max_transient_classes) is not int or max_transient_classes < 1:
        raise ValueError("positive class budget required")
    if probes is None:
        probes = tuple(product(range(n), range(d)))
    else:
        probes = tuple(probes)
        if any(len(p) != 2 or any(type(v) is not int for v in p)
               or not 0 <= p[0] < n or not 0 <= p[1] < d
               for p in probes):
            raise ValueError("probes must be valid (microstate,action) cells")
        probes = tuple(sorted(set(probes)))
    labels = tuple(exact_transient_classes(w) <= max_transient_classes
                   for w in worlds)

    @lru_cache(None)
    def solve(possible):
        values = {labels[i] for i in possible}
        if len(values) == 1:
            return 0, ("answer", values.pop())
        best = None
        for i, a in probes:
            zero = tuple(x for x in possible if worlds[x][i][a] == 0)
            one = tuple(x for x in possible if worlds[x][i][a] == 1)
            if not zero or not one:
                continue
            left = solve(zero)
            right = solve(one)
            if left is None or right is None:
                continue
            depth = 1 + max(left[0], right[0])
            candidate = (depth, (i, a), ("query", (i, a), left[1], right[1]))
            if best is None or (candidate[0], candidate[1]) < (best[0], best[1]):
                best = candidate
        return None if best is None else (best[0], best[2])

    return solve(tuple(range(len(worlds))))


def evaluate_decision_tree(tree, world):
    count = 0
    while tree[0] == "query":
        i, a = tree[1]
        tree = tree[2 + world[i][a]]
        count += 1
    assert tree[0] == "answer"
    return tree[1], count


def under_budget(worlds, max_transient_classes, budget, probes=None):
    if type(budget) is not int or budget < 0:
        raise ValueError("nonnegative integer budget required")
    candidate = decision_tree(worlds, max_transient_classes, probes)
    return candidate is not None and candidate[0] <= budget


def single_flip_worlds(actions):
    """All-zero baseline and one alternative flipping each of its 2d cells."""
    if type(actions) is not int or actions < 1:
        raise ValueError("positive action count required")
    baseline = ((0,) * actions, (0,) * actions)
    worlds = [baseline]
    for state, action in product(range(2), range(actions)):
        rows = [list(r) for r in baseline]
        rows[state][action] = 1
        worlds.append(tuple(tuple(r) for r in rows))
    return tuple(worlds)


def first_row_support_worlds(actions, alternative_masks):
    """Baseline plus first-row alternatives identified by nonempty hit masks."""
    if type(actions) is not int or actions < 1:
        raise ValueError("positive action count required")
    masks = tuple(alternative_masks)
    if not masks or any(type(m) is not int or not (0 < m < 1 << actions)
                        for m in masks):
        raise ValueError("nonempty support masks required")
    zero = (0,) * actions
    return ((zero, zero),) + tuple((
        tuple(int(bool(mask & (1 << a))) for a in range(actions)), zero
    ) for mask in masks)


def stochastic_reset_trace_probability(rate_table, probes, outcomes):
    """Likelihood of a fixed addressed-probe record under iid reset trials."""
    table = tuple(tuple(Q(p) for p in row) for row in rate_table)
    if not table or not table[0] or any(len(row) != len(table[0])
       or any(not 0 <= p <= 1 for p in row) for row in table):
        raise ValueError("valid rectangular Bernoulli rates required")
    if len(probes) != len(outcomes):
        raise ValueError("probe/outcome length mismatch")
    result = Q(1)
    for (i, a), hit in zip(probes, outcomes):
        if (type(i) is not int or type(a) is not int or
            not 0 <= i < len(table) or not 0 <= a < len(table[0])
            or type(hit) is not int or hit not in (0, 1)):
            raise ValueError("invalid probe or observation")
        p = table[i][a]
        result *= p if hit else 1-p
    return result

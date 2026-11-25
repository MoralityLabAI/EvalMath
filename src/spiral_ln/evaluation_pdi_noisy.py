"""PDI-02: witness-backed authorization under noisy finite audits."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from spiral_ln.evaluation_pdi import holds, instance, probability


def incidence(claims, n):
    _, c = instance([1]+[0]*((1 << n)-1), claims)
    return tuple(sum((w for w, certs in c if any(m & (1 << i) for m in certs)), F(0))
                 for i in range(n))


def amplification_cap(claims, costs):
    costs = tuple(costs)
    if not costs or any(not isinstance(v, (int, F)) or v <= 0 for v in costs):
        raise ValueError('positive exact obligation weights required')
    return max(d/v for d, v in zip(incidence(claims, len(costs)), costs))


def false_weights(world, accepted, claims, costs):
    """Authorize every claim with an accepted certificate; return (false claim, false obligation) weight."""
    _, c = instance([1]+[0]*((1 << len(costs))-1), claims)
    if not 0 <= world < 1 << len(costs) or not 0 <= accepted < 1 << len(costs):
        raise ValueError('invalid masks')
    amplification_cap(c, costs)
    return (sum((w for w, ms in c if holds(accepted, ms) and not holds(world, ms)), F(0)),
            sum((F(v) for i, v in enumerate(costs) if accepted & ~world & (1 << i)), F(0)))


def selection_risk(f, m):
    f = probability(f)
    if type(m) is not int or m < 0:
        raise ValueError('nonnegative integer trial count required')
    return 1-(1-f)**m


def setup(prior, claims, channels, budget, penalty):
    p, c = instance(prior, claims)
    n = len(p).bit_length()-1
    a = tuple((i, probability(t), probability(f), cost) for i, t, f, cost in channels)
    if (type(budget) is not int or budget < 0 or not isinstance(penalty, (int, F)) or penalty < 0
        or any(type(i) is not int or not 0 <= i < n or type(cost) is not int or cost <= 0 for i, _, _, cost in a)):
        raise ValueError('invalid audit or penalty')
    return p, c, a, F(penalty)


def optimal_audit(prior, claims, channels, budget, penalty, *, adaptive=True):
    """Return exact (utility, true weight, false weight) for a Bayes-optimal policy.

    Channel (bit, sensitivity, false-positive rate, cost) is usable once;
    distinct channels on one bit have independent noise conditional on world.
    A bit is accepted iff at least one positive and no negative were observed.
    Each authorized claim must have an accepted certificate; authorize only
    if its posterior expected utility is strictly positive. Ties between
    policies prefer smaller false weight, then larger true weight.
    """
    p, c, a, penalty = setup(prior, claims, channels, budget, penalty)
    zero = (F(0),)*3

    def key(v):
        return v[0], -v[2], v[1]

    def add(x, y):
        return tuple(u+v for u, v in zip(x, y))

    def leaf(mass, pos, neg):
        t = f = F(0)
        for weight, ms in c:
            if holds(pos & ~neg, ms):
                good = weight*sum(v for w, v in enumerate(mass) if holds(w, ms))
                bad = weight*sum(v for w, v in enumerate(mass) if not holds(w, ms))
                if good > penalty*bad:
                    t += good
                    f += bad
        return t-penalty*f, t, f

    def step(mass, pos, neg, j, y):
        i, t, f, _ = a[j]
        likelihood = tuple(t if w & (1 << i) else f for w in range(len(p)))
        return (tuple(v*(s if y else 1-s) for v, s in zip(mass, likelihood)),
                pos | ((1 << i) if y else 0), neg | (0 if y else (1 << i)))

    @lru_cache(None)
    def dp(mass, pos, neg, remaining, b):
        best = leaf(mass, pos, neg)
        for j in remaining:
            if a[j][3] <= b:
                rest = tuple(k for k in remaining if k != j)
                value = add(*(dp(*step(mass, pos, neg, j, y), rest, b-a[j][3]) for y in (0, 1)))
                best = max(best, value, key=key)
        return best

    if adaptive:
        return dp(p, 0, 0, tuple(range(len(a))), budget)
    best = zero
    for k in range(len(a)+1):
        for subset in combinations(range(len(a)), k):
            if sum(a[j][3] for j in subset) <= budget:
                value = zero
                for outcomes in product((0, 1), repeat=k):
                    state = (p, 0, 0)
                    for j, y in zip(subset, outcomes):
                        state = step(*state, j, y)
                    value = add(value, leaf(*state))
                best = max(best, value, key=key)
    return best

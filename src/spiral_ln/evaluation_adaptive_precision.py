"""Certified adaptive likelihood precision (MIT-09).

Model (MIT-07): one hidden winning strategy with exact prior weights, perfect guess feedback,
once-only instruments with positive integer costs and finite likelihood matrices rows[y][i],
budget B. Queries whose cost leaves no unit for a guess are omitted (MIT-08 convention).

Precision: every instrument j is held at a level in LEVELS. A level k quantizes each
likelihood column to multiples of 2^-k by largest-remainder rounding, which normalizes
exactly. Level None is the full-precision rational column.

Two error notions are kept apart:
  * a priori envelope: computable from the quantized column and k alone, using the
    rounding lemma |p_y - q_y| < 2^-k. Controllers may use only this.
  * retrospective error: the actual total variation to the full-precision column. It needs
    ground truth and is reported for certificate tightness only.
"""
from fractions import Fraction as F
from itertools import product
from random import Random
import time

LEVELS = (1, 2, 4, 8, 16, None)
FULL_BITS = 64          # declared charge per entry for fetching a full-precision rational
ACQUIRE = 8             # declared fixed charge per refinement acquisition


def level_bits(level):
    return FULL_BITS if level is None else level


def quantize(p, bits):
    """Largest-remainder rounding of a probability vector to multiples of 2^-bits."""
    p = tuple(map(F, p))
    if bits is None:
        return p
    if any(x < 0 for x in p) or sum(p) != 1:
        raise ValueError('not a probability vector')
    unit = 1 << bits
    scaled = [x * unit for x in p]
    floors = [s.numerator // s.denominator for s in scaled]
    order = sorted(range(len(p)), key=lambda y: (-(scaled[y] - floors[y]), y))
    for y in order[:unit - sum(floors)]:
        floors[y] += 1
    return tuple(F(v, unit) for v in floors)


def tv(p, q):
    return sum(abs(a - b) for a, b in zip(p, q)) / 2


def envelope(q, bits):
    """A priori sup of TV(p, q) over all p with largest-remainder image q at this level.

    Uses only |p_y - q_y| < 2^-bits, p >= 0 and sum p = 1. Three valid bounds:
    floor(m/2)*u (sign count), sum min(u, q_y) (mass that can leave), sum min(u, 1-q_y)
    (mass that can arrive).
    """
    if bits is None:
        return F(0)
    u = F(1, 1 << bits)
    return min(F(len(q) // 2) * u, sum(min(u, x) for x in q),
               sum(min(u, 1 - x) for x in q), F(1))


def box(q, bits):
    """Per-entry interval containing the full-precision value: (lo, hi)."""
    if bits is None:
        return tuple(q), tuple(q)
    u = F(1, 1 << bits)
    return tuple(max(F(0), x - u) for x in q), tuple(min(F(1), x + u) for x in q)


class Env:
    """Exact environment. queries: [(cost, rows)] with rows[y][i] = L(y | i)."""

    def __init__(self, weights, queries, budget):
        w = tuple(map(F, weights))
        if not w or any(x < 0 for x in w) or sum(w) <= 0:
            raise ValueError('invalid prior')
        if type(budget) is not int or budget < 0:
            raise ValueError('invalid budget')
        qs = []
        for cost, rows in queries:
            rows = tuple(tuple(map(F, r)) for r in rows)
            if type(cost) is not int or cost < 1 or not rows or any(len(r) != len(w) for r in rows):
                raise ValueError('invalid query')
            if any(x < 0 for r in rows for x in r) or any(sum(r[i] for r in rows) != 1 for i in range(len(w))):
                raise ValueError('invalid likelihood')
            qs.append((cost, rows))
        total = sum(w)
        self.w = tuple(x / total for x in w)
        self.qs = tuple(qs)
        self.budget = budget
        self.n = len(w)

    def column(self, j, i):
        return tuple(r[i] for r in self.qs[j][1])

    def quantized(self, profile):
        """Environment with each instrument's columns quantized at profile[j]."""
        qs = []
        for j, (cost, rows) in enumerate(self.qs):
            cols = [quantize(self.column(j, i), profile[j]) for i in range(self.n)]
            qs.append((cost, tuple(tuple(c[y] for c in cols) for y in range(len(rows)))))
        return Env(self.w, qs, self.budget)


class Solver:
    """Exact expanded Bellman solver with action values and a deterministic policy.

    State: normalized masses (zero for eliminated strategies), guessed mask, available mask,
    remaining budget. Action order: guesses of unguessed strategies by index, then queries
    by index; the policy takes the first maximizer (as MIT-07's reference executor).
    """

    def __init__(self, env):
        self.env = env
        self.memo = {}

    def actions(self, guessed, avail, b):
        if b <= 0:
            return ()
        acts = [('g', i) for i in range(self.env.n) if not guessed >> i & 1]
        acts += [('q', j) for j, (c, _) in enumerate(self.env.qs) if avail >> j & 1 and c < b]
        return tuple(acts)

    def value(self, m, guessed, avail, b):
        total = sum(m)
        if b <= 0 or total == 0:
            return F(0)
        key = (tuple(x / total for x in m), guessed, avail, b)
        hit = self.memo.get(key)
        if hit is None:
            hit = max(self._q(key[0], guessed, avail, b, a) for a in self.actions(guessed, avail, b))
            self.memo[key] = hit
        return hit * total

    def _q(self, m, guessed, avail, b, a):
        kind, k = a
        if kind == 'g':
            return m[k] + self.value(m[:k] + (F(0),) + m[k + 1:], guessed | 1 << k, avail, b - 1)
        cost, rows = self.env.qs[k]
        return sum(self.value(tuple(x * r for x, r in zip(m, row)), guessed, avail & ~(1 << k), b - cost)
                   for row in rows)

    def qvalues(self, m, guessed, avail, b):
        """Normalized action values at a state with positive mass."""
        total = sum(m)
        return {a: self._q(m, guessed, avail, b, a) / total for a in self.actions(guessed, avail, b)}

    def policy(self, m, guessed, avail, b):
        acts = self.actions(guessed, avail, b)
        if not acts:
            return None
        if sum(m) == 0:
            return acts[0]
        q = self.qvalues(m, guessed, avail, b)
        best = max(q.values())
        return next(a for a in acts if q[a] == best)

    def optimum(self):
        e = self.env
        return self.value(e.w, 0, (1 << len(e.qs)) - 1, e.budget)


def deployed_value(true_env, approx_env):
    """Exact true closure of the approximate-optimal deterministic policy, and both optima."""
    sa = Solver(approx_env)
    st = Solver(true_env)
    qs_t, qs_a = true_env.qs, approx_env.qs

    def run(t, a, guessed, avail, b):
        if b <= 0 or sum(t) == 0:
            return F(0)
        act = sa.policy(a, guessed, avail, b)
        if act is None:
            return F(0)
        kind, k = act
        if kind == 'g':
            z = F(0)
            return t[k] + run(t[:k] + (z,) + t[k + 1:], a[:k] + (z,) + a[k + 1:], guessed | 1 << k, avail, b - 1)
        cost = qs_t[k][0]
        return sum(run(tuple(x * r for x, r in zip(t, rt)), tuple(x * r for x, r in zip(a, ra)),
                       guessed, avail & ~(1 << k), b - cost)
                   for rt, ra in zip(qs_t[k][1], qs_a[k][1]))

    full = (1 << len(qs_t)) - 1
    v_pi = run(true_env.w, approx_env.w, 0, full, true_env.budget)
    return v_pi, st.optimum(), sa.optimum(), len(sa.memo) + len(st.memo)


def survival(costs, eps, b):
    """min over subsets S with total cost <= b of prod_{j in S} (1 - eps_j); 1 if b < 0."""
    if b < 0:
        return F(1)
    dp = [F(1)] * (b + 1)
    for c, e in zip(costs, eps):
        for x in range(b, c - 1, -1):
            dp[x] = min(dp[x], (1 - e) * dp[x - c])
    return dp[b]


def instrument_errors(true_env, profile):
    """(a priori envelopes, retrospective TVs) per instrument at a precision profile."""
    pri, retro = [], []
    for j in range(len(true_env.qs)):
        cols = [true_env.column(j, i) for i in range(true_env.n)]
        qcols = [quantize(c, profile[j]) for c in cols]
        pri.append(max(envelope(q, profile[j]) for q in qcols))
        retro.append(max(tv(c, q) for c, q in zip(cols, qcols)))
    return pri, retro


def global_certificate(env, eps):
    """MIT-08 coupling bound with exact prior (d=0): (D, regret bound min(1, 2D))."""
    if env.budget == 0:
        return F(0), F(0)
    d = 1 - survival([c for c, _ in env.qs], eps, env.budget - 1)
    return d, min(F(1), 2 * d)


def step_cost(env, j, old, new):
    """Charge for refining instrument j from level old to level new (one acquisition)."""
    if new == old:
        return 0
    entries = env.n * len(env.qs[j][1])
    return ACQUIRE + entries * (level_bits(new) - level_bits(old))


def memory_bits(env, profile):
    return sum(env.n * len(rows) * level_bits(profile[j]) for j, (_, rows) in enumerate(env.qs))


def next_level(level):
    i = LEVELS.index(level)
    return LEVELS[i + 1] if i + 1 < len(LEVELS) else level


def predicted_envelope(env, j, level):
    """Worst-case envelope at a level not yet acquired (data independent)."""
    if level is None:
        return F(0)
    return min(F(1), F(len(env.qs[j][1]) // 2, 1 << level))


# ---------------------------------------------------------------- controllers

def _cert_global(true_env, profile, approx):
    pri, _ = instrument_errors(true_env, profile)
    return global_certificate(approx, pri)[1]


def run_controller(true_env, eta, order, certify=None, seed=0):
    """Refine-then-deploy controller.

    order: 'uniform' | 'random' | 'greedy' | 'costnorm' | 'margin'. Greedy and cost-normalized
    orders predict with the data-independent worst-case envelope of the next level; margin
    order predicts the decision certificate from the current columns with the next level's
    widths. No order reads columns before acquiring them.
    certify(true_env, profile, approx_env) -> regret certificate computable by the controller
    (it may read only quantized columns and levels; true_env is passed so the function can
    quantize, and the provided certificates never read full-precision values otherwise).
    """
    certify = certify or _cert_global
    k = len(true_env.qs)
    profile = [LEVELS[0]] * k
    cost = initial_cost(true_env)
    rng = Random(seed)
    trace = []
    t0 = time.perf_counter()
    while True:
        approx = true_env.quantized(profile)
        cert = certify(true_env, tuple(profile), approx)
        trace.append((tuple(profile), cert))
        if cert <= eta:
            break
        open_ = [j for j in range(k) if profile[j] is not None]
        if not open_:
            break
        if order == 'uniform':
            for j in open_:
                new = next_level(profile[j])
                cost += step_cost(true_env, j, profile[j], new)
                profile[j] = new
            continue
        if order == 'random':
            j = rng.choice(open_)
        else:
            pri, _ = instrument_errors(true_env, profile)
            best = None
            for j0 in open_:
                new = next_level(profile[j0])
                trial = list(pri)
                trial[j0] = predicted_envelope(true_env, j0, new)
                if order == 'margin':
                    from .evaluation_decision_certificate import policy_certificate
                    gain = cert - policy_certificate(true_env, tuple(profile), assumed={j0: new})['certificate']
                else:
                    gain = cert - global_certificate(approx, trial)[1]
                score = gain / step_cost(true_env, j0, profile[j0], new) if order == 'costnorm' else gain
                if best is None or score > best[0]:
                    best = (score, j0)
            j = best[1]
        new = next_level(profile[j])
        cost += step_cost(true_env, j, profile[j], new)
        profile[j] = new
    wall = time.perf_counter() - t0
    return dict(profile=tuple(profile), cost=cost, certificate=cert, steps=len(trace) - 1,
                wall_s=wall, memory_bits=memory_bits(true_env, profile), trace=trace)


def initial_cost(env):
    return sum(ACQUIRE + env.n * len(rows) * LEVELS[0] for _, rows in env.qs)


def direct_cost(env, profile):
    """Cost of reaching a profile from all-level-1 with one acquisition per raised instrument."""
    return initial_cost(env) + sum(step_cost(env, j, LEVELS[0], lv) for j, lv in enumerate(profile))


def bellman_oracle(true_env, feasible):
    """Minimum refinement cost to reach a profile with feasible(profile) True.

    Bellman recursion over the precision lattice; transitions raise one instrument to any
    higher level with one acquisition. feasible may use full-precision information
    (clairvoyant), so the result lower-bounds every online controller using that criterion.
    Returns (cost, profile) or (None, None) if no profile is feasible.
    """
    k = len(true_env.qs)
    memo = {}

    def go(profile):
        if profile in memo:
            return memo[profile]
        if feasible(profile):
            memo[profile] = (0, profile)
            return memo[profile]
        best = (None, None)
        for j in range(k):
            i = LEVELS.index(profile[j])
            for new in LEVELS[i + 1:]:
                nxt = profile[:j] + (new,) + profile[j + 1:]
                sub, end = go(nxt)
                if sub is None:
                    continue
                c = step_cost(true_env, j, profile[j], new) + sub
                if best[0] is None or c < best[0]:
                    best = (c, end)
        memo[profile] = best
        return best

    c, end = go((LEVELS[0],) * k)
    return (None, None) if c is None else (initial_cost(true_env) + c, end)


def enumerate_oracle(true_env, feasible):
    """Independent reference: minimum direct cost over all feasible profiles."""
    best = (None, None)
    for profile in product(LEVELS, repeat=len(true_env.qs)):
        if feasible(profile):
            c = direct_cost(true_env, profile)
            if best[0] is None or c < best[0]:
                best = (c, profile)
    return best

"""Depth-precision-compression frontier with certified regret (MIT-11).

A planner sees a quantized environment (MIT-09 levels), optionally compressed by merging
strategy classes, and searches to a limited depth on the dynamic signature quotient
(MIT-07 groups). Its receding-horizon policy is executed exactly in the true environment.

Certified regret of the deployed policy pi (model M = quantized and merged environment):
    V*_true - V_true(pi) <= [V*_M - V_M(pi)] + 2 D <= [UB_d - V_M(pi)] + 2 D,
where D = 1 - (1 - d) R is the MIT-08 coupling bound between truth and M (d: prior TV, the
instrument errors are quantization envelopes plus exact merge errors by the triangle
inequality), and UB_d is the depth-d optimistic search whose leaves use the information
relaxation E[top-b posterior mass | all remaining query outcomes] >= any continuation value.

Merging: exact merging (identical mass and signature) is unconditional. A class cap K merges
the closest pair of classes (largest per-instrument column TV, then mass gap) into a mass-
and count-weighted representative until at most K classes remain; its error is computed
exactly and charged to the certificate.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import product
import time
from .evaluation_adaptive_precision import Env, Solver, quantize, envelope, tv, survival

INF = None


def merge_classes(env, cap):
    """(merged Env, prior TV d, per-instrument merge errors, number of classes)."""
    k = len(env.qs)
    sig = [tuple(env.column(j, i) for j in range(k)) for i in range(env.n)]
    classes = {}
    for i in range(env.n):
        classes.setdefault((env.w[i], sig[i]), []).append(i)
    groups = [dict(members=v, mass=key[0], sig=key[1]) for key, v in classes.items()]
    while cap is not None and len(groups) > cap:
        best = None
        for a in range(len(groups)):
            for b in range(a + 1, len(groups)):
                ga, gb = groups[a], groups[b]
                dist = max(tv(x, y) for x, y in zip(ga['sig'], gb['sig']))
                key = (dist, abs(ga['mass'] - gb['mass']), a, b)
                if best is None or key < best:
                    best = key
        _, _, a, b = best
        ga, gb = groups[a], groups[b]
        na, nb = len(ga['members']) * ga['mass'], len(gb['members']) * gb['mass']
        tot = na + nb
        wa, wb = (na / tot, nb / tot) if tot else (F(1, 2), F(1, 2))
        sig2 = tuple(tuple(wa * x + wb * y for x, y in zip(ca, cb)) for ca, cb in zip(ga['sig'], gb['sig']))
        members = ga['members'] + gb['members']
        mass = (len(ga['members']) * ga['mass'] + len(gb['members']) * gb['mass']) / len(members)
        groups = [g for t, g in enumerate(groups) if t not in (a, b)] + [dict(members=members, mass=mass, sig=sig2)]
    w2 = [None] * env.n
    cols = [[None] * env.n for _ in range(k)]
    for g in groups:
        for i in g['members']:
            w2[i] = g['mass']
            for j in range(k):
                cols[j][i] = g['sig'][j]
    qs = [(c, [[cols[j][i][y] for i in range(env.n)] for y in range(len(rows))]) for j, (c, rows) in enumerate(env.qs)]
    merged = Env(w2, qs, env.budget)
    d = tv(env.w, merged.w)
    err = [max(tv(env.column(j, i), merged.column(j, i)) for i in range(env.n)) for j in range(k)]
    return merged, d, err, len(groups)


def groups_of(env, m, guessed, avail, quotient=True):
    """Canonical quotient groups (mass, remaining signature, count, members) at a history.
    Without quotient every live strategy is its own group."""
    k = len(env.qs)
    live = [j for j in range(k) if avail >> j & 1]
    acc = {}
    for i in range(env.n):
        if guessed >> i & 1 or m[i] == 0:
            continue
        key = (m[i], tuple(env.column(j, i) for j in live)) + (() if quotient else (i,))
        acc.setdefault(key, []).append(i)
    return sorted((key[0], key[1], len(v), tuple(v)) for key, v in acc.items()), live


class Planner:
    """Depth-limited search on quotient groups. depth None means exact (unbounded)."""

    def __init__(self, env, depth, quotient=True):
        self.env, self.depth, self.quotient = env, depth, quotient
        self.memo = {}
        self.costs = [c for c, _ in env.qs]

    def _key(self, groups):
        if self.quotient:
            return tuple((m, s, n) for m, s, n, _ in groups)
        return tuple((m, s, n, mem) for m, s, n, mem in groups)     # no coalescing across members

    def value(self, groups, live, b, d, upper):
        """Normalized value (lower: direct-guess leaves; upper: information-relaxation leaves)."""
        total = sum(m * n for m, _, n, _ in groups)
        if b <= 0 or total == 0:
            return F(0)
        key = (self._key(groups), tuple(live), b, d, upper)
        if key in self.memo:
            return self.memo[key]
        if d == 0:
            v = self._ub(groups, live, b) if upper else self._top(groups, b)
        else:
            v = max(q for _, q in self._actions(groups, live, b, d, upper))
        self.memo[key] = v
        return v

    def _top(self, groups, b):
        total = sum(m * n for m, _, n, _ in groups)
        v = F(0)
        for m, _, n, _ in sorted(groups, reverse=True):
            t = min(b, n)
            v += m * t
            b -= t
            if b == 0:
                break
        return v / total

    def _ub(self, groups, live, b):
        total = sum(m * n for m, _, n, _ in groups)
        alph = [range(len(self.env.qs[j][1])) for j in live]
        v = F(0)
        for ys in product(*alph):
            masses = []
            for m, s, n, _ in groups:
                p = m
                for col, y in zip(s, ys):
                    p *= col[y]
                masses.append((p, n))
            rem = b
            for p, n in sorted(masses, reverse=True):
                t = min(rem, n)
                v += p * t
                rem -= t
                if rem == 0:
                    break
        return v / total

    def _actions(self, groups, live, b, d, upper):
        """[(action, normalized value)]: ('g', group index) and ('q', instrument)."""
        total = sum(m * n for m, _, n, _ in groups)
        nd = None if d is None else d - 1
        out = []
        for gi, (m, s, n, mem) in enumerate(groups):
            rest = list(groups)
            if n == 1:
                rest.pop(gi)
            else:
                rest[gi] = (m, s, n - 1, mem[1:])
            rt = sum(x * c for x, _, c, _ in rest)
            out.append((('g', gi), (m + rt * self.value(rest, live, b - 1, nd, upper)) / total))
        for pos, j in enumerate(live):
            if self.costs[j] >= b:
                continue
            if all(s[pos] == groups[0][1][pos] for _, s, _, _ in groups):
                continue                                  # constant column: pure noise
            live2 = live[:pos] + live[pos + 1:]
            v = F(0)
            for y in range(len(self.env.qs[j][1])):
                acc = {}
                for m, s, n, mem in groups:
                    p = m * s[pos][y]
                    if p == 0:
                        continue
                    key = (p, s[:pos] + s[pos + 1:]) if self.quotient else (p, s[:pos] + s[pos + 1:], mem)
                    if key in acc:
                        acc[key] = (acc[key][0] + n, acc[key][1] + mem)
                    else:
                        acc[key] = (n, mem)
                g2 = sorted((key[0], key[1], n, mem) for key, (n, mem) in acc.items())
                v += sum(p * n for p, _, n, _ in g2) * self.value(g2, live2, b - self.costs[j], nd, upper)
            out.append((('q', j), v / total))
        return out

    def act(self, m, guessed, avail, b):
        """Receding-horizon action in strategy coordinates (guess the lowest-index member)."""
        groups, live = groups_of(self.env, m, guessed, avail, self.quotient)
        if b <= 0:
            return None
        if not groups:
            free = [i for i in range(self.env.n) if not guessed >> i & 1]
            return ('g', free[0]) if free else None
        acts = self._actions(groups, live, b, self.depth, False)
        best = max(v for _, v in acts)
        kind, x = next(a for a, v in acts if v == best)
        if kind == 'g':
            return ('g', min(groups[x][3]))
        return ('q', x)


def execute(true_env, model_env, policy):
    """Exact closure under true_env of a policy acting on model_env posteriors."""
    count = [0]

    def run(t, a, guessed, avail, b):
        if b <= 0 or sum(t) == 0:
            return F(0)
        act = policy(a, guessed, avail, b)
        count[0] += 1
        if act is None:
            return F(0)
        kind, k = act
        z = F(0)
        if kind == 'g':
            return t[k] + run(t[:k] + (z,) + t[k + 1:], a[:k] + (z,) + a[k + 1:], guessed | 1 << k, avail, b - 1)
        cost = true_env.qs[k][0]
        return sum(run(tuple(x * r for x, r in zip(t, rt)), tuple(x * r for x, r in zip(a, ra)),
                       guessed, avail & ~(1 << k), b - cost)
                   for rt, ra in zip(true_env.qs[k][1], model_env.qs[k][1]))

    full = (1 << len(true_env.qs)) - 1
    return run(true_env.w, model_env.w, 0, full, true_env.budget), count[0]


def configuration(true_env, bits, depth, cap, quotient=True, v_true_opt=None):
    """Plan, deploy and certify one (precision, depth, class cap) configuration."""
    k = len(true_env.qs)
    t0 = time.perf_counter()
    quant = true_env.quantized((bits,) * k)
    model, d, merr, ncls = merge_classes(quant, cap)
    planner = Planner(model, depth, quotient)
    v_true, decisions = execute(true_env, model, planner.act)
    v_model, _ = execute(model, model, planner.act)
    groups, live = groups_of(model, model.w, 0, (1 << k) - 1, quotient)
    ub = planner.value(groups, live, model.budget, depth, True) if depth is not None else v_model
    wall = time.perf_counter() - t0
    eps = []
    for j in range(k):
        e_q = max(envelope(quant.column(j, i), bits) for i in range(true_env.n))
        eps.append(min(F(1), e_q + merr[j]))
    D = F(0) if true_env.budget == 0 else 1 - (1 - d) * survival([c for c, _ in true_env.qs], eps, true_env.budget - 1)
    cert = min(F(1), max(F(0), ub - v_model) + 2 * D)
    if v_true_opt is None:
        v_true_opt = Solver(true_env).optimum()
    return dict(bits=bits, depth=depth, cap=cap, quotient=quotient, classes=ncls, regret=v_true_opt - v_true,
                certificate=cert, D=D, search_gap=max(F(0), ub - v_model), prior_tv=d, states=len(planner.memo),
                decisions=decisions, wall_s=wall, root_action=planner.act(model.w, 0, (1 << k) - 1, model.budget))

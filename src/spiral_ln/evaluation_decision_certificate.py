"""Decision-sensitive certificates for quantized likelihood models (MIT-10).

Setting and notation as in evaluation_adaptive_precision (MIT-09). A controller holds each
instrument at a precision level and sees only the quantized columns. For every column it
knows an interval box [lo, hi] for each true entry (rounding lemma) and an a priori TV
envelope e_j per instrument.

Sound stepwise certificate. At a history h with approximate posterior p~ and boxed true
unnormalized masses [lo_i, hi_i]:
  * d(h) = sup TV(true posterior, p~) over the boxes
         = max over subsets S of hi_S / (hi_S + lo_{S^c}) - p~(S)        (exact for boxes)
  * for every legal first action a, the MIT-08 coupling argument on the continuation gives
         |Q*_true(h, a) - Q*_approx(h, a)| <= Delta_h(a) = 1 - (1 - d(h)) R_a,
    R_guess = survival(A, b-2), R_query j = (1 - e_j) survival(A \\ j, b-1-c_j);
  * the executed action a* has true gap V*_true(h) - Q*_true(h, a*) <= g_h where
         g_h = max(0, max_{a != a*} [Q~(a) + Delta(a)] - [Q~(a*) - Delta(a*)]).
Performance difference: V*_true - V_true(pi) = sum_h W(h) gap(h), W(h) the true probability
of reaching h unresolved. Two valid bounds are combined: the path bound
P(h) = min(1, g_h + max_child P) and the mass bound T(h) = min(W+(h), W+(h) g_h + sum T),
with W+(h) = sum_i hi_i >= W(h); a subtree's total is at most W(h) <= W+(h).
"""
from fractions import Fraction as F
from .evaluation_adaptive_precision import (Env, Solver, LEVELS, quantize, envelope, box,
                                            survival, next_level, step_cost, initial_cost,
                                            global_certificate)


class View:
    """What a controller knows at a precision profile: quantized env, boxes, envelopes."""

    def __init__(self, true_env, profile, assumed=None, approx=None, radius=None):
        """assumed: {j: level} uses that level's box and envelope widths around the columns
        quantized at profile[j]. A controller uses it to predict the value of a refinement
        without reading the not-yet-acquired columns.

        approx/radius: an explicit approximate environment and, per instrument, a known
        entrywise radius r_j with |p - q| <= r_j (true_env and profile are then unused).
        The envelope is the box bound min(floor(m/2) r, sum min(r, q), sum min(r, 1-q))."""
        self.profile = tuple(profile) if profile is not None else None
        self.env = approx if approx is not None else true_env.quantized(profile)
        self.solver = Solver(self.env)
        self.lo, self.hi, self.eps = [], [], []
        for j, (_, rows) in enumerate(self.env.qs):
            cols = [tuple(r[i] for r in rows) for i in range(self.env.n)]
            if approx is not None:
                rj = radius[j]
                boxes = [(tuple(max(F(0), x - rj) for x in c), tuple(min(F(1), x + rj) for x in c)) for c in cols]
                env_j = max(min(F(len(c) // 2) * rj, sum(min(rj, x) for x in c), sum(min(rj, 1 - x) for x in c), F(1))
                            for c in cols)
            else:
                lv = (assumed or {}).get(j, profile[j])
                boxes = [box(c, lv) for c in cols]
                env_j = max(envelope(c, lv) for c in cols)
            self.lo.append(tuple(tuple(bx[0][y] for bx in boxes) for y in range(len(rows))))
            self.hi.append(tuple(tuple(bx[1][y] for bx in boxes) for y in range(len(rows))))
            self.eps.append(env_j)


def posterior_tv_bound(m, lo, hi):
    """sup over true masses in [lo, hi] of TV(normalize(true), normalize(m)); m has positive sum."""
    idx = [i for i in range(len(m)) if hi[i] > 0 or m[i] > 0]
    total = sum(m)
    best = F(0)
    for mask in range(1, 1 << len(idx)):
        s = [idx[k] for k in range(len(idx)) if mask >> k & 1]
        hs = sum(hi[i] for i in s)
        if hs == 0:
            continue
        lc = sum(lo[i] for i in idx if i not in s)
        best = max(best, hs / (hs + lc) - sum(m[i] for i in s) / total)
    return min(F(1), best)


def action_radius(view, a, d, avail, b, rule='sound'):
    costs = [c for c, _ in view.env.qs]
    live = [j for j in range(len(costs)) if avail >> j & 1]
    kind, k = a
    if rule == 'local':                    # unsafe: immediate instrument error only
        return view.eps[k] if kind == 'q' else F(0)
    if kind == 'g':
        r = survival([costs[j] for j in live], [view.eps[j] for j in live], b - 2)
    else:
        rest = [j for j in live if j != k]
        r = (1 - view.eps[k]) * survival([costs[j] for j in rest], [view.eps[j] for j in rest],
                                         b - 1 - costs[k])
    return 1 - (1 - d) * r


def step_gap(view, m, lo, hi, guessed, avail, b, rule='sound'):
    """(executed action, certified gap g_h, posterior bound d) at one history."""
    s = view.solver
    acts = s.actions(guessed, avail, b)
    if not acts:
        return None, F(0), F(0)
    if sum(m) == 0:
        return acts[0], F(1), F(1)
    q = s.qvalues(m, guessed, avail, b)
    best = max(q.values())
    star = next(a for a in acts if q[a] == best)
    d = F(0) if rule in ('plugin', 'local') else posterior_tv_bound(m, lo, hi)
    rad = {a: action_radius(view, a, d, avail, b, rule) for a in acts}
    others = [q[a] + rad[a] for a in acts if a != star]
    g = max(F(0), max(others) - (q[star] - rad[star])) if others else F(0)
    return star, min(F(1), g), d


def children(view, act, m, lo, hi, guessed, avail, b):
    kind, k = act
    z = F(0)
    if kind == 'g':
        yield (m[:k] + (z,) + m[k + 1:], lo[:k] + (z,) + lo[k + 1:], hi[:k] + (z,) + hi[k + 1:],
               guessed | 1 << k, avail, b - 1)
        return
    cost, rows = view.env.qs[k]
    for y, row in enumerate(rows):
        h2 = tuple(x * u for x, u in zip(hi, view.hi[k][y]))
        if sum(h2) == 0:
            continue
        yield (tuple(x * r for x, r in zip(m, row)), tuple(x * u for x, u in zip(lo, view.lo[k][y])),
               h2, guessed, avail & ~(1 << k), b - cost)


def policy_certificate(true_env, profile, rule='sound', assumed=None, approx=None, radius=None):
    """Certified regret bound of the approximate-optimal policy at this profile.

    The sound certificate is min(global MIT-08 bound 2D, stepwise path/mass bound).

    rule: 'sound' (theorem above) or the unsafe variants 'plugin' (posterior drift ignored),
    'local' (immediate instrument error only, drift ignored), 'rootonly' (only the root
    decision is certified). Returns dict(certificate, histories, root_gap).
    """
    view = View(true_env, profile, assumed, approx, radius)
    e = view.env
    count = [0]

    def go(m, lo, hi, guessed, avail, b):
        wplus = sum(hi)
        if b <= 0 or wplus == 0:
            return F(0), F(0)
        act, g, _ = step_gap(view, m, lo, hi, guessed, avail, b, rule)
        if act is None:
            return F(0), F(0)
        count[0] += 1
        if sum(m) == 0:
            return F(1), wplus
        kids = [go(*c) for c in children(view, act, m, lo, hi, guessed, avail, b)]
        p = min(F(1), g + max((k[0] for k in kids), default=F(0)))
        t = min(wplus, wplus * g + sum(k[1] for k in kids))
        return p, t

    full = (1 << len(e.qs)) - 1
    root = step_gap(view, e.w, e.w, e.w, 0, full, e.budget, rule)
    if rule == 'rootonly':
        return dict(certificate=root[1], histories=1, root_gap=root[1])
    p, t = go(e.w, e.w, e.w, 0, full, e.budget)
    out = dict(stepwise=min(p, t), histories=count[0], root_gap=root[1])
    if rule == 'sound':
        # Both bounds are valid for the same deployed policy, so their minimum is.
        glob = global_certificate(e, view.eps)[1]
        out.update(global_bound=glob, certificate=min(glob, out['stepwise']))
    else:
        out['certificate'] = out['stepwise']
    return out


def online_controller(true_env, eta, start=None):
    """Certify-as-you-go: before each action, refine until its gap is at most eta / B.

    Refinement picks the open instrument whose next level is predicted (current columns,
    next level's box widths; the new columns are not read before paying) to lower the gap most
    per unit cost (ties: lowest index); with no decrease available it refines the cheapest open
    instrument. Evaluated exactly over the true outcome tree. Returns expected refinement
    cost (initial acquisition included), true closure, certified regret bound and counts.
    Refinements persist along a path; the approximate posterior is recomputed from the
    observed history whenever precision changes.
    """
    B = true_env.budget
    slack = F(0) if B == 0 else eta / B
    k = len(true_env.qs)
    views = {}

    def view_of(p):
        if p not in views:
            views[p] = View(true_env, p)
        return views[p]

    def replay(view, hist):
        m = lo = hi = view.env.w
        for ev in hist:
            if ev[0] == 'g':
                i = ev[1]
                z = F(0)
                m, lo, hi = m[:i] + (z,) + m[i + 1:], lo[:i] + (z,) + lo[i + 1:], hi[:i] + (z,) + hi[i + 1:]
            else:
                _, j, y = ev
                row = view.env.qs[j][1][y]
                m = tuple(x * r for x, r in zip(m, row))
                lo = tuple(x * u for x, u in zip(lo, view.lo[j][y]))
                hi = tuple(x * u for x, u in zip(hi, view.hi[j][y]))
        return m, lo, hi

    stats = dict(decisions=0, refinements=0)

    def go(t, hist, profile, guessed, avail, b):
        """Returns (success mass, expected added cost mass, certified gap path max)."""
        if b <= 0 or sum(t) == 0:
            return F(0), F(0), F(0)
        cost = F(0)
        while True:
            view = view_of(profile)
            m, lo, hi = replay(view, hist)
            act, g, _ = step_gap(view, m, lo, hi, guessed, avail, b)
            if act is None:
                return F(0), F(0), F(0)
            if g <= slack:
                break
            open_ = [j for j in range(k) if profile[j] is not None]
            if not open_:
                break
            best = None
            for j in open_:
                nxt = profile[:j] + (next_level(profile[j]),) + profile[j + 1:]
                v2 = View(true_env, profile, {j: nxt[j]})      # prediction: no peeking
                m2, lo2, hi2 = replay(v2, hist)
                g2 = step_gap(v2, m2, lo2, hi2, guessed, avail, b)[1]
                c = step_cost(true_env, j, profile[j], nxt[j])
                score = (g - g2) / c
                if best is None or score > best[0] or (score == best[0] and c < best[2]):
                    best = (score, nxt, c)
            profile = best[1]
            cost += best[2]
            stats['refinements'] += 1
        stats['decisions'] += 1
        mass = sum(t)
        kind, i = act
        if kind == 'g':
            z = F(0)
            s, c2, gp = go(t[:i] + (z,) + t[i + 1:], hist + (('g', i),), profile, guessed | 1 << i, avail, b - 1)
            return t[i] + s, mass * cost + c2, g + gp
        tc, rows = true_env.qs[i]
        s = c2 = F(0)
        gp = F(0)
        for y, row in enumerate(rows):
            r = go(tuple(x * u for x, u in zip(t, row)), hist + (('q', i, y),), profile, guessed,
                   avail & ~(1 << i), b - tc)
            s, c2, gp = s + r[0], c2 + r[1], max(gp, r[2])
        return s, mass * cost + c2, g + gp

    profile = tuple(start or (LEVELS[0],) * k)
    v, c, gp = go(true_env.w, (), profile, 0, (1 << k) - 1, B)
    return dict(value=v, expected_cost=initial_cost(true_env) + c, certificate=min(F(1), gp),
                views=len(views), **stats)

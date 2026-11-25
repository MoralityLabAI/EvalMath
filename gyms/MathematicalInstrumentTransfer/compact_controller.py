"""MIT-12: compact recurrent controller vs relational/scalar MLPs, LDT router and symbolic search.

Decisions are taken on the quotient state (groups of equal mass and equal remaining signature) of the
exact noisy-instrument model of src/spiral_ln (Env, Solver, Planner). Oracle labels are exact Fractions
from Planner(depth=None); tests check them against Solver.qvalues. Learned controllers only propose;
an external depth-2 certificate (LB_2(a) >= max_{a'!=a} UB_2(a') - eta) authorizes or falls back to exact search.
"""
import sys, os, json, time, math, hashlib
from fractions import Fraction as F
from random import Random
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'src'))
sys.path.insert(0, str(HERE))
from spiral_ln.evaluation_adaptive_precision import Env, Solver
from spiral_ln.evaluation_depth_precision import Planner, groups_of

OUT = HERE / 'results' / 'mit12'
SPLITS = {'train': 100000, 'dev': 200000, 'eval': 300000}      # disjoint seed ranges
FAMILIES = ('random', 'palette', 'higher')
KMAX, YMAX = 4, 3
NS = 3 + 5 * KMAX
NA = 9 + NS
NSCAL, NREL, NROUTE = 14, 8, 12
EXPERTS = ('direct', 'greedy', 'depth2', 'depth3')               # cheapest first; 'exact' is the fallback


# ------------------------------------------------------------------ root generators

def _composition(r, total, parts):
    cuts = sorted(r.randint(0, total) for _ in range(parts - 1))
    pts = [0] + cuts + [total]
    return tuple(F(pts[i + 1] - pts[i], total) for i in range(parts))


def gen_random(seed):
    r = Random(seed)
    n, k, budget = r.randint(7, 10), r.randint(3, 4), r.randint(4, 6)
    w = [r.choice((1, 2)) for _ in range(n)]
    qs = []
    for _ in range(k):
        ny, cost, den = r.choice((2, 3)), r.choice((1, 1, 2)), r.choice((4, 6, 10))
        types = [_composition(r, den, ny) for _ in range(r.randint(2, 4))]
        pick = [r.randrange(len(types)) for _ in range(n)]
        qs.append((cost, [[types[pick[i]][y] for i in range(n)] for y in range(ny)]))
    return Env(w, qs, budget), dict(family='random', seed=seed)


def gen_palette(seed):
    r = Random(seed)
    n, k, budget = r.randint(9, 14), r.randint(3, 4), r.randint(4, 6)
    p = r.randint(4, 6)
    sigw = [r.choice((1, 2)) for _ in range(p)]
    sigs = []
    for _ in range(p):
        sig = []
        for j in range(k):
            sig.append(_composition(r, r.choice((4, 6, 10)), 2 if j % 2 == 0 else r.choice((2, 3))))
        sigs.append(sig)
    ny = [max(len(s[j]) for s in sigs) for j in range(k)]
    pick = [i % p if i < p else r.randrange(p) for i in range(n)]
    costs = [r.choice((1, 1, 2)) for _ in range(k)]
    qs = []
    for j in range(k):
        rows = []
        for y in range(ny[j]):
            rows.append([sigs[pick[i]][j][y] if y < len(sigs[pick[i]][j]) else F(0) for i in range(n)])
        for i in range(n):                                          # renormalize ragged columns
            assert sum(rows[y][i] for y in range(ny[j])) == 1
        qs.append((costs[j], rows))
    return Env([sigw[pick[i]] for i in range(n)], qs, budget), dict(family='palette', seed=seed)


PAT = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]


def parity_pair(r):
    """MIT-04 construction: counts a and b = a + (-1)^|p| share all pairwise marginals."""
    a = tuple(r.randrange(1, 5) for _ in PAT)
    return a, tuple(n + (-1) ** sum(p) for n, p in zip(a, PAT))


def gen_higher(seed):
    """Deterministic parity columns (eps=0) or noisy ones; even seeds are filtered to roots where
    the exact optima of the aliased pair differ (aliasing witness), odd seeds are unfiltered."""
    from higher_order import optimum
    r = Random(seed)
    tries = 0
    while True:
        budget = r.randint(3, 5)
        a, b = parity_pair(r)
        tries += 1
        if seed % 2 == 1 or optimum(a, budget) != optimum(b, budget) or tries >= 400:
            break
    flag = optimum(a, budget) != optimum(b, budget)
    counts = a if r.random() < 0.5 else b
    eps = r.choice((F(0), F(0), F(1, 10), F(1, 5)))
    pats = [p for p, c in zip(PAT, counts) for _ in range(c)]
    n = len(pats)
    qs = []
    for j in range(3):
        rows = [[(1 - eps) if p[j] == y else eps for p in pats] for y in (0, 1)]
        qs.append((1, rows))
    return Env([1] * n, qs, budget), dict(family='higher', seed=seed, alias_witness=bool(flag), eps=str(eps),
                                           orientation='a' if counts == a else 'b')


GEN = dict(random=gen_random, palette=gen_palette, higher=gen_higher)


def root_list(split, per_family):
    """Deterministic list of (family, seed); seeds from disjoint ranges, one root per seed."""
    base = SPLITS[split]
    return [(f, base + 1000 * fi + i) for fi, f in enumerate(FAMILIES) for i in range(per_family)]


def make_root(family, seed):
    env, meta = GEN[family](seed)
    return env, meta


# ------------------------------------------------------------------ quotient-state operations
# state = (groups, live, b); groups = tuple of (mass, signature, count) sorted; signature is a tuple of
# per-live-instrument likelihood columns; works for Fraction and float masses.

class Ctx:
    def __init__(self, env):
        self.env = env
        self.costs = [c for c, _ in env.qs]
        self.nouts = [len(rows) for _, rows in env.qs]
        self.k = len(env.qs)
        self.root = None

    def root_state(self):
        env = self.env
        groups, live = groups_of(env, env.w, 0, (1 << self.k) - 1)
        return tuple((m, s, n) for m, s, n, _ in groups), tuple(live), env.budget


def total_of(gs):
    return sum(m * n for m, _, n in gs)


def actions(ctx, state):
    gs, live, b = state
    if b <= 0 or not gs:
        return []
    out = [('g', gi) for gi in range(len(gs))]
    for pos, j in enumerate(live):
        if ctx.costs[j] >= b or all(g[1][pos] == gs[0][1][pos] for g in gs):
            continue
        out.append(('q', j))
    return out


def step(ctx, state, a):
    """(immediate mass, [(child total mass, child state)]) so that value = (imm + sum w*V(child))/total."""
    gs, live, b = state
    if a[0] == 'g':
        m, s, n = gs[a[1]]
        rest = list(gs)
        if n == 1:
            rest.pop(a[1])
        else:
            rest[a[1]] = (m, s, n - 1)
        rt = sum(x * c for x, _, c in rest)
        return m, ([(rt, (tuple(rest), live, b - 1))] if rt else [])
    j = a[1]
    pos = live.index(j)
    live2 = live[:pos] + live[pos + 1:]
    kids = []
    for y in range(ctx.nouts[j]):
        acc = {}
        for m, s, n in gs:
            p = m * s[pos][y]
            if p == 0:
                continue
            key = (p, s[:pos] + s[pos + 1:])
            acc[key] = acc.get(key, 0) + n
        g2 = tuple(sorted((kk[0], kk[1], n) for kk, n in acc.items()))
        w = total_of(g2)
        if w:
            kids.append((w, (g2, live2, b - ctx.costs[j])))
    return 0, kids


def top(gs, b):
    v = 0
    for m, _, n in sorted(gs, key=lambda g: -g[0]):
        t = min(b, n)
        v += m * t
        b -= t
        if b <= 0:
            break
    return v


def planner_groups(state):
    return [(m, s, n, ()) for m, s, n in state[0]]


def planner_values(pl, state, d, upper):
    return [v for _, v in pl._actions(planner_groups(state), list(state[1]), state[2], d, upper)]


def first_argmax(vals):
    best = max(vals)
    return next(i for i, v in enumerate(vals) if v == best)


def to_float(state):
    gs, live, b = state
    return (tuple((float(m), tuple(tuple(float(x) for x in col) for col in s), n) for m, s, n in gs), live, b)


# ------------------------------------------------------------------ features (float states)

def analyse(ctx, state, alist):
    """Per action: (immediate mass, children, one-step lower bound LB0 as normalized float)."""
    gs, live, b = state
    total = total_of(gs)
    info = []
    for a in alist:
        imm, kids = step(ctx, state, a)
        lb0 = (imm + sum(top(cs[0], cs[2]) for _, cs in kids)) / total
        info.append((imm, kids, lb0))
    return info, total


def scalar_feats(ctx, state, alist, ana=None):
    gs, live, b = state
    info, total = ana or analyse(ctx, state, alist)
    base = top(gs, b) / total
    lbs = [x[2] for x in info]
    best = max(lbs) if lbs else 0.0
    nmem = sum(n for _, _, n in gs)
    rows = []
    for a, (imm, kids, lb0) in zip(alist, info):
        isg = a[0] == 'g'
        cost = 1 if isg else ctx.costs[a[1]]
        ps = [w / total for w, _ in kids] if not isg else [1.0]
        ent = -sum(p * math.log(p) for p in ps if p > 0) / math.log(3)
        rows.append([float(isg), float(not isg), cost / b, b / 5.0, imm / total, lb0, lb0 - base, lb0 - best,
                     max(ps), min(ps), ent, len(gs) / 10.0, len(live) / 4.0, nmem / 12.0])
    return rows


def rel_feats(ctx, state, alist, ana=None):
    """Pairwise action-interaction features: conditional two-step gains and intersection masses."""
    gs, live, b = state
    info, total = ana or analyse(ctx, state, alist)
    rows = []
    for a, (imm, kids, lb0) in zip(alist, info):
        gains_max, probs, gains_mean, cells_max, cells_mean, useful, used = [], [], [], [], [], 0, set()
        for w, cs in kids:
            ct = total_of(cs[0])
            cb = top(cs[0], cs[2]) / ct
            gl, cl = [], []
            for a2 in actions(ctx, cs):
                if a2[0] != 'q':
                    continue
                _, k2 = step(ctx, cs, a2)
                v2 = sum(top(c2[0], c2[2]) for _, c2 in k2) / ct
                gl.append(v2 - cb)
                cl.append(min([x / ct for x, _ in k2] + [0.0] * (len(k2) < ctx.nouts[a2[1]])))
                if v2 - cb > 1e-12:
                    used.add(a2[1])
            probs.append(w / total)
            gains_max.append(max(gl, default=0.0))
            gains_mean.append(sum(gl) / len(gl) if gl else 0.0)
            cells_max.append(max(cl, default=0.0))
            cells_mean.append(sum(cl) / len(cl) if cl else 0.0)
            useful += gains_max[-1] > 1e-12
        np_ = max(1, len(kids))
        rows.append([sum(p * g for p, g in zip(probs, gains_max)), max(gains_max, default=0.0),
                     min(gains_max, default=0.0), sum(p * g for p, g in zip(probs, gains_mean)),
                     max(cells_max, default=0.0), sum(p * c for p, c in zip(probs, cells_mean)),
                     len(used) / 4.0, useful / np_])
    return rows


def shuffle_state(state):
    """Shuffle strategy-to-column membership within equal-mass classes, per instrument, preserving masses,
    per-instrument column multisets and counts. Returns (state, group map, changed flag)."""
    gs, live, b = state
    members = []
    for gi, (m, s, n) in enumerate(gs):
        members += [(m, gi, s)] * n
    classes = {}
    for idx, mem in enumerate(members):
        classes.setdefault(mem[0], []).append(idx)
    newsig = [list(mem[2]) for mem in members]
    for idxs in classes.values():
        K = len(idxs)
        if K < 2:
            continue
        for pos in range(len(live)):
            shift = (pos + 1) % K
            if shift:
                for t, idx in enumerate(idxs):
                    newsig[idx][pos] = members[idxs[(t + shift) % K]][2][pos]
    acc, first = {}, {}
    for idx, mem in enumerate(members):
        key = (mem[0], tuple(newsig[idx]))
        acc[key] = acc.get(key, 0) + 1
        first.setdefault(mem[1], key)
    groups = tuple(sorted((k[0], k[1], n) for k, n in acc.items()))
    index = {(m, s): i for i, (m, s, _) in enumerate(groups)}
    gmap = [index[first[gi]] for gi in range(len(gs))]
    return (groups, live, b), gmap, groups != gs


def rel_feats_sham(ctx, state, alist):
    st2, gmap, _ = shuffle_state(state)
    a2 = [('g', gmap[a[1]]) if a[0] == 'g' else a for a in alist]
    return rel_feats(ctx, st2, a2)


def _tok(ctx, m, s, n, live, total, b):
    v = [m * n / total, m / total, n / 8.0] + [0.0] * (5 * KMAX)
    for pos, j in enumerate(live):
        o = 3 + 5 * j
        v[o] = 1.0
        v[o + 1] = ctx.costs[j] / 2.0
        for y, p in enumerate(s[pos]):
            v[o + 2 + y] = float(p)
    return v


def tokens(ctx, state, alist, gmap=None):
    """Strategy tokens (one per group) and action tokens for the set encoder."""
    gs, live, b = state
    total = total_of(gs)
    S = [_tok(ctx, m, s, n, live, total, b) for m, s, n in gs]
    A = []
    for a in alist:
        v = [0.0] * NA
        if a[0] == 'g':
            gi = gmap[a[1]] if gmap else a[1]
            v[0], v[6], v[7], v[8] = 1.0, 1.0 / b, b / 5.0, 0.0
            v[9:9 + NS] = S[gi]
        else:
            v[1] = 1.0
            v[2 + a[1]] = 1.0
            v[6], v[7] = ctx.costs[a[1]] / b, b / 5.0
        A.append(v)
    return S, A


def tokens_sham(ctx, state, alist):
    st2, gmap, _ = shuffle_state(state)
    return tokens(ctx, st2, alist, gmap)


def route_feats(ctx, state, alist, ana):
    gs, live, b = state
    info, total = ana
    base = top(gs, b) / total
    lbs = sorted([x[2] for x in info], reverse=True) + [0.0, 0.0]
    shares = sorted([m * n / total for m, _, n in gs], reverse=True) + [0.0, 0.0]
    ent = -sum(p * math.log(p) for p in shares if p > 0)
    nq = sum(a[0] == 'q' for a in alist)
    return [b / 5.0, len(gs) / 10.0, len(live) / 4.0, base, lbs[0] - base, lbs[0] - lbs[1], len(alist) / 14.0,
            shares[0], shares[0] - shares[1], ent / math.log(10), nq / 4.0, sum(n for _, _, n in gs) / 12.0]


def state_features(ctx, state, which=('scalar', 'rel', 'rel_sham', 'tok', 'tok_sham', 'route', 'lb0')):
    """Requested feature blocks for a state (exact Fractions in, floats out)."""
    fs = to_float(state)
    alist = actions(ctx, state)
    out = {'actions': alist}
    ana = analyse(ctx, fs, alist) if {'scalar', 'rel', 'route', 'lb0'} & set(which) else None
    if 'scalar' in which:
        out['scalar'] = scalar_feats(ctx, fs, alist, ana)
    if 'rel' in which:
        out['rel'] = rel_feats(ctx, fs, alist, ana)
    if 'rel_sham' in which:
        out['rel_sham'] = rel_feats_sham(ctx, fs, alist)
    if 'tok' in which:
        out['tok'] = tokens(ctx, fs, alist)
    if 'tok_sham' in which:
        out['tok_sham'] = tokens_sham(ctx, fs, alist)
    if 'route' in which:
        out['route'] = route_feats(ctx, fs, alist, ana)
    if 'lb0' in which:
        out['lb0'] = [x[2] for x in ana[0]]
    return out


# ------------------------------------------------------------------ exact oracle records

class Oracle:
    """Per-root exact machinery. One Planner holds exact, depth-2 and depth-3 memos (keys include d)."""

    def __init__(self, env):
        self.env = env
        self.ctx = Ctx(env)
        self.pl = Planner(env, None)
        self.cache = {}

    def rec(self, state):
        key = (state[0], state[1], state[2])
        r = self.cache.get(key)
        if r is None:
            alist = actions(self.ctx, state)
            q = planner_values(self.pl, state, None, False)
            assert len(q) == len(alist)
            lb2 = planner_values(self.pl, state, 2, False)
            ub2 = planner_values(self.pl, state, 2, True)
            lb3 = planner_values(self.pl, state, 3, False)
            r = dict(state=state, actions=alist, q=q, lb2=lb2, ub2=ub2, lb3=lb3)
            r['best'] = max(q)
            r['opt'] = first_argmax(q)
            self.cache[key] = r
        return r


def enumerate_states(orc, rng, cap=250):
    """Reachable states under the exact-optimal policy plus the children of one random deviation per state."""
    root = orc.ctx.root_state()
    seen, order, stack = {}, [], [root]
    dev = []
    while stack and len(order) < cap:
        st = stack.pop()
        key = (st[0], st[1], st[2])
        if key in seen or st[2] <= 0 or not st[0]:
            continue
        seen[key] = True
        order.append(st)
        r = orc.rec(st)
        _, kids = step(orc.ctx, st, r['actions'][r['opt']])
        stack.extend(c for _, c in kids)
        worse = [i for i, v in enumerate(r['q']) if v < r['best']]
        if worse:
            i = worse[rng.randrange(len(worse))]
            dev.extend(c for _, c in step(orc.ctx, st, r['actions'][i])[1])
    for st in dev:
        key = (st[0], st[1], st[2])
        if key not in seen and st[2] > 0 and st[0]:
            seen[key] = True
            order.append(st)
    return order


def root_records(family, seed, cap=250):
    """Labelled decision records for one root: features and exact labels as floats."""
    env, meta = make_root(family, seed)
    orc = Oracle(env)
    states = enumerate_states(orc, Random(seed ^ 0x5EED), cap)
    src = Source(env, orc)
    recs = []
    for st in states:
        r = orc.rec(st)
        f = state_features(orc.ctx, st)
        ex = {e: expert_index(src, st, r['actions'], e) for e in EXPERTS}
        q = [float(v) for v in r['q']]
        best = float(r['best'])
        reg = [best - v for v in q]
        recs.append(dict(
            root=seed, family=family, A=len(q), regret=reg, opt=[v == r['best'] for v in r['q']],
            scalar=f['scalar'], rel=f['rel'], rel_sham=f['rel_sham'], tok=f['tok'], tok_sham=f['tok_sham'],
            route=f['route'], expert_regret={e: reg[i] for e, i in ex.items()}, depth=st[2],
            sham_changed=bool(shuffle_state(to_float(st))[2])))
    root_total = total_of(orc.ctx.root_state()[0])
    return dict(meta=meta, root=seed, family=family, n=env.n, k=len(env.qs), budget=env.budget,
                groups=len(orc.ctx.root_state()[0]), exact_states=len(orc.pl.memo), records=recs,
                optimum=float(orc.rec(orc.ctx.root_state())['best']))


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------ tensors, models, training

try:
    import numpy as np
    import torch
    import torch.nn as nn
except ImportError:                                               # symbolic part and tests run without torch
    try:
        import numpy as np
    except ImportError:
        np = None
    torch = nn = None

GMAX, AMAX = 14, 18
MLP_H = (48, 32)
TRM_D, TRM_FF, TRM_HEADS = 16, 32, 2
ROUTE_H = 32
RANK_KINDS = ('scalar', 'rel', 'rel_sham', 'trm', 'trm_sham')


def mlp_params(din, h=MLP_H):
    return din * h[0] + h[0] + h[0] * h[1] + h[1] + h[1] + 1


def trm_params(d=TRM_D, ff=TRM_FF):
    return (NS * d + d) + (NA * d + d) + 2 * d + (4 * d * d + 4 * d) + 2 * d + (d * ff + ff + ff * d + d) + d + 1


def router_params():
    return NROUTE * ROUTE_H + ROUTE_H + ROUTE_H * len(EXPERTS) + len(EXPERTS)


def param_counts():
    return dict(scalar=mlp_params(NSCAL), rel=mlp_params(NSCAL + NREL), rel_sham=mlp_params(NSCAL + NREL),
                trm=trm_params(), trm_sham=trm_params(), router=router_params())


def pack(records):
    """Float records -> numpy arrays padded to (AMAX, GMAX)."""
    N = len(records)
    d = dict(scal=np.zeros((N, AMAX, NSCAL), 'f4'), rel=np.zeros((N, AMAX, NREL), 'f4'),
             rel_sham=np.zeros((N, AMAX, NREL), 'f4'), amask=np.zeros((N, AMAX), bool),
             regret=np.zeros((N, AMAX), 'f4'), opt=np.zeros((N, AMAX), bool),
             S=np.zeros((N, GMAX, NS), 'f4'), smask=np.zeros((N, GMAX), bool), A=np.zeros((N, AMAX, NA), 'f4'),
             S_sham=np.zeros((N, GMAX, NS), 'f4'), smask_sham=np.zeros((N, GMAX), bool),
             A_sham=np.zeros((N, AMAX, NA), 'f4'),
             route=np.zeros((N, NROUTE), 'f4'), exp=np.zeros((N, len(EXPERTS)), 'f4'),
             root=np.zeros(N, np.int64), fam=np.zeros(N, np.int8), depth=np.zeros(N, np.int8))
    for i, r in enumerate(records):
        a = r['A']
        assert a <= AMAX and len(r['tok'][0]) <= GMAX and len(r['tok_sham'][0]) <= GMAX, (a, len(r['tok'][0]))
        d['scal'][i, :a] = r['scalar']
        d['rel'][i, :a] = r['rel']
        d['rel_sham'][i, :a] = r['rel_sham']
        d['amask'][i, :a] = True
        d['regret'][i, :a] = r['regret']
        d['opt'][i, :a] = r['opt']
        S, A = r['tok']
        d['S'][i, :len(S)] = S
        d['smask'][i, :len(S)] = True
        d['A'][i, :a] = A
        S2, A2 = r['tok_sham']
        d['S_sham'][i, :len(S2)] = S2
        d['smask_sham'][i, :len(S2)] = True
        d['A_sham'][i, :a] = A2
        d['route'][i] = r['route']
        d['exp'][i] = [r['expert_regret'][e] for e in EXPERTS]
        d['root'][i] = r['root']
        d['fam'][i] = FAMILIES.index(r['family'])
        d['depth'][i] = r['depth']
    return d


if torch is not None:
    class MLPRanker(nn.Module):
        def __init__(self, din, mu, sd):
            super().__init__()
            self.net = nn.Sequential(nn.Linear(din, MLP_H[0]), nn.ReLU(), nn.Linear(MLP_H[0], MLP_H[1]), nn.ReLU(),
                                     nn.Linear(MLP_H[1], 1))
            self.register_buffer('mu', torch.as_tensor(mu, dtype=torch.float32))
            self.register_buffer('sd', torch.as_tensor(sd, dtype=torch.float32))

        def forward(self, x):
            return self.net((x - self.mu) / self.sd).squeeze(-1)

    class TRM(nn.Module):
        """Set encoder over strategy-group and action tokens; one shared attention+MLP block iterated T times
        with the embedded input re-injected into the recurrent latent at every iteration."""

        def __init__(self, T, d=TRM_D, ff=TRM_FF, heads=TRM_HEADS):
            super().__init__()
            self.T = T
            self.es, self.ea = nn.Linear(NS, d), nn.Linear(NA, d)
            self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
            self.att = nn.MultiheadAttention(d, heads, batch_first=True)
            self.ff = nn.Sequential(nn.Linear(d, ff), nn.GELU(), nn.Linear(ff, d))
            self.head = nn.Linear(d, 1)

        def forward(self, S, smask, A, amask):
            e = torch.cat([self.es(S), self.ea(A)], 1)
            pad = ~torch.cat([smask, amask], 1)
            h = torch.zeros_like(e)
            for _ in range(self.T):
                x = h + e
                z = self.ln1(x)
                x = x + self.att(z, z, z, key_padding_mask=pad, need_weights=False)[0]
                h = x + self.ff(self.ln2(x))
            return self.head(h[:, S.shape[1]:]).squeeze(-1)

    class Router(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(nn.Linear(NROUTE, ROUTE_H), nn.ReLU(), nn.Linear(ROUTE_H, len(EXPERTS)))

        def forward(self, x):
            return self.net(x)


def nparams(m):
    return sum(p.numel() for p in m.parameters())


def inputs_for(kind, d, idx):
    """Tensors for a batch of records (idx) for a ranker kind."""
    t = lambda a: torch.as_tensor(a[idx])
    if kind == 'scalar':
        return (t(d['scal']),)
    if kind == 'rel':
        return (torch.cat([t(d['scal']), t(d['rel'])], -1),)
    if kind == 'rel_sham':
        return (torch.cat([t(d['scal']), t(d['rel_sham'])], -1),)
    if kind == 'trm':
        return t(d['S']), t(d['smask']), t(d['A']), t(d['amask'])
    if kind == 'trm_sham':
        return t(d['S_sham']), t(d['smask_sham']), t(d['A_sham']), t(d['amask'])
    raise ValueError(kind)


def make_model(kind, d=None, T=2):
    if kind.startswith('trm'):
        return TRM(T)
    din = NSCAL + (0 if kind == 'scalar' else NREL)
    x = inputs_for(kind, d, np.arange(len(d['amask'])))[0].numpy()
    m = d['amask']
    mu, sd = x[m].mean(0), x[m].std(0) + 1e-6
    return MLPRanker(din, mu, sd)


def rank_loss(score, regret, mask, optm):
    tgt = -10.0 * regret
    mse = (((score - tgt) ** 2) * mask).sum() / mask.sum()
    logp = torch.log_softmax(score.masked_fill(~mask, -1e9), -1)
    ce = -((logp * optm).sum(-1) / optm.sum(-1)).mean()
    return mse + 0.5 * ce


def rank_eval(model, kind, d, bs=1024):
    """Per-state (proposal regret, argmax in optimal set) on packed data."""
    model.eval()
    reg, hit = [], []
    with torch.no_grad():
        for s in range(0, len(d['amask']), bs):
            idx = np.arange(s, min(s + bs, len(d['amask'])))
            sc = model(*inputs_for(kind, d, idx)).masked_fill(~torch.as_tensor(d['amask'][idx]), -1e9)
            a = sc.argmax(-1).numpy()
            reg.append(d['regret'][idx, a])
            hit.append(d['opt'][idx, a])
    return np.concatenate(reg), np.concatenate(hit)


def train_ranker(kind, seed, dtrain, ddev, T=2, epochs=40, lr=3e-3, bs=128):
    torch.manual_seed(seed)
    model = make_model(kind, dtrain, T)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    N = len(dtrain['amask'])
    mask, regret, optm = (torch.as_tensor(dtrain[k]) for k in ('amask', 'regret', 'opt'))
    best, curve, rng = None, [], np.random.default_rng(seed)
    t0 = time.perf_counter()
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(N)
        for s in range(0, N, bs):
            idx = perm[s:s + bs]
            sc = model(*inputs_for(kind, dtrain, idx))
            loss = rank_loss(sc, regret[idx], mask[idx], optm[idx].float())
            opt.zero_grad()
            loss.backward()
            opt.step()
        sched.step()
        if ep % 2 == 1 or ep == epochs - 1:
            r, h = rank_eval(model, kind, ddev)
            curve.append((ep, float(r.mean()), float(h.mean())))
            if best is None or (r.mean(), -h.mean()) < best[0]:
                best = ((float(r.mean()), float(-h.mean())), {k: v.clone() for k, v in model.state_dict().items()}, ep)
    model.load_state_dict(best[1])
    return dict(kind=kind, seed=seed, T=T, state={k: v.numpy() for k, v in best[1].items()}, best_epoch=best[2],
                dev_regret=best[0][0], dev_acc=-best[0][1], train_s=time.perf_counter() - t0,
                params=nparams(model), curve=curve)


def load_ranker(blob):
    kind = blob['kind']
    if kind.startswith('trm'):
        m = TRM(blob['T'])
    else:
        din = NSCAL + (0 if kind == 'scalar' else NREL)
        m = MLPRanker(din, np.zeros(din), np.ones(din))
    m.load_state_dict({k: torch.as_tensor(v) for k, v in blob['state'].items()})
    m.eval()
    return m


def train_router(seed, dtrain, ddev, epochs=80, lr=3e-3, bs=128):
    torch.manual_seed(seed)
    m = Router()
    opt = torch.optim.Adam(m.parameters(), lr=lr)
    X, Y = torch.as_tensor(dtrain['route']), torch.as_tensor(10 * dtrain['exp'])
    Xd, Yd = torch.as_tensor(ddev['route']), torch.as_tensor(10 * ddev['exp'])
    rng, best = np.random.default_rng(seed), None
    for ep in range(epochs):
        perm = rng.permutation(len(X))
        for s in range(0, len(X), bs):
            idx = perm[s:s + bs]
            loss = ((m(X[idx]) - Y[idx]) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
        with torch.no_grad():
            dl = float(((m(Xd) - Yd) ** 2).mean())
        if best is None or dl < best[0]:
            best = (dl, {k: v.clone() for k, v in m.state_dict().items()}, ep)
    return dict(kind='router', seed=seed, state={k: v.numpy() for k, v in best[1].items()}, dev_mse=best[0],
                best_epoch=best[2], params=nparams(m))


def load_router(blob):
    m = Router()
    m.load_state_dict({k: torch.as_tensor(v) for k, v in blob['state'].items()})
    m.eval()
    return m


def route_choice(pred, tau):
    """Cheapest expert with predicted regret <= tau (pred is 10x regret); 'exact' is the fallback."""
    for e, p in zip(EXPERTS, pred):
        if p / 10.0 <= tau:
            return e
    return 'exact'


# ------------------------------------------------------------------ sources, deciders, rollouts

def skey(state):
    return (state[0], state[1], state[2])


class Source:
    """Planner values and features at states. Shared mode reuses an Oracle's planner; a fresh Source counts
    the planner states it creates (memo growth), which is the search cost of the decisions it serves."""

    def __init__(self, env, shared=None):
        self.env = env
        self.ctx = shared.ctx if shared else Ctx(env)
        self.pl = shared.pl if shared else Planner(env, None)
        self.vc, self.fc, self.states = {}, {}, 0

    def vals(self, state, d, upper):
        key = (skey(state), d, upper)
        v = self.vc.get(key)
        if v is None:
            n0 = len(self.pl.memo)
            v = planner_values(self.pl, state, d, upper)
            self.states += len(self.pl.memo) - n0
            self.vc[key] = v
        return v

    def feat(self, state, which):
        key = (skey(state), which)
        f = self.fc.get(key)
        if f is None:
            f = state_features(self.ctx, state, which)
            self.fc[key] = f
        return f


def expert_index(src, state, alist, name):
    gs = state[0]
    if name == 'direct':
        gidx = [i for i, a in enumerate(alist) if a[0] == 'g']
        return max(gidx, key=lambda i: (gs[alist[i][1]][0], -i))
    if name == 'greedy':
        return first_argmax(src.feat(state, ('lb0',))['lb0'])
    if name == 'depth2':
        return first_argmax(src.vals(state, 2, False))
    if name == 'depth3':
        return first_argmax(src.vals(state, 3, False))
    if name == 'exact':
        return first_argmax(src.vals(state, None, False))
    raise ValueError(name)


KIND_BLOCKS = dict(scalar=('scalar',), rel=('scalar', 'rel'), rel_sham=('scalar', 'rel_sham'),
                   trm=('tok',), trm_sham=('tok_sham',))


def ranker_index(kind, net, f):
    with torch.no_grad():
        if kind == 'scalar':
            x = (torch.tensor([f['scalar']], dtype=torch.float32),)
        elif kind in ('rel', 'rel_sham'):
            x = (torch.tensor([[s + r for s, r in zip(f['scalar'], f[kind])]], dtype=torch.float32),)
        else:
            S, A = f['tok' if kind == 'trm' else 'tok_sham']
            x = (torch.tensor([S], dtype=torch.float32), torch.ones(1, len(S), dtype=torch.bool),
                 torch.tensor([A], dtype=torch.float32), torch.ones(1, len(A), dtype=torch.bool))
        return int(net(*x)[0].argmax())


def certified(src, state, ai, eta):
    lb, ub = src.vals(state, 2, False), src.vals(state, 2, True)
    if len(lb) == 1:
        return True
    return lb[ai] >= max(v for i, v in enumerate(ub) if i != ai) - eta


def make_decider(src, spec):
    """spec: kind 'base' (name) | 'rank' (rkind, net, cache) | 'router' (net, tau, cache); eta None = no certificate."""
    cache = spec.get('cache', {})
    eta = spec.get('eta')

    def propose(state, alist):
        kind = spec['kind']
        if kind == 'base':
            return expert_index(src, state, alist, spec['name']), None
        key = skey(state)
        if key in cache:
            return cache[key]
        if kind == 'rank':
            f = src.feat(state, KIND_BLOCKS[spec['rkind']])
            out = (ranker_index(spec['rkind'], spec['net'], f), None)
        else:
            f = src.feat(state, ('route',))
            with torch.no_grad():
                pred = spec['net'](torch.tensor([f['route']], dtype=torch.float32))[0].tolist()
            e = route_choice(pred, spec['tau'])
            out = (expert_index(src, state, alist, e), e)
        cache[key] = out
        return out

    def decide(state):
        alist = actions(src.ctx, state)
        s0, t0 = src.states, time.perf_counter()
        ai, expert = propose(state, alist)
        t1, s1 = time.perf_counter(), src.states
        info = dict(proposed=ai, expert=expert, accepted=None, t_prop=t1 - t0, st_prop=s1 - s0, t_cert=0.0,
                    st_cert=0, t_fb=0.0, st_fb=0)
        if eta is not None and expert != 'exact':
            ok = certified(src, state, ai, eta)
            t2, s2 = time.perf_counter(), src.states
            info.update(accepted=ok, t_cert=t2 - t1, st_cert=s2 - s1)
            if not ok:
                ai = expert_index(src, state, alist, 'exact')
                info.update(t_fb=time.perf_counter() - t2, st_fb=src.states - s2)
        elif eta is not None:
            info['accepted'] = True                                  # the router already ran exact search
        return alist, ai, info

    return decide


def play(src, decide):
    """Execute a decider over the full outcome tree from the root; exact Fraction value of the policy."""
    ctx = src.ctx
    root = ctx.root_state()
    layers = {root[2]: {skey(root): [root, 1.0]}}
    nodes = {}
    for b in range(root[2], 0, -1):
        for k, (st, reach) in list(layers.get(b, {}).items()):
            alist, ai, info = decide(st)
            t = time.perf_counter()
            imm, kids = step(ctx, st, alist[ai])
            info['t_update'] = time.perf_counter() - t
            tot = total_of(st[0])
            nodes[k] = dict(st=st, alist=alist, ai=ai, imm=imm, kids=kids, tot=tot, reach=reach, info=info)
            for w, c in kids:
                if c[2] > 0 and c[0]:
                    layers.setdefault(c[2], {}).setdefault(skey(c), [c, 0.0])[1] += reach * float(w / tot)
    V = {}
    for b in range(1, root[2] + 1):
        for k in layers.get(b, {}):
            n = nodes[k]
            V[k] = (n['imm'] + sum(w * V.get(skey(c), 0) for w, c in n['kids'])) / n['tot']
    return V[skey(root)], nodes


def summarize(value, nodes, orc=None):
    """Reach-weighted decision statistics of one executed policy."""
    R = sum(n['reach'] for n in nodes.values())
    acc = [n for n in nodes.values() if n['info']['accepted'] is not None]
    out = dict(decisions=len(nodes), reach=R,
               t_decision=sum(n['reach'] * (n['info']['t_prop'] + n['info']['t_cert'] + n['info']['t_fb']
                                            + n['info']['t_update']) for n in nodes.values()) / R,
               states_decision=sum(n['reach'] * (n['info']['st_prop'] + n['info']['st_cert'] + n['info']['st_fb'])
                                   for n in nodes.values()) / R,
               accept=(sum(n['reach'] for n in acc if n['info']['accepted']) / sum(n['reach'] for n in acc))
               if acc else None)
    if orc is not None:
        ow = [(n['reach'], orc.rec(n['st'])) for n in nodes.values()]
        out['proposal_opt'] = sum(w for (w, r), n in zip(ow, nodes.values())
                                  if r['q'][n['info']['proposed']] == r['best']) / R
        out['exec_opt'] = sum(w for (w, r), n in zip(ow, nodes.values()) if r['q'][n['ai']] == r['best']) / R
        out['exec_decision_regret'] = sum(w * float(r['best'] - r['q'][n['ai']])
                                          for (w, r), n in zip(ow, nodes.values())) / R
    return out


def root_policy_regret(orc, value):
    return orc.rec(orc.ctx.root_state())['best'] - value


# ------------------------------------------------------------------ evaluation workers

_W = {}
ETAS = (None, F(0), F(1, 100))
BASELINES = ('direct', 'greedy', 'depth2', 'depth3', 'exact')


def _init_worker(models_path):
    torch.set_num_threads(1)
    import pickle
    bundle = pickle.load(open(models_path, 'rb'))
    nets = {}
    for b in bundle['rankers']:
        T = b['T'] if b['kind'].startswith('trm') else 0
        if b['kind'].startswith('trm') and T != bundle['T_sel']:
            continue
        nets[(b['kind'], b['seed'])] = load_ranker(b)
    routers = {b['seed']: load_router(b) for b in bundle['routers']}
    _W.update(nets=nets, routers=routers, tau=bundle['tau_sel'])


def eta_tag(eta):
    return 'plain' if eta is None else ('c0' if eta == 0 else 'c01')


def learned_specs(seeds=None, etas=ETAS, kinds=RANK_KINDS):
    out = []
    for (kind, seed), net in sorted(_W['nets'].items()):
        if kind in kinds and (seeds is None or seed in seeds):
            for eta in etas:
                out.append((f'{kind}_s{seed}', eta_tag(eta), dict(kind='rank', rkind=kind, net=net, eta=eta)))
    for seed, net in sorted(_W['routers'].items()):
        if seeds is None or seed in seeds:
            for eta in etas:
                out.append((f'router_s{seed}', eta_tag(eta), dict(kind='router', net=net, tau=_W['tau'], eta=eta)))
    return out


def eval_root(task):
    """Accuracy-pass rollouts for one root with a shared exact oracle (cost is not measured here)."""
    family, seed = task
    env, meta = make_root(family, seed)
    orc = Oracle(env)
    src = Source(env, orc)
    opt = orc.rec(orc.ctx.root_state())['best']
    res = {}

    def run(name, tag, spec):
        spec = dict(spec)
        spec.setdefault('cache', _caches.setdefault(name, {}))
        v, nodes = play(src, make_decider(src, spec))
        s = summarize(v, nodes, orc)
        s['regret'] = float(opt - v)
        s['regret_exact'] = str(opt - v)
        res[f'{name}|{tag}'] = s

    _caches = {}
    for b in BASELINES:
        run(b, 'plain', dict(kind='base', name=b, eta=None))
    for b in ('greedy', 'depth2', 'depth3'):
        for eta in ETAS[1:]:
            run(b, eta_tag(eta), dict(kind='base', name=b, eta=eta))
    for name, tag, spec in learned_specs():
        run(name, tag, spec)
    return dict(family=family, seed=seed, meta=meta, optimum=float(opt), results=res)


def cost_root(task):
    """Cost-pass rollouts: a fresh planner per rollout so planner states and wall-clock are fully attributed."""
    family, seed = task
    env, meta = make_root(family, seed)
    res = {}

    def run(name, tag, spec):
        src = Source(env)
        spec = dict(spec, cache={})
        v, nodes = play(src, make_decider(src, spec))
        res[f'{name}|{tag}'] = dict(summarize(v, nodes), value=float(v))

    for b in ('greedy', 'depth2', 'depth3', 'exact'):
        run(b, 'plain', dict(kind='base', name=b, eta=None))
    for b in ('greedy', 'depth2', 'depth3'):
        run(b, 'c0', dict(kind='base', name=b, eta=F(0)))
    for name, tag, spec in learned_specs(seeds={0}, etas=(None, F(0), F(1, 100))):
        if tag == 'c01' and not name.startswith(('rel_s', 'trm_s', 'router')):
            continue
        run(name, tag, spec)
    return dict(family=family, seed=seed, optimum=None, results=res)


# ------------------------------------------------------------------ stages

WORK = OUT / 'work'
PER_FAMILY = dict(train=150, dev=40, eval=60)
COST_PER_FAMILY = 8
SEEDS = (0, 1, 2)
TARGET_DEV_REGRET = 0.005
TAU_GRID = (0.0, 0.002, 0.005, 0.01, 0.02, 0.05)
SAMPLE_CAP = 250


def _pool(n=4):
    import multiprocessing as mp
    return mp.get_context('spawn').Pool(n)


def _root_task(t):
    return root_records(t[0], t[1], SAMPLE_CAP)


def stage_build():
    import pickle
    WORK.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    with _pool() as p:
        for split in ('train', 'dev', 'eval'):
            tasks = root_list(split, PER_FAMILY[split])
            roots = p.map(_root_task, tasks, chunksize=1)
            pickle.dump(roots, open(WORK / f'roots_{split}.pkl', 'wb'))
            recs = sum(len(r['records']) for r in roots)
            print(split, len(roots), 'roots', recs, 'states', f'{time.perf_counter() - t0:.0f}s', flush=True)


def load_split(split):
    import pickle
    roots = pickle.load(open(WORK / f'roots_{split}.pkl', 'rb'))
    recs = [r for root in roots for r in root['records']]
    return roots, recs


_TD = {}


def _train_init(path):
    torch.set_num_threads(1)
    z = np.load(path)
    _TD.update({k: z[k] for k in z.files})


def _train_job(job):
    kind, seed, T = job
    dtr = {k[3:]: v for k, v in _TD.items() if k.startswith('tr_')}
    ddv = {k[3:]: v for k, v in _TD.items() if k.startswith('dv_')}
    if kind == 'router':
        return train_router(seed, dtr, ddv)
    return train_ranker(kind, seed, dtr, ddv, T=T)


def stage_train(epochs=40):
    import pickle
    _, rtr = load_split('train')
    _, rdv = load_split('dev')
    dtr, ddv = pack(rtr), pack(rdv)
    path = WORK / 'packed.npz'
    np.savez(path, **{f'tr_{k}': v for k, v in dtr.items()}, **{f'dv_{k}': v for k, v in ddv.items()})
    jobs = [(k, 12000 + s, T) for k in ('trm', 'trm_sham') for T in (2, 4) for s in SEEDS] + \
           [(k, 12000 + s, 0) for k in ('scalar', 'rel', 'rel_sham') for s in SEEDS] + \
           [('router', 12000 + s, 0) for s in SEEDS]
    import multiprocessing as mp
    t0 = time.perf_counter()
    with mp.get_context('spawn').Pool(4, initializer=_train_init, initargs=(str(path),)) as p:
        out = []
        for r in p.imap_unordered(_train_job, jobs):
            out.append(r)
            print('trained', r['kind'], r.get('T'), r['seed'], 'dev_regret', r.get('dev_regret'), 'acc', r.get('dev_acc'),
                  f'{time.perf_counter() - t0:.0f}s', flush=True)
    for r in out:
        if 'seed' in r:
            r['seed'] -= 12000
    rankers = [r for r in out if r['kind'] != 'router']
    routers = [r for r in out if r['kind'] == 'router']
    dev_by_T = {T: float(np.mean([r['dev_regret'] for r in rankers if r['kind'] == 'trm' and r['T'] == T]))
                for T in (2, 4)}
    T_sel = min(dev_by_T, key=lambda T: dev_by_T[T])
    # tau by dev state-level router regret: largest tau meeting the target
    tau_rows = []
    for tau in TAU_GRID:
        regs = []
        for b in routers:
            m = load_router(b)
            with torch.no_grad():
                pred = m(torch.as_tensor(ddv['route'])).numpy()
            reg = []
            for p_, e_ in zip(pred, ddv['exp']):
                c = route_choice(p_, tau)
                reg.append(0.0 if c == 'exact' else float(e_[EXPERTS.index(c)]))
            regs.append(np.mean(reg))
        tau_rows.append(dict(tau=tau, dev_state_regret=float(np.mean(regs))))
    ok = [r['tau'] for r in tau_rows if r['dev_state_regret'] <= TARGET_DEV_REGRET]
    tau_sel = max(ok) if ok else 0.0
    bundle = dict(rankers=rankers, routers=routers, T_sel=T_sel, tau_sel=tau_sel, dev_by_T=dev_by_T,
                  tau_rows=tau_rows, train_wall_s=time.perf_counter() - t0,
                  train_cpu_s=sum(r.get('train_s', 0) for r in out))
    pickle.dump(bundle, open(WORK / 'models.pkl', 'wb'))
    print('T_sel', T_sel, dev_by_T, 'tau_sel', tau_sel, tau_rows, f'wall {time.perf_counter() - t0:.0f}s', flush=True)


def stage_eval():
    import pickle
    import multiprocessing as mp
    models = str(WORK / 'models.pkl')
    t0 = time.perf_counter()
    for split in ('dev', 'eval'):
        tasks = root_list(split, PER_FAMILY[split])
        with mp.get_context('spawn').Pool(4, initializer=_init_worker, initargs=(models,)) as p:
            out = p.map(eval_root, tasks, chunksize=1)
        pickle.dump(out, open(WORK / f'rollouts_{split}.pkl', 'wb'))
        print('rollouts', split, len(out), f'{time.perf_counter() - t0:.0f}s', flush=True)
    tasks = root_list('eval', PER_FAMILY['eval'])
    cost_tasks = [t for fi, f in enumerate(FAMILIES) for t in tasks[fi * PER_FAMILY['eval']:][:COST_PER_FAMILY]]
    with mp.get_context('spawn').Pool(4, initializer=_init_worker, initargs=(models,)) as p:
        out = p.map(cost_root, cost_tasks, chunksize=1)
    pickle.dump(out, open(WORK / 'cost.pkl', 'wb'))
    print('cost', len(out), f'{time.perf_counter() - t0:.0f}s', flush=True)


# ------------------------------------------------------------------ report

def _root_index(d, roots):
    order = {r['root']: i for i, r in enumerate(roots)}
    return np.array([order[x] for x in d['root']]), len(roots)


def _per_root(vals, idx, n):
    s = np.bincount(idx, weights=vals, minlength=n)
    c = np.bincount(idx, minlength=n)
    return s / np.maximum(c, 1)


def _boot(diff, B=4000, seed=0):
    rng = np.random.default_rng(seed)
    n = len(diff)
    m = diff[rng.integers(0, n, (B, n))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def paired(a, b, fam=None):
    """Root-level paired difference a - b (lower is better for regret/cost): mean, bootstrap 95% CI, counts."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    out = dict(n=int(len(d)), mean=float(d.mean()), ci95=_boot(d), a_lower=int((d < -1e-12).sum()),
               b_lower=int((d > 1e-12).sum()), ties=int((np.abs(d) <= 1e-12).sum()), a_mean=float(a.mean()),
               b_mean=float(b.mean()))
    if fam is not None:
        out['by_family'] = {f: dict(mean=float(d[fam == i].mean()), n=int((fam == i).sum()))
                            for i, f in enumerate(FAMILIES)}
    return out


def state_metrics(split, bundle):
    """Per-state proposal regret / optimal-hit for every controller on a split's records."""
    roots, recs = load_split(split)
    d = pack(recs)
    idx, n = _root_index(d, roots)
    out = {}
    for b in bundle['rankers']:
        m = load_ranker(b)
        reg, hit = rank_eval(m, b['kind'], d)
        key = f"{b['kind']}{b['T']}" if b['kind'].startswith('trm') else b['kind']
        out.setdefault(key, []).append((reg, hit.astype(float)))
    for e in EXPERTS:
        j = EXPERTS.index(e)
        out[e] = [(d['exp'][:, j].astype(float), (d['exp'][:, j] < 1e-12).astype(float))]
    for tau in TAU_GRID:
        runs = []
        for rb in bundle['routers']:
            m = load_router(rb)
            with torch.no_grad():
                pred = m(torch.as_tensor(d['route'])).numpy()
            reg = np.array([0.0 if (c := route_choice(p, tau)) == 'exact' else float(e_[EXPERTS.index(c)])
                            for p, e_ in zip(pred, d['exp'])])
            runs.append((reg, (reg < 1e-12).astype(float)))
        out[f'router@{tau}'] = runs
    return roots, recs, d, idx, n, out


def _agg(runs, idx, n):
    """Per-root arrays (seed-mean) of regret and accuracy, plus per-seed arrays."""
    reg = np.stack([_per_root(r, idx, n) for r, _ in runs])
    acc = np.stack([_per_root(h, idx, n) for _, h in runs])
    return reg, acc


def stage_report():
    import pickle, subprocess
    bundle = pickle.load(open(WORK / 'models.pkl', 'rb'))
    T_sel, tau_sel = bundle['T_sel'], bundle['tau_sel']
    res = dict(schema='mit12-result-v1', config=dict(
        per_family=PER_FAMILY, cost_roots_per_family=COST_PER_FAMILY, seeds=list(SEEDS), T_sel=T_sel, tau_sel=tau_sel,
        tau_grid=TAU_GRID, target_dev_regret=TARGET_DEV_REGRET, sample_cap=SAMPLE_CAP, etas=['0', '1/100'],
        certificate='accept a if LB_2(a) >= max_{a!=a*} UB_2(a*) - eta, Planner depth 2 on quotient groups; else exact search',
        action_space='quotient groups: guess a group, query a live nonconstant instrument with cost < budget',
        label='exact Fractions from Planner(depth=None); tests compare to Solver.qvalues',
        families={f: dict(random='random noisy roots', palette='palette roots with repeated signatures',
                          higher='MIT-04 parity roots with noisy perturbations')[f] for f in FAMILIES},
        mlp_hidden=MLP_H, trm=dict(d=TRM_D, ff=TRM_FF, heads=TRM_HEADS), epochs=40, train_threads_per_process=1,
        processes=4))
    res['param_counts'] = param_counts()
    res['param_counts_trained'] = {f"{b['kind']}{b.get('T') or ''}_s{b['seed']}": b['params']
                                   for b in bundle['rankers'] + bundle['routers']}
    res['training'] = [dict(kind=b['kind'], T=b.get('T'), seed=b['seed'], best_epoch=b['best_epoch'],
                            dev_regret=b.get('dev_regret'), dev_acc=b.get('dev_acc'), dev_mse=b.get('dev_mse'),
                            train_s=b.get('train_s')) for b in bundle['rankers'] + bundle['routers']]
    res['selection'] = dict(dev_regret_by_T={str(k): v for k, v in bundle['dev_by_T'].items()}, T_sel=T_sel,
                            tau_rows=bundle['tau_rows'], tau_sel=tau_sel,
                            train_cpu_s=bundle['train_cpu_s'], train_wall_s=bundle['train_wall_s'])
    sizes = {}
    stats = {}
    for split in ('train', 'dev', 'eval'):
        roots, recs = load_split(split)
        sizes[split] = dict(roots=len(roots), states=len(recs), actions=int(sum(r['A'] for r in recs)),
                            per_family={f: dict(roots=sum(r['family'] == f for r in roots),
                                                states=sum(1 for r in recs if r['family'] == f))
                                        for f in FAMILIES})
        stats[split] = roots
    res['dataset'] = sizes
    res['alias_witness_roots'] = {s: sum(bool(r['meta'].get('alias_witness')) for r in stats[s] if r['family'] == 'higher')
                                  for s in stats}
    # ---- state-level metrics (dev for selection, eval for report)
    dev = state_metrics('dev', bundle)
    ev = state_metrics('eval', bundle)
    roots_e, recs_e, d_e, idx_e, n_e, sm_e = ev
    roots_d, recs_d, d_d, idx_d, n_d, sm_d = dev
    fam_e = np.array([FAMILIES.index(r['family']) for r in roots_e])
    res['sham_changed_state_fraction'] = dict(
        dev=float(np.mean([r['sham_changed'] for r in recs_d])), eval=float(np.mean([r['sham_changed'] for r in recs_e])),
        by_family={f: float(np.mean([r['sham_changed'] for r in recs_e if r['family'] == f])) for f in FAMILIES})
    types = {}
    for key in sm_e:
        if key.startswith('router@') and key != f'router@{tau_sel}':
            continue
        name = 'router' if key.startswith('router@') else key
        if name in ('trm2', 'trm4', 'trm_sham2', 'trm_sham4'):
            pass
        reg, acc = _agg(sm_e[key], idx_e, n_e)
        types[name] = dict(state_regret_root=reg.mean(0), state_acc_root=acc.mean(0), regret_seed=reg, acc_seed=acc)
    types['trm'] = types[f'trm{T_sel}']
    types['trm_sham'] = types[f'trm_sham{T_sel}']
    dev_types = {}
    for key in sm_d:
        if key.startswith('router@') and key != f'router@{tau_sel}':
            continue
        name = 'router' if key.startswith('router@') else key
        reg, acc = _agg(sm_d[key], idx_d, n_d)
        dev_types[name] = dict(state_regret_root=reg.mean(0), state_acc_root=acc.mean(0), regret_seed=reg)
    dev_types['trm'] = dev_types[f'trm{T_sel}']
    # ---- rollouts
    ro = {s: pickle.load(open(WORK / f'rollouts_{s}.pkl', 'rb')) for s in ('dev', 'eval')}

    def rvec(split, name, tag='plain', field='regret'):
        return np.array([r['results'][f'{name}|{tag}'][field] for r in ro[split]], dtype=float)

    def seeds_of(kind):
        return [f'{kind}_s{s}' for s in SEEDS]

    def rtype(split, kind, tag='plain', field='regret'):
        names = [kind] if kind in BASELINES else seeds_of(kind)
        arr = np.stack([rvec(split, nm, tag, field) for nm in names])
        return arr

    exec_types = ('direct', 'greedy', 'depth2', 'depth3', 'exact', 'scalar', 'rel', 'rel_sham', 'trm', 'trm_sham', 'router')
    summary = {}
    for kind in exec_types:
        row = dict(params=res['param_counts'].get(kind))
        a = rtype('eval', kind)
        row['executed_regret_mean'] = float(a.mean())
        row['executed_regret_max_root'] = float(a.mean(0).max())
        row['executed_regret_max_seed_root'] = float(a.max())
        row['proposal_opt_reach'] = float(rtype('eval', kind, 'plain', 'proposal_opt').mean())
        if kind in types:
            row['state_accuracy'] = float(types[kind]['state_acc_root'].mean())
            row['state_regret'] = float(types[kind]['state_regret_root'].mean())
        elif kind in ('direct', 'greedy', 'depth2', 'depth3'):
            pass
        for tag, eta in (('c0', '0'), ('c01', '0.01')):
            if kind in ('exact', 'direct') and tag != 'c0':
                continue
            try:
                b = rtype('eval', kind, tag)
            except KeyError:
                continue
            row[f'cert_eta{eta}'] = dict(
                executed_regret_mean=float(b.mean()), executed_regret_max=float(b.max()),
                acceptance=float(rtype('eval', kind, tag, 'accept').mean()),
                fallback=float(1 - rtype('eval', kind, tag, 'accept').mean()))
        summary[kind] = row
    for kind in ('direct', 'greedy', 'depth2', 'depth3'):
        j = EXPERTS.index(kind)
        summary[kind]['state_accuracy'] = float((d_e['exp'][:, j] < 1e-12).mean())
        summary[kind]['state_regret'] = float(d_e['exp'][:, j].mean())
    res['summary_eval'] = summary
    res['state_metrics_by_T'] = {k: dict(state_regret=float(types[k]['state_regret_root'].mean()),
                                         state_acc=float(types[k]['state_acc_root'].mean()))
                                 for k in ('trm2', 'trm4', 'trm_sham2', 'trm_sham4')}
    res['state_metrics_by_family'] = {
        k: {f: dict(state_regret=float(types[k]['state_regret_root'][fam_e == i].mean()),
                    state_acc=float(types[k]['state_acc_root'][fam_e == i].mean()),
                    executed_regret=float(rtype('eval', k)[:, fam_e == i].mean()) if k in exec_types else None)
            for i, f in enumerate(FAMILIES)} for k in ('scalar', 'rel', 'rel_sham', 'trm', 'trm_sham', 'router')}
    res['router_tau_eval'] = {
        str(tau): float(np.mean([r[0].mean() for r in sm_e[f'router@{tau}']])) for tau in TAU_GRID}
    # ---- best learned by dev state regret
    cand = ('scalar', 'rel', 'trm', 'router')
    best = min(cand, key=lambda k: (dev_types[k]['state_regret_root'].mean(), res['param_counts'].get(k, 0)))
    res['best_learned_by_dev'] = best
    res['dev_state_regret'] = {k: float(dev_types[k]['state_regret_root'].mean()) for k in dev_types}
    # ---- paired differences on eval roots
    P = {}
    for metric, getter in (('executed_regret', lambda k: rtype('eval', k).mean(0)),
                           ('state_regret', lambda k: types[k]['state_regret_root']),
                           ('state_error', lambda k: 1 - types[k]['state_acc_root'])):
        for a_, b_ in (('trm', 'rel'), ('trm', 'trm_sham'), ('rel', 'rel_sham'), ('trm', 'scalar'), ('trm', 'rel_sham')):
            P[f'{metric}: {a_} - {b_}'] = paired(getter(a_), getter(b_), fam_e)
    P[f'executed_regret: {best} - depth3'] = paired(rtype('eval', best).mean(0), rtype('eval', 'depth3').mean(0), fam_e)
    P[f'state_regret: {best} - depth3'] = paired(types[best]['state_regret_root'],
                                                 _per_root(d_e['exp'][:, EXPERTS.index('depth3')], idx_e, n_e), fam_e)
    res['paired_eval'] = P
    # ---- cost pass
    cost = pickle.load(open(WORK / 'cost.pkl', 'rb'))
    keys = sorted({k for r in cost for k in r['results']})
    cs = {}
    for k in keys:
        rows = [r['results'][k] for r in cost if k in r['results']]
        cs[k] = dict(roots=len(rows),
                     states_per_decision=float(np.mean([x['states_decision'] for x in rows])),
                     ms_per_decision_mean=float(1000 * np.mean([x['t_decision'] for x in rows])),
                     ms_per_decision_median=float(1000 * np.median([x['t_decision'] for x in rows])),
                     acceptance=float(np.mean([x['accept'] for x in rows])) if rows[0]['accept'] is not None else None)
    res['cost_pass'] = dict(roots=len(cost), per_config=cs)
    cid = [(r['family'], r['seed']) for r in cost]
    res['cost_pass']['root_ids'] = cid
    cres = {r['seed']: r['results'] for r in cost}

    def cvec(name, field):
        return np.array([cres[r['seed']][name][field] for r in cost], float)
    bn = f'{best}_s0' if best != 'router' else 'router_s0'
    CP = {}
    for tag in ('c0', 'c01'):
        nm = f'{bn}|{tag}'
        if nm in cs:
            CP[f'states_per_decision: {nm} - depth3|plain'] = paired(cvec(nm, 'states_decision'), cvec('depth3|plain', 'states_decision'))
            CP[f'ms_per_decision: {nm} - depth3|plain'] = paired(1000 * cvec(nm, 't_decision'), 1000 * cvec('depth3|plain', 't_decision'))
    for nm in ('scalar_s0|c0', 'rel_s0|c0', 'trm_s0|c0', 'router_s0|c0', 'greedy|c0'):
        if nm in cs:
            CP[f'states_per_decision: {nm} - depth2|plain'] = paired(cvec(nm, 'states_decision'), cvec('depth2|plain', 'states_decision'))
            CP[f'states_per_decision: {nm} - exact|plain'] = paired(cvec(nm, 'states_decision'), cvec('exact|plain', 'states_decision'))
    res['paired_cost'] = CP
    # ---- per-root values saved
    pr = []
    for i, r in enumerate(ro['eval']):
        row = dict(family=r['family'], seed=r['seed'], optimum=r['optimum'], executed_regret={}, state_regret={},
                   state_accuracy={}, accept_c0={}, accept_c01={})
        for kind in exec_types:
            row['executed_regret'][kind] = [float(x) for x in rtype('eval', kind)[:, i]]
            if kind in types:
                row['state_regret'][kind] = [float(x) for x in types[kind]['regret_seed'][:, i]]
                row['state_accuracy'][kind] = [float(x) for x in types[kind]['acc_seed'][:, i]]
            for tag, key in (('c0', 'accept_c0'), ('c01', 'accept_c01')):
                try:
                    row[key][kind] = [float(x) for x in rtype('eval', kind, tag, 'accept')[:, i]]
                except KeyError:
                    pass
        pr.append(row)
    res['per_root_eval'] = pr
    res['per_root_cost'] = [dict(family=r['family'], seed=r['seed'], results={
        k: dict(states_decision=v['states_decision'], t_decision=v['t_decision'], accept=v['accept'])
        for k, v in r['results'].items()}) for r in cost]
    # ---- preflight on DEV roots: effect = regret(relational) - regret(TRM) in value units (positive favors TRM)
    rel_d = rtype('dev', 'rel')
    trm_d = rtype('dev', 'trm')
    sham_d = rtype('dev', 'trm_sham')
    pilot_rows = []
    for i, r in enumerate(ro['dev']):
        eff = float((rel_d[:, i] - trm_d[:, i]).mean())
        shams = [float(rel_d[:, i].mean() - sham_d[s, i]) for s in range(len(SEEDS))]
        pilot_rows.append(dict(unit_id=f"{r['family']}-{r['seed']}", paired_effect=f'{eff:.10f}',
                               sham_effects=[f'{x:.10f}' for x in shams]))
    pilot = dict(schema_version=1, experiment_id='MIT-12-trm-vs-relational-dev', independent_unit='root',
                 alpha='0.05', scientific_min_effect='0.005', target_effect='0.02', measurement_resolution='0.0001',
                 sham_quantile='0.95', sham_confidence='0.95', planned_comparisons=3, confirm_units_planned=100,
                 pilot_from_development_only=True, heldout_sealed=False, units_independent=True, pilot=pilot_rows)
    pp = WORK / 'pilot_dev.json'
    pp.write_text(json.dumps(pilot, indent=1))
    script = HERE.parents[1] / 'skills' / 'evalmath-mechinterp-power' / 'scripts' / 'preflight.py'
    cp = subprocess.run([sys.executable, str(script), '--pilot', str(pp), '--strict'], capture_output=True, text=True)
    res['preflight'] = dict(command='python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot pilot_dev.json --strict',
                            exit_code=cp.returncode, stdout=cp.stdout, stderr=cp.stderr,
                            pilot_units=len(pilot_rows),
                            pilot_effect_definition='dev-root mean over seeds of regret(relational) - regret(TRM); sham effects = regret(relational) - regret(TRM sham) per seed')
    res['source_sha256'] = {p: file_sha256(HERE.parents[1] / p) for p in (
        'gyms/MathematicalInstrumentTransfer/compact_controller.py',
        'src/spiral_ln/evaluation_adaptive_precision.py', 'src/spiral_ln/evaluation_depth_precision.py',
        'gyms/MathematicalInstrumentTransfer/higher_order.py',
        'skills/evalmath-mechinterp-power/scripts/preflight.py')}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'mit12_result.json').write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
    write_md(res)
    print('report written', flush=True)


def write_md(res):
    S, P, C = res['summary_eval'], res['paired_eval'], res['cost_pass']['per_config']
    pc = res['param_counts']
    L = ['# MIT-12 compact recurrent controller (open exploratory, CPU)', '']
    L.append('Open development evidence. No sealed set exists or was created. Controllers and thresholds were chosen on '
             'the dev roots only; eval roots were not used for any choice.')
    L.append('')
    ds = res['dataset']
    L.append('## Data')
    for s in ('train', 'dev', 'eval'):
        pf = ', '.join(f"{f} {v['roots']}r/{v['states']}s" for f, v in ds[s]['per_family'].items())
        L.append(f"- {s}: {ds[s]['roots']} roots, {ds[s]['states']} states, {ds[s]['actions']} state-actions ({pf})")
    L.append(f"- higher-order roots with exact aliasing witness (optimum(a) != optimum(b)): {res['alias_witness_roots']}")
    sc = res['sham_changed_state_fraction']
    L.append(f"- states where the sham changed the state: eval {sc['eval']:.3f} ({', '.join(f'{k} {v:.3f}' for k, v in sc['by_family'].items())})")
    L.append('')
    L.append('## Parameters')
    L.append(', '.join(f'{k} {v}' for k, v in pc.items()) + f"; TRM T selected on dev: {res['config']['T_sel']} (dev state regret {res['selection']['dev_regret_by_T']}); router tau {res['config']['tau_sel']}")
    L.append('')
    L.append('## Eval roots: proposal quality and executed policy (mean over 3 seeds and roots)')
    L.append('| controller | params | state acc | state regret | executed regret (uncertified) | max root regret | accept eta=0 | accept eta=0.01 | regret eta=0.01 |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for k in ('direct', 'greedy', 'depth2', 'depth3', 'scalar', 'rel', 'rel_sham', 'trm', 'trm_sham', 'router'):
        r = S[k]
        c0, c1 = r.get('cert_eta0', {}), r.get('cert_eta0.01', {})
        f = lambda x: '-' if x is None else f'{x:.4f}'
        L.append(f"| {k} | {r['params'] or '-'} | {f(r.get('state_accuracy'))} | {f(r.get('state_regret'))} | "
                 f"{r['executed_regret_mean']:.5f} | {r['executed_regret_max_root']:.4f} | {f(c0.get('acceptance'))} | "
                 f"{f(c1.get('acceptance'))} | {f(c1.get('executed_regret_mean'))} |")
    L.append('')
    L.append('Certified execution at eta=0: executed regret ' + ', '.join(
        f"{k} {S[k]['cert_eta0']['executed_regret_max']:.1e}" for k in ('scalar', 'rel', 'trm', 'router', 'greedy', 'depth2', 'depth3')) + ' (max over roots/seeds).')
    L.append('')
    L.append('## Cost per decision (cost roots: ' + str(res['cost_pass']['roots']) + ', seed 0, fresh planners)')
    L.append('| config | planner states / decision | ms / decision (mean) | ms (median) | acceptance |')
    L.append('|---|---|---|---|---|')
    for k, v in C.items():
        L.append(f"| {k} | {v['states_per_decision']:.1f} | {v['ms_per_decision_mean']:.2f} | {v['ms_per_decision_median']:.2f} | "
                 f"{'-' if v['acceptance'] is None else format(v['acceptance'], '.3f')} |")
    L.append('')
    L.append('## Paired root-level differences on eval roots (a - b, lower is better; 95% bootstrap CI)')
    for k, v in list(P.items()) + list(res['paired_cost'].items()):
        L.append(f"- {k}: mean {v['mean']:+.5f} CI [{v['ci95'][0]:+.5f}, {v['ci95'][1]:+.5f}], a lower {v['a_lower']}, b lower {v['b_lower']}, ties {v['ties']}, n {v['n']}")
    L.append('')
    fam = res['state_metrics_by_family']
    L.append('## Higher-order family (state regret / state accuracy / executed regret)')
    for k, v in fam.items():
        h = v['higher']
        L.append(f"- {k}: {h['state_regret']:.4f} / {h['state_acc']:.4f} / {h['executed_regret']:.5f}")
    L.append('')
    pf = res['preflight']
    L.append('## Preflight (dev pilot, strict), verbatim')
    L.append(f"exit code {pf['exit_code']}; best learned by dev state regret: {res['best_learned_by_dev']}")
    L.append('```')
    L.append(pf['stdout'].strip())
    L.append('```')
    L.append('')
    L.append(f"Training CPU seconds (sum over jobs) {res['selection']['train_cpu_s']:.0f}; wall {res['selection']['train_wall_s']:.0f}.")
    L.append('Source sha256 are in mit12_result.json.')
    (OUT / 'MIT12_REPORT.md').write_text('\n'.join(L) + '\n', encoding='utf8')


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else ''
    if stage == 'build':
        stage_build()
    elif stage == 'train':
        stage_train()
    elif stage == 'eval':
        stage_eval()
    elif stage == 'report':
        stage_report()

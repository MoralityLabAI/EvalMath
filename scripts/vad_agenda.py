"""VAD-10: exact finite oracle for research-agenda selection over a dependency hypergraph.

Vertices are propositions 0..n-1; premises of every hyperedge have smaller indices than its conclusion.
A hidden world fixes which hyperedges exist. The agent holds a verified library L (bitmask), a posterior
over worlds, and an integer budget. Actions: attempt an edge whose premises are verified (reveals whether
it exists; success verifies its conclusion and pays the conclusion's reward once), run an information
experiment (noisy signal about the world), or stop. At stop, the library is scored against a future
distribution: N iid future targets with law mu, each costing D_{L,w}(g) reference units (1 if verified,
else min over existing edges of edge cost + sum of premise costs, capped). All arithmetic is Fraction.
"""
from fractions import Fraction as F
from dataclasses import dataclass
from itertools import product
from random import Random

STOP = ("stop",)


@dataclass(frozen=True)
class Edge:
    premises: tuple
    concl: int
    cost: int


@dataclass(frozen=True)
class Experiment:
    cost: int
    lik: tuple  # lik[y][w]: probability of signal y in world w; columns sum to 1


@dataclass(frozen=True)
class Instance:
    n: int
    facts: tuple
    edges: tuple
    prior: tuple  # prior[w]: probability of world w
    worlds: tuple  # worlds[w]: frozenset of existing edge indices
    reward: tuple  # reward[v], paid on first verification by an attempt
    mu: tuple  # future-target law over vertices
    N: int
    cap: int
    budget: int
    lam: F = F(0)  # utility charged per budget unit spent
    experiments: tuple = ()

    def check(self):
        assert sum(self.prior) == 1 and len(self.prior) == len(self.worlds)
        for e in self.edges:
            assert all(u < e.concl for u in e.premises) and e.cost >= 1
        assert sum(self.mu) == 1
        for x in self.experiments:
            for w in range(len(self.worlds)):
                assert sum(row[w] for row in x.lik) == 1


def mask(vs):
    m = 0
    for v in vs:
        m |= 1 << v
    return m


class Oracle:
    def __init__(self, inst):
        inst.check()
        self.i = inst
        self.start = mask(inst.facts)
        self._J = {}
        self._memo = {}
        self.nodes = 0  # memo misses in value()
        self.qevals = 0  # calls of q(): planning work including the root decision

    # ---- terminal (deployment) value -------------------------------------------------------
    def J(self, L, w):
        key = (L, w)
        if key in self._J:
            return self._J[key]
        i = self.i
        D = [0] * i.n
        present = [e for k, e in enumerate(i.edges) if k in i.worlds[w]]
        for v in range(i.n):
            if L >> v & 1:
                D[v] = 1
                continue
            best = i.cap
            for e in present:
                if e.concl == v:
                    best = min(best, e.cost + sum(D[u] for u in e.premises))
            D[v] = min(best, i.cap)
        val = -i.N * sum(m * d for m, d in zip(i.mu, D))
        self._J[key] = val
        return val

    def terminal(self, L, pi):
        return sum(p * self.J(L, w) for w, p in enumerate(pi) if p)

    # ---- actions -----------------------------------------------------------------------------
    def actions(self, L, pi, b):
        i = self.i
        out = [STOP]
        for k, e in enumerate(i.edges):
            if L >> e.concl & 1 or e.cost > b:
                continue
            if all(L >> u & 1 for u in e.premises) and any(p for w, p in enumerate(pi) if k in i.worlds[w]):
                out.append(("att", k))
        for j, x in enumerate(i.experiments):
            if x.cost <= b:
                out.append(("exp", j))
        return out

    def branches(self, L, pi, b, a, lik_override=None):
        """List of (prob, immediate utility, L', pi', b') for an action."""
        i = self.i
        if a[0] == "att":
            k = a[1]; e = i.edges[k]
            ps = sum(p for w, p in enumerate(pi) if k in i.worlds[w])
            out = []
            if ps:
                post = tuple(p / ps if k in i.worlds[w] else F(0) for w, p in enumerate(pi))
                out.append((ps, i.reward[e.concl] - i.lam * e.cost, L | 1 << e.concl, post, b - e.cost))
            if ps != 1:
                post = tuple(p / (1 - ps) if k not in i.worlds[w] else F(0) for w, p in enumerate(pi))
                out.append((1 - ps, -i.lam * e.cost, L, post, b - e.cost))
            return out
        x = i.experiments[a[1]]
        out = []
        for row in x.lik:
            py = sum(p * row[w] for w, p in enumerate(pi))
            if py:
                post = tuple(p * row[w] / py for w, p in enumerate(pi))
                out.append((py, -i.lam * x.cost, L, post, b - x.cost))
        return out

    # ---- value with bounded lookahead ---------------------------------------------------------
    def value(self, L, pi, b, depth=None):
        """Optimal value; depth limits the number of further actions (None = unlimited)."""
        if depth == 0:
            return self.terminal(L, pi)
        key = (L, pi, b, depth)
        if key in self._memo:
            return self._memo[key]
        self.nodes += 1
        best = self.terminal(L, pi)
        for a in self.actions(L, pi, b)[1:]:
            q = self.q(L, pi, b, a, None if depth is None else depth - 1)
            if q > best:
                best = q
        self._memo[key] = best
        return best

    def q(self, L, pi, b, a, depth=None):
        self.qevals += 1
        if a == STOP:
            return self.terminal(L, pi)
        return sum(p * (u + self.value(L2, pi2, b2, depth)) for p, u, L2, pi2, b2 in self.branches(L, pi, b, a))

    def best_action(self, L, pi, b, k=None):
        """Argmax action when each action is followed by an optimal continuation of at most k steps.
        Ties keep the earlier action in the order stop, attempts, experiments."""
        acts = self.actions(L, pi, b)
        best, ba = None, None
        for a in acts:
            q = self.q(L, pi, b, a, k)
            if best is None or q > best:
                best, ba = q, a
        return ba, best

    # ---- decomposition ------------------------------------------------------------------------
    def decompose(self, L, pi, b, a):
        """Q(a) = V(L,pi,b') + immediate + reuse + information, telescoped in two orders.
        reuse: E[V(L',pi,b')-V(L,pi,b')]; info: E[V(L',pi',b')-V(L',pi,b')] (library first).
        The other order swaps them; the gap is the interaction."""
        i = self.i
        cost = i.edges[a[1]].cost if a[0] == "att" else i.experiments[a[1]].cost
        b2 = b - cost
        base = self.value(L, pi, b2)
        br = self.branches(L, pi, b, a)
        imm = sum(p * u for p, u, *_ in br)
        reuse = sum(p * (self.value(L2, pi, b2) - base) for p, _, L2, _, _ in br)
        info = sum(p * (self.value(L2, pi2, b2) - self.value(L2, pi, b2)) for p, _, L2, pi2, _ in br)
        info_first = sum(p * (self.value(L, pi2, b2) - base) for p, _, _, pi2, _ in br)
        reuse_after = sum(p * (self.value(L2, pi2, b2) - self.value(L, pi2, b2)) for p, _, L2, pi2, _ in br)
        q = self.q(L, pi, b, a)
        assert q == base + imm + reuse + info == base + imm + info_first + reuse_after
        return dict(q=q, base=base, immediate=imm, reuse=reuse, information=info,
                    information_first=info_first, reuse_after_information=reuse_after,
                    interaction=reuse - reuse_after)


# ---- policies and forward evaluation -----------------------------------------------------------

def policy_direct(orc, L, pi, b):
    """Goal-directed baseline: pursue the highest-reward unverified target, through its best attemptable
    edge, or else through prerequisites of that target (edges concluding any ancestor of it)."""
    i = orc.i
    acts = orc.actions(L, pi, b)
    order = sorted((v for v in range(i.n) if i.reward[v] > 0 and not L >> v & 1), key=lambda v: (-i.reward[v], v))
    for v in order:
        anc, stack = {v}, [v]
        while stack:
            x = stack.pop()
            for e in i.edges:
                if e.concl == x:
                    for u in e.premises:
                        if u not in anc:
                            anc.add(u); stack.append(u)
        for tier in ({v}, anc - {v}):
            cands = []
            for a in acts[1:]:
                if a[0] == "att" and i.edges[a[1]].concl in tier:
                    e = i.edges[a[1]]
                    ps = sum(p for w, p in enumerate(pi) if a[1] in i.worlds[w])
                    cands.append((-ps / e.cost, a[1], a))
            if cands:
                return [(min(cands)[2], F(1))]
    return [(STOP, F(1))]


def policy_random(orc, L, pi, b):
    acts = [a for a in orc.actions(L, pi, b) if a != STOP and a[0] == "att"]
    if not acts:
        return [(STOP, F(1))]
    return [(a, F(1, len(acts))) for a in acts]


def policy_lookahead(k):
    def pol(orc, L, pi, b):
        return [(orc.best_action(L, pi, b, k)[0], F(1))]
    return pol


def evaluate(true_inst, assumed_orc, policy):
    """Exact expected utility of a policy that plans with assumed_orc's model while the world follows
    true_inst. Walks the true joint tree (worlds x signals); independent of the Bellman recursion."""
    T = Oracle(true_inst)
    A = assumed_orc

    def go(L, b, tw, aw):
        mass = sum(tw)
        if not mass:
            return F(0)
        acts = policy(A, L, aw, b)
        total = F(0)
        for a, pa in acts:
            if a == STOP:
                total += pa * sum(t * T.J(L, w) for w, t in enumerate(tw) if t)
                continue
            if a[0] == "att":
                k = a[1]; e = true_inst.edges[k]
                ts = [t if k in true_inst.worlds[w] else F(0) for w, t in enumerate(tw)]
                tf = [t if k not in true_inst.worlds[w] else F(0) for w, t in enumerate(tw)]
                ps = sum(p for w, p in enumerate(aw) if k in true_inst.worlds[w])
                a_s = tuple(p / ps if k in true_inst.worlds[w] else F(0) for w, p in enumerate(aw)) if ps else aw
                a_f = tuple(p / (1 - ps) if k not in true_inst.worlds[w] else F(0) for w, p in enumerate(aw)) if ps != 1 else aw
                cost = e.cost
                total += pa * (sum(ts) * (true_inst.reward[e.concl]) - true_inst.lam * cost * mass
                               + go(L | 1 << e.concl, b - cost, ts, a_s) + go(L, b - cost, tf, a_f))
            else:
                x_t = true_inst.experiments[a[1]]; x_a = A.i.experiments[a[1]]
                total += pa * (-true_inst.lam * x_t.cost * mass)
                for y in range(len(x_t.lik)):
                    tws = [t * x_t.lik[y][w] for w, t in enumerate(tw)]
                    awu = [p * x_a.lik[y][w] for w, p in enumerate(aw)]
                    z = sum(awu)
                    awn = tuple(p / z for p in awu) if z else aw
                    total += pa * go(L, b - x_t.cost, tws, awn)
        return total

    return go(A.start, true_inst.budget, list(true_inst.prior), A.i.prior)


def solve(inst):
    o = Oracle(inst)
    return o, o.value(o.start, inst.prior, inst.budget)


# ---- instance builders --------------------------------------------------------------------------

def independent_worlds(probs):
    worlds, prior = [], []
    for bits in product((0, 1), repeat=len(probs)):
        pr = F(1)
        for bit, p in zip(bits, probs):
            pr *= p if bit else 1 - p
        if pr:
            worlds.append(frozenset(k for k, bit in enumerate(bits) if bit)); prior.append(pr)
    return tuple(prior), tuple(worlds)


def build(n, facts, edges, probs, reward, mu, N, cap, budget, lam=F(0)):
    prior, worlds = independent_worlds(probs)
    return Instance(n, tuple(facts), tuple(Edge(tuple(p), c, k) for p, c, k in edges), prior, worlds,
                    tuple(F(r) for r in reward), tuple(F(m) for m in mu), N, cap, budget, F(lam))


def strategic_intermediate(p_direct=F(1, 5), q=F(4, 5), s=F(4, 5), reward=10, N=4, budget=3):
    """T (reward) has a costly direct edge and a cheap route through M; M also makes future G cheap."""
    edges = [((0,), 2, 2), ((0,), 1, 1), ((1,), 2, 1), ((1,), 3, 4), ((0,), 3, 10)]
    probs = [p_direct, q, s, F(1), F(1)]
    mu = [0, 0, 0, 1]
    return build(4, [0], edges, probs, [0, 0, reward, 0], mu, N, 20, budget)


def complementary(N=3, budget=16):
    """Two lemmas that each cost 8 to derive (deployment gives up at the cap 10) pay only together."""
    edges = [((0,), 1, 8), ((0,), 2, 8), ((1, 2), 3, 2)]
    return build(4, [0], edges, [F(1)] * 3, [0, 0, 0, 0], [0, 0, 0, 1], N, 10, budget)


def chain(k, p=F(9, 10), reward=10, budget=None):
    """Delayed payoff: only the end of a k-edge chain pays; intermediate lemmas have no reuse value."""
    edges = [((v,), v + 1, 1) for v in range(k)]
    rew = [0] * k + [reward]
    mu = [1] + [0] * k
    return build(k + 1, [0], edges, [p] * k, rew, mu, 1, 5, k if budget is None else budget)


def misleading_signal(true_reliable=False):
    """Two candidate routes to a rewarded target; a cheap automated check is read as a signal.
    Assumed: the check raises (hi) when route A exists. True model may reverse this."""
    edges = [((0,), 1, 2), ((0,), 1, 2)]  # route A, route B, same conclusion, mutually exclusive
    worlds = (frozenset({0}), frozenset({1}))
    prior = (F(1, 2), F(1, 2))

    def inst(lik_hi):  # lik_hi[w] = P(hi | world)
        x = Experiment(1, ((lik_hi[0], lik_hi[1]), (1 - lik_hi[0], 1 - lik_hi[1])))
        return Instance(2, (0,), tuple(Edge(*e) for e in ((( 0,), 1, 2), ((0,), 1, 2))), prior, worlds,
                        (F(0), F(10)), (F(1), F(0)), 1, 5, 3, F(0), (x,))
    assumed = inst((F(9, 10), F(1, 10)))
    true = inst((F(1, 5), F(4, 5)) if not true_reliable else (F(9, 10), F(1, 10)))
    return assumed, true


def failed_attempt_information():
    """Exactly one of two routes exists; the first attempt is a pure experiment for the second."""
    worlds = (frozenset({0}), frozenset({1}))
    return Instance(2, (0,), (Edge((0,), 1, 1), Edge((0,), 1, 1)), (F(1, 2), F(1, 2)), worlds,
                    (F(0), F(6)), (F(1), F(0)), 1, 5, 2)


def random_instance(seed, kind):
    r = Random(seed)
    if kind == "modular":
        m = r.randint(3, 6)
        edges = [((0,), v + 1, 1) for v in range(m)]
        probs = [F(r.randint(1, 9), 10) for _ in edges]
        rew = [0] + [r.randint(0, 6) for _ in range(m)]
        mu = [r.randint(0, 3) for _ in range(m + 1)]
        mu = [F(x, sum(mu)) if sum(mu) else F(0) for x in mu]
        if sum(mu) != 1:
            mu = [F(1)] + [F(0)] * m
        return build(m + 1, [0], edges, probs, rew, mu, r.randint(1, 5), 12, r.randint(1, m))
    n = r.randint(5, 6)
    edges = []
    for v in range(1, n):
        for _ in range(r.randint(1, 2)):
            if len(edges) >= 7:
                break
            pr = tuple(sorted(r.sample(range(v), r.randint(1, min(2, v)))))
            edges.append((pr, v, r.randint(1, 3)))
    probs = [F(r.randint(2, 9), 10) for _ in edges]
    rew = [0] + [r.choice([0, 0, 2, 5, 9]) for _ in range(n - 1)]
    mu = [r.randint(0, 3) for _ in range(n)]
    s = sum(mu)
    mu = [F(x, s) for x in mu] if s else [F(1)] + [F(0)] * (n - 1)
    return build(n, [0], edges, probs, rew, mu, r.randint(1, 5), 14, r.randint(2, 5))


def correlated_instance(seed):
    """Latent regime (good/bad) shifts every edge probability; a costed experiment reveals it with noise."""
    r = Random(seed)
    base = random_instance(seed, "layered")
    m = len(base.edges)
    pg = [F(r.randint(5, 9), 10) for _ in range(m)]
    pb = [F(r.randint(1, 4), 10) for _ in range(m)]
    prior, worlds = [], []
    for t, ps in enumerate((pg, pb)):
        pr_, wl = independent_worlds(ps)
        prior += [x / 2 for x in pr_]; worlds += list(wl)
        if t == 0:
            n_good = len(wl)
    lik = (tuple(F(9, 10) if w < n_good else F(1, 10) for w in range(len(worlds))),
           tuple(F(1, 10) if w < n_good else F(9, 10) for w in range(len(worlds))))
    return Instance(base.n, base.facts, base.edges, tuple(prior), tuple(worlds), base.reward, base.mu, base.N,
                    base.cap, base.budget, F(0), (Experiment(1, lik),))


def knapsack():
    """Unequal costs: the best single net gain uses the whole budget; two cheaper attempts beat it."""
    edges = [((0,), 1, 2), ((0,), 2, 1), ((0,), 3, 1)]
    return build(4, [0], edges, [F(1)] * 3, [0, 3, 2, 2], [1, 0, 0, 0], 1, 5, 2)

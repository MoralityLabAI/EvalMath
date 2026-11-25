"""VAD-12 instance families and controller-facing features for the exact VAD-10 oracle.

Training families reuse the VAD-10 'layered' and 'correlated' generators. Fresh test families change the
graph structure: wider graphs, planted complementary lemma pairs (deployment gives up at the cap unless both
lemmas are verified) and planted delayed-payoff chains. All instances stay small enough for the exact oracle.
"""
from fractions import Fraction as F
from random import Random

import vad_agenda as g

E_MAX = 8
N_SLOT = E_MAX + 2 + 1  # edge slots, two experiment slots, stop
FDIM = 14


def _mu(r, n, hot=None, mass=F(1, 2)):
    raw = [r.randint(0, 2) for _ in range(n)]
    if hot is not None:
        raw = [0] * n
        raw[hot] = 1
        rest = [r.randint(0, 2) if v != hot else 0 for v in range(n)]
        s = sum(rest)
        mu = [(1 - mass) * F(x, s) if s else F(0) for x in rest]
        mu[hot] += mass if s else F(1)
        return mu
    s = sum(raw)
    return [F(x, s) for x in raw] if s else [F(1)] + [F(0)] * (n - 1)


def _base_edges(r, n, limit):
    edges = []
    for v in range(1, n):
        for _ in range(r.randint(1, 2)):
            if len(edges) >= limit:
                break
            pr = tuple(sorted(r.sample(range(v), r.randint(1, min(2, v)))))
            edges.append((pr, v, r.randint(1, 3)))
    return edges


def fresh(seed, kind):
    r = Random(seed)
    if kind == "wide":
        n = r.randint(7, 8)
        edges = _base_edges(r, n, 7)
        probs = [F(r.randint(2, 9), 10) for _ in edges]
        rew = [0] + [r.choice([0, 0, 2, 5, 9]) for _ in range(n - 1)]
        return g.build(n, [0], edges, probs, rew, _mu(r, n), r.randint(1, 5), 14, r.randint(3, 5))
    if kind == "complementary":
        n0 = 4
        edges = _base_edges(r, n0, 3)
        a, b, f = n0, n0 + 1, n0 + 2
        edges += [((0,), a, r.randint(2, 3)), ((0,), b, r.randint(2, 3)), ((a, b), f, 1)]
        probs = [F(r.randint(3, 9), 10) for _ in edges[:-3]] + [F(r.randint(7, 10), 10), F(r.randint(7, 10), 10), F(1)]
        rew = [0] + [r.choice([0, 0, 3, 6]) for _ in range(n0 - 1)] + [0, 0, 0]
        n = n0 + 3
        return g.build(n, [0], edges, probs, rew, _mu(r, n, hot=f), r.randint(2, 5), 9, r.randint(4, 6))
    if kind == "chain":
        n0 = 3
        edges = _base_edges(r, n0, 3)
        c1, c2, c3 = n0, n0 + 1, n0 + 2
        edges += [((0,), c1, r.randint(1, 2)), ((c1,), c2, r.randint(1, 2)), ((c2,), c3, 1)]
        probs = [F(r.randint(3, 9), 10) for _ in edges[:-3]] + [F(r.randint(8, 10), 10) for _ in range(3)]
        rew = [0] + [r.choice([0, 0, 2]) for _ in range(n0 - 1)] + [0, 0, r.randint(8, 14)]
        n = n0 + 3
        return g.build(n, [0], edges, probs, rew, _mu(r, n), 1, 14, r.randint(3, 5))
    raise ValueError(kind)


def train_instance(seed):
    kind = ("layered", "modular", "correlated")[seed % 3]
    if kind == "correlated":
        return g.correlated_instance(seed)
    return g.random_instance(seed, kind)


# ---- controller features --------------------------------------------------------------------------

def structure(inst):
    """Static graph features per edge: descendant reward mass, descendant future mass, child count, depth to reward."""
    out = []
    for k, e in enumerate(inst.edges):
        desc, stack = {e.concl}, [e.concl]
        while stack:
            x = stack.pop()
            for e2 in inst.edges:
                if x in e2.premises and e2.concl not in desc:
                    desc.add(e2.concl)
                    stack.append(e2.concl)
        out.append((float(sum(inst.reward[v] for v in desc)) / 10, float(sum(inst.mu[v] for v in desc)),
                    sum(1 for e2 in inst.edges if e.concl in e2.premises) / 3, len(desc) / 4))
    return out


def features(orc, L, pi, b, struct, oracle_features=False):
    """(N_SLOT, FDIM) float rows, mask over actions. Slot layout: edges, experiments, stop."""
    inst = orc.i
    rows = [[0.0] * FDIM for _ in range(N_SLOT)]
    mask = [False] * N_SLOT
    acts = set(orc.actions(L, pi, b))
    stop_val = orc.terminal(L, pi)
    for k, e in enumerate(inst.edges):
        ps = float(sum(p for w, p in enumerate(pi) if k in inst.worlds[w]))
        row = rows[k]
        feas = ("att", k) in acts
        mask[k] = feas
        row[0] = 1.0
        row[1] = float(feas)
        row[2] = ps
        row[3] = e.cost / 5
        row[4] = float(inst.reward[e.concl]) / 10
        row[5] = float(inst.mu[e.concl])
        row[6] = float(bool(L >> e.concl & 1))
        row[7] = len(e.premises) / 3
        row[8] = sum(1 for u in e.premises if L >> u & 1) / max(1, len(e.premises))
        row[9], row[10], row[11], row[12] = struct[k]
        row[13] = b / 6
        if oracle_features and feas:
            row[13] = float(orc.q(L, pi, b, ("att", k), 0) - stop_val) / 10  # one-step net gain (privileged)
    for j, x in enumerate(inst.experiments[:2]):
        row = rows[E_MAX + j]
        feas = ("exp", j) in acts
        mask[E_MAX + j] = feas
        row[0] = -1.0
        row[1] = float(feas)
        row[3] = x.cost / 5
        row[13] = b / 6
    rows[N_SLOT - 1][0] = 2.0
    rows[N_SLOT - 1][13] = b / 6
    mask[N_SLOT - 1] = True
    return rows, mask


def action_of_slot(inst, slot):
    if slot < E_MAX:
        return ("att", slot)
    if slot == N_SLOT - 1:
        return g.STOP
    return ("exp", slot - E_MAX)


def slot_of_action(a):
    if a == g.STOP:
        return N_SLOT - 1
    return a[1] if a[0] == "att" else E_MAX + a[1]

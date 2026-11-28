"""Independent, deliberately naive evaluator for VAD-10: explicit history trees, Bayes from the prior at
every node, fixpoint (not topological) reference costs. Shares only the Instance dataclass."""
from fractions import Fraction as F


def ref_cost(inst, library, world):
    D = {v: (1 if v in library else inst.cap) for v in range(inst.n)}
    changed = True
    while changed:
        changed = False
        for k, e in enumerate(inst.edges):
            if k in inst.worlds[world] and e.concl not in library:
                c = min(inst.cap, e.cost + sum(D[u] for u in e.premises))
                if c < D[e.concl]:
                    D[e.concl] = c
                    changed = True
    return D


def future_value(inst, library, world):
    D = ref_cost(inst, library, world)
    return -inst.N * sum(inst.mu[g] * D[g] for g in range(inst.n))


def opt(inst, library=None, history=(), budget=None):
    """history: tuple of (kind, index, result); the posterior is recomputed from the prior at every node."""
    library = frozenset(inst.facts) if library is None else library
    budget = inst.budget if budget is None else budget

    def weight(w):
        p = inst.prior[w]
        for kind, idx, res in history:
            if kind == "att":
                p = p if ((idx in inst.worlds[w]) == res) else F(0)
            else:
                p *= inst.experiments[idx].lik[res][w]
        return p

    ws = [weight(w) for w in range(len(inst.worlds))]
    Z = sum(ws)
    stop = sum(ws[w] / Z * future_value(inst, library, w) for w in range(len(ws)) if ws[w])
    best = stop
    for k, e in enumerate(inst.edges):
        if e.concl in library or e.cost > budget or not all(u in library for u in e.premises):
            continue
        ps = sum(ws[w] for w in range(len(ws)) if k in inst.worlds[w]) / Z
        if ps == 0:
            continue
        q = ps * (inst.reward[e.concl] - inst.lam * e.cost
                  + opt(inst, library | {e.concl}, history + (("att", k, True),), budget - e.cost))
        if ps != 1:
            q += (1 - ps) * (-inst.lam * e.cost + opt(inst, library, history + (("att", k, False),), budget - e.cost))
        best = max(best, q)
    for j, x in enumerate(inst.experiments):
        if x.cost > budget:
            continue
        q = F(0)
        for y in range(len(x.lik)):
            py = sum(ws[w] * x.lik[y][w] for w in range(len(ws))) / Z
            if py:
                q += py * (-inst.lam * x.cost + opt(inst, library, history + (("exp", j, y),), budget - x.cost))
        best = max(best, q)
    return best

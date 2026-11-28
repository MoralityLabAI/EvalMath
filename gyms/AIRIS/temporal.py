"""AIRIS-03: exact delayed-effect identifiability and active design."""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

# Input bits a,u,v. Coefficient bits alpha,beta,gamma,delta,epsilon,zeta.
# In an episode previous input and cumulative output reset to zero.
# Reset is a declared simulator operation; each episode costs two transitions.
INPUTS = tuple(range(8))
# Put nuisance pulses first for the declared fixed-order control.
PULSES = ((4, 0), (2, 0), (1, 0))
PROBES = PULSES + tuple(q for q in product(INPUTS, repeat=2) if q not in PULSES)
MODES = ("trajectory", "terminal")
POLICIES = ("fixed", "uniform", "collision", "goal", "optimal")
TARGET = frozenset((0, 1, 2, 3))
PASSIVE = (7, 7)
WORLDS = tuple(range(64))


def parity(x):
    return x.bit_count() % 2


def row(now, previous):
    if now not in INPUTS or previous not in INPUTS:
        raise ValueError("input outside declared grammar")
    return sum((((now >> j) & 1) << (2*j)) |
               (((previous >> j) & 1) << (2*j+1)) for j in range(3))


def rows(q, mode):
    if mode not in MODES or len(q) != 2:
        raise ValueError("invalid episode")
    r0, r1 = row(q[0], 0), row(q[1], q[0])
    # We observe cumulative state, not a free additional delta sensor.
    return (r0, r0 ^ r1) if mode == "trajectory" else (r0 ^ r1,)


def simulate(w, q, mode):
    if w not in WORLDS or mode not in MODES or len(q) != 2:
        raise ValueError("invalid episode")
    previous = state = 0
    trace = []
    for x in q:
        if x not in INPUTS:
            raise ValueError("input outside declared grammar")
        # Independent transition calculation, without using design rows.
        for j in range(3):
            state ^= ((x >> j) & 1) * ((w >> (2*j)) & 1)
            state ^= ((previous >> j) & 1) * ((w >> (2*j+1)) & 1)
        trace.append(state)
        previous = x
    return tuple(trace) if mode == "trajectory" else (trace[-1],)


@lru_cache(None)
def extend(space, rs):
    s = set(space)
    for r in rs:
        s |= {x ^ r for x in s}
    return frozenset(s)


def rank(space):
    return len(space).bit_length() - 1


INITIAL = extend(frozenset((0,)), rows(PASSIVE, "trajectory"))


def target_rank(space):
    return rank(space & TARGET)


def certificate(space):
    return target_rank(space) == 2


def posterior(history):
    return tuple(w for w in WORLDS if all(
        simulate(w, q, mode) == o for q, mode, o in history))


def predict(worlds, q, mode):
    counts = {}
    for w in worlds:
        o = simulate(w, q, mode)
        counts[o] = counts.get(o, 0) + 1
    return {o: F(n, len(worlds)) for o, n in counts.items()}


def history_space(history):
    space = frozenset((0,))
    for q, mode, _ in history:
        space = extend(space, rows(q, mode))
    return space


@lru_cache(None)
def options(space, mode):
    return tuple((q, nxt) for q in PROBES
                 if (nxt := extend(space, rows(q, mode))) != space)


@lru_cache(None)
def value(space, mode, remaining, policy):
    """Exact success probability over policy randomization.

    Linear queries have outcome-independent posterior direction spaces.
    The uniform prior on each nonempty affine fibre makes all attainable
    outcome transcripts equiprobable. Hence information gains and goal
    identification depend only on the row space, not the observed values.
    """
    if remaining == 0 or certificate(space):
        return F(certificate(space))
    opts = options(space, mode)
    if not opts:
        return F(0)
    if policy == "fixed":
        return value(opts[0][1], mode, remaining-1, policy)
    if policy == "goal":
        _, nxt = max(opts, key=lambda item: (target_rank(item[1]), rank(item[1])))
        return value(nxt, mode, remaining-1, policy)
    if policy == "optimal":
        return max(value(nxt, mode, remaining-1, policy) for _, nxt in opts)
    if policy == "collision":
        # Uniform over ALL maximum-collision probes, no lucky tie ordering.
        # Collision probability of distinct outputs = 1 - 2^(-rank gain).
        best = max(rank(nxt) for _, nxt in opts)
        opts = tuple((q, nxt) for q, nxt in opts if rank(nxt) == best)
    elif policy != "uniform":
        raise ValueError("unknown policy")
    return sum(value(nxt, mode, remaining-1, policy) for _, nxt in opts) / len(opts)


def goal_trace(w, mode, budget):
    history = [(PASSIVE, "trajectory", simulate(w, PASSIVE, "trajectory"))]
    space = INITIAL
    for _ in range(budget):
        if certificate(space):
            break
        opts = options(space, mode)
        if not opts:
            break
        q, space = max(opts, key=lambda item: (target_rank(item[1]), rank(item[1])))
        history.append((q, mode, simulate(w, q, mode)))
    ws = posterior(history)
    targets = {x & 3 for x in ws}
    if certificate(space) != (len(targets) == 1):
        raise AssertionError("certificate disagrees with hidden-world oracle")
    return {"history": history, "compatible_world_count": len(ws),
            "compatible_action_responses": sorted(targets),
            "active_transitions": 2*(len(history)-1),
            "certified": certificate(space),
            "response": next(iter(targets)) if len(targets) == 1 else None}


def receipt():
    aggregates = {}
    for mode in MODES:
        for budget in range(3):
            aggregates[f"{mode}:episodes{budget}"] = {
                p: str(value(INITIAL, mode, budget, p)) for p in POLICIES}
    return {
        "experiment": "AIRIS-03", "evidence": "exact finite synthetic development",
        "world_count": len(WORLDS), "passive_fibres": 4,
        "worlds_per_passive_fibre": 16, "passive_rank": rank(INITIAL),
        "passive_target_rank": target_rank(INITIAL),
        "episode_transition_cost": 2, "passive_transition_cost": 2,
        "budget_semantics": "maximum active transitions; early stop on certificate",
        "candidate_episodes": len(PROBES),
        "uniform_policy_semantics": "uniform over informative ordered input pairs",
        "collision_policy_semantics": "uniform among all maximal total-rank-gain ordered input pairs",
        "aggregates": aggregates,
        "rows": [{"root": w, "mode": mode, "episode_budget": b,
                  "trace": goal_trace(w, mode, b)}
                 for w in WORLDS for mode in MODES for b in range(3)],
        "source_sha256": {name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                          for name in ("temporal.py", "test_temporal.py", "TEMPORAL.md")}
    }


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))

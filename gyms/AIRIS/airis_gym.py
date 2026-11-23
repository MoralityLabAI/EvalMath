"""Exact finite AIRIS-inspired rule learning and active experimentation."""
from collections import deque
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

MASKS = (6, 3, 5)  # decor, route, support
ACTIONS = ("decor", "route", "support")
AFFINE = tuple(t for t in range(16) if t.bit_count() % 2 == 0)
PROBES = tuple((a, c) for a in range(3) for c in (1, 2))
GOALS = ((1, 1), (3, 3))  # (mask, target)
POLICIES = ("fixed", "confidence", "collision", "goal")


def bit(table, context):
    return (table >> context) & 1


def require_state(c, a, s):
    if not (0 <= c < 4 and 0 <= a < 3 and 0 <= s < 8):
        raise ValueError("out of domain")


class Belief:
    def __init__(self):
        self.rules = tuple(
            AFFINE if mask & (1 << j) else (0,)
            for mask in MASKS for j in range(3)
        )

    def observe(self, c, a, before, after):
        require_state(c, a, before)
        require_state(c, a, after)
        delta = before ^ after
        updated = list(self.rules)
        for j in range(3):
            k = 3 * a + j
            updated[k] = tuple(t for t in self.rules[k] if bit(t, c) == ((delta >> j) & 1))
            if not updated[k]:
                raise ValueError("observation contradicts grammar")
        self.rules = tuple(updated)

    def predict(self, c, a):
        require_state(c, a, 0)
        pools = self.rules[3*a:3*a+3]
        probs = [F(sum(bit(t, c) for t in pool), len(pool)) for pool in pools]
        out = {}
        for d in range(8):
            p = F(1)
            for j, p1 in enumerate(probs):
                p *= p1 if d & (1 << j) else 1 - p1
            if p:
                out[d] = p
        return out

    def updated(self, q, d):
        a, c = q
        b = Belief()
        b.rules = self.rules
        b.observe(c, a, 0, d)
        return b

    def plan(self, c, start, mask, target):
        require_state(c, 0, start)
        if not (0 < mask < 8 and 0 <= target < 8 and target & ~mask == 0):
            raise ValueError("invalid goal")
        edges = []
        for a in range(3):
            outcomes = self.predict(c, a)
            if len(outcomes) == 1:
                edges.append((a, next(iter(outcomes))))
        queue = deque([(start, ())])
        seen = {start}
        while queue:
            s, path = queue.popleft()
            if s & mask == target:
                return path
            for a, delta in edges:
                nxt = s ^ delta
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, path + (a,)))
        return None

    def candidates(self):
        return tuple(q for q in PROBES if len(self.predict(q[1], q[0])) > 1)


def passive_belief():
    b = Belief()
    for a, mask in enumerate(MASKS):
        b.observe(0, a, 0, 0)
        b.observe(3, a, 0, mask)
    return b


def roots():
    # Each root is one distinct tuple of nine truth tables. Uniform over the
    # posterior after the common passive observations.
    return product(*passive_belief().rules)


def outcome(world, c, a):
    return sum(bit(world[3*a+j], c) << j for j in range(3))


def collision(p):
    return 1 - sum(v*v for v in p.values())


def plan_success(b, goal):
    return b.plan(1, 0, *goal) is not None


def choose(b, policy, goal):
    if policy not in POLICIES:
        raise ValueError("unknown policy")
    qs = b.candidates()
    if not qs:
        return None
    if policy == "fixed":
        return qs[0]

    def score(q):
        a, c = q
        p = b.predict(c, a)
        if policy == "confidence":
            return 1 - max(p.values())
        if policy == "collision":
            return collision(p)
        return (sum(v for d, v in p.items()
                    if plan_success(b.updated(q, d), goal)), collision(p))
    return max(qs, key=score)


def trial(world, policy, goal, budget):
    b = passive_belief()
    trace = []
    for _ in range(budget):
        q = choose(b, policy, goal)
        if q is None:
            break
        a, c = q
        d = outcome(world, c, a)
        b = b.updated(q, d)
        trace.append((a, c, d))
    plan = b.plan(1, 0, *goal)
    if plan is not None:
        s = 0
        for a in plan:
            s ^= outcome(world, 1, a)
        if s & goal[0] != goal[1]:
            raise AssertionError("invalid certificate")
    return int(plan is not None), trace


def random_value(world, b, goal, remaining):
    qs = b.candidates()
    if not remaining or not qs:
        return F(plan_success(b, goal))
    return sum(random_value(world, b.updated(q, outcome(world, q[1], q[0])),
                            goal, remaining-1) for q in qs) / len(qs)


def receipt():
    worlds = tuple(roots())
    rows = []
    totals = {}
    for goal in GOALS:
        for budget in range(3):
            key = f"{goal[0]}:{goal[1]}:budget{budget}"
            sums = {p: F(0) for p in (*POLICIES, "random")}
            for i, world in enumerate(worlds):
                scores = {}
                traces = {}
                for p in POLICIES:
                    scores[p], traces[p] = trial(world, p, goal, budget)
                    sums[p] += scores[p]
                r = random_value(world, passive_belief(), goal, budget)
                sums["random"] += r
                scores["random"] = str(r)
                rows.append({"root": i, "rule_tables": world, "case": key,
                             "scores": scores, "traces": traces})
            totals[key] = {p: str(v/len(worlds)) for p, v in sums.items()}
    return {"experiment": "AIRIS-01", "evidence": "exact finite constructed development slice",
            "n_roots": len(worlds), "passive_cost": 6, "active_cost_budgets": [0, 1, 2],
            "upstream_runtime": "not executed", "aggregates": totals, "rows": rows,
            "source_sha256": {p.name: sha256(p.read_bytes()).hexdigest()
                              for p in (Path(__file__), Path(__file__).with_name("test_airis.py"),
                                        Path(__file__).with_name("README.md"))}}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))

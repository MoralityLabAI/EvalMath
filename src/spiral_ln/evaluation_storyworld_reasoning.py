"""SRG-01: finite storyworld authoring/decision audit (exact synthetic reference).

The information oracle is a static hidden-state experiment with deterministic
queries followed by one terminal action. It is not a Sweepweave engine or a
model evaluation. Probabilities and scores must be explicitly declared.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product


def squared_distance(x, y, weights):
    """HG-01 Clifford squared distance; weights are positive amplitudes."""
    if not (len(x) == len(y) == len(weights)) or any(w <= 0 for w in weights):
        raise ValueError("dimension/positive weights required")
    return sum((F(w) * (F(a) - F(b))) ** 2
               for a, b, w in zip(x, y, weights))


def effect_audit(x, successors, goal, weights):
    """Separate geometric energy and goal-directed progress for actual steps.

    A path is ordered; telescoping holds for one fixed goal and metric.
    Energies and shares are descriptive, not causal attribution or fairness.
    """
    if not successors:
        raise ValueError("nonempty path required")
    states = [x, *successors]
    energy = [squared_distance(a, b, weights)
              for a, b in zip(states, states[1:])]
    costs = [squared_distance(a, goal, weights) for a in states]
    progress = [a - b for a, b in zip(costs, costs[1:])]
    positive = sum(max(F(0), p) for p in progress)
    total = sum(energy)
    return {"energy": energy, "progress": progress,
            "net_progress": costs[0] - costs[-1],
            "max_energy_share": max(energy)/total if total else F(0),
            "max_positive_progress_share":
                max(max(F(0), p) for p in progress)/positive if positive else F(0)}


def winners(scores):
    if not scores:
        raise ValueError("empty reaction menu")
    best = max(scores)
    return frozenset(i for i, v in enumerate(scores) if v == best)


def linear_scores(x, coefficients, intercepts):
    if not coefficients or len(coefficients) != len(intercepts) or any(
            len(row) != len(x) for row in coefficients):
        raise ValueError("invalid reaction score dimensions")
    return tuple(F(b) + sum(F(a)*F(v) for a, v in zip(row, x))
                 for row, b in zip(coefficients, intercepts))


def formula_audit(states, scores):
    """Audit a supplied feasible-state table of deterministic reaction scores.

    A coordinate needs feasible one-coordinate pairs to identify its effect.
    Common-mode score changes cannot alter argmax selection. Ties are sets.
    Scores are not assumed to be probability weights.
    """
    if not states or len(states) != len(scores) or len(set(states)) != len(states):
        raise ValueError("nonempty distinct aligned states required")
    d = len(states[0])
    m = len(scores[0])
    if not m or any(len(s) != d for s in states) or any(len(s) != m for s in scores):
        raise ValueError("fixed dimensions required")
    score = [tuple(map(F, s)) for s in scores]
    choice = [winners(s) for s in score]
    pairs = [0]*d
    shifts = [0]*d
    flips = [0]*d
    for i, j in combinations(range(len(states)), 2):
        differing = [k for k in range(d) if states[i][k] != states[j][k]]
        if len(differing) != 1:
            continue
        k = differing[0]
        pairs[k] += 1
        delta = [b-a for a, b in zip(score[i], score[j])]
        shifts[k] += int(len(set(delta)) > 1)
        flips[k] += int(choice[i] != choice[j])
    margins = [sorted(s, reverse=True)[0] - sorted(s, reverse=True)[1]
               for s in score] if m > 1 else []
    return {"feasible_pairs": pairs, "relative_score_changes": shifts,
            "winner_set_changes": flips, "margins": margins,
            "unidentified": [k for k, n in enumerate(pairs) if n == 0]}


class DecisionProblem:
    """Finite information experiment; common terminal action menu across states.

    rows: states x terminal actions (utilities, e.g. 0/1 success).
    queries: queries x states (deterministic observable labels).
    prior: rational, nonnegative, sums to one.
    observation: initial public labels; no future information.
    """
    def __init__(self, rows, queries, prior, observation=None):
        self.rows = tuple(tuple(map(F, row)) for row in rows)
        self.queries = tuple(tuple(q) for q in queries)
        self.prior = tuple(map(F, prior))
        n = len(self.rows)
        self.observation = tuple(observation) if observation is not None else (0,)*n
        if (not n or not self.rows[0] or len(self.prior) != n
            or len(self.observation) != n or sum(self.prior) != 1
            or min(self.prior) < 0 or any(len(q) != n for q in self.queries)
            or any(len(row) != len(self.rows[0]) for row in self.rows)):
            raise ValueError("malformed decision problem")
        self.n_actions = len(self.rows[0])
        self.root = tuple(i for i, p in enumerate(self.prior) if p)

    def split(self, cell, labels):
        bins = {}
        for i in cell:
            bins.setdefault(labels[i], []).append(i)
        return tuple(tuple(v) for v in bins.values())

    def stop(self, cell):
        return max(sum(self.prior[i]*self.rows[i][a] for i in cell)
                   for a in range(self.n_actions))

    def full(self):
        return sum(self.prior[i]*max(self.rows[i]) for i in self.root)

    def value(self, budget, allowed=None):
        """Optimal adaptive expected utility with <= budget distinct queries."""
        if not isinstance(budget, int) or budget < 0:
            raise ValueError("nonnegative integer budget required")
        indices = tuple(range(len(self.queries))) if allowed is None else tuple(allowed)
        if len(set(indices)) != len(indices) or any(
                not 0 <= j < len(self.queries) for j in indices):
            raise ValueError("invalid query indices")

        @lru_cache(None)
        def rec(cell, remaining, k):
            best = self.stop(cell)
            if k:
                for q in remaining:
                    parts = self.split(cell, self.queries[q])
                    if len(parts) > 1:
                        rest = tuple(j for j in remaining if j != q)
                        best = max(best, sum(rec(part, rest, k-1) for part in parts))
            return best
        return sum(rec(part, indices, budget)
                   for part in self.split(self.root, self.observation))

    def fixed(self, indices):
        """Utility if a declared nonadaptive query set is disclosed."""
        indices = tuple(indices)
        if any(not 0 <= j < len(self.queries) for j in indices):
            raise ValueError("invalid query indices")
        labels = tuple((self.observation[i], *(self.queries[j][i] for j in indices))
                       for i in range(len(self.rows)))
        return sum(self.stop(cell) for cell in self.split(self.root, labels))

    def profile(self):
        curve = [self.value(k) for k in range(len(self.queries)+1)]
        full = self.full()
        return {"full": full, "public": curve[0], "available": curve[-1],
                "unobservable_gap": full-curve[-1],
                "adaptive_curve": curve,
                "min_budget_full": next((k for k, v in enumerate(curve) if v == full), None)}


def parity_problem(k, visible=None, nuisance=0):
    """Uniform binary support; k relevant coordinates, optional irrelevant bits.

    One coordinate can be queried at a time. Visible declares permitted queries.
    An implicit closed form is valid for this fixture only: 1/2 until all k
    relevant bits are available within budget, then 1.
    """
    if not 1 <= k or nuisance < 0 or k+nuisance > 10:
        raise ValueError("explicit census limited to 10 bits")
    states = tuple(product((0, 1), repeat=k+nuisance))
    rows = tuple((int(sum(s[:k]) % 2 == 0), int(sum(s[:k]) % 2 == 1))
                 for s in states)
    visible = tuple(range(k+nuisance)) if visible is None else tuple(visible)
    if len(set(visible)) != len(visible) or any(not 0 <= j < k+nuisance for j in visible):
        raise ValueError("invalid visible coordinates")
    queries = tuple(tuple(s[j] for s in states) for j in visible)
    return DecisionProblem(rows, queries, [F(1,len(states))]*len(states))


def independent_fixed_value(problem, budget):
    """Small independent enumeration: disclose fixed query sets, enumerate
    all response-contingent terminal policies. Exponential, tests only."""
    best = None
    for count in range(min(budget, len(problem.queries))+1):
        for chosen in combinations(range(len(problem.queries)), count):
            labels = [(problem.observation[i], *(problem.queries[j][i] for j in chosen))
                      for i in problem.root]
            distinct = list(dict.fromkeys(labels))
            for policy in product(range(problem.n_actions), repeat=len(distinct)):
                v = sum(problem.prior[i]*problem.rows[i][policy[distinct.index(label)]]
                        for i, label in zip(problem.root, labels))
                best = v if best is None else max(best, v)
    return best

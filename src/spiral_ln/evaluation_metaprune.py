"""MP-01 finite Bayesian research-budget decision, exact fractions only."""
from fractions import Fraction
from functools import lru_cache

def predict_and_update(prior, likelihood):
    """Yield (observation, predictive mass, normalized posterior) for supported outcomes."""
    assert len(prior) == len(likelihood) and len(prior) > 0
    assert sum(prior) == 1 and all(p >= 0 for p in prior)
    outcomes = sorted(set().union(*(set(row) for row in likelihood)))
    for row in likelihood:
        assert all(q >= 0 for q in row.values()) and sum(row.values()) == 1
    for o in outcomes:
        weights = tuple(prior[i] * likelihood[i].get(o, Fraction(0))
                        for i in range(len(prior)))
        mass = sum(weights)
        if mass:
            yield o, mass, tuple(w / mass for w in weights)

def terminal_value(prior):
    return max(prior)

def optimal_choice(prior, experiments, budget, price=Fraction(0)):
    """Return (optimal exact expected net utility, first action name or 'stop').

    Each experiment is (name, strictly positive integer cost, tuple of likelihood dicts).
    Repeated experiments are conditionally independent GIVEN the latent hypothesis;
    dependent experiments require history-enlarged hypotheses/kernels.
    """
    assert budget >= 0 and all(isinstance(cost, int) and cost > 0
                               for _, cost, _ in experiments)
    @lru_cache(None)
    def solve(p, b):
        best = terminal_value(p)
        choice = "stop"
        for name, cost, likelihood in experiments:
            if cost > b:
                continue
            expected = -price * cost
            for _, mass, posterior in predict_and_update(p, likelihood):
                expected += mass * solve(posterior, b - cost)[0]
            if expected > best:
                best, choice = expected, name
        return best, choice
    return solve(tuple(prior), budget)

def four_state_examples():
    q = Fraction
    prior = tuple(q(1, 4) for _ in range(4))
    split = tuple(({"L": q(1)} if i < 2 else {"R": q(1)}) for i in range(4))
    reveal = tuple({"?": q(3, 5), str(i): q(2, 5)} for i in range(4))
    return prior, (("split", 1, split), ("reveal", 1, reveal))

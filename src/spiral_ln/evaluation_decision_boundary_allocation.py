"""QI-04: quotient-feasibility-aware fractional experiment allocation.

The baseline and counterfactual Bernoulli rate tables are fixed as an
explicit candidate family BEFORE collecting any data. Each alternative
must cross the *actual* goal-visible one-step quotient feasibility
boundary, verified by an independent exact Fraction partition oracle.

The structured family is deliberately narrower than every feasible
rate-table perturbation. Its optimal fractional information allocation
is a necessary KL budget for that *specific family*, not a guarantee
of optimal transfer on unknown or out-of-support environments.

This module is a self-contained finite proof-of-contract companion to
QI-03; no neural model, training data, or paid API is involved.
"""
from fractions import Fraction as Q
from itertools import combinations, product

from spiral_ln.evaluation_quotient_fractional_cover import (
    fractional_information_cover, information_cost_lower_bound
)

N_STATES = 3
N_ACTIONS = 2
BASE_P = Q(1, 10)
ALT_P = Q(9, 10)
TV_TOLERANCE = Q(1, 5)
CLASS_BUDGET = 1
DELTA = Q(1, 20)


def _validate_rates(table):
    rates = tuple(tuple(Q(p) for p in row) for row in table)
    if not rates or not rates[0] or any(len(row)!=len(rates[0])
           or any(not 0 <= p <= 1 for p in row) for row in rates):
        raise ValueError("nonempty rectangular Bernoulli rate table required")
    if len(rates)>5:
        raise ValueError("finite reference optimizer capped at 5 transient states")
    return rates


def exact_quotient_radius(table, classes):
    """Independent exhaustive one-step hit/hold partition oracle.

    A class containing transient states with action rates p_i^a has
    optimal per-action TV radius half the range of those rates.
    The absorbing goal occupies its own separate macro class.
    """
    rates = _validate_rates(table)
    if type(classes) is not int or classes < 1:
        raise ValueError("positive transient macrostate budget required")
    n, d = len(rates), len(rates[0])
    def radius(labels):
        return max((
            (max(rates[i][a] for i in range(n) if labels[i]==z)
             - min(rates[i][a] for i in range(n) if labels[i]==z))/2
            for z in set(labels) for a in range(d)
        ),default=Q(0))
    return min(radius(labels) for labels in product(range(min(n,classes)),repeat=n))


def rate_table_from_mask(mask, base=BASE_P, alternative=ALT_P,
                         states=N_STATES, actions=N_ACTIONS):
    if type(states) is not int or type(actions) is not int or (
            states<2 or actions<1):
        raise ValueError("at least two states and one action required")
    if type(mask) is not int or not 0<=mask<(1<<(states*actions)):
        raise ValueError("perturbation mask must refer to declared cells")
    p, q = Q(base), Q(alternative)
    if not 0<p<1 or not 0<q<1 or p==q:
        raise ValueError("distinct strictly interior Bernoulli rates required")
    return tuple(tuple(q if mask&(1<<(i*actions+a)) else p
                       for a in range(actions)) for i in range(states))


def structured_supports(states=N_STATES, actions=N_ACTIONS):
    """Predeclared decision-aware alternative supports.

    For the 3x2 contract, each action-zero singleton is an alternative,
    while each pair of action-one state cells forms an alternative.
    In both cases the one-class quotient becomes infeasible.
    """
    if (states, actions)!=(3,2):
        raise ValueError("the registered structured family is 3 states x 2 actions")
    first_action_singles = tuple(1<<(i*actions) for i in range(states))
    second_action_pairs = tuple(
        (1<<(i*actions+1)) | (1<<(j*actions+1))
        for i,j in combinations(range(states),2))
    return first_action_singles+second_action_pairs


def decision_boundary_family(masks=None, base=BASE_P, alternative=ALT_P,
                             tolerance=TV_TOLERANCE,
                             classes=CLASS_BUDGET):
    """Ground proposed alternative supports in the actual quotient decision."""
    masks = structured_supports() if masks is None else tuple(masks)
    if not masks or len(set(masks))!=len(masks):
        raise ValueError("nonempty unique alternative-support masks required")
    tolerance = Q(tolerance)
    if not 0<=tolerance<=1:
        raise ValueError("TV tolerance must lie in [0,1]")
    baseline = rate_table_from_mask(0,base,alternative)
    baseline_radius = exact_quotient_radius(baseline,classes)
    if baseline_radius>tolerance:
        raise ValueError("declared baseline is already infeasible")
    worlds=[]
    for mask in masks:
        alternative_rates=rate_table_from_mask(mask,base,alternative)
        radius=exact_quotient_radius(alternative_rates,classes)
        worlds.append({
            "mask":mask,
            "rates":alternative_rates,
            "one_step_tv_optimum":radius,
            "crosses_boundary":radius>tolerance,
            "changed_cells":tuple(i for i in range(N_STATES*N_ACTIONS)
                                  if mask&(1<<i))
        })
    return {
        "baseline_rates":baseline,
        "baseline_tv_optimum":baseline_radius,
        "class_budget":classes,
        "tv_tolerance":tolerance,
        "alternatives":tuple(worlds),
        "boundary_masks":tuple(w["mask"] for w in worlds
                               if w["crosses_boundary"]),
        "nonboundary_masks":tuple(w["mask"] for w in worlds
                                  if not w["crosses_boundary"]),
    }


def boundary_fractional_certificate(rotated=False):
    """QI-03 exact rational LP with independently validated boundary labels."""
    masks=structured_supports()
    if rotated:
        # Half-turn exchanges which *action* receives the singleton prior.
        n=N_STATES*N_ACTIONS
        permutation=tuple((i+n//2)%n for i in range(n))
        masks=tuple(sum((1<<permutation[i] for i in range(n)
                         if mask&(1<<i)),0) for mask in masks)
    family=decision_boundary_family(masks)
    if family["nonboundary_masks"]:
        raise AssertionError("a claimed counterfactual has the same decision label")
    optimum=fractional_information_cover(N_STATES*N_ACTIONS,
                                         family["boundary_masks"])
    if optimum is None:
        raise AssertionError("missing distinguishing probe")
    lower=information_cost_lower_bound(N_STATES*N_ACTIONS,
              family["boundary_masks"],DELTA,BASE_P,ALT_P)
    return {
        "family":family,
        "optimal_primal":optimum["primal"],
        "optimal_dual":optimum["dual"],
        "fractional_objective":optimum["optimum"],
        "kl_evidence_floor":lower["expected_cost_lower"],
        "rotated_control":bool(rotated),
    }


def complete_singleton_floor():
    """Full finite perturbation universe includes all single-cell changes.

    If every single-cell change crosses the decision boundary, its
    fractional information cover has optimum n*d: each x_c>=1 is
    necessary, and x_c=1 for all cells covers every conceivable
    nonempty support mask. This is an exact constructive primal/dual
    certificate requiring no exponential solver.
    """
    singles=tuple(1<<i for i in range(N_STATES*N_ACTIONS))
    checked=decision_boundary_family(singles)
    if checked["nonboundary_masks"]:
        raise AssertionError("single-cell alternative does not change decision")
    n=N_STATES*N_ACTIONS
    return {
        "baseline_feasible":True,
        "all_singletons_cross_boundary":True,
        "unrestricted_family_fractional_objective":Q(n),
        "uniform_primal":(Q(1),)*n,
        "singleton_dual":(Q(1),)*n,
        "finite_perturbation_worlds":(1<<n),
        "opposite_label_masks":tuple(mask for mask in range(1,1<<n)
             if exact_quotient_radius(rate_table_from_mask(mask),
                                      CLASS_BUDGET)>TV_TOLERANCE),
    }

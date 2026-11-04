"""QI-03: exact fractional information-cover certificates for quotient tests.

A baseline Bernoulli world and m alternatives have cellwise KL costs.
When each alternative changes a subset of n cells by the SAME per-cell
KL divergence kappa, any delta-correct adaptive decision process obeys

    E_0[total cost] >= kl(1-delta, delta)/kappa * fractional_hit_cost.

The fractional-hit optimum is an elementary LP. This module enumerates
tiny rational primal/dual vertices independently; it does NOT claim to
provide a scalable LP solver or the statistical consistency of a learner.

Prior art: change-of-measure/transportation lemmas for bandit
identification (Kaufmann-Cappe-Garivier 2016; Lattimore-Szepesvari 2020).
"""

from fractions import Fraction as Q
from itertools import combinations, product
from math import ceil, log


def _validate(n_cells, alternative_masks, cell_costs=None):
    if type(n_cells) is not int or not 1 <= n_cells <= 6:
        raise ValueError("finite rational oracle supports 1..6 cells")
    masks = tuple(alternative_masks)
    if len(masks) > 10 or any(
            type(mask) is not int or mask < 0 or mask >= (1 << n_cells)
            for mask in masks):
        raise ValueError("invalid alternative masks (limit 10)")
    if cell_costs is None:
        costs = (Q(1),) * n_cells
    else:
        costs = tuple(Q(w) for w in cell_costs)
        if len(costs) != n_cells or any(w <= 0 for w in costs):
            raise ValueError("one strictly positive cost per cell")
    return masks, costs


def _solve_square(matrix, targets):
    """Independent rational Gauss-Jordan solver; singular system -> None."""
    n = len(matrix)
    if len(targets) != n or any(len(row) != n for row in matrix):
        raise ValueError("square linear system required")
    aug = [[Q(v) for v in row] + [Q(targets[i])]
           for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col]), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        divisor = aug[col][col]
        aug[col] = [v/divisor for v in aug[col]]
        for row in range(n):
            if row == col:
                continue
            coefficient = aug[row][col]
            if coefficient:
                aug[row] = [u-coefficient*v
                            for u,v in zip(aug[row],aug[col])]
    return tuple(aug[i][-1] for i in range(n))


def _vertices(dimension, inequalities):
    """Enumerate intersection vertices of Ax >= b, exactly.

    A feasible bounded polytope has at least one vertex. All target
    programs here have bounded optimal faces, and use <=6 variables
    for the primal and <=10 for the dual.
    """
    for chosen in combinations(inequalities, dimension):
        vector = _solve_square(
            [coefficients for coefficients, rhs in chosen],
            [rhs for coefficients, rhs in chosen])
        if vector is None:
            continue
        if all(sum((a*x for a,x in zip(coefficients,vector)),Q(0)) >= rhs
               for coefficients,rhs in inequalities):
            yield vector


def _primal(n_cells, masks, costs):
    """min sum c_i x_i, A x >= 1, 0 <= x_i <= 1."""
    constraints = []
    for i in range(n_cells):
        unit = tuple(Q(int(j == i)) for j in range(n_cells))
        constraints.append((unit,Q(0)))
        constraints.append((tuple(-z for z in unit),Q(-1)))
    for mask in masks:
        constraints.append((
            tuple(Q(int(bool(mask & (1 << i)))) for i in range(n_cells)),
            Q(1)))
    best = None
    for vector in _vertices(n_cells, constraints):
        value = sum((c*x for c,x in zip(costs,vector)),Q(0))
        key = (value,vector)
        if best is None or key < best:
            best = key
    return best


def _dual(n_cells, masks, costs):
    """max sum y_j, A^T y <= cost, y_j >= 0."""
    count = len(masks)
    if count == 0:
        return Q(0), ()
    constraints = []
    for j in range(count):
        constraints.append((
            tuple(Q(int(i == j)) for i in range(count)),Q(0)))
    for cell in range(n_cells):
        constraints.append((
            tuple(-Q(int(bool(mask & (1 << cell)))) for mask in masks),
            -costs[cell]))
    best = None
    for vector in _vertices(count, constraints):
        value = sum(vector,Q(0))
        key = (-value,vector)
        if best is None or key < best:
            best = key
    return None if best is None else (-best[0],best[1])


def fractional_information_cover(n_cells, alternative_masks, cell_costs=None):
    """Exact primal/dual witness for tiny binary-incidence information design.

    A zero mask makes an alternative indistinguishable by any permitted
    cell, hence the finite-design problem has no feasible solution.
    Return None for this genuine unidentifiability case.
    """
    masks, costs = _validate(n_cells, alternative_masks, cell_costs)
    if any(mask == 0 for mask in masks):
        return None
    if not masks:
        return {
            "optimum": Q(0),
            "primal": (Q(0),)*n_cells,
            "dual": (),
            "cell_costs": costs,
            "alternative_masks": masks,
        }
    primal = _primal(n_cells,masks,costs)
    dual = _dual(n_cells,masks,costs)
    if primal is None or dual is None:
        raise AssertionError("feasible bounded LP lost a vertex")
    objective, x = primal
    dual_value, y = dual
    # The equality of TWO independently enumerated optima is also
    # a checkable primal/dual certificate of global optimality.
    if objective != dual_value:
        raise AssertionError("fractional cover primal/dual gap")
    if any(sum((x[i] for i in range(n_cells) if mask & (1 << i)),Q(0))
           < 1 for mask in masks):
        raise AssertionError("invalid primal cover")
    if any(sum((y[j] for j,mask in enumerate(masks)
                if mask & (1 << i)),Q(0)) > costs[i]
           for i in range(n_cells)):
        raise AssertionError("invalid dual information packing")
    return {
        "optimum": objective,
        "primal": x,
        "dual": y,
        "cell_costs": costs,
        "alternative_masks": masks,
    }


def integral_hitting_cover(n_cells, alternative_masks, cell_costs=None):
    """Independent brute-force integer oracle for small cell universes."""
    masks,costs = _validate(n_cells,alternative_masks,cell_costs)
    if any(mask == 0 for mask in masks):
        return None
    best = None
    for size in range(n_cells+1):
        for selected in combinations(range(n_cells),size):
            if all(any(mask & (1 << cell) for cell in selected)
                   for mask in masks):
                score = sum((costs[i] for i in selected),Q(0))
                candidate = score,selected
                if best is None or candidate < best:
                    best = candidate
    return best


def independent_half_grid_oracle(n_cells, masks, costs=None):
    """Brute rational grid {0,1/2,1}; only a diagnostic for <=3 cells."""
    masks,costs = _validate(n_cells,masks,costs)
    if n_cells > 3:
        raise ValueError("half-grid diagnostic limited to 3 cells")
    best = None
    for x in product((Q(0),Q(1,2),Q(1)),repeat=n_cells):
        if all(sum((x[i] for i in range(n_cells) if mask & (1 << i)),Q(0))
               >= 1 for mask in masks):
            objective = sum((costs[i]*x[i] for i in range(n_cells)),Q(0))
            if best is None or (objective,x) < best:
                best = objective,x
    return best


def bernoulli_kl(p,q):
    """Standard KL in nats, float only in the final physical scale."""
    p,q = float(p),float(q)
    if not (0 <= p <= 1 and 0 <= q <= 1):
        raise ValueError("Bernoulli probabilities must lie in [0,1]")
    if p == q:
        return 0.
    if (q==0 and p>0) or (q==1 and p<1):
        return float("inf")
    return ((p*log(p/q) if p else 0.)
            + ((1-p)*log((1-p)/(1-q)) if p<1 else 0.))


def information_cost_lower_bound(
        n_cells, alternative_masks, delta, base_probability=Q(1,2),
        alternative_probability=Q(5,8), cell_costs=None):
    """Expected cost floor from the multi-alt KL inequality.

    Each alternative changes precisely its masked cells from the SAME
    baseline Bernoulli rate to the SAME alternative rate.
    The LP factor is an exact rational certificate; the final nats
    factor is floating-point and reported as approximate.
    """
    d = float(delta)
    if not 0 < d < .5:
        raise ValueError("delta must be in (0,1/2)")
    kl = bernoulli_kl(base_probability,alternative_probability)
    if kl <= 0 or kl == float("inf"):
        raise ValueError("distinct interior Bernoulli rates required")
    result = fractional_information_cover(n_cells,alternative_masks,cell_costs)
    if result is None:
        return None
    beta = bernoulli_kl(1-d,d)
    return {
        "fractional_cover": result,
        "beta_nats": beta,
        "kl_per_changed_cell": kl,
        "expected_cost_lower": float(result["optimum"])*beta/kl,
        "integer_hard_budget_floor": ceil(
            float(result["optimum"])*beta/kl-1e-12),
        "status": "necessary bound only; not an achievable policy",
    }

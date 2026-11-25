# PDI-03: risk-constrained proof discovery and versioned eligibility

**Evidence:** exact finite synthetic oracle and paper derivation; no empirical or Lean claim. PDI-02 defines the conditional independent noisy channels, fixed certificate families, perfect knowledge of the prior and witness-backed authorization rule. All budgets are pathwise audit-cost budgets. The risk limit below is on expected false-authorized weight, not a pathwise or high-probability guarantee.

## Deterministic frontier

Represent a policy by (f,t), its expected false and true authorized claim weight. A point dominates another if its false weight is no larger and its true weight no smaller, with at least one strict inequality. At a leaf, each eligible claim contributes either (0,0) or its unnormalized (bad,good) posterior mass times claim weight. Take the Minkowski sum over claims, pruning dominated points. At an audit node, take the Minkowski sum of the two child frontiers (unnormalized posterior masses already include transcript probabilities). Union all affordable first-action alternatives and the stop frontier, then prune. The recursion terminates as channels are consumed. Induction on remaining channels proves equality with the nondominated attainable deterministic values: every policy stops or selects an affordable first action and specifies a policy independently for each outcome. Addition and union preserve the sufficiency of Pareto pruning. Terminal choices include any subset of eligible claims, not just the positive-utility choices of PDI-02. Fixed baselines enumerate affordable audit subsets and condition terminal decisions on their observations.

## Randomized frontier

Independent precommitment to a deterministic policy realizes any finite convex combination of its values. Conversely fixing all random coins of any randomized policy gives a deterministic tree; hence its expected value lies in the convex hull. Maximizing t subject to f<=epsilon is a finite linear program over mixing weights. An optimum has support at most two: an extreme point of the feasible simplex sliced by one halfspace is a vertex or an intersection of an edge with the risk hyperplane. Enumerating feasible vertices and pairwise intersections suffices, and Pareto pruning cannot hurt. The implementation returns endpoint values and weights, not executable policy witnesses. The scalar objective max(t-lambda*f) for lambda>=0 recovers PDI-02's optimal utility.

The three independent fair bits and 90% sensitivity/10% false-positive channels from PDI-02 yield fixed points (0,0), (1/40,9/40), (1/20,9/20). The adaptive frontier additionally contains (3/25,63/100). At epsilon=3/40 the best deterministic value is 9/20; the randomized value is 18/35, a relative gain of 1/7. Choose the (1/20,9/20) policy with probability 9/14 and the (3/25,63/100) policy with probability 5/14. This mixture is admissible under the expected risk limit only; it may realize large false weight in individual runs. At epsilon=1/20 the adaptive and fixed frontiers have the same optimum.

## Revocation and selection leakage

An immutable audit event records obligation identity, evidence version and outcome. Current eligibility uses only observations matching the active version for each obligation: at least one positive and no negative. Old events remain for provenance and cannot authorize a new version. This is only an eligibility projection, not a posterior state or a dynamic optimizer. A source revocation may also invalidate information used to choose subsequent audits.

Exact counterexample: a fair hidden bit X is reported by a source. On X=0 choose probe left, on X=1 choose probe right; both probes always return 1. After deleting the source's output, the retained action and result imply posterior P(X=1) equal to 0 or 1. Projecting out the action identity too leaves P(X=1)=1/2. The latter projection describes a different observer, not an erasure from an actor's memory. If the source's reliability is disputed, recomputing the posterior requires a revised joint model for the source and the selection policy. A source-version ledger and a posterior alone do not establish revocation sufficiency. We do not solve dynamic noisy audit revocation here.

## Reproduction and next gates

    PYTHONPATH=src pytest -q tests/test_evaluation_pdi_frontier.py
    PYTHONPATH=src python scripts/verify_evaluation_pdi_frontier.py
    python scripts/check_receipts.py --only pdi_frontier

The independent oracle pre-samples all potential outcomes, executes all affordable policy trees, enumerates terminal authorization subsets and uses pairwise dominance. It compares 64 frontiers on 32 seeded correlated instances and checks 256 scalar support values against PDI-02. The strict mixture and version counterexamples are explicit. PDI-04: robust priors and unknown reliability, enforceable conditional risk budgets and a versioned actor-filtration game. Export actual policy witnesses and formalize the Pareto recurrence before deployment. Model-level reward hacking and transfer experiments remain separate gates.

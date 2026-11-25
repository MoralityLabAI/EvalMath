# PDI-02: noisy proof audits and dependency amplification

**Evidence:** algebraic paper bound and exact finite verification. No empirical model runs or calibration of published papers. PDI-01 defines the finite certificate hypergraph.

## Pathwise amplification

Let each authorized claim j have an accepted certificate (a conjunction of accepted obligations), with nonnegative weight w_j. A false claim means all of its available certificates are invalid in the latent world, not that the underlying mathematical theorem is false. Define D_i as the sum of w_j over claims whose eligible certificate family contains obligation i at least once. Let X_i indicate that i is accepted and invalid; obligation weights v_i are positive. Let F be the sum of weights of falsely authorized claims. Every falsely authorized claim has an accepted witness certificate containing an invalid accepted obligation. Charge its weight to one such obligation. Therefore pathwise F <= sum_i D_i X_i <= C sum_i v_i X_i, where C=max_i D_i/v_i. Expectations preserve the inequalities under any joint distribution, policy or noise, provided the witness rule and the declared dependency graph hold. The ratio is meaningful only when the denominator is positive. C is sharp over the class: eight claims of unit weight with the same single-obligation certificate give F=8 and false obligation weight=1 when that gate is falsely accepted. This need not be tight for every fixed graph. A claim can count at most once in D_i; double-counting alternatives is unnecessary. If an agent chooses the graph adaptively, the same bound holds pathwise with its realized C; a uniform expectation bound requires an enforced cap on C, rather than multiplying two expectations.

## Noisy audit policies

For a fixed rational prior over worlds, each one-use channel has an obligation index, sensitivity, false-positive probability and positive integer cost. Distinct channels, including repeats of the same obligation, have independent potential outcomes conditional on the world. These parameters are known to the evaluator. No new worlds, repairs, hidden feedback, or revocations occur during an audit. A bit is accepted exactly when at least one observed audit is positive and none is negative. Authorize only claims with an accepted witness and strictly positive conditional expected utility (true certificate availability earns w, false availability costs lambda*w). This policy treats alternate certificates as available even if unobserved; a separate metric of selected-witness validity would be stricter. Terminal Bayes decisions are separable by claim. At ties reject. Policy ties prefer lower expected false weight then higher true weight.

The Bellman state stores unnormalized posterior masses, positive and negative masks, unused channels and remaining budget. Each audit splits mass by its likelihood; the objective adds child utilities (no extra probability weighting). Induct on the remaining channels to prove optimality, including stopping and the terminal decisions. The exact oracle samples every potential channel outcome before executing every affordable deterministic tree and sums utility by reached transcript. Fixed baseline enumerates affordable subsets and may condition authorization on their observations. Both optimize the same utility; this is not a guarantee that adaptive auditing lowers false authorization.

Strict example: independent fair A,B,C, claims A AND B (weight 2) and C (weight 1), unit costs, budget 2, sensitivity 9/10, false-positive rate 1/10, lambda=1. Fixed optimum: utility 2/5, true weight 9/20, false weight 1/20. Adaptive optimum: utility 51/100, true weight 63/100, false weight 3/25. Utility rises 27.5% while false weight rises 140%. A risk-constrained objective, not merely utility maximization, is the next gate. This is an exact finite counterexample to monotonic safety under adaptation, not a model-level conclusion.

## Candidate selection

For m independent invalid candidates, each accepted with probability f, an agent who can inspect every binary audit result and select a passing candidate has success probability 1-(1-f)^m (zero when m=0). At f=1/20, two candidates give 39/400. The independence, access and budget assumptions are essential. For correlated outcomes the union bound min(1,m*f) applies if each marginal is bounded by f. Adaptive proposals require a conditional bound in the full actor filtration. PDI-02 does not solve strategic graph selection or unknown channel reliability; the pathwise incidence cap supplies a constraint for that future game.

## Reproduce

    PYTHONPATH=src pytest -q tests/test_evaluation_pdi_noisy.py
    PYTHONPATH=src python scripts/verify_evaluation_pdi_noisy.py
    python scripts/check_receipts.py --only pdi_noisy

The receipt checks 4096 world/acceptance pairs across 64 seeded graphs, 48 noisy instances against exhaustive policy trees, and the explicit witnesses. PDI-03: exact risk-budget frontier, actor-filtered selection, dependency-version ledger and revocation-sufficient state. General Lean formalization remains open.

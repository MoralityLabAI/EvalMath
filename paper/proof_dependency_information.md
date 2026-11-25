# PDI-01: proof dependency information and adaptive certification

**Scope:** exact finite synthetic model, inspired by mathematical discovery via reusable constructions. No claim about the correctness or independence of any particular published proof. The local-smoothing and ETH manuscripts are motivating cases; EvalMath's existing ETH fidelity audit is separate. Lean targets require kernel verification before a formal evidence label.

## Model

A world assigns validity bits to a finite list of proof obligations. The prior is any exact rational distribution over worlds. Each claim has a nonnegative weight and a nonempty family of certificates, each a conjunction of obligations. A claim has at least one valid certificate in a world if any conjunction holds. Obligations may be shared. A certificate can be empty (already established). This is a flattened dependency hypergraph; cycles or arbitrary proof semantics are outside this model. The underlying truth of a theorem is distinct from the validity of its supplied certificates.

With one shared gate failing with probability q and k branch gates independently failing with probability r conditional on the shared gate succeeding, the probability of no valid certificate is q+(1-q)r^k. With independent replicas of the whole mechanism it is (q+(1-q)r)^k. The shared risk is at least q. For k=2 the difference is exactly q(1-q)(1-r)^2; for general k>=1 the inequality follows from convexity of x^k on [0,1] with mixture of 1 and r. The hypotheses are declared model assumptions, not empirical estimates.

If only marginal failure probabilities p_i are known, the sharp intersection bounds are max(0,sum p_i-k+1) and min p_i. The lower bound follows by the union bound on complements; the upper bound by containment. On a uniform interval of length one, nested failure sets attain the upper bound. Arrange complementary sets of lengths 1-p_i consecutively around a unit circle; their union has length min(1,sum(1-p_i)), attaining the lower bound. Rational interval endpoints give a finite rational construction. The receipt checks two-event endpoint couplings; general sharpness is a paper argument.

## Perfect audits and budgeted policies

Auditing bit i costs a positive integer and reveals it perfectly, with no change to the world. At a leaf of an audit policy, award a claim's weight only if it has a valid certificate in every positive-mass world consistent with the transcript. This is prior-relative certainty, not proof by kernel; worlds assigned zero prior are excluded. A claim may be certain even when no single certificate is certain. No unobserved side channel or revocation is allowed in this first experiment.

For surviving support S, remaining audit set A and budget b, define T(S)=mass(S) times the total certainly certified weight. Then the unnormalized optimal value is

    V(S,A,b) = max(T(S), max_i [V(S_i0,A-i,b-c_i)+V(S_i1,A-i,b-c_i)]),

where the second maximum uses affordable i in A. Empty support contributes zero. This follows by induction on the number of remaining actions: any deterministic policy stops or chooses an affordable first audit, then independently optimizes each child. Randomizing is a mixture of deterministic policy values and cannot improve the maximum. Fixed policies enumerate affordable audit subsets and partition support by their observed bits. Adaptive policies include all fixed policies.

Strict example: three independent fair validity bits A,B,C; claim A AND B has weight 2, claim C has weight 1. Budget 2, unit costs. Best fixed value is 1/2. Audit A first, audit B if A succeeds and C otherwise: expected value 3/4, a 50% improvement. Three audits yield expected weight 1. These are synthetic exact values.

## Reproduce

    PYTHONPATH=src pytest -q tests/test_evaluation_pdi.py
    PYTHONPATH=src python scripts/verify_evaluation_pdi.py
    python scripts/check_receipts.py --only pdi
    cd lean && lake env lean FeedbackChannel/ProofDependency.lean

The receipt compares memoized Bellman optimization to exhaustive policy-tree enumeration on 64 seeded correlated priors with varying weights, costs and budgets; it checks 64 shared-gate grid cases and the explicit strict witness. The Lean file targets the algebraic floor, two-certificate gap and two-event bounds; it does not formalize the Python implementation, the general Fréchet sharpness or Bellman optimality.

## Next gates

PDI-02: noisy verification, explicit false-authorization loss, prior misspecification and adaptive transcript leakage. PDI-03: source-version and revocation sufficiency, including audit-selection leakage; simply deleting old observations is insufficient when selection depended on them. PDI-04: register a sealed downstream proof-transfer benchmark in a separate gym; measure saved verifier work with equal budgets, construction held out by family, and independent proof-dependency auditing.

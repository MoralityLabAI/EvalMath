# CFH-01B: learned boundary search, public development results

**Status:** structural arithmetic ceiling reproduced; learned adaptive policy fails extrapolative promotion against sign-only bisection at 16+ queries. One public construction genealogy, no sealed family, no neural or causal claims. CPU only, no paid compute.

## Design

A witness is an integer b in [0,q^16] with negative discriminant. The evaluator asserts strict decreasing discriminant via its quadratic derivative, checks three sampled values against direct flag counts, and derives exact minimal b using the CFH-01 oracle. This is a logical query simulation against an exact precomputed polynomial, not a latency benchmark. All policies share endpoint queries (first q^16, then 0 for feasible cases); the cap sign alone establishes absence conditional on the certified monotonicity premise. Gap is (best feasible b - optimal b)/q^16 and is aggregated exactly with fractions before decimal display. The full-value interpolation policy can certify an optimum without querying the candidate itself; direct adjacent-query verification is separately tracked. Gamma positivity at the optimum is checked by the underlying boundary oracle.

Data: q-grouped splits within this one public genealogy, two polynomial variants, m=q^4 plus floor(q^4/k) for k=512,256,128,64,32,16 (and zero addition). Train 19 q values, 266 total cases, 214 with witnesses, fit only on witness cases. Initial parameter test: interpolation 6 q values, 84 cases (70 feasible), extrapolation q=101..257 prime powers, 36 q values, 504 cases (432 feasible). Added exploratory stress test after seeing initial results: q=263..509 prime powers, 45 q values, 630 cases (474 feasible). Total test 87 q groups, 1218 cases, 976 feasible. These are dependent variations; the number of independent conjecture families is one. No inference of generalization across mathematical constructions.

Fixed eight-coefficient ridge fit on normalized thresholds, feature vector defined in script, penalty 1e-5 and residual-width floor 1e-4. Static prior uses a fixed van der Corput quantile sequence; adaptive prior uses the conditional median of the same fitted distribution after each sign update. Prior mixture has 10% uniform support. Uniform baseline uses fixed reproducible seed per case. Bisection uses only signs. Two post hoc controls, evaluated also on extra development q, use first learned proposal followed by bisection, or enforce a central-half guard on subsequent learned proposals. Full-value quadratic solver uses exact integer/rational values, a stronger observation interface than sign-only arms; it reconstructs coefficients from three points, verifies derivative sign and internally computes the minimal integer root boundary. This is the structural ceiling, not a matched sign-only competitor. No timing equivalence, no trained neural network, and no empirical mechanistic causal inference.

## Results (mean normalized optimality gap, 16 query budget)

| Policy | Interpolation | Extrapolation | Extra development |
|---|---:|---:|---:|
| Full cap | 3.3121e-2 | 2.7954e-2 | 2.1687e-2 |
| Uniform | 2.5831e-2 | 2.2533e-2 | 1.8515e-2 |
| Bisection | 3.4836e-5 | 2.9781e-5 | 3.0902e-5 |
| Static prior | 9.7680e-6 | 4.1437e-4 | 2.5780e-3 |
| Adaptive prior | 3.0850e-8 | 2.9821e-4 | 2.4006e-3 |
| Warm-start bisection | 4.9884e-6 | 5.5057e-5 | 5.7362e-5 |
| Guarded adaptive | 4.0535e-6 | 5.7936e-5 | 5.7489e-5 |
| Exact quadratic | 0 | 0 | 0 |

At 8 queries adaptive prior gaps were 4.899e-6, 5.004e-4, 2.687e-3; bisection 1.035e-2, 7.049e-3, 8.765e-3. At 32 queries adaptive prior gaps were 5.527e-13, 6.072e-8, 1.133e-7; bisection 4.931e-10, 4.968e-10, 4.827e-10. The initial fit's effective residual width hits the floor. Narrow priors hurt under parameter shift; the added guard greatly reduces the failure but still trails bisection in extrapolation at 16 queries. Reject general adaptive advantage and further neural spending on this single family. 

Exact full-value solver: 976/976 feasible cases have optimum after 3 queries; 976/976 have directly queried adjacent boundary after 5 queries. All 242 infeasible cases identified by cap sign (given certified monotonicity). Exact polynomial interpolation is a strong baseline whenever the observation model and quadratic structure are available. Next research should target independently held-out construction families where polynomial degree or invariant transformation is unknown, and report retrieval, derivation and verification separately. Register the next family before inspecting solutions. A causal mechanism test will require root-level pilot/sham preflight before allocation. Here only finite arithmetic and descriptive policy performance are asserted.

## Replay and provenance

Python 3.13.5, NumPy 2.3.5, OPENBLAS_NUM_THREADS=1. From gyms/CFH01:

    OPENBLAS_NUM_THREADS=1 python search_pilot.py > search_receipt.json

Final receipt contains 58,464 policy/budget records, exact fractional gap and width strings, train/test q lists, weights and summary. No generated run committed; regenerate locally. Float regression/quantile rounding can differ across numerical environments, whereas exact oracle checks and quadratic results are integer/rational. SHA-256 of this run's search_receipt.json: 19c2264a0e91aa4fa00966e33d7dbe8efafc1b7b158a9d8304039b0418336202. Initial six-policy receipt before the exploratory additions: 59598237f607172df25a89a67b54c2d9f2dd7b58643c1b0072c2231ffe54ba18. Code SHA-256: 6c05d53041ebdbd67115787f1e57713fbecf31aa136c0d9d840b8575347c510f. Oracle SHA-256: 0af3d9fb6990cbeca670706e3d944465e3330a1ed10fde40441b71f5e2b06dc2. Both code blobs verified against the branch; full repository CI and Lean rebuild outstanding.

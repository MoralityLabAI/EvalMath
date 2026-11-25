# NFAS-05: Independent-value stopping games and imperfect audits

Exploratory follow-up, 2026-11-25. Extends NFAS-04's correlated three-candidate counterexample. **All 284 finite instances have equal public- and private-seed scalar optima.** This does not establish a general theorem.

## Game and assumptions

Three independently drawn candidates, mandatory selection of one, full observation history, scheduler knows the whole candidate world and chooses a permutation before any arrival. In the private-seed game the scheduler knows the policy, not its realized random draw. In the public-seed game the scheduler also knows the realized seed. Complete first/second stopping realizations x,z are constrained by x>=0, z>=0, x+z<=1; final selection is mandatory. For each world and order the expected reward is x*g_first+z*g_second+(1-x-z)*g_last. Maximize the world-mass-weighted sum of lower bounds on all six order payoffs. The resulting LP represents every private randomized policy; the deterministic subset has binary stopping realizations. A public random seed cannot beat its best deterministic realization.

Two observable-value families use independent two- or three-point nonnegative integer values, known distributions, and full value observations on arrival. Integer probability weights are normalized separately per candidate. The third family has independent failure bits X_i, independently flipped observations Y_i, fixed valid-candidate values v_i and imperfect failure detection with sensitivity s/4, specificity one. If auditing i, valid utility is v_i(1-X_i) and expected residual failures are sum(X) - (s/4)X_i. The scalar objective U - lambda R can be optimized through the nonnegative effective payoff g_i=4v_i(1-X_i)+lambda*s*X_i; subtract the common offset 4lambda E(sum X) and divide by four to recover the scalar objective. The scheduler knows X,Y but not independent audit noise. The reported ratio to the offline maximum uses g, NOT the offset-adjusted U-lambda R. No interpretation as a competitive ratio for arbitrary imperfect verification.

## Results and verification

| Family | Instances | Exact deterministic optimum matches private optimum | Minimum effective payoff/offline |
|---|---:|---:|---:|
| Observable binary | 124 | 124 | 113/154 |
| Observable ternary | 60 | 60 | 1690/2137 |
| Hidden imperfect audit | 100 | 100 | 74/109 |

The deterministic lower witness is evaluated exactly by direct enumeration over all worlds and permutations. SciPy HiGHS supplies candidate dual support; exact rational Gaussian elimination reconstructs dual multipliers, then checks nonnegativity, every dual inequality and equality with the directly evaluated deterministic witness. Mixed-integer discovery is used only when a rounded LP solution does not yield the matching lower bound (15 binary, 9 ternary, zero imperfect cases locally). Numerical solver status never suffices. The receipt records a digest of the full generated instance/optimum list per family; witness discovery and exact validation are replayed rather than storing individual witnesses.

Seeded exploratory design: binary 4 explicit controls plus 120 seed-33 product distributions, ternary 60 seed-601 product distributions, hidden 100 seed-76 product distributions. Supports, weights, noise, sensitivity and price are in code. These are exploratory, not preregistered or sealed. No empirical agent experiment or general prophet guarantee. The visible-payoff model and hidden-payoff model both differ from NFAS-04's correlated one-good-identity construction. The result motivates a restricted no-randomization conjecture for independent three-candidate scalar games, not a proof; a counterexample could occur outside this grid.

## Reproduce

Python 3.12/3.13 with NumPy and SciPy 1.17.0. Run `OPENBLAS_NUM_THREADS=1 python scripts/verify_nfas05.py --output /tmp/nfas05.json` and compare to `output/nfas05.json`. The optional exploratory solver is isolated from the standard NFAS-01–04 Node receipts. Exact checks fail closed if numerical support cannot be reconstructed.

## Next gate

Separate three potential explanations: product distribution, fully informed scheduler, and scalar objective. Sweep correlated-to-product interpolations with fixed marginals; search for exact fractional gaps and characterize the associated dual constraints. Then investigate larger n and alternative finite support sizes. Do not claim the upstream matroid prophet theorem follows.

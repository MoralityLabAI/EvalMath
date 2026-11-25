# NFAS-06: Private randomness at the independent endpoint

Research draft, 2026-11-25. Exact finite counterexample and affine interpolation theorem. This revises the prospective independence conjecture in NFAS-05, not the results on its 284 instances.

## Construction

Use NFAS-04's clean three equally probable worlds, with signals Y=(0,0,0), (0,1,1), (1,1,0) and respective good identities C, A, B. Let G_i indicate a good audit payoff. Each candidate has three equally probable local types (Y_i,G_i). For A and C they are (0,0),(0,1),(1,0); for B they are (0,0),(1,0),(1,1). Flip B's observable bit to make the local types identical across all candidates. Let Q be this correlated three-world law and P the product of its three local marginals. P has 27 equiprobable worlds, including all three Q worlds. Let P_alpha=(1-alpha)P+alpha Q, 0<=alpha<=1. Every candidate marginal is unchanged. All candidate types are independent and identically distributed (after signal relabeling) at alpha=0. Under P the number of good candidates can be zero, one, two or three. This is a hidden payoff problem, not a fully observable prophet problem.

A scheduler knows the whole realized type vector and chooses one permutation before arrivals. The auditor observes only candidate identities and their signals, has mandatory one-audit quota and complete history. Payoff is the selected G_i. Private seed means scheduler commits without knowing the realized seed. Public seed means it sees the realized seed before committing. This is expected scalar payoff, with no audit feedback before selection and no further scheduling intervention. Since the scheduler can choose an order separately in each world, the payoff of a fixed policy is affine in the world law.

## Theorem: exact full interpolation

For all alpha in [0,1],
    
    V_private(alpha) = (1-alpha)*10/27 + alpha/2
                     = (20+7*alpha)/54,
    V_public(alpha) = 1/3,
    gap(alpha) = (2+7*alpha)/54.

In particular private randomization strictly improves the minimax value at the fully independent endpoint, by 1/27 (11.11% relative). There is no positive dependence threshold in this family. The three-candidate counterexample therefore does not require cross-candidate dependence, though it does require hidden payoffs in this construction.

Proof: The exact stopping-realization LP of NFAS-04 has 30 policy variables and 27 nonnegative per-world worst-payoff variables. The verifier checks a common feasible half-integral realization table, giving total worst payoff 10 over the 27 product worlds and 3/2 over the three correlated worlds. For each endpoint, a nonnegative rational dual vector with exact equal objective is explicitly supplied and checked against every column of the LP. Thus each endpoint value is optimal. For the public-seed game the oracle enumerates all 64 first-decision masks. Under a fixed mask, each world's guaranteed success is either impossible or a conjunction of requirements on second-decision bits: if stopping first is bad or both remaining candidates are bad, success is impossible; if exactly one of the remaining candidates is good, the second decision must select that identity. The exact recursion branches on conflicting requirements and prunes only when the remaining number of compatible worlds cannot exceed the incumbent. If no conflicts remain, all remaining conjunctions can be simultaneously satisfied. It certifies deterministic endpoint optima of 9/27 and 1/3. Auditing fixed identity A achieves both. Public mixing cannot improve the best deterministic policy because the scheduler sees the seed. For either visibility model, the maximum of the affine combination of two policy payoffs is bounded above by the affine combination of their individual maxima, and the common maximizing policy attains that upper bound. This establishes the formula over the entire interval, not merely on the 21-point verification grid.

## Dependence measure and interpretation

The total correlation (nats) is D(P_alpha || P), since the marginals are fixed. For the 3 special worlds the mass is (1+8alpha)/27; for the other 24 it is (1-alpha)/27. Therefore

    TC(alpha) = ((1+8alpha)/9)*ln(1+8alpha)
                + (8*(1-alpha)/9)*ln(1-alpha),

with the continuous endpoint convention 0 ln 0 = 0. TC(0)=0. The exact seed-value gap is already positive there. A cross-candidate total-correlation budget alone cannot certify that private randomness is unnecessary. Hidden payoff ambiguity and the scheduler's access to it must also be declared. This example cannot be transferred directly to the OpenAI one-sample theorem: the scheduler observes hidden payoff values while the auditor sees only signals, whereas the prophet's selection algorithm sees arriving values. NFAS-05's visible-value no-gap census is unaffected, and its hidden-audit family used a different local support/noise law. No claim of general absence or presence of a gap in fully observed independent prophet games.

For a perturbation of the full world law by total variation delta with the same observation and scheduler model, each policy payoff changes by at most delta since payoffs lie in [0,1]. Thus the private/public optimality gap decreases by at most 2 delta; the product gap is guaranteed positive for delta < 1/54. This is a paper argument; no continuous optimization or real model runs are involved.

## Reproduction and evidence

Run node scripts/verify_nfas06.mjs --check. It uses integer arithmetic throughout, checks dual feasibility and exact endpoint objectives, independently evaluates the realization policies, exhaustively certifies deterministic optima, checks fixed marginals at 21 grid points, and commits a source-linked receipt. The LP witness was discovered numerically and checked exactly. The affine theorem uses the endpoint certificates; a Lean formalization of the game/certificates is outstanding.

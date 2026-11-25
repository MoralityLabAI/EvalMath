# CCF-01C: Minimax receipt encoding under coupling uncertainty

Status: handwritten mathematical argument and exact synthetic finite witnesses; three targeted local tests passed. No empirical model claims, Lean kernel check or upstream proof audit. Extends CCF-01B.

## 1. N-candidate risk and the robust compiler

Fix finite feasible contexts, authorization bits, deterministic encoding e, and complete decoder U from CCF-01. Under a finite normalized law mu on ordered N-tuples of feasible (context,state) candidates, let F_j be the event that U falsely authorizes candidate j. Let T_e be the deterministic selector transcript; it can depend on e. Exactly one candidate must be selected. The optimal selector risk is

    R_mu(e,T_e) = sum_t max_{1<=j<=N} mu(T_e=t, F_j).

Proof: maximize independently in each transcript cell. This is the CCF-01B argument with N choices. For fixed e and T_e, this risk is a maximum of finitely many linear functionals of the normalized law, hence convex. For a convex hull of finitely many declared laws mu_i,

    sup_{mu in conv(mu_i)} R_mu(e,T_e) = max_i R_mu_i(e,T_e).

The inequality follows by convexity and equality by inclusion of each original law. The same applies to a finite-dimensional compact polytope using its vertices. This is worst-case selector risk (sup over joint law and selector), not a guarantee under a Bayesian prior on scenarios or a game with an encoder secretly randomized. The compiler enumerates restricted-growth encodings with at most k labels and minimizes this maximum. Label values are arbitrary identifiers. For the visibility vocabulary none, contexts, context+receipt, full world, transcript refinement gives monotone risk for each fixed encoding. Minimizing exposure alone would trivially choose the coarsest allowed transcript, so auditor disclosure obligations must be specified independently. This version treats the four modes as declared constraints rather than assigning a monetary value to disclosure. A private verification channel and the actor-visible channel must be modeled separately.

## 2. A compromise optimal in neither scenario

Use the triangle contexts from CCF-01B, with weights on (0,0),(1,1),(2,0),(0,1),(1,2),(2,2) equal to 2,2,3,4,4,5. Total is 20. Begin with the diagonal coupling with these masses. Scenario A exchanges two units from each diagonal for a=(1,1) and b=(0,1) into the two off-diagonal ordered pairs (a,b),(b,a). Scenario B performs the same exchange with a=(0,0), b=(1,2). Both have identical single-candidate marginals. Under context+receipt visibility, exact risks are:

| Code | A | B | Worst |
|---|---:|---:|---:|
| 000 | 9/20 | 9/20 | 9/20 |
| 001 | 1/10 | 1/5 | 1/5 |
| 010 | 3/20 | 3/20 | 3/20 |
| 011 | 1/5 | 1/10 | 1/5 |

All possible partitions with at most two labels are listed. The unique robust optimum 010 is individually suboptimal in both scenarios. The guarantee extends to every convex mixture of these two laws by section 1. It reduces worst-case risk by one quarter relative to either scenario-specialized optimum. This is a restricted ambiguity family; it is not a claim about all possible couplings.

## 3. Unrestricted coupling boundary

Suppose every candidate has identical record marginal nu and the selector sees the full world. For a fixed code let the marginal error mass be p. Under the ambiguity set of ALL joint laws with these marginals,

    sup_mu R_mu(e, world) = min(1,N p).

Proof: the union bound gives the upper bound. On a uniform circle, choose N equally spaced translates of an arc of length p, taking flag j as the indicator that the point lands in translate j. Every flag has probability p; the union has measure min(1,N p). Conditional on the flag, draw record j from nu restricted to its error class or its complement. This extends the flag construction to the specified record marginals. At p=0 or p=1 the constant flag suffices. With rational masses the circle has a finite exact grid realization and conditional sampling uses rational weights.

Thus an encoding that minimizes passive error also minimizes worst-case full-world risk under unrestricted identical-marginal coupling uncertainty (additional encoders may tie after saturation). The previous optimizer reversal depends on restrictions on the ambiguity set or transcript; it cannot be generalized to this full-world setting. With only receipt visibility the same expression is an upper bound; attainability requires a separate argument.

## 4. Exact finite receipt

The independent oracle enumerates every deterministic policy on each finite transcript support, and enumerates labeled assignments instead of set partitions for minimax values. On 96 seeded synthetic instances, N=1..4, two scenario laws and four disclosure modes, there are 3072 selector-value comparisons and 384 minimax comparisons; all agree. Refinement monotonicity is checked on these cases. The compromise verifies both scenario marginals and convexity at eleven rational mixture weights. The sharp circle construction is checked on 720 (possibly repeated rational p) parameter instances with N=1..8 and denominator 1..12. These corroborate the algorithms and constructions; they do not estimate physical evaluation risk.

Reproduce:

    PYTHONPATH=src python -m pytest -q tests/test_evaluation_ccf_robust.py
    python scripts/verify_evaluation_ccf_robust.py
    python scripts/check_receipts.py --only ccf01c

Source hashes cover the module, tests and verifier. Full repository CI is pending; the existing Lean draft still needs explicit kernel inclusion and an axiom audit.

## 5. Next gates

CCF-01D: build and audit the existing exact-code iff, then formalize the cellwise maximum and union-bound boundary. CCF-02: independently pin and audit actual OpenAI local-smoothing comparator and theorem declarations, including strict range, loss and exception mutations. CCF-03: independently pin and audit FlashProve model/decoder/verifier boundaries. Freeze a multi-context receipt disclosure contract before any Control-Harness adoption; in particular test the assumption that feasibility facts are independently authenticated. No empirical failure frequency may be inferred from the synthetic table.

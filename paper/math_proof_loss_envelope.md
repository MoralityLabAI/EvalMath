# EM-MPT-07: Sharp fixed-product proof closure envelopes

2026-11-25. Extends MPT-01 from one extra attempt to every budget. Evidence: analytic argument and exact finite checks, not a claim of literature novelty or empirical calibration.

## Setup and theorem

Fix d>=1 sequential obligations, a fixed vector p in [0,1]^d, independent Bernoulli retries conditional on obligation, irreversible verified progress, unit attempt costs and integer budget B. Every success completes the current obligation. Let q=product p_i. For q>0 the equally weighted designated-witness negative log loss is L=-(1/d)log q. At B<d closure is zero. For B>=d, with k=B-d,

    1-(1-q)^(k+1) <= R(p,B) <= Pr[Binomial(B,q^(1/d)) >= d].

Both bounds are sharp for real probabilities. The lower extremizer is (q,1,...,1) and the upper extremizer is the uniform vector. If q=0 all vectors fail, if q=1 all vectors are all ones, and if B=d all feasible vectors have closure q. The empty proof is handled separately in the implementation. For 0<q<1, d>=2 and k>=1, each extremum is unique up to permutation: at most one p_i<1 for the minimum, all p_i equal for the maximum.

## Proof

For q>0 let G_i be the independent geometric waiting times supported on positive integers. The number of failures before finishing all obligations is F=sum_i(G_i-1). Its probability generating function as a formal power series in t is q times product_i (1-(1-p_i)t)^(-1). The CDF at k is its coefficient after multiplication by (1-t)^(-1). This follows by finite convolution at each coefficient, even when a p_i=1; no analytic convergence assumption is needed.

Replace a pair a,b by c,e with ab=ce. Write D_ab(t)=(1-(1-a)t)(1-(1-b)t), and let H(t) be the product of reciprocal factors for the other obligations. Expanding gives

    D_ce(t)-D_ab(t)=(c+e-a-b)t(1-t).

Thus for k>=1 the CDF change (new minus old) is

    q (a+b-c-e) [t^(k-1)] H(t)/(D_ab(t)D_ce(t)).

Every coefficient after the prefactor is nonnegative, since all failure rates are nonnegative. At k=0 the change is zero. If the pair sum strictly decreases or increases and q>0, at least one of the four failure rates is strictly positive, so every coefficient of this reciprocal product is positive. Hence at k>=1 the change is strict in the indicated direction.

Balancing an unequal pair to (sqrt(ab),sqrt(ab)) strictly decreases its sum. At fixed q>0 the feasible vectors lie in the compact set [q,1]^d with product q, and R is a finite polynomial (therefore continuous). A maximizer exists and cannot contain an unequal pair when k>=1; thus all p_i=q^(1/d). Its closure is the homogeneous binomial tail. For the minimum, if two entries a,b are strictly below one, replacing them with (ab,1) strictly increases the sum since (1-a)(1-b)>0, and decreases the closure. After finitely many such steps all but one probability are one; the remaining q-valued obligation has B-d+1 attempts. This proves the exact endpoints and equality cases. For q=0 an impossible obligation prevents completion; q=1 and B=d follow directly.

## Numerical witness and reproduction

With d=4, B=8, q=1/16, the two endpoint probabilities are 289201/1048576 (about 27.58%) and 163/256 (63.67%). The same designated-witness loss gives a gap of approximately 36.09 percentage points. Unlike a comparison between controllers, both endpoints use the same persistent retry controller and budget.

The generating-function implementation uses finite rational coefficients. The receipt checks 8,390 exact matches to the independent state-mass DP, 8,390 lower-bound/attainment comparisons, 2,294 upper-bound/attainment checks where the root is rational, 4,375 pair-exchange identities and four larger stress cases (d up to 16). The 23,453 counted checks overlap; they are not independent samples. The upper theorem for arbitrary real q follows from the argument above, not from a grid. The 0 and 1 boundaries have unit tests.

    PYTHONPATH=src python -m pytest -q tests/test_evaluation_math_loss_envelope.py
    python scripts/verify_math_loss_envelope.py
    python scripts/check_receipts.py --only math_loss_envelope

These are sharp loss-only envelopes for the narrow independent retry model. They do not apply directly to real LM perplexity, correlated or history-dependent attempt success, arbitrary proof graphs with optional subgoals, or uncharged inference. For general predictors the designated-witness probability need not even equal attempt success. No actual model capabilities are bounded by this theorem.

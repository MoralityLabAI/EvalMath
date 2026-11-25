# EM-MPT-02: Correlated failures and charged proof persistence

2026-11-25. Extension of [EM-MPT-01](math_proof_persistence.md). Evidence: algebraic identities under a declared synthetic mechanism, with finite exact verification. No model or Lean execution.

## Shared root difficulty

Fix d>=1 required proof obligations, integer budget B>=0 and a hidden root-specific success rate P in a declared finite support S within [0,1]. Conditional on P=p, all attempt outcomes are independent Bernoulli(p). Unconditionally, two hypothetical attempt outcomes X,Y have covariance Var(P), by conditional independence. The mean success probability is E[P]=mu. This is a model of common difficulty, not arbitrary correlated error or learning from failure. No controller observes P. Every success is valid; the graph and certificate validation are shared by the arms.

Persistent search with n usable attempts completes with f(d,n,p)=Pr[Binomial(n,p)>=d] conditional on P. Hence unconditional completion is E[f(d,n,P)]. The function is identically zero for n<d. For 1<=d<=n, differentiation and telescoping give f'(p)=n*C(n-1,d-1)*p^(d-1)*(1-p)^(n-d), and for n>1, 0<p<1 the sign of f'' is the sign of (d-1)-(n-1)p. Jensen gives the convex/concave effect for a distribution whose entire support stays within the corresponding region. Across the inflection point a general Jensen ordering is unavailable.

Example: P=1/2 always versus P uniformly in {1/4,3/4}. Both have mean 1/2, but the second has covariance 1/16 and correlation 1/4 for two attempts. With d=4, n=4, the respective closure rates are 1/16 and 41/256; with n=8 they are 163/256 and 35603/65536. The sign of the difference changes. Equal marginal success is not equal context-conditional cross entropy: -log(E[P]) differs from E[-log(P)]. No identification of real perplexity with either expression is assumed.

## Charged ledger versus optimal static quotas

In the persistent arm reserve a deterministic extra ledger charge C integer, 0<=C<=B, measured in base attempt units. Remaining attempt budget is B-C. This represents incremental orchestration and memory work; all ordinary proof generation, certificate validation and final assembly costs are assumed covered by the common base unit. The static baseline is deliberately granted zero incremental dynamic-ledger tax and enough local certificate storage for the fixed slots. In a real system measure both arms' costs. A fixed charge is a simplification; history-dependent overhead, storage bandwidth, parallel inference and context-dependent attempt costs remain open.

The static comparator assigns nonnegative integer quotas a_i with sum B before observing any outcomes or P. Its conditional closure probability is s(a,p)=product_i(1-(1-p)^a_i). Balanced quotas (d-r copies of floor(B/d) and r copies of ceil(B/d), r=B mod d) maximize this product for every p, and thus every mixture of P. Proof: write q=1-p. For b>=a+2 replace (a,b) by (a+1,b-1). The change in the two-factor product is (1-q)(q^a-q^(b-1))>=0, with q^0=1 at the endpoints. Other factors are nonnegative; repeated balancing terminates because the sum of squared quotas strictly decreases. B<d gives zero closure for every allocation. This comparator excludes adaptive symbolic search and grants no advantage over that larger class.

Define h_C(p)=f(d,B-C,p)-s(a_balanced,p). The exact worst-case advantage at known finite support S and mean mu is

    g(C) = min_{law(P): support(P) subset S, E[P]=mu} E[h_C(P)].

Claim (algebraic identity): g(C) is the minimum of h_C(mu) if mu is in S, and all values

    ((hi-mu)*h_C(lo)+(mu-lo)*h_C(hi))/(hi-lo)

over lo<mu<hi in S. Proof: minimization of a linear functional on a nonempty compact probability polytope attains a vertex. Any law supported on at least three distinct points has a nonzero perturbation supported on those points preserving normalization and mean. Scaling it sufficiently small permits perturbation in both directions; the law is not extreme. One- and two-point feasible supports give exactly the candidates above, each feasible. This establishes equality and produces a least-favorable witness. Since f is nondecreasing in usable attempts, g is nonincreasing in charge. The largest C with g(C)>=0 is a weak break-even; require g(C)>0 for a uniform strict benefit. The set can be empty for the strict criterion. All statements condition on the declared finite support and exact mean, not estimates.

## Numerical examples

For d=4, B=8, S={1/4,1/2,3/4}, mu=1/2, worst-case gaps C=0..4 are respectively 4545/32768, 6255/65536, 7/256, -33/256, -65/256. The uniform strict break-even is two attempt units. For B=12 it is four. If P can lie at both 0 and 1, there is a mean-preserving law under which every root is either always impossible or always solvable, eliminating a strict guaranteed benefit when the budget permits d successes. In particular for S={0,1}, d=4, B=8 and mu=1/2 no strict break-even exists.

## Checks and next gate

The exact receipt contains 180 comparisons with direct binary enumeration, 180 against exhaustive quota enumeration, and 180 robust-gap/monotonicity cases checked with 38 independently enumerated rational weight laws. The finite-grid oracle includes every extremizer at mean 1/2 on {0,1/4,1/2,3/4,1}, with denominator 8 or 3. Three unit tests pass. No empirical support, mean, or actual costs have been measured.

Reproduce:
    PYTHONPATH=src python -m pytest -q tests/test_evaluation_math_persistence_cost.py
    python scripts/verify_math_persistence_cost.py
    python scripts/check_receipts.py --only math_persistence_cost

Empirical design: record root-level repeat outcomes and retry conditional probabilities, not only aggregated closure. Fit any latent model exclusively on development roots; audit within-root correlations and calibration on a fresh split. Use matched symbolic and learned policies with the actual ledger cost, record all failed attempts, and run the repository's independent-world resolution preflight before sealing confirmation data. The next formal gate is a finite-horizon controller with state-dependent retrieval costs and posterior updates following failures, compared with a graph-matched symbolic scheduler. A support or mean estimated from finite data must carry a confidence region; the present exact mean constraint is not an empirical guarantee.

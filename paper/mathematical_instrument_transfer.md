# Mathematical instrument transfer under costly search (MIT-01)

Draft 0.1, 2026-11-25. Evidence: algebraic identities under a declared single-winner search model; exact finite synthetic mechanism checks. No language model was run. This is not a referee report on the physics or sphere-packing theorems.

## Motivation and claim scope

OpenAI, [Ten advances in mathematics and theoretical computer science](https://openai.com/index/ten-advances-in-mathematics/) (2026-08-01), reports a sphere-packing bound reaching the Cohn–Elkies threshold. Anthropic, [Claude solves two open problems in the physics of black holes](https://www.anthropic.com/research/claude-black-hole-physics) (2026-11-17), describes a related technique used to establish the optimal asymptotic spinless modular-bootstrap bound. A sphere-packing agent developed a method reproducing the OpenAI result; part of the later optimality argument followed the OpenAI strategy. An earlier agent had failed in 61 parallel attempts. These reports motivate instrument transfer; the 61 failures do not establish a controlled causal comparison, and the upstream Lean artifacts have not been independently rebuilt here.

## 1. Paid shortlist law

Let a target have N equally likely candidate strategies with exactly one winning strategy. An instrument returns a shortlist S of size K (0<K<N). Given the observed shortlist, the posterior probability that the winner lies in S is q; assume conditional exchangeability within S and its complement. For the before-acquisition comparison assume a uniform prior, and a symmetric shortlist channel with the same K and q for all realized S. For fixed S the calculation below is conditional. Each attempted strategy costs one unit, the instrument costs c integer units, and a verifier reveals the winner exactly. The budget B is a nonnegative integer with 0<=c<=B. Distinct strategies may be tried without replacement; every strategy is accessible even after the hint.

Put r=min(N,B-c), a=q/K, b=(1-q)/(N-K), L=max(0,r-(N-K)), H=min(K,r). An allocation of x attempts inside S has success mass x*a+(r-x)*b, with L<=x<=H. The optimum is

    P_paid = max(H*a+(r-H)*b, L*a+(r-L)*b).

Proof: any adaptive policy's all-failure path is a list of distinct strategies of length at most r; the event of closure is exactly membership in that list. Randomization mixes lists. Conditional exchangeability reduces the objective to the stated affine function of x, maximized at an endpoint. Unused capacity cannot increase the optimum. Ties allow either endpoint. The no-instrument baseline is min(N,B)/N. If acquisition is optional, take max of this baseline and P_paid in the symmetric single-channel case.

The shortlist is prioritized iff q/K >= (1-q)/(N-K), equivalent to q>=K/N (with both allocations equivalent at equality or when L=H). Anti-informative hints can be exploited by searching the complement first. A fixed policy that blindly searches the shortlist first achieves the H endpoint; it can underperform the unaided policy.

For 0<=c<B<=K<N and q>=K/N, the exact condition for a strictly positive paid transfer value is

    q > B*K / (N*(B-c)).

Proof: H=B-c; compare (B-c)*q/K with B/N and multiply by positive denominators. The threshold can exceed one, so perfect applicability need not justify acquisition. The same expression with q replaced by a lower bound q_min certifies strictly positive gain uniformly over a calibration interval if q_min exceeds the threshold. A fixed shortlist-first policy allows that bound without any assumption that the agent knows the true q. Estimating q requires independent calibration; this result does not supply a confidence interval.

Example N=16, K=4, B=4, c=1: break-even q=1/3. At q=1/2 paid success is 3/8 versus 1/4 unaided. At q=1/4 paid success is 3/16. At q=0, optimal complement search achieves 1/4 while blind priority achieves zero. All values are exact.

## 2. Adaptive instrument selection

Let a nonempty finite world set contain one hidden winner, with nonnegative weights w_i, positive total mass. An instrument j has a positive integer cost c_j and finite likelihood matrix L_j(y|i), whose columns are probability distributions. Queries are conditionally independent given i and each may be bought once. The state (w,A,b) consists of unnormalized posterior mass, unused instruments and remaining budget. A failed guess sets its coordinate to zero. Let V be successful mass, with V=0 at budget zero or zero mass.

    V(w,A,b) = max(
      0,
      max_i [w_i + V(w with i zeroed,A,b-1)],
      max_{j in A: c_j<=b} sum_y V(w*L_j(y|.), A\{j}, b-c_j)
    ).

Omit unavailable actions. The normalized value is V/sum(initial w). Induction on b proves optimality by partitioning successful worlds by first action and its observation; every action decreases b. A randomized first action averages deterministic values. Positive homogeneity in w follows by induction. The implementation also permits an immediate no-query top-b guess list, already included by the recurrence. This does not model arbitrary mathematical proof trees, concurrent search, correlated queries conditioned on omitted latent variables, or imperfect proof verification.

## 3. Adaptive separation (finite witness)

Eight equally weighted worlds indexed 0..7; budget four. Three unit-cost membership queries ask whether the winner lies in {0,1,2,3}, {0,1}, or {4,5}. Query the first set, then the appropriate two-element set, then guess the two remaining possibilities. Success is 1. The best fixed subset of queries bought before any guesses yields 3/4: with zero queries four guesses; with one query at most two cells and three guesses each; with two queries at most three nonempty cells and two guesses each; with three queries at most four cells and one guess each. The witness compares with fixed query prefixes only, not all possible nonadaptive interleavings of guesses and queries.

## 4. Reproduction

    PYTHONPATH=src python -m pytest -q tests/test_instrument_transfer.py
    python scripts/verify_instrument_transfer.py

The verifier invokes the test functions and records source hashes. The shortlist is cross-checked by explicit subset enumeration. The adaptive recurrence is independently checked against a deterministic partition oracle for 26 nonzero three-world integer priors, eight banks and five budgets (1,040 cases). The stochastic case is a unit witness, not a systematic independent stochastic audit. The committed receipt is generated by the verifier. Lean candidates are not part of a verified claim until a native kernel rebuild and axiom audit succeeds.

## 5. Next gate

Construct a proof-obligation transfer pilot with source-only, abstract instrument, applicable mapping, matched inapplicable mapping and unaided arms. Charge all acquisition, mapping, failed proof and verification work; register the root split and power preflight before a sealed readout. Estimate transfer and false applicability jointly. See the gym protocol. No architecture claim is supported by the finite model alone.

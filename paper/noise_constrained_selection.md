# NFAS-01: Noise-constrained selection and verification
**Research draft, 2026-11-25.** Algebraic identities and finite verified examples; cited upstream claims remain conditional.

## Sources and scope

* OpenAI, [Sharp binary-information contraction on the discrete cube](https://github.com/openai/math/tree/main/preprints/Sharp-binary-information-contraction-on-the-discrete-cube-September-24-2026), Theorem 1.1 in build/main.tex: uniform X on the sign cube, independent symmetric coordinate noise, binary U generated conditionally on X independently of the noise. The claimed soft-channel bound is I(U;Y) <= psi(|rho| psi^-1(I(U;X))), with psi(r)=ln 2 minus entropy of a sign of mean r. We use only its Boolean corollary I(f(X);Y) <= ln 2 - h(epsilon), where h is binary entropy in nats. The proof has not been audited here.
* OpenAI, [One Sample Suffices for Matroid Prophet Inequalities against an Almighty Adversary](https://github.com/openai/math/tree/main/preprints/One-Sample-Suffices-for-Matroid-Prophet-Inequalities-against-an-Almighty-Adversary-September-23-2026), abstract: independent nonnegative values, one independent sample per element, known finite matroid, adversary knows samples, realized values and seed and controls arrival order. Claimed competitive ratio 2^-310. No practical competitive guarantee is inferred. No proof audit.

## Theorem 1 (quota-sensitive selection bound; paper proof)

Let B_i be arbitrary binary failures, p_i=E B_i. A policy selects S of deterministic size r from m candidates, using a transcript T and independent private randomization. Let A_i=1{i in S}, q_i=E A_i and d_i(T)=Pr(B_i=1|T)-p_i. Randomization can be appended to T without changing I_i=I(B_i;T). The exact identity is E sum_{i in S} B_i = sum q_i p_i + sum Cov(A_i,d_i(T)). Conditional Pinsker in nats gives E d_i^2 <= I_i/2. Cauchy-Schwarz gives

    E failures <= sum q_i p_i + sum sqrt(q_i(1-q_i) I_i/2)
               <= sum q_i p_i + sqrt((r-r^2/m) sum I_i/2).

The same holds for the negative deviation by absolute values. When r=0 or r=m, the penalty vanishes. For rank r>0 divide by r to obtain mean risk per selected element. For partition bases, apply the second inequality within each block using its size and quota, then add. The theorem assumes selection uses the *full* declared transcript, including any side signals; it does not require independent failures.

Under the upstream Boolean contraction assumptions, B_i=f_i(X) and T=Y (or T adds only conditionally independent information given Y), each I_i <= ln 2 - h(epsilon). Consequently the uniform common-budget penalty is sqrt(r(m-r)(ln 2-h(epsilon))/2). It may be capped by r-sum q_i p_i. This last implication is conditional on the upstream theorem.

## Theorem 2 (exact fair-bit partition-base oracle)

X_i independent fair failure bits, Y_i their independent epsilon flips. For a block of n elements and mandatory quota r, posterior probability of failure is 1-epsilon when Y_i=1 and epsilon when Y_i=0. An adversarial selector maximizing expected failures picks the largest posterior probabilities, so the exact expected failure count is

    epsilon*r + (1-2*epsilon) E[min(K,r)], K ~ Binomial(n,1/2),

for 0 <= epsilon <= 1/2. Add over blocks. A fixed base has expected r/2. For a single selection, risk = epsilon + (1-2*epsilon)(1-2^-n). These are exact identities. The objective here is maximizing failures, not verification utility. If one selected item is perfectly verified, its failure is detected rather than authorized; a real authorization policy must specify which selections are verified.

## Finite audit

Run `node scripts/verify_nfas01.mjs --check` (Node 18+, no dependencies). The receipt includes a Git blob hash of the verifier. This standalone JS oracle is deliberately isolated from the existing Python receipt runner; port/integration is a later gate.

The Boolean census exhausts dimensions 1–4 at epsilon = 1/8, 1/4, 3/8; complement pairs share mutual information. A butterfly transform computes exact integer conditional probabilities; direct convolution independently cross-checks every function through n=3 and a deterministic subset at n=4. Logarithms use outward intervals scaled by 10^18: reduce x by powers of 2, then use 24 terms of the atanh expansion for ln((1+t)/(1-t)), with 0<=t<=1/3. The tail is bounded by 2*(1/3)^49/(49*(1-1/9)) < 10^-18. Every division is directed. Signed coordinates are equality witnesses checked directly. Every other function is strictly below the claimed universal bound in the tested grid. This is finite verification only, not proof of the upstream conjecture or its soft-channel strengthening.

The partition oracle independently compares the binomial formula with enumeration of latent states, noisy observations, and all feasible bases through six items, including zero and full quotas and epsilon=0,1/2. The threshold experiment has independent two-point values {0,w_i} with w=(1,2,4,8), independent samples and rank one. Accept the first value strictly exceeding the maximum sample. Exhaust every sample/value combination and every arrival permutation. The worst-order and best-order objectives are exact rational values. This tests a toy threshold rule, not the upstream general algorithm.

## Counterexample: filtration mismatch

At epsilon=1/2, Y is independent of fair hidden failures. An arrival-order adversary who also observes X can place a failing candidate first whenever one exists. A first-arrival selector then has risk 1-2^-m (255/256 for m=8), despite I(B_i;Y)=0. The arrival order is additional feedback and must be included in T. Likewise conditioning on shared feedback can destroy independence of candidate utilities; for independent fair V1,V2, conditioning on their parity makes them dependent. The upstream prophet result cannot be transferred unless conditional independence and independent samples are established under the actual disclosure policy.

## Next gates

NFAS-02: give each candidate a nonnegative independent utility, a hidden failure event, and a known partition quota. Declare the full transcript, when utility is observed, whether order depends on hidden failures, and what independent verification certifies. Compare fixed independent audit, sample-threshold selection, posterior-risk prioritization and offline utility optimum. Enumerate finite policies and worst-order cases, report verified utility and expected unverified failures separately. Freeze a small instance grid before adding correlated utilities or repeated/adaptive disclosures. Formalize Theorem 1 using finite probability in Lean; no Lean proof claimed in NFAS-01. Keep empirical agent experiments in Control-Harness.

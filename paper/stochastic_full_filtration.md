# Stochastic evaluation feedback and full-filtration ordering

**Draft 0.1 | 26 October 2026.** An exact finite extension to [selection risk](selection_risk_continuations.md) and [covert feedback risk](covert_feedback_risk.md), informed by the adversarial acquisition-order and conditional-null boundaries in [Beyond-Bayes](https://github.com/patrickdugan/beyond-bayes). The new module `src/spiral_ln/evaluation_full_filtration.py`, its unit tests, and the source-hashed `full_filtration_v0_1.json` receipt are synthetic mathematical research artifacts. No real model, grader, instrument or stochastic sampling system has been tested. The results below are classical finite dynamic programming and filtration calculations, with explicit provenance and evidence levels.

## 1. Exact information contract

Nature draws a *fixed* null world \(\omega\in\Omega\) with positive integer weight \(m_\omega\), total \(M=\sum_\omega m_\omega\). Candidate test \(j\) has a Boolean false-authorization event \(E_j\). Public query \(q\) produces a response \(y\) from a rational kernel \(K_q(y\mid\omega)\). A private signal, unreported to the public audit, is emitted from another rational kernel \(C(h\mid\omega)\). Conditional on \(\omega\), response draws on distinct rounds and private draws on distinct rounds are independent, even if public queries are chosen adaptively. The actor can use all its acquired information to choose the next public query and which candidate test to report.

There are two acquisition orders per attempted query: **private-first** observes \(h\) before choosing \(q\), then observes \(y\); **public-first** chooses \(q\), receives \(y\), and then receives \(h\). The actor may stop and report a test before exhausting the allowed number of queries, in which case it forfeits future samples. A signal already seen remains available for future choices. This timing distinction supplies a concrete analogue of the full actor filtration required by Beyond-Bayes.

## 2. Theorem: exact stochastic Bellman equations

For a vector of unnormalized nonnegative rational world masses \(\mu\), let

\[
J(\mu)=\max_j\sum_{\omega\in E_j}\mu_\omega,\qquad
(\mu C_h)_\omega=\mu_\omega C(h\mid\omega),\qquad
(\mu K_{q,y})_\omega=\mu_\omega K_q(y\mid\omega).
\]

Set \(B_0(\mu)=A_0(\mu)=J(\mu)\). For \(k\ge1\), the optimal unnormalized false-authorization masses under the two acquisition orders are exactly

\[
\boxed{B_k(\mu)=\sum_h\max\left\{J(\mu C_h),\max_q\sum_y B_{k-1}(\mu C_hK_{q,y})\right\}}
\]

and

\[
\boxed{A_k(\mu)=\max\left\{J(\mu),\max_q\sum_y\sum_h A_{k-1}(\mu K_{q,y}C_h)\right\}}.
\]

The risks are \(B_k(m)/M\) and \(A_k(m)/M\). Both optimize over deterministic query-selection trees and final test choices, with actual query identifiers included in their public transcript.

*Proof.* At any actor history, all future conditional observation probabilities and terminal false-positive payoffs depend on that history through the unnormalized vector \(\mu\). This follows from the fixed-world assumption and conditional independence of future draws. A terminal choice optimizes \(J(\mu)\). In the private-first model, the actor receives \(h\) and separately optimizes its action for each attainable \(h\). A chosen \(q\) then yields response \(y\) with the corresponding unnormalized mass vector; induction on the remaining rounds proves the first recurrence. The public-first recurrence follows by reversing the order of these conditional decisions. A finite deterministic decision tree attains each maximum, and a randomized mixture cannot improve a linear expected objective. \(\square\)

**Evidence: algebraic identity.** The implementation returns both the exact rational optimum and its selected policy tree. The policy is independently evaluated by exhaustive world-and-outcome path summation. A second one-round oracle searches all query assignments to private-signal values and chooses final tests by direct conditional event counts.

Under this finite information contract, private-first information is weakly more valuable than the same signals obtained after their corresponding queries, and either schedule dominates committing all public query choices in advance. Extra query opportunities can be ignored. The verifier checks these relations at zero-, one- and two-round horizons.

## 3. A pair of nominally 5%-calibrated tests

Let \(S,A\) be independent fair bits and \(R\sim\mathrm{Bernoulli}(1/10)\) be independent of them. The null has eight worlds \((S,A,R)\). Define two test events

\[
E_0=\{R=1,A=0\},\qquad E_1=\{R=1,A=1\}.
\]

Each is calibrated to an unconditional probability of exactly \(1/20\). A private signal reveals the selector \(S\). Query \(q_s\) reports a noisy version of \(A\), correct with probability \(3/4\), when \(s=S\); the query returns a distinct erasure otherwise. The query outcome is public and the actor chooses which test to report after seeing its available information.

| Query/information schedule | Exact optimal false-authorization risk |
|---|---:|
| Zero queries | \(1/20=5\%\) |
| One query, private selector **before** choosing query | \(3/40=7.5\%\) |
| One query, private selector **after** choosing query | \(1/16=6.25\%\) |
| Two queries, either timing | \(3/40=7.5\%\) |

*Derivation.* Conditional on \(R=1\), the private-first actor always queries the correct selector and learns \(A\) with probability \(3/4\), hence \((1/10)(3/4)=3/40\). In the public-first single-query case, the selector agrees with the predetermined query half the time, contributing success \(3/4\); otherwise the erasure carries no information about \(A\) and the best choice succeeds with probability \(1/2\). Thus \((1/10)((3/4+1/2)/2)=1/16\). Two queries can inspect both selectors. \(\square\)

**Evidence: algebraic identity for these explicitly constructed finite probabilities; finite verified example for the executable implementation.** The individual 5% calibration concerns each fixed event. Outcome-dependent selection of the event creates a different decision procedure requiring an appropriate joint risk allowance.

## 4. A coarse martingale and a private pre-peek

Let \(X\sim\mathrm{Bernoulli}(1/2)\). Consider \(M_0=1\) and \(M_1=2X\). This is a martingale relative to the public filtration \(\mathcal G_0\) trivial, \(\mathcal G_1=\sigma(X)\), since \(\mathbb E M_1=1\). Suppose a private time-zero signal \(H\) guesses \(X\) correctly with probability \(p\ge1/2\). Relative to the actor's enlarged filtration \(\mathcal F_0=\sigma(H)\), the conditional expected one-step factors are \(2(1-p)\) or \(2p\), depending on \(H\). The actor may stop at time zero when \(H=0\) and at time one otherwise. For that stopping rule,

\[
\mathbb E[M_\tau]=\tfrac12+p,
\]

giving the exact stopped expectation \(5/4\) at \(p=3/4\). The two conditional expectations are \(1/2\) and \(3/2\). Enumerating all four possible private-signal-dependent stopping rules confirms optimality.

**Evidence: algebraic identity.** A one-step factor divided by \(2p\) satisfies the conditional expectation constraint in this particular one-step model. The general problem of lifting e-processes across filtrations is treated by Choe and Ramdas (2026), [*Combining Evidence Across Filtrations*](https://doi.org/10.1093/jrsssb/qkag058), JRSS-B 88(4), 1492–1514. Their adjuster constructions and characterization results are outside the scope of this code.

A consequential distinction: this counterexample defeats the *stopped-expectation e-process requirement in the enlarged filtration*. The fixed unmodified martingale's original **pathwise threshold-crossing** guarantee remains intact, since selecting a stopping time cannot create a crossing absent from the realized path. Post-selection across multiple tests is a separate source of elevated false-authorization risk.

## 5. Continuation-sufficient statistical compression

**Theorem (fixed-vocabulary world aggregation).** When two null worlds have the same Boolean event vector, private-signal response distribution and response distribution for every available public query, they can be replaced by one world whose mass equals the sum of their masses. Every future adaptive policy's joint observation/event law and its optimum false-selection risk remain unchanged for all finite horizons.

*Proof.* The likelihood of every possible next private or public outcome is the same in the two worlds. Their posterior unnormalized masses therefore acquire the same likelihood multiplier under any continuation. Summing their weights commutes with each update, so all terminal event masses and optimal policy values are preserved by induction. \(\square\)

**Evidence: algebraic identity.** Forty randomly generated fixtures duplicate every world with an additional positive mass, then recompute each optimum on the original and compressed models. All six timing/horizon comparisons per fixture reproduce exactly.

This sufficiency statement is relative to the *declared statistical future vocabulary*. It does not certify procedural histories that permit arbitrary future source revocation, altered risk scope, new query families or externally chosen sampling rules. The proposed Dot Matrix research state in Beyond-Bayes addresses those distinct continuation questions with event-sourced provenance and recoverable archives.

## 6. Verified scope and next theorem target

All computations use `fractions.Fraction`. The new verifier records 20 checks, **192** comparisons against an independently coded one-round exhaustive policy oracle, **144** direct world/outcome replays of cached two-round optimal policies, **40** world-compression fixtures and SHA-256 hashes of its source files. Nine new pytest tests cover zero-probability outcomes, hidden-signal timing, repeated queries, calibrated events, prior compression, and malformed kernels. No Lean theorem is asserted.

The world remains static; observation kernels are precommitted and conditionally independent given it. Hidden side-information availability and its causal acquisition time are stipulated mathematical assumptions. Signatures, timestamps and software start receipts alone do not establish those physical assumptions in Beyond-Bayes ACE v0.10.

**Next mathematical obligation:** admit controlled finite latent-state transitions and history-dependent noisy kernels, then characterize what a verified public transcript can certify when the actor receives unrecorded information between queries. Compare any proposed conditional-null or evidence-lifting bound with finite POMDP theory and the filtration-lifting literature before claiming novelty.

Reproduce with `python -m pytest tests/test_evaluation_full_filtration.py -q` and `python scripts/check_receipts.py --only full_filtration`. This note is mathematical and synthetic evidence only.

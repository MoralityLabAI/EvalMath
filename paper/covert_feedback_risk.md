# Risk from bounded covert evaluation feedback

**Draft 0.2 | 2026-10-26.** A narrowly specified extension of [post-selection risk](selection_risk_continuations.md), motivated by the full-filtration and acquisition-order assumptions in `patrickdugan/beyond-bayes` ACE v0.6–v0.10. Source: `src/spiral_ln/evaluation_covert_feedback.py`; independently structured tests: `tests/test_evaluation_covert_feedback.py`; verifier: `scripts/verify_evaluation_covert_feedback.py`; exact receipt: `output/evaluation_covert_feedback/covert_feedback_v0_2.json`.

**Evidence labels:** The finite identities and sharp bounds below are *algebraic identities*, with paper proofs. All numerical witnesses and 210 independently enumerated comparisons are *finite verified examples*. No learner, judge, real instrument or model was run. No new Lean formalization is claimed. The ideas are instances of classical Bayes decision theory and weighted maximum coverage, not an assertion of priority over that literature.

## 1. Declared information contract

Fix finitely many distinct null worlds \(\omega\in\Omega\), positive integer masses \(w_\omega\), and total \(W=\sum_\omega w_\omega\). Test \(j\in[m]\) has a fixed false-authorization event \(E_j\subseteq\Omega\). An existing *public* deterministic evaluator transcript partitions the worlds into nonempty classes \(F_t\). The actor may select one of the tests after reading its public transcript.

Suppose an **additional unrecorded message** \(H\) takes at most \(L\ge1\) different values *per public transcript*. For the upper-bound problem, an adversarial encoder is permitted to inspect the entire world and select \(H(\omega)\), while the final reported test \(J(t,H)\) may use only the public transcript and the message. This permits arbitrary correlation between hidden messages and candidate outcomes. Its premise is an explicit finite alphabet cap, which real acquisition systems would have to establish separately. \(L\) is a number of message *symbols*, **not** the number of experiments inspected, a Shannon mutual-information budget, or an attestation of what the evaluator really saw.

The previously established public-transcript risk is

\[
R_1(T)=\frac{1}{W}\sum_t\max_j\sum_{\omega\in F_t\cap E_j}w_\omega.
\]

## 2. Exact covert-channel optimization

**Theorem 1 (bounded covert selection).** The greatest achievable false-authorization probability when there are at most \(L\) hidden message symbols per public transcript is

\[
\boxed{R_L(T)=\frac1W\sum_t\max_{S\subseteq[m],\ 1\le|S|\le L}\ \sum_{\omega\in F_t\cap\bigcup_{j\in S}E_j} w_\omega.}
\]

*Proof.* Fix the public response \(t\). Each possible covert message \(h\) leads to one selected test \(j(t,h)\). Since at most \(L\) messages exist, these decisions name a set \(S_t\) of at most \(L\) tests. Every successfully authorized world in \(F_t\) must belong to the union of those events, which bounds its total mass by the displayed maximum. For attainment, choose a maximizing set \(S_t=(j_0,\ldots,j_{r-1})\). If \(\omega\in F_t\) lies in one of its events, send the first message index \(h\) whose test succeeds; on worlds outside the union send an arbitrary message. The resulting decision succeeds exactly on \(F_t\cap\bigcup_{j\in S_t}E_j\). The public fibres partition the null, so sum over \(t\). Randomized hidden encoders and test selectors cannot improve the maximum because conditional risk is affine in their randomization. \(\square\)

This is weighted **maximum coverage** within each public transcript. The code enumerates event-index subsets and constructs an attaining message assignment; an independent oracle enumerates every *world-to-hidden-symbol map* and selects the best test within each message class. These implementations have different search spaces and agree on all 210 seeded small-world comparisons.

**Corollary 2 (sharp factor bound and endpoints).** For every public partition,

\[
R_1(T)\le R_L(T)\le\min\left\{\frac1W\sum_\omega w_\omega\mathbf1_{\cup_j E_j}(\omega),\ L R_1(T)\right\}.
\]

Moreover \(R_L(T)\) is nondecreasing in \(L\), and \(R_m(T)\) equals full-information risk. The factor \(L\) is sharp: with no public observations and \(L\) mutually disjoint, equiprobable false-positive events of mass \(a\), \(R_L=L a\) while \(R_1=a\).

*Proof.* An actor can ignore extra messages. The union of \(L\) tests within a public fibre has mass at most the sum of their event masses, each no greater than the largest event mass in that fibre, and at most the full union mass. Enlarging the event set cannot decrease its covered mass. Taking all \(m\) events realizes the full union. Disjoint events attain the factor bound. \(\square\)

**Proposition 3 (minimum hidden alphabet for full risk).** In each public fibre, let \(U_t=F_t\cap\bigcup_{j=1}^mE_j\), and let \(\tau_t\) be the smallest number of events whose union covers \(U_t\). (Set \(\tau_t=1\) if \(U_t\) is empty.) The smallest alphabet limit that gives full-information risk on every leaf is \(\max_t\tau_t\).

*Proof.* Since masses are positive, a chosen test family attains the full risk in a fibre precisely when its union covers every world of \(U_t\). A different family is permitted for each public transcript. \(\square\)

This is a finite weighted optimization/certificate, not an empirical claim that a hidden side channel is controllably limited to \(L\) signals.

## 3. Exact statistical witnesses

Two tests with **identical marginal error rates** of \(1/20\) show why source dependence matters. In one model both false-positive events fire on the same world, so even an unlimited covert channel has risk \(1/20\). In another model the events are disjoint and a single covert bit (\(L=2\)) raises maximum risk from \(1/20\) to \(1/10\). The marginal event rates agree exactly in the two models.

For **three independent** Bernoulli(\(1/20\)) false-positive events on eight possible outcome vectors, weighted by their exact product probabilities, the outcomes are:

| Information before selecting one test | Exact false-authorization risk |
|---|---:|
| No feedback, or \(L=1\) hidden symbol | \(1/20=5\%\) |
| No public feedback, \(L=2\) hidden symbols | \(39/400=9.75\%\) |
| No public feedback, \(L=3\) hidden symbols | \(1141/8000=14.2625\%\) |
| Publicly reveal the first test outcome, no hidden channel | \(39/400\) |
| Publicly reveal the first test outcome, plus a covert binary message | \(1141/8000\) |

The last row reaches full-information selection risk. Under this particular null, after a public failure on test 1, a covert bit can choose whether test 2 or 3 is the favorable candidate; on a public success, choose test 1. The covert encoder is permitted to inspect all outcomes before sending that bit. This distinction between **message bandwidth** and **causal acquisition access** is operationally important.

These numbers are finite verified examples. Their values are derived from the explicit Boolean event distribution, with probabilities \(1-(19/20)^2=39/400\) and \(1-(19/20)^3=1141/8000\). The events are abstract false positives under a declared null; they are not measured failure rates of a real evaluator.

## 4. Joint public-query optimization with terminal covert signaling

**Theorem 4 (finite Bellman law).** Assume that the public agent can choose the next query using only the previous *public* responses, and receives its \(L\)-symbol covert message only after the final public query. For a nonempty subset \(B\subseteq\Omega\), define the unnormalized terminal value

\[
V_0(B;L)=\max_{S\subseteq[m],\ 1\le |S|\le L}\sum_{\omega\in B\cap\cup_{j\in S}E_j}w_\omega.
\]

With at most \(k\ge1\) additional public queries from a finite bank \(\mathcal Q\), the exact optimal value is

\[
\boxed{V_k(B;L)=\max\left\{V_0(B;L),\ \max_{q\in\mathcal Q}\sum_{a:\, B_{q,a}\ne\varnothing}V_{k-1}(B_{q,a};L)\right\},}
\qquad B_{q,a}=\{\omega\in B:q(\omega)=a\}.
\]

The unconditional optimal risk is \(V_k(\Omega;L)/W\).

*Proof.* An optimal controller may stop immediately and obtain \(V_0\). Otherwise its first query \(q\) partitions \(B\) into the reachable response sets \(B_{q,a}\). The controller selects a continuation independently for each observed response. Exactly \(k-1\) public queries remain per response, so backward induction yields the sum of optimal child values. The terminal covert message is optimized independently within each resulting leaf by Theorem 1. All query decisions depend on public history, as required. \(\square\) **Evidence: algebraic identity.**

For three IID 5% false-positive events, with the public query bank consisting of a constant and each individual test outcome, zero public queries and one covert bit yield risk \(39/400\). One public query plus a covert bit yields \(1141/8000\); two public queries with no covert feedback also yield \(1141/8000\). **Finite verified examples** with explicit optimal trees. Eighty seeded small models were checked by an *independent whole-policy enumerator* that tries each first public query, each response-contingent second query or stop, and every complete covert message assignment, rather than calling the Bellman recursion or weighted coverage routine.

For the five-atom example of [selection-risk continuation](selection_risk_continuations.md), a two-public-query budget with no covert access has fixed-query optimum \(3/40\) and adaptive optimum \(1/10\), while a single public query plus one terminal covert bit reaches \(1/10\). These relations depend on the chosen query bank and the event structure; no general substitutability law between public queries and covert message bits is claimed.

An unrecorded signal that also informs *intermediate* public query choices violates this theorem's policy-information contract. Its accessible query histories must then be modeled using an expanded filtration and a new decision tree.

## 5. Cross-repository implications and proof boundaries

1. **EvalMath.** A public query partition determines \(R_1(T)\). Adding a covert alphabet yields the exact maximum-coverage functional \(R_L(T)\); the existing adaptive-query tree can supply public fibres. To analyze an auditor who also uses hidden information when choosing *future public queries*, model the combined actor's actual query policy and information filtration, rather than applying an exogenous public partition blindly.
2. **Beyond-Bayes ACE.** A signed reservation, risk-spend ledger and source signature authenticate a recorded history under stated trust assumptions. They alone cannot upper-bound a covert encoder's available alphabet or show that source values were generated after reservation. ACE's sequential familywise guarantee still requires conditional validity relative to *all* prior actual information. A nominal \(\alpha\) assigned to each candidate event need not be the null risk of its outcome-dependent selected event.
3. **Dot Matrix.** Finite risk sufficiency is relative to a fixed contract: null event family, query bank, public policy, actual information boundary and future procedural event vocabulary. The contingency histogram and audit continuation state in PR #5 preserve recorded deterministic continuations. Unobserved pre-peeking is outside that certificate. The source archive supports rehydration if tests, causal dependencies or admissible queries are later amended.

Recent formal work directly relevant to this boundary is Choe and Ramdas, *Combining Evidence Across Filtrations*, **JRSS-B** 88(4), 1492–1514 (2026), https://doi.org/10.1093/jrsssb/qkag058. They study the failure of coarse-filtration e-process validity in a finer information filtration and methods using adjusters to restore such validity. The current finite-risk result neither constructs an adjuster nor establishes an anytime-valid e-process theorem. The result is best interpreted as a bounded finite decision-risk calculation motivating which filtration an ACE certificate needs to cover.

**Next mathematical target:** extend the finite model to stochastic/noisy responses and side information that can affect intermediate query choices, with an explicit full-filtration conditional-null contract. Compare the resulting error guarantees against ACE's e-process requirements. Any formal novelty claim should be tested against information-constrained statistical decision theory, adaptive-data-analysis bounds and the 2026 filtration-lifting literature.

## 6. Reproduce

```bash
python -m pytest tests/test_evaluation_covert_feedback.py -q
python scripts/check_receipts.py --only covert_feedback
```

The verifier regenerates a schema-v0.2 receipt containing 19 checks, 70 seeded null models, **210** covert message-assignment comparisons and **80** independent two-round joint-policy comparisons to the independent hidden-assignment oracle, monotonicity/bound checks and exact SHA-256 source hashes. It makes no use of clocks, external assets, cryptographic signatures or network data. The source model is small, deterministic, and intended for independent replication.

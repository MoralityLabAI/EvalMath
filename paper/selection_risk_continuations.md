# Selection risk under adaptive evaluation: finite channel and audit-state results

Draft 0.1, 26 October 2026. Exact finite examples, algebraic identities, and a declared audit automaton. **Research scope:** This note quantifies how disclosed evaluation information permits post-selection of false-positive events, and what a finite procedural state must retain for later amendments or revocations. All null models and state transitions are specified, and no model or grader was run. The work is a synthesis of established decision and automata mathematics with executable, exact synthetic witnesses. It is not a new general theory of valid statistical inference.

Module: `src/spiral_ln/evaluation_selection_risk.py`; tests: `tests/test_evaluation_selection_risk.py`; independent verifier: `scripts/verify_evaluation_selection_risk.py`; receipt: `output/evaluation_selection_risk/selection_risk_v0_1.json`. The verifier records the SHA-256 of all three source files.

## 1. Risk after observing a finite feedback channel

Let \(\Omega\) be a finite null-world set with positive integer masses \(w_\omega\) and total \(W\), let \(E_1,\ldots,E_m\subseteq\Omega\) be potential false-authorization events, and let \(T:\Omega\to\mathcal T\) be the information made available *before* selecting which event to report. The controller can choose exactly one event as a function of the observed transcript.

**Proposition 1 (finite post-selection value).** The maximum false-authorization probability obtainable by choosing an event after seeing \(T\) is

\[
 \mathcal R(T)=\frac1W\sum_{t\in\mathcal T}\max_{1\le j\le m}\sum_{\omega:T(\omega)=t,\omega\in E_j}w_\omega.
\]

*Proof.* For every transcript cell, selecting event \(j\) contributes exactly its mass in that cell. Choosing independently the largest mass in each cell maximizes their sum. Randomization cannot exceed a deterministic maximizer. \(\square\)

With no feedback the value is \(\max_j P_0(E_j)\); with complete observation it is \(P_0(\bigcup_jE_j)\). Therefore

\[\max_j P_0(E_j)\le\mathcal R(T)\le P_0(\bigcup_jE_j).\]

Further deterministic information can only split transcript cells, so \(\mathcal R\) is monotone under channel refinement. For a split of cell \(B\) into \(B_a\), the exact incremental gain in *unnormalized* risk is

\[\sum_a\max_j w(B_a\cap E_j)-\max_jw(B\cap E_j)\ge0.\]

These facts are elementary instances of the Blackwell value-of-information principle. Evidence level: **algebraic identity**, with finite executable corroboration. They are not a novelty claim about Blackwell's theorem.

**Proposition 2 (optimal adaptive query recurrence).** Suppose a finite bank of deterministic integer-valued queries \(q_1,\ldots,q_r\) can be asked, with at most \(k\) subsequent queries. For any nonempty current posterior cell \(B\), let \(V_0(B)=\max_j w(B\cap E_j)\). Then

\[
 V_k(B)=\max\Big(V_0(B),\ \max_{q\in\mathcal Q}\sum_{a\in q(B)}V_{k-1}(B\cap\{q=a\})\Big).
\]

*Proof.* Condition on the next query and exact response. Child subproblems are independent choices of future questions. Include stopping as the first candidate, then apply backward induction. \(\square\) **Algebraic identity.** The code checks this recurrence against an independent enumerator of *whole* two-query decision trees on 192 seeded, finite null models. The exhaustive oracle enumerates a first query and every branch's choice of a second query or stopping, then optimizes event selection per final cell. Exact values agree on every case; this is a **finite verified example** of implementation fidelity.

## 2. Marginally identical models have different future selection risk

Two tests \(A,B\) each have marginal false-positive probability \(1/20\). In the *shared* null, only states \((A,B)=(0,0)\) and \((1,1)\) occur, with probabilities \(19/20,1/20\). In the *disjoint* null, states \((0,0),(1,0),(0,1)\) have probabilities \(18/20,1/20,1/20\). A controller next learns the single bit \(A\).

In both models, the pre-query maximum is \(1/20\). After the query, the shared model still permits only \(1/20\), since simultaneous false positives occur together. In the disjoint model the controller chooses \(A\) after seeing \(A=1\), and \(B\) after seeing \(A=0\); its total risk is \(2/20\). The *per-test marginal vector, current value and current decision* were identical. Their future risk differs. **Algebraic counterexample.**

This shows precisely why a state recording only marginal test error rates is insufficient for the future-query contract. It does not show that the full underlying null law is always necessary.

## 3. A two-query adaptive advantage with individually calibrated events

An exact five-atom null (integer masses summing to 40) has three potential false-positive events, called \(A,B,C\), and three available binary score queries. Here is the complete definition:

| World | Mass | False-positive events occurring | \(q_0\) | \(q_1\) | \(q_2\) |
|---|---:|---|---:|---:|---:|
| \(\omega_0\) | 1 | C | 1 | 0 | 1 |
| \(\omega_1\) | 1 | A | 1 | 0 | 0 |
| \(\omega_2\) | 1 | B | 0 | 0 | 0 |
| \(\omega_3\) | 1 | B | 1 | 1 | 1 |
| \(\omega_4\) | 36 | none | 0 | 0 | 0 |

The marginal errors are \(P(A)=1/40\), \(P(B)=2/40=1/20\), and \(P(C)=1/40\). All individually meet a nominal 5% ceiling. Selecting a test without feedback gives risk \(1/20\).

**Finite verified example.** Over all fixed schedules of at most two queries, the maximum risk is \(3/40\). The optimal adaptive tree first asks \(q_2\), then asks \(q_0\) on its zero branch and \(q_1\) on its one branch. Each of the four false-positive worlds can now be assigned to its respective successful test. Adaptive risk reaches the complete-information ceiling \(4/40=1/10\). A second implementation independently enumerates all first-query choices and all response-dependent second choices and obtains exactly the same optimum. The fixed-query oracle evaluates ten schedules, including stopping and repeated queries.

The witness isolates the effect of a **bounded adaptive observation policy** on post-selection risk. Its events and query functions are synthetic and are not asserted to arise from realistic p-values or independent item outcomes. No general strict-gain theorem is inferred from this fixture.

## 4. Finite continuation-sufficient risk information

Define the *response/event contingency histogram* of the known null law to give, for each possible joint vector

\[(q_1(\omega),\ldots,q_r(\omega),\mathbf 1_{E_1}(\omega),\ldots,\mathbf1_{E_m}(\omega)),\]

the total mass of null worlds realizing that vector. Worlds with identical vectors may be merged by summing their weights.

**Proposition 3 (contract-relative sufficiency).** The histogram determines the risk of every deterministic, finite-depth adaptive query tree over the fixed bank and the fixed false-positive event family. Conditioning after any available query corresponds to selecting histogram rows whose answer coordinate agrees with the observed value, so the same histogram supports sequential updates. Consequently the optimal value \(V_k\) is preserved for every finite \(k\).

*Proof.* Every allowed query and every candidate false-positive event is constant on each histogram class. All transcript fibres are therefore unions of classes; every event mass in every leaf is preserved. Filtered class masses give exactly the corresponding posterior calculation, and induction on depth gives the optimal adaptive value. \(\square\) **Algebraic identity.** The receipt compares compressed and original models for 192 finite examples, including all two-round adaptive values. This is a *sufficient* state for the specified fixed query/event vocabulary, and may contain redundant information for a narrower decision problem.

If later queries can inspect a new feature or a source revocation changes the definition of admissible evidence, an earlier aggregation may have discarded distinctions that have become relevant. A content-addressed, losslessly recoverable archive supports recomputing the state under a new contract. A commitment hash without retrievable content supports integrity verification but does not recover those distinctions.

## 5. Continuation state for revocations and amendment timing

We instantiate a finite procedural machine whose histories have an active bitmap of \(m\) separately revocable support roots and one of three chronology phases: before any observation, after an observation with no post-observation amendment, and after a post-observation amendment. Events are idempotent \(\mathrm{GRANT}_i\), \(\mathrm{REVOKE}_i\), \(\mathrm{VIEW}\), and \(\mathrm{AMEND}\). The declared outputs are a current `GO`/`STOP` depending on whether any root is active and an `eligible`/`exploratory` procedural status depending on whether a late amendment occurred. These statuses are rules of this synthetic contract, not statements about whether external claims are true.

**Proposition 4 (all states necessary for this contract).** All \(3\cdot2^m\) reachable machine states are pairwise distinguishable by some legal future event sequence. Hence any exact finite continuation-sufficient encoding for this model needs at least

\[\big\lceil\log_2(3\cdot2^m)\big\rceil=m+2\quad\text{bits}.\]

*Proof.* If root sets differ, choose a root in their symmetric difference and revoke every other root. The `GO` outputs then differ. If root sets coincide but chronology phases differ, phase 2 is immediately observable through the status output. Phases 0 and 1 have the same present output but the event `AMEND` makes the latter exploratory while leaving the former eligible. Every root subset is reachable by grants; phases 1 and 2 are reached by `VIEW` and `VIEW, AMEND`. An encoding containing the exact bitmap and two phase bits attains the claimed bit bound. \(\square\) **Algebraic identity for the declared machine.** Generic partition refinement independently computes the Moore-automaton quotient; a separate breadth-first search constructs distinguishing continuations for all 276 state pairs when \(m=3\). It finds 24 classes requiring five bits. Results for \(m=1,2,3,4\) are also checked.

This builds on the classical Myhill–Nerode right-congruence theorem, with a specific procedural event vocabulary. It is neither a theorem about arbitrary research histories nor a minimality result for real-world inference systems.

### Product state for a fixed risk/audit contract

Let \(H\) be the response/event contingency histogram from Proposition 3, restricted to worlds compatible with the responses observed so far. Let \(z\) be a state of the procedural machine in Proposition 4, or its continuation-equivalence class. A **risk projection** is the pair \((H,z)\). The contract permits ordinary procedural events plus selection of a query \(q\) from the fixed bank. A disclosed response \(a\) removes from \(H\) precisely the rows whose \(q\)-coordinate differs from \(a\), and *also* feeds the event `VIEW` to \(z\). Procedural events update \(z\) while preserving \(H\). The numerical current selection risk is the maximum event mass in \(H\), divided by its total mass.

**Proposition 5 (joint continuation sufficiency under recorded histories).** Two recorded histories with identical risk projections have the same current procedural output and conditional selection risk. For every finite adaptive continuation allowed by the fixed bank and procedural machine, they have identical distributions of future query responses, identical subsequent risk projections after each response, and identical procedural outputs.

*Proof.* Both histories assign identical joint masses to every available query-response/event pattern, so the next selected query has the same response distribution. After any response, both histories filter the same histogram rows. The machine has deterministic, well-defined transitions on continuation classes. Induct over the continuation length, allowing query choices to depend on previous observed responses and procedural outputs. \(\square\) **Algebraic identity for the declared model.** The implemented `RiskProjection` updates each posterior histogram exactly and automatically registers `VIEW` when a query is disclosed. Two new independent tests and four verifier checks cover the product construction; the source hashes are part of the receipt.

This projection can be materially smaller than raw histories and is exact only for **the declared fixed vocabulary and complete recorded exposure history**. The stated contract allows any finite continuation of queries without a global query quota. If future query eligibility depends on prior query counts, remaining alpha, cost budgets, deadlines or already-consumed challenges, those counters and obligations must also be included in the procedural state; an otherwise identical histogram can represent different available actions. If an additional feature, event family, physical side channel or amendment semantics is admitted, the sufficient projection needs revalidation or reconstruction from the archive. In particular, the positive result does not certify unrecorded pre-peeking.

## 6. Physical and probabilistic validity boundary

A procedural ledger can verify the sequence of *recorded* commitments, query releases and amendments. If the actor sees outcomes before the alleged reservation and the observation is omitted from the record, two different causal histories may present identical signed-looking audit records. Any deterministic verification function of those records returns the same answer. A certificate of actual acquisition order therefore needs an independently trustworthy sampling or information-flow boundary, as opposed to a signature of a caller-supplied value after the fact.

In the simple case of 20 independent null tests with per-test false-positive rate \(1/20\), choosing the first successful candidate *after seeing them all* gives exact family-wise risk

\[1-(19/20)^{20}\approx0.641514.\]

A single properly selected test has nominal rate \(1/20\). The calculation is exact, while the causal semantics of a real test or instrument must be established separately. Sequential alpha spending can guarantee a budget only when the selected levels and tests satisfy the claimed conditional validity relative to the **full actual information filtration**. A correct budget ledger does not establish that probabilistic premise.

Choe and Ramdas (2026) specifically study combining evidence across different filtrations, including why validity in a coarser filtration does not automatically persist in a finer one. That literature is directly relevant before extending the present finite-event calculations to real e-processes. This note contains no new filtration-lifting theorem.

## 7. Reproduction and research frontier

Run `PYTHONPATH=src python -m pytest tests/test_evaluation_selection_risk.py -q` and `PYTHONPATH=src python scripts/verify_evaluation_selection_risk.py`. The verifier includes 22 checks: exact analytic fixtures, 192 independently enumerated finite policy comparisons, 192 histogram-compression comparisons, minimal automaton classes for up to four roots, and 276 pairwise continuation witnesses for the three-root contract. The receipt records source hashes and a deterministic test-case fingerprint. **No Lean formalization is claimed.**

Three unsolved directions are substantive: (i) state minimization for a stochastic, externally justified conditional-null model with source revocations and bounded horizons; (ii) post-selection risk under noisy/partial evaluator channels with an actor's additional side information explicitly modeled; (iii) prospective tests of whether a compact auditable reviewer outperforms a matched history-aware reviewer on consequential procedural errors. For such tests, use a truly unseen sealed case set and preregister the error metric and compute budget. Keep exploratory examples from this repository outside the confirmatory set.

## Relevant prior work

- Blackwell comparison of statistical experiments and Bayes decision value: https://doi.org/10.1214/aos/1176344790
- Dwork et al., *The Reusable Holdout* (2015): https://research.ibm.com/publications/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis
- Russo and Zou, information-theoretic adaptive-selection bias (2016): https://proceedings.mlr.press/v51/russo16.html
- Choe and Ramdas, *Combining Evidence Across Filtrations*, JRSS-B (2026): https://doi.org/10.1093/jrsssb/qkag058
- Myhill–Nerode theorem, standard finite continuation-equivalence state minimization.

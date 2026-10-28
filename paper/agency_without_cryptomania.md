# Agency without Cryptomania: an exact finite witness and a hierarchy argument

**Draft 0.1, 2026-10-27.** Independent workstream adjacent to the five-world assumption audit in [EvalMath PR #14](https://github.com/MoralityLabAI/EvalMath/pull/14). This note is a formal treatment of an interpretation of the claim that a creator may value intelligent struggle. It makes **no empirical claim about the existence, intentions, or preferences of God**. It does not select which complexity world is real.

**Research question.** Does a meaningful opportunity for bounded agents to learn, deliberate, and improve require asymptotically secure public-key cryptography? The answer depends on how "meaningful" is defined. Under the deliberately weak *functional agency witness* below, it does not: a constant-time learnable decision problem suffices. More ambitious meanings require explicit bridge axioms.

## 1. Distinguish the five worlds from the agency hypothesis

The Impagliazzo taxonomy separates five possibilities by hardness strength, including *Algorithmica* (`P = NP`), *Heuristica* (worst-case NP hardness without average-case NP hardness), *Pessiland* (average-case NP hardness without one-way functions), *Minicrypt* (one-way functions without public-key encryption) and *Cryptomania* (public-key encryption exists). These are *hypothetical* cases; our program neither proves them separately consistent nor rules them out. For careful provenance see [Impagliazzo five worlds via Sorbonne Université](https://qics.sorbonne-universite.fr/en/impact-quantum-computers-impagliazzos-five-worlds) and [Hirahara's survey](https://researchmap.jp/shuichi.hirahara/published_papers/40816859/attachment_file.pdf).

A polynomial-time attack on a particular curve breaks a concrete scheme under its security assumptions. It does not establish the universal statement that *all* public-key encryption is impossible. A proof of `P = NP` would exclude the standard asymptotic definition of Cryptomania; it would not erase time-bounded choice, noisy information, undecidable problems, or complexity beyond NP. Practical feasibility additionally depends on exponents, constants and available resources.

## 2. Exact functional agency witness (FAW-01)

The following is an intentionally narrow, falsifiable *operational* definition, not a definition of moral worth or consciousness. A functional agency witness has (a) available policies with different expected utility in a common environment; (b) a bounded, causally available information channel; (c) an independently scored policy whose expected utility improves after useful calibration; and (d) a finite budget choice with a measurable opportunity cost. "Meaningful" in a broader philosophical sense remains an external premise.

Let hidden channel polarity `theta` and the state `s` be independent, uniform bits. On any interaction the agent receives a signal `y = s XOR theta XOR e`, where `Pr(e = 0) = q` and `1/2 <= q <= 1`. A *labeled calibration item* shows `(s,y)`; a held-out item provides only `y`. Its state, polarity prior and noise law match calibration, but its noise is fresh. The agent learns `theta` by majority vote over `s_i XOR y_i`, choosing zero on a tie. It then predicts held-out `s_hat = y XOR theta_hat`. Scoring gives reward one when `s_hat = s` and zero otherwise. Sample acquisition costs `c` per labeled example.

Let `alpha_m(q)` be the probability that majority voting recovers `theta` from `m` calibration labels. For every nonnegative integer `m`,

\[
\alpha_m(q)=\sum_{k>m/2}\binom{m}{k}q^k(1-q)^{m-k}
+\tfrac12\mathbf 1_{2\mid m}\binom{m}{m/2}q^{m/2}(1-q)^{m/2}.
\]

**Claim A1, algebraic identity.** The fresh held-out probability of success is

\[
A_m(q)=(1-q)+(2q-1)\alpha_m(q),\quad A_0(q)=\tfrac12.
\]

*Proof.* Conditional on `theta_hat = theta`, the fresh signal is correct with probability `q`; conditional on a wrong inferred polarity, it is correct with probability `1-q`. Total probability yields the formula. For even `m`, a tied majority has equal prior likelihood under both polarities, so a deterministic zero tie-break succeeds with probability one half under the uniform prior. In this particular symmetric model the resulting tie term is exactly the displayed factor.

A full-information oracle that knows the polarity obtains `q` on future items, leaving unavoidable noise when `q < 1`. All mathematical work here concerns the synthetic declared distribution. It makes no claim about an actual AI evaluator.

**Claim A2, finite verified fixture.** At `q = 3/4`,

| Calibration labels | Held-out success | Improvement over zero labels |
|---:|---:|---:|
| 0 | 1/2 | 0 |
| 1 | 5/8 | 1/8 |
| 2 | 5/8 | 1/8 |
| 3 | 43/64 | 11/64 |
| 4 | 43/64 | 11/64 |
| 5 | 715/1024 | 203/1024 |

The finite program independently enumerates polarities, calibration noise, and fresh held-out noise to check the binomial formula. The train and held-out draws are independent. With a cost `c=1/32` per calibration label and a budget `m <= 5`, one label uniquely maximizes `A_m(q)-mc`, giving `19/32`; zero labels give `1/2`. This yields both a measurable advantage to information and a nontrivial finite choice concerning its cost. The program records all ties rather than inventing a unique choice.

The information-access negative control is also exact: a policy that memorizes the one labeled calibration item can score `1` on that reused item while its independent held-out success is `5/8`, a gap of `3/8`. That apparent training success has a different estimand from population learning.

Degenerate controls: when `q=1/2`, every budget obtains `1/2` held-out accuracy; when `q=1`, one label identifies the polarity exactly. Neither control licenses an interpretation of observed model learning.

**Claim A3, interpretive limit.** The FAW-01 fixture uses constant-size binary operations and exact finite probabilities. Its existence does not assume a one-way function, hardness of NP, or public-key encryption. Embedding it in the five *hypothetical* worlds gives the same payoff law. Hence, given this operational definition, the proposition "agency witness implies public-key encryption" has a simple counterexample. The argument says nothing about whether any of the five worlds is logically consistent, nor whether this limited operational witness suffices for the theological meaning of struggle.

## 3. Stronger computational challenge survives Algorithmica

**Claim H1, cited theorem application.** The deterministic time-hierarchy theorem yields `P` as a proper subset of `EXP`. Even if `P = NP`, there are decidable languages outside polynomial time. More specifically, for each fixed polynomial time budget `n^k` (with conventional machine-model and time-constructibility conditions), a decidable language can be diagonalized to exceed that budget while remaining in a larger deterministic time class. This is an *unconditional worst-case existence* claim. It supplies neither average-case hardness on a natural distribution, efficient solution verification, nor public-key cryptography. An accessible [proof and time-hierarchy derivation](https://introtcs.org/public/lec_11_running_time.html) appears in Barak's *Introduction to Theoretical Computer Science*.

A more ethically interesting notion of struggle needs an explicit family of resource-bounded learning environments with natural tasks, consequential rewards, adaptation and independent evaluation. Such a theorem is **open here**. FAW-01 establishes an elementary information-limited instance, and H1 identifies an independent complexity-theoretic source of difficulty. They are different evidence types.

## 4. Falsification ledger

| Observed result | What follows | What remains open |
|---|---|---|
| Prove `P = NP` | Rules out Cryptomania's standard asymptotic hardness premise | Whether bounded agency has moral meaning; practical exponents |
| Discover polynomial-time ECDLP for a named curve | Breaks the asymptotic ECDLP premise of the affected scheme | Existence of secure public-key encryption from another assumption |
| Demonstrate secure PKE from a named assumption | Conditional route to Cryptomania | Whether the assumption is true; creator's preference |
| Run `q=1/2` in FAW-01 | Zero feedback benefit, as the model predicts | Whether useful information exists in other environments |
| Observe real-agent gains on reused evaluations | Potential measurement artefact | True transfer until held-out evaluation confirms it |
| Reject the theological bridge "a good struggle requires PKE" | Revised philosophical hypothesis | Complexity world's actual identity |

A creator-preference hypothesis becomes mathematically discriminating only with explicit bridge assumptions connecting a utility over possible worlds to particular complexity statements. A broad claim that God enjoys struggle is consistent with every row of the world taxonomy. No cryptographic experiment can independently infer divine intentions.

## 5. Proof obligations and scope

- **Algebraic identity:** A1, by elementary total probability and finite binomial counting. Not Lean-formalized.
- **Finite verified example:** A2 and all boundary cases, exact rational tests and independently enumerated witness. No AI was run.
- **Synthetic mechanism:** A3, restricted to the FAW-01 operational definition.
- **Cited:** H1 (deterministic time hierarchy), not proved in this repository.
- **Open:** Natural-distribution hardness in the agency setting, principled mapping from functional to moral agency, theological bridge axioms, and any empirical world selection.

To reproduce from repository root:

```sh
PYTHONPATH=src python -m pytest -q tests/test_agency_worlds.py
PYTHONPATH=src python scripts/verify_agency_worlds.py --output /tmp/agency_worlds.json
python scripts/check_receipts.py --only agency_worlds
```

The committed receipt includes source hashes, rational values and twelve independently checked invariants. The verifier never overwrites an existing receipt. The repository's general `verify.yml` workflow runs this test file with the full test suite and the registered receipt checker; its status must be read separately from local results.

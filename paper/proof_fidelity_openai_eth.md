# Case study: OpenAI ETH preprint, manuscript versus Lean endpoint

*EvalMath external-source audit, 2026-10-27. Evidence level: pinned-source structural audit. This is a claim-fidelity assessment and does not constitute a new proof of ETH's failure or a fresh Lean kernel verification.*

## Provenance and reproduction

Source: [OpenAI, *The Exponential Time Hypothesis is False*, October 25, 2026](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf), on upstream commit [`7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`](https://github.com/openai/math/commit/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a). The audited sources are archived under `fixtures/external/openai_eth_20261025/`. Their original Git blob SHA-1 values and GitHub paths are pinned in `configs/openai_eth_fidelity.json`; the verifier recalculates Git's `blob <size>\0<content>` hash before reading a source. These copies are source snapshots, not material rewritten for this note.

Run `PYTHONPATH=src python scripts/verify_proof_fidelity_openai_eth.py` to inspect the crosswalk, or `python scripts/check_receipts.py --only openai_eth_fidelity` to compare its source-hashed receipt with the committed one. The tests include deliberate evidence promotion, hypothesis deletion, source tampering, and a missing space guarantee. This checker is offline and does not execute the upstream Lean modules. It checks that carefully chosen statements are present in authentic, pinned text; statement matching alone cannot establish that a mathematical proof is valid.

## The claim ladder

| Layer | Source and located statement | What is claimed | Evidence/fidelity |
|---|---|---|---|
| Headline | [`main_full_version.tex`, `\\title`](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex) | "The Exponential Time Hypothesis is False" | Title, shorthand for a mathematical consequence |
| Main manuscript | Theorem `thm:main` | Deterministic exact counting of assignments of every fixed-width `k`-CNF, `k >= 2`, `n >= 20`, general time `(n+m)^O_k(1) * 2^O_k(n log log n / sqrt(log n))`, polynomial space | Manuscript theorem and proof |
| Sharper sparse-input case | `thm:main` with fixed `D` and `m <= Dn`, proved in `quantitative-reduction.tex` | Time `(n+m)^O_{k,D}(1) * 2^O_{k,D}(n / sqrt(log n))` | Manuscript only, fixed-density condition retained |
| Supporting contraction result | [`quantitative-reduction.tex`, `thm:tensor-contraction`](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/quantitative-reduction.tex) | `2^O(s/sqrt(log s))` for bipartite Boolean tensor networks with bounded wires/degree and efficient local tensor entries over a specified truncated ring | Manuscript-only theorem; additional premises matter |
| Weaker manuscript path | `main_full_version.tex`, the `rho(n)` discussion | `rho(n) = n (log log n)^2 / sqrt(log n)` | Manuscript argument supporting the weaker exponent |
| Lean endpoint | [`SqrtLogSpace/Final.lean`, `exact_count_and_sat`](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean) | Existence of a fixed primitive machine, correct exact count, correct SAT decision, `runtimeScale(n)` bound and polynomial visited tape space **at every prefix** | Implemented Lean theorem in source; build and axiom output not independently replayed here |
| Comparator | [`ComparatorChallenges/SubexponentialSAT.lean`](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/ComparatorChallenges/SubexponentialSAT.lean) | The corresponding theorem *specification* contains `sorry` | Explicit specification placeholder; the actual proof is in `Final.lean` |
| Upstream formalization scope | [`lean/docs/378.md`](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/378.md) | Explicitly distinguishes the Lean `loglog^2` exponent from the manuscript's sharper `loglog` and sparse `1` bounds | Upstream documentation, consistent with file inspection |

The whitespace-normalized theorem signature of `exact_count_and_sat` matches its comparator specification exactly in these pinned files. This equality covers the written hypotheses and conclusion, independently of the proof term.

The Lean file also contains `exact_count_eth`, which transports the machine theorem to a bound in `n + F.card` with `rho(n)`. This is useful for connecting input encoding to the conventional parameterization. The Lean CNF type is a finite set of finite sets of literals on `Fin n`. It normalizes duplicate literals and clauses, preserving satisfaction counts over the declared variables. Matching this input model to every syntactic choice in the manuscript remains an explicit fidelity obligation.

## Implication, formal boundary, and the verification gap

For every fixed nonnegative integer `p`, `(log log n)^p / sqrt(log n) -> 0`. Thus any of the three stated scales, for sparse formulas with polynomial input overhead, would yield `2^o(n)` SAT on `n` variables. That is enough to refute ETH, which asserts a worst-case `2^Omega(n)` lower bound for 3-SAT; **it does not establish P = NP**. Exact #SAT counting is a strictly stronger *algorithmic task* than satisfiability, since positivity of the count decides SAT. The existence of a subexponential exact counter is the substantive result.

The formal Lean endpoint corresponds to the weaker exponent, and the sharper rates depend on the manuscript's tensor-contraction argument. Source inspection establishes that `Final.lean` contains a proof term for `exact_count_and_sat` and that its comparator file has an admitted goal. The former imports substantial dependencies; a complete independent kernel replay must rebuild their transitive closure and inspect the printed axioms. The comparator configuration permits `propext`, `Quot.sound`, and `Classical.choice` only, but this audit has read the configuration rather than executed the comparator. No inference about the truth of the tensor theorem is drawn from the successful source checks.

## Independent review targets

The mathematically highest-value audit is `quantitative-contraction.tex`'s **tapered Hermite recovery** (`lem:tapered-hermite`): check the valuation identity, truncation orders, powers-of-two precision loss, and reconstruction under the exact ring. The packing lemma's port-incidence construction and the recurrence turning a contraction on `M` wires into child networks with at most `M/8` wires are separate obligations. In the counting reduction, check that the clause network has `O_k(n+m)` edges, that variable-equality gadgets count each satisfying assignment once, and that a residue modulo `2^(n+1)` preserves an exact count at most `2^n`.

A finite exact check of the tapered-Hermite valuation identity and its lower bound covers **15,492** choices of `(a,u,M,t)` with `1 <= a <= 7`, `1 <= u <= a`, `u <= M <= u+5` and positive node multiplicity. The code calculates the valuation from the original product's factors and separately from the grouped-valuation expression, using rational arithmetic and the signed residue grid `{-2^a, ..., 2^a - 1}`. All enumerated cases agree. Evidence level: **finite verified example**.

An independent Lean audit should pin Mathlib and the Lean toolchain, run `lake build` on the upstream commit, replay the `#print axioms` commands, and compare exact theorem types after elaboration. There is a further trust boundary between validating a *theorem statement* and validating that it faithfully encodes an intended algorithm and its runtime cost model. A source-hashed receipt documents this distinction; it does not close the remaining proof obligations.

## Falsification cases

The checker rejects a changed archived blob, an invented Lean proof of the tensor exponent, promotion of the weak Lean bound to the manuscript's sharper rate, removal of the fixed-density hypothesis, disappearance of the explicit visited-space bound, and replacing the proof's final `exact hrun` with `sorry`. This is a finite set of structural adversarial tests. It is not an exhaustive audit of all mathematical derivations or of a complex external toolchain.

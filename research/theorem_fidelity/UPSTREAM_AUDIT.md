# Unique Games upstream statement audit (2026-10-27)

Upstream repository: https://github.com/openai/math
Observed main head: `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`.
For reproducible source reads, checkout that commit rather than a moving main branch.

Audited specification paths:
- `lean/docs/102.md`
- `lean/ComparatorChallenges/UniqueGamesTheorem.lean`

**Key distinction:** the comparator's theorem `OAI.UniqueGamesTheorem.theorem11` ends with `by sorry`. It is a *challenge statement*, not a kernel-checked proof certificate. The proof itself must be located and audited separately. Never count the comparator file as verification of the result.

Contract in the comparator:
- `BinaryGapReduction ε δ`, for fixed positive ε and δ strictly below 1/2.
- `alphabet : Nat`, `coordinates : Fin alphabet ≃ (Fin dimension → ZMod 2)`: alphabet fixed before the input.
- `construct : List Bool → Instance alphabet` together with `TM2ComputableInPolyTime`.
- Simple bipartite output and translation permutations.
- `completeness`: each satisfiable binary input has **some** labeling satisfying fraction at least 1-ε.
- `soundness`: for an unsatisfiable binary input **every** labeling satisfies fraction at most δ.

Mutation linkage:
| Fixture | Comparator declaration or field | Failure category |
|---|---|---|
| TF-01 | `BinaryGapReduction.soundness` | forall-labeling weakened to exists-labeling |
| TF-02 | `PermutationTable`, `translations` | arbitrary relation substituted for permutation |
| TF-03 | `completeness`, `soundness` | misplaced gap, thresholds or hypotheses |
| TF-04 | `BinaryLanguage.language` | different SAT source language |
| TF-05 | `alphabet` fixed in structure | input-dependent alphabet |
| TF-06 | `computation` | polynomial runtime dropped |

Limitations:
1. The local finite game checker permits parallel edges; upstream requires simple bipartite games. It therefore supplies minimal *semantic witnesses*, not instances of the target class.
2. A few finite examples cannot certify superpolynomial growth or alphabet nonuniformity across unbounded input sizes.
3. The provided Lean microexamples are independent logical illustrations. Upstream extraction, axiom auditing and full proof replay remain open.
4. The observed upstream head is a source pin. Do not equate a successfully fetched comparator with a verified theorem implementation.

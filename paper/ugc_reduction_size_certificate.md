# UGC-PT-01B: exact size ledger for the claimed UGC reduction

**Evidence level:** cited reduction formulas and a conditional symbolic deduction. No independent UGC soundness verification or extracted Håstad reduction exponent.

**Source pin:** `openai/math`, `preprints/The-Unique-Games-Theorem-September-23-2026/build/sections/06-finish.tex`, blob SHA `468dc7eacc1e769c34d9ddf2c117170d59b8e8a0`, read October 27, 2026. The published final proof provides more than an unspecified polynomial.

## Count the actual output

Write `M=N_E` for the number of positive occurrences after the weighted-parity and distinct-position steps. For each fixed completeness and soundness target, the construction chooses constants `k`, `t`, `tau>0`, and `s=ell*t` **before** seeing the input formula.

- The matrix-test game lists `h=C*M^k` occurrences for a fixed finite enumerator factor `C`; more conservatively, `h<=C*M^k`.
- Largest-remainder rounding uses `Q=ceil(h/tau)`, followed by four-edge subdivision. The resulting simple bipartite graph `B` has exactly `4Q` edges, at most `2h+3Q` vertices, and retains translation constraints.
- The final t-fold product `G=B^(tensor t)` has exactly `(4Q)^t` edges. Its alphabet is `F_2^(ell*t)`, fixed for these gap parameters.
- With a full permutation table per edge and binary endpoint IDs, the explicit encoded output has length `L=O(M^(k*t) log(M+2))`. The polynomial exponent in `M` is **k*t**, up to the endpoint-index logarithm. The original polynomial preprocessing determines the exponent in the 3SAT input size.

If the 3SAT-to-parity stage produces at most `C_p*n^a` occurrences from a sparse 3SAT instance of size `O(n)`, then

`L = O(n^(a*k*t) log(n+2))`.

For any fixed `eta>0`, this is `O(n^(a*k*t+eta))`. Assuming ETH and **assuming the entire claimed gap reduction is correct**, a uniform gap algorithm with running time `2^o(L^(1/(a*k*t+eta)))` would imply a `2^o(n)` sparse-3SAT algorithm, a contradiction. This statement concerns the explicit encoding length and uses ETH plus the sparsification lemma. The constant `a` has not been extracted from the cited parity reduction and is not invented here.

The more precise asymptotic expression (for positive finite parameters) is `2^o((L/log(L+2))^(1/(a*k*t)))`. It follows by monotonicity of `x/log(x+2)` above a fixed threshold and the size estimate, with small outputs handled by the trivial upper bound.

## Parameter-order and feasibility warnings

The manuscript's displayed sufficient repetition condition is

`(1 - 1/10,240,000)^t <= delta_0`,

with sufficient choice `t >= ceil(10,240,000*log(1/delta_0))`. The same section chooses `p_*`, `tau`, latent dimensions, and then a cube `k` exceeding additional thresholds. Thus the exponent `a*k*t` can be enormous. An ETH hardness transfer survives formally, while the implied finite-size numerical lower bound may carry very little practical force.

The overall reduction time could have a larger degree than the output-size exponent due to its exact rational arithmetic and key-canonicalization steps. A complete fine-grained reduction certificate must bound runtime as well as output size: `poly(n)+T_UGC(L)` needs to become `2^o(n)`. Any fixed polynomial overhead is harmless under ETH; uniform parameter dependence is the delicate issue.

## Audit obligations

1. Pin the exact 3SAT-to-weighted-parity enumerator and its occurrence bound `a`, with all bit-length assumptions.
2. Confirm the `C` factor covers each table, perturbation vector, positive noise outcome, and repeated occurrence.
3. Check the four-edge replacement exactly preserves binary-translation constraints, and its value identity `OPT(B)=1-(1-OPT(H'))/4`.
4. Verify `t`-fold edge tuples are encoded explicitly and remain simple bipartite, and that `2^(ell*t)` is held constant with respect to `n`.
5. Keep the output-bound certificate separate from the manuscript's soundness proof. An input/output count cannot validate a faulty gap promise.

**References:** [source finishing proof](https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/build/sections/06-finish.tex); [theorem introduction](https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/build/sections/00-introduction.tex); [separate fidelity PR #13](https://github.com/MoralityLabAI/EvalMath/pull/13).

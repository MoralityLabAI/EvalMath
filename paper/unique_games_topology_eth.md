# Unique Games × cohomology × ETH: a finite audit (UGC-PT-01)

**Evidence:** Algebraic identity (elementary, derived below); finite verified example (1001 small cases); cited (OpenAI's 2026 UGC claim, subject to external proof review). **No new hardness theorem is established by the census.**

## Game and cohomological dictionary

An edge occurrence `e=(u,v,c_e)` of an oriented graph requires `x_v = x_u + c_e` in the *fixed* alphabet `A=F_2^s`. The support of an edge-valued 1-cochain counts edges whose *entire s-bit vector* is nonzero; it never counts individual bad coordinates. Graph cochains are `C^0=A^V`, `C^1=A^E`, and the coboundary is `(dx)_e=x_v-x_u`. A graph has no 2-cells, so `H^1(G;A)=C^1/im(d)`. Isolates, multiedges, and loops are admitted by our finite oracle; the cited theorem uses simple bipartite graphs.

For every finite game with `m>0`, exactly:

`OPT(G) = 1 - min_{x in A^V} |supp(c-dx)|/m = 1 - ||[c]||_cosys / m`.

The class norm uses block-Hamming weight: `||[c]||_cosys = min_{b in im d} |supp(c-b)|`. This is an **algebraic identity**, valid for all finite graphs and finite abelian alphabet groups, not a bound requiring expansion. The zero-edge convention is `OPT=1`. In particular, `OPT=1` iff `[c]=0`. Thus exact satisfiability is decided by spanning-forest holonomy; approximating the norm can remain hard. For general permutation games the corresponding obstruction is nonabelian and cannot simply be identified with this abelian `H^1`.

Choose a spanning forest `T`, set its root potentials to zero, and transport shifts along its tree paths. Every tree shift becomes zero after a vertex gauge transformation. The residual on each chord is the cycle holonomy. The ordered chord residuals, for a fixed edge order and forest convention, determine the gauge class. Their number is `m-n+components`. They diagnose exact satisfiability, while the minimum block-Hamming representative determines the optimum.

An edge-disjoint collection of cycles with nonzero holonomy forces at least one failed edge per cycle. This yields a valid lower bound on `||[c]||_cosys`. The current verifier uses edge-disjoint **fundamental** cycles, hence only a potentially weaker bound. The cycle rank alone cannot determine `OPT`: frustrated `C4` and `C6` have the same rank 1 and values `3/4` and `5/6`.

## Reproducible experiments

Two separate oracles are cross-checked: (A) enumerate all vertex labelings, gauge-fixing one root in each connected component; (B) enumerate edge deletions in ascending cardinality, accepting a retained graph iff every fundamental cycle has zero holonomy. The full audit covers:

| Exhaustive family | Cases | Deletion-distance histogram |
| --- | ---: | --- |
| Oriented 4-cycle, alphabet `F_2^2`, all edge shifts | 256 | 0: 64, 1: 192 |
| `K_2,3`, alphabet `F_2^2`, every gauge class with tree edges zero | 16 | 0: 1, 1: 9, 2: 6 |
| All signed simple subgraphs of `K4`, alphabet `F_2`, each potential edge absent / 0 / 1 | 729 | Independently cross-checked (includes forests, isolated vertices) |

In the `K_2,3` example, set all spanning-tree shifts to zero and its two chord shifts to `(h_1,h_2)`. The class `(1,1)` needs one deletion, while `(1,2)` needs two, even though each has two nonzero fundamental holonomies. This falsifies the tempting rule that counting nonzero fundamental cycles equals the cosystolic norm.

```bash
PYTHONPATH=src python -m pytest -q tests/test_unique_games_topology.py
PYTHONPATH=src python scripts/verify_unique_games_topology.py --output /tmp/unique_games_topology.json
python scripts/check_receipts.py --only ugc_topology
```

The receipt stores counts, source SHA-256 hashes and exact logical checks. Tests also cover disconnected vertices, loops, repeated pairs, invalid shifts, and gauge equivalence.

## ETH: what a reduction transfers

The September 2026 *The Unique Games Theorem* manuscript states: for each fixed `epsilon,delta` in `(0,1/2)`, a deterministic polynomial-time reduction from 3SAT to explicit, unweighted, simple bipartite `F_2^s` translation games with YES value `>=1-epsilon` and NO value `<=delta`. The alphabet and polynomial exponent depend on these fixed errors. This is **cited manuscript content**, not an independent proof here. Its Lean statement / replay belongs to the separate EvalMath theorem-fidelity audit PR #13.

Assuming the manuscript reduction is correct, suppose sparse 3SAT with `n` variables and `O(n)` clauses maps to a game whose explicit encoded length `N` obeys `N <= C n^d`, uniformly in input size at fixed gap. Under ETH (using the sparsification lemma for sparse 3SAT), a uniform algorithm distinguishing these promised game values in `2^{o(N^{1/d})}` time would decide sparse 3SAT in `2^{o(n)}` time, contradicting ETH. Input representation and alphabet table sizes matter: the exponent `d` must be measured against **explicit encoding length**, not merely vertex count. This is a **conditional deduction**, distinct from any proved fine-grained hardness exponent. A polynomial-time reduction alone gives no ETH-implied `2^{Omega(N)}` statement.

Topology translates the same YES and NO conditions into a promise on cosystolic distance:

- YES: `||[c]||_cosys <= epsilon*m`;
- NO: `||[c]||_cosys >= (1-delta)*m`.

This reduction therefore claims hardness of distinguishing low and high block-Hamming weight in graph cohomology classes. The census demonstrates the dictionary on toy graphs; it does not certify gap amplification, parameter order, or the manuscript's soundness argument.

## Limits and next falsification targets

1. Extract and pin an explicit `N(n)` size certificate from the theorem's final reduction; check the encoding of every listed permutation and every weight-clearing step, with `s,epsilon,delta` fixed before `n` varies.
2. Compare cosystolic lower bounds obtained by fundamental-cycle packing with exact deletion distance on larger bipartite graphs. Look for adversarial configurations where the packing bound is weak.
3. Add a Lean proof of the block-Hamming identity and an executable certificate checker for a selected graph family. The current Python tests are finite evidence, not Lean formalization.
4. Keep the claim of a solved UGC tagged as **OpenAI's stated theorem**, pending independent validation of the complete Lean proof and correspondence. Audit overlap: https://github.com/MoralityLabAI/EvalMath/pull/13.

**Sources checked (October 27, 2026):**

- OpenAI, *The Unique Games Theorem*, 2026-09-23, introduction: https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/build/sections/00-introduction.tex
- OpenAI, *The Unique Games Theorem*, game construction: https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/build/sections/03-game.tex
- Lean scope and public source: https://github.com/openai/math/blob/main/lean/docs/102.md

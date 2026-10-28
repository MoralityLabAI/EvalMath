# Referee report, second pass: mathematical validity and semantic proof fidelity

**Subject.** OpenAI, *The Exponential Time Hypothesis is False* (October 25, 2026), as pinned at `openai/math@7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`; and MoralityLabAI/EvalMath PR #10 at head `898a0d1d8eb1cfc58a8a7af4153dd392fd03f84b`.
**Reviewer environment.** Sandbox with 2 cores, 7 GB, no route to the Lean release server or the Mathlib cache. Everything below is either source inspection, derivation, or exact rational arithmetic in Python. Nothing below is a kernel verification.
**Evidence classes used.** `K` kernel-verified (none in this report); `X` exact-arithmetic-verified by this reviewer; `D` derivation re-checked line by line; `S` source-inspected; `U` unverified.

---

## 0. Verdicts, kept separate

### 0.1 EvalMath PR #10 (source-fidelity audit) — merge-ready as what it is

The receipt is the verifier's output (one-shot Actions workflow, bot commit `f904d40`, microsecond timestamp, verifier key order, reproduces identically under `check_receipts`); all ten archived blobs match the upstream tree at the pinned commit; 27 checks pass; 25 of 26 targeted mutations are caught by the named check, the 26th being a sweep artifact (§5.3); every item of the first review is addressed except two residuals (§5.4, R1–R2), neither blocking. What the PR establishes is statement- and definition-level fidelity between the manuscript, the comparator challenge and the implementation's referents. It establishes nothing about the truth of the theorem, and says so.

### 0.2 OpenAI's ETH refutation — not established on evidence available to this reviewer; no error found

Three facts, stated in order of weight.

1. **No concrete mathematical error was found** in the components examined: the tapered-Hermite recovery lemma (exact, including sharpness of its own error model, §3), the mode expansion and the recursion identity that define the child networks (exact on random networks, §4.2–4.3), the packing lemma (derivation, §4.1), and the cost and space summation (derivation with the paper's constants, §4.4). The fixed-density reduction is verified by derivation (§4.6). The dense-case reduction depends on main-text lemmas I did not re-derive (§4.6).
2. **The formal statement is faithful.** The comparator challenge is a self-contained Lean file whose definitions encode "one fixed deterministic multitape machine per width `k` that exactly counts the satisfying assignments of a canonically encoded `k`-CNF in time `C(L+1)^d 2^{A·n(ln ln(n+16))²/√ln(n+16)}` with `S(L+1)^e` visited cells at every prefix" (§2.2). All 35 declarations the statement depends on are textually identical in the implementation modules (§2.3). The 3,977-file, 710,320-line closure contains no `sorry`, `axiom`, `native_decide`, `unsafe`, `partial def`, `implemented_by` or `extern` (§2.4). That theorem, if it holds, refutes ETH by a two-line argument (§2.6).
3. **The decisive obligation is external and checkable, and has not been met publicly:** an independent `lake build` of `OAI.Algorithms.SubexponentialSAT.Main` at the pinned commit, the printed axioms of `SqrtLogSpace.exact_count_and_sat` being a subset of `{propext, Quot.sound, Classical.choice}`, and a comparator run against `ComparatorChallenges/SubexponentialSAT`. The upstream repository carries no Lean CI; EvalMath's green Lean job builds EvalMath's own formalization. Until that replay exists, "ETH is false" rests on an unverified 710k-line artifact whose source looks clean. I would not accept the result on that basis, and I would not reject it either.

The sharper manuscript-only rates (`n log log n/√log n` general, `n/√log n` at fixed density) are not needed for the ETH consequence and are not formally verified anywhere; §4 is the review of their proof.

---

## 1. Setting and notation used below

Lean endpoint: `OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat` in `SqrtLogSpace/Final.lean` (blob `a69635a2`); comparator challenge `lean/ComparatorChallenges/SubexponentialSAT.lean` (blob `a8d5ff3a`), config (blob `d4cc9e70`). Manuscript `main_full_version.tex` (blob `f7af85e6`) with appendices `quantitative-reduction.tex` (`80389ac3`), `quantitative-contraction.tex` (`51ba54ef`), `quantitative-circuits.tex` (`e25def5e`). Line numbers refer to those blobs.

---

## 2. A — Lean semantic fidelity

### 2.1 What the comparator tool checks (S, from `leanprover/comparator` README)

Both challenge and solution are built and exported with `lean4export` inside a `landrun` sandbox; the tool checks that every declaration used in the statement of each listed theorem in the challenge environment is the *same declaration* in the solution environment (name, type, value), that the solution theorem's body uses only the permitted axioms, and then replays the solution environment through the Lean kernel. The README is explicit that the challenge file and its imports are trusted. So the comparator settles elaborated equivalence of referents; it does not settle whether the challenge means what the paper claims. That second question is the one a human must answer, and it is answered in §2.2.

### 2.2 Faithfulness of the challenge statement (D/S)

Walking the challenge file (`SubexponentialSAT.lean` ll. 1–220):

- **Formula and count** (ll. 13–51). `CNF V = Finset (Finset (Literal V))`, `Literal = ⟨variable, positive⟩`, `Literal.eval a l = (a l.variable == l.positive)`, `Clause.eval = decide (∃ l ∈ C, …)`, `CNF.eval = decide (∀ C ∈ F, …)`, `count F = (univ.filter (F.eval · = true)).card` over `Fin n → Bool`. Duplicate literals and clauses are normalized by the `Finset` structure, which does not change the count; an empty clause gives 0, an empty formula gives `2^n`. `WidthAtMost k F := ∀ C ∈ F, C.card ≤ k`. Faithful.
- **Input encoding** (ll. 53–81). `encodeNat n = replicate n true ++ [false]` (unary); literal codes `2v + sign`, each in unary; clauses sorted, formula sorted, framed. Length `L = O(k·m·n)`. Unary is wasteful but harmless because the time bound carries a `(L+1)^d` factor; it does not inflate the exponent, which is a function of `n` alone.
- **Machine model** (ll. 83–128). A `PrimitiveMachine` has finitely many states and tapes, a `scan` function choosing the tape read in each state, and `transition : state → Option Bool → Bool ⊕ (state × TM0.Stmt (Option Bool))`: one step reads one symbol and either halts with an answer or changes state and performs one move or one write on that tape. `step` is a function, so the machine is deterministic; `init` places the input on `inputTape`, blanks elsewhere. `Trace step time init final` is the standard inductive `time`-step relation. This is a multitape Turing machine with a ternary alphabet and unit-cost steps; nothing in it allows more than constant work per step.
- **Time** (ll. 130–141). `runtimeScale n = n·(ln ln(n+16))²/√ln(n+16)`, `runtimeBound C A d L n = C·(L+1)^d·2^{A·runtimeScale n}`. The `+16` keeps the double logarithm positive; the base of the logarithm only changes `A`.
- **Space** (ll. 145–182). `LocatedCfg` carries head position and the visited interval per tape; `monitor` updates them from the executed action exactly as `step` moves the head; `visitedSpace = Σ_tapes (upper − lower + 1)`. The statement requires `visitedSpace ≤ S(L+1)^e` for **every prefix** of the trace, which is the right notion of polynomial space.
- **Quantifier order and non-vacuity** (ll. 194–218). `∃ machine, countTape, answerTape, C A S d e, positivity, ∀ n F, WidthAtMost k F → ∃ time final, Trace … ∧ final.tapes countTape = count in binary ∧ final.tapes answerTape = [decide (0 < count)] ∧ final.state = Sum.inl (decide (0 < count)) ∧ toNat (countWord …) = count ∧ length ≤ n+1 ∧ time ≤ runtimeBound … ∧ (∀ prefix, visitedSpace ≤ …)`. The machine and constants are chosen before `n` and `F`; the halting state carries the SAT answer; a halted state has `step = none`, so the trace cannot be extended. Nothing here is satisfiable trivially.

Conclusion: the challenge statement is a faithful formalization of the manuscript's exact-counting claim at the `(log log n)²` scale, for canonically encoded inputs. The only "normalization" is the `Finset` representation, which is semantically inert.

### 2.3 Declaration-by-declaration comparison (S; `compare_declarations.py`)

The challenge statement depends on 35 declarations. For each, the implementation module defining the same fully-qualified name was located in the sparse checkout of `lean/OAI/Algorithms/SubexponentialSAT` at the pinned commit and its comment-stripped, whitespace-normalized text compared:

| result | count | names |
|---|---|---|
| identical | 33 | `BinaryArithmetic.{bitVal,toNat}`, `SAT.{Assignment,Literal,Clause,CNF,Literal.eval,Clause.eval,CNF.eval,WidthAtMost,satisfyingAssignments,count}`, `Encoding.{encodeNat,frame,encodeList,literalCode,clauseNumbers,cnfNumbers,encodeCNFBody,encodeCNF,formulaBitLength}`, `Computation.{Trace,PrimitiveMachine,PrimitiveMachine.Cfg,.step,.init}`, `SqrtLogSpace.{countWord,LocatedCfg,locatedInit,headDisplacement,LocatedCfg.monitor,locatedStep,visitedSpace}` |
| differ by modifier only | 2 | `SqrtLog.Statement.runtimeScale`, `.runtimeBound`: `noncomputable def` in the challenge, `def` inside a `noncomputable section` in `SqrtLog/StatementScale.lean` |
| missing | 0 | — |

Surrounding context also matches: `SAT.lean` declares `universe u`, `variable {V : Type u}`, `[DecidableEq V]`, and `[Fintype V]` inside `section Finite`, in the same order and scope as the challenge; both environments import all of Mathlib (`LeanCompat.lean` begins `import Mathlib`). `Main.lean` imports `SqrtLogSpace.Final`, so the config's `solution_module` reaches the endpoint. What source text cannot settle: whether instance resolution and section-variable inclusion elaborate identically in both files. Both are determined by the same Lean version and the same imported instances, so divergence would be surprising, but only the comparator's export comparison settles it.

### 2.4 Closure scan (S)

`lean/OAI/Algorithms/SubexponentialSAT` at the pinned commit (tree `959444ea`): 3,977 `.lean` files, 710,320 lines. Occurrences as declaration keywords or tactics: `sorry` 0, `admit` 0 (six English prose hits in doc comments), `axiom` 0, `native_decide` 0, `implemented_by` 0, `extern` 0, `unsafe` 0, `partial def` 0, `set_option maxHeartbeats/maxRecDepth` 0. `opaque` as a declaration: 3 (`queryRecovery`, `rawRecovery`, `fixedRecovery` in `SqrtLog/LeafProgramPrepared*`), each subtype-valued with an explicit `:= by …` body, i.e. sealed proof-carrying constructions that add no axioms. Imports outside Mathlib and the project: `Lean.Elab.Tactic.Omega` only. Seventeen files carry `#print axioms` commands. A scan is not a build: it rules out the visible escape hatches, not elaboration failure.

### 2.5 What is not established, and why not here (U)

Compilation of the closure, kernel acceptance, the actual `#print axioms` output, and a comparator pass. The upstream repository's only workflow is `lock-prs.yml`; there is no public build log. The toolchain is `leanprover/lean4:v4.34.1` with Mathlib `d13f23b7` and some thirty further Git dependencies with compatibility patches; this sandbox cannot reach `releases.lean-lang.org` or the Mathlib cache, and a from-source Mathlib build on two cores is a multi-day job, so the replay was not attempted rather than attempted and failed. This is the single obligation on which acceptance turns.

### 2.6 How the formal theorem would refute ETH (D)

For fixed `k = 3`: a 3-CNF on `n` variables has at most `(2n)³` distinct clauses after deduplication, so `L = O(n⁴)` and `(L+1)^d = 2^{O(log n)}`; `runtimeScale(n)/n = (ln ln(n+16))²/√ln(n+16) → 0`; hence time `= 2^{o(n)}` for 3-SAT, contradicting ETH's `2^{δn}` lower bound. Exact counting is stronger than deciding, so the theorem as stated suffices. It does not bear on `P = NP`.

---

## 3. B — The tapered-Hermite recovery lemma (`quantitative-contraction.tex` ll. 244–336)

### 3.1 The formula (D)

With nodes `t ≠ 0`, multiplicities `q_t = h·max(0, u − v₂(t))`, `E_t(T) = Π_{q≠0,t} ((T−q)/(t−q))^{q_q}`, and `Σ_t q_t > deg F`, the Chinese-remainder form of Hermite interpolation gives `F = Σ_t E_t·G_t` exactly, where `G_t` is the Taylor truncation of `F/E_t` at `t` below order `q_t`; in the local coordinate `z = (T−t)/α` this is eq. `tensor-hermite-origin`, evaluated at `z = −t/α`. `Σ_{t≠0} q_t ≥ L·h·u ≥ 3ML > M(2L−1) ≥ deg F` holds because `h = ⌈3M/u⌉` and `S` has `L` odd points. Each factor `1 + αz/(t−q)` has `α/(t−q) = 2^{a+1}/(t−q) ∈ 2ℤ_(2)` since `v₂(t−q) ≤ a`, so its reciprocal series is 2-integral and the truncated quotient loses no precision, as claimed at l. 297.

### 3.2 The error model (D)

The only inexactness is that `G_t`'s coefficients `g_{t,j}` are known modulo `2^{p_t}`. A perturbation `δ ∈ 2^{p_t}ℤ_(2)` of `g_{t,j}` moves the reconstruction by `E_t(0)·δ·(−t/α)^j`, of valuation `≥ p_t + v₂(E_t(0)) − (a+1)j`. The lemma therefore holds exactly when, for every node and every `j < q_t`,

```
p_t ≥ p − v₂(E_t(0)) + (a+1)(q_t − 1).                                      (R)
```

### 3.3 The budget suffices for every admissible parameter choice (D + X)

The paper's budget is `p_t = p + 8hD_t + 8M(a+1)`. Using its two inputs — `−v₂(E_t(0)) ≤ 6D_t h` (eq. `tensor-hermite-loss`; verified on 129,258 cells earlier, and a clean convergent sum `Σ j²/2^j = 6`) and `q_t ≤ h·u ≤ 4M` (which needs `u ≤ M`, a hypothesis of the lemma and a consequence of eq. `tensor-parameter-bounds`) — the slack is

```
8hD_t + 8M(a+1) − [6D_t h + (a+1)(4M − 1)]  =  2hD_t + 4M(a+1) + (a+1)  >  0 .
```

Exact computation (`attack_hermite.py`, Part 1): over all 18,074 admissible `(a,u,M,t)` cells with `1 ≤ a ≤ 7`, `1 ≤ u ≤ a`, `u ≤ M ≤ u+6`, `q_t > 0`, computing `v₂(E_t(0))` from the product itself, the minimum slack of (R) against the paper's budget is **57 bits**, at `(a,u,M,t) = (1,1,1,−1)`.

### 3.4 End-to-end recovery with worst-case jets (X)

`attack_hermite.py`, Part 2, over `a ∈ {1,2,3}`, `u ≤ a`, `M ∈ {u, u+1, u+2}`, `p ∈ {1,3,7}`, with random integer `F` of degree `M(2L−1)` and every jet coefficient replaced by a lift differing from the true value by `2^{p_t}·(odd)`:

| budget used for `p_t` | correct mod `2^p` |
|---|---|
| the paper's, `p + 8hD_t + 8M(a+1)` | 54 / 54 |
| the exact requirement (R) | 54 / 54 |
| (R) minus one bit at the binding node, single perturbation of the binding coefficient | **0 / 12 correct** — error valuation exactly `p−1` in every case |

The last row shows that (R) is attained, i.e. the error model is sharp and the slack in §3.3 is real slack, not an artefact of a loose bound. (A first version of that control perturbed every coefficient at once and saw no failures: the symmetric nodes `t, −t` carry equal valuations and their perturbations cancel one bit. The single-coefficient control is the correct one.)

### 3.5 Denominators and reconstruction (D)

`E_t(0) = Π_{q≠0,t}(−q/(t−q))^{q_q}` is rational with 2-adic part bounded by §3.3 and an odd part that is a unit; `(−t/α)^j` contributes `2^{−(a+1)j}`; the reciprocal series has no 2-power denominators (§3.1). The sum differs from the integral `F(0)` by an element of `2^pA`, so it is integral and reduces correctly (l. 322).

### 3.6 Preserved failed attempt

My first implementation wrote `E_t(0)` as `Π(q/(t−q))^{q_q}`, dropping the sign of `−q`. The valuation identity is blind to this; the exact reconstruction is not: every case with odd `h` failed. This is recorded because it is evidence for the review method: the finite valuation grid certifies one equation of the proof, and an exact end-to-end reconstruction is what certifies the lemma.

### 3.7 Not verified

The interpolation of `F(t+αz)` from `M(2L−1)+1 < s⁴` evaluations at binary-coordinate lifts over `O = ℤ_(2)[U]/(f)` (standard Lagrange over a ring with unit node differences; not executed), and multi-level composition of recovery with the recursion identity (argued by induction in §4.3, executed for one level only).

---

## 4. C — The tensor-contraction bound (`quantitative-contraction.tex`; theorem at `quantitative-reduction.tex` ll. 26–49)

### 4.1 Packing into packets (Lemma `tensor-packets`, ll. 114–171) (D)

`E Σ_γ (X_γ − M/D_arr)² = Σ_γ Var X_γ = Σ_{(e,e')} Cov(1[e→γ],1[e'→γ])` summed over `γ`: pairs with disjoint endpoints contribute 0, and each of the at most `2MΔ` ordered pairs sharing an endpoint (including `e = e'`) contributes at most their label-agreement probability `≤ 1`. Hence some labeling has every load `≤ M/D_arr + √(2MΔ)`; conditional expectation makes it constructive in polynomial time. Padding to a multiple of `L` gives `H_pad ≤ M/D_arr + √(2MΔ) + L ≤ 3M/D_arr` exactly when `M ≥ 2D_arr²Δ` and `M ≥ LD_arr` (eq. `tensor-packing-conditions`); with `L ≤ s^{4ε}`, `D_arr = 64^{2a} ≤ s^{48ε}`, `Δ = ⌈s^{9/10}⌉`, `ε = 2^{−17}`, and `M > H = s/⌊√λ⌋`, both hold for large `s`. Packets: `H_pad·D_arr/L ≤ 3M/L`; a packet draws `2^{a−a'}` slots from each of the `2^{a'}` orientations of one unordered-pair class, which is possible because `L | H_pad`; bit `i` of the slot number then encodes the orientation in coordinate `i`, which is exactly what §4.2 uses. Ports per symbol per coordinate per side `≤ H_pad D_arr/r ≤ 3M/r`, so a child has `≤ 6M/r = 3M/32 < M/8` edges and a packet vertex `≤ 2L ≤ Δ` ports. Verified.

### 4.2 Mode expansion (eq. `tensor-mode-expansion`, ll. 384–431) (D + X)

Premise: for a row `x` and a column tile `y₀` in different groups (equal `i`-th bits), `v₂(t − y₀ + x) ≤ i`; proof: `t ≡ 2^i (mod 2^{i+1})`, so `t − y₀ + x ≡ 0 (mod 2^{i+1})` would force `x − y₀ ≡ 2^i`, i.e. different `i`-th bits. `αζ` has valuation `≥ a+1 > i`, so the valuation is unchanged at `T = t + αζ`; the geometric series in `2^{i+1}j/(T − y₀ + x)` has ratio of valuation `≥ 1`, and the leading factor `C(T)/(C'(0)(T−y₀+x))` has valuation `≥ a+1−i ≥ 1` because `v₂(C(T)/C'(0)) = v₂(αζ) ≥ a+1` by translation invariance of the difference counts. So the coefficient of the weight-`(b+1)` mode is divisible by `2^{b+1}` and the remainder by `2^{p_t}`.

Exact test (`attack_recursion.py`, `check_mode_expansion`): for every crossing `(x,y)` of every random packet in every instance of §4.3, the premise held, each coefficient had valuation `≥ b+1`, and `v₂(W_xy(T) − Σ_{b<p_t−1} c_{x,(y₀,b)} j^b)` was `≥ p_t` (observed minima 7 at `p_t = 5`, 8 at `p_t = 6`, or exact equality).

### 4.3 Child networks and the recursion identity (eq. `tensor-recursion-identity`, ll. 484–529) (D + X)

Derivation: expanding `Π_x l_{Y_x}(local_x + Σ_Z c_{x,Z} Z)` as a polynomial in the modes, the coefficient of `Z^β` is divisible by `2^{Σ w_Z β_Z}` and factors over `(packet, target group)` because modes targeted at different `(packet, group)` pairs are distinct variables; substituting `Z = L_Z(X)`, which depends only on the source group's column bits, every summand of `F(T)` becomes a product over groups of a function of that group's port bits; summing the independent bits group by group gives `Π_g Z_{g,β}`, where `Z_{g,β}` is the contraction of the stated child. Composition across depth is sound by induction: the child is needed modulo `2^{p_t}`, the child's own `F'` is defined from any lifts of its entries and satisfies `F'(0) ≡ Z_{g,β} (mod 2^{p_t})`, and the child's recovery (§3) returns `F'(0)` modulo its own `p`, which is `p_t`.

Exact test (`attack_recursion.py`): random bipartite networks given as 1–3 packets with random real slots, random symbol pairs over 2–3 symbols (equal pairs allowed), vertices owning 1–3 slots of one group and spanning packets, random integer tensors; `F(t+αζ)` computed by brute force over all Boolean port bits and compared modulo `2^{p_t}` with `Σ_β Π_g Z_{g,β}` built from the paper's definitions (including the rules for empty target rows and empty source tiles). Coverage: `a ∈ {1,2,3}`, nodes with `v₂(t) ∈ {0,1,2}` (two, four and eight column tiles), `ζ ∈ {−2,−1,0,1,3}` including `ζ = 0` (the node itself), `p_t ∈ {4,…,8}`, 1–3 packets, 1–3 groups, up to 48 modes and 1,365 exponent tuples per instance, residues both zero and nonzero (e.g. 29, 52, 62, 64). Result: **68 of 68 instances agree modulo `2^{p_t}`**, with 0 mismatches (seed 1: 28, seed 2: 28, reduced `a=3` set: 6, higher-precision set: 6; logs attached). (Preserved: an early harness version derived the group set from vertices rather than from packet symbol pairs and so omitted the factor `Z_{g,β} = 0` of a group with no real ports but a positive targeted exponent; the two resulting mismatches disappeared once the paper's rule was implemented. The identity itself was never contradicted.)

### 4.4 Cost summation with the paper's constants (D)

- Parameters: `λ = ⌈log₂ s⌉`, `ε = 2^{−17}`, `u_d = ⌊ελ/2^d⌋`, `a_d = 2Σ_{j≤d}u_j ≤ 4ελ`, `L = 2^{a_d} ≤ s^{4ε}`, `D_arr = 64^{2a_d}`, leaf threshold `H = ⌈s/⌊√λ⌋⌉`, `r = 64`, `Δ = ⌈s^{9/10}⌉`.
- Depth: children have `≤ 3M/32 < M/8` edges, so `M_d ≤ Cs·8^{−d}` and active depth `d ≤ log₈(C√λ) = (log₂λ)/6 + O(1)`; then `u_d ≥ ελ/2^{d} = Ω(λ^{5/6}) ≥ λ^{4/5}` for large `λ`.
- Precision (eq. `tensor-precision-bound`): along a path the increments are `8hD_t + 8M(a+1) ≤ 32Cs·2^{a_{d−1}}/u + 8Cs(4ελ+1)`, summed over `O(log λ)` depths: `p ≤ sλ^{O(1)}2^{a_{d−1}}`. At an active node `i = v₂(t) < u_d`, so `D_t = 2^{a_d − i} ≥ 2^{a_{d−1} + u_d + 1}`; with `M > s/√λ` this gives `p/D_t ≤ M·λ^{O(1)}/2^{u_d} ≤ M/u_d` once `2^{u_d} ≥ u_d λ^{O(1)}`, and `8M(a+1) ≤ MD_t/u_d` once `(a+1)u_d ≤ 2^{a_{d−1}+u_d+1}`. Hence `p_t = O(MD_t/u)` for every active node.
- Mode count: modes of weight `w` number `≤ (3M/L)·2^{i+1} = 6M/D_t`; tuples with `Σ w β < p_t` number `≤ exp(θp_t + (6M/D_t)(π²/6)/θ)`, and `θ = √(M/(D_t p_t))` gives `exp(O(√(Mp_t/D_t))) = exp(O(M/√u))`.
- Branching per call: `s^{O(1)}·exp(O(M_d/√u_d)) = s^{O(1)}·exp(O((s/√λ)(√2/8)^d))`; product over depths `= exp(O(s/√λ) + O(λ log λ))`.
- Leaf: `2^H` assignments times polynomially many entry evaluations at `≤ 2^{As^{9/10}}` each: `exp(O(s/√λ) + O(s^{9/10})) = exp(O(s/√λ))` since `s^{9/10} = o(s/√log s)`.
- Per-call work besides children: Lagrange over `< s⁴` points, Hermite recovery, packing by conditional expectation, packet-tensor entries at `exp(O(L log s)) ≤ exp(O(s^{4ε} log s)) ≪ 2^{s^{9/10}}`: polynomial times the entry budget.
- Space: depth-first, `O(log λ)` stack levels, polynomially many retained descriptions, no tables of size `2^{2L}` (which would be superpolynomial) — entries are recomputed from descriptions, and old descriptions are shared by reference so entry routines do not compose with depth.

Each inequality was re-derived; none failed. Total `(s+𝓛)^{O(1)}·2^{O(s/√log s)}` time and `(s+𝓛)^{O(1)}` space follows.

### 4.5 Implicit tensor entries within budget (D)

A packet-vertex entry is the coefficient of a prescribed monomial in a product of at most `L` affine forms, each with `≤ L` local terms and `≤ 2^i·(p_t−1)` mode terms, times powers `L_Z(X)^{β_Z}` by repeated squaring in `A_{p_t}`: full expansion has `poly(s)^L = exp(O(L log s))` terms, polynomial space. Retained tensors are evaluated from their creation-time descriptions and canonically lifted; packet tensors keep their creation-time representatives. This satisfies the theorem's uniform entry hypothesis for the children with room to spare.

### 4.6 The reductions (D / U)

- Fixed density (`quantitative-reduction.tex` ll. 67–98): clause tensors with one port per distinct variable, equality trees for repeated variables, subdivision of every edge by a binary equality tensor to make the network bipartite, `O_k(n+m)` edges, degree `≤ max{k,3}`, ring `ℤ/2^{n+1}` with `ℓ = 1`, `2^u` for unused variables, residue determines `#F ≤ 2^n`. Verified.
- Arbitrary density (ll. 108–361): sparsification tree with `2^{O(n/√λ)}` leaves, greedy parity hashes, idempotent lift in `(ℤ/2^{n+1})[V]/(V^{n+1})`, monomial indexing with `M ≤ J² + K log₂(e(N+K)/K) = O(nν)` wires (the `log₂` is `O(ν)` because `N ≤ nλ^{O(1)}` and `K = Θ(n)`), degree `n^{3/4}λ^{O(1)} ≤ s^{9/10}`, entries in `2^{λ^{O(1)}}`. The arithmetic I checked is consistent; this part depends on `lem:sparsify`, `lem:sparse-checks`, `lem:greedy-hashes`, `lem:total-order`, `lem:rational-idempotent` and eq. `hash-query` in the main text, which I did not re-derive. The weaker `(log log n)²` path, which the Lean formalizes, shares this machinery, so a successful kernel replay would verify those lemmas in the form the Lean uses, not in the sharper path's use.

### 4.7 The weakest inference

In my ranking, for the implication `T(s) = poly(s+𝓛)·2^{O(s/√log s)}`:

1. **The second assertion of eq. `tensor-precision-bound`, `p_t = O_C(MD_t/u)`** (ll. 348–368). It is the one place where the taper (`q` changes by `h` per level), the cumulative choice of `a_d` (the inherited precision must be absorbed by the extra `2^{u}` in `D_t`), and the leaf threshold meet; it is correct, but only for `s` so large that `ελ/2^d ≥ λ^{4/5}` at depth `(log₂λ)/6`, i.e. `λ ≳ 2^{510}`, `s ≳ 2^{2^{510}}`. The theorem is a purely asymptotic statement with no instantiable case; that is admissible for refuting ETH, which is itself asymptotic, but it means the bound can never be checked computationally and every constant in the proof is load-bearing only in the limit. Everything else in §4.4 is a clean inequality once this one holds.
2. **The mode-count estimate's dependence on the packing lemma's `6M/D_t` multiplicity**, which in turn depends on property (2) of the packing lemma (fixed symbol pair per coordinate, orientation by slot bit). Verified, but it is the structural fact that makes the child networks factor at all.
3. **The dense reduction's reliance on main-text lemmas** (§4.6), which this review did not cover.

No concrete error was found in §4.

---

## 5. D — EvalMath PR #10 at `898a0d1` (S + X)

### 5.1 Receipt authenticity and reproducibility

`output/proof_fidelity/openai_eth_v0_2.json` was written by `scripts/verify_proof_fidelity_openai_eth.py` under the one-shot workflow `.github/workflows/regenerate-eth-fidelity.yml` (added in `ff2639b`, removed in `898a0d1`), committed by `github-actions[bot]` as `f904d40` at 00:22:50Z, four seconds after the recorded `generated_at_utc` `2026-10-27T00:22:46.035268+00:00`; the key order is the verifier's. At `898a0d1`, `check_receipts.py --only openai_eth_fidelity` reports `27 all true; sources 5 match; regenerates identically`, and the 15 targeted tests pass. Authentic and reproducible.

### 5.2 Archive

All ten `git_blob_sha` values equal `git hash-object` of the archived file and the tree entry at `openai/math@7ef5c0cc` for the stated upstream path (`manuscript`, `tensor_reduction`, `tensor_contraction`, `lean_final`, `lean_comparator`, `lean_config`, `lean_scope`, `lean_scale`, `lean_asymptotics`, `circuits_appendix`).

### 5.3 Mutation sensitivity (`mutation_sweep.py`)

One semantically meaningful mutation per text check, 26 in all: 25 caught by the named check; a comment-only edit to the comparator is (correctly) not flagged. The one "not caught" case replaced the first occurrence of `visitedSpace intermediate` in `Final.lean`, which lies in the internal lemma `compiled_exact_count_and_sat`, not in the audited endpoint; the endpoint's own occurrence was untouched, so the check was right to pass. The PR's own test replaces all occurrences and fails as intended.

### 5.4 Status of the first review's findings

| item | status |
|---|---|
| exponent scale read only from prose | fixed: `comparator_runtime_scale_definition` compares the challenge's `runtimeScale`/`runtimeBound` text with `SqrtLog/StatementScale.lean` and asserts the `(ln ln(n+16))²/√ln(n+16)` form; `lean_rho_scale_definition` pins `Asymptotics.rho` |
| text-vs-meaning boundary unstated | fixed: receipt carries `comparison_kind: syntactic_statement_and_printed_definition_text; elaborated_type_not_checked` and an open obligation to run the upstream comparator |
| three unfalsifiable checks | removed (20 + 7 = 27) |
| hand-patched receipt | replaced by verifier output (§5.1) |
| `quantitative-circuits.tex` not archived | archived, with `circuits_appendix_outside_main_proof` |
| duplicated manifest loop | consolidated |
| sparse-formula wording | adjusted |

**Residuals.** R1: closure of the archive under the manuscript's `\input` graph is now true (all three inputs archived) but not enforced by a check; a two-line `manuscript_input_closure_archived` would make it one. R2: the crosswalk should say in one sentence that `Asymptotics.rho` (base-2 logs, no shift) and the challenge's `runtimeScale` (natural logs, `+16`) agree up to the constant `A` and for all `n`; both are correctly labelled `loglog_squared`. R3 (optional, the one addition I would make): a closure-scan receipt — pin the tree SHA `959444ea…` of `lean/OAI/Algorithms/SubexponentialSAT` and `179f2547…` of `lean/ComparatorChallenges` at the commit, record file and line counts and the zero counts of §2.4, and check that the challenge file imports only `Mathlib`, since self-containment is what makes the definition pins meaningful. None of these should delay the merge.

### 5.5 What each layer actually claims

| layer | claim | evidence class |
|---|---|---|
| manuscript headline | ETH is false | title |
| manuscript `thm:main`, general | exact count in `(n+m)^{O_k(1)} 2^{O_k(n log log n/√log n)}`, poly space | manuscript only (§4, consistent, dense reduction not re-derived) |
| manuscript `thm:main`, `m ≤ Dn` | `2^{O_{k,D}(n/√log n)}` | manuscript only (§4 + fixed-density reduction verified) |
| Lean `exact_count_and_sat` / comparator | exact count, canonical encoding, `2^{A·n(ln ln(n+16))²/√ln(n+16)}·C(L+1)^d`, poly visited space at every prefix | faithful statement (§2.2); referents identical (§2.3); closure clean (§2.4); **compilation, axioms and comparator pass unverified** (§2.5) |
| EvalMath PR #10 | the above layers are the pinned texts and the labels match the texts | verified (§5.1–5.3) |

The gap that matters is between the fourth row's "faithful, clean source" and "kernel-accepted". EvalMath states it as an open obligation; it is the right statement.

---

## 6. Reproduction

All scripts are standard-library Python with exact `Fraction` arithmetic; no floating point enters any decision.

```
# A: declaration comparison against the sparse checkout of openai/math@7ef5c0cc (lean/ subtree)
python3 -I compare_declarations.py <checkout>/lean            # expect same=33 differ=2 (modifier only) missing=0

# B: Hermite budget slack, corrupted-jet recovery, sharpness control
python3 -I attack_hermite.py 7                                 # expect min slack 57; 54/54; 54/54; then the sharpness control in the transcript

# C: mode expansion and recursion identity on random networks (two seeds; logs attached)
python3 -u -I attack_recursion.py 1 > recursion_run1.log
python3 -u -I attack_recursion.py 2 > recursion_run2b.log

# D: mutation sweep against the pinned EvalMath head
python3 mutation_sweep.py <EvalMath checkout at 898a0d1>       # expect 25/26 caught, comment control passes
```

Logs `recursion_run1.log`, `recursion_run2b.log` and the sharpness-control transcript are attached. The one run that mattered and could not be done is the Lean replay (§2.5); the commands for it are in `lean/ComparatorChallenges/README.md` upstream.
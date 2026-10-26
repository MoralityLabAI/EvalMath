# Research priority: what in EvalMath is worth a major project

Referee: Claude Fable 5.1, 2026-10-26. Companion to `FABLE_REFEREE_REPORT.md`; the numbers cited
are from `reviews/checks/outputs/`. Each item carries an acceptance criterion and a falsifying
search; the ranking weighs mathematical significance, tractability, experimental relevance and
expected value, in that order of weight where they conflict.

## 0. The problem the audit raises: the divergence budget of a perturbative loop

The repository's cleanest quantitative statement is "selection inside a divergence budget": one
best-of-K step costs at most λ_K = ln K − (K−1)/K nats, and Theorem B′ (report, G1) extends that to any
selection rule. The audit found that the same budget fails for the one chain in the repository that
resembles a policy update. In the §5 mutation chain (candidates copy the incumbent item by item and
redraw with probability q), the exact KL of the reported count from Bin(n, p) is 1.54, 2.66, 3.91 at
G = 5, 10, 20 for q = ½ (n = 8, K = 2) against the i.i.d. budget λ_{GK+1} = 1.49, 2.09, 2.74, and
4.09 against 2.74 at q = ¼; the record-level KL is larger by data processing. It stayed below the
additive G·λ_{K+1} on every cell computed.

**Problem P\*.** Let a loop keep a record X_g, propose K candidates from a p₀-stationary Markov
kernel Q(X_{g−1}, ·) (Q = p₀ ⊗ 1 is the i.i.d. case), and keep one of {X_{g−1}, Z₁, …, Z_K} by any
rule. Find the sharp bound on KL(law(X_G) ‖ p₀) as a function of (G, K, Q).

- *Conjecture P\*.1 (additive budget).* KL(law(X_G) ‖ p₀) ≤ G·λ_{K+1} for every p₀-stationary Q.
  Evidence: holds on every cell of `check_mutation_chain_kl.py`; the chain rule gives
  KL(law(X_G)‖p₀) ≤ Σ_g E[KL(law(X_g | X_{g−1}) ‖ Q(X_{g−1},·))], and each term is a selection among
  the incumbent and K draws from Q(x,·), which Theorem B′ does not cover because the incumbent is a
  point mass, not a draw.
- *Conjecture P\*.2 (interpolation).* For the item-wise mutation kernel with redraw probability q the
  sharp per-round budget is between λ_{K+1} and λ_{K+1} + (1−q)·c(n, p), and the i.i.d. budget
  λ_{GK+1} is recovered iff q = 1.
- *Acceptance.* A proof of P\*.1 (or a counterexample), and the exact per-round budget for q ∈ (0,1)
  on the Spiral null, with the Theorem C consequence ρ_G ≤ √(2v(p)·budget/n) checked against the
  exact mutation-chain gaps (0.455 at q = ¼, 0.447 at q = ½, n = 8, K = 2, G = 20).
- *Falsifying search.* Exact KL of the count law for n ≤ 16, K ≤ 4, q ∈ {1/8, …, 7/8}, G ≤ 40,
  naive and gated rules, against G·λ_{K+1}; a single cell above refutes P\*.1 (the count KL is a
  lower bound on the record KL, so a count-level violation is a violation).
- *Why it is the consequential one.* It is the difference between proving properties of a synthetic
  channel and predicting an RL loop: policy updates are perturbative, and the budget that transfers is
  the one that bounds reward hacking per round.

## 1. Ranked programme

### 1. Finite-sample power and identification for noisy judges — rank 1

*Significance* moderate, *tractability* high, *experimental relevance* highest.

What is proved: six population identities with a copying residual (exact), two level-α tests
(exact size), an interval for ε₁ with proven coverage (§11). What the audit adds (report G9): the
tetrad test rejects any violation of conditional independence given a binary latent, and
item-difficulty heterogeneity without copying produces first tetrads of the same sign and comparable
size (+0.0036 against copying's +0.0064), with sign-test power 0.72 at m = 4000. Identification fails:
a (Y, D) four-class model with four raters has 19 parameters on 15 degrees of freedom.

- *Conjecture 1.1 (discrimination).* Under copying between raters 1 and 2 only the first tetrad
  is nonzero (c₁₃c₂₄ = c₁₄c₂₃ exactly, proved); under a two-stratum heterogeneity model all three
  tetrads are nonzero for generic parameters. A joint sign test of (τ₁, τ₂) separates the two at
  m = 10,000 with power ≥ 0.5 against the heterogeneity alternatives of the report.
- *Conjecture 1.2 (identification with repeats).* With a fifth rater, or two independent gradings by
  one rater, the four-class (Y, D) Dawid–Skene model is locally identified; the tetrads of the
  enlarged table test heterogeneity against copying.
- *Acceptance.* Exact power tables for the joint test from the 16⁴ block law (as in
  `check_gold_four_rater.py`), and a Jacobian-rank computation for 1.2 at a grid of parameter points.
- *Falsifying search.* A parameter point of the heterogeneity model with τ₂ = 0 and τ₁ ≠ 0 (then 1.1
  fails); a rank deficiency of the 5-rater Jacobian on an open set (then 1.2 fails).

### 2. Composition of adaptive feedback channels across rounds — rank 2

*Significance* high, *tractability* moderate, *relevance* high. This is Problem P\* for i.i.d. and
Markov candidates, plus the ledger question: given declared (n, G, K, access class, query counts), is
the phantom-gain bound a theorem for the composed loop?

- *Theorem (immediate from B′).* For the naive reuse chain with i.i.d. candidates and any
  accept/reject rule, KL(law of the kept record ‖ p₀) ≤ λ_{GK+1}, hence
  ρ_G ≤ √(2v(p)λ_{GK+1}/n), sharper than multigen Prop 5 (report S2). Acceptance: add it to the
  multigen note with the exact comparison table; Lean: `MultigenRunningMax` + `SelectionContainment`.
- *Conjecture 2.1 (gated chains).* Every threshold rule has KL(law(c_G)‖Bin) ≤ KL(naive) under the
  null (Prop 4 gives the gap ordering; the KL ordering is open). Falsifying search: n ≤ 16, K ≤ 4,
  z ∈ {1,2,3}, G ≤ 40, exact laws.
- *Conjecture 2.2 (item-level access).* With f score queries per round and item-level feedback the
  reported gain after G rounds is bounded by min(1 − a, G·f·(…)/n) — the bound of the lattice note
  composed; the composition note's 22,143-sequence check is the finite base. Acceptance: an algebraic
  identity for the composed ceiling-crossing count.

### 3. Threshold gating under mixed positive gains — rank 3

*Significance* moderate, *tractability* moderate (the window identity (W) is the tool),
*relevance* moderate (gates are what practitioners use).

- *Conjecture 3.1 (adjacent gains).* For gain support {g, g+1} with any q₀ and any non-decreasing
  level function, the naive rule dominates every threshold rule in count. Evidence: no count failure
  on any of the 126 {1,2} cells screened (multigen §6), none on the audit's abstract chains.
- *Conjecture 3.2 (ratio threshold).* A gate can win in count only if some gain exceeds twice
  another; the witnesses have ratios 3 and 2 with a zero gain ({0,1,2} wins only with gain 0 present).
- *Acceptance.* A proof of 3.1 via (W)–(V) with two-level divergence states, or an exact
  counterexample; the exact characterisation of the two-gain cells that fail on n ≤ 6.
- *Falsifying search.* Exact windows W^a_k for support {g, g+1}, g ≤ 3, n ≤ 8, K ≤ 4, seven
  lattices, k ≤ 40 (the note's `support_window_screen` machinery); one negative count window
  followed by a losing rule refutes 3.1. For 3.2, support {1,2} with gain 0 absent and a plateau.

### 4. Optimal adaptive patching with three or more hits; complexity — rank 4

*Significance* high as mathematics, *tractability* moderate, *relevance* low (the patching model is
stylised; its experimental use is the ceiling-crossing count, which Props 4–5 already give).

- *Conjecture 4.1 (two categories).* With two categories committing is optimal for every H
  (verified on 782,600 states, sizes ≤ 24). Route: Lemma 12's slack is non-negative for two
  categories; a proof would be an inequality E[δ] ≤ 1/(F+1) + p·E[ρ] from the single-failure
  corollary's marking argument extended to F failures.
- *Conjecture 4.2 (at most two failures per category).* Committing is optimal. The note calls this a
  stressed regularity; the Corollary-14 witness needed F = 7.
- *Complexity.* PATCH with H in the input: the referee sees no reduction and no pseudo-polynomial
  obstruction; the natural conjecture is that PATCH is in P via a switching-curve characterisation,
  since the three-hit witness switches exactly once and the loss is one part in 739. A hardness proof
  would need both C and max n_c to grow; an NP-hardness reduction from a partition-type problem would
  have to encode numbers in unary sizes, which is a sign it does not exist.
- *Acceptance.* Proof of 4.1; exhaustive scan of 4.2 to sizes 30 with three categories; either a
  polynomial algorithm for H = 3 or a reduction.
- *Falsifying search.* Two-category states, sizes ≤ 40, all H (4.1); three categories, F_c ≤ 2,
  sizes ≤ 30 (4.2).

### 5. Best-of-K sharpness and asymptotics beyond K = 50 — rank 5

*Significance* moderate, *tractability* low with the present method, *relevance* low (sup_n r = c_K
is known; monotonicity is a refinement).

- *Status after this review.* The monotone approach holds at every n for K = 2..50 (K = 41..50 closed
  by the referee's exact scan of (400, 1160] against the heavy run's N₀ ≤ 1151; report G2).
- *Conjecture 5.1.* a_n(K)² is strictly increasing in n for every K ≥ 2 and every n ≥ 1.
- *Conjecture 5.2 (structural route).* M_n(K)/M_n(2) is non-decreasing in n for every K ≥ 2
  (ρ_n ≥ 1), equivalently E[2^{−N_n}] ≤ ½ − M_n/(2n) with N_n the number of candidates at the
  maximum; the increment identity makes this a statement about tie counts of binomial maxima, and
  a coupling of N_n with N_{n+1} (adding a fair bit to every count) may prove it directly without
  Edgeworth.
- *Acceptance.* A proof of 5.2, or the effective-bound method with C_K growing polynomially in K
  (the Poisson strip bound (1 + φ(0)√e)^K is the obstruction), plus exact scans to N₀(K).
- *Falsifying search.* Exact D_n for K ∈ {60, 80, 100, 200, 500, 1000}, n ≤ 3000, by the integer
  method of `check_selection_d5_sweep.py` (cost ∝ K·n² big-integer multiplications; K = 1000,
  n = 3000 is hours, not days). A negative D_n refutes 5.1 and 5.2.

### 6. Higher-order topology of joint and separate observations — rank 6

*Significance* low after Counterexample 9 (the natural homotopy invariants are shown not to
determine the fibre), *tractability* high, *relevance* low.

- *Conjecture 6.1.* For separate observation of k ≥ 3 maps, f(P) is the corank of the vertex–facet
  incidence of the nerve, hence a matroid invariant of the balanced complex, and no functor of the
  homotopy type determines it (already shown for the listed family).
- *Worth doing anyway.* Proposition 11's integrality question: the smallest balanced complex whose top
  homology class has no {0, ±1} representative (the note uses 78 flags); and whether integrality ever
  matters for two maps observed jointly with a third (the note leaves this open; the pair-joint pattern
  is a graph, so no).
- *Acceptance.* An exhaustive search over balanced 2-complexes with ≤ 12 vertices for a top class with
  no {0,±1} representative. *Falsifying search for 6.1:* two supports with isomorphic nerves (as
  uncoloured complexes) and different f(P) — this would refute the note's claim that f(P) is a
  combinatorial invariant of the nerve with colours erased, which was checked only on the 2×2×3 grid.

## 2. Scientific relevance (Assignment B)

**What the theory predicts, and for what.** The exact results are properties of declared channels:
(i) the reported score on a reused set under no true change is the running maximum of GK+1 draws,
with increments decreasing and a bound √(2v(p)λ_{GK+1}/n) (report S2), (ii) an item-level or
score-only loop crosses the ceiling after a computable number of patches or queries, (iii) a judge
that shares the controller's errors reaches the ceiling without memorisation iff ε₁ ≥ ½, (iv) a
fourth independent grader makes rater dependence testable. None is a prediction about a language
model until the channel is identified with a training loop, and the audit's S2 shows the first
prediction's budget does not survive perturbative candidates.

**Measurable quantities and their causal content.**

| Quantity | Measured by | Causal reading | Where identification fails |
|---|---|---|---|
| n, G, K, access class, query/patch counts | the ledger | none needed; they are inputs | an undeclared query is invisible |
| reported − sealed gap ρ_g | a sealed readout set never fed to the loop | phantom gain, by construction | without a sealed set, ρ_g is not identified from the reported curve |
| ε, ε₁ of the judge | gold-labelled sealed sample, 2×2 table | shared error, if gold is clean and independent | gold noise η confounds (Judge Cor.), and η is identified only under conditional independence of graders |
| η from a second grader | three pairwise agreements | exact under the symmetric model | not testable with three raters; absorbed by asymmetry (§7) |
| tetrads of four raters | 16-cell table | rejects conditional independence given a binary latent | copying vs difficulty heterogeneity not separated by the first tetrad (G9) |

**The synthetic-channel / real-training gap.** The chains assume candidates independent of the
incumbent (Prop 1), or correlated through one parameter q (§5), with clean labels and a fixed n. A
policy update is perturbative (q < 1), gains are correlated with the incumbent's errors, and the loop
sees gradients, not accept/reject. The theory's robust predictions are the ones that need only
exchangeability of candidates — the running maximum and its decreasing increments — and the ones that
need only the judge model. The KL budget is not among them.

**Experiments.**

*E1. Reuse inflation versus the running-max law.* Setup: a small instruction-tuned model, a fixed
scored set of n = 1,000 items, G = 20 generations of best-of-K = 4 sampling with the incumbent
replaced by the best candidate (no weight update), a sealed set of 1,000 items, 10 seeds.
Hypotheses: H₀ (running max of GK+1 exchangeable draws): reported − sealed gap equals
E[max of 81 Bin(1000, p)]/1000 − p = 0.0384 at p = ½ (exact; the S2 bound is 0.0413) with increments decreasing; H₁ (hill-climbing
correlation): the gap exceeds H₀ and keeps growing; H₂ (true gain): the sealed score rises.
Discriminant: the gap series against the exact H₀ curve, and the sealed curve's slope. Power: a
single reported score has s.d. √(p(1−p)/n) ≈ 0.016; ten seeds give s.e. 0.005 per generation, so a
gap of 0.038 against 0, or against a q = ½ excess of the size seen on the n = 8 toy (0.447 against 0.365,
22% larger), is resolved at G = 20 with margin. Cost: 20 × 4 × 2,000 = 160,000 generations per seed, 1.6 M generations total;
on a 1–3 B model this is hours on one GPU.

*E2. Judge contamination and the ε₁ ceiling.* Setup: a judge model fine-tuned on the controller's
own outputs versus the same judge fine-tuned on an unrelated model's outputs; 10,000 gold-labelled
sealed items with two human graders (or one human and one strong independent model) and the
controller as rater; the pipeline of gold calibration §4 with the §11 interval. Hypotheses: H₀
ε₁ = ε (independent judge); H₁ ε₁ > ε (shared error), the controller-trained judge showing the larger
excess. Discriminant: the plug-in-free interval for ε₁ (width about 0.17 at m = 10,000 for the
fixture) and the exact ceiling test. Power: the §9 tables give separation of ε₁ = 0.1 from 0.5 at
m = 4,000; for ε₁ − ε = 0.1 the §11 interval, of width 0.22 at m = 10,000 in the note's table, needs about
four times the items for half the width — the design constraint is grader labour, not compute. Cost: 2 judge fine-tunes
and 10,000 × 2 gradings.

*E3. Rater dependence versus heterogeneity.* Setup: four graders (two humans, two models) on the
same 10,000 items, no copying by construction, items stratified by a measured difficulty proxy.
Hypotheses: H₀ conditional independence given the label; H₁ difficulty heterogeneity; H₂ a copying
pair. Discriminant: the pair (τ₁, τ₂) by the block sign test, and the within-stratum tetrads (which
vanish under H₁ if the proxy captures D). Power: at m = 10,000, sign-test power 0.92 and 0.98 against the two
stronger heterogeneity models of the report (0.17 against the mild one) for τ₁; the second tetrad at
+0.0008 needs m of order 10⁵ for power 0.8 (scaling the 0.0036 → 0.72 result at 4,000 by τ²m). Cost: 40,000 gradings; no training.

*E4 (the consequential one). Per-round KL of a real update.* Setup: a policy and a reference policy;
each round, sample K = 8 candidates from a perturbation of the current policy (a small LoRA step, or
temperature-perturbed sampling), keep the best by a fixed scorer, estimate KL(current ‖ reference)
by importance sampling on 10,000 prompts each round, G = 20. Hypotheses: H₀ (i.i.d. budget)
KL_G ≤ λ_{GK+1} = 4.09 nats at G = 20; H₁ (additive) KL_G ≤ G·λ_9 = 26.2 nats, and above the i.i.d.
curve; H₂ neither bound. Discriminant: the KL series against the two curves. Power: IS estimates of
KL at 4 nats with 10,000 prompts have relative s.e. ≈ 3% when the log-ratio variance is ≈ 10;
the two curves differ by a factor 6 at G = 20. Cost: 20 × 8 × 10,000 generations plus 20 LoRA steps
on a 1–3 B model: a day on one GPU.

## 3. Lean and verification priorities

1. Theorem B′ (replaces `SelectionContainment`'s jitter route; `atom_le` is most of it).
2. The running-max corollary ρ_G ≤ √(2v(p)λ_{GK+1}/n) (`MultigenRunningMax` + `SelectionContainment`).
3. Multigen Prop 10 (Count), the one proof the audit could only stress-test.
4. The K = 41..50 closure: commit the exact window scan as a receipt (the referee's
   `check_selection_d5_sweep.py gap 41 50 400 1160` ran in 18 minutes).

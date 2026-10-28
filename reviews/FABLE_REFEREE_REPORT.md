# Referee report on MoralityLabAI/EvalMath (main `424dc8b`) and PR #1 (`3d939c3`)

Referee: Claude Fable 5.1, 2026-10-26. Independent code under `reviews/checks/`, with every
recorded output under `reviews/checks/outputs/`. Nothing below was imported from `spiral_ln`; where a
number of the repository's own verifier is quoted, the file says so.

## 0. What was run, and what was not

| Check | Command | Result |
|---|---|---|
| Fast receipts | `python scripts/check_receipts.py` | 11 of 11 regenerate identically (float tolerance for `selection_kl`) |
| Heavy selection verifier | `python scripts/verify_evaluation_selection_kl.py --heavy` | 66/66 checks true; thresholds `N_0` for K = 31..40 are 520..760 and for K = 41..50 are 794, 827, 862, 899, 937, 976, 1017, 1060, 1105, 1151 (`outputs/selection_heavy_summary.json`) |
| Slow receipts (`--all`: multigen full sweep, gold calibration) | not run | the two slow receipts were not regenerated here |
| Lean build | not run | Mathlib was not built; the Lean statements of `SelectionTieRules.lean` and `CLAIMS.md` were read, not compiled |
| Independent checks | `python -I reviews/checks/<file>.py` | listed per finding below |

Every claim of the five priority areas was re-derived from the notes' definitions, with no code shared
with the repository. No blocking mathematical error was found. The findings are a scope gap resolved
by a new theorem, a wording error in Counterexample 9, several overstatements, a novelty overclaim in
PR #1, a scientific non-identifiability in the four-rater test, and one open item that the referee's
computations close.

## 1. Blocking mathematical errors

None. Every exact witness in the five priority areas reproduced to the last digit, and every
*algebraic identity* audited held on its stated domain, including the boundary cases checked (one-hit
states with failure-free categories, K = 1, the all-tied score law, levels with plateaus and with
p = 0, `F = n` sure hits, and `rank Ψ = 0`).

## 2. Proof gaps, scope gaps, fidelity gaps

**G1. Theorems A/B (selection KL) are stated for tie rules that see only the score vector; the
synthesis says "every tie rule".** Theorem A's hypothesis, and the Lean structure `TieRule`
(`pick : R → (Fin K → ℝ) → Fin K`), exclude rules that look at the records themselves — "among
tied candidates keep the shortest", a lexicographic order, or any non-transitive tournament. A rule
induced by a total preorder on records is best-of-K on a refined score and is covered; a
non-transitive choice is not. The gap closes, in the stronger direction, by the following theorem,
which the notes do not contain and which replaces the jitter construction of Theorem B.

> **Theorem B′ (any selection rule, any f-divergence).** Let ω₁,…,ω_K be i.i.d. from p₀ on any
> measurable space, and let J be any random index in {1,…,K}, a function of (ω₁,…,ω_K) and of
> independent randomness, with no symmetry and no score. Let π be the law of ω_J. For every convex
> f with f(1) = 0,
> D_f(π ‖ p₀) ≤ ∫₀¹ f(K u^{K−1}) du.
> In particular KL(π‖p₀) ≤ ln K − (K−1)/K, χ²(π‖p₀) ≤ (K−1)²/(2K−1), and for finite Ω and K ≥ 2
> the KL inequality is strict.
>
> *Proof.* For every measurable A, π(A) = P(ω_J ∈ A) ≤ P(∃k : ω_k ∈ A) = 1 − (1 − p₀(A))^K =: G(p₀(A)),
> with G concave, G(0) = 0, G(1) = 1, G′(u) = K(1−u)^{K−1}. Hence π ≪ p₀; let h = dπ/dp₀ and h* its
> decreasing rearrangement on ([0,1], Lebesgue). For finite Ω, sort the atoms by h: at a breakpoint
> t = p₁+…+p_j, ∫₀ᵗ h* = π({1..j}) ≤ G(t); between breakpoints ∫₀ᵗ h* is linear and G is concave, so
> ∫₀ᵗ h* ≤ G(t) = ∫₀ᵗ G′ for all t, with equality at t = 1 (the general case is the Hardy–Littlewood
> rearrangement inequality). So h* is majorized by G′ as decreasing functions with equal integrals,
> and for convex f, ∫₀¹ f(h*) ≤ ∫₀¹ f(G′) (Hardy–Littlewood–Pólya; Chong 1974 for the continuous
> form). The left side is Σ p₀(ω) f(h(ω)) = D_f(π‖p₀); the right side is ∫₀¹ f(K v^{K−1}) dv after
> v = 1 − u. Strictness for finite Ω, K ≥ 2: a step function cannot equal the strictly decreasing
> continuous G′ a.e. □

Evidence from `check_selection_tie_rules.py` and `check_selection_any_rule.py`: over *all*
deterministic selection rules f : Ω^K → [K] (not only argmax rules) with p₀ optimised by coordinate
ascent — 16 rules at (|Ω|,K) = (2,2), 512 at (3,2), 6561 at (2,3), and 20,000 sampled rules at (2,4)
and (3,3) — the largest KL found was 0.136, 0.166, 0.317, 0.478, 0.318 against λ_K = 0.193, 0.193,
0.432, 0.636, 0.432; the maxima were all attained by transitive (refined-score) rules. The χ² version
held with maxima 0.296 (bound 1/3) and 0.620 (bound 4/5). Theorem B′ is not a correction of Theorem B;
it is the theorem the synthesis's sentence needs, and it also supports the "selection inside a
divergence budget" framing against an adversarial chooser. **Severity: wording gap in the synthesis
and in Theorem B's "every tie rule"; no false claim.**

**G2. The computer-assisted monotone approach (D.5, version 0.4, K = 4..30) was not re-derived; its
output was checked for consistency, and its open window for K = 41..50 is closed below.** The interval
constants (`cdf_and_midpoint_constants`, `second_order_margin_constant`) rest on a long chain —
Robbins' bounds, a midpoint Euler–Maclaurin kernel, Poisson summation on a strip — that this referee
did not reconstruct; the note's own labelling (*algebraic identity given the cited Robbins and Poisson
statements*) is honest. What was checked independently (`check_selection_d5_sweep.py`,
`check_selection_d5_constants.py`):

- Exact integer recomputation of M_n(K), D_n(K) and a_n(K)² from S_m = Σ_{j≤m} C(n,j): D_n > 0 and
  a_{n+1}² > a_n² for every K = 4..40 and n ≤ 400 (the 0.3 sweep), and for K = 4..10 and n ≤ 1500
  (beyond the sweep; consistent with the theorem's range n ≥ 400). For K = 2, 3, D_n = 0 exactly at
  every n ≤ 60 while a_n² still increases, as the note states.
- The Gaussian table (E[M_K], c_K) reproduces to 5 decimals at K = 2, 3, 5, 10, 100; the quadrature
  identity δ_K = c(K)E[M_K]/2 holds to 10⁻⁹ at K = 4, 5, 10, 20, 30 with δ_K computed from the note's
  three-integral formula and c(K) from (E[M_K³] − 5/2 E[M_K])/(6E[M_K]).
- At n = 400 and 900, exact √n·D_n minus δ_K is +3.2·10⁻⁵/+1.4·10⁻⁵ (K = 4), +4.0·10⁻⁴/+1.8·10⁻⁴
  (K = 10), +1.0·10⁻³/+4.6·10⁻⁴ (K = 20), +1.6·10⁻³/+7.2·10⁻⁴ (K = 30): inside C_K/n by factors
  58, 70, 110, 161, and n·(√nD_n − δ_K) = 0.0129, 0.158, 0.416, 0.645, matching the note's 0.0129,
  0.158, 0.416. The bound's sign and order are right.
- **The unchecked window (400, N₀) for K = 41..50.** The note leaves D_n > 0 unverified for
  400 < n < N₀(K) ≤ 1151. The exact scan `sweep`/`gap` in `check_selection_d5_sweep.py` finds
  D_n > 0 for every n ∈ [400, 1160] and K = 41..50 (`outputs/d5_gap_K41_50.txt`), and for n ≤ 400
  (`outputs/d5_sweep_K41_50_n400.txt`). With the heavy run's certified N₀ (above), the monotone
  approach holds at every n for K = 41..50 under exactly the hypotheses of the K = 4..30 theorem.
  This upgrades the status of "Best-of-K for K > 40" in findings §8 item 2 from open to open only for
  K > 50.
- One fragility worth stating in the note: the scaled margin N₀^{3/2}D_{N₀}/(2C_K) is 1.00004 at
  K = 26 (N₀ = 417) and below 1.003 for K = 26..30; the certificate is exact, so this is not an error,
  but it means the C_K are within 0.004% of too large to certify at those K.

**G3. Counterexample 9: "the vertex links agree as multisets of forests" is false as written; the
conclusion stands.** `check_leak_topology.py` rebuilds both nerves from the partitions. Face numbers
(8, 16, 6) and coloured face numbers (2,3,3; 5,5,6; 6) agree, both nerves have reduced Betti numbers
(0, 3, 0), the three rank-selected two-map graphs are connected with β₁ = 1, the three merged-colour
graphs are two trees each, and f(P₀) = 0, f(P₁) = 1 with Theorem 8's data (β₁(G), f(P′), rank Ψ) =
(0, 1, 1) and (0, 1, 0). But the eight vertex links, as graphs, have (vertices + edges) counts
{3, 5, 6, 6, 6, 6, 8, 10} in P₀ and {5, 5, 6, 6, 6, 6, 6, 10} in P₁: they agree only as multisets of
*homotopy types* (six links with two tree components, two connected trees, in both). The module
(`homotopy_profile`) compares homotopy profiles, so the receipt is right; the sentence should read
"agree as multisets of homotopy types of forests". The theorem the counterexample proves — the
separate fibre is not a function of the listed homotopy data and face numbers — is intact, since that
list is of homotopy types. Also: the six-item version of Proposition 10's witness ("confuses `100110`
with `011001`") presupposes that the doubled cell's items are numbered 1 and 2 (items in cell order);
appending the new item as item 5 gives a different pair. The note should state the numbering.

**G4. Theorems 7 and 8 (leak topology) are correct; the proofs were re-derived and the formulas
checked by independent rank computation.** Theorem 7: the sign trick (multiplying rows of face type
W∖w by (−1)^{pos w}) is valid because, for a fixed omitted colour, the orientation sign is the same for
every facet over that face, so the unsigned margin equations and the simplicial boundary have the same
kernel; the link of an R-cell is the nerve of the W-projections of its slice, and the slice complex is
pure of dimension |W|−1. The link formula agrees with the direct rank on all 1,351 (support, W) pairs
of the 2×2×2 grid. Theorem 8: Z₁(G) is the kernel of π; a y lifts iff the transportation problem on G
with row sums y and column sums 0 is feasible iff each component balances, which is the image
description of a bipartite incidence matrix (rank |V| − c). The exact sequence reproduces f(P) on all
193 supports (rank Ψ > 0 in 10 of them). Theorem 1 reproduces on 400 random pairs.

**G5. Multigen Proposition 10 and the two-gain counterexamples: every number reproduces; the proof
was not fully re-derived; a stress test beyond the binomial chain found nothing.**
`check_multigen_two_gain.py` re-implements the drift chain from §6's definitions (gain posterior
q_μ Bin(n,p(i+μ))(M)/mix(M)). On n = 3, K = 1, levels (0,¼,¼,¾), gains {0,1,3} w.p. (3/5,1/5,1/5),
rule t = (1,0,0,0): the gate is ahead in P(c_k = 3) exactly at k = 28..80 (0.99090 vs 0.99045 at
k = 34), in E[c_k] exactly at k = 39..80, in E[p(i_k)] exactly at k = 19..80, and the limits are
2909/3968 and 8058689/11073200 exactly. The second witness (n = 4, gains {0,1,2}) reproduces
(31..80, 31..80, 15..80), and the hand witness gives 17/18 against 139/150. For Proposition 10 itself,
the referee verified by hand the lemmas (M1), (M2) and the time-monotonicity under hypothesis (A)
alone, but not every step of the (Count) cross-gap bound. Instead, Proposition 10 was stressed on
400 random *abstract* chains — arbitrary laws π_i on (J, i′) with i′ ∈ {i, i+1}, not binomial, with
(B) enforced on 70% of them — against every level-dependent threshold rule for small (n, top) and 60
sampled rules otherwise, from (0,0), horizon 6, all tail indicators of count (when (B) holds) and
level: 711,520 rule–cell pairs, no violation. **Status: finite-stress evidence that the abstract
statement is right; the written proof is dense enough that a Lean formalization of (Count) is the
right next check, as findings §8 item 6 already lists.**

**G6. Lean fidelity.** `CLAIMS.md` is candid and the two gaps that matter are already disclosed:
Props 9 and 10 take the binomial stochastic-monotonicity (`hstoch`, H non-decreasing) as hypotheses
rather than deriving them; the synthesis labels Prop 9 *full*, which is true of the abstract
statement and should say "with the binomial property assumed". `theoremB_every_tie_rule` requires only
Σν = 1, not ν ≥ 0 (harmless: each r gives the same law). `TieRule` is score-only, as in G1.

**G7. The synthesis overstates in §7.** "Given those, the largest phantom gain is computable, and
anything above it is real" holds only for loops that are one of the modelled channels with
candidates independent of the incumbent. For the mutation chain of §5 no bound is proved, and the
referee's `check_mutation_chain_kl.py` shows the stronger fact that the i.i.d. divergence budget is
exceeded there (see S2 below). The sentence should be conditioned on the ledger's channel being one
of the modelled ones.

**G8. PR #1 is mathematically sound and its novelty is overstated.** `check_pr1_capacity.py`,
brute force only: 193 coordinate-surjective supports; 99 with positive rational kernel; 91 with a
0/1 collision at unit capacity (all 2^|P| cell vectors enumerated); the other 8 collide at uniform
capacity 2; the five-cell witness gives joint 3/128, separate 49/2048, ratio 49/48 by direct
enumeration of all record pairs, and 1 at unit capacity; Theorem 2's lattice sum equals the direct
enumeration on 60 random (support, sizes, pattern) cases; for the pair-joint/third-separate pattern,
positive kernel implies a unit-capacity collision in all 579 cases. Proposition 3's certificate
satisfies ‖z‖_∞ ≤ max|minor| ≤ r^{r/2} on all 99 supports. But:
- Theorem 1 is leak topology §5, third bullet ("a nonzero integer fibre vector z is a witness once
  s_c ≥ |z_c|"), restated; the PR's claim to "settle the finite-size question left by Proposition 10"
  settles what that bullet already states.
- Theorem 2 is leak topology Theorem 4 with H₁(I;ℤ) replaced by ker_ℤ M; the proof is the same
  sentence.
- Proposition 3 is Cramer plus Hadamard. On the five-cell witness the bound is 16 (r = 4) against the
  true capacity 2; on 3 of the 99 supports the RREF certificate has sup-norm 2 where a kernel vector
  of sup-norm 1 exists (`outputs/pr1_capacity.txt`), so "its maximum absolute entry is a finite
  sufficient capacity" is right and "critical" would be wrong; the PR does not say "critical". For
  0/1 matrices the sharper determinant bound (r+1)^{(r+1)/2}/2^r is available.
- The counts 193/99/8 duplicate leak topology's; what is new is "each of the eight admits a witness at
  capacity two", the number 49/48, and a second implementation of the collision count.
Recommendation: merge after relabelling Theorems 1–2 as corollaries of leak topology Theorem 4 and
§5 with citations, trimming the findings bullet to the new facts, and keeping the receipt.

**G9. The four-rater tetrad test is valid but non-specific.** `check_gold_four_rater.py` verifies
symbolically (sympy, all 16 cells) the six §8 equalities and the copying residual
c₁₂c₃₄ − c₁₃c₂₄ = ρV₁c₃₄ with c₁₃c₂₄ = c₁₄c₂₃; rebuilds the block law of Z from all 16⁴ quadruples
(size control exact: P(Z=+1) = P(Z=−1) = 22895240409/5·10¹¹ at ρ = 0); and reproduces every power in
the §10 table (0.326 at 742; 0.212, 0.519, 0.788, 0.930 at 4000; 0.417, 0.869, 0.990, 0.9996 at
10000). It then puts, in place of copying, item-difficulty heterogeneity: Y ~ Bern(¼), a binary
difficulty D independent of Y, error rates scaled by a factor per stratum, raters conditionally
independent given (Y, D) — no copying. The first tetrad is +0.000773, +0.003591, +0.003178 (copying
at ρ = 1 gives +0.006413) and the one-sided sign test has power 0.10, 0.72, 0.58 at m = 4000. The
test rejects conditional independence given a *binary* latent; it does not identify copying. The
observable discriminant is the second tetrad c₁₃c₂₄ − c₁₄c₂₃, exactly zero under copying between
G₁, G₂ and +0.00022, +0.00089, +0.00081 under the three heterogeneity models. The note should say
so where it says "the one copying breaks" (§10) and in findings §6. This is a modelling point, not an
error in any identity.

## 3. Suggestions (not findings)

**S1. Replace Theorem B by Theorem B′ in the note and the Lean.** The majorization proof is shorter
than the jitter, covers every rule, and gives every f-divergence at once. Lean: `atom_le` already
does the tangent-line Jensen per atom; the rearrangement step is a sort plus `Finset.sum` telescoping.
Strictness for finite Ω follows as in `atom_lt`.

**S2. A sharper running-max bound is already implied by the notes, and the mutation chain breaks it.**
Multigen Prop 1 gives ρ_G = γ(n, GK+1, p); selection Theorems B and C give γ(n, m, p) ≤
√(2v(p)λ_m/n). So ρ_G ≤ √(2v(p)(ln(GK+1) − GK/(GK+1))/n), strictly below Prop 5's
√(ln(GK+1)/(2n)) at every p and below its Bernstein bound at p = ½
(`outputs/running_max_bounds.txt`: at n = 8, K = 2, G = 20, p = ½ the three bounds are 0.414, 0.482,
0.637 against the exact 0.365). The synthesis quotes the weakest. More consequentially,
`check_mutation_chain_kl.py` computes the exact law of c_G under the §5 mutation chain and finds
KL(law(c_G) ‖ Bin(n,p)) = 1.54, 2.66, 3.91 at G = 5, 10, 20 for q = ½ (n = 8, K = 2) against
λ_{GK+1} = 1.49, 2.09, 2.74, and 4.09 against 2.74 at q = ¼, G = 20, while q = 1 (i.i.d.) stays
below as Theorem B′ requires. By data processing the record-level KL is larger still. So "selection
inside a divergence budget" (findings §4) does not extend to perturbative candidates, which is what a
policy update is; the per-round additive budget G·λ_{K+1} was not exceeded on these cells. This is
the problem proposed in `FABLE_RESEARCH_PRIORITY.md` §0.

**S3. Promote δ_K = (E[M_K³] − 5/2·E[M_K])/12 from "checked by quadrature" to "cited".** It is the
statement that the 1/√n coefficient of the proven expansion of D_n equals the coefficient implied by
the continuity-corrected Edgeworth expansion of the symmetric binomial; given a rigorous Edgeworth
theorem for lattice distributions (Esseen 1945; Petrov 1975, Ch. VI) with remainder O(n^{-3/2}) after
continuity correction, uniqueness of asymptotic coefficients gives the identity. No new computation
is needed.

**S4. Theorem 11 and Corollary 14 (lattice) reproduce exactly in an independent DP**
(`check_lattice_patching.py`: Theorem 10 and 11 against the programme on 300 random states, the
witnesses 1055429/205920 vs 351823/68640, 7477604/479655 vs 22463159/1438965, 763/120 vs 509/80, and
committing exact at H ≤ 2 on 4,040 (state, H) pairs with sizes ≤ 6). Nothing to fix.

**S5. Wording.** In findings §3, "What a threshold gate does" should state the hypotheses of Prop 10
((A) and (B)) rather than "every gain law with a single positive gain value", since (B) is a
hypothesis on the chain and the time-varying schedule is outside it, as the note's §8 says.

## 4. Executed checks

| File | What it establishes | Runtime | Output |
|---|---|---|---|
| `check_multigen_two_gain.py` | §6 witnesses exact; Prop 10 stress on abstract chains | 3 m 22 s | `multigen_two_gain.txt`, all `[OK]` |
| `check_selection_tie_rules.py` | argmax-rule scope: no record-dependent tie rule beats λ_K | 6 s | `selection_tie_rules.txt`, all `[OK]` |
| `check_selection_any_rule.py` | Theorem B′ numerics, KL and χ² | 51 s | `selection_any_rule.txt`, all `[OK]` |
| `check_selection_d5_sweep.py` | exact D_n, a_n² sweeps; K = 41..50 window | 1–18 min per run | `d5_sweep_*.txt`, `d5_gap_K41_50.txt` |
| `check_selection_d5_constants.py` | Gaussian constants, δ_K identity, bound consistency | 12 s | `d5_constants.txt` |
| `check_leak_topology.py` | Theorems 1, 7, 8; Counterexample 9; Prop 10 witness | 1 s | `leak_topology.txt`, one deliberate `[FAIL]` (G3) |
| `check_pr1_capacity.py` | PR #1 counts, 49/48, Theorem 2, Prop 3 | 2 m 29 s | `pr1_capacity.txt`, all `[OK]` |
| `check_gold_four_rater.py` | six equalities, copy residual, sign-test power, heterogeneity | 1 m 33 s | `gold_four_rater.txt` |
| `check_lattice_patching.py` | Theorems 10, 11, Corollary 14 witnesses | 1 s | `lattice_patching.txt`, all `[OK]` |
| `check_mutation_chain_kl.py` | KL of the mutation chain vs λ_{GK+1} | <1 s | `mutation_chain_kl.txt` |

Not executed: the slow receipts, the Lean build, any model.

## 5. Publication assessment

**Could stand alone now, with the edits above.**
- The selection-KL note, rewritten around Theorem B′ (any rule, any f-divergence) plus Theorem C,
  D.1–D.4 and D.5 for K = 2, 3: a short, complete paper. The K = 4..50 computer-assisted part is a
  separate, longer contribution whose interval chain needs a second reconstruction before it is
  refereed; the sweeps and consistency checks here are evidence, not a proof check.
- Leak topology Theorems 1–8 and Counterexample 9, with Proposition 10 and PR #1's capacity facts as
  one section: a clean combinatorial paper. The "topology is nominal for separate observation"
  conclusion is the publishable point.
- The lattice patching results (Theorems 10, 11, Corollary 14, Lemma 12) with the complexity
  question stated: a self-contained operations-research note.

**Needs new evidence first.**
- Any claim about adaptive evaluation of real models: the repository is explicit that it has none,
  and S2 shows the central budget bound does not transfer to perturbative loops; a paper framed around
  RL would need the experiment of `FABLE_RESEARCH_PRIORITY.md` §1 or an honest restriction to
  i.i.d.-candidate selection (best-of-K sampling, rejection sampling, reranking).
- The four-rater testing section: valid, but the non-specificity of G9 must be addressed (joint test
  of both tetrads, or an explicit heterogeneity model) before "detects copying" can be a headline.
- Multigen Props 8–10: the proofs are long and not formalized; a Lean proof of (Count) or an
  independent written proof is the missing evidence.

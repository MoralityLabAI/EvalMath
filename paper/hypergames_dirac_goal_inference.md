# HG-01: Hypergames, implicit Dirac metrics and the geometry of implied goal states

**2026-11-16 | Evidence:** algebraic identities with exact finite tests, plus synthetic deterministic game mechanisms. Implemented in `src/spiral_ln/evaluation_hypergames.py`; reproducible at `output/evaluation_hypergames/hg01.json`. No Lean proof, model run, actual objective inference, or quantum physical claim. GPTStoryworld source revision `c8d46591f983473023daf0232e9b413baaa02194`; EvalMath base `f115865b1bf8cdaca59cae97ff66fcda60e348a2`.

## 1. Why a hypergame instead of a conventional game

The external true game has state space \(S=\prod_{j=1}^d S_j\), legal actions \(A(s)\), a transition law \(T\), terminal gates, and payoff/reachability constraints. Agent \(i\) interacts through an observation map \(O_i\) and a subjective game \(G_i=(S_i,A_i,T_i,U_i,O_i)\); its belief about agent \(j\)'s view is \(G_i^j\). Distinct subjective successor distributions can rationalize the same public action even when the objective transition oracle gives the action a very different result. In GPTStoryworld, first-order `p` and second-order `p2` keyrings instantiate useful parts of this multi-level modeling. Perceived and actual BNumbers must keep separate coordinates.

The live diplomacy engine uses trust matrices, coalitions, messages, outcomes, and turn ownership. The storyworld reasoning v2 schema has pick-time `visible_state`, `legal_actions`, `chosen_action`, and post-turn `hidden_state_reveal`. A raw trace contains no counterfactual successor for an unchosen action. HG-01 conditions on an explicitly supplied, frozen action-successor table, which is necessary for inverse planning. A `shared_full_state` benchmark is evaluated as exactly that observation mode.

The existing Sweepweave code refers to state-effect scripts as “Dirac operators.” Its secret-ending geometry quality test checks for `Absolute Value` and ≥2 variables, while local-max anchors are one-axis finite-difference heuristics. These are existing authoring/evaluation semantics. The Clifford construction below is a new, independently defined metric contract and must not be represented as how the current engine computes transitions.

## 2. High-dimensional states without an exponential tensor allocation

For a finite categorical coordinate \(x_j\) with a distinguished basis vector \(|x_j\rangle\) and shared flag \(|*\rangle\), choose rational amplitudes \(\alpha=3/5\), \(\beta=4/5\). Define

\[
|\phi_j(x_j)\rangle=\alpha|*\rangle+\beta|x_j\rangle,
\quad |\phi(x)\rangle=\bigotimes_{j=1}^d |\phi_j(x_j)\rangle.
\]

All factors have norm one. For categorical mismatch count \(h(x,y)\), orthogonality gives the exact identity

\[
K(x,y)=\langle\phi(x)|\phi(y)\rangle=(9/25)^{h(x,y)},\qquad
\|\phi(x)-\phi(y)\|^2=2\bigl(1-K(x,y)\bigr). \tag{HG-1}
\]

Proof: the shared flag contributes \(\alpha^2\) on mismatches and the complete factor inner product contributes \(\alpha^2+\beta^2=1\) on matches; the tensor inner product factors. The induced chordal distance is a genuine metric on discrete labels because \(\beta>0\) makes the map injective. It can be computed without allocating the \(3^d\)-dimensional Hilbert vector. A basis-only embedding would make every distinct state orthogonal and conceal degrees of separation. With many mismatches, \(K\) approaches zero; the fixed-amplitude kernel then saturates, motivating local comparison, feature weighting, or calibrated alternatives. The tensor Hilbert representation is an exact feature construction, not evidence of quantum dynamics.

For rational numerical BNumbers and trust/goal coordinates let \(\Gamma_j\) be self-adjoint Clifford generators satisfying \(\Gamma_i\Gamma_j+\Gamma_j\Gamma_i=2\delta_{ij}I\), with positive rational \(w_j\). Define \(D_w(x)=\sum_j w_jx_j\Gamma_j\). Clifford anticommutation cancels cross terms:

\[
\bigl(D_w(x)-D_w(y)\bigr)^2
=\left(\sum_j w_j^2(x_j-y_j)^2\right)I,
\quad \|D_w(x)-D_w(y)\|_{op}^2=\sum_jw_j^2(x_j-y_j)^2. \tag{HG-2}
\]

The numerical operator is a faithful metric when weights are strictly positive. Storing a full spin representation at \(d=140\) would require an enormous matrix (complex spinor dimension \(2^{70}\)); the formula evaluates with O(d) rational operations. A two-generator matrix calculation is independently verified using exact fractions. Categorical distances and numerical distances can be combined with a positive direct-sum weight after calibration; HG-01 tests them separately.

## 3. Inverse Voronoi polyhedra of compatible goals

Assume an action \(a\) deterministically yields successor \(s_a\) in the **agent's subjective view**. For a goal prototype \(g\), consider the explicitly restricted myopic policy \(a\in\arg\min_b d_D^2(s_b,g)\). For observed choice \(c\), its rational regret is

\[
r_g(c)=d_D^2(s_c,g)-\min_{a\in A}d_D^2(s_a,g)\ge0. \tag{HG-3}
\]

For each competing action \(a\), expanding the squares in \(r_g(c)=0\) yields

\[
2\langle W^2(s_a-s_c),g\rangle\le\|Ws_a\|^2-\|Ws_c\|^2. \tag{HG-4}
\]

**HG-01/T1 (inverse-goal region; algebraic identity).** The full set of real-valued goals making a finite sequence of choices optimal under the stated one-step metric is an intersection of closed affine halfspaces (HG-4), hence a convex polyhedron, possibly empty. All inequalities have exact rational coefficients for rational states and weights. Proof: expanding and canceling the common \(\|Wg\|^2\) term gives each halfspace; conjunction over actions and time is equivalent to zero regret. The `inverse_voronoi_halfspaces` oracle emits the inequalities and `halfspaces_accept` checks candidate membership independently of `infer_goals`' distance comparisons.

**HG-01/T2 (rank obstruction; algebraic identity).** Let \(M\) contain each halfspace's normal vector as a row. If its rational rank is \(r\), any vector \(v\in\ker M\) leaves every observed preference comparison invariant under \(g\mapsto g+tv\). Therefore \(\dim\ker M=d-r\) is a dimension of **linear observational blindness** under this behavior model. This is a statement about the comparisons; external goal bounds may cut the feasible region. At an interior feasible goal these \(d-r\) directions give local goal ambiguity as well. Proof: the left side of each inequality changes by \(tMv=0\); exact row reduction computes the nullity.

The registered fixture has 140 dimensions, four finite goal prototypes, and two probes that differ along x or y only. The first choice permits two goals. The second leaves the single declared candidate `g01`, but the comparison matrix has rank 2, so its continuous goal space has **138 blind directions**. A finite dictionary can be uniquely classified even when the underlying continuous preference geometry is massively underdetermined. This is a synthetic mechanism result and is not a claim that a storyworld agent has goal `g01`.

## 4. Robust active probes and hypergame misperception

For a probe \(e\) let \(M_e(g)\subseteq A_e\) be the set of all distance-minimizing actions under candidate goal \(g\). Two candidates are *guaranteed separated by that probe* only if their minimizer sets are disjoint. The set of probes that covers every pair is a weighted minimum test collection, exactly the finite combinatorial structure used in EvalMath BPD-01, with ties kept as sets. The executable oracle exhausts at most 16 probes and returns infeasible if some candidate pair cannot be robustly separated. In the fixture, `x` costs 2 and `y` costs 3; both are necessary, with exact minimum cost 5. An uninformative tie probe correctly certifies no separation.

A subjective choice may have zero regret under \(T_i\) and nonzero regret under the audited world \(T\). HG-01's one-coordinate witness has subjective `ally=1`, `wait=0`, objective `ally=-1`, `wait=0`, and goal `trust=1`. Choosing `ally` gives subjective regret 0 and objective regret 3. This discrepancy diagnoses **model mismatch conditional on that goal**, and cannot alone establish deception, irrationality or the actor's actual preferences.

## 5. Compactification stability and the critical threshold

Suppose a projection keeps coordinates \(J\) and discards the rest. Write full squared distance \(C_a=P_a+E_a\), where \(E_a\ge0\) is the omitted squared energy. Let \(a_*\) be a unique full-space minimizer, with gap \(\Delta=\min_{b\ne a_*}(C_b-C_{a_*})>0\). Let \(R=\max_aE_a-\min_aE_a\).

**HG-01/T3 (projection margin; algebraic inequality).** If \(\Delta>R\), the projected costs retain \(a_*\) as unique minimizer. For any rival \(b\),
\[
P_b-P_{a_*}=(C_b-C_{a_*})-(E_b-E_{a_*})\ge\Delta-R>0.
\]

This is a sufficient certificate, not a necessary condition. The reference stable example has gap \(24/25\), omitted-energy range \(1/25\). A second exact witness changes the winner under projection when the sufficient condition fails. One-action menus are stable by convention; tied full winners cannot receive a unique-winner certificate. In a learned SAE/looped-transformer observer, register the projection and scaling before using this test to make a causal statement.

## 6. EvalMath alignment and evidence boundaries

- **BPD-01:** minimum test collection on hypothesis pairs, robust ties, and explicit `no_hypothesis_fits`; higher-order policy trees remain future work.
- **IRC-02:** an observer's information determines distinguishable future signatures. HG-01's blind nullspace is one-step preference equivalence and should not be confused with IRC-02's all-policy dynamic quotient.
- **FAW-03:** latent-state and channel identifiability require appropriate repeated observations; labels revealed after a decision cannot be considered pick-time knowledge.
- **Evaluation game testbed:** compare objective regret and prospective action quality to explicit baselines, not to polished rationale strings.

### What the receipt supports

The CPU verifier validates 140-feature exact metric arithmetic, one-pass and two-pass finite goal inference, rank/nullity, two-probe minimum cost, p/p2 observer isolation, 16-axis diplomacy projection, and a strict hidden-reveal noninterference test. It also runs the 12-test adversarial suite, including direct small matrix and tensor checks. The synthetic fixture is source-locked and deterministic; its candidates and decisions were designed for mechanism demonstration. No learned goal, unseen-world generalization, causal SAE transfer, or Lean kernel verification has been established.

### Next experiment

Read-only export from the actual GPTStoryworld engine must supply counterfactual successor tables for every legal action at a frozen state, per-agent subjective games, and exact seen/unseen fields. Then test new storyworld generators and hidden endings with the HG-02 protocol in `Hypergames/PROTOCOL.md`, including fixed-first-legal and capability-state baselines. A finite-horizon stochastic hypergame needs a Bellman value operator, priors over opponent games, and an intervention design respecting the actor's information filtration. The distance-only pilot deliberately stops at deterministic one-step behavior.

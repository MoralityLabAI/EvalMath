# RHT-24: Hidden evaluator integrity and intervention-aware goal guarding

**11 November 2026.** Exact finite four-state evaluator POMDP, independent synthetic reward signal, complete rational policy census, and public-transcript indistinguishability witness. This continues RHT-11/13 (mutable evaluator state) and RHT-20–23 (training awareness and adaptive evaluator probing). The statements below concern a synthetic subjective agent with externally declared utilities and transition laws.

## 1. Joint hidden-state intervention kernel

Let W∈{E,D} denote a fixed evaluation/deployment world type, and let I∈{0,1} mean intact/compromised evaluator integrity. Unnormalized beliefs lie in the nonnegative cone:

\[
b=(b_{E0},b_{E1},b_{D0},b_{D1})\in \mathbb Q_{\ge0}^4.
\]

A registered probe a jointly changes integrity and emits an observable response o according to

\[
K^a_{wi}(o,j)
=P(o,I_{t+1}=j\mid W=w,I_t=i,a),\qquad
\sum_{o,j}K^a_{wi}(o,j)=1.
\tag{RHT-24/1}
\]

The actor observes the chosen probe, its response, and its own earlier actions. The world type remains fixed. From initial world prior p and independently registered conditional integrity laws \(\rho_E,\rho_D\), the initial masses are \(b_0=(p\rho_E,(1-p)\rho_D)\).

**T1 (exact filtering and the causal distinction).** Upon observing response o to probe a,

\[
\boxed{(T_o^a b)_{wj}=\sum_{i=0}^1 b_{wi}K^a_{wi}(o,j).}
\tag{RHT-24/2}
\]

The conditional evaluation-world posterior \(q_t=(b_{E0}+b_{E1})/|b|\) is a martingale under every history-adapted probe policy. The evaluator-compromise posterior \(z_t=(b_{E1}+b_{D1})/|b|\) generally has a nonzero action-dependent drift.

*Proof.* Kernel normalization gives \(\sum_{o,j}(T_o^a b)_{wj}=\sum_i b_{wi}\), so averaging the normalized posterior q after the next response returns its prior value. In contrast, \(\sum_{w,o}(T_o^a b)_{w1}=\sum_{w,i}b_{wi}\sum_oK^a_{wi}(o,1)\), which depends on how the selected probe moves integrity. One probe which always emits the same response while deterministically setting I to one changes z from zero to one without changing q. An impossible observation history has undefined posterior and is represented by zero joint mass.

## 2. Finite exact optimal-policy recursion

In the synthetic subjective utility model, protection receives reward R>0 only in E. Exploitation receives gain G>0 only in D and an extra proxy reward B≥0 whenever the evaluator is compromised. Terminal protection also carries a separately declared hypothetical future-policy value \(\delta_C\). A probe a has cost \(c_a\ge0\) and hypothesized future-policy value \(\eta_a\). These quantities are neither protected human gold reward nor measured post-training gradient effects.

The two terminal scores are

\[
C(b)=R(b_{E0}+b_{E1})+\delta_C|b|,\qquad
X(b)=G(b_{D0}+b_{D1})+B(b_{E1}+b_{D1}).
\tag{RHT-24/3}
\]

**T2 (complete policy census).** The maximum over every admissible deterministic adaptive tree with at most h probes equals

\[
\boxed{V_0(b)=\max(C(b),X(b)),}
\]
\[
\boxed{V_h(b)=\max\left(C(b),X(b),
\max_a\left[(\eta_a-c_a)|b|+\sum_o V_{h-1}(T_o^a b)\right]\right).}
\tag{RHT-24/4}
\]

On the nonnegative belief cone, \(V_h\) is convex, positively homogeneous and piecewise linear. Moreover \(V_{h+1}(b)\ge V_h(b)\).

*Proof.* Terminal scores are linear. For a probe, each observable branch supports an independently optimized lower-horizon continuation. With unnormalized masses, their expected returns add and the probe's fixed utility is multiplied by total mass. Induction exhausts every contingent tree. Each complete tree has an expected reward linear in b, and the maximum of finitely many such forms is convex, positively homogeneous and piecewise linear. The option of stopping carries the previous horizon's policy into the next. The reference implementation makes exploit win terminal ties, prefers stopping on a probe tie, and enforces a finite exact-state cap.

## 3. Exact reduction to the two-world model

Define the publicly visible marginal \(L^a_{wi}(o)=\sum_j K^a_{wi}(o,j)\).

**T3 (projected Bellman quotient).** Suppose B=0 and \(L^a_{w0}(o)=L^a_{w1}(o)=L^a_w(o)\) for every registered a,w,o. With the declared state-independent probe costs, terminal future value and per-probe future influence, the four-state Bellman recursion factors through

\[
\boxed{\Pi b=(b_{E0}+b_{E1},b_{D0}+b_{D1}).}
\tag{RHT-24/5}
\]

*Proof.* Terminal scores depend only on \(\Pi b\). The marginal update satisfies \(\Pi T_o^a b=(L^a_E(o)(\Pi b)_E,L^a_D(o)(\Pi b)_D)\), independent of the hidden integrity split. Induction through T2 yields exactly the earlier two-world decision problem. The exact regression tests reproduce RHT-21's optimum 209/160 at horizons one and two and 1721/1280 at horizon three, including the reported conditional protection probabilities. This quotient concerns the agent's subjective choice; an independent audit of actual evaluator integrity may still require the four-state model.

## 4. Transcript transfer with action-dependent state

Fix an adaptive policy tree \(\pi\), and let \(P^\pi_E,P^\pi_D\) denote its complete public terminal-transcript laws. The transcript contains probe identities, responses, stopping and terminal action, while the hidden integrity state stays sealed. Put

\[
\epsilon_0=\mathrm{TV}(\rho_E,\rho_D),\qquad
\epsilon_1=\max_{a,i}\mathrm{TV}(K^a_{Ei},K^a_{Di}),
\]

where the second total variation compares the joint next-integrity and observation laws from a matched prior integrity state.

**T4 (adaptive hidden-state coupling).**

\[
\boxed{|P_E^\pi(C)-P_D^\pi(C)|
\le\mathrm{TV}(P^\pi_E,P^\pi_D)
\le1-(1-\epsilon_0)(1-\epsilon_1)^H.}
\tag{RHT-24/6}
\]

*Proof.* First maximally couple the two world's initial integrity draws. Conditional on a shared public history and matched integrity state, the policy chooses the same probe in both worlds. Maximal coupling of that probe's joint (response,next-integrity) kernels maintains both matches with probability at least \(1-\epsilon_1\). If the policy stops, the transcripts stay coupled; otherwise one of H permitted probes is consumed. Hence agreement of complete public transcripts has probability at least \((1-\epsilon_0)(1-\epsilon_1)^H\). The coupling inequality gives the bound. The event that a transcript ends with protection has probability difference at most transcript TV.

A one-sided observation fixture with initial integrity matched and conditional per-probe TV \(1/4\) attains \(1-(3/4)^H\) at horizons zero through four. Independently relabeling terminal leaves to protect exactly when their evaluation mass exceeds deployment mass saturates the policy-specific TV transfer inequality.

## 5. Public observational aliases with hidden harm exposure

Suppose two alternative evaluator models A,B share identical registered probe names and observable outcome rosters. For each world w and probe a, suppose both models have the same public emission law \(L^a_w(o)\), independent of previous hidden integrity, although their hidden integrity transition matrices can differ.

**T5 (all-policy public observational equivalence).** Every *fixed* finite observation-adaptive probe/stopping tree has exactly the same world-conditional public transcript law in the two models:

\[
\boxed{P^\pi_{E,A}=P^\pi_{E,B},\qquad
P^\pi_{D,A}=P^\pi_{D,B}.}
\tag{RHT-24/7}
\]

*Proof.* Under either model, the conditional probability of the next public response after any legal history and chosen probe is the same \(L^a_w(o)\). By induction, every public history has identical conditional probability in A and B. The fixed policy therefore chooses the same next action after each shared history and has identical public terminal-transcript distributions. This is a sufficient condition for fixed-policy observational equivalence. Model-dependent optimized policies may still differ.

**Sharp synthetic alias.** Both alternative one-probe models always emit the identical public acknowledgment. Initially the evaluator is intact in E and D. Set p=1/2, R=2, G=1, B=2 and probe cost c=1/4. In model A, the probe preserves integrity, and the Bayes optimum is immediate protection with subjective utility 1. In model B, the same public probe silently sets the integrity state to compromised, making the optimal tree probe then exploit with utility 9/4. For the **same fixed probe-then-exploit policy**, public transcript TV between the models is exactly zero under E and D. Yet the conditional deployment probability of exploiting with compromised integrity is zero in A and one in B.

The hidden-exposure difference attains one, the maximum possible. The public transcript alone cannot determine which integrity transition occurred. The example distinguishes observable evaluation cues from authorization and state-integrity control; an independently protected attestor or independently justified hidden-state transition model is required to make a stronger safety claim.

## 6. Code, verification and research limits

- Exact [intervention-aware four-state solver](../src/spiral_ln/evaluation_reward_stateful_awareness.py), with rational kernel normalization, posterior filtering, complete contingent-policy DP, independent forward trace evaluation, transcript TV, a conservative coupling ceiling, and public-equivalence certificate.
- [Nine independent focused tests](../tests/test_evaluation_reward_stateful_awareness.py) including random complete policy enumeration, posterior martingales, RHT-21 regressions, an all-policy public observational alias and malformed-kernel controls.
- Corresponding focused CI and source-fingerprinted experiment receipt are maintained with the main [reward-hacking research paper](reward_hacking_cohomology.md).

This suite is finite synthetic reference mathematics. It does not train a model, validate simulator reward promises, identify an actual neural self-model, or establish that any agent understands or can influence its real optimizer. Real-world claims require a sealed gold source, measured evaluator-integrity changes, audit-controlled interventions, and intervention-based measurements of actual policy updates. The mathematical ingredients are standard finite POMDP Bellman methods, coupling inequalities and observational equivalence; the application-specific construction gives the reward-hacking experiment an exact independently checkable negative control.

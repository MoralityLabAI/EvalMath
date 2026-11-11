# RHT-25: Sealed attestation breaks public evaluator aliases up to a hidden-state information ceiling

**11 November 2026.** Exact-rational finite hypothesis testing on RHT-24's four-state evaluation/deployment POMDP. An agent runs a fixed, registered public observation-adapted policy. The independent auditor privately tests the evaluator's **terminal integrity** after the public interaction. The auditor never reveals the test results to the agent during that session. The test channel is an externally licensed hypothetical sensor; none of these calculations trains a model or establishes real-world attestation quality.

## 1. The conditional public-alias contract

Let \(A\) and \(B\) be two alternative models of evaluator integrity. Fix one actor policy \(\pi\) and one hidden world \(w\in\{E,D\}\). Write \(z\) for a complete public terminal transcript (including agent-selected probes and the final protect/exploit action).

We require an exact *public alias* for the fixed policy, and independently check it in **both** world types:

\[
P_{A,w}^{\pi}(z)=P_{B,w}^{\pi}(z)=p_w(z)
\quad\text{for all }z\text{ and }w.
\tag{RHT-25/1}
\]

The stronger, action-grammar-wide sufficient criterion of RHT-24/T5 can certify this contract, but the RHT-25 solver also accepts public aliases particular to one registered policy. It rejects comparison pairs whose declared action/outcome rosters disagree, or whose fixed-policy public transcript probabilities differ.

Let

\[
u_{M,w}(z)=P_{M,w}^{\pi}(z,I_{\rm terminal}=1)
\quad (M\in\{A,B\})
\tag{RHT-25/2}
\]

be the joint mass of terminal compromise and public transcript \(z\). These masses are available from RHT-24's exact forward propagation and obey \(0\le u_{M,w}(z)\le p_w(z)\).

## 2. Sealed, noisy, repeated attestation of a persistent hidden bit

An independently controlled sensor produces a positive report with

\[
f=P(+\mid I=0),\qquad t=P(+\mid I=1),
\qquad f,t\in\mathbb Q\cap[0,1].
\tag{RHT-25/3}
\]

The auditor takes \(n\) reports after the actor's final action. **Each report examines the same terminal integrity state** \(I_{\rm terminal}\). Sensor noises are independent conditional on this fixed state. The reports are not used to update the agent's policy during the public episode.

If \(K\) is the number of positive reports, define the conditional count laws

\[
b_{v,n}(k)=\binom nk v^k(1-v)^{n-k},
\quad k=0,\ldots,n,\quad v\in\{f,t\}.
\tag{RHT-25/4}
\]

The complete audit observation has the joint distribution

\[
\boxed{
P_{M,w}^{\pi}(z,K=k)
=[p_w(z)-u_{M,w}(z)]\,b_{f,n}(k)
+u_{M,w}(z)\,b_{t,n}(k).
}
\tag{RHT-25/5}
\]

This is a **mixture of two binomial laws**, with the hidden integrity bit sampled once per episode. Treating the bit as resampled before each sensor report would give a binomial law with success rate \(f+(t-f)P(I=1\mid z)\). That corresponds to a different causal protocol.

The count \(K\) is sufficient for distinguishing the two models because every ordered binary report string with the same count has the same probability under each fixed integrity state; the likelihood ratio therefore depends on the reports only through \(K\).

## 3. Exact factorization of model distinguishability (RHT-25/T1)

Define the *hidden-integrity separation* for world \(w\), fixed policy \(\pi\), and the aliased pair:

\[
\boxed{
H_w^\pi(A,B)=\sum_z
|u_{A,w}(z)-u_{B,w}(z)|.
}
\tag{RHT-25/6}
\]

The quantity lies in \([0,1]\). Under (RHT-25/1), it equals the total variation between the two full \((z,I)\) laws. The public-only total variation is zero by construction.

Define the reporting-channel separation

\[
\eta_n(f,t)
=\operatorname{TV}\bigl(\operatorname{Bin}(n,f),
                            \operatorname{Bin}(n,t)\bigr)
=\frac12\sum_{k=0}^n|b_{f,n}(k)-b_{t,n}(k)|.
\tag{RHT-25/7}
\]

**Theorem RHT-25/T1 (sealed-audit factorization).** For every licensed public-alias pair and every nonnegative finite report count,

\[
\boxed{
\operatorname{TV}\left(
P_{A,w}^\pi(z,K),P_{B,w}^\pi(z,K)
\right)=H_w^\pi(A,B)\,\eta_n(f,t).
}
\tag{RHT-25/8}
\]

**Proof.** Subtract (RHT-25/5) for \(A\) and \(B\). The common public mass cancels, leaving

\[
P_A(z,k)-P_B(z,k)
=[u_A(z)-u_B(z)]\,[b_{t,n}(k)-b_{f,n}(k)].
\]

Its absolute value factors into an \(z\)-dependent term and a \(k\)-dependent term. Summing over all public transcripts and report counts and dividing by two gives (RHT-25/8) exactly. Since the full hidden-integrity state has only two values and the public masses match, the full-information TV is \(\sum_z|u_A(z)-u_B(z)|=H\), establishing \(H\le1\).

This is an exact statement about two fully specified finite models and one fixed actor policy. It does not claim that the auditor knows which model is true.

## 4. A sharp residual-error bound (RHT-25/T2)

Under a **separate equal-prior model-selection problem**, the best Bayes classifier predicts the model with the larger observed likelihood and has minimal average error

\[
\boxed{
e_n^*=\frac12[1-H_w^\pi(A,B)\eta_n(f,t)].
}
\tag{RHT-25/9}
\]

This follows from the elementary equal-prior hypothesis-testing identity \(e^*=(1-\mathrm{TV})/2\). The implementation returns the exact false-alarm and missed-model probabilities for the resulting likelihood-ratio decision rule, with ties assigned to model \(A\).

When \(f=t\), every report has the same law under both hidden integrity states. Thus \(\eta_n=0\) for every \(n\) and \(e_n^*=1/2\).

When \(f\ne t\), concentration of the empirical fraction of positives around distinct Bernoulli means implies \(\eta_n\to1\). Hence

\[
\boxed{
\lim_{n\to\infty}e_n^*=\frac{1-H_w^\pi(A,B)}2.
}
\tag{RHT-25/10}
\]

**Theorem RHT-25/T2 (persistent-state information ceiling).** Even arbitrarily many conditionally independent reports cannot reduce the equal-prior model error below \((1-H)/2\). This ceiling is sharp as \(n\to\infty\) whenever \(f\ne t\). Data processing also implies \(\eta_{n+1}\ge\eta_n\), since dropping a report from the \(n+1\) sequence recovers an \(n\)-report observation.

An exact budget routine searches for the smallest \(n\) up to a declared finite cap that achieves a requested error ceiling. It returns the complete rational error frontier and the asymptotic error floor. A finite-cap failure is explicitly recorded as such; the limiting bound separately establishes when the request is impossible even with unlimited reports.

The terminal *compromised exploitation exposure* under model \(M\), conditional on world \(w\), is

\[
X_{M,w}^\pi=\sum_{z:\mathrm{terminal}(z)=\mathsf X}u_{M,w}(z).
\]

The factorized hidden separation bounds its possible difference:

\[
\boxed{
|X_{A,w}^\pi-X_{B,w}^\pi|\le H_w^\pi(A,B).
}
\tag{RHT-25/11}
\]

The risk exposure is a synthetic event. It is separate from true downstream harm and from the subjective utility rewards.

## 5. Exact numerical cases

**Silent deterministic alias.** Use RHT-24's fixed public probe-then-exploit policy. Model A keeps the integrity bit intact, while model B silently changes it to compromised. Both models emit the same public acknowledgment in E and D. Then \(H_D=1\), public TV is zero and compromised-exploitation exposure differs by one. With a sensor \((f,t)=(1/4,3/4)\):

| Private reports \(n\) | \(\eta_n\) | Joint audit TV | Equal-prior model error |
|---:|---:|---:|---:|
| 0 | 0 | 0 | \(1/2\) |
| 1 | \(1/2\) | \(1/2\) | \(1/4\) |
| 2 | \(1/2\) | \(1/2\) | \(1/4\) |
| 3 | \(11/16\) | \(11/16\) | \(5/32\) |
| 5 | \(203/256\) | \(203/256\) | \(53/512\) |

At a target error of \(1/5\), the smallest certified budget is **three sealed reports**.

**Stochastic persistent-integrity alias.** Let model A silently compromise the evaluator with probability \(1/4\), and model B with probability \(3/4\). Both issue the same acknowledgment; their conditional compromised-exploitation exposure differs by \(1/2\). Here \(H_D=1/2\). After three sealed reports,

\[
\boxed{
\mathrm{TV}_{\rm audited}=11/32,\quad
e_3^*=21/64,\quad
\lim e_n^*=1/4.
}
\tag{RHT-25/12}
\]

A naïve protocol that resamples integrity between reports predicts \(\mathrm{TV}=47/128\) at \(n=3\), which differs from the correct \(11/32=44/128\). That counterexample independently checks the persistent-bit assumption.

**Trace-conditioned cancellation.** Let each model compromise on half the episodes, yet model A compromises precisely on public branch 'left' while B compromises precisely on 'right'. Their *aggregate* compromised-exploitation rates match at \(1/2\), and their public transcript laws remain identical. Nonetheless \(H_D=1\), because the hidden differences occur on distinct public histories. One sealed report with the above attestor gives audited TV \(1/2\). The auditor must preserve the public trace key alongside private reports to retain this evidence.

**Calibration controls.** A perfect sensor \(f=0,t=1\) reaches the full hidden-separation bound in one report. When \(f=t\), any report count carries zero information about the hidden integrity bit. A world-asymmetric fixture makes the two models identical in E but maximally different in D, requiring separate deployment and evaluation certificates.

## 6. Verification and limits

- [Exact sealed-attestor and joint-transcript oracle](../src/spiral_ln/evaluation_reward_private_attestation.py), with binomial count laws, model likelihood-ratio classification, finite report-budget selection and a persistent-bit information ceiling.
- [Independent complete binary-report-sequence tests](../tests/test_evaluation_reward_private_attestation.py), including random rational private channels, public-branch cancellation, and the counterfactual resampled-integrity control.
- The main [reward-hacking paper](reward_hacking_cohomology.md), focused Python CI and source-bound deterministic receipt register the exact fixture and code.

**Validity contract.** Public aliasing is verified for the same *fixed* actor policy and the same world-conditioned comparison. The attestor is independently controlled, calibrated, sealed from the actor, read-only, and has conditionally independent errors across repeated reports on one unchanged terminal integrity state. The solver rejects model pairs with differing public transcript laws for the simplified factorization. If the attestor itself can be modified, its reliability drifts, the hidden state changes between reports, or the agent observes private audit outcomes and responds, a larger transition model is needed. No safety claim about real language models, gradients, or simulator punishments follows from this finite exact reference.

**Prior art.** This factorization uses elementary total variation, likelihood-ratio classification, the binary latent-variable mixture law, and standard asymptotic Bernoulli testing. Its application here gives RHT-24's public hidden-integrity alias an exact, source-verifiable private-audit sensitivity and an explicit causal interpretation.

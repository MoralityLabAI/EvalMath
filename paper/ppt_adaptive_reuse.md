# PPT-EVAL-01: Posterior Prefix Tuning under adaptive sample reuse

**Draft 0.1 | 2 November 2026.** A Resolution/Timaeus × EvalMath crossover. The finite experiments and receipts in this note use exact rational arithmetic with no transformer calls. The general confidence inequality is an application of standard Hoeffding concentration. Neither the adaptive-data-analysis framework nor importance sampling is claimed as a new invention. **No Lean proof and no empirical BFT result are claimed.**

**Source:** Garrett Baker, Vinayak Pathak, Daniel Murfet, Susan Wei, [*Elicitation without Backpropagation: Steering Model Behavior by Optimizing the Latent Posterior*](https://arxiv.org/html/2607.18804) (2026), [official code](https://github.com/timaeus-research/elicitation). Related EvalMath work: [selection-risk continuations](selection_risk_continuations.md), [stochastic full-filtration feedback](stochastic_full_filtration.md), [dynamic-filtration validity](dynamic_filtration_validity.md), [selection-KL containment](selection_law_kl_containment.md), and [feedback running-max effects](evaluation_feedback_multigen.md).

## 1. The claim that sample reuse puts under pressure

For a latent prior \(P\), a prompt kernel \(\kappa\), and continuation utility \(U\in[0,1]\), PPT defines a nonnegative tilt \(W_{\kappa}(k)\) and utility \(\bar\mu_{U,\kappa}(k)\in[0,1]\). Its continuous surrogate is

\[
J_{\rm tilt}(\kappa,U)=\frac{A_{\kappa,U}}{B_\kappa},\qquad
A_{\kappa,U}=\mathbb E_P[W_\kappa(k)\bar\mu_{U,\kappa}(k)],\quad
B_\kappa=\mathbb E_P[W_\kappa(k)]>0.
\]

On an iid, utility-independent latent sample bank \(S=(k_1,\ldots,k_L)\), PPT uses the self-normalized importance sampling (SNIS) estimator

\[
\widehat J_S(\kappa,U)=\frac{\widehat A_S(\kappa,U)}{\widehat B_S(\kappa)},\qquad
\widehat A=\frac1L\sum_i W_\kappa(k_i)\bar\mu_{U,\kappa}(k_i),\quad
\widehat B=\frac1L\sum_i W_\kappa(k_i).
\]

The gradient of this sampled ratio is reused for each optimization update, so the output \((\widehat\kappa,\widehat U)\) generally depends on \(S\). PPT's utility-independent *cost of constructing* the sample bank does not make a selected utility or prompt independent of that bank. A pointwise concentration claim for a fixed \((\kappa,U)\) cannot be applied unchanged to the post-selected pair. Furthermore SNIS has finite-sample ratio bias even before adaptive selection.

The paper records \(\mathrm{ESS}=(\sum_i W_i)^2/(\sum_i W_i^2)\) as a weight-collapse diagnostic. ESS concerns the spread of weights at a fixed query. **It does not account for search over utilities or prompts.** This distinction can be seen with *perfect* ESS.

## 2. Exact witness A: two utilities, perfect ESS, 12.5-point optimism

Let \(k\) be a Bernoulli probability \(p\) taking values \(1/4\) or \(3/4\) with equal prior probability. This is a valid finite exchangeable \(k=0\) BFT prior. Take the binary PPT prompt kernel \(\alpha(1)=\alpha(0)=1/2\), with *any* positive prefix length \(m\). Eq. (8) of Baker et al. becomes

\[
W(p;\alpha)=((1-\alpha)(1-p)+\alpha p)^m=2^{-m},
\]

which is constant across every latent draw, so \(\mathrm{ESS}=L\) exactly. Use two fixed, predeclared utilities on a one-symbol continuation: \(U_+(Y)=\mathbf1[Y=1]\) and \(U_-(Y)=\mathbf1[Y=0]\). Their latent conditional utilities are \(p\) and \(1-p\); their *true* surrogate objectives are both \(1/2\). For two prior samples, the in-bank selector picks whichever utility has higher estimated score.

\[
\mathbb E_S\left[\max\bigl(\widehat J_S(U_+),\widehat J_S(U_-)\bigr)\right]
=\frac58,\qquad
\max_U J_{\rm tilt}(U)=\frac12.
\]

The exact expected selection optimism is \(1/8=12.5\) percentage points, even with \(\mathrm{ESS}/L=1\) on every sample bank. If a false-improvement event means \(\widehat J_S(U)-J(U)\ge1/4\), either *fixed* utility has probability \(1/4\) of such an event. The utility selected after reading the bank has probability \(1/2\).

For general \(L\), write \(p_i=1/2+\xi_i/4\) with independent signs \(\xi_i\in\{-1,+1\}\). Then the selected-score optimism is exactly

\[
\mathbb E_S\left[\max_U\widehat J_S(U)\right]-\frac12
=\frac{1}{4L}\,\mathbb E\left|\sum_{i=1}^L\xi_i\right|
=\sum_{r=0}^L\frac{\binom Lr}{2^L}\frac{|2r-L|}{4L}.
\]

**Evidence:** algebraic identity and an independent enumeration of all \(2^L\) banks for \(1\le L\le7\). This witness isolates *post-selection* from importance-weight degeneracy.

## 3. Exact witness B: fixed utility, adaptive choice between prefixes

For a second binary \(k=0\) PPT, let the latent prior be uniform over \(p\in\{1/8,3/8,5/8,7/8\}\). Fix the two-token utility \(U(Y_1,Y_2)=\mathbf1[Y_1\ne Y_2]\), whose conditional mean is \(\mu(p)=2p(1-p)\). Compare the predeclared prompt kernels \(\alpha\in\{0,1\}\) with prefix length \(m=1\). By prior symmetry their true objectives coincide:

\[
J_{\rm tilt}(\alpha=0)=J_{\rm tilt}(\alpha=1)=\frac{11}{32}.
\]

With two iid prior draws, the exact, self-normalized estimate for a *fixed* prefix has expectation \(113/320\), whereas choosing the higher estimated prefix gives

\[
\mathbb E_S\max_{\alpha\in\{0,1\}}\widehat J_S(\alpha)
=\frac{73}{192}.
\]

Of the total optimism \(\frac{73}{192}-\frac{11}{32}=\frac7{192}\), the increment **specifically due to choosing the prefix** is \(\frac{73}{192}-\frac{113}{320}=\frac{13}{480}\). At a false-improvement threshold \(1/16\), the risk is \(1/2\) for each predetermined prefix, and \(3/4\) for the adaptively selected prefix. This identifies a genuine prefix-selection effect with the utility fixed; the remaining optimism in the fixed estimator is the SNIS ratio effect.

**Evidence:** exact enumeration of all 16 two-sample worlds, with rational outcomes. These toy priors and utility families are deliberately small, and the numbers are not predictions for the paper's trained models.

## 4. Certified solution A: simultaneous finite-class bounds

Let \(\mathcal C\) be a **precommitted**, finite class of \(M\) candidate prompt/utility pairs, independent of the bank. Assume each \(k_i\overset{\rm iid}\sim P\), \(0\le W_c(k)\le1\), \(0\le\mu_c(k)\le1\) and \(B_c=\mathbb E W_c>0\). The empirical numerator \(\widehat A_c\) and denominator \(\widehat B_c\) are means of bounded iid variables. Hoeffding and a union bound yield

\[
\Pr\left(\forall c\in\mathcal C:\ |\widehat A_c-A_c|\le\epsilon\ \text{and}\ |\widehat B_c-B_c|\le\epsilon\right)
\ge1-4M e^{-2L\epsilon^2}.
\]

In particular choose \(\epsilon=\sqrt{\log(4M/\delta)/(2L)}\). On this simultaneous event, **every** candidate, including any candidate selected adaptively from this precommitted class, obeys the explicit ratio interval

\[
J_c\in\left[
\max\!\left(0,\frac{\widehat A_c-\epsilon}{\widehat B_c+\epsilon}\right),
\quad
\begin{cases}
\min\!\left(1,\frac{\widehat A_c+\epsilon}{\widehat B_c-\epsilon}\right)&\widehat B_c>\epsilon,\\
1&\widehat B_c\le\epsilon.
\end{cases}
\right].
\]

The interval is deterministic given the event; its *probability* follows from the uniform inequality. The denominator condition is important: long prefixes can make \(B_c\) extremely small, leaving a valid but vacuous interval. A bound on ESS alone does not rescue denominator collapse. Tighter bounded-variance, clipping-aware and structured-covering bounds are research extensions, subject to their own assumptions. The count \(M\) means the *entire eligible class*, not merely the number of adaptively visited prompts. A continuously optimized prompt family needs complexity control or separate validation.

**Evidence:** standard concentration result (cited mathematical technique) and a finite exhaustive check of the implication from simultaneous numerator/denominator accuracy to all-candidate interval coverage. The verifier enumerates \(4^3\) worlds for an illustrative three-candidate family. No general Lean proof is yet attached.

## 5. Certified solution B: independent latent-bank or model-rollout validation

Maintain two disjoint data roles:

- **Exploration bank E:** derive posterior samples, take as many PPT gradient steps as desired, alter the utility, choose and snap a prompt. Exploratory scores and ESS stay visible, labelled *training/exploration*.
- **Validation bank V:** independently sample new latents after the candidate is fixed, then evaluate that single chosen pair. Conditional on E and the recorded candidate, a one-candidate concentration interval applies on V. This avoids paying \(\log M\) for a large exploratory search.

Validation can reuse V for a **precommitted finite family with simultaneous coverage**, or follow a rigorously specified adaptive-holdout mechanism that controls information released to the optimizer. Repeatedly exposing its individual scores makes the validation bank part of the adaptive search. When allowing repeated fresh validations indexed by \(t\), assign conditional failure budgets \(\delta_t\) with \(\sum_t\delta_t\le\delta_{\rm total}\). EvalMath's [full-filtration](dynamic_filtration_validity.md) warning applies: conditional validity must cover *everything the selector has seen*, including off-ledger peeks and score leaks.

For an actual **hard prompt** \(z\), validate the hard-prompt posterior ratio using \(W_z(k)=\prod_{t=1}^m k(z_t\mid z_{<t})\) and \(\mu(k;z)\), rather than treating the continuous PPT surrogate \(J_{\rm tilt}(\kappa)\) as though it were \(J(z)\). The original work does not guarantee snapping is optimal. A genuine transformer-continuation claim needs an independent bound or check of the trained BFT's discrepancy from the exact Bayes mixture, plus PMC error. Without those checks, report a bound for the *idealized latent model* only.

A release field `J_minus_latent` can carry the valid lower ratio endpoint for the declared class and prior; a `J_minus_model` field is eligible only after recording an appropriate certified model discrepancy allowance. An unknown model discrepancy means the latter stays `uncertified`.

## 6. EvalMath-specific accounting and experimental plan

The existing [selection-risk continuation model](selection_risk_continuations.md) treats the sample bank as a finite null world, utility/prefix scores as feedback queries, and false optimism events as selectable claims. Its equation \(\mathcal R(T)=\sum_t\max_j P(E_j,T=t)\) gives an *exact* risk for a finite feedback transcript. The two exact witnesses here instantiate that mechanism; the dynamic-filtration work supplies the stricter stopping and provenance question for a controller that may learn private information before deciding when to accept a result.

For a trained-model follow-up, start with the public `timaeus-research/elicitation` Beta–Bernoulli 34K and reinforced-urn 11.4M checkpoints. Compare PPT, PPT-RB and analytic-prior controls; use the authors' actual PMC implementation and record generation length, sample count, sampler seed and weight profile. Sweep prefix lengths \(m\in\{6,50\}\), prior-bank sizes \(L\in\{256,1024,5000\}\), and predeclared utility families of sizes 1, 8 and 32. Use multiple independent seeds and log all optimization steps, ESS trajectories, candidate/utility selection, training-bank score, fresh-bank score, snapped-prompt score and model-vs-mixture discrepancy where measurable. Compare uncertified SNIS reporting, a finite-class bound, and independent held-out certification. Include an adaptive family that deliberately hunts Monte Carlo noise as an adversarial control.

**Failure criteria:** a claimed nominal coverage level missed on independent replications; a positive `J_minus_model` without a measured model-error allowance; a fixed-bank generalization claim that conditions only on *visited* adaptive prompts; or a reported lower bound for a snapped hard prompt derived solely from the continuous surrogate. ESS and confidence interval width should be recorded independently.

## 7. Reproduce the current exact result

```bash
PYTHONPATH=src python -m pytest -q tests/test_evaluation_ppt_reuse.py
PYTHONPATH=src python scripts/verify_evaluation_ppt_reuse.py
python scripts/check_receipts.py --only ppt_reuse
```

Paths: `src/spiral_ln/evaluation_ppt_reuse.py`, `tests/test_evaluation_ppt_reuse.py`, `scripts/verify_evaluation_ppt_reuse.py`, and `output/evaluation_ppt_reuse/ppt_reuse_v0_1.json`. The receipt contains source hashes and 12 exact checks; the test suite adds direct enumerations and invalid-input controls. It supplies synthetic evidence only.

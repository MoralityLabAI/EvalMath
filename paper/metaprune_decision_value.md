# MP-01: Research-direction selection as a finite decision problem

**Status:** 2026-11-04 draft mathematical note, with a dependency-free exact rational reference and tests. Propositions below are elementary and proved under their stated finite assumptions. The new application to compact AI research controllers is a *proposal*. No agent, model, or scientific discovery run is claimed. Source-dependent experiments remain to be conducted.

## Why this belongs in EvalMath

A 2026 public video on continual learning and metacognition (user-provided transcript, 2026-11-04, ~11:43–21:40) argues that a research agent's bottleneck is judging which experiments deserve resources. A separate Michael Levin interview series motivates reuse of latent competence across embodiments. This note gives the **decision-theoretic** part a clean finite contract.

See existing [adaptive selection risk](selection_risk_continuations.md), [validity under the actor's filtration](dynamic_filtration_validity.md), and [interface-relative compactification](interface_relative_compactification.md). MP-01 optimizes *learning value*; it does not certify the honesty of adaptively selected claims. Any statistical report selected by this policy must separately satisfy the full-filtration evaluation contract.

## 1. Finite research game

Let Theta={0,...,m-1} be mutually exclusive hypotheses with rational prior p. An available experiment e has positive integer cost c_e, finite outcome set O_e, and fully specified rational likelihood K_e(o|theta), summing to one for each theta. Upon observing o with positive predictive probability q_e(o)=sum_theta p(theta) K_e(o|theta), update

    p_e^o(theta) = p(theta) K_e(o|theta)/q_e(o).

At any time the controller may stop and make a *single* hypothesis choice. Under 0/1 correctness reward, terminal Bayes value is

    U(p)=max_theta p(theta).

There is a hard remaining integer budget b, and an optional additive price lambda*c_e per experiment. Outcomes and actions are fully observable, and the policy can adapt to them. No same-source independence assumption is made: each likelihood is conditional on the current declared hypothesis model.

**Proposition MP-01/T1 (Bellman optimum).** With V_0(p)=U(p), the maximum expected net utility from remaining budget b is

    V_b(p) = max{ U(p),
                  max_{e:c_e≤b} [sum_{o:q_e(o)>0} q_e(o) V_{b-c_e}(p_e^o)
                                 - lambda*c_e] }.                  (1)

**Proof.** The first choice is either stop or some affordable e. Conditioning on its observation gives an independent optimal continuation with strictly smaller remaining budget; backward induction proves (1). Randomizing the first choice is a convex combination and cannot improve its maximum. QED. Because all c_e are positive integers, recursion terminates.

**Proposition MP-01/T2 (nonnegative free information).** For lambda=0 and any experiment e,

    sum_o q_e(o) U(p_e^o) ≥ U(p).                                     (2)

**Proof.** Choose theta* maximizing p(theta). At every posterior the maximum is at least p_e^o(theta*). Taking expectations yields sum_o q_e(o)p_e^o(theta*)=p(theta*)=U(p). QED. Costs may make stopping optimal even when (2) holds.

This is the usual elementary Bayes value-of-information principle, **not** a novel general theorem.

## 2. Exact counterexample: entropy reduction can rank experiments incorrectly

Let Theta={0,1,2,3} with uniform prior. Both experiments cost 1.

- **Split A:** outputs L for theta∈{0,1}, R for theta∈{2,3}. Posterior is uniform on two candidates. Expected terminal success = 1/2; information gain = 1 bit.
- **Reveal B:** independently of theta, with probability 2/5 reveal theta exactly, and with probability 3/5 output "?". Expected success = (2/5)*1+(3/5)*(1/4)=11/20; information gain = (2/5)*2=4/5 bits.

Thus the experiment with **higher information gain** (A: 1 bit) has **lower terminal decision value** (A: 1/2) than B (4/5 bits but 11/20 success). The exact rational code tests these values under budget b=1.

This separates entropy reduction from optimizing the declared goal; it does **not** say entropy reduction is an invalid measure of information or that utility-only experiment choice is always preferable.

## 3. Auditing controller training

A meta-controller must predeclare a utility, budget, and observable filtration. Hypothesis posterior updates and finite Bellman optimization are mechanically reproducible for this toy class. When a learned controller chooses which evaluation outcomes to disclose, it inherits the adaptive selection risk in the existing EvalMath notes: a high V_b score supplies no type-I error guarantee.

A proper held-out evaluation compares, on **paired seeds** and identical total resources:
1. random affordable experiment selection;
2. myopic expected information gain;
3. myopic terminal Bayes utility;
4. exact finite-horizon Bellman choice;
5. a learned MetaPrune policy with parameters frozen before the held-out panel.

Report terminal decision accuracy, calibration, false-claim risk, stopping frequency, tokens or GPU-hour equivalents, and old-task regression after updates. Separately include mislabeled observation-source and correlated-source controls; independently attributed witnesses matter more than raw report count.

**Rejection gate:** a learned MetaPrune controller that fails to improve over the exact Bellman oracle on the *same known finite contract* has an implementation defect; a controller that matches Bellman only on the training families has not shown transfer.

## 4. Evidence and reproduction

- **Algebraic identity:** T1 and T2 with proofs above.
- **Finite verified example (upon test execution):** the four-hypothesis counterexample.
- **Experimental hypothesis:** learned research-selection policies can amortize judgment across tasks and reduce compute cost at fixed scientific validity.
- **Not established:** an AGI scaling law, a biological analogue of human intuition, or a fundamental lower bound on higher-order learning.

Run:

    PYTHONPATH=src python -m unittest discover -s tests -p test_evaluation_metaprune.py -v
    PYTHONPATH=src python scripts/verify_evaluation_metaprune.py

The verifier writes a local deterministic JSON receipt with hashes of the reference, test, and verifier. This PR does **not** contain a checked-in receipt or Lean formalization; both are review tasks before promoting the note to the repository's certified findings.

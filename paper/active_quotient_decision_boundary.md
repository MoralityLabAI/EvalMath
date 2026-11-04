# QI-04: Decision-boundary-aware evidence allocation for goal-preserving quotients

**2026-11-04.** This is the mathematical repair to the negative QO-09 transfer experiment. The [QO-09 receipt](https://github.com/MoralityLabAI/Compactification-Theory/blob/main/results/fractional_probe_pilot/receipt.json) establishes that an LP allocation optimized for an unrelated candidate family can be poor at certifying the actual quotient-feasibility decision. Here we construct candidate alternatives **by checking the real one-step quotient error** and use only the alternatives with the opposite decision label. The statistical lower bound is still conditional on the selected **candidate family**, which must be declared before collecting evaluation observations.

## Model and exact decision oracle

The declared micro-dynamics are named-state absorbing-goal hit/hold kernels. For n=3 transient states and d=2 actions, let rates \(p_{i,a}\in(0,1)\) describe the chance of hitting the separately observable goal; otherwise the process stays at named microscopic state i. For a partition \(\pi\) into at most k transient macrostate classes, the minimum worst-case one-step projected TV error is

\[
 D_P(\pi)=\frac12\max_{B\in\pi,\ a\in A}
 \left(\max_{i\in B}p_{i,a}-\min_{i\in B}p_{i,a}\right).
\]

The exact goal-preserving capacity decision at tolerance \(\tau\) is

\[
 {\sf Feasible}_k(P,\tau)\iff \min_{|\pi|\le k}D_P(\pi)\le\tau.
\]

The test universe fixes **k=1**, **\(\tau=1/5\)**, baseline Bernoulli rate **p=1/10** on each of the six state/action cells and changed rate **q=9/10**. The all-baseline table has exact optimal error zero. A perturbation of a strict nonempty subset of the three states in any one action has exact optimal TV error \((q-p)/2=2/5\) and therefore crosses the declared decision boundary.

The reference [independent exact oracle](../src/spiral_ln/evaluation_decision_boundary_allocation.py) enumerates every finite assignment of microscopic states to macrostate labels and evaluates its exact Fraction error. Its tests compare all **64** binary-change masks with an independent grid minimax calculation. Exactly **60 masks** produce an infeasible one-class quotient; the other four have constant rates down every action column and remain exactly feasible. A proposed counterfactual changing all three state rates in one action is rejected as same-decision evidence.

## A structured prior with an exact rational LP

A finite experimental model family is fixed before sampling. Number probe cells in state-major order \(c=2i+a\), where \(a=0,1\). The family contains six **opposite-decision** counterfactual tables:

- single-state rate changes in action 0, one for each microscopic state;
- pairwise rate changes in action 1, one for each of the three pairs of microscopic states.

For every candidate, the exact quotient oracle verifies error 2/5, exceeding tolerance 1/5. Let each changed-cell set be \(C_j\). Because every candidate cell changes from the same p to the same q, the KL divergence contributed by a probed changed cell is the same constant \(\kappa=\operatorname{kl}(p,q)>0\). The [QI-03 theorem](active_quotient_fractional_information.md) applies directly:

\[
 \mathbb E_0[N]\ge\frac{\operatorname{kl}(1-\delta,\delta)}
 {\operatorname{kl}(p,q)}\tau_f,
\qquad
 \tau_f=\min_{x\ge0}\Bigl\{\sum_{c=0}^{5}x_c:
   \sum_{c\in C_j}x_c\ge1\ \forall j\Bigr\}.
\]

With the six registered alternatives, the exact primal and dual optimum is

\[
 \boxed{
 x=(1,\tfrac12,1,\tfrac12,1,\tfrac12),
 \qquad\tau_f=\tfrac92.}
\]

Each singleton alternative forces one unit of action-0 weight. The three pair constraints in action 1 form the classical triangle fractional-cover witness with \(1/2\) weight at each endpoint. A dual certificate assigns unit weight to each action-0 singleton alternative and half weight to each action-1 pair alternative. Both objectives equal 9/2.

A **rotation control** permutes cell indices by half of the six-cell vector, transporting the alternative masks and the optimal allocation together. The resulting plan \(x=(1/2,1,1/2,1,1/2,1)\) remains an exact dual-certified optimum for *its separately declared opposite-decision candidate family*. It tests sensitivity to which action receives the higher sampling priority.

## Complete-family limitation: symmetry forces uniform probing

Suppose the scientific alternative family admits **every** nonempty binary mask that changes the quotient decision. In particular it includes the six single-cell perturbations. To distinguish all of these with the QI-03 KL constraints, every expected-count variable must satisfy \(x_c\ge1\). The uniform vector \(x=(1,\ldots,1)\) attains all 60 counterfactual covering constraints. Hence

\[
 \boxed{\tau_f^{\rm full}=6.}
\]

This is a useful *no-shortcut theorem*: a decision-aware objective alone yields no nonuniform sampling benefit if all named cells can independently hide the same decisive perturbation. The asymmetric 9/2 allocation **requires a structured, predeclared alternative prior**. It is possible to build an adaptive mixture over several families, but the QI-03 lower bound must then be recomputed for the actual composite contract.

## Statistical scope and experimental dispatch

Fix \(\delta=1/20\). Under the stated binary-incidence candidate-world model, an adaptive sequential decision rule with both errors at most \(\delta\) must satisfy the QI-03 KL-information floor based on \(\tau_f=9/2\). This is a **necessary expected-cost lower bound**, not an upper bound on sample complexity or a proof that any particular static sampling schedule attains it.

A matching QO-10 synthetic pilot must:
1. Freeze the structured alternative masks and primal/dual certificates before generating test Bernoulli outcomes.
2. Use a predictable static weighted-fair sampler based on x and compare it at matched query counts with QO-07's original round-robin, width and bottleneck methods, plus QO-09's unrelated fractional plan and this family's rotated null.
3. Test independently seeded **synthetic holdout rate tables**, including baseline-feasible, supported counterfactual-infeasible, and **out-of-family** action-1 singleton counterfactuals. Keep every unresolved decision, false certificate, confidence coverage failure and negative paired difference.
4. Continue to obtain honest three-valued confidence certificates from the QO-07 anytime beta-binomial ledger. LP optimality for the candidate-family discrimination problem does **not** authorize translating its bound into a confidence statement about arbitrary unknown rate tables.
5. Charge a runtime and program-size ledger before comparing total economic cost or proposing model-scale transfer.

The finite exact theory itself is reusable. General state identities, resettable IID hit/hold probes, and known action semantics remain prerequisites. No neural mechanism, mind, goal consciousness or biological form is observed or inferred.

**Reproduce:**

    PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_decision_boundary_allocation.py' -v

The referenced QI-03 rational LP oracle independently enumerates feasible primal and dual vertices; this note's test additionally runs a separate 3^6 half-integer allocation oracle. Published information-theoretic precedents are in [QI-03](active_quotient_fractional_information.md) and [QI-02](active_quotient_information_budget.md).

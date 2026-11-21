# EvalMath contract for Storyworld and Hypergames causal inclinations

## Observables and epistemic scope

A Storyworld model can contain (a) actual bounded character traits, (b) observer-indexed `pValues`, (c) observer-believer-target `p2Values`, (d) an exact posterior over latent generator states, and (e) real model action traces. Record each separately. `pValues` are authored first-order beliefs, **not** hypothesis-test p-values. `p2Values` may update after correlation-only evidence while the first-order marginals stay fixed. An exact posterior enumeration over `2^10=1024` synthetic worlds verifies a finite inference mechanism, while externally sampled world-generator roots govern generalization claims.

## Formula constraints

For a declared public feature vector `x` with `|x_i|<=1`, keep the authored response scores within an announced range:

\[
I_0(x)=\tfrac12+\sum_i\beta_i x_i+\sum_{i<j}\gamma_{ij}x_i x_j,
\qquad I_1(x)=1-I_0(x).
\]

The HGW-04 convention `sum(|beta|)+sum(|gamma|)<=0.34` guarantees `0.16<=I_j<=0.84`. This is a **bound on scripted inclination**, and by itself says nothing about calibrated choice probabilities or meaningful causal response. A probabilistic actor requires a separately specified choice mechanism, for example a softmax with temperature fitted only on development roots and evaluated by proper scoring rules. Track branch diversity, saturation, score margins and action selection on independent roots. Fit complexity budgets to actual named actors and causal edges. Preserve validity of storyworld endings independently of apparent consensus.

## Causal identification test

Specify an acyclic structural model with fixed exogenous root `U_r`, public inference features `M_r=f_M(U_r,E)`, and choices `A_r=f_A(M_r,C)` or stochastic equivalents. For matched interventions, replace the mechanism equation `do(E=e)`, carry the **same** `U_r` through candidate/sham arms, and recompute downstream public features. A causal input that changes `p2` while holding `p1` fixed helps distinguish higher-order reasoning; a sham changes an irrelevant but equal-dose coordinate. Record the predicted sign and the actual action flip separately. A source copied from an already counted report has the same provenance root and must never count as an independent information source.

If hidden generator state is visible to the grader, prove the policy prompt excludes it. Directly manipulating a belief feature rather than its evidence-generating cause is a different intervention and must be labelled accordingly. Causal structure in authored synthetic mathematics is a mechanism property of the simulator, with learned-agent causal claims requiring independent agent traces.

## Robustness and confirmation

- **Unit:** independent world-generator root, with all descendant episodes, prompts, agent samples and counterfactuals clustered together. For multi-model claims, also account for independently trained model seeds.
- **Effect:** register `d_r=Y_r(candidate,do(E))-Y_r(baseline/sham,do(E))` in an actual behavior metric, and a physical intervention dose. Make task success conditional on legal behavior and absence of critical actions.
- **Variation floor:** `max(scientific_min_effect, matched_sham_upper, measurement_resolution)` under the same dose and task population. The 95th-percentile matched-sham bound at 95% confidence requires **at least 59 independent calibration worlds** even if their maximum is used.
- **Budget:** run `evalmath-mechinterp-power/scripts/preflight.py --strict` before reading confirm worlds. Reject a null/zero-effect pilot that derives spurious normal-theory power from zero variance.
- **Selection:** preserve the complete adaptive search history, discarded weights and policies, nuisance seeds, generator-version locks and proposed hypotheses. Match developmental difficulty with predeclared mixing across causal types rather than refitting to confirmation.
- **Inference:** export `evaluation_finite_sample` paired binary cases grouped by root with a preregistered comparison family. Use matched-sham controls, Holm-adjusted comparisons and report effect-floor lower bounds. Repeat-policy reruns on the same roots are uncertainty diagnostics, not additional independent worlds.
- **Calibration:** prefer Brier or log score for declared belief probabilities, reported as macro world means with diagnostic confidence intervals. Check prediction errors by role, causal intervention, and posterior dependence. Preserve an exact separation between probability calibration and belief-vector magnitude.

## Required evidence for a benchmark climb

The report should say which variables are latent, which were inferred from public evidence, what intervention changes them, what independent roots were generated, how many worlds and task cases were scored, which endpoints and error budgets were frozen, whether the mechanism effect exceeded sham variation, and whether the agent chose legal actions. Include causal diagrams, baseline and sham traces, confidence intervals, model/generator/judge hashes, the preflight decision, source-provenance seals and the status of hidden confirmation data.

A benchmark win following development search stays a development result until fresh sealed roots are opened. A trained exact solver of a synthetic law is an algorithmic ceiling, with separate evidence needed to establish that a neural model learned the law.

## Reference implementation

`MoralityLabAI/GPTStoryworld`, branch `research/hgw04-causal-inclinations-evalmath-20261121`:
`codex-skills/hyperworld-builder/scripts/causal_inclinations.py` and
`scripts/benchmark_receipts.py` generate EvalMath-compatible development preflight and FSI-01 manifests. Their included eight-root and four-root fixtures explicitly fail confirmation requirements. Use the public test suite and CI integration to verify the manifests, and preserve the older Cairo Hyperworld fixtures unchanged.

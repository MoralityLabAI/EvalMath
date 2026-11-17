# Mechanistic variation and finite-sample resolution

## What must the experiment detect?

For a causal endpoint define a signed paired effect at independent unit i:

\[d_i = Y_i(\text{mechanism intervention})-Y_i(\text{matched sham}),\quad -1\le d_i\le1.\]

`Y_i` is the mean of all observations belonging to that unit. Score the full task family and retain variants in one cluster. If causal claims depend on the latent state, compare observationally matched interventions that alter the suspected state direction, its random rotation, an irrelevant direction, and a delayed readout. The unit may be a complete task family or independently trained checkpoint when the claim generalizes across trainings.

Specify before test:

- `scientific_min_effect`: the smallest causal change that matters, with units (paired solve fraction, corrected proof probability, future-logit margin, task utility, ACT6 flip rate).
- `measurement_resolution`: instrumentation noise, discrete 1/n outcome steps, calibration tolerance.
- `matched-sham floor`: a conservative upper-tail envelope of absolute effects for equal-dose controls on independent development roots. Calibrate both direction and magnitude, conditioned on dose when required.

\[\Delta_{\mathrm{mech}}=\max(\Delta_{\mathrm{scientific}},\Delta_{\mathrm{sham,upper}},\Delta_{\mathrm{measurement}}).\]

The target effect must clear this floor in a prospective experiment. Power to reject zero alone can be irrelevant to identifying the mechanism.

The supplied preflight tool uses independent-root *worst sham magnitudes*. Its upper one-sided order-statistic threshold is supported only when the binomial order-statistic coverage reaches the user-supplied confidence. For a continuous reference distribution with q=0.95 and confidence 0.95, the largest observed null needs n>=59 independent roots. For discrete laws it is conservative. When calibration is unavailable, any calculated threshold is a *development-only estimate*.

## Root-level planning

For independently sampled world effects with pilot standard deviation s, approximate a 2-sided (family-adjusted) 80%-power requirement to separate a target effect `delta` from the mechanistic floor `tau`:

\[G\approx\left[\frac{(z_{1-\alpha/(2m)}+z_{0.8})s}{\delta-\tau}\right]^2,\quad \delta>\tau.\]

This normal approximation supplies design guidance, not finite-sample power coverage and not a valid adaptive stopping rule. Non-Gaussian paired effects, nonexchangeable roots, heterogeneity and selection invalidate its naive interpretation. Use prospective Monte Carlo power simulation under the registered generator as an independent cross-check when the effect distribution is complicated. Sampling more *states* on the same world can make `Y_i` better measured, yet it does not yield new independent worlds.

The observed FSI-01 report should provide paired counts and nonparametric uncertainty. For a positive prespecified minimum effect, check the independent-world effect-floor lower bound. A bootstrap with eight roots is a descriptive diagnostic; an eight-root bootstrap can look narrow despite severe mechanism heterogeneity.

## Causal variation versus a stable score

A mechanism claim needs a discriminator such as wrong-state donor steering that flips an answer with a predicted sign, restoring the correct answer by a matched reverse edit, or a time-lag-specific intervention. Strong observational probes and high future-logit capture alone cannot settle causal mediation. Fix the model checkpoint and physical intervention dose before evaluating on a sealed set. Measure task correctness alongside intervention success, since a high flip rate can destroy correct answers as easily as it repairs wrong ones.

Report the fraction of original wrongs corrected, fraction of corrects corrupted, paired net change, and any delayed recovery. Select a single primary causal endpoint and predeclare a comparison family. For claims about invariant latent mechanisms across checkpoints, the checkpoint or independently trained model can itself be the generalization unit.

## Statistical evidence classes

1. Exact identities / complete finite enumerations: verify source + domain coverage, Lean kernel when applicable. Generalization outside the domain is a new empirical question.
2. Prospective causal experiments: new independent roots, frozen dosage, matched null, sealed outcomes, calibrated variation threshold and family-aware inference. Use the FSI-01 report.
3. Exploratory pilots: optimize architecture and discover effects, report all arms and source hashes, never count reused data as confirmation.
4. Underpowered nulls: indicate minimum resolvable effect and how many additional independent roots would address the question. Do not conclude equivalence or absence of a mechanism.

## Real examples within the research program

- HG-07: 6 world seeds, 256 test states each. Recurrent-versus-flat sign-flip p=0.3125, a 4/6 directional gate alone was inadequate to establish superiority.
- HG-08: 32 world seeds, 8,192 test states in total. About +0.54 percentage points observed for recurrence, family-adjusted p≈0.70. Repeating the same generator/optimization regime would target an effect smaller than its variation.
- ARG-03 development: 96 cases, 103 stored comparisons, 19 nominal p<0.05, none after broad Holm correction. Historical registered hypotheses require their own protected scope.
- BPD expected-L0: exact optimal-basis witnesses have algebraic status. Synthetic 32-world frequency sampling does not establish mechanisms inside pretrained looped transformers.

## Checklist for reviewer or agent

Determine what hypothesis would be falsified by a positive score; inspect matched null arms; identify the experimental unit and sampling population; compute or declare the physical effect threshold; estimate detectable change at available G; freeze all tests; preserve all outcomes; decide whether the evidence is structural, observational, or causal. A negative conclusion must state the power or equivalence margin that supports it.

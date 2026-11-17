---
name: evalmath-mechinterp-power
description: Design, audit and gate evaluation plans for looped transformers, SAEs, BPD, Hypergames and other mechanistic experiments. Use before running any small-n, repeatedly reused, clustered, multi-arm or causal-intervention evaluation. Decide whether independent held-out units can resolve the minimum physically meaningful mechanism effect above matched sham variation. Prevent significance claims from 64 correlated outcomes or post-selection, and preserve exact finite proofs as a separate evidence class.
---

# EvalMath: mechanistic-resolution preflight

**Trigger:** Before allocating compute, drafting a gym, interpreting a small benchmark, reporting a mechanism, training a probe on reused puzzles, picking the best of multiple interventions, or claiming causal transfer. Also trigger on follow-up work with AF, PEF, NRF, LS-SAE, SMC, HG, LOOPSCOPE and BPD experiments.

Start from the declared *scientific effect*. Ask what physical change in a model's behavior would establish the mechanism: corrected task outcomes, paired future-logit changes, retained proof paths, donor-specific causal flips, or recoverable readout variance at a fixed intervention dose. A statistically significant tiny shift can still be too small to establish the proposed mechanism. Freeze this target and its control family before opening the confirmation data.

## Required order

1. **Find the independent unit.** Preserve source puzzle, generator world, task family, training seed and model checkpoint identifiers. Within-world tokens, loop steps, repeated probes, rank-matched random bases and alternative intervention doses are observations on the same unit. Count independent units separately from scored rows.
2. **Specify the minimum meaningful mechanism variation.** State a primary outcome, physical intervention dose, `delta_mech in the outcome's units, the direction, and the strongest competing null. Calibrate a matched sham distribution using independently generated *development* units. The relevant threshold is the maximum of the scientific minimum, reliable sham-variation envelope and measurement resolution. Distinguish this threshold from arbitrary 5% significance.
3. **Perform pre-data resolution planning.** Use `python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot pilot.json --strict` with independent development-world paired effects and matched shams. Treat power as a planning estimate; default to `REDESIGN_OR_PILOT_ONLY` when effect size cannot exceed the mechanistic null floor or the planned root count is insufficient.
4. **Freeze selection and tests.** Record candidate count, adaptive queries, researcher degrees of freedom, familywise error budget, minimum effect, independent root population, all controls, failure gates and a manifest hash. Use an independent sealed readout that remained untouched by architecture search.
5. **Run a causal discrimination test.** When the claim concerns a mechanism, require a physically matched sham or donor/null intervention, equal-dose controls and a measurable distinction between competing causal hypotheses. A linear probe, beautiful SAE feature, or statistically stable accuracy number on its own supports an observational claim.
6. **Score once and keep the scope.** Apply `spiral_ln.evaluation_finite_sample` (FSI-01): exact paired McNemar for independent paired binary cases, cluster-level signed inference and bootstrap for grouped worlds, Holm/Bonferroni for registered comparisons, uncertainty and effect-floor analysis. A nonzero p-value alone cannot certify a practically important or identifiable mechanism. Archive raw paired outcomes, all discarded arms and source hashes.
7. **Assign an evidence class.** `exact finite domain`, `measured causal effect with prospective heldout`, `suggestive observational`, `power-limited` or `refuted`. Keep Lean-exhaustive theorems, toy synthetic laws and trained-model observations in distinct classes.

## Hard stop conditions

- Fewer than the planned independent roots, even if 64 or 8,192 scored outputs are available. One task transformed 64 ways is one task family for generalization.
- The minimum meaningful effect lies inside the matched-sham variation interval, or below measurement resolution. Increase the causal contrast or improve the instrument before expanding the same evaluation.
- No sealed held-out readout, especially after iterative intervention or architecture selection. Allocate new root families rather than rerunning on the same 64 cases.
- Multiple baselines/intervention directions were screened and only the winner is reported. Account for the *actual* comparison family and adaptive use. Direction-count gates, such as 4/6 seeds, are weak evidence without world-level uncertainty.
- A parity or algebraically generated task comes with an exact specialized solver. Label it a structural ceiling and test the proposed neural mechanism separately.
- A negative or null result is used to claim equivalence. Pre-register an equivalence margin and prove the confidence interval is contained inside it.
- The null is calibrated on individual observations with shared roots. For a nonparametric 95th-percentile sham threshold at 95% confidence, even using the sample maximum needs at least **59 independent sham worlds**. Eight roots cannot calibrate that tail regardless of their number of repeated examples.

## Example

On HG-08, 32 independent synthetic worlds each contain 256 task states. The tied recurrent model's gain over a flat control was roughly 0.54 percentage points, and the family-adjusted signed p was about 0.70. Treat further identical 64-case sweeps as development diagnostics until an explicit causal contrast can produce an effect above the matched sham floor. If the target is ±5-point equivalence, compute the number of independent worlds needed for an equivalence interval to sit inside that margin.

On BPD/ARG-03, development data from 96 cases contained 103 reported paired comparisons and 19 nominal p-values below 0.05. Holm across the complete retrospective family left none below 0.05. Preserve separate prospectively registered decisions. The held-out 168-case ARG-03 split remains sealed.

## Output contract

Every research handoff must include `unit`, `n_units`, `n_cases`, `primary contrast`, `physical dose`, `scientific variation floor`, `matched-sham floor with confidence/source`, `planned and actual comparisons`, `estimated resolution/power`, `readout selection exposure`, `causal controls`, `verdict`, and `exact evidence provenance`. For small n, report *what further data would change the conclusion* rather than a false certainty.

See [resolution notes](references/resolution-and-evidence.md), [EvalMath FSI-01](../../paper/finite_sample_inference.md), [selection and adaptive reuse](../../paper/evaluation_feedback_multigen.md).

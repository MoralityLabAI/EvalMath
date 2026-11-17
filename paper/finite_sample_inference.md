# FSI-01: Small-sample inference for looped-transformer evaluation

**Status:** implementation with enumerated/exact-test checks and a synthetic reporting gate. No new model results or formal Lean theorem. Mathematical exactness concerns the stated binomial and sign-flip laws, **not** the independence of generated tasks or the completeness of an external exhaustive evaluation.

## Why 64 scored outputs are not necessarily 64 replications

Our research gyms frequently produce 64 outcomes per checkpoint, sometimes as eight root instances with eight transformations each. When transformations inherit task structure, the independent unit may be the **root**, rather than the outcome. Running more seeds on the same 64 tasks also reuses the same evaluation set. The effective sample size cannot be inferred from the raw row count.

FSI-01 introduces an auditable JSON contract. It requires distinct `case_id`, explicit `cluster_id`, declared `target_population`, pre-registered `minimum_effect`, familywise multiplicity count, and flags indicating whether the readout was sealed, the hypothesis was registered, the clusters can be treated as independent, and the paired-label exchangeability null is appropriate. These flags are assertions by the experiment author; no program can establish them from 0/1 results alone.

## Mathematical endpoints

For `n` **independent Bernoulli** cases, the module computes two-sided Clopper–Pearson accuracy bounds using rational bisection. The returned interval expands the exact beta-quantile endpoints outwards by at most `2^-18`; finite-sample coverage is at least `1-alpha`, conditional on binomial sampling. It suppresses those nominal case-level intervals when a cluster has repeated cases.

For `b` candidate-only wins and `c` baseline-only wins on independent paired cases, the two-sided exact McNemar tail is

\[
 p=\min\left\{1,2\,2^{-(b+c)}\sum_{j=0}^{\min(b,c)}\binom{b+c}{j}\right\}.
\]

It is an exact **conditional null** test of equal marginal performance. For 15 wins, 3 losses, 46 ties, `p=247/32768≈0.00753784`, based on 18 discordances. Counts of ties still matter for effect size and confidence intervals. When there are correlated cases within roots, the module substitutes an exact two-sided root-sign-flip test for up to 18 independent roots, or a seeded Monte Carlo version beyond 18, under the explicitly declared independent-root and signed-symmetry assumptions. The Monte Carlo p-value includes a `+1` correction and is labelled approximate.

The effect is the **equal-cluster macro mean** of paired case differences, with a separately reported case-weighted effect. A seeded percentile cluster bootstrap gives a *descriptive*, approximate interval. Small numbers of roots can make that interval too narrow. The default evidence policy requires at least 20 independent roots for a positive confirmation, in addition to a sealed readout, preregistration, suitable test assumptions, and familywise p-value control.

A positive minimum effect `delta > 0` gets an extra non-asymptotic gate. Each cluster mean lies in `[-1,1]`, so for `g` independent clusters, a one-sided Hoeffding lower bound on the expected macro effect is

\[
\bar d - \sqrt{\frac{2\log(m/\alpha)}{g}},
\]

where `m` is the number of prespecified comparisons; the upper bound has `+` instead. This conservative bound is required to exceed `delta` before the module uses **confirmed** for a positive effect floor. For `delta=0`, the primary calibrated paired hypothesis test and descriptive bootstrap direction are used together. The bootstrap is not treated as an exact finite-sample confidence guarantee.

The module reports conservative iid planning via `ceil(log(2/alpha)/(2*epsilon^2))`: for a 95% Hoeffding accuracy half-width of five percentage points, `n=738` independent Bernoulli draws. It is a planning bound, rather than a post hoc assertion of power or a substitute for matched-pair design calculations.

## Selection, multiplicity, provenance

`planned_comparisons` produces a conservative Bonferroni-adjusted primary p-value and adjusts the displayed interval level. `holm_adjust` accepts the *complete* family of exact p-values if a higher-level reporter has them all. Neither correction repairs adaptive reuse of the very readout being scored. `sealed_readout=false` blocks a confirmation regardless of the p-value, because the model or intervention was selected using this dataset. See `rl_training_signal_limits.md` L5 and `evaluation_feedback_multigen.md` for the selection-inflation null. A fresh, untouched confirmation readout is the main repair.

For deterministic exhaustive experiments, specify `evaluation_mode="exhaustive"`, `declared_domain_size` matching unique cases, and a `coverage_audit_sha256` that identifies the external domain coverage audit. The module calls this `exact_finite_result`, strictly over the declared domain. Matching the count and a SHA-256-shaped audit identifier is **an attestation interface**, not an independent proof that the domain or oracle is complete. Scope must be reviewed at the source.

## JSON contract and CLI

```json
{
  "schema_version": 1,
  "experiment_id": "AF-FSI-EXAMPLE",
  "target_population": "frozen generated task family, root-level sampling",
  "evaluation_mode": "sampled",
  "alpha": "0.05",
  "minimum_effect": "0.00",
  "planned_comparisons": 1,
  "hypothesis_preregistered": true,
  "sealed_readout": true,
  "clusters_independent": true,
  "exchangeable_pair_labels": true,
  "cases": [
    {"case_id": "root01-a", "cluster_id": "root01", "candidate": 1, "baseline": 0},
    {"case_id": "root01-b", "cluster_id": "root01", "candidate": 0, "baseline": 0},
    {"case_id": "root02-a", "cluster_id": "root02", "candidate": 0, "baseline": 1}
  ]
}
```

Run `PYTHONPATH=src python -m spiral_ln.evaluation_finite_sample --manifest manifest.json --output result.json`; add `--require-confirmed` to return exit code 2 for a non-confirmation. Use a **frozen manifest hash** and retain raw individual outcomes in every receipt. Reject a confirmation if root identifiers, reuse history, candidate search count, or the prespecified test family are missing from the experimental record.

For source replay tests: `PYTHONPATH=src pytest -q tests/test_evaluation_finite_sample.py`. An exact finite calculation about a toy generator is evidence for that generator and its stated support; a Lean compiler replay concerns proof validity; neither is population generalization to unseen real-world tasks.

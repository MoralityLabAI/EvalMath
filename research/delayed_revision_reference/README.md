# EVAL-REV-01: evaluating revision-aware recurrent representations

**Source-only mathematical crosswalk, 18 November 2026.** Upstream [Beyond Bayes BB-CQ-05 PR #24](https://github.com/patrickdugan/beyond-bayes/pull/24), frozen `main` merge `abc89f73d223f00305eb0416a34fe5aee602494d`. Exact model: 12 known-label reports, 3 regime priors (9/20,7/20,1/5), match probabilities (19/20,13/20,3/20), delayed public correction schedule. The independent [oracle](bridge.py) and [tests](test_bridge.py) re-enumerate raw histories on smaller domains; they do not import upstream scorers.

## Evidence claim to audit

The current marginal posterior can be sufficient to predict a hidden regime **before** a correction schedule becomes visible while failing to preserve the information needed to update after the schedule arrives. For any 1≤j<n, the self-contained encoder must distinguish all 2^n old bit vectors to answer every legal delayed revision exactly. For n=12, this is 4096 classes / 12 fixed bits. Separately retaining the current count-posterior label requires an additional tag of up to 10 bits inside its largest fiber; the joint optimum remains 12 bits. If the schedule arrives **before encoding**, the calibrated accepted-report count is sufficient. An external archive can supply the old count at corrected slots; with j=6, its numeric message has 7 values / 3 bits. These omit archive/verification cost and assume full trusted versions.

The upstream exact six-revision expected Brier risks (unhalved 3-class score) are 0.170499060115450 for aggregate-only and 0.106036369270665 for full Bayes, a gap 0.064462690844785. This is inherited **mathematical** evidence, not a novel neural effect or fresh independent confirmation. The preregistered authorization gain at BB-CQ-04 was 0.006206757142 below the 0.02 practical gate, so it remains **HEADROOM_BLOCKED** for that task.

## Exact evaluation decomposition

Let `X` be the named old bit vector, `S` the correction schedule and `Y` the accepted replacements. Define `H=sigma(S,X,Y)` and `G_r=sigma(S,sum(X),Y,X[S[:r]])` for a fixed, outcome-independent disclosure order. With `p_H=P(K|H)` and `p_r=P(K|G_r)`, conditional expectation gives `p_r=E[p_H|G_r]`. For any predictor `a` computed only from `G_r`:

```
E[Brier(a,K)] - E[Brier(p_H,K)]
= E[||a-p_r||_2^2] + E[||p_r-p_H||_2^2].
```

The first term is **model approximation error**, estimated on independent issuer roots. The second is **irreducible information loss** for the explicitly count-restricted arm and is known exactly for this finite generator. An observational probe might estimate `p_r` accurately while a native hidden-state edit does not transport it forward. Label that outcome observational.

A raw-stream recurrent model receives all of `X` before `S` is revealed. After receiving `S` and `Y`, its complete input history is `H`; its final Bayes comparator is `p_H` for every `r`. Repeating old bits can help the model recover forgotten information, while the optimal full-input posterior stays fixed. Restricting hidden-state capacity leaves the model free to retain functions of `X` other than its total, so capacity alone does not make its output `G_r`-measurable. The count-restricted formula requires an enforced old-history interface containing only `sum(X)` plus the declared disclosures.

For example, with `n=4`, `S=(0,)`, `Y=(0,)`, the old vectors `(1,0,0,0)` and `(0,1,0,0)` have the same `G_0` and different accepted counts. Their full-input Bayes posteriors differ. Across the finite population, using `a=p_H` gives expected excess relative to `p_r` equal to `-E[||p_r-p_H||_2^2]`, which is negative whenever information is lost. This witness prevents interpreting that quantity as nonnegative approximation error for a learner with full old-input access.

## Gym protocol for BPD / LoopedTransformers / Control-Harness

Fix and hash the full source generator, exact oracle, model checkpoints, event grammar and all arms **before** sampling the first development root. Separate early from delayed schedule cohorts and include full replay, calibrated early-count, reduced-information Bayes, archive-verified delta, stale-native, and physically matched neural shams. Freeze `r=0..j` and the number of evidence amendments per root.

The primary registered neural endpoint should be root-level **input-matched excess Brier**, `Brier(a,K)-Brier(p_F,K)`, where `F` is that arm's complete input history and `p_F=P(K|F)`. Use a root-paired difference against a strong baseline with identical input privileges. The raw-stream arm has `F=H` after all replacements arrive. An enforced count-restricted arm has `F=G_r` and reports `Brier(p_r,K)-Brier(p_H,K)` separately. The expected approximation term is nonnegative for the matching information set; an empirical paired estimate can fluctuate below zero. For a causal-mechanism claim, intervene on native recurrent states at fixed model and dose, measure final task behavior and future logits; match random/gauge/nuisance directions and include a no-edit reference. A full-input replay advantage alone establishes input handling.

The independent unit is one issuer/source root when reusing a frozen model; for cross-training generalization count independently initialized **model roots**. Each root's 12 report slots, 3 correction sizes, disclosure stages, shams and decisions are repeated observations on that root. Do not count them as extra replications. Multiple exploration-selected endpoints must use a separately reserved confirmation cohort.

The native study must pass the existing [mechanistic resolution preflight](../../skills/evalmath-mechinterp-power/SKILL.md). Calibrate physically equal-dose shams on independent development roots, state a minimum scientifically meaningful Brier change, establish sufficient task headroom and selection-family adjustment. For a mean Brier effect, use the same paired root-mean statistic and a stated uncertainty procedure for the sham comparison. The 95/95 maximum-sham order-statistic rule needs >=59 independent calibration units under the published conditions and provides a per-root tolerance statement. A mean-effect gate requires a mean-matched sham estimator. **Zero external/new protected roots opened** by this crosswalk.

## Independent oracle scope

`python -m unittest discover -s research/delayed_revision_reference -p 'test_*.py' -v` checks the conditional posterior through raw bit-vector and named-schedule enumeration for small n, exact Brier variance decomposition and memory accounting. A named-slot collision and a negative full-input-versus-reduced expected excess check enforce the comparator's information contract. It does not claim a second full n=12 enumeration or a new Lean proof. [BB-CQ-05's archived receipt](https://github.com/patrickdugan/beyond-bayes/blob/main/results/bb_cq05_exact_v1.json) remains the canonical larger-domain source with source-hashed reproduction.


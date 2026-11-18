# EVAL-REV-01: evaluating revision-aware recurrent representations

**Source-only mathematical crosswalk, 18 November 2026.** Upstream [Beyond Bayes BB-CQ-05 PR #24](https://github.com/patrickdugan/beyond-bayes/pull/24), frozen `main` merge `abc89f73d223f00305eb0416a34fe5aee602494d`. Exact model: 12 known-label reports, 3 regime priors (9/20,7/20,1/5), match probabilities (19/20,13/20,3/20), delayed public correction schedule. The independent [oracle](bridge.py) and [tests](test_bridge.py) re-enumerate raw histories on smaller domains; they do not import upstream scorers.

## Evidence claim to audit

The current marginal posterior can be sufficient to predict a hidden regime **before** a correction schedule becomes visible while failing to preserve the information needed to update after the schedule arrives. For any 1≤j<n, the self-contained encoder must distinguish all 2^n old bit vectors to answer every legal delayed revision exactly. For n=12, this is 4096 classes / 12 fixed bits, with 10 extra tags when separately retaining the current count-posterior label. If the schedule arrives **before encoding**, the calibrated accepted-report count is sufficient. An external archive can supply the old count at corrected slots; with j=6, its numeric message has 7 values / 3 bits. These omit archive/verification cost and assume full trusted versions.

The upstream exact six-revision expected Brier risks (unhalved 3-class score) are 0.170499060115450 for aggregate-only and 0.106036369270665 for full Bayes, a gap 0.064462690844785. This is inherited **mathematical** evidence, not a novel neural effect or fresh independent confirmation. The preregistered authorization gain at BB-CQ-04 was 0.006206757142 below the 0.02 practical gate, so it remains **HEADROOM_BLOCKED** for that task.

## Exact evaluation decomposition

With `H` containing the full history and accepted replacements, and `G_r` the reduced information after a fixed disclosure prefix, let `p_H=P(K|H)` and `p_r=P(K|G_r)`. Then `p_r=E[p_H|G_r]`. For any predictor `a` computed only from `G_r`:

```
E[Brier(a,K)] - E[Brier(p_H,K)]
= E[||a-p_r||_2^2] + E[||p_r-p_H||_2^2].
```

The first term is **model approximation error**, estimated on independent issuer roots. The second is **irreducible information loss** and is known exactly for this finite generator. An observational probe might estimate `p_r` accurately while a native hidden-state edit does not transport it forward. Label that outcome observational.

## Gym protocol for BPD / LoopedTransformers / Control-Harness

Fix and hash the full source generator, exact oracle, model checkpoints, event grammar and all arms **before** sampling the first development root. Separate early from delayed schedule cohorts and include full replay, calibrated early-count, reduced-information Bayes, archive-verified delta, stale-native, and physically matched neural shams. Freeze `r=0..j` and the number of evidence amendments per root.

The primary registered neural endpoint should be root-level **reduced-info-relative excess Brier**, `Brier(a,K)-Brier(p_r,K)`, with root-paired difference against a strong baseline at identical input privileges. Report the information loss `Brier(p_r,K)-Brier(p_H,K)` separately. For a causal-mechanism claim, intervene on native recurrent states at fixed model and dose, measure final task behavior and future logits; match random/gauge/nuisance directions and include a no-edit reference. A full-input replay advantage measures input handling, not a discovered causal fiber.

The independent unit is one issuer/source root when reusing a frozen model; for cross-training generalization count independently initialized **model roots**. Each root's 12 report slots, 3 correction sizes, disclosure stages, shams and decisions are repeated observations on that root. Do not count them as extra replications. Multiple exploration-selected endpoints must use a separately reserved confirmation cohort.

The native study must pass the existing [mechanistic resolution preflight](../../skills/evalmath-mechinterp-power/SKILL.md). Calibrate a physically equal-dose sham envelope on independent development roots, state a minimum scientifically meaningful Brier change, establish sufficient task headroom and selection-family adjustment. The 95/95 maximum-sham order-statistic rule needs >=59 independent calibration units under the published conditions. **Zero external/new protected roots opened** by this crosswalk.

## Independent oracle scope

`python -m unittest discover -s research/delayed_revision_reference -p 'test_*.py' -v` checks the conditional posterior through raw bit-vector and named-schedule enumeration for small n, exact Brier variance decomposition and memory accounting. It does not claim a second full n=12 enumeration or a new Lean proof. [BB-CQ-05's archived receipt](https://github.com/patrickdugan/beyond-bayes/blob/main/results/bb_cq05_exact_v1.json) remains the canonical larger-domain source with source-hashed reproduction.

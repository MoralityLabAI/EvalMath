# EVAL-AUTH-03: noisy authorization, posterior errors and the audit-budget frontier

**Status:** exact finite probability calculus and reproducible oracles. No model calls, issuer authentication or empirical audit calibration. The mathematical ingredients are classical Bayesian decision theory and the value-of-information principle, applied to the ECA authorization setting.

## 1. A binary audit with finite false-positive and false-negative channels

Let `A=1` mean the host policy truly permits an action, and let `p=P(A=1 | public)` be the prior conditional on the full public evidence. An optional independent audit returns `S∈{0,1}`, with

```
t = P(S=1 | A=1, public)   (sensitivity)
f = P(S=1 | A=0, public)   (false positive rate).
```

We assume exact `p,t,f∈[0,1]`, symmetric 0/1 decision loss and a controller that chooses the Bayes action, breaking posterior ties toward denial.

Without inspection, the minimum error is `r0=min(p,1-p)`. If the audit report is observed before the decision, its two possible values yield exact expected error

```
r1 = min(p*t, (1-p)*f) + min(p*(1-t), (1-p)*(1-f)).
```

The error reduction `v=r0-r1≥0` follows from subadditivity of the minimum over nonnegative masses: `min(a,c)+min(b,d)≤min(a+b,c+d)`. This is an algebraic identity in the declared channel and cannot establish that a real issuer has the stated sensitivity or false-positive rate.

| Conditional public prior / channel | Error before | Error after | Value |
|---|---:|---:|---:|
| `p=1/2; t=9/10; f=1/10` | 1/2 | 1/10 | **2/5** |
| `p=1/2; t=3/5; f=2/5` | 1/2 | 2/5 | 1/10 |
| `p=1/8; t=9/10; f=1/10` | 1/8 | 1/10 | 1/40 |
| `p=1/8; t=3/5; f=2/5` | 1/8 | 1/8 | 0 |
| `p=1/3; t=9/10; f=1/10` | 1/3 | 1/10 | 7/30 |

## 2. Exact nonadaptive fixed-budget policy

For independent root items `i` with additive symmetric error loss and an audit decision chosen before seeing any private reports, suppose a budget requires inspecting exactly `B` items. The best expected risk reduction is the sum of the `B` highest audit values, including negative values when the decoder is a *fixed misspecified rule*:

```
max_{I subset of {1..N}, |I|=B} Σ_{i∈I} v_i
  = Σ_{j=1..B} v_(j),
```

where `v_(1)≥...≥v_(N)` are sorted values. This is the exchange argument for choosing the top-B weights. `optimal_fixed_budget` gives a deterministic tie-break by public case ID; `audit_budget_frontier` provides all N+1 exact budget levels; `brute_force_budget_gain` enumerates every subset for independent regression.

This optimality claim is for an additive nonadaptive setting with public case information. Shared latent states across items, audit outcomes that change beliefs about another case, sequential cost constraints, and adversarially selected audit reports require a richer decision model. A fixed maximum-budget constraint (at most B audits) may skip negative-value inspections, while the implemented comparator fixes *exactly* B to preserve equal-cost policy comparisons.

## 3. The fitted-controller failure mode

A model can hold incorrect priors or incorrect audit calibration. `expected_error_under_rule(true_channel, estimated_channel, inspect=...)` evaluates its deterministic action rule under a distinct true channel. Its signed audit benefit may be negative.

A complete exact witness is

```
true:     p=3/5, t=1/2, f=1/2   (audit contains zero information)
estimated: p=3/5, t=99/100, f=1/100.
```

The fitted controller authorizes without inspection, giving true error `2/5`. With the imaginary discriminating audit in its posterior, it authorizes positive reports and denies negative reports, giving actual error `1/2`. Its true gain is `-1/10`. This demonstrates why source independence and a valid signature do not certify the informational quality of an audit.

## 4. Reproducibility

```bash
PYTHONPATH=src python -m pytest -q tests/test_evaluation_noisy_authorization.py
PYTHONPATH=src python scripts/verify_eval_auth03.py --output /tmp/eval_auth03.json
```

The unit suite checks the five published exact channels, enumerates 125 rational probability triples, compares true Bayes risk with the model's rule, and exhaustively checks the sorting law against independent fixed-budget subset enumeration for every one-to-four-case roster over four signed audit values. The verifier records exact-rational outcomes and SHA-256 of its code, tests and this note. Hosted CI independently replays them; until that passes, the Lean or Python claims remain candidate artifacts.

## 5. Next ECA-02 experiment and source boundaries

The first [Control-Harness ECA-01](https://github.com/MoralityLabAI/Control-Harness/pull/49) is merged and its preregistered result remains fixed at [the original run](https://github.com/MoralityLabAI/Control-Harness/actions/runs/44131080443). The posterior-free ECA-01 audit is a host-truth oracle, so its exact 28/64 inspection frontier is a theorem-calibration control.

ECA-02 should introduce **publicly known but imperfect authorization priors** and **noisy signed audits**. Fit each decision policy only on a distinct calibration cohort, select inspection targets under the same fixed budget without reading held-out hidden labels or audit reports, then evaluate on independent held-out roots. Use a registered equal-cost policy family: fixed-order random selection, public-uncertainty selection, fitted audit-value selection, and an oracle that knows the declared synthetic channel. Report false authorizations and missed permitted actions separately, alongside inspection cost and total error. Group repeated observations from the same root; protect an untouched second cohort from tuning. A model-based predictor is a separate future step.

The original [MathCan AUTHQ-02](https://github.com/patrickdugan/MathCan/pull/140) remains a deterministic information-limit theorem. This new work analyzes the additional error caused by a *noisy* audit and by beliefs that misrepresent that audit. Neither independently authenticates external issuer authorities nor proves real-world safety.


## 6. EVAL-AUTH-04: specify the cost of unauthorized approval

After ECA-02's first preregistered readout, a consequential objective difference emerged. Symmetric-error fitted-value auditing completed 3,143/4,096 heldout decisions correctly, versus 3,109/4,096 for public-uncertainty auditing at the same 1,024 audits per arm. The fitted rule missed 152 fewer genuinely authorized actions but made 118 more unauthorized approvals. For the **frozen, already-recorded decisions** the weighted loss `λ FP + FN` crosses over at the exact retrospective arithmetic ratio `λ=76/59≈1.288`. That comparison motivates a *new* cost-registered experiment; the original study remains a symmetric-risk test.

Let `c_FP > 0` penalize granting forbidden authorization and `c_FN > 0` penalize denying a permitted authorization. The Bayes decision grants only when `c_FN p > c_FP(1-p)`, equivalently `p > c_FP/(c_FP+c_FN)`. The best expected loss with the public prior is

```
R0 = min(c_FN * p, c_FP * (1-p)).
```

After the binary audit report:

```
R1 = min(c_FN * p*t, c_FP * (1-p)*f)
   + min(c_FN * p*(1-t), c_FP * (1-p)*(1-f)).
```

The exact nonnegative value `V=R0-R1` follows by the same finite minimum-mass argument. Cost weighting changes both the **post-report decision** and **which cases deserve audit**, because the expected reduction is recomputed from asymmetric losses.

For example, with `c_FP=2,c_FN=1`, a balanced high-fidelity audit (`p=1/2,t=9/10,f=1/10`) has weighted value `7/20`, while a balanced weak audit (`p=1/2,t=3/5,f=2/5`) has weighted value zero. The latter can still change the output when a mismatched decoder misinterprets its evidence; the theorem applies to the true Bayes decoder.

The exact `weighted_expected_error_under_rule` function evaluates a fixed fitted model against a different true channel, retaining the possibility of a **negative** realized audit gain under miscalibration. The tests enumerate 500 conditional-channel/cost configurations, verify the cost-aware decision threshold and check the exact observed crossover identity.

**New prospective decision:** ECA-03 should register `c_FP=2,c_FN=1` before any new heldout roots are sampled. It should compare calibrated cost-weighted value targeting, cost-weighted public uncertainty, and the original symmetric policy at equal audit budget. Training labels can be reused only when the training policy permits it and the training data are distinct from the new sealed cohort. All scoring must preserve the original forbidden/authorized denominators.

The [registered ECA-02 synthetic readout](https://github.com/MoralityLabAI/Control-Harness/actions/runs/44136694988) and its [full source-hashed artifact](https://github.com/MoralityLabAI/Control-Harness/actions/runs/44136694988/artifacts/14353225355) remain unchanged; [ECA-02 PR #50](https://github.com/MoralityLabAI/Control-Harness/pull/50) records the research boundaries. A separate independent replay reconstructed 20,480/20,480 rows, all policy choices and all six calibrated stratum parameters. Its compressed raw SHA-256 is `699c1746267eb13e1921d8a5b725e15412e640f102d529cfc45128e5c7d67162`.

**Limits:** The probabilities and host audit signatures are synthetic. The theorem is an exact algebraic statement about an assumed binary channel, without external authority, policy-ethics or model-performance certification.

# SRG-22: Task-conditioned directed residual geometry

[Pre-run protocol](../integrations/sweepweave-ts/srg22/PROTOCOL.md), commit b316765e71b2eb1de8b3676ddf4e1a1d8e75aadf. Source pin 0f2b12f8915180764c5d53d525163106fd8b3945. Original public cohorts and a separately seeded public replication. No actual model inference, private evaluation or editor modifications. Preserve SRG-21 negative result and concurrent SRG-AC work.

## Directed operator

Set V1(u)=max legal immediate reward r(u,a), V1(terminal)=0. For directed edge e=(u,v), rho(e)=r(e)+V1(v)-V1(u). This is an affine reward-conditioned coboundary, not a self-adjoint Dirac spectrum. Summing along a complete trajectory gives sum rho = sum r - V1(root). The expectation identity is checked under uniform legal-action forward propagation. All reward features are normalized by 3H+B. The feature arrays summarize local rewards, occupancy-weighted positive and negative residuals, residual RMS, first and last layer magnitudes, root maximum residual, and uniform expected running and terminal utility plus first-action terminal reachability range. No scored-policy rollouts or full oracle values enter the feature extractor. Uniform propagation visits the full graph; it may cost more than exact DP in small worlds.

For epistemic worlds, a_i(x) is the conditional accuracy of agent i's standalone direct-routing Bayesian rule. For root history h, local delegation residual is E[a_1(x)|h]-fee/8-max(P(target=0|h),P(target=1|h)). Later-agent alignment compares the best conditional direct accuracy of agents i>=2 to agent 1. This is a local contrast, not an optimal suffix value. D=1 can coincide with exact one-link decisions because the successor is terminal. Features are built independently of source control choices and oracle scores; labels use SRG-18/SRG-20 exact regret. Posterior and graph invariances under padding are tested. No strategic signaling.

## Registered primary gate

| Cohort | Domain | RMSE reduction vs size | Improved tapes | Reduction vs local | Reduction vs spectral | Gate |
|---|---|---:|---:|---:|---:|---|
| original | reaction | 11.08% | 16/16 | 5.04% | 7.11% | PASS |
| original | epistemic | 24.45% | 7/8 | 8.53% | 25.28% | PASS |
| fresh | reaction | 12.42% | 16/16 | 4.61% | 7.63% | PASS |
| fresh | epistemic | 25.17% | 8/8 | 17.78% | 26.35% | PASS |

Reaction gate PASS; epistemic gate PASS; joint gate PASS. The threshold is >=5% RMSE improvement and >=75% improved held-out tapes in both cohorts. This supports the fixed predictor of one-step or one-link control regret on these synthetic families, not a universal difficulty label. Fresh cohorts refit the fixed method within fresh training folds; this is methodological replication rather than transfer of a frozen fitted predictor. All six original size baseline RMSEs reproduce exactly. The separate recovery execution after concurrent branch movement reproduced all four directed primary RMSEs within 1e-10.

## Full results

Ridge lambda=1, intercept, standardization fitted only on training tapes, no tuning/clipping. All matched siblings stay together. R2 against per-fold training mean; within-stratum rank correlations average ties and omit constant strata. RMSE and MAE in fractions of nominal utility. Eight/sixteen public shared tapes per cohort; no independent significance claim.

| Cohort | Domain | Outcome | Arm | RMSE | MAE | R2 | Reduction vs size | Improved tapes | Within-stratum rho |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| original | reaction | d1 | mean | 0.146689 | 0.128245 | 0.000000 | -11.27% | 0 | -0.143896 |
| original | reaction | d1 | structural | 0.134258 | 0.110210 | 0.162309 | -1.84% | 2 | 0.280405 |
| original | reaction | d1 | size | 0.131836 | 0.107369 | 0.192261 | 0.00% | 0 | 0.292252 |
| original | reaction | d1 | local | 0.123450 | 0.100985 | 0.291752 | 6.36% | 16 | 0.395130 |
| original | reaction | d1 | directed | 0.117228 | 0.094775 | 0.361347 | 11.08% | 16 | 0.460743 |
| original | reaction | d1 | spectral | 0.126206 | 0.101189 | 0.259777 | 4.27% | 15 | 0.375120 |
| original | reaction | d2 | mean | 0.119891 | 0.098046 | -0.000000 | -13.40% | 0 | -0.213416 |
| original | reaction | d2 | structural | 0.108323 | 0.082956 | 0.183665 | -2.46% | 3 | 0.167676 |
| original | reaction | d2 | size | 0.105722 | 0.080962 | 0.222398 | 0.00% | 0 | 0.190843 |
| original | reaction | d2 | local | 0.105505 | 0.081726 | 0.225586 | 0.21% | 10 | 0.205286 |
| original | reaction | d2 | directed | 0.099622 | 0.077428 | 0.309539 | 5.77% | 15 | 0.319428 |
| original | reaction | d2 | spectral | 0.104125 | 0.079759 | 0.245708 | 1.51% | 14 | 0.202336 |
| original | reaction | d4 | mean | 0.057237 | 0.035036 | 0.000000 | -8.69% | 3 | -0.284033 |
| original | reaction | d4 | structural | 0.052824 | 0.031643 | 0.148236 | -0.31% | 6 | 0.057035 |
| original | reaction | d4 | size | 0.052662 | 0.031840 | 0.153472 | 0.00% | 0 | 0.071830 |
| original | reaction | d4 | local | 0.052048 | 0.030244 | 0.173097 | 1.17% | 14 | 0.110909 |
| original | reaction | d4 | directed | 0.052163 | 0.030102 | 0.169439 | 0.95% | 13 | 0.119483 |
| original | reaction | d4 | spectral | 0.052445 | 0.031084 | 0.160428 | 0.41% | 10 | 0.062629 |
| original | epistemic | d1 | mean | 0.068356 | 0.031794 | -0.000000 | -3.07% | 4 | -0.281418 |
| original | epistemic | d1 | structural | 0.065886 | 0.033159 | 0.070975 | 0.65% | 7 | 0.357439 |
| original | epistemic | d1 | size | 0.066320 | 0.033341 | 0.058694 | 0.00% | 0 | 0.345048 |
| original | epistemic | d1 | local | 0.054773 | 0.033926 | 0.357944 | 17.41% | 7 | 0.514096 |
| original | epistemic | d1 | directed | 0.050103 | 0.031839 | 0.462761 | 24.45% | 7 | 0.661434 |
| original | epistemic | d1 | spectral | 0.067056 | 0.033989 | 0.037671 | -1.11% | 2 | 0.318575 |
| original | epistemic | d1 | belief | 0.066537 | 0.033645 | 0.052511 | -0.33% | 2 | 0.308104 |
| original | epistemic | last | mean | 0.060203 | 0.044731 | -0.000000 | -2.64% | 5 | -0.401024 |
| original | epistemic | last | structural | 0.058790 | 0.040017 | 0.046384 | -0.23% | 2 | 0.146000 |
| original | epistemic | last | size | 0.058655 | 0.039839 | 0.050763 | 0.00% | 0 | 0.153664 |
| original | epistemic | last | local | 0.075033 | 0.052862 | -0.553341 | -27.92% | 1 | -0.074914 |
| original | epistemic | last | directed | 0.076411 | 0.051960 | -0.610924 | -30.27% | 0 | -0.048735 |
| original | epistemic | last | spectral | 0.058482 | 0.039134 | 0.056345 | 0.29% | 6 | 0.177818 |
| original | epistemic | last | belief | 0.073852 | 0.052093 | -0.504841 | -25.91% | 0 | -0.081385 |
| original | epistemic | factor | mean | 0.040373 | 0.029821 | -0.000000 | -21.10% | 0 | -0.498505 |
| original | epistemic | factor | structural | 0.033309 | 0.020985 | 0.319310 | 0.09% | 5 | 0.449917 |
| original | epistemic | factor | size | 0.033338 | 0.021028 | 0.318144 | 0.00% | 0 | 0.451663 |
| original | epistemic | factor | local | 0.033433 | 0.021324 | 0.314241 | -0.29% | 2 | 0.461051 |
| original | epistemic | factor | directed | 0.034407 | 0.021484 | 0.273698 | -3.21% | 1 | 0.440253 |
| original | epistemic | factor | spectral | 0.032442 | 0.020644 | 0.354270 | 2.69% | 5 | 0.530258 |
| original | epistemic | factor | belief | 0.034043 | 0.021043 | 0.288985 | -2.12% | 2 | 0.385467 |
| fresh | reaction | d1 | mean | 0.157064 | 0.137419 | -0.000000 | -11.41% | 1 | -0.125845 |
| fresh | reaction | d1 | structural | 0.144352 | 0.119060 | 0.155324 | -2.39% | 1 | 0.290853 |
| fresh | reaction | d1 | size | 0.140984 | 0.114768 | 0.194276 | 0.00% | 0 | 0.318877 |
| fresh | reaction | d1 | local | 0.129447 | 0.105516 | 0.320744 | 8.18% | 15 | 0.425868 |
| fresh | reaction | d1 | directed | 0.123475 | 0.100285 | 0.381977 | 12.42% | 16 | 0.470835 |
| fresh | reaction | d1 | spectral | 0.133671 | 0.106359 | 0.275699 | 5.19% | 15 | 0.405816 |
| fresh | reaction | d2 | mean | 0.129331 | 0.107609 | 0.000000 | -14.51% | 1 | -0.179607 |
| fresh | reaction | d2 | structural | 0.116983 | 0.091049 | 0.181833 | -3.58% | 1 | 0.164733 |
| fresh | reaction | d2 | size | 0.112939 | 0.086354 | 0.237422 | 0.00% | 0 | 0.190304 |
| fresh | reaction | d2 | local | 0.112417 | 0.088076 | 0.244461 | 0.46% | 10 | 0.211651 |
| fresh | reaction | d2 | directed | 0.106092 | 0.083099 | 0.327086 | 6.06% | 14 | 0.319193 |
| fresh | reaction | d2 | spectral | 0.110388 | 0.085435 | 0.271482 | 2.26% | 13 | 0.230673 |
| fresh | reaction | d4 | mean | 0.058019 | 0.037159 | 0.000000 | -10.00% | 1 | -0.181971 |
| fresh | reaction | d4 | structural | 0.053101 | 0.033067 | 0.162348 | -0.67% | 4 | 0.087621 |
| fresh | reaction | d4 | size | 0.052746 | 0.032788 | 0.173511 | 0.00% | 0 | 0.093074 |
| fresh | reaction | d4 | local | 0.052298 | 0.031423 | 0.187472 | 0.85% | 13 | 0.121906 |
| fresh | reaction | d4 | directed | 0.052277 | 0.031178 | 0.188141 | 0.89% | 14 | 0.100340 |
| fresh | reaction | d4 | spectral | 0.052419 | 0.032183 | 0.183711 | 0.62% | 13 | 0.082350 |
| fresh | epistemic | d1 | mean | 0.095356 | 0.058173 | 0.000000 | -8.24% | 4 | -0.304888 |
| fresh | epistemic | d1 | structural | 0.086431 | 0.058596 | 0.178437 | 1.89% | 7 | 0.408818 |
| fresh | epistemic | d1 | size | 0.088093 | 0.060241 | 0.146533 | 0.00% | 0 | 0.373639 |
| fresh | epistemic | d1 | local | 0.080169 | 0.058301 | 0.293165 | 8.99% | 8 | 0.463702 |
| fresh | epistemic | d1 | directed | 0.065917 | 0.048884 | 0.522138 | 25.17% | 8 | 0.671989 |
| fresh | epistemic | d1 | spectral | 0.089501 | 0.060315 | 0.119039 | -1.60% | 3 | 0.349005 |
| fresh | epistemic | d1 | belief | 0.087748 | 0.060313 | 0.153213 | 0.39% | 5 | 0.372773 |
| fresh | epistemic | last | mean | 0.081531 | 0.065903 | -0.000000 | -8.65% | 2 | -0.399955 |
| fresh | epistemic | last | structural | 0.075357 | 0.057986 | 0.145719 | -0.42% | 3 | 0.428471 |
| fresh | epistemic | last | size | 0.075040 | 0.057829 | 0.152894 | 0.00% | 0 | 0.410042 |
| fresh | epistemic | last | local | 0.072453 | 0.059565 | 0.210296 | 3.45% | 4 | 0.467280 |
| fresh | epistemic | last | directed | 0.068823 | 0.054524 | 0.287440 | 8.28% | 5 | 0.450327 |
| fresh | epistemic | last | spectral | 0.075505 | 0.059201 | 0.142363 | -0.62% | 4 | 0.402013 |
| fresh | epistemic | last | belief | 0.069767 | 0.055384 | 0.267759 | 7.03% | 5 | 0.386332 |
| fresh | epistemic | factor | mean | 0.038179 | 0.024716 | 0.000000 | -7.51% | 3 | -0.317180 |
| fresh | epistemic | factor | structural | 0.040357 | 0.027937 | -0.117376 | -13.65% | 2 | 0.494271 |
| fresh | epistemic | factor | size | 0.035511 | 0.024932 | 0.134885 | 0.00% | 0 | 0.550820 |
| fresh | epistemic | factor | local | 0.038238 | 0.026689 | -0.003111 | -7.68% | 2 | 0.549063 |
| fresh | epistemic | factor | directed | 0.039828 | 0.027949 | -0.088252 | -12.16% | 1 | 0.520436 |
| fresh | epistemic | factor | spectral | 0.035773 | 0.025205 | 0.122064 | -0.74% | 3 | 0.562888 |
| fresh | epistemic | factor | belief | 0.033780 | 0.023257 | 0.217181 | 4.88% | 7 | 0.611931 |

For D>=2 only (models fitted with all D), original epistemic d1 size/local/directed RMSE: 0.079681, 0.064094, 0.056752. Fresh: 0.102524, 0.093809, 0.073214. Last-observation and factorized controls do not consistently benefit. Task-conditioned features should be calibrated against the specific reasoning failure.

## Checks and cost

- original reaction: 3584 worlds; edges=267712, flow_edges=965520, flow_checks=75264, telescopes=3584, root_mixtures=3584, source_oracle=3584, target_pairs=8960, target_feature_changes=8078, zero_regret=2688.
- original epistemic: 720 worlds; likelihood_evaluations=1133568, likelihood_checks=70848, graph_mass=720, residual_checks=720, padding=288, fee_pairs=720, fee_shift=720, zero_regret=240, source_oracle=720.
- fresh reaction: 3584 worlds; edges=274268, flow_edges=989416, flow_checks=75264, telescopes=3584, root_mixtures=3584, source_oracle=3584, target_pairs=8960, target_feature_changes=8106, zero_regret=2688.
- fresh epistemic: 720 worlds; likelihood_evaluations=1133568, likelihood_checks=70848, graph_mass=720, residual_checks=720, padding=288, fee_pairs=720, fee_shift=720, zero_regret=240, source_oracle=720.

Edge passes and likelihood evaluations are operation counts, not measured wall-clock latency. Probability and geometric checks use floating tolerance. Exact source policy labels are separate from feature extraction. No optimized-DP compute comparison or speed claim. Core computations ran twice in isolated ECMAScript, with the pinned source. Standalone Node verification remains unexecuted. Relative imports use the checked-out commit; receipt comparison detects drift. No paid compute.

Reproduce from repository root: `node integrations/sweepweave-ts/srg22/verify.mjs`.
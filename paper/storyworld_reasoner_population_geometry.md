# SRG-25: Reasoner-population geometry

Registered protocol at 186429d9857bc22b3907aa039499d9cba397e597, source ef74263d59830712a83dee5a7f76f1f1f0b4fec9. Uses actual frozen SRG-24 candidate and outcome receipts, joined by cohort, base and proposal. No selected-tier-only sampling. 7532 candidate joins, 22596 training-policy replays, 4975 feasible rows in 253 nonempty bases. Each base has total weight one; its feasible variants share that weight. Original-only analysis includes feasible proposal zero rows with equal base weight.

## Geometry

Let M_ij be nominal regret of policy j in world i. For weighted mean mu, C=Σ_i w_i(M_i-mu)^T(M_i-mu)/Σ_i w_i. Eigenvalues λ of C are squared singular values of the weighted centered matrix with normalized weights. Participation rank = (Σλ)^2/Σλ². Relative profiles subtract each row's mean before column centering. Symmetric Jacobi solves 6x6 or 3x3 matrices; trace, PSD, orthogonality, reconstruction and column-permutation checks passed. Deterministic sign is largest magnitude loading positive. Eigenvectors in degenerate subspaces are not uniquely identifiable.

Column order d1,d2,terminal,uniform,beam,d4. Variance fractions ordered by decreasing eigenvalue.

| Population | Rows | Participation rank | Component variance fractions |
|---|---:|---:|---|
| full | 4975 | 3.17476 | 50.78% / 15.52% / 13.30% / 9.73% / 6.24% / 4.44% |
| relative | 4975 | 3.24739 | 47.85% / 19.81% / 16.30% / 9.20% / 6.83% / 0.00% |
| original | 199 | 2.85237 | 54.68% / 15.15% / 12.64% / 9.75% / 4.71% / 3.07% |

For matched feasible variants of a base, compare integer regret differences. The receipt contains strict ordering reversals for every policy pair, with denominators excluding ties or all comparisons. 13230 pairs have identical exact mean anchor regret; 2531 differ by at least 5 pp in a reserved policy. This is a direct witness that scalar anchor difficulty cannot determine target response. Pairs overlap.

Three-cluster k-means on row-centered six-policy profiles: deterministic farthest-first centers fit on cohort 1, held fixed when assigning cohort 2, weighted by base. Uses all six measured outcomes; descriptive only.

| Cluster | Cohort 2 base-weight share | Mean regret in column order |
|---|---:|---|
| 0 | 27.56% | 0.18436 / 0.18315 / 0.09900 / 0.13623 / 0.14756 / 0.07910 |
| 1 | 27.34% | 0.30667 / 0.21899 / 0.14001 / 0.03267 / 0.22723 / 0.03280 |
| 2 | 45.10% | 0.08374 / 0.05368 / 0.26711 / 0.05091 / 0.03881 / 0.01810 |

## Held-out response prediction

Only d1/d2/terminal anchors available at inference. Targets uniform/beam/d4 calibrated on other worlds; this is not zero-shot prediction of an unseen reasoner. Each leave-one-(cohort,tape)-out fold keeps all variants and target/bonus siblings together. Fit weighted ridge with training standardization and intercept, lambda=1, normalized mean training weight 1. Structural features H,W,C,B, optimum/nominal, informative density, sensitive-stage fraction and swap count. Compare scalar mean, PCA ranks 1/2/3, and raw anchor vector; PCA fit on training-only weighted covariance. Raw/PCA3 can differ under feature standardization/ridge. No tuning. Fit on all source feasible candidates and transfer frozen coefficients to two fresh unedited SRG-18 cohorts of 256 worlds each. Independent guard DP agrees with source oracle/rows; uniform-suffix and width-2 beam definitions preserved. This tests distribution shift, not private data.

| Split | Arm | Macro RMSE | Uniform / beam / d4 RMSE |
|---|---|---:|---|
| LOTO | structural | 0.08717 | 0.08369 / 0.11013 / 0.06770 |
| LOTO | scalar | 0.07646 | 0.07996 / 0.08481 / 0.06459 |
| LOTO | pca1 | 0.07428 | 0.07781 / 0.08083 / 0.06421 |
| LOTO | pca2 | 0.07401 | 0.07800 / 0.07963 / 0.06439 |
| LOTO | pca3 | 0.07412 | 0.07797 / 0.07978 / 0.06459 |
| LOTO | raw | 0.07412 | 0.07797 / 0.07978 / 0.06459 |
| Fresh 1 | structural | 0.08344 | 0.08707 / 0.09981 / 0.06345 |
| Fresh 1 | scalar | 0.08022 | 0.08346 / 0.09340 / 0.06380 |
| Fresh 1 | pca1 | 0.07490 | 0.08147 / 0.08062 / 0.06260 |
| Fresh 1 | pca2 | 0.07503 | 0.08102 / 0.08136 / 0.06271 |
| Fresh 1 | pca3 | 0.07478 | 0.08031 / 0.08168 / 0.06235 |
| Fresh 1 | raw | 0.07478 | 0.08031 / 0.08168 / 0.06235 |
| Fresh 2 | structural | 0.08577 | 0.07803 / 0.11289 / 0.06639 |
| Fresh 2 | scalar | 0.08062 | 0.07771 / 0.10061 / 0.06355 |
| Fresh 2 | pca1 | 0.07886 | 0.07523 / 0.09782 / 0.06354 |
| Fresh 2 | pca2 | 0.07834 | 0.07567 / 0.09639 / 0.06297 |
| Fresh 2 | pca3 | 0.07888 | 0.07630 / 0.09737 / 0.06296 |
| Fresh 2 | raw | 0.07888 | 0.07630 / 0.09737 / 0.06296 |

| Split | PCA2 macro reduction vs scalar | Per-target reductions (uniform/beam/d4) | Improved tapes | Gate |
|---|---:|---|---:|---|
| LOTO | 3.20% | 2.46% / 6.10% / 0.31% | 8/8 | FAIL |
| Fresh 1 | 6.47% | 2.92% / 12.89% / 1.71% | 8/8 | PASS |
| Fresh 2 | 2.83% | 2.63% / 4.19% / 0.91% | 6/8 | FAIL |

Joint promotion: **FAIL**. Required ≥5% macro reduction in all three splits, no target worsening >2%, and ≥6/8 improved held-out source tapes. No post-hoc substitution of another arm. Weighted MAE/R2 and per-tape and cohort metrics in receipt. Fresh transfer is without refitting. These are synthetic repeated public tapes; no independent statistical inference, actual model calls, private evaluation or editor modifications. Core computations ran in isolated ECMAScript with pinned inputs; standalone Node CLI not run. No paid compute.

Reproduce: `node integrations/sweepweave-ts/srg25/verify.mjs`.
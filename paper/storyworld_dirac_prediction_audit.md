# SRG-21: Dirac geometry and held-out regret prediction

[Protocol](../integrations/sweepweave-ts/srg21/PROTOCOL.md) committed before execution at fab2cb922cd3165185fc5ca9cf9e4693fbee0359; source benchmarks pinned to c15fa646cdd52690810f923512f929c05848b7df. This is a public exploratory feature audit, not model inference.

## Discrete operator

For graph vertices u,v and edge conductance w, define B column sqrt(w)(e_v-e_u). D on vertex plus edge space is the symmetric block matrix [[0,B],[B^T,0]], D²=diag(L,B^TB), L=BB^T. For degree matrix A, normalized incidence N=A^(-1/2)B (zero on isolated vertices) defines normalized Laplacian L_n=NN^T. Nonzero Dirac eigenvalues occur in +/-sqrt(lambda) pairs. For n vertices, m edges and c components, rank(B)=n-c, nullity(D)=m-n+2c. For any potential f, f^TLf=sum_e w(f_v-f_u)^2. Changing edge orientation changes incidence column signs but leaves L and Dirac spectrum invariant. The spectrum therefore cannot preserve directed causal order or reward labels on its own.

Compute normalized trace moments through degree four from M=A^(-1/2) adjacency A^(-1/2), with L_n=I-M on nonisolated vertices: t1=n_nonisolated, t2=n_nonisolated+tr(M²), t3=n_nonisolated+3tr(M²)-tr(M³), t4=n_nonisolated+6tr(M²)-4tr(M³)+tr(M⁴). tr(M⁴)=||M²||_F². Effective spectral rank t1²/t2. For raw L, use tr(L)=sum degree, tr(L²)=sum degree²+sum adjacency², tr(L³)=sum degree³+3sum_i degree_i sum_j adjacency_ij²-tr(adjacency³). These formulae are exact identities; implementation uses floating point. Feature vector is (t2/n,t3/n,t4/n,t1²/(n t2),n raw_t2/raw_t1²,n² raw_t3/raw_t1³). Bipartite graphs make odd adjacency moments zero and features redundant. These are low-order spectral summaries, not full spectra. Small reference matrices use symmetric Jacobi iteration until maximum off-diagonal magnitude <1e-13, with known spectra and trace-moment cross-checks. The reported off-diagonal residual is a numerical convergence diagnostic, not an interval-arithmetic eigenvalue certificate.

## Cohorts and invariances

SRG-18: 3584 target-specific worlds, public reachable state graph with parallel action edges. Unit conductance or 1+public edge reward. The independent integer Bellman implementation matches all 3584 source root Q vectors and 3584 oracle rollouts. 2816 exact-form moment comparisons across targets, 8960 matched target pairs, 2184 strict action reversals with unchanged unit features. SRG-20: 720 worlds, latent parity-signature quotient connected to feasible agent/history vertices, conductance P(signature, history | uniformly chosen agent). Graph mass sums to one. 288 padding comparisons preserve feature values and covariance PR. 480 matched fee comparisons preserve the epistemic graph features; 2660 of 11520 matched history/fee pairs have different unique optimal actions. This proves these feature sets cannot uniquely determine policy in these matched environments.

Energy and orientation tests: 448 reaction graphs, 90 epistemic graphs, four reference graphs (path, triangle, parallel edges, disconnected components). Moment checks and nullity identities pass. A small actual graph per domain is diagonalized for a reference gap; full cohort uses moments.

## Held-out prediction

Per-world targets are source-control regret divided by 3H+B for reaction or 8 for epistemic; no oracle-derived features. Reaction structural features: H,W,C,B, initial-equals-target, mean collect reward, initial collect reward, max last-stage collect reward. Epistemic structural features: K,R,D,fee, late-profile flag, root and union mask rank, target-in-root-span, root and mean count of exact target masks, mean observation precision. Size baseline adds vertex count, edge count, mean weighted edge conductance. Unit/weighted models add the six moments above; weighted reaction arm also includes unit moments. Epistemic belief arm adds posterior covariance PR, mean entropy and distinct posterior classes instead of graph moments. Intercept, training-only standardization, fixed ridge lambda=1, no tuning or clipping. Leave-one-tape-out evaluation keeps siblings together. RMSE and MAE in nominal utility fractions; R² vs per-fold training mean. Rank correlation computed within H/W or K/R/D strata, weighted by stratum size; omit constant strata. Tapes are public and repeated; these are descriptive comparisons, not independent confidence estimates.

### Reaction

| Outcome | Features | RMSE | MAE | R² | Relative RMSE reduction vs size | Improved tapes | Within-strata rho |
|---|---|---:|---:|---:|---:|---:|---:|
| d1 | mean | 0.14669 | 0.12825 | 0.00000 | -11.27% | 0 | -0.14390 |
| d1 | structural | 0.13426 | 0.11021 | 0.16231 | -1.84% | 2 | 0.28041 |
| d1 | size | 0.13184 | 0.10737 | 0.19226 | 0.00% | 0 | 0.29225 |
| d1 | unit | 0.13098 | 0.10692 | 0.20269 | 0.65% | 13 | 0.30008 |
| d1 | weighted | 0.12621 | 0.10119 | 0.25978 | 4.27% | 15 | 0.37512 |
| d2 | mean | 0.11989 | 0.09805 | -0.00000 | -13.40% | 0 | -0.21342 |
| d2 | structural | 0.10832 | 0.08296 | 0.18367 | -2.46% | 3 | 0.16768 |
| d2 | size | 0.10572 | 0.08096 | 0.22240 | 0.00% | 0 | 0.19084 |
| d2 | unit | 0.10544 | 0.08153 | 0.22661 | 0.27% | 11 | 0.18029 |
| d2 | weighted | 0.10413 | 0.07976 | 0.24571 | 1.51% | 14 | 0.20234 |
| d4 | mean | 0.05724 | 0.03504 | 0.00000 | -8.69% | 3 | -0.28403 |
| d4 | structural | 0.05282 | 0.03164 | 0.14824 | -0.31% | 6 | 0.05704 |
| d4 | size | 0.05266 | 0.03184 | 0.15347 | 0.00% | 0 | 0.07183 |
| d4 | unit | 0.05246 | 0.03113 | 0.15994 | 0.38% | 12 | 0.06445 |
| d4 | weighted | 0.05244 | 0.03108 | 0.16043 | 0.41% | 10 | 0.06263 |

Primary reaction gate: FAIL (4.27% relative improvement, 15/16 improved tapes).

### Epistemic

| Outcome | Features | RMSE | MAE | R² | Relative RMSE reduction vs size | Improved tapes | Within-strata rho |
|---|---|---:|---:|---:|---:|---:|---:|
| d1 | mean | 0.06836 | 0.03179 | -0.00000 | -3.07% | 4 | -0.28142 |
| d1 | structural | 0.06589 | 0.03316 | 0.07098 | 0.65% | 7 | 0.35744 |
| d1 | size | 0.06632 | 0.03334 | 0.05869 | 0.00% | 0 | 0.34505 |
| d1 | epistemic | 0.06706 | 0.03399 | 0.03767 | -1.11% | 2 | 0.31858 |
| d1 | belief | 0.06654 | 0.03365 | 0.05251 | -0.33% | 2 | 0.30810 |
| last | mean | 0.06020 | 0.04473 | -0.00000 | -2.64% | 5 | -0.40102 |
| last | structural | 0.05879 | 0.04002 | 0.04638 | -0.23% | 2 | 0.14600 |
| last | size | 0.05865 | 0.03984 | 0.05076 | 0.00% | 0 | 0.15366 |
| last | epistemic | 0.05848 | 0.03913 | 0.05635 | 0.29% | 6 | 0.17782 |
| last | belief | 0.07385 | 0.05209 | -0.50484 | -25.91% | 0 | -0.08139 |
| factor | mean | 0.04037 | 0.02982 | -0.00000 | -21.10% | 0 | -0.49850 |
| factor | structural | 0.03331 | 0.02099 | 0.31931 | 0.09% | 5 | 0.44992 |
| factor | size | 0.03334 | 0.02103 | 0.31814 | 0.00% | 0 | 0.45166 |
| factor | epistemic | 0.03244 | 0.02064 | 0.35427 | 2.69% | 5 | 0.53026 |
| factor | belief | 0.03404 | 0.02104 | 0.28899 | -2.12% | 2 | 0.38547 |

Primary epistemic gate: FAIL (-1.11% relative improvement, 2/8 improved tapes).

Joint promotion: **FAIL**. Gate requires >=5% relative RMSE improvement and >=75% of held-out tapes improved in each domain. A weak or negative result is retained; do not use the moment features as validated difficulty labels if the gate fails.

## Stage interventions

1120 single-stage identity cuts on representative tape, 953 change root Q. Euclidean distance between unstandardized six-feature moment vectors gives AUROC 0.53227 (unit) and 0.63932 (payoff weighted); tied distances rank averaged. 32 unit and 4 weighted cuts change Q despite moment distance <1e-10. Spectral distance is an exploratory causal sensitivity proxy. It omits action orientation, stage labels and full reward/observation semantics; feature invariance is not proof of isospectrality. The target/fee witnesses give identical underlying weighted or unit graphs in the relevant ablation, a stronger limitation.

## Reproduce

```sh
node integrations/sweepweave-ts/srg21/verify.mjs
```

All reported core computations ran in isolated ECMAScript from source benchmark modules. Standalone Node CLI remains unexecuted. No fresh SWMD runtime replay, actual model inference, private evaluation, editor changes or paid compute. Retain Dirac diagnostics for graph structure; consider task-conditioned directed boundary operators and policy regret calibration in the next experiment.
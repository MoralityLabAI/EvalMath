# CFH-03: learned certificate routing on graph-generator shift

Status: completed CPU public-development pilot, descriptive only. Recurrence promotion not warranted; retain cheap learned ranking and coefficient-conditioned escalation as candidate supervision. No paid compute, no independent-conjecture confirmation, no causal interpretation.

## Design and custody

Companion to CFH-02. Each deck contains six distinct graphs, and all five graph invariants are scored on the same deck. Graph order 8–10. Fixed seeds generate 240 train graphs (40 decks), 72 development graphs (12 decks), and 192 shift graphs (32 decks). Training and development use Erdos–Renyi, Prufer trees, random bipartite graphs and stochastic blocks; shift uses preferential attachment, Watts–Strogatz, split and geometric graphs. Balanced generator counts in each partition. All 504 graph roots have distinct (order, four-round Weisfeiler–Lehman hash) keys, with collisions discarded conservatively. Graphs are never reused in another deck or split. The five targets and repeated model seeds within each deck are dependent, and graph-generator shift within this public suite is not generalization to independent conjectures. No protected splits touched.

Exact CFH-02 coefficient enumerators and squarefree Sturm oracle supply training labels; cheap certificate outcomes are checked against gold for every graph-invariant pair. The learned policies receive graph features and one-hot invariant before the coefficient query, and may use coefficient features only when ranking already-queried unresolved candidates for Sturm. Offline simulation precomputes truth and feature tables, but policy ranking uses only the applicable stage's predictions. No actual latency or FLOP equivalence claim. All arms share max coefficient and root-query budgets, and actual logical calls are recorded. All non-abstaining decisions checked against the deck truth. A witness always requires a sound cheap or exact certificate; absence requires resolution of every candidate.

Neural arms: 2,305 parameters each, width 32; graph feature encoder plus polynomial feature encoder use the same input projection (zero polynomial channel and stage flag at prior step). Recurrent arm uses U h_prior in the posterior update, static arm uses U h_new, with equal parameter count and matched matrix shapes. Shared output head; binary cross entropy on prior witness labels and posterior labels of cheap-unresolved cases, 180 full-batch AdamW updates, fixed LR 0.003 and decay 0.01, seeds 11,29,47. Train-only feature scaling. Separate regularized logistic regressions for prior and posterior, random-deck order, degree rank and invariant-aware degree rank supply controls. The recurrent prior-only arm holds pre-query ranking fixed and escalates in that order rather than using posterior scores. This measures policy routing, not causal latent-state interventions. No checkpoint selection or hyperparameter fitting on shift.

## Measured results

Primary descriptive budget C=3 coefficient queries, S=1 Sturm query. Shift: 160 tasks, 127 witness-bearing tasks; 33 decks/targets without a witness. Means across all 160 tasks for query counts, across three fits for neural arms.

| Policy | Witness hits / 127 | Mean C | Mean S |
|---|---:|---:|---:|
| Uniform | 101 | 2.175 | 0.40625 |
| Degree | 101 | 2.20625 | 0.4375 |
| Invariant-aware degree | 99 | 2.225 | 0.45 |
| Logistic | 110 | 2.14375 | 0.45625 |
| Static neural | 119.333 | 1.89167 | 0.350 |
| Recurrent prior only | 115.333 | 1.92917 | 0.347917 |
| Recurrent neural | 120 | 1.92917 | 0.347917 |

Static per-seed hits: 120,118,120; recurrent: 121,119,120. Recurrent posterior versus its own prior-only: 14 additional discoveries across 381 seed-by-witness opportunities. Recurrent versus static: two additional discoveries across 381 opportunities, 0.525 percentage points, and 0.4167 percentage points across all 480 seed-by-task opportunities. Paired deck totals (loop minus static, summed across five targets and three seeds): 23 ties, three +1, two -1, two -2, one +2, one +3. Development: 42 witness-bearing out of 60 tasks; static and loop both total 122/126 across seeds, all 12 deck aggregate differences zero.

Other budgets on shift, mean witness hits (maximum 127):
| (C,S) | Degree | Logistic | Static | Recurrent |
|---|---:|---:|---:|---:|
| (2,1) | 93 | 95 | 112 | 113 |
| (3,1) | 101 | 110 | 119.333 | 120 |
| (3,2) | 106 | 111 | 121.667 | 122 |
| (6,1) | 121 | 125 | 124.667 | 123.667 |
| (6,2) | 123 | 127 | 127 | 125.333 |

No absence certificate possible under the primary budget for a six-candidate deck; unresolved decks abstain. Matching-size enumerator supplies no nonreal witness in any shift deck. Gains concentrated in independence and clique polynomial routing. No independence-based significance tests, post-selection estimates or neural causal claims.

## Disposition and limitations

No recurrence promotion: the development root-level aggregate signal is exactly zero, shift advantage tiny and reverses at larger budgets. The cheap static router is a viable candidate for subsequent development. The posterior's extra coefficient information is useful; static consumes that information too. The prior-only control is not a physically matched causal sham. The repo's mechanistic-resolution preflight cannot earn READY: only 12 development deck clusters, no independently calibrated intervention sham, no sealed independent conjecture families; strict planner was not run with invented sham inputs. This is a pilot rather than confirmatory evaluation. No new GPU allocation. Next: acquire independent mathematical families with real invariant-derivation uncertainty and explicit verifier costs; pre-register route-ID and exact-proof gates, evaluate coefficient-query efficiency and aggregate by independent conjecture root. Compare static, logistic and exact theorem-aware controls before spending on recurrence.

## Replay

From gyms/CFH03:
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python learned_router.py > receipt.json

Python 3.13.5; Torch 2.10.0+cpu; NumPy 2.3.5; NetworkX 3.6.1; scikit-learn 1.8.0; SymPy 1.14.0. CPU single thread; no saved model weights. 14,300 outcome records with exact counts, all root edge lists and generator assignments, 504 distinct graphs / 2,520 graph-invariant pairs. Public reproducible seed list. SHA-256 source: 08be66c2cc0e5dec465593180520f3698d4964e9c7c2dbc3973ecd36152c0378; CFH02 source: 5729c7e826a304f6e81c18a42f08f64fad491c08d5b028f31942861cd02b389e. Receipt: caa6faa84b4096f4b7cf8481b902b066149d0e3a581093aff12e0b1bdb2bda0c. Gzipped receipt (gzip -n): fd5cc1ca13190cc86261fcafeb306b1ba020d62f75dba7b20b8a47c59bedca48. Source blob matches local tested file. Generated receipts are not committed. Repo-wide CI and Lean rebuild remain outstanding.

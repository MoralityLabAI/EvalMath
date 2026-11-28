# MIC-10: conditional decomposition and bounded-width exact search

Cloud CPU public development follow-up to [MIC-09 draft #93](https://github.com/MoralityLabAI/EvalMath/pull/93). The four inherited source files are pinned from cf2255ba898889fd46e86b4e1c603ccb2fbb96e6. No upstream manuscript bytes, model training, or paid GPU allocation.

## Mathematical scope

Consider the same binary maximum-weight feasible-mask problem as MIC-06–09. Each conflict is a two-variable factor, each support clause (antecedent implies at least one alternative) a factor on the entire clause scope, and the objective is additive positive integer weight. The primal graph makes each factor scope a clique. A separator S partitions its complement into components C_i. Fix a separator assignment a. Every original factor lies entirely in S or touches exactly one C_i, so its truth can be determined from that component and its separator boundary. Check separator-only factors and maximize each component independently; an infeasible component invalidates that assignment. Thus V=max_a[w_S(a)+sum_i V(C_i|a)], with infeasible branches omitted. Union of component witnesses with a reconstructs a feasible global mask. Boundary cache keys include every separator bit occurring in the assigned component clauses. The implementation rejects overlapping or incomplete partitions and crossing factor scopes; antecedent-only star connectivity after separator removal would be unsound.

For a prescribed ordering, variable elimination collects all factors involving the next variable, sums them and maximizes over its two values to form a factor on remaining neighbors. This preserves the maximum over all uneliminated assignments, by distributivity of max over additive factors independent of the eliminated variable. Backtracking stored argmax tables yields an optimal assignment. Induced width w limits each generated factor to at most 2^w entries. Work also depends on factor incidence, table indexing and order construction; no polynomial bound for general graphs. The dense NumPy implementation uses penalty -(sum weights+1) per violated factor, so any infeasible full mask has negative score and the all-zero feasible mask has score zero. For the small positive-weight integer domain no overflow is possible. Independent dictionary replay uses missing entries as infeasible rather than a finite penalty, reconstructs the optimum from the original constraints and supplied order, and checks the witness and claimed value/upper bound. It is a separate computational implementation, not a Lean or cryptographic proof. Separator replay re-enumerates every conditional component without using cached answers, sharing only the basic clause predicate. Both checkers reject altered upper bounds in tests.

## Public design

72 roots: four inherited generator families, 32/64/128 vertices, two fresh seeds 6000..6001, three structural conditions. Original generator unchanged. Planted one-hub and three-hub conditions connect relabeled local blocks (size at most 8, each connected by conflict path edges) through separator vertices, with crossing support clauses restricted to a single block and hubs. These are synthetic controlled topology tests, not independent real mathematical families. Each separator heuristic attempts at most three vertices and requires at least two components of size <=10. Compare greedy primal degree, exhaustive one-step balance scan and seeded random removal. The elimination planners use min-degree and min-fill induced-graph heuristics; skip exact elimination if planned width >10. Hybrid uses min-degree planning first, runs elimination when width <=10 and otherwise runs the MIC-09 combined 512-normalization search. All seven arms are descriptive development comparisons; no held-out seal or prospective model claim. Different caps and arithmetic work; no fixed-time fairness claim.

## Final run

| Structure | MIC-09 baseline | Hybrid | Degree separator | Balance separator | Random separator | Min-degree VE | Min-fill VE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original | 15/24 | 15/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 |
| One hub | 20/24 | 24/24 | 22/24 | 24/24 | 0/24 | 24/24 | 24/24 |
| Three hubs | 24/24 | 24/24 | 15/24 | 1/24 | 0/24 | 24/24 | 24/24 |
| All | 59/72 | 63/72 | 37/72 | 25/72 | 0/72 | 48/72 | 48/72 |

Hybrid certifies 24/24 at n=32, 23/24 at n=64, 16/24 at n=128; nine original roots remain interval-valued. Each feasible incumbent independently checked; all available bounds intersect. No claim of optimality for unresolved roots. All 62 applicable separator receipts and 96 elimination receipts pass independent replay; repeated orders on the same root are not independent instances. Five targeted tests pass (16-vertex exhaustive separator optima on 12 roots, explicit crossing-disjunction rejection, two elimination policies on 32 exhaustive 9-vertex roots, boundary and width-cap behavior, hybrid exactness). First draft had a local/global feasibility-variable collision caught by a boundary test; fixed before final measurements. A greedy degree selector can miss a planted separator, so the theorem tests explicitly provide a known separator rather than assert heuristic completeness.

Final one-thread CPU timings, producer-only, including planning and fallback; independent replay excluded. Baseline/hybrid means 38.705/28.690 ms across all roots; 93.607/66.463 ms at n=128. On original roots 69.880/72.138 ms; on one hub 28.222/6.680 and three hubs 18.012/7.253 ms. Hybrid gains mostly come from planted low-width cases. Degree separator mean 5.805 ms across all roots including failures, 11.072 ms on 37 successful roots; balance mean 6.156 ms including failures, 6.851 ms on 25 successful roots. Min-degree VE mean 6.912 ms on applicable roots; min-fill 13.893 ms, same coverage. The min-fill ordering's reduced width on some instances does not offset its planning cost here. Times are single-machine observations, not portable guarantees. Work counters include factor cell reads, separator assignment counts, local masks, clause checks, cache hits, candidate scans, and inherited B&B counters; counters are not interchangeable or fully exhaustive. Raw output generated in 8.552 s, including verification replays and all policies.

Preflight uses the hybrid-vs-baseline objective gain normalized by total root weight and averaged per generator family. Mean +0.010265 pp; objective mostly unchanged even when optimality is certified. Nominal deterministic same-policy sham is zero (placeholder; no independent sham calibration), four lineages, no seal, inherited 5 pp floor. Repository planner strict exit 2, REDESIGN_OR_PILOT_ONLY. The preflight is a retrospective planning diagnostic; certification coverage and timing are separate metrics. No learned selector was trained: cheap deterministic planning was the stronger next step given MIC-09's negative learned gate. No corpus promotion.

## Replay

From the repository root:

    cd gyms/MIC10
    OMP_NUM_THREADS=1 python -m pytest -q test_mic10.py
    OMP_NUM_THREADS=1 python mic10.py > results.json
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC10/preflight_input.json --strict

Source SHA-256 mic10.py 39be9c4e17acfdfad382814e2fd28365bc2005294b094874a8e7273cff1ae069; test_mic10.py a67f4670bfdf37cfc0597af448d458dcee5239174eacdfd431c18ed1ba8af7d9. Final timing-dependent raw receipt SHA-256 044ee123350d78c4941781365c145c2a982706ea3c3cfc00cc24e94eaf01d08d, kept in cloud sandbox. Planner Git blob 0ff062f76f5534d9f18425f986ae3e750397f50c inherited from MIC-09. Full repository CI and Lean kernel proof outstanding.

Next: use width-capped elimination inside branch-and-bound after conditioning and propagation, rather than gating only at the root. Compare against same solver with component enumeration, account for actual table reads and calls under explicit budgets, and independently replay residual-state certificates. Only revisit learned cutset selection when there are useful alternatives beyond degree/min-fill with a demonstrably nontrivial cost frontier. The original textual mathematical-history question remains untested.

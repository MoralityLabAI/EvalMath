# MIC-09: forced support propagation and exact component reduction

Public cloud CPU follow-up to [MIC-08 #92](https://github.com/MoralityLabAI/EvalMath/pull/92). Inherited core.py/run.py/audit.py pinned from b436128c3880edd8d5a594c94853c98aa5ed5b79. No manuscript bytes used.

## Mathematical argument

A state consists of an active mask S and required mask R contained in S; feasible continuations X satisfy R subset X subset S and the original support and conflict constraints. Positive-support closure deletes any node whose clause has no active supporter, preserving every feasible continuation. If a required node has exactly one surviving alternative in any support clause, that alternative belongs to every feasible continuation; add it to R. Remove every conflict neighbor of R; if two required vertices conflict or a required vertex is deleted, the state is infeasible. Iteration terminates since S shrinks or R grows on every nonterminal change. These are exact inference rules for the specified positive-support/conflict system.

After closure, build an undirected graph on S using active conflict edges and edges joining every active antecedent i to each active alternative j in each of its support clauses. This represents the connected components of the active constraint hypergraph. Every active constraint lies entirely in one component, so feasible continuations are Cartesian products of component-wise feasible continuations with their local forced masks. The additive objective yields an optimum equal to the sum of component optima. A component with no conflict is solved by retaining its entire active mask, because support closure guarantees feasibility and weights are positive. Components of size <=8 are solved by exact submask enumeration, conditioned on their forced mask. Retaining one optimal component mask, marking its vertices forced, and removing its other vertices preserves the state optimum; it may discard equally optimal alternatives. If a component has no feasible continuation, the state is infeasible. No global optimum is lost. The reference applies this reduction only if at least two components exist, and only to proper components meeting the size/conflict criterion.

Include/exclude branches partition all feasible continuations of an unresolved state; the clique-partition upper bound covers each remaining continuation. State reductions above preserve its optimum, so the frontier still covers the unresolved optimal value. The reported interval is a verified feasible incumbent and an upper bound conditional on search implementation correctness. A full independently replayable proof log or Lean certification of the search is not provided.

## Structural development experiment

72 fresh public roots: 4 original generators x 3 sizes (32,64,128) x 3 seeds 4000..4002 x 2 structural conditions. Half are original sparse generators; they are not guaranteed connected. Half are disjoint unions of independently generated size-eight blocks with randomly relabeled vertices (planted decomposition). Both arms share the deterministic initializer and clique bounds of MIC-08. 512 child normalizations after initialization is the common cap. A normalization can run extra closure passes, forced inference and exact submask checks; this is NOT an equal-operation cap. Timing includes initialization, search and feature work, and is a single machine-specific measurement. No timed cap experiment. Report raw closure, support, component, enumeration and cache counters separately.

| Arm | Certified /72 | Mean objective / pooled incumbent % | Mean ms | Mean normalizations |
|---|---:|---:|---:|---:|
| Baseline | 34 | 98.940 | 60.446 | 331.389 |
| Forced propagation | 38 | 99.229 | 62.786 | 314.694 |
| Factor | 51 | 99.584 | 36.508 | 172.611 |
| Both | 56 | 99.846 | 38.727 | 156.306 |

Original generators: certificates 15/36,19/36,15/36,20/36 respectively; mean times 55.784,57.567,69.840,74.392 ms. Planted disjoint blocks: 19/36,19/36,36/36,36/36; mean times 65.107,68.004,3.176,3.061 ms. For planted 128 vertices, baseline 0/12 vs combined 12/12; 154.718 vs 6.337 ms. All 36 planted cases are certified by decomposition. Pooled optimum intervals close on 56/72; remaining 16 are unresolved. Do not treat pooled best incumbent as true optimum. Mean pooled relative interval width on original generators 13.822%; planted zero. Combined mean raw closure calls after initialization 219.069, enumeration checks of eligible masks 2162.056, enumeration predicate checks 3982.639. Baseline 331.389 raw closure calls and zero enumeration; counters omit some graph traversal, sorting and arithmetic. Overall timing gains are driven by planted decomposition; no general speedup claim.

## Learned scan gate

Three 161-parameter MLPs (seeds 17/29/43) trained for 120 full-batch Adam steps on 573 search states from 48 separate size-16/32 conflict/mixed roots (seeds 5000..5005, both structural conditions, 128 normalization cap), 237 positive labels. Eight features derived from active size, required size, conflict degrees, remaining weight and original support count. Label is existence of a reducible proper component after propagation, not downstream speedup. Learned gate only decides whether to run the exact component scan; it cannot authorize pruning. Compare periodic gate (first two calls, every eighth, or active size <=16), always-on decomposition and no decomposition. The classifier's diagnostic confusion table is on a replay of always-on trajectories, separate from timed gate evaluation. It is clustered by root and does not describe the gate's own state distribution.

| Gate | Certified /72 | Mean ms | Mean objective / pooled incumbent % |
|---|---:|---:|---:|
| Always on | 56 | 38.727 | 99.846 |
| Periodic | 55 | 32.149 | 99.738 |
| Learned (mean of 3) | 56 | 40.151 | 99.846 |

Each learned seed returns the same objective as always-on on all 72 roots (zero observed objective effect and seed disagreement). No additional optima certified. Periodic loses one certificate. The learned selector incurs overhead, with no demonstrated performance advantage. The gate and structural comparisons are public development diagnostics, not independent confirmation. Four generator lineages are not established independent; planted and original variants share family mechanisms. Repository planner strict exit 2, REDESIGN_OR_PILOT_ONLY; effect zero, inherited floor 5 pp, no calibrated 95/95 sham quantile, no sealed holdout. No model or corpus promotion.

## Replay and integrity

    cd gyms/MIC09
    OMP_NUM_THREADS=1 python -m pytest -q test_mic09.py
    OMP_NUM_THREADS=1 python mic09.py > results.json
    OMP_NUM_THREADS=1 python gate.py > gate_results.json
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC09/preflight_input.json --strict

Four tests passed twice. Exhaustive 7-vertex propagation checks (128 active masks x 3 required masks per family), independent 8-vertex component optimality checks, small exhaustive 9-vertex search checks at 4 caps, and exact MIC-08 baseline agreement on 12 replay roots. Initial structural run 14.33 s; gate training/evaluation 15.70 s. After adding the optional gate hooks, the full structural replay reproduced every objective, upper bound, mask and selected work counter on all 72 roots. Original timing results source hash cb634fb909f9981217be921e9b7bcfc6d503a4557c0ffe114bfc57215f56813d; final replay source hash 7a62c3b0c109f878cb6f33f59fb0533bad9252f6f5f40ff572961de961507091. Original raw result SHA256 d42a831342142e827459f25a5e54b1004239d52bba0c4b3470f9b033cc180f28; final structural replay fe0d92aca196c981461b8f8976995298c080c1d60788b2148ef34bb7190ee33a; gate 01911c81dc883273a9694ed8943b702f9beb8232b1ece52f9cffcf522a4fd51e. Raw files remain sandbox artifacts, not committed. Planner verified Git blob 0ff062f76f5534d9f18425f986ae3e750397f50c. Full repository CI and independent confirmation outstanding. No paid GPU.

Next: use exact decomposition at the root and branch over separators or small treewidth rather than assuming the graph decomposes completely; count separator enumeration and independently replayable bound certificates. Compare against strong deterministic separator heuristics before further learned gate work. The original textual discovery-history question remains untested.

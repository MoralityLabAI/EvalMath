# MIC-08: learned child ordering versus bounded certified search

Public CPU development after [MIC-07 #91](https://github.com/MoralityLabAI/EvalMath/pull/91). Reuses the pinned MIC-07 code as core.py (Git blob 2225c0d6c29128261d30b73dee41dbc0366dd9d7). No licensed manuscript content or paid compute.

## Method

Train three 897-parameter MLP rankers, seeds 17/29/43, 120 Adam steps, on 96 n=12 conflict/mixed roots, 658 teacher decisions labeled by an exhaustive feasible-submask table. Ten child-state features include weight, degree, active size, immediate loss, clique upper bound and support clauses. This is a learned child-ordering test, not a recurrent architecture test. Public development roots: 4 lineages x 3 sizes (32,64,128) x 4 new seeds, 48 roots; 144 learned model-root pairs. Conflict probability scales as min(.4, expected degree/(n-1)), expected degree 6 or 9 for mixed. Named families share generator mechanisms; no independent lineage or graph-isomorphism audit. No sealed confirmation.

The common initializer is deterministic weighted-degree removal followed by support closure. Common budget 512 closure calls AFTER initialization, common edge selection and two greedy clique-partition upper bounds. Positive support closure removes nodes impossible in any feasible descendant. The initial full mask represents all possible solutions. A conflict edge requires at least one endpoint removed. Search maintains a feasible incumbent and a frontier whose admissible bounds cover every still-unresolved subproblem. Prune only when upper bound <= incumbent. The minimum of the two clique partition bounds is valid since every feasible subset selects at most one vertex per clique. Exact upper = max(incumbent, all surviving frontier bounds). Returned equality certifies optimality, conditional on correctness of the search implementation. Full proof trace or independent kernel replay was not emitted. An independent brute-force oracle verifies small-case bounds and exactness. Learned scores affect traversal only; never pruning or feasibility.

Retrospective stronger include/exclude control branches on one vertex, either excluding it or forcing it and removing all neighbors. Maintain a forced mask; prune if support closure deletes a forced vertex. The children partition feasible subsets by vertex membership, avoiding the overlap of deleting one or the other endpoint. Same initializer and bound, same search-call cap. Also audit soft elapsed-time deadlines derived from learned mean runtime on each root, allowing up to 8192 calls. Deadlines are checked between whole expansions, not hard time caps. Measurements include initialization, feature extraction and neural inference; training excluded.

## Results

Mean objective divided by the pooled best feasible incumbent over all arms, percent. This denominator is a retrospective reference, NOT the true optimum unless the pooled interval closes. Lower/upper intervals remain explicit in raw receipts.

| Policy | 32 | 64 | 128 | All | Certified |
|---|---:|---:|---:|---:|---:|
| Bound-ordered DFS | 99.603 | 91.360 | 93.020 | 94.661 | 5/48 |
| Loss-prioritized DFS | 96.291 | 91.486 | 90.436 | 92.738 | 5/48 |
| Best-first | 85.710 | 76.686 | 81.078 | 81.158 | 5/48 |
| Learned DFS | 99.249 | 89.266 | 91.481 | 93.332 | 15/144 |
| Include/exclude DFS | 100.000 | 98.433 | 98.231 | 98.888 | 22/48 |
| Timed include/exclude | 100.000 | 99.556 | 98.430 | 99.329 | 22/48 |

Include/exclude certificates by size 16/16, 6/16, 0/16. Pooled mean relative interval width 16.515%; by size 0,16.082,33.464%. 26 roots remain uncertified. All returned incumbents verified; pooled intervals intersect. No exact-optimum fraction asserted for unresolved cases.

Bound/learned/include-exclude mean runtime 60.28/68.48/55.10 ms, actual closure calls 490.7/487.3/341.3. Timed include/exclude 60.95 ms mean, 391.5 calls, 26/48 observed soft-deadline overruns (max 0.552 ms). No strict equal-time performance claim. The learned ordering loses to the same deletion search with deterministic bound ordering; structural branching is stronger still. Learned vs bound primary effect normalized by total root weight = -0.43265 pp; inherited minimum scientific effect 5 pp. Worst within-root seed disagreement 3.8926 pp; 4 unverified family summaries and unsealed confirmation. Repository planner strict exit 2, REDESIGN_OR_PILOT_ONLY. All effects are public development diagnostics; include/exclude audit selected retrospectively.

## Reproduction

From repo root:

    cd gyms/MIC08
    OMP_NUM_THREADS=1 python -m pytest -q test_mic08.py
    OMP_NUM_THREADS=1 python run.py > results.json
    OMP_NUM_THREADS=1 python audit.py > audit_results.json
    python summarize.py
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC08/preflight_input.json --strict

Local cloud CPU, torch 2.10.0+cpu; 29.85 s primary run, 4 tests passed including 7-node exhaustive submask/closure/bound comparison, 9-node exact search, teacher replay and forced-branch checks. Full repo CI and independent confirmation pending. The raw timing-dependent outputs are local downloadable artifacts; SHA-256 results.json 839031f26b4bc22f7350d6d49867129df9b699c041994f7ce8dd65a3294c9e70, audit_results.json 1b339c5e8f9aede8a371b6d1888d2d09bcce1f55bf3b9ce77a817f16862163e4. Source SHA-256 run.py bf8b2a9f5c2af7a7304a7308e99bd93017606d283e9840e1dc5bdeba807c848e, core.py a664053ab35978461b8fbe1d016bce120eaccdc960885087f10b5c88e1000b39. No weights or raw run files committed.

## Next gate

Prefer the include/exclude state space. Strengthen it with forced singleton-support propagation, component decomposition when the full constraint hypergraph separates, and checked admissible bound certificates; compare against the same include/exclude solver before learned branch selection is attempted again. Keep work, time, incumbent, frontier upper bound and certificate status separate. No corpus promotion or new training spend.

# MIC-13: proof-carrying exact search and global frontier replay

Public cloud CPU follow-up to [MIC-12 draft #96](https://github.com/MoralityLabAI/EvalMath/pull/96) and [MIC-11 draft #95](https://github.com/MoralityLabAI/EvalMath/pull/95). The six inherited modules are pinned from f5bc306abbdde1dded55e79ba4b74849ddc6b1c1. No manuscript ingestion, new training, or paid GPU.

## Certificate semantics

For the established positive-integer weighted binary constraint domain, (S,R) denotes every feasible X satisfying R subset X subset S. The certificate is a finite rooted proof DAG containing raw and normalized states, component optima, branch partitions, and justified leaf closures or explicit open frontier bounds. The verifier is supplied the original problem by the caller; in this experiment the pinned generator reconstructs it from each row. Masks are serialized as hexadecimal strings.

Independent CNF unit propagation checks every recorded propagation outcome. Each positive-support clause becomes an implication represented as a CNF clause, and every conflict becomes a two-negative-literal clause. Unit propagation preserves all feasible continuations; contradiction proves infeasibility. For component reduction, verify there are no active clauses connecting the selected component with its complement (satisfied clauses may be ignored), then check the local optimum with the forced mask retained. A feasible full component has maximal weight by positivity; otherwise enumerate every submask for components of size at most eight. Forcing an optimal local witness and excluding its complement preserves the best objective.

Branch on a free vertex j. Exclude j, or include j and exclude all its conflict neighbors; the two children partition every feasible continuation. The checker reconstructs these raw child states from the original graph. The terminal leaf contains the full active mask as a feasible solution, which maximizes positive weight. A residual elimination leaf is verified using the independent MIC-11 sparse-factor checker. A clique cover upper bound partitions all active vertices into disjoint conflict cliques; verify membership, disjointness, coverage and every pairwise conflict, then sum maximum clique weights. A pruned bound must be at most the final verified incumbent. Open leaves retain their bounds. Alias references, if present, require the same normalized state and an earlier reference; cycles and unreachable nodes are rejected. No alias occurred in this benchmark, so alias handling remains unexercised by the reported replay. The proof yields a global upper bound by taking the maximum over branch children, and finally the maximum with the checked feasible incumbent. Equality certifies optimality; unequal values certify an interval. The checker does not call producer traversal, normalization or bound-construction methods. It shares the problem representation and the already tested sparse VE checker. This is executable verification under the stated finite-domain assumptions, not a Lean proof of the implementation, a hardened arbitrary-input parser or an adversarial security audit.

The checked work ledger reconstructs branch count, child normalizations, and successful VE cell charges. Unsuccessful attempt costs, producer support/enum counters, and timing remain descriptive, not independently certified by the trace. The check of the proof does not reconstruct chronological incumbent updates, since a valid final incumbent suffices for all pruning.

## Public experiment

72 fresh graphs: 4 inherited families x sizes 32/64/128 x seeds 10000..10001 x original/one-hub/three-hub conditions. Both MIC-11 baseline and periodic elimination run with 512 child normalizations and inherited width-10 residual budgets (250000 factor cells, 250000 planning scans, 64 attempts). The instrumented producer exactly matches the previous uninstrumented solver on value, upper, incumbent mask, normalizations, expansions, VE cells and VE attempts for every root-policy pair. Timings are single-machine, sequential, and descriptive.

| Policy | Certified optima /72 | Nodes | Prior mean ms | Instrumented mean ms | Independent check mean ms |
|---|---:|---:|---:|---:|---:|
| Baseline | 55 | 13336 | 42.126 | 46.929 | 69.369 |
| Periodic VE | 63 | 6474 | 47.506 | 50.060 | 55.685 |

Original graph counts: 12/24 vs 15/24. One-hub: 21/24 vs 24/24. Three-hub: 22/24 vs 24/24. Pooled interval closes on 63/72; nine unresolved. Both modes return independently checked bounds on all 72 roots. Across the 144 complete certificates: 19810 nodes, 9833 branches, 15382 component reductions, 819 terminal leaves, 1940 infeasibility leaves, 6098 pruned leaves, 553 exact VE leaves, 567 open leaves and 3103870 charged VE cells. Run 23.985 s including production, checking, previous solver comparison and serialization; second independent serialized replay 10.152 s. The full proof archive is 18,374,357 bytes before newline delimiters and 958,285 bytes compressed. Data archive and results are local generated artifacts; not committed to source repository.

Four targeted tests passed in 1.54 s: 2916 exhaustive ternary conditioned states, 16 nine-node graphs under 8 policy/cap conditions each, component/VE boundaries and malformed proof checks. Second replay reads the serialized archive rather than in-memory objects, checks all 144 proofs, and rejects all 12 representative corruptions: false upper/lower, false normalization, unreachable node, wrong work ledger, missing/swapped branch, missing clique, false component infeasibility, false residual value, wrong residual state, unsafe pruning. These are finite checks and do not establish rejection of every possible malformed proof.

The retrospective resolution planner compares baseline interval width minus periodic width normalized by total root weight. Mean gain 1.206713 pp below inherited 5 pp floor. Four generator lineages, unverified independence, no seal, deterministic zero sham placeholder. Actual repository planner strict exit 2 REDESIGN_OR_PILOT_ONLY. This does not invalidate the finite verification receipts; it prevents promotion of the performance comparison. No model trained. Full repository CI not yet run.

## Replay

    cd gyms/MIC13
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python -m pytest -q test_mic13.py
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python mic13.py > results.json
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python replay_frontier.py
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC13/preflight_input.json --strict

Source SHA256 mic13.py 873c10d13ece3ad0a645fd018404d3146ff27292318bcf52518278e5ff8120f3, tests 94397fc3aa4a4082fd47169defcb1e54101631528977dee93918a97a601aaa10, replay 58ccb4aa9107fe55be5b4352a3dab5798b62feea284cfc7c9bda49162c022706. Original results SHA256 9490766fcd3aad9b7464fa38e889e609f6f97c806110f693ed8d0568b3c4270b; compressed proof archive 281200c167336532e0a3120629c61b5fad0b0ebd818b718ea80a001ef12fc6a5; serialized replay receipt 43851aa26322ea22d75718db908b2d1f66bb6fa7f5412f33f273f99e39f80893. Timing and gzip header timestamps vary on replay. Planner verified Git blob 0ff062f76f5534d9f18425f986ae3e750397f50c.

## Next

Separate proof production and verification into minimal independent modules, harden the input schema and exercise alias/cycle/duplicate handling. Extract typed, verified inference obligations from the proof DAG with root-grouped splits, compare true chronological and shuffled obligation schedules, and include exact teacher cost, admissibility and proof coverage. Validate the receipt calculus in Lean before calling it a formally certified implementation. The original DLMST discovery-history hypothesis remains untested; public manuscripts remain reference-only and quarantined for training. No training allocation is proposed.

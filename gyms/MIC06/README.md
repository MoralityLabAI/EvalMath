# MIC-06: weighted atomic revision with positive supports and mutual exclusion

Public CPU development follow-up to [MIC-05 draft #88](https://github.com/MoralityLabAI/EvalMath/pull/88). The new gym uses original binary constraint systems, not extracted DLMST manuscript content and not a literal signed version of every integer recurrence. The monotone closure Lean candidate is separately filed in [MathCan draft #280](https://github.com/patrickdugan/MathCan/pull/280); kernel validation pending.

## Mathematical boundary

A block is a binary vector z. Support clauses impose z_i <= sum_{j in A} z_j; all support clauses associated with i must hold. Singleton A is an implication; larger A is a positive disjunction. Conflict edges impose z_i+z_j<=1. The objective is max sum_i w_i z_i, with positive integer weights. Zero is always feasible. Positive supports alone preserve union closure: if i is in a union of feasible blocks, it has support in some constituent and hence in the union. Deletion to the greatest support-feasible subset is complete for that subproblem. Mutual exclusion destroys the property, as shown by two conflicting singleton blocks whose union is infeasible. Conflict-only optimization is maximum-weight independent set exactly; unit weights give maximum independent set, hence the general optimization problem is NP-hard. Feasibility of a proposed block is directly checkable. This is an original finite proxy for jointly revisable proof obligations, not a claim about Lean or general reasoning complexity.

## Public experiment

Four generators: conflict-only, conflict plus singleton implications, conflict plus two-way alternative supports, and mixed support clauses. Every generated root has at least one conflict; all indices and weights are synthetic. Train 192 size-ten roots (96 conflict-only and 96 mixed, seeds 0..95). Develop on 128 roots (32 per generator, sizes 10 and 12, seeds 1000..1015). Exact serialized roots are distinct within and across train/development; no graph-isomorphism or broader source-family independence claim. Different sizes and model seeds are not independent lineages. Implication and disjunction are withheld named generators, but training mixed roots already contain individual clauses of both kinds. No sealed confirmation.

Train 3,297-parameter GRU rankers with identical architecture and local features (weight, conflict degree, support/reverse degree and support arity), three matched initialization seeds 17/29/43, 120 full-batch Adam updates, lr 0.008. Graph arm uses three normalized adjacency messages (conflict, support, reverse support) at each of three tied visits; node-only arm uses its own state for each message. Alternative-support membership is aggregated into pairwise features; the exact verifier retains original clauses. Binary cross-entropy targets each node's marginal inclusion across ALL exact optimal masks. Learned priorities are fixed during a repair trajectory, not recomputed as clauses change. This tests graph information in a recurrent ranker, not recurrence versus feedforward architecture. Model parameter counts are matched; operation counts and wall time are not.

Repair starts with full support closure, selects the first conflicting edge in fixed enumeration order, removes one endpoint according to priority and propagates support deletions, then repeats. Final integer bitmask is independently checked. Baselines include static weight, static weighted degree, seeded random priority and two-child immediate objective lookahead (same first conflict, greater work). Retrospective stronger baselines: dynamic weighted degree and global removal minimizing exact immediate weighted loss per removed active conflict after support closure. All policies use exact objective and feasibility checks. Exhaustive bitmask enumeration (at most 4096 masks/root) supplies training labels and evaluation ceiling. Oracle labels are never used to choose an action at evaluation.

## Results

Mean fraction of exact optimal objective, percent. All 128 oracles positive. Each learned result averages three seeds per root; other policies one run per root. The retrospective baselines were added after observing the primary run and remain descriptive.

| Family | Weight | Static degree | Random | Two-branch | Dynamic degree | Global removal | Node-only | Graph |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Conflict | 84.793 | 90.025 | 63.178 | 84.793 | 92.463 | 94.380 | 89.762 | 96.983 |
| Implication | 73.318 | 72.650 | 74.646 | 79.040 | 80.215 | 83.835 | 80.585 | 90.622 |
| Disjunction | 63.490 | 71.620 | 52.984 | 71.040 | 81.015 | 85.240 | 78.643 | 89.133 |
| Mixed | 77.779 | 82.531 | 40.233 | 85.055 | 86.202 | 89.781 | 81.945 | 91.064 |
| All | 74.845 | 79.206 | 57.760 | 79.982 | 84.974 | 88.309 | 82.734 | 91.951 |

Graph/node mean gap +9.2168 pp, graph/global +3.642 pp. Graph hits the exact optimum 214/384 model-root pairs, node-only 115/384, global removal 54/128. All 1,280 main-policy and 256 retrospective-control outputs are verifier-valid and bounded by exact oracle; no invalid block committed.

Mean support+conflict check counts: weight 104.28, static degree 96.20, random 104.86, two-branch 175.55, node-only 96.69, graph 92.52, dynamic degree 150.88, global removal 949.85. Counters omit feature construction, neural computation, some auxiliary degree/objective arithmetic, and final validation; they are not common elapsed-time or FLOP budgets. Do not claim speedup. Primary sandbox training/evaluation wall time 4.43s, CPU PyTorch 2.10.0+cpu. No paid compute.

## Resolution and caveats

Repository planner (verified Git blob 0ff062f76f5534d9f18425f986ae3e750397f50c) ran strict exit 2. REDESIGN_OR_PILOT_ONLY. Group by four generator lineages; no confirmed independence or sealed roots. Graph vs node-only average effect clears inherited five-point scientific floor. Worst within-root seed disagreement is 93.75 pp (disjunction); four lineages cannot calibrate a 95/95 sham quantile. The normal planning estimate is not actionable. One primary planning comparison, inherited thresholds and 128 planned roots are retrospective; global removal comparison and audit are exploratory. All masks are verified, but the model experiment is not prospective confirmation. Local node labels, repair order and tie handling may create index nuisances; future controls should permute vertices, use isomorphism-aware splits and larger independent generator lineages. No evidence for increased Aleph training allocation, no upstream content ingestion.

## Replay

```sh
cd gyms/MIC06
python -m pytest -q test_mic06.py
OMP_NUM_THREADS=1 python run.py > results.json
python audit.py > audit_results.json
cd ../..
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC06/preflight_input.json --strict
```

Five targeted tests passed: counterexample, exhaustive support closure, independent brute-force oracle on 32 small roots, explicit disjunction, retrospective heuristic feasibility. Full repository CI not run. Source SHA-256 b9c34450fb1248b868f0161a4ecc574fb4ae216b6235531f0caa7901b0f76afc; audit 944f6e222503c1b9a7cc85be184ef4e203842741b057a03bb5fa1e76ddbc0480; tests f7e6e176bfbc40377fb868a03b51c8185dde609efab08fcde5e7af70684afaa4. Raw run SHA-256 e186420abf4ddfbf834fa95f6dd5fb1707bf7f9ff27ca9c7b3317469007a76c4 (time varies); audit cb9391026f92f10d853892e88d0e1e4e152f15d8648767d3730fe10448110cb2. Replay outputs locally, no model checkpoints or raw runs committed.

## Next gate

MIC-07 should compare the fixed graph priority against a parameter-matched state-updating ranker with current active-clause messages after each deletion. Include strong independent-set controls such as branch-and-bound with admissible bounds, exchange moves and a common wall-time or verified-work budget. Separate positive-support-only controls from signed exclusions; vary graph density, planted traps, structure, and disjunctive arity. Audit vertex permutations and isomorphism duplicates, collect independent generator-lineage sham calibration (at least 59 independent units for a distribution-free 95/95 maximum-based bound), then freeze an externally held confirmation manifest before scoring. Prioritize this development lead rather than another monotone closure ranker. The textual discovery-history question remains untested.

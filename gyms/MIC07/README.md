# MIC-07: dynamic graph priorities versus bounded exact search

Cloud CPU public development diagnostic following [MIC-06 #90](https://github.com/MoralityLabAI/EvalMath/pull/90). No source manuscripts ingested, no sealed confirmation or paid compute.

## Design and result

192 synthetic training roots at n=10, conflict and mixed generators, seeds 0..95. Exact feasible-submask dynamic program supplies optimal conflict-branch labels for 891 teacher decisions. Six 3297-parameter models, seeds 17/29/43, 40 Adam updates, recurrent message passing over current active conflict, support and reverse-support graphs. The reset-state model is evaluated both with frozen priorities from the first step and with refreshed priorities. The persistent model retains hidden state across deletions and is separately trained. Development: 128 new roots, n=10/12, seeds 2000..2015, four lineages. No independent lineage or isomorphism certification. All final masks checked by the exact integer verifier. The 32-closure-call ceiling includes initialization; equal caps do not imply equal actual work. Training cost excluded from inference timing.

| Policy | Mean % exact optimum |
|---|---:|
| Dynamic reset-state graph | 94.31 |
| Persistent graph state | 90.65 |
| Basic B&B, 32 closure calls | 90.27 |
| Frozen priorities, same reset-state checkpoint | 89.61 |
| Dynamic weighted degree | 83.29 |

Dynamic-vs-frozen paired effect +4.7081 pp, worst within-root seed variation 94.5946 pp. Resolution planner returns REDESIGN_OR_PILOT_ONLY: four unverified lineages, no sealed set, uncalibrated sham quantile, effect below inherited 5 pp scientific floor. Planning inputs retrospective; no confirmation claim. Persistent recurrence trails the reset arm.

## Stronger retrospective baseline

Clique partition of the active conflict graph gives an admissible upper bound: at most one vertex from each clique can be selected, and all weights are positive. Sum the maximum weight in each clique. Positive-support closure removes vertices that cannot occur in any feasible submask of the current state. Branch on both endpoints of an unresolved conflict, preserving every possible feasible submask in at least one child. Prune only if the upper bound cannot improve the feasible incumbent. These facts establish exactness when the queue is exhausted or its maximum bound is no greater than the incumbent. The independent exhaustive subset table verifies the claimed optima on the finite test domain.

Strong 32/64/128/256 closure-call caps recover 94.9468/99.1685/100/100% mean objective. Optimality certificates 98/124/128/128 of 128. In the final audit replay, mean wall times 0.206/0.228/0.226/0.222 ms per root, with 21.969/25.656/26.141/26.141 actual closure calls. Dynamic model mean 1.680 ms per root in the primary run. A retrospective per-root deadline derived from mean dynamic inference time certified all 128 optima; mean 0.231 ms, zero observed deadline overruns. Deadline checked between expansions, so soft rather than real-time hard guarantee. Timings are machine-specific, order-dependent and include Python overhead; no general runtime theorem. The stronger exact baseline defeats learned proposals in this domain. No need for further small-instance pure neural routing; consider larger sizes, learned B&B branch ordering and strong bounds under equal measured resource caps.

## Replay

```sh
cd gyms/MIC07
python -m pytest -q test_mic07.py
OMP_NUM_THREADS=1 python run.py > results.json
python audit.py > audit_results.json
cd ../..
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC07/preflight_input.json --strict
```

Cloud sandbox PyTorch 2.10 CPU; primary run 11.6s; three targeted tests passed (subset optimum and admissibility checked against brute-force submasks, B&B exactness and call caps, optimal trajectory labels). The audit filename's docstring mentions permutation-invariant oracle checks; no explicit vertex relabeling experiment was run. Full repository CI unverified. Planner source verified against repo Git blob 0ff062f76f5534d9f18425f986ae3e750397f50c and strict exit 2. Raw receipts reproducible; timings vary. Raw result SHA-256 1cc8f9da86ce979e590cc739261eef62a3237f061c70c230331e08838e1b8892; audit 2562068e30025b26ba3fefbb6d2968cb67395c86b8c73ce653ee36608a7ac26e. No raw runs or weights committed.

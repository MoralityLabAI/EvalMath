# MIC-11: residual variable elimination within bounded branch-and-bound

Public CPU follow-up to [MIC-10 #94](https://github.com/MoralityLabAI/EvalMath/pull/94), using pinned inherited modules from 82fce2dbe594b6f00c463bb0666707fd40d170e0. No manuscript bytes or paid compute.

## Mathematical contract

A search state (S,R) denotes the feasible subsets X with R subset X subset S. Fix coordinates in R to 1 and outside S to 0. Substitute these values into the original signed clauses, drop satisfied clauses, and reject a constant false clause. The resulting free problem is exactly equivalent, with additive objective offset sum of required weights. A forced antecedent in an alternative-support clause leaves an OR over all surviving alternatives; its factor scope must retain the entire clause. Max-sum elimination on the free factor graph preserves the residual optimum, so a verified exact residual solution can update the incumbent and discharge the state from the frontier. If its optimum is infeasible, it can be discarded. Search remains sound conditional on the inherited propagation, component reductions, frontier bookkeeping and admissible bounds.

For a fixed order, plan scopes before allocating tables. Charge the initial factor cells, both candidate-value factor reads and output factor writes at each elimination. If k factors meet at a variable with w remaining neighbors, the local cell charge is (2k+1)*2^w. Min-degree fill determines the order, not necessarily minimum treewidth. The producer uses a dominating negative penalty, safe in the bounded positive-integer domain; any infeasible assignment has negative score. The independent checker constructs sparse feasible factor tables from original predicates with the fixed values substituted, then max-sum replays the claimed order, objective, width, charged cells and witness. This verifies residual optimum certificates independently of dense producer arithmetic; it does not replay the full branch-and-bound proof frontier. Exhaustive tests cover infeasibility, including forced disjunctions.

## Design

72 fresh public graphs: four inherited families, 32/64/128 vertices, seeds 7000..7001, original/one-hub/three-hub conditions. Same deterministic initialization, include/exclude branching, propagation, component reduction and clique bounds as MIC-09. Baseline uses 512 child normalizations; additional baseline uses 1024. Elimination modes attempt at the root only, periodically (root, every eighth nonpruned pop or at most 24 free vertices), or at every nonpruned pop while budget remains. Each elimination arm caps width at 10, total factor cells at 250,000, degree-candidate scans at 250,000, attempts at 64 and child normalizations at 512. Failed planning consumes its scan/attempt budget; an over-budget table is not allocated. These are different work counters and not a hard wall-time or total arithmetic budget. Planning, projection, memory operations, indexing, and other search costs are not all included in the counters. All five policies are deterministic. No sealed confirmation or model training.

## Results

| Policy | Certified /72 | Mean ms | Mean normalizations | Mean factor cells | Mean degree scans |
|---|---:|---:|---:|---:|---:|
| MIC-09 baseline | 57 | 38.523 | 162.92 | 0 | 0 |
| Baseline 1024 | 60 | 63.141 | 261.53 | 0 | 0 |
| Root-only | 61 | 30.067 | 96.86 | 8995.6 | 3088.5 |
| Periodic | 62 | 46.486 | 82.36 | 35620.9 | 10118.5 |
| Always | 63 | 51.754 | 75.28 | 62721.4 | 26686.3 |

Original roots: 13/24, 15/24, 13/24, 14/24, 15/24 certificates in table order. On the 48 planted hub roots, all elimination modes certify all optima at the root; baseline certifies 44/48 and 1024 baseline 45/48. Always certifies 24/24 at n=32, 23/24 at n=64 and 16/24 at n=128. Pooled interval closes on 64/72 across all arms; the other eight remain interval-valued. Mean objective as fraction of pooled best feasible incumbent: 99.603%, 99.842%, 99.603%, 99.906%, 99.991%, respectively. Pooled incumbent is not an exact optimum on unresolved roots.

Residual search adds two certificates beyond root-only and reduces mean branch normalizations, but root-only remains fastest overall. Always is slower than root-only, faster than the doubled baseline on the aggregate, and slower than doubled baseline on original graphs (135.124 vs 123.099 ms). Timings are single-machine, order-dependent, exclude independent replay, and do not establish a general speedup. The measured mean always-vs-root objective benefit normalized by total root weight is +0.136674 pp, much smaller than the inherited 5 pp floor. Four generator lineage summaries, independence unverified, no sealed set. Deterministic same-policy sham zero is a placeholder, not independent sham calibration. The actual EvalMath planner (blob 0ff062f76f5534d9f18425f986ae3e750397f50c) returned REDESIGN_OR_PILOT_ONLY, strict exit 2. This is a retrospective structural diagnostic, not a prospective mechanistic claim.

## Verification

Four tests passed: 2916 exhaustive ternary conditioned states across four 6-vertex graphs; explicit forced disjunction and infeasible cases; 16 small exact full-search roots at several caps; budget boundaries. Public run completed in 16.609s on sandbox CPU. Independent replay in 10.101s accepted all 884 residual receipts, including 740 below the root; 231 always, 605 periodic, 48 root-only. All replayed values are feasible on this public suite; infeasible cases tested separately. Tampered objective rejected for every receipt. Inherited baseline matches value, upper bound, mask, normalization count and expansion count for all 72 roots. Global branch-and-bound frontier is not independently certified. No full repo CI or external confirmation.

## Reproduction

    cd gyms/MIC11
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python -m pytest -q test_mic11.py
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python mic11.py > results.json
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python replay.py
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC11/preflight_input.json --strict

SHA-256 mic11.py dde601708cc61309a5b75b6cc91c9ab51a863b8f48c3fc219c4f5d800123852a; tests 1f9cfcc1fc6d0c347f0a3d0708f3d0c26c6ba3a527d603eb181d18905eba621b; replay fd465683956cda0c88180942efe14b5fa4b994dd79f70c708b0d2a519224745b. Timing-dependent local results.json 17a578061334049664c06d44d53230bad323c464b9879f953f77c8a00fc604ca; audit_results.json 359043fc1661a4946f1468de05e13d0ef724241beacda9892b212eba2bc6927f. Raw files not committed. MathCan's separate MIC-06 closure audit now has a successful replacement [CI run](https://github.com/patrickdugan/MathCan/actions/runs/45582256494); this does not formalize MIC-11.

Next: estimate value of an elimination attempt from cheap structural features and a shared work allowance. Compare against root-only and periodic controls, use continuation regret including both runtime and residual bound reduction, and preserve explicit proof costs. Do not allocate training tokens on the public DLMST lineage. The original textual discovery-history hypothesis remains untested.

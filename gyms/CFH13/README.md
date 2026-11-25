# CFH-13: measured coefficient-computation costs

**Disposition:** retain invariant-specific acquisition and batching as development candidates. The calibrated CPU-cost frontier passes finite arithmetic replay, but the hard runtime-budget and end-to-end efficiency gates remain closed. No neural fits, paid compute, corpus admission, independent conjecture confirmation, or new Lean claim.

## Algorithms and measurement

Inherit the CFH-12 depth-two route grammar, 90 hypotheses per deck, and two observation queries. A targeted purchase computes only a requested subset of base polynomial coefficients. Independent/clique sets use a size-indexed include/exclude recurrence (complement adjacency for clique). Matchings use a size-indexed recurrence branching on whether a vertex is unmatched or paired with one neighbor. Domination enumerates just the requested subset sizes. Chromatic coefficients use partitions into independent color classes: if P_G(x)=sum_j b_j (x)_j, its x^k coefficient is sum_{j>=k} b_j s(j,k), where s are signed Stirling numbers of the first kind. The targeted partition recurrence prunes impossible numbers of classes and shares scalar DP across a batch of requested coefficients.

Compare against a strong full-vector implementation: vector include/exclude or matching recurrence, bitmask coverage DP for domination, and a vector independent-color-class partition recurrence. All per-call memoization is local; no persistent result cache is used by either algorithm. Each timed profile is keyed by labeled graph, invariant, method and requested index set. The profile itself is cached for pricing decisions. Initial calibration uses five samples of three invocations each, median per-call thread CPU time, rounded upward to integer microseconds (minimum one). Timing includes algorithm invocation and local graph setup, but excludes reference construction, receipt handling, and the cost of the decision process. Re-execute selected calls separately and record their single-call CPU time. Each selected acquisition is checked against the reference before the corresponding state restriction is replayed; state masks use the evaluator-owned coefficients only after purchase or symbolic availability. The offline timing calibration computes the candidate operations in advance or on demand during planning, so it is privileged and costly. The greedy baseline receives that same cost calibration, not a cheap deployable runtime estimator.

The initial test uses six new public decks, 18 cards, order 8–9, sparse/dense random graphs and geometric graphs. Exclude 195 prior graph-hash keys from CFH-07 through CFH-12. An exploratory recalibration uses four more decks, 12 additional cards, excluding all 213 prior keys including the first run. These are related graph-grammar examples, with conservative WL-hash exclusion, not independent conjecture families. All six policies, three budgets (100,400,1200 estimated microseconds) and three prices (0,0.0001,0.0004 utility per microsecond) are evaluated on all 90 routes per deck. Price and acquisition budgets use calibrated integer costs, not hard CPU limits.

Four exact offline planner menus: scalar (one call per required coefficient), batch (one targeted call per base group), vector (one whole-vector call per touched group, including future available coefficients), hybrid (choose among these three uniform methods and locally cheapest per-group mixture at each observation). The hybrid menu includes all actions of the three narrower menus; it is exact only within this restricted menu, not all possible cross-group mixtures or independent coefficient acquisition schedules. The privileged teacher reads full reply partitions. The free planner and price-adjusted greedy hybrid use only purchased or symbolic predictions when selecting queries; the latter ranks by conservative partition gain, or known singleton fraction at the final query, minus immediate calibrated price. Any new purchase is executed and checked against the independently enumerated reference. The free plan is fallback when no greedy score is positive. All arms may stop without claiming a singleton.

## Initial timing profiles

AMD EPYC 9V74, Python 3.13.5, single thread, NetworkX 3.6.1. Six-deck run:
- 702 base vectors and 46,710 derived residues checked against the CFH-12 environment and independent direct enumeration; 26,335 residues already available by sparse identities.
- 9,232 distinct timed profile entries, including 2,624 group-index single-versus-vector comparisons. 2,165 individual coefficient calls are strictly cheaper in calibrated integer microseconds. These group-index comparisons can reuse measurements for identical transformed graph requests.
- 3,955 actual selected function calls verified in replay, 1,683 chosen observation decisions, 29,160 hidden-route outcomes. Budget and exact planner utility checks pass. Separate per-deck/cap/price comparison confirms hybrid-menu utility dominance in all 54 groups.

| Invariant | Single comparisons | Single cheaper | Median single/vector | Median all missing batch/vector |
|---|---:|---:|---:|---:|
| Domination |729|729|.320|1.062|
| Matching |242|239|.531|.667|
| Independence |462|442|.625|1.261|
| Clique |462|427|.625|1.222|
| Chromatic |729|328|1.041|1.333|

Ratios use integer microsecond charges; all-missing ratios are one per base group, not repeated per index. A whole polynomial can be cheaper than repeated scalar calculations, especially for chromatic polynomials. Batching shares some work, but a targeted batch of all missing coefficients does not necessarily beat a vector recurrence. This is finite implementation-specific evidence, not an asymptotic complexity claim.

At zero price, discoveries out of 540 / mean calibrated microseconds / independently replayed mean acquisition microseconds:

| Cap | Vector | Scalar | Batch | Hybrid | Greedy hybrid |
|---:|---:|---:|---:|---:|---:|
|100|64 / 36.03 / 86.68|82 / 55.65 / 123.09|87 / 73.60 / 137.73|87 / 73.59 / 160.40|55 / 28.00 / 42.63|
|400|93 / 227.79 / 364.26|95 / 116.66 / 239.60|96 / 111.09 / 270.33|97 / 114.91 / 233.37|55 / 28.00 / 55.29|
|1200|104 / 551.25 / 674.25|101 / 252.55 / 381.75|103 / 381.01 / 633.41|105 / 357.34 / 569.99|55 / 28.00 / 173.78|

Free planning: 11 discoveries at zero acquisition cost. At cap 400, price .0004, hybrid net calibrated utility .14215 vs vector .10918 and greedy hybrid .09527. Results do not establish runtime superiority: 3,866 of 29,160 route outcomes exceed the calibrated cap on single-call replay (15.91% of the 24,300 paid outcomes). At zero price/cap 100 only 9 hybrid identifications meet the actual acquisition cap, versus 41 vector and 55 greedy hybrid. At cap 400 the actual-cap counts are 86 hybrid, 54 vector, 55 greedy. Acquisition-only replay time systematically exceeds initial calibration in this environment; timing variability, cache lifecycle and GC are possible factors, not isolated causal findings.

Offline timing calibration consumes 10.813 thread-CPU seconds, measured policy/planner calls 29.223 seconds (may include on-demand calibration), selected acquisition functions only .1197 seconds across all actual tree-node invocations. These totals are not independent additive categories and repeated policy branches have shared memoized planning. No end-to-end compute benefit can be asserted.

## Exploratory conservative recalibration

After observing overruns, use nine individual-call samples and charge 1.5 times their maximum, rounded up to microseconds. This is an empirical safety margin, not a worst-case time proof. Four fresh public decks, 360 routes per condition; same algorithms, caps, prices and policy menus. Comparing overrun rates across runs is confounded by deck differences as well as the calibration change; no causal claim.

| Cap, zero price | Vector hits | Hybrid hits | Vector hits within actual acquisition cap | Hybrid hits within actual acquisition cap |
|---:|---:|---:|---:|---:|
|100|37|46|37|43|
|400|44|62|44|62|
|1200|64|69|64|69|

Free: 7 hits; greedy hybrid: 35 hits at zero price. At 400 estimated microseconds, hybrid buys an average of 166.12 calibrated microseconds and replays at 226.65 actual acquisition microseconds, versus vector 113.67/105.09; hence the hit advantage also spends more average computation. At 1200, hybrid gets 69 versus 64 with mean calibrated acquisition 275.07 versus 701.00 and replay 259.90 versus 425.58 microseconds. Do not extrapolate this finite tradeoff to real tasks. 192/19,440 outcomes exceed the acquisition cap (1.19% of 16,200 paid outcomes). Every overrun occurs at the 100-us budget; none at the higher two caps on these decks. Calibration 3.736 seconds, planning 9.591 seconds (overlapping), selected acquisition .03195 seconds. 5,735 distinct timed profiles, 468 base vectors, 31,590 derived residues and 1,387 selected function calls checked; 1,122 observation decisions. All 36 per-deck/cap/price hybrid calibrated utility dominance checks pass.

Combined totals: 48,600 outcome records, 14,967 timed profile entries, 1,170 base-vector reference comparisons, 78,300 derived residue comparisons, 5,342 selected function calls. All finite replay checks passed; timing-budget promotion fails. The actual replay times are measured per tree node then shared across hidden hypotheses that visit that node; outcomes are not independent timing trials. The two runs are not a controlled matched-deck timing comparison. No statistical generalization claim.

## Reproduction

From gyms/CFH13, using earlier public CFH-07..12 gzip receipts (CFH-07 candidates, then CFH-08..12 main receipts):
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python frontier.py --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz /path/to/cfh11_receipt.json.gz /path/to/cfh12_receipt.json.gz --out receipt.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python conservative.py --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz /path/to/cfh11_receipt.json.gz /path/to/cfh12_receipt.json.gz receipt.json --decks 4 --out conservative.json
```
Requires earlier CFH04..12 Python modules, NetworkX and inherited dependencies. Both CPU processes exited zero. Timing-dependent values and selected policies may vary on replay. Source SHA-256:
- targeted.py ed6e1b99787ad950040e4c67953d2d6f14894f3cc289a14fe86ed5e5467eedad
- frontier.py f83a0111d8716fa4296c4a7f91f6714d3aad4426af465ea981b1877f6f58f575
- conservative.py c86b56d4880a566b3bd83b3e8b9e06d882aea316a785483591a37b31716191af
- receipt.json 1e60f136e5112a5d7cfd3db941dced2073d8fce1d1d49d41936abec714c74a44
- conservative.json baec2172868b510031c85be8c530658526ed44dd4715cbc39f105ef4f4f79c47
- gzip receipts a624d1bacc594c5c51c555b749d9a1709e5402fef67a9f4892ebe28290b71c2f and 0bffc26c20d67c2241be6c6b24846d95fa3df966c5135fa3b854bdcbdf6d865e.
Remote source blob identities verified against the tested local files. Generated receipts not committed. Full repository CI pending.

Next: prospectively compare deterministic recurrence-operation counts and an independently calibrated cost predictor on fresh decks, then implement a cheap online acquisition selector and actual deadline-aware fallback. Charge the decision procedure, not just the mathematical functions. No additional training or paid compute until a deployable interface shows a resource-adjusted gain.

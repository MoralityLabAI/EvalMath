# CFH-14: cost prediction and charged decision procedures

**Disposition:** retain dependency indexing and shortlisting for development. Hold learned cost-model promotion and hard runtime-budget claims. No independent conjecture confirmation or paid compute.

## Protocol

Use the CFH-12 depth-two canonical route grammar, 90 routes per deck, three graph cards, two observations maximum. Each observation is a coefficient modulo 2, 3 or 5. The mathematical interface exposes sparse identities and acquired coefficient values, with no exact unpaid values used in decisions. The evaluator independently constructs full reference tables and checks purchased values and partitions after each selected action. The graph metadata, symbolic expressions, and dependency masks are prepared before the warm budget begins; setup time is recorded separately.

Fit a log-linear ridge model separately for each of the five invariants and two acquisition methods (targeted batch and vector) on the 9,232 CFH-13 primary timing profiles, using the median of raw timing samples, ridge penalty .05 and a nonnegative 90th-percentile training residual margin. The basic model uses graph size/density/degree statistics and requested degree summary; the work-proxy model adds log counts of candidate subsets, possible scalar states, partition branches and weighted subset sizes. These are deterministic combinatorial proxies, not instrumented executed operation counts or certified runtime upper bounds. Model fitting is offline. No candidate execution timing on evaluation decks is used for selection or fitting. After the policy run, audit predicted prices against medians of three actual function calls for each available single coefficient and vector request. Prediction call time is measured separately. The audit may contain repeated transformed graph requests; the parent graph cards are excluded by WL hash, not a proof of complete transformed-graph independence.

Six new decks (18 graph cards of order 8–9) exclude 225 graph hash keys from CFH-07 through CFH-13 receipts. The same public graph grammar and related generator families remain in use. At 1, 4 and 16 ms warm thread-CPU budgets, compare free symbolic scan, full vector-cost scan, full hybrid-cost scan, and top-six shortlist with either cost model. All candidate query scores use available predictions only. Paid first queries rank by conservative partition gain; last-step paid candidates use a heuristic singleton score with an unknown-mass allowance, not a certified acquisition value. Estimated cost discounts the score. Choose targeted batch or vector per group in the hybrid menu. Cost predictions are cached only during a single selection. Acquire by invoking the actual CFH-13 algorithms and store the resulting coefficient values.

Budget accounting charges thread CPU time spent in selection (including prediction), acquisition calls, copying acquired values and reconstructing the observation partition. It excludes offline training, reference generation, evaluation assertions, simulator bookkeeping, and initial symbolic setup. A selected action must have its estimated cost plus 30 microseconds available after selection. Calls are atomic and may exceed estimates. Record actual overruns and count a singleton only if measured elapsed time is within the cap. This is deadline-aware scoring, not a preemptive hard deadline. All routes visiting a shared replay node inherit that node's timing; outcomes are correlated and are not independent timing trials. Cold-hit counts are post hoc warm replay plus recorded setup cost, not policies rerun under a cold deadline.

## Results

3,292 audited acquisition requests (all single coefficients and vectors): basic estimates cover 2,452 measured median times (74.5%), work-proxy estimates cover 2,223 (67.5%). Median absolute log error .22910 versus .16820; median estimated/measured ratio 1.1597 versus 1.0913; median prediction time 2.524 versus 4.9625 microseconds. The work proxies improve typical error but cost more to evaluate and underpredict more frequently. The in-sample residual margin is not a coverage guarantee. No calibration or training on evaluation timing.

Warm results: verified discoveries out of 540 / mean measured charged milliseconds / over-budget route outcomes.

| Cap (ms) | Free | Vector scan | Hybrid scan | Basic shortlist | Work-proxy shortlist |
|---:|---:|---:|---:|---:|---:|
|1|0 / 1.021 / 540|0 / 1.420 / 540|0 / 1.257 / 540|0 / 1.021 / 360|0 / 1.223 / 360|
|4|10 / 1.975 / 80|0 / 4.063 / 450|0 / 4.274 / 450|35 / 3.061 / 89|34 / 3.806 / 265|
|16|10 / 1.908 / 0|39 / 9.320 / 89|39 / 14.509 / 195|43 / 3.883 / 0|43 / 5.263 / 0|

At 16 ms, the basic shortlist matches work-proxy discoveries and has smaller measured overhead. At 4 ms it makes 35 vs 34 discoveries and has fewer overruns. Both full scans still spend substantial time evaluating candidate menus. The first run has 8,100 route outcome records, 205 selected decisions, 838 acquired function calls, 3,958 over-budget outcomes. Setup measured 12.97–15.36 ms on five decks and 188.61 ms on the first; no measured attribution for this first-deck outlier. Including the recorded cold setup in the 16-ms cap leaves 6 free and 6 basic/work-proxy shortlist discoveries; no cold discovery fits the smaller budgets. Cold overhead and the first setup outlier make a production latency claim inappropriate.

## Exploratory matched-deck dependency index

After the main run, test a semantics-preserving index on four further decks excluding 243 previous graph-hash keys (12 new parent cards). For each probe, group routes by equal missing-coefficient mask D. With active route mask S and purchase mask B, a group contributes D & ~B to requirements precisely when its route mask intersects S; if all D is purchased, evaluate the stored residue expressions of active members. The root uses the precomputed union of all nonempty dependencies. Symbolically known routes remain in disjoint cheap reply masks. This is equivalent to scanning routes individually because OR is associative and idempotent, and the same acquired coefficients are used in the residue expressions. Check the scan/index output equality on 300 random partial states per deck, 1,200/1,200 passed, with exact evaluator masks providing the purchased values in these audit states only.

Both versions use the same basic predictor and the same selector, alternating symbolic setup order and shuffling the policy/cap evaluation order. Budget-dependent choices may differ as the measured remaining time differs. Results (hits out of 360 / mean charged ms / overruns):

| Cap (ms) | Free scan | Free index | Shortlist scan | Shortlist index |
|---:|---:|---:|---:|---:|
|1|0 / 1.005 / 350|8 / .521 / 0|1 / .988 / 89|23 / .964 / 142|
|4|8 / 1.443 / 0|8 / .512 / 0|26 / 2.423 / 0|27 / 1.479 / 0|
|16|8 / 1.476 / 0|8 / .538 / 0|27 / 2.416 / 0|27 / 1.728 / 0|

At 4 ms, indexed shortlist spends 38.95% less mean charged time and yields one more discovery. At 16 ms it matches the original shortlist's discoveries. At 1 ms it increases within-budget discoveries but also raises overruns compared with shortlist scan: 142 vs 89. This fails a hard-deadline gate. Free index alone yields 8 discoveries within the 1-ms warm cap and no overruns in this finite sample. The follow-up is exploratory, not a registered confirmation. It has 4,320 outcomes, 151 selected decisions, 492 function calls and 581 over-budget outcomes. Scan setup has a 175.37-ms first-deck outlier; index setups are 12.31–14.64 ms, and the other scan setups 12.00–13.26 ms. At 16 ms adding recorded setup gives 20/24 cold shortlist discoveries for scan/index. Timing variation, differing setup and correlated paths preclude strong latency generalization.

## Verification and replay

Across both runs: 12,420 outcomes, 356 chosen decisions, 1,330 actual acquisition function calls checked, 1,170 reference base-vector and 76,950 residue comparisons in the inherited Deck oracle, 43,695 symbolically available residues, 1,200 partial-state index equivalence checks, and 3,292 timing audit requests (three actual executions per request, each checked against reference). All mathematical assertions passed, and no over-budget singleton is scored as a hit. The outcome count is not an independent-root sample size. No new Lean theorem, GPU spend, neural training, or corpus admission. Predictors are small classical regressions; their evidence is public development only. Repository-wide CI for this new commit has not yet been verified.

Run from gyms/CFH14 with Python, NumPy, NetworkX and earlier CFH dependencies; use the previous public receipts as manifest exclusions:
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python pilot.py --train /path/to/cfh13_receipt.json.gz --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz /path/to/cfh11_receipt.json.gz /path/to/cfh12_receipt.json.gz /path/to/cfh13_conservative.json.gz --out receipt.json --decks 6
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python indexed.py --train /path/to/cfh13_receipt.json.gz --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz /path/to/cfh11_receipt.json.gz /path/to/cfh12_receipt.json.gz /path/to/cfh13_conservative.json.gz receipt.json --out indexed.json --decks 4

Timing-dependent policies and scores may differ on replay. Both tested source blobs checked against remote:
- pilot.py SHA-256 aa82b4ff336467a6232d760e88fb9a121985e9bd4e1d1ee51f5cac0dff75b967
- indexed.py SHA-256 4659ab1620544c10ca03f59ec1a1df26d96505cbec294bfcc764488daec5c66f
- receipt.json SHA-256 49804fed35bdaac747e52628be907d1227ff4079583451ec85377a7cfecc2bc1
- indexed.json SHA-256 31fa031ddafcd8ab04578bab483ce524edf9d1eb5e1be078fda2f2e784770657
- gzip receipts SHA-256 2ba52df5c2c7b300e4c358088e1d59f1fabca999570ff0580c94e91b2ce72c82 and 146124083f5cf6cc261fc26b7f320b507b1a59fc2d8c55e36ffb6ef879a9100c.
Generated receipts not committed.

Next: use the indexed interface as the reference, instrument recurrence work and implement interruptible acquisitions with explicit deterministic fuel charges, including setup and selection. Compare on separately registered mathematical families before promoting a learned acquisition policy.

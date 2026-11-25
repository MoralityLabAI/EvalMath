# CFH-16: verified batch checkpoints under interruption

**Disposition:** pass finite checkpoint soundness and fixed-query recovery; fail to establish an end-to-end discovery improvement. Seven abstract Lean theorem candidates, kernel status pending. Public development only, no neural fit, paid compute, corpus admission or independent conjecture confirmation.

## Interface and threat boundary

Inherit CFH-15's factored scan, 90-route grammar, three graph cards and two observations. The policy computes coefficient batches using the resumable cooperative kernels. A trusted, separately constructed CFH-12 Deck reference verifies each proposed cell value, its group ownership and reference context; duplicate entries or conflicting values are rejected. The receipt is a candidate data structure, not an authenticated signature. The context digest binds this prototype's reference descriptors, but is not a security credential or cross-process canonical serialization. Merge always rechecks candidate entries against the trusted exact reference. Reference construction and evaluator assertions are outside the policy fuel ledger. The comparisons and bounded cache updates themselves are charged. This is a logical operation budget with bounded host-language work between charges, not a CPU instruction, wall-clock, memory or distributed durability guarantee. In particular, full independent reference generation is not cheap in general; the pilot does not claim end-to-end verification efficiency.

Each batch is staged, fully checked, and charged for all its cache writes before any are published. A failed validation or insufficient commit fuel does not mutate the batch cache. All previously committed entries remain unchanged. Only a completed exact restriction advances the observation count or changes the surviving hypotheses. In the checkpoint variant, an interrupted query retains the completed verified batches; no unchecked partial recurrence state or incomplete observation is exposed. In the atomic variant, interruption rolls the entire query's new batch cache back to its prior contents. Both retain all spent charges, and retry within the original global allowance. No persistence across process death, malicious evaluator defense or Python/Lean refinement is claimed.

## Fixed-query interruption audit

Four fresh public decks (12 graph cards of order 9–10, excluding 285 prior graph-hash keys from the CFH-07 through CFH-15 manifests). These are related public grammar cases, not independent conjectures. For each deck, choose the probe with largest missing coefficient mask using only symbolic information. An uninterrupted reference acquisition establishes the exact full-query cost (28,725 / 34,296 / 54,077 / 76,777 fuel). The diagnostic sweep uses total allowances of 100%, 125% and 150% of this measured cost, and 21 initial cutoffs (0, 1, and each twentieth of total from 1/20 to 19/20). Try once at the first cutoff, then retry the same probe under the remaining global allowance if it has not completed. No additional fuel or observations are granted. Comparing relative-to-cost schedules is an offline diagnostic, not a deployable selection rule; some initial attempts complete without interruption.

| Deck | Schedules per policy | Rollback/recompute completes | Checkpoint completes |
|---:|---:|---:|---:|
|0|63|24|43|
|1|63|25|43|
|2|63|24|41|
|3|63|24|41|
|Total|252|97|168|

All 504 schedule-policy combinations respect the same total caps, retain only exact values, and produce the identical reference partition whenever the query completes. 157 checkpoint schedules retain at least one verified cell after an unsuccessful first attempt. Relative gain 71/97 = 73.2%, with 168/252 vs 97/252 completion; the schedules are correlated repeated cases, not independent trials. Reject 16 corrupted receipts (wrong value, wrong group, duplicate cell, mismatched context per deck), with cache unchanged. This is a finite mutation set, not exhaustive security assurance.

## Cold end-to-end replay

Compare uninterrupted acquisition, rollback-and-retry, and checkpoint-and-retry on the same four decks at caps 30k, 40k, 50k, 60k, 90k. Use the same CFH-15B factored scan and score, charge validation and cache writes equally, and preserve the global cap. Retry arms give the first attempt half of the remaining post-selection fuel; after exhaustion, restore the original cap, retry the identical query with its remaining fuel, and consume no observation unless the restriction succeeds. Incomplete kernels are discarded in both retry arms. This is batch-level salvage, not whole-task resumability. No alternative query is selected after failure. All policies yield the same hits in this pilot.

| Fuel cap | Hits / 360 (each arm) | Mean spent fuel (each arm) | Checkpoint cells retained on interrupted tree nodes |
|---:|---:|---:|---:|
|30,000|0|30,000|37|
|40,000|8|39,458.18|35|
|50,000|31|37,616.35|0|
|60,000|31|37,616.35|0|
|90,000|31|37,616.35|0|

There are 5,400 route outcomes and 296 attempted tree-node transactions (65 interrupted, 231 committed); 72 retained coefficient cells at interrupted checkpoint nodes, counted as new cells relative to the attempt's input. Neither retry arm completes an additional observation after an unsuccessful first attempt at these caps. At the larger caps first attempts succeed, at the smaller caps the remaining fuel is insufficient. Thus the fixed-query recovery improvement does not establish a discovery gain. A better selector should schedule bounded batches and adapt to the value of partially acquired data rather than retrying the same costly observation blindly.

The separately computed reference checks 468 base vectors, 34,560 derived residues and 18,208 available symbolic residues. Every purchased value and committed partition is checked. Independent receipt audit confirms complete coverage, nonnegative integer phase ledger, fuel cap, query cap and singleton scoring for 60 groups / 5,400 records / 296 transactions. No overrun or false singleton in this finite replay. Reference generation excluded from resource comparisons; no independent-family inference, no neural causal claim.

## Lean scope

lean/FeedbackChannel/CFH16.lean has seven proof candidates: successful charge preserves valid ledger, over-cap charge rejects, sound cache merge, preservation of old exact entries, checkpoint preserves hypothesis set and observations while spending the charge, interruption preserves the entire committed cache and epistemic state, and authenticated observation retains hidden truth while respecting the observation cap. The external verifier's soundness and observation consistency are explicit hypotheses. The abstract charge admits zero, while the Python meter accepts only positive charges; the theorem covers that stronger mathematical domain, not a line-by-line implementation refinement. Budget caps remain fixed in the abstract model; temporary Python sublimits and retry restoration are outside the current Lean proof. All candidates are wired into the main build and axiom audit. Local Lean/Lake unavailable; kernel confirmation pending. Prior CFH-07 abstract retention theorem is reused. Do not mark this module kernel-verified until the CI result is checked.

## Replay

From gyms/CFH16 with CFH04–15 sources and inherited dependencies (Python 3.13.5, NetworkX, NumPy, SymPy, Torch inherited imports):
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python incremental.py --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz /path/to/cfh11_receipt.json.gz /path/to/cfh12_receipt.json.gz /path/to/cfh13_receipt.json.gz /path/to/cfh13_conservative.json.gz /path/to/cfh14_receipt.json.gz /path/to/cfh14_indexed.json.gz /path/to/cfh15_receipt.json.gz /path/to/cfh15_factored.json.gz --out receipt.json
python check_receipt.py receipt.json
```
Local tested file SHA-256:
- incremental.py: 22c4d627f2d4a58cea69caf43776f8d16b1fbbe32e821fba1aafc637f84d3215
- check_receipt.py: 3fbc8d5dae673828ee2ed42d0cda64fc2e8cbef53bf8ef3c2fa951011945480d
- CFH16.lean (uncompiled locally): 35dd1fc8d2243189023d8776159e3300ccb28627846fa54212dcc0d558646b87
- receipt.json: 9869e815c92e31063fb7175a8ce403f330070f4f6ebc4cd720d45f913a0faddb
- receipt.json.gz: 4535478f8941bc3fad5bc34b87c1a4e778b931f1ec892b344cfecff4a35147d0

No generated receipt committed. Next: compare budget-aware partial-query abandonment and targeted small-batch scheduling to full rollback and uninterrupted controls, then measure independent verification cost rather than relying on a precomputed trusted reference. Freeze new independent mathematical families before claiming general discovery improvement. No production admission or paid compute.

# VAD-06B/C: transfer validation and delayed discovery

2026-11-25. Exact finite synthetic Horn reference-cost experiments; no new Lean kernel run and no trained model. VAD-06A kernel verification remains the separately recorded result.

## VAD-06B: transfer validation

Eight regimes, 12 calibration and 24 test families each, disjoint seed namespaces. Every family has eight development goals, 32 pilot goals and 256 deployment goals. The private proof routes compete with two possible shared hubs. The mixture percentage is the probability a pilot/deployment root uses the original development hub. Immediate shift changes the hub before the pilot; late shift changes it after the pilot. Null has no shared hub routes. Dominated has a direct one-rule private proof from a fact, so the alternative hub can never shorten its two-reference proof, even if the hub is cached. Every goal is terminal and disjoint across phases.

All arms prove the full pilot without a cache. The baseline includes these proofs and the deployment proofs, including conjunction constructors for both batches. Select a candidate from the development ancestor cone using the VAD-06A support policy. Test its exact counterfactual proof savings on a pilot prefix, with a memoized recursive oracle. Charge its atom lookups, rule and argument scans, and each gate decision. Validation never selects a different candidate. Gate thresholds compare projected deployment savings with selection, construction, validation, and an optional margin. They are empirical thresholds, not statistical guarantees. Choose among 21 fixed/sequential gates by pooled calibration cost, write the freeze file, then evaluate fresh public-seeded test families. No independent third-party sealing. All arms use identical pilot workloads and reference costs. Full-graph solves are ex post scoring oracles, not observed deployment outcomes.

Calibration chose fixed_4_0; even on calibration it lost to support without validation (304449 versus 281029). On test, baseline 571019, support 564723 (1.0111x), fixed validation 607791 (0.9395x), support_exact 697414 (0.8188x). Validation spends 21743 additional units, rejects all 24 immediate-shift and all 24 dominated families, but accepts all 24 late-shift families with zero deployment savings. Its validation gate fails the cost comparison. Null families abstain in both support arms. The negative result matters: a veto can reduce mistaken construction without improving total cost.

## VAD-06C: delay discovery

Use the same generator in two additional disjoint seed namespaces, 96 calibration and 192 test families. Compare development-only support, four-pilot marginal/full gates, delayed online support and exact reranking on prefix lengths 2/4/8/16, and triggering a fixed candidate using a one-rule proof certificate. Marginal adoption tests prospective savings against prospective construction cost; previous discovery and validation are sunk, but still counted in total reported cost. The certificate replaces cached premises by unit cost in a rule and uses original shortest proofs for other premises. Its implied saving is a lower bound on exact cached saving by explicit feasible construction. The code independently checks this inequality on evaluated triggers.

The delayed selector uses only rules in the ancestor cone of the observed deployment prefix. That prefix is proved uncached, and only the remaining goals can benefit; there is no re-selection after the prefix. The test explicitly removes every rule outside the prefix cone and checks the selector is unchanged. Select the best alternative by pooled calibration cost before fresh test generation. Calibration picked online_support_4.

Test totals: baseline 567120; development-only support 562566; marginal pilot 589469; full pilot 606460; delayed support 421276 (1.3462x, 25.72% saving relative to direct, 25.11% relative to development-only support). Profitable in 141/192, including 24/24 immediate-shift and 24/24 late-shift. Online_support_4 chooses a cache in 168/192, including all 24 dominated families for which no savings occur; null abstains but incurs search work. Shared/75%/50%/25%/shifted/null/dominated/late-shift total costs: 41777/56786/66856/58451/42689/87286/24610/42821. This is an empirical advantage on the specified mixture, not a guarantee under arbitrary nonstationarity.

Both experiments charge proof references, candidate search, construction, and explicit extra validation. The full graph's premise index, generation and common base proof-search scans are outside the reported cost model, as are memory and physical compute. The online and offline policies have different observed information at commitment time, which is the intended intervention. A deployment prefix is used for adaptation, not an independently sealed test of zero-shot transfer; costs and missed savings of the prefix are included, and the remainder is untouched at commitment. The finite DAG has no backward edges or later rules concluding earlier targets. Do not extrapolate to general Lean premise search.

## Reproduce

    python scripts/verify_vad_transfer.py --out /tmp/vad06b
    python scripts/verify_vad_online.py --out /tmp/vad06c
    python -m pytest -q tests/test_vad_transfer_online.py

Three local tests pass; they replay 4608 and 3072 test records, confirm prefix-cone invariance and verify the dominated-route witness. The two runs report 1718892 and 1449578 cost/oracle or certificate comparisons across calibration and test, including repeated comparisons; these are not independent statistical observations. Source and receipt digests are in output/verified_abstraction/vad_06bc.json.

## Next gate

Before expensive search, identify goals whose uncached cost already equals the grammar's minimum (two references for nonfacts with a direct one-rule proof). No non-target cache can reduce this cost below two. Use a cheap dominance screen, but include late-unlock and mixed-easy/hard families where the initial prefix is misleading. Compare prefix lengths and an adaptive stop rule on fresh calibration/test namespaces. A cheap observation screen must be charged, and early abstention can miss future savings. Train a recurrent controller only after a robust symbolic baseline and independent kernel receipts for the actual new gym are in place.

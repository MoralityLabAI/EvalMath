# DCF16-EVAL: scoring compute-aware reasoning and algorithm selection

**Status:** implementation with exact rational scoring and a receipt over the real held-out split (200 records, 17 receipt checks, 6 hashed sources). Evidence level: *finite verified example*. No model is evaluated here; the three reference predictors are computed from record fields alone.

## Source data

The DCF-16 curriculum (`Compactification-Theory/research/dcf16_decision_curriculum`, read-only) holds parity queries on binary factor graphs. Each record carries a compute budget `2**budget_log2_ops`, the reward rule (+1 correct, -pen wrong, 0 abstain), every inference operator with its exact counted ops, stored posterior `p` and action, the exact reference posterior `verification.reference_p` (confirmed by independent exact paths), `truth_parity`, the oracle label `selected.operator`, and `hard_negative` flags. The held-out file is read in place, not copied. The receipt records its SHA-256 (`c128ee68...` for the gzip bytes, `ff709266...` uncompressed, equal to the generator's MANIFEST value). A 36-record stratified fixture of the held-out file (`fixtures/dcf16_heldout_sample.jsonl`, 9 families, 18 hard-negative records, bulky `problem`, `receipts` and `targets` fields removed) serves the tests.

The held-out split has nine families. Six (star, dense, hyper, ktree, xor_noiseless, weak_dense) never appear in train or validation; chain, grid and sparse appear at other sizes in the protocol's second held-out block, so "held-out family" means unseen only for those six.

## Scoring contract

A prediction row is `{id, algorithm, action in {1,0,-1}, p?, claimed_ops?}`. It must cover the records exactly (missing, unknown, duplicate ids, bad action, bad `p` all raise).

Expected utility of action a under reference posterior q and penalty pen is linear: `EU(1) = q - pen(1-q)`, `EU(0) = (1-q) - pen q`, `EU(-1) = 0`. Stored floats enter as `Fraction(float)`, which is exact, so every reported score is a rational; floats appear only as `approx` display values. Reported per slice (overall, hard-negative, non-hard-negative, per family):

- **eu**: mean verified expected utility; **realized**: mean utility against `truth_parity`; **regret**: mean of `oracle_utility(q) - EU`; **oracle_eu**: mean oracle utility.
- **coverage**: fraction acted; **selective_risk**: wrong fraction among acted (null when nothing acted).
- **algorithm_accuracy**: `algorithm == selected.operator` (the oracle label is `abstain` when abstaining is best).
- **budget_compliance**: the named operator's ops, read from the record's `operators`, is at most `2**budget_log2_ops`. `abstain` and `unary_evidence_only` cost 0; an algorithm the record does not list is non-compliant. `eu_budget_enforced` scores non-compliant rows as abstain. `claimed_ops` is compared with the record's ops and counted, never trusted.
- **calibration** over rows with `p`: Brier and 10-bin ECE against `truth_parity` (bins `floor(10p)`, last bin closed).
- **paired comparison**: per-record wins, losses, ties and mean difference for EU, realized utility and algorithm match, with an exact two-sided sign test on discordant records and per-family mean differences. Records of one family are structurally related, so the sign-test p is descriptive.

## Reference predictors (record fields only; no `reference_p`, no truth)

| predictor | EU | realized | coverage | selective risk | algorithm acc. |
|---|---|---|---|---|---|
| symbolic (cheapest exact within budget, else `mbe`, else abstain) | 0.35238 | 0.360 | 0.535 | 5/107 = 0.0467 | 0.505 |
| always-abstain | 0 | 0 | 0 | none | 0.510 |
| unary-evidence-only shortcut | 0.00967 | 0 | 0.075 | 1/5 = 0.200 | 0 (never names an operator) |

Mean oracle EU is 0.44546, so symbolic regret is 0.09307, abstain regret 0.44546, shortcut regret 0.43578. All three predictors are budget-compliant.

Hard-negative slice (117 records): symbolic EU 0.5415, coverage 0.846, selective risk 5/99; unary shortcut EU -0.0529, coverage 0.051, selective risk 1/2; always-abstain EU 0. Paired, symbolic against the shortcut on EU: 92 wins, 10 losses, 98 ties (mean difference 0.3427). Symbolic calibration: Brier 0.1166, ECE 0.0558 over 186 records with `p`; shortcut Brier 0.2292, ECE 0.0426.

Always-abstain matches the oracle label on 51% of records because 102 of 200 oracle labels are `abstain`; accuracy there rewards abstaining and says nothing about utility, so read it next to EU.

## Receipt

`scripts/verify_evaluation_dcf16_decision.py` writes `output/evaluation_dcf16_decision/dcf16_eval_v0_1.json`. Its checks include: file digest equals the generator manifest; every stored operator regret equals `oracle - EU(action)` (tolerance 1e-9 against the stored floats); stored operator actions equal the Bayes action on `p`; the stored oracle regret is reproduced; oracle selections score algorithm accuracy 1; exact zero for always-abstain; symbolic budget compliance 1; regret nonnegative for all predictors; symbolic beats both baselines on EU. `scripts/score_dcf16_decision.py HELDOUT PREDS [--against OTHER]` scores any predictions file.

## Scope

The eval measures decision quality under the stored reference posterior and the sampled truth parity. For misspecified records the reference is the generating model; the oracle label and `selected.operator` are the generator's, with a 0.05 ops-cost penalty, so algorithm accuracy measures agreement with that label, not the only defensible choice. The 200 records come from 9 families by fixed sizes and seeds; they are not an independent sample from a population.

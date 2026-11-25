# SRG-17B: Controlled planning advantage and SWMD runtime replay

Complementary to the independently implemented SRG-17 high-K, epistemic and order-witness gym. This is an exploratory public diagnostic, not a preregistered model evaluation. Original SWMD world unchanged.

Each matched tape has four independent contracts, with 1, 2 or 3 active. H=1,2,4,8 turns; K=1,2,4,8 parity bits; q=0.6,0.8,1.0. For H>1 use gap g=0,10,25,50 points. H=1 has zero planning gap. Ordinary routing pays 90 points for correct parity. The audited signal is exact and audited payout A=90q±4 (positive sign excluded at q=1). M=max(90q,A). Bank pays M-g immediately on profitable/tie instances, M+4 on trap instances. Deferred routes pay zero initially and open final settlement. All payouts are bounded by 100. The positive root Bellman advantage over immediate greedy equals g exactly, checked by independently enumerating parity and error words. Trap roots have zero gap and require banking.

Score realized points / (100 × active contracts), raw and informative accuracy, root Q assuming optimal continuation, and trap regret. Positive-gap recovery = sum(chosen root Q - greedy Q)/sum(oracle Q - greedy Q) on positive-gap roots. This is optimistic root recovery, not realized normalized utility. Always-route and always-audit controls use oracle settlement: they isolate root heuristics. Informative row density differs from active-contract density. H controls delay, with inert padding, not causal depth; K controls parity width, not epistemic order. Contracts are independent; the root admits a closed-form solution. A genuine coupled multistep benchmark is needed for claims of planning depth. There are only 16 matched tapes; no independent statistical inference across cells/rows.

## Results

468 cells, 29952 contracts, 232704 policy rows. 13824 root-value checks, 13824 gap checks, 29888 matched-tape checks, 29952 oracle completions. 936 generated SWMD-SRG/2 fixtures, 15048 one-step transitions checked against the reference, including hidden-score and public-signal checks.

| Control | Raw accuracy | Informative accuracy | Realized utility | Positive-gap recovery | Trap regret (points) |
|---|---:|---:|---:|---:|---:|
| oracle | 100.00% | 100.00% | 75.33% | 100.00% | 0 |
| greedy | 98.00% | 89.10% | 66.85% | 0.00% | 0 |
| first | 90.56% | 48.48% | 53.25% | 64.95% | 38732 |
| always_route | 95.69% | 76.46% | 68.42% | 94.53% | 40512 |
| always_audit | 94.68% | 70.96% | 70.83% | 91.35% | 55328 |
| bank | 98.00% | 89.10% | 66.84% | 0.00% | 0 |

Oracle realized 75.33% vs 66.85% greedy, an 8.48 pp separation. Positive-gap-only recovery of always-route is 94.53%, but its trap regret is 40,512 points and global root regret 50,112. The oracle's gap is meaningful even when raw accuracy is nearly saturated.

Core and pinned SRG/1–2 runtime tests ran in isolated ECMAScript. Standalone Node CLI, actual model inference and private evaluation remain outstanding. Public IDs and order can reveal grouping; for private evaluation randomize order and omit IDs from prompts, keep source fixtures and seeds verifier-only. No production editor edits.

## Reproduction

```sh
node integrations/sweepweave-ts/srg17b/cli.mjs verify
node integrations/sweepweave-ts/srg17b/cli.mjs stage /tmp/srg17b-pilot 0x53521701 1
node integrations/sweepweave-ts/srg17b/cli.mjs score /tmp/srg17b-pilot /tmp/submissions.jsonl
```

The stage command writes model_input/planning.jsonl and a private hash manifest. Score accepts JSONL id/action pairs. SRG-08 runner compatibility is unverified.

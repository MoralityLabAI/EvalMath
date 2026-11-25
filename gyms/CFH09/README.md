# CFH-09: exact finite-horizon action-value distillation

**Disposition:** reject promotion of direct value regression; retain tie-aware and relative ranking as public development candidates. No independent conjecture test, causal mechanism claim, production training admission, or paid compute.

## Acquisition and observation interface

The CFH-05 canonical grammar at depths 1 and 2 has 28 and 90 routes, respectively. Each deck has three simple labeled graphs of order 7–8. Each observation requests a coefficient modulo 2, 3 or 5, with a two-query horizon. An action bundles acquisition of every as-yet-unavailable base polynomial needed to predict the selected observation for **all** surviving hypotheses with that observation itself. Sparse CFH-06 coefficient identities can eliminate acquisitions. A purchased base group supplies all derived predictions on its card; costs count distinct (card, graph transformation, invariant) groups acquired during the episode. Caps 0, 4, 12. Bundled actions restrict the policy class relative to CFH-06; these scores are not directly comparable with the four-query CFH-08 experiment. A base purchase may cost very different actual CPU time for different invariants.

For surviving set S, acquired group mask B, remaining budget c and horizon h, let N(S,a) be the groups required by action a and not yet acquired. The cost is |N(S,a)|. Querying after purchase supplies an exact partition (S_v) of S. Let V(S,B,c,h) count the maximum hidden routes that an optimal decision tree can uniquely identify. Terminal singleton value is 1; terminal nonsingleton value is 0. For h>0 and |S|>1:
```
Q(S,B,c,h,a) = sum_v V(S_v,B union N(S,a),c-|N(S,a)|,h-1)
V(S,B,c,h) = max(0,max_{affordable a} Q(S,B,c,h,a)).
```
All counts are exact integers in the DP. A fully known nonsplitting zero-cost query is dominated by skipping it. A nonsplitting query that buys new groups is retained because it may help a later query. The exact teacher has privileged offline knowledge of all residue partitions, including unpaid predictions; it is the optimal bundled-action ceiling, not an online equal-resource competitor. The learned and heuristic online policies see only sparse predictions and coefficients explicitly acquired in their current episode. No hidden-route ID, exact unpaid partition, or teacher action value is an input. Target generation and evaluator scoring use independent enumerations in CFH-07. Online acquisition calls the actual base coefficient enumerator with its upstream cache bypassed, and compares each acquired vector to direct enumeration. Derived residues are calculated from the acquired coefficients. The shared experiment cache retains purchased vectors across exhaustive hidden-route replays; access is gated by the current episode's purchase mask, and each episode is charged its own acquisitions. Report actual distinct computations separately. This is not a wall-clock benchmark or end-to-end cost equality claim.

## Data and fits

Ten new training decks from random, Prufer tree and random bipartite generators, at depths 1 and 2. Eight new generator-shift evaluation decks from Watts–Strogatz, preferential attachment and geometric generators, depth 2. All 54 graph cards have distinct (order, four-round WL hash) keys, also excluding prior CFH-07 candidate deck and CFH-08 evaluation graph keys. Other earlier CFH graph sets are not exhaustively excluded. All cases are related public graph-grammar variations, with no independent conjecture roots. The original training labels include each cap's root and up to 32 sampled nonsingleton child states from affordable root actions; discard no-action and all-zero-value states. 1,218 retained examples, 219,276 DP state-action scans to generate labels.

Matched width-32 two-layer tanh models, scalar action logit, 26 features of available partition counts, unknown mass, conservative gain, version-set size, horizon, budget, cost, graph/probe metadata and invariant masses. Each has 1,953 parameters. Fixed seeds 11,29,47, matched initialization/minibatch sampling, 240 AdamW updates, batch 48, lr .003, weight decay .001. Initial arms: one-hot imitation of an exact optimal action (deterministic heuristic tie-break), cross entropy against uniform distribution on all exact optimal ties, and MSE on sigmoid action scores against normalized exact Q/|S|. Exploratory extra arm after reviewing initial results: relative-rank soft targets proportional to exp((Q/max Q)/0.2), cross entropy over eligible actions. Original three arms rerun unchanged; their hit counts and logical acquisition costs reproduce. No checkpoint selection or parameter tuning on evaluation data; the extra objective was selected after seeing initial public results. All neural policies choose argmax scalar score and retain the exact verifier. Greedy ranks by conservative expected elimination before the last step and by guaranteed singleton count at the last step. Cost-greedy divides the primary heuristic score by 1+required acquisitions. The latter is intentionally simple, not an optimal cost baseline.

## Results

Mean correct singleton discoveries out of 720 per cap, neural means across 3 seeds. Mean logical base acquisitions per episode in parentheses.

| Policy | cap 0 | cap 4 | cap 12 |
|---|---:|---:|---:|
| Exact offline planner | 14 (0) | 80 (3.2181) | 117 (9.5292) |
| Greedy | 14 (0) | 58 (2.8833) | 64 (6.7222) |
| Cost greedy | 14 (0) | 14 (1.7778) | 17 (5.3333) |
| Imitation | 14 (0) | 57.333 (2.7838) | 62.667 (7.8171) |
| Optimal-action ties | 13.667 (0) | 57.667 (3.3884) | 68 (9.8588) |
| Value regression | 13.333 (0) | 9.667 (2.2222) | 9.667 (2.2222) |
| Relative rank (exploratory) | 14 (0) | 58.333 (3.4727) | 70.333 (10.3375) |

Per-seed hits at cap 4: imitation 54,61,57; ties 56,58,59; value 9,12,8; relative rank 59,58,58. At cap 12: imitation 58,70,60; ties 71,70,63; value 9,12,8; relative rank 74,69,68. Direct regression fails across both nonzero caps and all matched seeds. Relative ranking improves high-cap hits over greedy, but spends 53.8% more acquisitions on average. It still reaches only 60.1% of privileged exact hits at cap 12. No cost-efficient superiority established. Future work: compare explicit acquisition-cost penalties, budget-matched tradeoff frontiers and exact lookahead on free symbolic observations. Do not infer a cause for MSE collapse from these results alone.

Final receipt: 32,400 hidden-route outcome records (360 deck/cap/arm/seed combinations), 1,400 tree decisions, 55,080 sparse residue tests on evaluation decks, 340 distinct acquired base coefficient vectors recomputed and checked against independent direct enumeration. At every selected action, acquired/symbolic predictions exactly match the evaluator's complete partition of the remaining set; all episodes respect both budgets. No false singleton promotions. Timing fields only describe enumerator misses on this shared-cache run, excluding offline audit, setup, planning, and replay.

## Bellman regret identity and verification

Let a policy decision tree visit each reachable nonsingleton state once per branch, and define local regret R(s,a)=V(s)-Q(s,a) in integer hidden-route counts. By substituting the Bellman recursion through the finite tree, the sum of regrets over its internal nodes equals root optimum minus the policy's actual singleton count. In probability units the per-node normalized regret is weighted by |S|/|S_root|. This identity is valid for this fully partitioning interface and makes it possible to locate the exact lost discovery mass by step. The receipt stores normalized values as float32; the audit reconstructs their integer counts to tolerance 1e-5 and compares integer sums. **360/360** groups passed the telescoping check, with the exact planner's replay matching DP root values. This is a finite check plus the stated algebraic telescoping argument, not a Lean formalization.

## Replay and custody

From gyms/CFH09:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python value_pilot.py --prior-candidates /path/to/cfh07_candidates.json.gz --prior-pilot /path/to/cfh08_receipt.json.gz --out receipt.json
python check_regret.py receipt.json
```
Requires prior CFH-04..07 sources and Python/NumPy/NetworkX/Torch CPU. Source SHA-256 0552ff1c6df08ea3de4b956cd06348deefcdceaeafd1a5f37fa6f1b390416bcc; final uncompressed receipt SHA-256 76717b286a9839f06fcb03b57e208cf7dfa6cbe6bea94ef1e844dbc54c1bd1af; gzip SHA-256 fb18b407020d8da7df0a2d5318e5cabc9944b331420ed054c174ac5d980c7c69. Initial source SHA-256 9d0ea52da7add0bebac112f7210ac596bc09183377843fb42c6d8ba0153b8a20; initial receipt SHA-256 2e5c9107c8af5d6582a7ed6682bf3b4a61a3e3533fad8709e00a697625cbd232. Timing fields vary on replay. The source blob matches locally tested bytes. No weights, generated data, training admission, quota changes, or paid compute. No sealed confirmation or calibrated mechanism intervention; the pilot is descriptive and not a causal study. Current repository-wide CI not yet verified.

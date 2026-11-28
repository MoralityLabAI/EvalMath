# CFH-05: compositional route identification and amortized planning

**Status:** finite public-development CPU pilot. Exact combinatorial observations and replay; ridge-regression ranking only, no neural mechanism, independent-conjecture generalization, or sealed confirmation. The horizon-conditioned redesign was exploratory after the first evaluation.

## Grammar and observation contract

A route is (l,r,c,i,d,s): delete l smallest and r largest labels, optionally complement (c in {0,1}), choose one of the five CFH-04 invariants i, differentiate d times and substitute x+s. Nonnegative l,r,d,s and l+r+c+d+s <= grammar depth D. Normalize deletion order, complement parity and commutation with vertex deletion, and derivative/translation commutation. Complement interchanges clique and independence, so remove those two complemented representatives. The resulting canonical form count is 5*binom(D+4,4)+3*binom(D+3,4), interpreting the second term as zero at D=0. Sizes: 5, 28, 90, 220 for D=0..3. The 220 forms have distinct combined exact signatures on the 36 evaluation graph-card occurrences, witnessing pairwise distinguishability on the graph domain, not necessarily on each deck.

A probe requests a polynomial coefficient modulo 2, 3 or 5 on one of three given graphs of order 7 or 8. All policies get the same exact hypothesis tables, full-interface singleton mask, and induced query partitions. This shared setup costs 3*N logical route predictions per deck at depth with N routes; actual work benefits from cache reuse. The model does not infer an unknown grammar or prove new theorems. Prediction cost, exact observation cost and offline planning cost are different resources.

For version set S, a full exact planner maximizes the number of hidden routes uniquely identified with at most b probes, using the CFH-04 recurrence. The full-interface singleton mask M gives upper bound U(S,b)=min(|S intersect M|,5^b) on every reachable state (observationally indistinguishable classes cannot be split). For candidate partition A, sum of U(child,b-1) is an admissible bound. Exact planner deduplicates induced partitions, memoizes states and prunes actions unable to exceed the incumbent. It orders actions by entropy for pruning. Greedy and width-four planners restrict candidate expansions at nonfinal levels, but use exact last-step decisions and identical admissible pruning. Replaying every hidden route against each selected tree confirms singleton hit counts, retention of the true route, and budget compliance.

## Corpus and learned policies

Eight training decks, three cards each, using Erdos-Renyi, Prufer tree and complete bipartite generators; twelve evaluation decks: eight shift decks (Watts-Strogatz, preferential attachment, geometric), four structured decks (path, cycle, complete). Fixed seeds in code. Generator groups differ; graphs were not deduplicated across generator groups, and relabeling can reproduce equivalent graphs. Decks, routes, budgets and planners are dependent public-development variations of the same finite grammar. No independent root-level inference.

All fits use 8 partition-size features including normalized singleton count, entropy, largest cell fraction, pair-collision probability, number of reply cells, version-set size and doubleton mass. Ridge penalty 0.01. Initial learned beam fits 542 exact two-query root action values at depth 2; it applies the same weights for both horizons. Initial evaluation revealed weaker three-query results. Exploratory horizon redesign uses training decks only, with separate horizon-2 and horizon-3 weights, grammar depths 1/2, and 12 sampled non-singleton root children per training deck/depth for two-query supervision. Training labels: 9,471 (horizon 2), 1,078 (horizon 3). No fitting at depth 3 or on evaluation labels. The redesign was evaluated on the same public decks; it is not confirmatory. Both learned planners have beam width 4, matching entropy beam. The greedy control uses width 1.

## Results

Counts across 12 decks, followed by state-action partition evaluations in parentheses. The exact comparison is available for every depth/budget.

| D | Queries | Greedy | Entropy beam | Initial learned | Horizon-aware | Exact |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 189 (4,776) | 202 (16,258) | 202 (15,784) | 202 (16,258) | 204 (37,629) |
| 1 | 3 | 328 (10,001) | 328 (13,706) | 324 (26,640) | 328 (17,494) | 330 (26,966) |
| 2 | 2 | 155 (4,854) | 175 (16,989) | 186 (16,989) | 190 (16,989) | 193 (83,515) |
| 2 | 3 | 837 (23,993) | 882 (185,745) | 801 (158,428) | 884 (190,660) | 885 (716,251) |
| 3 | 2 | 124 (4,872) | 139 (17,052) | 158 (17,052) | 165 (13,095) | 179 (117,092) |
| 3 | 3 | 914 (25,098) | 1008 (264,099) | 961 (222,372) | 1025 (283,940) | 1043 (1,833,051) |

At D=3 and b=2, original learned beam improves over entropy by 19 hits at identical partition-evaluation work. Horizon-aware improves by 26 hits while using 23.2% fewer evaluations than entropy. At D=3 and b=3, horizon-aware adds 17 hits over entropy at 7.5% more partition evaluations (unequal actual costs); it reaches 98.27% of exact hits with 15.49% of exact partition evaluations. Shift subgroup: 706 horizon / 695 entropy / 720 exact; structured subgroup: 319 / 313 / 323. This is an approximate planning quality/cost tradeoff, not an exact-planner speedup with preserved optimality. Exact planner gives 1043/2640 hits; the full residue interface's ceiling is 2518/2640 (2520/2640 with complete vectors). The low absolute success at two queries is constrained by at most 25 reply leaves per deck.

Training cost: initial fit uses 119,596 state-action partition evaluations for label generation; exploratory horizon fit uses 4,000,931. At the observed average D=3,b=3 work savings per deck relative to exact, horizon label-generation work alone would amortize after roughly 31 comparable decks, conditional on accepting the loss of exact-optimal hits and stable work rates. Excludes feature computation, table setup, regression, pruning, audit and replay costs. State-action evaluations count scans of unique global query partitions at previously unseen states; also report primitive mask intersections and expansions. This is not a wall-clock or end-to-end cost claim. Time fields are descriptive only. The exact planner took only a few seconds over this development suite; no GPU spend is warranted.

## Audit and limitations

1,980/1,980 composed coefficient vectors matched an independent route on nine graph cards (131 distinct transformed base graphs): direct subset/edge-subset/color-partition enumeration from CFH-04, NetworkX graph operations and SymPy differentiation/translation. 360 planner aggregates; 40,560 exhaustive hidden-route replays, all consistent with planned hits and residue ceilings. Every approximate result is <= the corresponding exact result. The audit covers the sampled compositions, not a general verification of every graph polynomial on arbitrary graphs. The learner has no hidden state or recurrent neural network. This is algorithmic amortization of query ranking, with non-identifiability explicitly represented by unresolved version sets. Full-interface singleton computation is shared privileged setup; in expensive real discovery this cost must be charged. No mechanistic-power preflight was fabricated: the pilot has no independent conjecture families, no sealed confirmation or calibrated intervention sham.

Next experiment: prospectively freeze independent construction families and a separate cost budget for *obtaining* hypothesis predictions, not just scanning already-computed partitions. Compare exact lazy partitions, entropy beam, horizon ranker and equal-cost nonlearned pruning. For DataGoblin, preserve route canonicalization, observation, version-set restriction, available horizon, exact target action value and abstention as distinct supervision fields; no corpus admission or token quota change.

## Replay

From gyms/CFH05:
```sh
OPENBLAS_NUM_THREADS=1 python compositional.py > receipt.json
```
Requires Python 3.10+, NumPy, NetworkX and SymPy; imports CFH-04. Generated receipt is not committed. Timing fields vary. Local final-run receipt SHA-256: 3790f9ae9cdd4f0a9beacf6f1a56e79f09781d03ea4276ece7c6791545e544fc. Initial-run receipt SHA-256: 37f9503455c1b51eccb48a61cfa685377f7a6045fbe50dc836b5e887d30c11b5. Source SHA-256: ffbbe11f6c0e3b3da1720967e0824032eb138615d95912a861d2dfae8aacbd2f. CFH-04 dependency SHA-256: 3af465d20b8d315f6cade3c86027604ccb568ce600b996f78597dad24c88ffe2. GitHub source blob verified against local tested source. Repository-wide CI and Lean build not run; public development only.

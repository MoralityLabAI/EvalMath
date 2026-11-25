# SRG-24: Robust multi-reasoner constrained authoring

[Registered protocol](../integrations/sweepweave-ts/srg24/PROTOCOL.md), commit fca7e7e8ec6ce7938bdc3412dd3eb7c13a1d4568. Source 282a9bc90c70cfd543383b805a131231d76c6f28. Complete candidate and selection manifests frozen at da3f55c755bcb1052e453e798ed342d4945dd97d before any reserved-policy evaluation. Preserve SRG-23 rejection and concurrent SRG-AC work. Public synthetic worlds only.

For each fresh SRG-18 base, form the source plus 32 deterministic two- or four-swap reward permutations, deduplicate exact reward tables. Preserve per-stage reward multisets, phase maps, target, energy, guards and all other world fields. Same SRG-23 optimum, informative-row and causal-sensitivity constraints. Use an independent integer Bellman guard; causal sensitivity means stage identity replacement changes root Q, not proof of minimal computational depth.

Training uses actual composed normalized regrets of d1, d2 and terminal-only controls, so this is deliberate optimization against those reasoners with oracle labels. J=min of those three regrets. Compare J, mean training regret, d1-only, and a fixed random ordering. Select low/median/high on one common feasible pool; robust high is Pareto-optimal for maximizing J, preserving optimum (-absolute deviation), maximizing sensitive stage count and informative density. Dominance checked for every feasible candidate. High tie ordering favors smaller utility change, greater sensitivity and density; final ascending proposal-index tie-break is deterministic. Eligible bases have at least three feasible variants and robust gap >=.025. Ineligible bases remain in the audit. All reserved outcomes are evaluated only after the two freeze files are committed.

Uniform-suffix policy chooses an action by immediate reward plus future value under uniformly random legal actions, replanning at each state. Beam policy keeps the two highest earned-reward partial paths at each depth, stable menu expansion ties, no state dedup or terminal heuristic, and executes the best terminal path. These are reserved algorithmic families, not actual independently trained models. d4 is also reserved for diagnostic scoring. Regret is (exact attainable utility - realized points)/(3H+B). The selected held-out minimum summarizes simultaneous difficulty of both reserved policies. All candidate outcomes, including infeasible and nonselected, are published.

## Registered gate

| Cohort | Eligible coverage | Conditions | Result |
|---|---:|---|---|
| 1 | 84.38% | coverage PASS; uniform_gap PASS; beam_gap PASS; uniform_positive PASS; beam_positive PASS; over_d1 PASS | PASS |
| 2 | 75.00% | coverage PASS; uniform_gap PASS; beam_gap PASS; uniform_positive PASS; beam_positive PASS; over_d1 PASS | PASS |

Joint gate: **PASS**. Each cohort requires >=60% coverage; both held-out policies mean high-low >=.01 and strictly positive fraction >=50%; robust average held-out mean separation exceeds d1-only by >=.005. Comparisons use the same eligible bases. Weak monotonicity includes ties. Failure is retained without promotion.

## Tier audit

| Cohort | Arm | Policy | Low regret | Median regret | High regret | High-low | Strict positive | Weak monotone |
|---|---|---|---|---|---|---|---|---|
| 1 | robust | d1 | 0.18125 | 0.19208 | 0.21854 | 0.03729 | 68.52% | 62.04% |
| 1 | robust | d2 | 0.07299 | 0.13174 | 0.21101 | 0.13801 | 90.74% | 79.63% |
| 1 | robust | terminal | 0.16746 | 0.17955 | 0.20126 | 0.03380 | 66.67% | 63.89% |
| 1 | robust | uniform | 0.05126 | 0.07765 | 0.09136 | 0.04010 | 62.04% | 64.81% |
| 1 | robust | beam | 0.08603 | 0.13035 | 0.17711 | 0.09108 | 76.85% | 71.30% |
| 1 | robust | d4 | 0.03663 | 0.04889 | 0.07803 | 0.04141 | 61.11% | 68.52% |
| 1 | robust | held_min | 0.03302 | 0.06322 | 0.08223 | 0.04920 | 65.74% | 76.85% |
| 1 | robust | train_min | 0.02533 | 0.08349 | 0.15363 | 0.12829 | 100.00% | 100.00% |
| 1 | mean | d1 | 0.15576 | 0.19172 | 0.24059 | 0.08483 | 86.11% | 80.56% |
| 1 | mean | d2 | 0.05440 | 0.13452 | 0.24012 | 0.18573 | 96.30% | 95.37% |
| 1 | mean | terminal | 0.15298 | 0.18362 | 0.20648 | 0.05350 | 86.11% | 83.33% |
| 1 | mean | uniform | 0.04671 | 0.07672 | 0.09889 | 0.05219 | 68.52% | 67.59% |
| 1 | mean | beam | 0.08737 | 0.12474 | 0.20355 | 0.11618 | 84.26% | 83.33% |
| 1 | mean | d4 | 0.03346 | 0.04663 | 0.07076 | 0.03729 | 57.41% | 67.59% |
| 1 | mean | held_min | 0.03369 | 0.06016 | 0.09313 | 0.05944 | 71.30% | 80.56% |
| 1 | mean | train_min | 0.03645 | 0.08120 | 0.13848 | 0.10203 | 87.96% | 92.59% |
| 1 | d1 | d1 | 0.13861 | 0.19342 | 0.26844 | 0.12984 | 100.00% | 100.00% |
| 1 | d1 | d2 | 0.11152 | 0.13395 | 0.13439 | 0.02287 | 49.07% | 58.33% |
| 1 | d1 | terminal | 0.17101 | 0.18315 | 0.19897 | 0.02796 | 56.48% | 62.96% |
| 1 | d1 | uniform | 0.06219 | 0.07912 | 0.08246 | 0.02027 | 48.15% | 52.78% |
| 1 | d1 | beam | 0.10761 | 0.12235 | 0.16049 | 0.05288 | 63.89% | 67.59% |
| 1 | d1 | d4 | 0.03760 | 0.05388 | 0.06075 | 0.02315 | 52.78% | 62.04% |
| 1 | d1 | held_min | 0.05036 | 0.06535 | 0.06973 | 0.01937 | 47.22% | 61.11% |
| 1 | d1 | train_min | 0.06415 | 0.08719 | 0.08336 | 0.01921 | 51.85% | 61.11% |
| 1 | random | d1 | 0.20141 | 0.19532 | 0.19221 | -0.00921 | 18.52% | 37.04% |
| 1 | random | d2 | 0.12989 | 0.14128 | 0.13657 | 0.00669 | 25.00% | 45.37% |
| 1 | random | terminal | 0.17976 | 0.18061 | 0.17567 | -0.00409 | 20.37% | 43.52% |
| 1 | random | uniform | 0.08233 | 0.07605 | 0.07677 | -0.00556 | 16.67% | 46.30% |
| 1 | random | beam | 0.12263 | 0.13133 | 0.12670 | 0.00406 | 22.22% | 36.11% |
| 1 | random | d4 | 0.06134 | 0.04735 | 0.05255 | -0.00880 | 23.15% | 45.37% |
| 1 | random | held_min | 0.06456 | 0.06327 | 0.06402 | -0.00054 | 19.44% | 50.93% |
| 1 | random | train_min | 0.08351 | 0.08825 | 0.08189 | -0.00162 | 20.37% | 44.44% |
| 2 | robust | d1 | 0.17876 | 0.20735 | 0.22509 | 0.04633 | 70.83% | 62.50% |
| 2 | robust | d2 | 0.08171 | 0.16979 | 0.22297 | 0.14126 | 89.58% | 80.21% |
| 2 | robust | terminal | 0.16140 | 0.16513 | 0.19777 | 0.03637 | 67.71% | 67.71% |
| 2 | robust | uniform | 0.06675 | 0.08762 | 0.07763 | 0.01088 | 52.08% | 53.13% |
| 2 | robust | beam | 0.09823 | 0.15035 | 0.15330 | 0.05506 | 66.67% | 60.42% |
| 2 | robust | d4 | 0.03582 | 0.05052 | 0.03663 | 0.00081 | 36.46% | 60.42% |
| 2 | robust | held_min | 0.04806 | 0.07295 | 0.05399 | 0.00593 | 44.79% | 52.08% |
| 2 | robust | train_min | 0.02969 | 0.09210 | 0.14586 | 0.11617 | 100.00% | 100.00% |
| 2 | mean | d1 | 0.15816 | 0.20344 | 0.25286 | 0.09470 | 92.71% | 92.71% |
| 2 | mean | d2 | 0.06079 | 0.16942 | 0.24936 | 0.18857 | 97.92% | 97.92% |
| 2 | mean | terminal | 0.15608 | 0.16649 | 0.19259 | 0.03652 | 69.79% | 76.04% |
| 2 | mean | uniform | 0.05095 | 0.09418 | 0.07512 | 0.02416 | 53.13% | 59.38% |
| 2 | mean | beam | 0.10347 | 0.15625 | 0.16528 | 0.06181 | 71.88% | 76.04% |
| 2 | mean | d4 | 0.03672 | 0.04543 | 0.03756 | 0.00084 | 34.38% | 59.38% |
| 2 | mean | held_min | 0.03903 | 0.07841 | 0.05885 | 0.01982 | 43.75% | 60.42% |
| 2 | mean | train_min | 0.03932 | 0.09245 | 0.13203 | 0.09271 | 88.54% | 94.79% |
| 2 | d1 | d1 | 0.14086 | 0.20304 | 0.26490 | 0.12405 | 100.00% | 100.00% |
| 2 | d1 | d2 | 0.13137 | 0.16565 | 0.18385 | 0.05249 | 72.92% | 68.75% |
| 2 | d1 | terminal | 0.16123 | 0.16849 | 0.18223 | 0.02101 | 57.29% | 64.58% |
| 2 | d1 | uniform | 0.05911 | 0.08084 | 0.07648 | 0.01736 | 53.13% | 59.38% |
| 2 | d1 | beam | 0.11617 | 0.15579 | 0.14696 | 0.03079 | 64.58% | 60.42% |
| 2 | d1 | d4 | 0.03773 | 0.05110 | 0.03851 | 0.00078 | 31.25% | 66.67% |
| 2 | d1 | held_min | 0.04777 | 0.07060 | 0.05399 | 0.00622 | 43.75% | 58.33% |
| 2 | d1 | train_min | 0.06808 | 0.09117 | 0.10952 | 0.04144 | 73.96% | 73.96% |
| 2 | random | d1 | 0.19688 | 0.20469 | 0.20142 | 0.00454 | 37.50% | 29.17% |
| 2 | random | d2 | 0.17352 | 0.15547 | 0.14592 | -0.02760 | 21.88% | 23.96% |
| 2 | random | terminal | 0.16782 | 0.16441 | 0.17153 | 0.00370 | 27.08% | 48.96% |
| 2 | random | uniform | 0.08568 | 0.07364 | 0.07332 | -0.01236 | 30.21% | 39.58% |
| 2 | random | beam | 0.14968 | 0.14120 | 0.14294 | -0.00674 | 35.42% | 35.42% |
| 2 | random | d4 | 0.04236 | 0.04193 | 0.05469 | 0.01233 | 25.00% | 56.25% |
| 2 | random | held_min | 0.07182 | 0.06033 | 0.06461 | -0.00720 | 29.17% | 45.83% |
| 2 | random | train_min | 0.08811 | 0.09031 | 0.08160 | -0.00651 | 25.00% | 41.67% |

## Verification and cost

- Cohort 1: bases=128, proposals=4224, duplicates=476, unique=3748, scope_checks=3748, guard_dp=30036, guard_states=1873040, utility_fail=531, info_fail=402, causal_fail=636, feasible=2470, training_states=277056, training_decisions=78864, pool_ge3=120, eligible=108, frontier_points=484, pareto_checks=2470. Audit: oracle_checks=3748, training_replays=11244, beam_expansions=110768, fixtures=48, states=2916, transitions=6456, terminal=1572, packet_checks=2916; eligible runtime cells=16.
- Cohort 2: bases=128, proposals=4224, duplicates=440, unique=3784, scope_checks=3784, guard_dp=30304, guard_states=1853608, utility_fail=516, info_fail=423, causal_fail=607, feasible=2505, training_states=272796, training_decisions=79560, pool_ge3=120, eligible=96, frontier_points=464, pareto_checks=2505. Audit: oracle_checks=3784, training_replays=11352, beam_expansions=111800, fixtures=48, states=2730, transitions=6078, terminal=1524, packet_checks=2730; eligible runtime cells=16.

The source oracle and all three training controls replay exactly after freeze. SWMD runtime compiled selected robust tiers for one eligible base per available cell, checked public coordinates and legal menus, reward transitions with one hidden-score prefix per projected state, and terminal status. Stage and score use actual source planning packets and compose submitted actions; oracle and missing-response checks pass for all three tiers of cohort 1. Scope guarantees numeric reaction consistency only, not human narrative quality. Eight public repeated tapes across two cohorts; no independent significance inference, private evaluation, actual model inference or paid compute. Core executed in isolated ECMAScript; standalone Node CLI remains unexecuted. Exact guard and training-policy computation are not a claimed compute saving.

Reproduce: `node integrations/sweepweave-ts/srg24/cli.mjs verify`. Stage: `node integrations/sweepweave-ts/srg24/cli.mjs stage /tmp/srg24-low 0 low`. Score: `node integrations/sweepweave-ts/srg24/cli.mjs score /tmp/srg24-low /tmp/submissions.jsonl`. Withhold packet IDs and verifier data from model prompts; randomize packet order and separate tiers for future model evaluation.
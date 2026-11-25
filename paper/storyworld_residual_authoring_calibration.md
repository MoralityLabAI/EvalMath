# SRG-23: Frozen-predictor constrained storyworld authoring

[Pre-run protocol](../integrations/sweepweave-ts/srg23/PROTOCOL.md), commit 14d7cf2f51a092483aea07e9aeaf15df8e534402. Source b3ea7c7b197cd27708f987454cdd65fa9e915c95. Original SRG-13 candidate and concurrent SRG-AC work unchanged. Public synthetic cargo worlds only.

Train the SRG-22 local and directed ridge models on 3,584 original reaction worlds; fixed lambda=1, all training tapes. Freeze mean, standardization and coefficients. On each fresh base, propose the original and sixteen deterministic two-swap reward edits. Preserve all per-stage reward multisets, phase maps, energy rules, target and bonus. A candidate is feasible when attainable optimum differs by at most one point, informative reachable-row fraction >= max(.85, baseline-.03), and number of stage cuts changing root Q >= max(H-1, baseline count-1). Exact DP guards use full optimal values only for these constraints. No candidate control regret enters tier selection. Each arm uses same deduplicated feasible pool; rank directed or local predictions, or fixed pseudorandom hash, select min/median/max. A base is eligible when pool has >=3 and directed predicted gap >=.03. Commit all selections and coefficients in the freeze manifest before candidate outcome audit. No tuning.

Audit every unique candidate after freeze, including unselected and infeasible proposals. Source oracle and guard outputs agree. Evaluate d1/d2/d4/terminal controls and a new uniform-suffix expected-return policy (compute expected future reward under uniform actions, choose maximizing one-step action plus that expectation at every state). This last control is independent of regression labels but shares public transition information with predictor; it is not an independently trained reasoner. Score regret as (oracle utility - composed utility)/(3H+B). Report high-minus-low per matched eligible base, strict positive fraction and weak monotonic fraction. No significance claim: four repeated public tapes per cohort. Fixed pool selection is not independent model evaluation.

## Registered gate

| Cohort | Eligible coverage | Conditions | Result |
|---|---:|---|---|
| 1 | 45.83% | coverage FAIL; d1_gap PASS; d1_positive FAIL; over_local PASS; independent FAIL | FAIL |
| 2 | 47.40% | coverage FAIL; d1_gap PASS; d1_positive PASS; over_local PASS; independent FAIL | FAIL |

Joint gate: **FAIL**. Coverage >=60%; d1 mean high-low >=.025; strict positive fraction >=60%; d1 improvement over local >=.005; uniform-policy high-low >=.01; all required per cohort. Retain rejection if any gate fails. This is not a production difficulty calibration.

## Tier audit

| Cohort | Arm | Policy | Low regret | Median-tier regret | High regret | High-low | Strict positive | Weak monotone |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | directed | d1 | 0.18576 | 0.19804 | 0.23277 | 0.04700 | 56.82% | 73.86% |
| 1 | directed | d2 | 0.10473 | 0.11604 | 0.15496 | 0.05022 | 52.27% | 72.73% |
| 1 | directed | d4 | 0.01985 | 0.01831 | 0.01319 | -0.00666 | 10.23% | 78.41% |
| 1 | directed | terminal | 0.11465 | 0.11218 | 0.10634 | -0.00830 | 14.77% | 55.68% |
| 1 | directed | uniform | 0.08807 | 0.08390 | 0.09116 | 0.00309 | 39.77% | 63.64% |
| 1 | local | d1 | 0.19568 | 0.19713 | 0.21676 | 0.02109 | 48.86% | 64.77% |
| 1 | local | d2 | 0.12854 | 0.11802 | 0.13239 | 0.00385 | 35.23% | 59.09% |
| 1 | local | d4 | 0.01133 | 0.01992 | 0.01976 | 0.00843 | 17.05% | 86.36% |
| 1 | local | terminal | 0.11405 | 0.11332 | 0.10786 | -0.00619 | 14.77% | 55.68% |
| 1 | local | uniform | 0.10028 | 0.08365 | 0.08722 | -0.01307 | 32.95% | 51.14% |
| 1 | random | d1 | 0.20180 | 0.19931 | 0.20574 | 0.00395 | 31.82% | 42.05% |
| 1 | random | d2 | 0.11910 | 0.11562 | 0.12187 | 0.00278 | 26.14% | 56.82% |
| 1 | random | d4 | 0.01714 | 0.01698 | 0.01698 | -0.00016 | 7.95% | 86.36% |
| 1 | random | terminal | 0.10928 | 0.10830 | 0.11234 | 0.00306 | 26.14% | 63.64% |
| 1 | random | uniform | 0.08093 | 0.08747 | 0.09473 | 0.01379 | 28.41% | 51.14% |
| 2 | directed | d1 | 0.14737 | 0.16825 | 0.20327 | 0.05589 | 61.54% | 84.62% |
| 2 | directed | d2 | 0.12399 | 0.14484 | 0.15125 | 0.02726 | 49.45% | 74.73% |
| 2 | directed | d4 | 0.01633 | 0.01120 | 0.01187 | -0.00446 | 7.69% | 87.91% |
| 2 | directed | terminal | 0.14008 | 0.13864 | 0.13922 | -0.00085 | 18.68% | 59.34% |
| 2 | directed | uniform | 0.06850 | 0.06972 | 0.06682 | -0.00168 | 32.97% | 58.24% |
| 2 | local | d1 | 0.16126 | 0.17140 | 0.19335 | 0.03208 | 43.96% | 72.53% |
| 2 | local | d2 | 0.12399 | 0.14756 | 0.13333 | 0.00934 | 32.97% | 56.04% |
| 2 | local | d4 | 0.01404 | 0.01172 | 0.00943 | -0.00461 | 5.49% | 85.71% |
| 2 | local | terminal | 0.14142 | 0.13724 | 0.14121 | -0.00021 | 20.88% | 61.54% |
| 2 | local | uniform | 0.06337 | 0.06877 | 0.06294 | -0.00043 | 23.08% | 56.04% |
| 2 | random | d1 | 0.17549 | 0.17283 | 0.17241 | -0.00308 | 20.88% | 47.25% |
| 2 | random | d2 | 0.13541 | 0.12689 | 0.15079 | 0.01538 | 25.27% | 48.35% |
| 2 | random | d4 | 0.01224 | 0.01374 | 0.01343 | 0.00119 | 6.59% | 82.42% |
| 2 | random | terminal | 0.13938 | 0.14206 | 0.14045 | 0.00107 | 15.38% | 61.54% |
| 2 | random | uniform | 0.06484 | 0.06966 | 0.05635 | -0.00849 | 17.58% | 48.35% |

Candidate-level outcomes and selection/feasibility margins are in separate receipts. The scope constraint preserves public reaction templates and payoff ranges, not human narrative consistency in an existing storyworld. Eligible tiers are synthetic fixed worlds; selection optimizes a proxy and can exploit its errors. Evaluation against local and independent controls is essential. Actual language-model calibration remains outstanding.

## Verification and cost

- Cohort 1: bases=192, proposals=3264, duplicates=572, unique=2692, scope_checks=2692, guard_dp=19084, guard_states=1007792, utility_fail=231, info_fail=231, causal_fail=318, feasible=1992, pool_ge3=181, eligible=88, feature_calls=1992, feature_edges=217639, flow_edges=796736. Runtime/audit: oracle_checks=2692, fixtures=57, states=2370, transitions=5328, terminal=1440, packet_checks=2370; 19 cells with eligible fixtures.
- Cohort 2: bases=192, proposals=3264, duplicates=452, unique=2812, scope_checks=2812, guard_dp=19852, guard_states=979696, utility_fail=405, info_fail=326, causal_fail=358, feasible=1883, pool_ge3=184, eligible=91, feature_calls=1883, feature_edges=189516, flow_edges=690456. Runtime/audit: oracle_checks=2812, fixtures=60, states=2085, transitions=4506, terminal=1320, packet_checks=2085; 20 cells with eligible fixtures.

Compiled selected worlds for one eligible base per available factorial cell, checked reachable projected state transitions with one prefix per state, hidden score and terminal reward. Stage exports source-defined public planning packets and scores id/action submissions by actual composed policy; oracle and missing-response checks passed for all three tiers of cohort 1. Standalone Node CLI remains unexecuted. Core computations executed in isolated ECMAScript with pinned source. No paid compute, private data or editor modification.

Reproduce: `node integrations/sweepweave-ts/srg23/cli.mjs verify`. Stage: `node integrations/sweepweave-ts/srg23/cli.mjs stage /tmp/srg23-low 0 low` (cohort 0 or 1, low/mid/high). Score: `node integrations/sweepweave-ts/srg23/cli.mjs score /tmp/srg23-low /tmp/submissions.jsonl`. Withhold IDs, manifests and gold labels from prompts; randomize order and separate tiers during future actual model evaluation.
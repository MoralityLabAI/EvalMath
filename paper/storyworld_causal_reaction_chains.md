# SRG-18: Coupled reaction chains and causal planning sensitivity

[Protocol](../integrations/sweepweave-ts/srg18/PROTOCOL.md) committed before public run at fccdd4a14ac9f643770de447e04f86f45946d487. Original storyworld unchanged. This is an exploratory deterministic SWMD calibration gym.

## Model

State s=(t,m,e) consists of turn, mode and energy. A legal action a applies a published per-turn phase permutation and an energy increment of 0, -1 or +1. Collect pays r_t(m) in {1,2,3}, other actions pay zero running points. The last reaction adds B if m'=target and e'>0. V_t(s)=max_a[r_t(s,a)+V_{t+1}(T_t(s,a))], V_H=0. The terminal bonus is included in the last reaction reward. Root Q is computed in integers. V with d remaining lookahead steps has zero continuation value at d=0; a receding policy replans after every reaction. Terminal-only solves the same transitions ignoring running reward. Every stage has its own reaction maps and reward vector; unlike SRG-17B there is no deliberately inert waiting stage. Some random maps coincide or are identity. W is state width, not a certified K-complexity measure. Full model inputs include all remaining reaction tables and the target.

## Public diagnostic

48 factor cells, 768 matched base worlds, 3584 target-specific roots, 120128 reachable decision packets. 1904 independent brute root checks, 4760 action-value comparisons, 384 matched bonus checks and 2816 same-base target comparisons. All oracle rollouts match exact optimum. 48 SWMD-SRG/2 fixtures, 1358 reachable projected states, 3024 transitions including 854 terminal reactions. Runtime check keeps one witness prefix per projected state; hidden cumulative score may differ across prefixes but has no effect on transition guards or payoffs. Scorer malformed, missing and oracle submissions passed.

| Policy | Root accuracy | Informative accuracy | Nominal utility | Fraction of oracle points | Total regret |
|---|---:|---:|---:|---:|---:|
| first | 38.76% | 49.67% | 24.33% | 36.12% | 37000 |
| d1 | 82.03% | 82.09% | 53.21% | 79.02% | 12154 |
| d2 | 87.47% | 87.71% | 57.58% | 85.50% | 8400 |
| d4 | 92.94% | 96.63% | 64.51% | 95.79% | 2436 |
| terminal | 47.99% | 64.89% | 50.11% | 74.41% | 14820 |
| oracle | 100.00% | 100.00% | 67.34% | 100.00% | 0 |

| Horizon | d1/oracle | d2/oracle | d4/oracle |
|---|---:|---:|---:|
| H2 | 87.26% | 100.00% | 100.00% |
| H4 | 76.27% | 84.60% | 100.00% |
| H6 | 78.21% | 82.90% | 94.06% |
| H8 | 78.55% | 83.34% | 93.35% |

Root accuracy uses the whole oracle winner set. Regret uses composed deterministic rollouts. Nominal utility denominator is sum(3H+B); fraction of oracle points uses sum of exact optimum. Do not treat rows or targets as independent samples. Lookahead d1/d2/d4 is a specific zero-leaf-heuristic baseline. Exact dynamic programming with a better heuristic can avoid enumerating all trajectories.

## Interventions

All 8960 target pairs in a common base are considered. 2184 have unique opposite (different) optimal root actions with each margin >=1. A target-blind deterministic policy with common tie-breaking cannot be correct on both. This is a deliberately conditioned witness subset, not an independent test distribution. All observed target pairs have the same immediate root reaction table and initial state. (The terminal reward differs, and target is public.)

| Policy | Both roots correct | Individual roots correct | Paired rollout regret |
|---|---:|---:|---:|
| first | 0/2184 | 1687/4368 | 41646 |
| d1 | 0/2184 | 2112/4368 | 18254 |
| d2 | 711/2184 | 2858/4368 | 12117 |
| d4 | 1422/2184 | 3586/4368 | 3508 |
| terminal | 662/2184 | 2633/4368 | 12610 |
| oracle | 2184/2184 | 4368/4368 | 0 |

Stage cuts replace all phase maps at one stage by identity, preserving energy rules and running reward function. Out of 17920 probes, 15745 change the root Q vector, 12651 change the optimal root value, 3343 change a unique optimal root action to a different unique action. 2174 roots have a Q change under every single-stage cut. The intervention also changes reachable states; sensitivity is causal under this simulator, not a lower bound on reasoning complexity. Of 3244 strict roots, 426 require full nominal depth for these specific truncated controls, and 294 have nonmonotone correctness across depths. The receipt reports min and persistent thresholds, broken down by H/W.

## Reproduction

```sh
node integrations/sweepweave-ts/srg18/cli.mjs verify
node integrations/sweepweave-ts/srg18/cli.mjs stage /tmp/srg18-pilot 0x53521801 1
node integrations/sweepweave-ts/srg18/cli.mjs score /tmp/srg18-pilot /tmp/submissions.jsonl
```

Score accepts JSONL id/action pairs. Only model_input/planning.jsonl is model-facing; avoid exposing IDs, seeds, source fixtures and prior submissions to the model; randomize packet order for fresh private runs. Hash checks bind corpus and generator. The public run used isolated ECMAScript with pinned runtime sources, not standalone Node CLI, HTTP inference, independent private seeds, or the production editor. No paid compute. Sixteen matched tapes; no statistical generalization claim. The finite state and fully observed transition tables are deliberate simplifications. Next use partial information and stochastic reaction outcomes, preserve the matched target intervention, and compare against a calibrated state-value heuristic and analytic shortcuts.
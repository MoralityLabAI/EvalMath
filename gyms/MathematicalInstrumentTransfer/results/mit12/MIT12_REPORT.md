# MIT-12 compact recurrent controller (open exploratory, CPU)

Open development evidence. No sealed set exists or was created. Controllers and thresholds were chosen on the dev roots only; eval roots were not used for any choice.

## Data
- train: 450 roots, 9873 states, 50662 state-actions (random 150r/2866s, palette 150r/3858s, higher 150r/3149s)
- dev: 120 roots, 2707 states, 13324 state-actions (random 40r/895s, palette 40r/965s, higher 40r/847s)
- eval: 180 roots, 4110 states, 20923 state-actions (random 60r/1137s, palette 60r/1707s, higher 60r/1266s)
- higher-order roots with exact aliasing witness (optimum(a) != optimum(b)): {'train': 92, 'dev': 26, 'eval': 33}
- states where the sham changed the state: eval 0.254 (random 0.522, palette 0.187, higher 0.103)

## Parameters
scalar 2321, rel 2705, rel_sham 2705, trm 3153, trm_sham 3153, router 548; TRM T selected on dev: 4 (dev state regret {'2': 0.0032711902167648077, '4': 0.0031283244024962187}); router tau 0.05

## Eval roots: proposal quality and executed policy (mean over 3 seeds and roots)
| controller | params | state acc | state regret | executed regret (uncertified) | max root regret | accept eta=0 | accept eta=0.01 | regret eta=0.01 |
|---|---|---|---|---|---|---|---|---|
| direct | - | 0.8341 | 0.0146 | 0.15130 | 0.5294 | - | - | - |
| greedy | - | 0.9949 | 0.0001 | 0.00150 | 0.0526 | 0.4255 | 0.4318 | 0.0000 |
| depth2 | - | 1.0000 | 0.0000 | 0.00000 | 0.0000 | 0.4260 | 0.4323 | 0.0000 |
| depth3 | - | 1.0000 | 0.0000 | 0.00000 | 0.0000 | 0.4260 | 0.4323 | 0.0000 |
| scalar | 2321 | 0.9954 | 0.0001 | 0.00116 | 0.0417 | 0.4247 | 0.4305 | 0.0000 |
| rel | 2705 | 0.9951 | 0.0001 | 0.00105 | 0.0267 | 0.4219 | 0.4274 | 0.0000 |
| rel_sham | 2705 | 0.9947 | 0.0001 | 0.00139 | 0.0200 | 0.4235 | 0.4290 | 0.0000 |
| trm | 3153 | 0.9422 | 0.0033 | 0.03727 | 0.1877 | 0.4249 | 0.4310 | 0.0000 |
| trm_sham | 3153 | 0.9345 | 0.0037 | 0.04506 | 0.2451 | 0.4207 | 0.4272 | 0.0000 |
| router | 548 | 0.9472 | 0.0016 | 0.02046 | 0.1579 | 0.4207 | 0.4261 | 0.0000 |

Certified execution at eta=0: executed regret scalar 0.0e+00, rel 0.0e+00, trm 0.0e+00, router 0.0e+00, greedy 0.0e+00, depth2 0.0e+00, depth3 0.0e+00 (max over roots/seeds).

## Cost per decision (cost roots: 24, seed 0, fresh planners)
| config | planner states / decision | ms / decision (mean) | ms (median) | acceptance |
|---|---|---|---|---|
| depth2|c0 | 313.2 | 129.15 | 81.65 | 0.409 |
| depth2|plain | 44.4 | 8.27 | 6.86 | - |
| depth3|c0 | 422.0 | 157.80 | 123.15 | 0.409 |
| depth3|plain | 129.1 | 33.73 | 24.08 | - |
| exact|plain | 223.1 | 97.15 | 58.48 | - |
| greedy|c0 | 314.9 | 125.12 | 89.00 | 0.407 |
| greedy|plain | 0.0 | 0.23 | 0.23 | - |
| rel_s0|c0 | 315.8 | 128.77 | 87.84 | 0.409 |
| rel_s0|c01 | 317.1 | 128.89 | 87.66 | 0.423 |
| rel_s0|plain | 0.0 | 1.55 | 1.50 | - |
| rel_sham_s0|c0 | 315.2 | 129.97 | 99.41 | 0.408 |
| rel_sham_s0|c01 | 316.7 | 126.08 | 90.30 | 0.425 |
| rel_sham_s0|plain | 0.0 | 1.37 | 1.42 | - |
| router_s0|c0 | 321.2 | 128.01 | 90.47 | 0.403 |
| router_s0|c01 | 322.7 | 135.84 | 101.11 | 0.417 |
| router_s0|plain | 0.0 | 0.60 | 0.62 | - |
| scalar_s0|c0 | 318.2 | 129.28 | 86.60 | 0.405 |
| scalar_s0|plain | 0.0 | 0.72 | 0.68 | - |
| trm_s0|c0 | 316.9 | 132.95 | 91.59 | 0.411 |
| trm_s0|c01 | 318.2 | 128.08 | 93.43 | 0.426 |
| trm_s0|plain | 0.0 | 2.83 | 2.88 | - |
| trm_sham_s0|c0 | 318.8 | 134.45 | 97.35 | 0.406 |
| trm_sham_s0|c01 | 320.1 | 132.53 | 91.19 | 0.421 |
| trm_sham_s0|plain | 0.0 | 2.58 | 2.54 | - |

## Paired root-level differences on eval roots (a - b, lower is better; 95% bootstrap CI)
- executed_regret: trm - rel: mean +0.03622 CI [+0.03063, +0.04199], a lower 1, b lower 134, ties 45, n 180
- executed_regret: trm - trm_sham: mean -0.00779 CI [-0.01158, -0.00392], a lower 86, b lower 42, ties 52, n 180
- executed_regret: rel - rel_sham: mean -0.00034 CI [-0.00087, +0.00020], a lower 14, b lower 9, ties 157, n 180
- executed_regret: trm - scalar: mean +0.03612 CI [+0.03056, +0.04190], a lower 1, b lower 134, ties 45, n 180
- executed_regret: trm - rel_sham: mean +0.03588 CI [+0.03027, +0.04159], a lower 2, b lower 133, ties 45, n 180
- state_regret: trm - rel: mean +0.00327 CI [+0.00265, +0.00393], a lower 2, b lower 122, ties 56, n 180
- state_regret: trm - trm_sham: mean -0.00041 CI [-0.00080, -0.00003], a lower 79, b lower 47, ties 54, n 180
- state_regret: rel - rel_sham: mean -0.00002 CI [-0.00004, +0.00000], a lower 18, b lower 9, ties 153, n 180
- state_regret: trm - scalar: mean +0.00326 CI [+0.00265, +0.00392], a lower 2, b lower 121, ties 57, n 180
- state_regret: trm - rel_sham: mean +0.00325 CI [+0.00264, +0.00391], a lower 2, b lower 122, ties 56, n 180
- state_error: trm - rel: mean +0.05296 CI [+0.04456, +0.06111], a lower 2, b lower 121, ties 57, n 180
- state_error: trm - trm_sham: mean -0.00764 CI [-0.01245, -0.00277], a lower 72, b lower 37, ties 71, n 180
- state_error: rel - rel_sham: mean -0.00044 CI [-0.00130, +0.00049], a lower 16, b lower 9, ties 155, n 180
- state_error: trm - scalar: mean +0.05325 CI [+0.04499, +0.06141], a lower 2, b lower 121, ties 57, n 180
- state_error: trm - rel_sham: mean +0.05253 CI [+0.04416, +0.06058], a lower 2, b lower 122, ties 56, n 180
- executed_regret: scalar - depth3: mean +0.00116 CI [+0.00056, +0.00191], a lower 0, b lower 19, ties 161, n 180
- state_regret: scalar - depth3: mean +0.00006 CI [+0.00003, +0.00010], a lower 0, b lower 24, ties 156, n 180
- states_per_decision: scalar_s0|c0 - depth3|plain: mean +189.12125 CI [+136.48747, +250.65860], a lower 0, b lower 24, ties 0, n 24
- ms_per_decision: scalar_s0|c0 - depth3|plain: mean +95.54729 CI [+63.12645, +132.87078], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: scalar_s0|c0 - depth2|plain: mean +273.85096 CI [+201.69626, +354.37603], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: scalar_s0|c0 - exact|plain: mean +95.16686 CI [+79.10010, +112.61495], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: rel_s0|c0 - depth2|plain: mean +271.38632 CI [+199.81209, +351.22147], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: rel_s0|c0 - exact|plain: mean +92.70222 CI [+78.13260, +108.41274], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: trm_s0|c0 - depth2|plain: mean +272.50770 CI [+200.53461, +352.55039], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: trm_s0|c0 - exact|plain: mean +93.82360 CI [+78.90109, +109.58586], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: router_s0|c0 - depth2|plain: mean +276.78525 CI [+203.61586, +358.42472], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: router_s0|c0 - exact|plain: mean +98.10115 CI [+80.56688, +117.52986], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: greedy|c0 - depth2|plain: mean +270.55389 CI [+199.11944, +350.37158], a lower 0, b lower 24, ties 0, n 24
- states_per_decision: greedy|c0 - exact|plain: mean +91.86979 CI [+77.51490, +107.38102], a lower 0, b lower 24, ties 0, n 24

## Higher-order family (state regret / state accuracy / executed regret)
- scalar: 0.0001 / 0.9982 / 0.00150
- rel: 0.0000 / 0.9988 / 0.00102
- rel_sham: 0.0001 / 0.9982 / 0.00159
- trm: 0.0012 / 0.9864 / 0.03217
- trm_sham: 0.0013 / 0.9849 / 0.03943
- router: 0.0013 / 0.9561 / 0.00880

## Preflight (dev pilot, strict), verbatim
exit code 2; best learned by dev state regret: scalar
```
{
  "approx_resolvable_effect": 0.2686547161462134,
  "approx_worlds_for_80pct_power": null,
  "decision": "REDESIGN_OR_PILOT_ONLY",
  "experiment_id": "MIT-12-trm-vs-relational-dev",
  "independent_unit": "root",
  "limits": "Normal-based power is planning only. A zero-effect zero-variance pilot cannot support extrapolating a hypothetical positive effect. Root and sham independence, symmetry, readout sealing, and the scientific effect floor require independent audits. Repeated outcomes within a root are never additional worlds.",
  "mean_pilot_effect": -0.039231103573333335,
  "mechanistic_variation_floor": 0.2562962963,
  "minimum_exact_sign_test_roots": 6,
  "observed_worst_sham": 0.2885802469,
  "order_statistic_rank": 119,
  "pilot_world_sigma": 0.03819512887613275,
  "pilot_worlds": 120,
  "planned_comparisons": 3,
  "planned_confirmation_worlds": 100,
  "reasons": [
    "heldout_unsealed",
    "target_below_mechanistic_variation_floor",
    "pilot_effect_not_above_mechanistic_variation_floor",
    "confirmation_underpowered"
  ],
  "schema": "EvalMath/mechinterp-power-preflight/v1",
  "target_effect": 0.02,
  "upper_sham_quantile": 0.2562962963
}
```

Training CPU seconds (sum over jobs) 3023; wall 788.
Source sha256 are in mit12_result.json.

Provenance correction: `source_sha256` for `compact_controller.py` was computed on a CRLF working copy (4bf061a72c0f…); the committed LF file hashes to 30373512bd59… (recorded in `source_sha256_correction`). The source text is the same.

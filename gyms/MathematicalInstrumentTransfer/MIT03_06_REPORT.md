# MIT-03–06: open development suite

2026-11-25. Synthetic development evidence; no sealed model proof run. All timings below refer to one CPU implementation.

## MIT-03 relational selector

44 training roots, 13,008 within-root states, 148,672 action labels. Nine fits (three seeds each for scalar, relation and scrambled relation). 209 and 211 parameters respectively. Residual Q above one-action/direct-guess score. Relation features encode conditional follow-up gains and intersections. Sham rotates membership inside equal-weight classes, preserving marginal cardinalities and masses. On 96 open roots, oracle and all three relation seeds and exact two-action search score 85.6217%; scalar mean 84.9702%, sham mean 84.966%, greedy 84.9142%, direct guess 51.4685%. Two-action search median 1.001 ms, relational 1.014–1.040 ms, initial expanded oracle 10.716 ms. Relation features partly compute symbolic two-step gains; no resolved neural advantage. Three-step and two-step here count adaptive actions, including guesses, before filling remaining budget with direct guesses.

## MIT-04 exact counterexample

20 equally weighted worlds, three binary instrument bits, budget five. Counts in lexicographic signature order are A=(3,1,1,4,4,1,2,4) and B=(4,0,0,5,3,2,3,3). Their difference is an alternating parity vector, summing to zero when any coordinate is omitted. Identical pairwise tables: (4,5,5,6), (4,5,6,5), (7,2,3,8). Count recursion and expanded search yield 13/20 versus 14/20. Pairwise-only representations cannot determine optimal value everywhere. This is a value counterexample, not a universal claim about policy rankings or relational neural nets.

## MIT-05 signature quotient

For deterministic binary queries, one winner, positive integer prior weights, once-only positive-cost queries, perfect guess feedback: group strategies by full membership signature and identical weight. Retain counts, available query set, remaining budget. By induction on budget, expanded states with equal counts have identical value: every guess type has the same success mass and decrement, and each query splits types identically. Thus the available first-action maxima agree. Randomization mixes values. The implementation skips deterministic no-information queries, which are dominated by preserving budget. No Lean verification yet; scope excludes stochastic channels, real proof trees and arbitrary priors conditioned on unmodeled variables.

22 exact comparisons with expanded search match. Cached states 519362 vs 81168; repeated-signature subset (12 roots) 408465 vs 34366, median 123.256 vs 10.594 ms. Speed depends on duplication and implementation. Open seed 52003: 28 worlds, 6 queries, budget 6; two-action rollout 22/28, three-action and compressed oracle 23/28. Fresh open stress seeds 52040–52063: exact and three-action 74.256% (24/24 optimal), two-action 73.363% (18/24), relational 73.661%, 73.958%, 73.661% (20,22,20 of 24). Median oracle initial value 52.344 ms (group construction excluded), three-action 45.286 ms, two-action 6.074 ms, relational 4.123–4.366 ms. Timing/quality tradeoff is exploratory, not prospective confirmation.

## MIT-06 proof fixtures

128 open roots, 4 families (finite integer LP maximum, DAG longest path, integer covering minimum, modular inconsistency). 128 true and 128 false variants, 1024 prompt rows. Symbolic constructor and independent finite enumeration verify all rows; 256/256 mapping checks. This only validates fixtures; symbolic solver has typed instance, no model inference. Certificate-neutral common response format, applicability separated from statement truth. Public row ID contains arm/truth; send ONLY prompt. Private instance and candidate must stay with verifier. Shams are not token matched; actual model runs need frozen tokenizer, budget, checkpoint and usage ledger. Raw local data, trained weights, regression tests and model scorer are in the accompanying local MIT-03-06 archive; repository code is a reproducible development runner, not the full archived local result.

## Preflight

Ran repository script blob 0ff062f76f5534d9f18425f986ae3e750397f50c on 96 root-level paired effects, averaging seeds and retaining separate sham controls. Rel minus scalar +0.6515 pp, descriptive 95/95 sham order statistic 8.333 pp, provisional meaningful floor 10 pp. Strict exit 2 REDESIGN_OR_PILOT_ONLY: heldout_unsealed, independence_unverified, pilot_effect_not_above_mechanistic_variation_floor. No sealed split opened. Do not claim neural causal gain. Keep symbolic quotient and depth3 baselines. Actual compact model proof runs require local weights and matched budgets.

## Reproduce search suite

Install NumPy separately, then from this gym directory run:
```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python relational.py --output relational_result.json
python higher_order.py
python signature_dp.py
python deep_stress.py
python deep_eval.py
```
Generate open proof fixtures with the proof_pilot.py runner once present. The repository central exact receipts are unchanged because these are open, timing-sensitive diagnostics. No model checkpoint or Lean build was available locally. Prior PR CI still in progress at review.

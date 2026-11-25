# MIC-12: cost-aware elimination gate

Cloud CPU public development following [MIC-11 draft #95](https://github.com/MoralityLabAI/EvalMath/pull/95). Six inherited source modules pinned from 3377d30884fec603b40e08ea81761dd3f99e521f. No upstream manuscripts or paid compute.

## Counterfactual teacher

From 24 original conflict/mixed training graphs (32/64 vertices, seeds 8100..8105), collect up to 12 nonroot states per root from root-only search at 256 normalizations. For each state, compare one independently verified residual elimination attempt against a fresh local branch-and-bound search capped at 32 child normalizations. The same global incumbent is the lower reference for both; a successful elimination must lie within the local branch interval. Define gap as the interval width for the maximum of the global incumbent and the residual optimum; successful elimination closes it. Failure to plan/execute leaves the original gap.

The exact rational utility proxy is (gap_branch - gap_elim)/total_root_weight - (1/50)*(cost_elim - cost_branch). Cost_elim = cells/250000 + degree_scans/250000 + attempts/64, cost_branch = normalizations/32. These coefficients were chosen as a development heuristic, not measured interchangeable work or a calibrated runtime penalty. Label 1 requires a successful attempt and positive utility. All 120 successful attempts among 194 training decisions were positive, so the cost term did not distinguish among successful attempts. This is a substantive label collapse: the learned binary target is identical to eligibility on the collected training distribution. Do not interpret it as a calibrated net-value estimator.

Ten features: free/required/root sizes, projected clause count, projected primal degree statistics, fraction of degree <=2, current bound gap and free weight. Three 193-parameter MLP fits at seeds 17/29/43, 160 Adam steps, lr .012, BCE, threshold logit >=0. Root attempt is shared by every elimination arm, independent of the model. Gate only selects whether to request a residual computation; it cannot approve a solution, discharge an uncertified state or modify pruning bounds. Feature extraction and inference incur real cost. The local teacher resets the branch solver/cache and VE budget; it does not model the whole search's opportunity cost or remaining budget.

## Fresh public evaluation

72 roots (4 inherited families x sizes 32/64/128 x seeds 9000..9001 x original/one-hub/three-hub structures), eight policy rollouts per root. All share 512 normalization cap, 250000 VE cells, 250000 degree scans, 64 attempts, width <=10. Baseline uses no VE; root attempts once; size triggers at <=24 free vertices; periodic attempts every eighth surviving pop or <=24 free vertices; always attempts while caps permit; learned gate acts on nonroot states while caps permit. Counters omit other arithmetic and are not a common total-work budget. Timings include inference and features, exclude independent replay and training; single-machine order-dependent observations, not universal speed or hard-deadline claims.

| Policy | Certified /72 | Mean ms | Mean normalized gap % | Mean normalizations | Mean VE attempts | Mean VE cells |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 56 | 40.238 | 3.5235 | 171.08 | 0 | 0 |
| Root-only | 60 | 31.572 | 2.8705 | 104.39 | 1 | 8779.58 |
| Periodic | 63 | 50.258 | 2.2361 | 89.11 | 10.47 | 45297.81 |
| Size | 62 | 40.413 | 2.4275 | 94.61 | 7.49 | 18973.78 |
| Always | 62 | 54.741 | 2.3731 | 87.75 | 14.32 | 67958.97 |
| Learned, mean of 3 | 63 | 67.901 | 2.2061 | 86.74 | 13.19 | 63347.06 |

Each learned seed certifies 63/72. Pooled interval closes on 63/72, nine remain unresolved. On 24 original roots: baseline/root 12 certificates, size/always 14, periodic/each learned seed 15. On 48 planted roots, all VE policies close the root. Thus gate comparison is diluted by common root success. Original-only mean ms for periodic/learned = 131.998/184.739; original-only normalized gap = 6.7084/6.6183%. Learned gate calls 5630 and selects 2632 attempts across 216 model-root rollouts (nonroot decisions); all occur on originals. The learned policy's small interval improvement has no certificate count gain and incurs ~35% higher overall observed runtime than periodic. Root-only remains fastest aggregate; size is useful as a cheaper intermediate. No training promotion.

## Verification and resolution

Four targeted tests pass: exhaustive small-root local teacher comparison, learned gate soundness under caps (12 small roots), inherited policy agreement and budget boundaries. Cloud CPU PyTorch 2.10.0+cpu, one thread; primary run 32.739 s. Every one of 576 final masks and its objective validated. Replay accepted 1605 distinct residual certificates covering 2890 occurrences, 2554 nonroot occurrences; identical receipts within a root replayed once; each distinct receipt rejects a tampered objective. Replay 12.458 s. This is independent sparse-factor replay of residual optima, not replay of the full global B&B frontier.

Retrospective preflight contrast: periodic gap minus mean learned gap, divided by total root weight, grouped across four unverified generator lineages. Mean 0.030059 pp; maximum within-root seed difference 0.139276 pp; no calibrated 95/95 sham threshold, no sealed confirmation, inherited 5 pp floor. Exact repo planner returned REDESIGN_OR_PILOT_ONLY (strict exit 2). A deterministic model gate cannot establish a general learned performance advantage from this pilot.

## Replay

    cd gyms/MIC12
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python -m pytest -q test_mic12.py
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python mic12.py > results.json
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python replay.py
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC12/preflight_input.json --strict

SHA256 tested mic12.py b7452e26fecbefc19ad0a14fbc3b24377e1569a38936e6847ebd37270cbb6461, test_mic12.py 0d9e68b224b1460f64ae95fb9e3e890e32c892a649bdf89dba403ecccd49cd0b, replay.py ac49d22795e8e2d633ad7a8f52cc78de344f1d696dfc0a43eeb163e97a281fc2. Timing-dependent results.json d84a73bccc7dd6152f81944df4e2e805d2af15abf50905694bcc6d9022ea5e6d; audit_results.json 3ebb87f6ddb8d6c7cdb18c0f4f35fcc1f11b7e5876942fbdf50b36fd218e2add. Raw files not committed; reproducible from code. Full repo CI outstanding. A cloud tool timeout was reported despite a complete valid result file; replay and tests subsequently succeeded.

## Next direction

Stop small gate sweeps on this distribution until cost-sensitive labels distinguish expensive successful attempts from cheap ones and include remaining budget/opportunity cost. Prefer exact proof-carrying search: serialize the frontier, branch partitions, normalization witnesses, component eliminations and residual receipts for independent global interval replay. Build a curriculum of independently verified proof-obligation transformations. Only pursue learned scheduling with a nontrivial cost frontier and an equal measured work/time comparison. The original DLMST textual discovery-history question remains untested; keep public manuscripts out of held-out discovery evaluation and quarantine rights-sensitive materials. No new token allocation.

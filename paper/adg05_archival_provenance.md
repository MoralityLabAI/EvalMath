# ADG-05: Provenance-aware planning under revocation

**Evidence:** exact finite synthetic law and parameter census. No language-model training, empirical archival validation, independent sampling, or sealed confirmation.

## Contract

Two possible attributions, uniform prior. There are three conditionally independent source origins A, B and C given the true attribution H. A supplies one observed positive report and two deterministic copies. B requires one or two unit-cost catalogue hops before a unit-cost fetch. C is accessible immediately. Each origin has a validity prior q, an accuracy a conditional on validity, and a fair report conditional on invalidity. A noisy unit-cost audit tests validity with symmetric sensitivity/specificity t. A two-unit registry query reveals validity exactly. All observations condition the same origin's factor; copies add no information. The likelihood parameters, origin relationships and access costs are public. The hidden outcomes are marginalized, not available to policies. This is a closed-world structural model, not an open-ended search engine.

Actions cost positive integers. Budgets are 3, 4 or 5. Correct assertion pays +1; false assertion pays -4; abstention pays zero. Hence assertion requires posterior probability strictly greater than 4/5 (ties abstain). No cost penalty beyond the budget; reported cost is a secondary outcome. Scores below are unconditional probabilities, conditional on the initial A report being positive; symmetry makes the other initial sign equivalent. The binary, conditionally independent, known-channel assumptions and the reward are design choices.

## Source ledger and two exact results

Let E_s contain observations from origin s, including noisy audits and registry results. Let L_s(h)=sum_v P(v) P(report|h,v) P(audit|v) 1{registry agrees with v}, omitting unobserved factors. Conditional independence yields posterior odds O = O_prior * product_s L_s(1)/L_s(0). A new observation for origin s replaces its factor, including prior audits. An invalid source with fair report and validity observations independent of H has L_s(1)=L_s(0). This is a conditioning result for the stated model, not a general instruction to discard adverse evidence. If invalid sources can be systematically biased or share latent confounders, use their joint likelihood instead.

A scalar posterior fails to be revision sufficient: identical sources with q=2/3 and a=1 yield report likelihood ratios 5 and 1/5. Histories (A+,B-) and (A-,B+) both give P(H)=1/2. A registry ruling that A is invalid yields respectively 1/6 and 5/6. Treating A's two deterministic copies as independent origins preserves their spurious odds after invalidating A and yields respectively 5/6 and 1/6. The examples are exact. Preserving provenance is sufficient here; the example disproves sufficiency of a scalar posterior without identifying the minimal representation for general dependent sources.

At every terminal assertion under the correctly specified model, the conditional error probability is less than 1/5. By averaging over transcripts on which the policy asserts, the unconditional false-assertion probability is bounded by (1/5) times assertion probability. This holds for adaptive legal queries and a stopping decision based solely on the acquired transcript. The result does not calibrate an agent with incorrect priors or hidden information.

## Finite Bellman oracle

A state consists of the per-origin report, audit, definitive validity status, catalogue progress, and remaining budget. The next-observation law is the ratio of the sum of successor likelihood masses to the current sum. A catalogue hop has deterministic outcome and no immediate change in posterior. The value recurrence maximizes terminal expected utility and the expected successor value for each legal action. Positive costs yield a finite induction proving optimality for the given model. One- and two-step controls truncate the horizon and replan. Macro control additionally evaluates a whole deterministic catalogue+fetch chain, forecasting one stochastic observation; it then takes the first legal step and replans. It is a strong access-aware baseline, not a full search policy. The copies arm intentionally counts duplicated reports as independent and stops. Deduplicated stop and all planners use the true model; all arms are scored with the true posterior.

## Development census

72 fixed parameter cells: q_A in {1/3,2/3,5/6}; a_A in {3/4,1}; B gate length in {1,2}; budget in {3,4,5}; audit accuracy in {2/3,5/6}. B: q=5/6,a=1; C: q=2/3,a=3/4. Six policies share every cell; all outcomes are integrated exactly. These are cells in a parameter grid, not independent experimental roots. There is no protected test set.

| Policy | Correct | False | Abstain | Utility | Mean cost |
|---|---:|---:|---:|---:|---:|
| Copies | 91/144 | 29/144 | 1/6 | -25/144 | 0 |
| Stop | 7/24 | 1/24 | 2/3 | 1/8 | 0 |
| One | 313/864 | 19/2592 | 817/1296 | 863/2592 | 227/162 |
| Two | 40603/62208 | 269/15552 | 2281/6912 | 36299/62208 | 99505/31104 |
| Macro | 18001/20736 | 1525/62208 | 835/7776 | 47903/62208 | 8447/2592 |
| Full | 27095/31104 | 767/31104 | 1621/15552 | 8009/10368 | 27167/7776 |

Full strictly exceeds macro in 10/72 cells and ties in 62/72. Mean utility gain is 151/62208 = 0.00242734, while mean acquisition cost rises. Maximum cell gain 17/432 (~0.03935) remains below the provisional 0.05 utility effect floor. In this finite family, learning deeper planning beyond catalogue-aware lookahead has little headroom. The severe penalty from treating copies as independent is a separate deliberate misspecification, not a claim about real historical agents.

## Checks and preflight

Six ADG-05 tests and 19 earlier focused ADG tests passed locally. The factorized source likelihood was checked against an independent full triple enumeration over 432 source-history/hypothesis cases; a separate latent-world decision tree agrees with the Bellman oracle on four three-unit-budget profiles. Seven receipt checks pass: probability conservation, budget, optimal dominance, reverse-action-order utility equality, conditional risk bound, independent decision tree, and revocation witness. The action-order sham is exact structural symmetry, not calibrated model variation. Preflight: mean paired effect 0.00242734, provisional meaningful floor 0.05, target 0.15, five comparisons, 240 proposed future confirmation units. REDESIGN_OR_PILOT_ONLY: independence unverified, no sealed holdout, effect below floor. The planner's nominal sample-size estimate is inapplicable to trained neural policies or this nonrandom grid. No model training or paid compute.

The preflight source discrepancy in earlier bundles was a line-break difference. The local file now matches the branch Git blob 0ff062f76f5534d9f18425f986ae3e750397f50c. Earlier receipts have not been regenerated to change their recorded source hashes.

Reproduce from the bundle or repo root:

    PYTHONPATH=src python -m pytest -q tests/test_archival_provenance.py
    PYTHONPATH=src python scripts/verify_archival_provenance.py
    python scripts/check_receipts.py --only adg05

The full receipt includes all 72 cells, exact rates, preflight inputs and outputs, and source SHA-256. The compact receipt retains the canonical raw-row SHA-256. No repository-wide CI was run in this session.

## ADG-06 proposal: infer the lineage itself

The current oracle assumes source relationships and likelihood parameters are known. Remove this privilege from the learned agent. Generate alternative ancestry graphs with latent common sources, missing provenance, independent contradictory witnesses, unreliable metadata and uncertain audit calibration. Provide text and graph clues plus actions that can resolve lineage. Keep the exact known-graph oracle as an upper comparator and compute a small graph-mixture Bayesian oracle for uncertain graphs. Train recurrent and flat planners on the same ledger interface with matched compute; include origin-shuffling, common-source confounders, copied-report amplification, and explicit revocation tests. Optimize source-discovery value and calibrated selective risk at matched budget; freeze generator-family-disjoint confirmation before training. Export only public development trajectories to Data Goblin. Keep oracle latent graph, truth, and confirmation roots evaluator-side.

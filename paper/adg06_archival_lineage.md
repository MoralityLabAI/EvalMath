# ADG-06: Hidden provenance and the value of discovering source lineage

Evidence class: exact finite synthetic development. No trained model, independently sampled historical cases, or sealed confirmation. The second grid was designed after observing the first result.

## Contract

The three reports A, B and C can descend from any of the five partitions of three labels. A is observed positive; B is observed either positive or negative. C is initially unretrieved. A partition G determines which labels share the same validity bit and report. A common latent calibration variable R takes two values, and controls the origin-validity prior, conditional report accuracy, and noisy audit accuracy. Conditional on H, G and R, distinct origins are independent. Invalid reports are fair. The five graph priors allocate probability p to the all-independent graph and (1-p)/4 to each other partition. The prior on H is uniform. Source priors and the possible graph family are known; realized G, R, H and unqueried evidence are unknown. Observing A and B reweights both G and R.

The ordinary grid has validity/conditional accuracy/audit accuracy (1/2, 3/4, 2/3) in the weak regime and (5/6, 1, 5/6) in the strong regime. Graph independence prior and strong-regime prior are each 1/4 or 3/4; metadata accuracy is 2/3 or 5/6; B sign is 0 or 1; budget is 2, 3 or 4. These give 48 parameter cells, not sampled worlds. Querying C or exact lineage requires its own unit-cost catalogue step. Fetching C and querying exact lineage cost one additional unit each. Noisy A/B lineage metadata and noisy A validity audit cost one unit each. Definitive validity registries cost two units; C must be fetched before its registry query. Each action can be taken once. Definitive registry results reveal a validity bit, shared across copies. There is no physical archival access or realistic text-generation layer.

The post-hoc boundary grid fixes B positive, changes the weak and strong regimes to (1/2,1,1/2) and (2/3,1,2/3), respectively, increases C fetch to three units, noisy audit to two, and definitive registries to four. All other factors match the first grid. There are 24 cells. This bundles changes in accuracy and costs: it cannot identify which change is necessary, and is not confirmation of an effect.

Reward is +1 correct attribution, -4 false, zero abstain. An exact posterior supports assertion iff its maximum mass is strictly above 4/5. Cost is a hard budget with secondary preference for lower expected acquisition cost among equal-utility plans. For each profile the oracle enumerates rational masses over latent assignments and converts them to integer weights with a common denominator. Bellman recursion over compatible world masks, legal queries, and remaining budget sums unnormalized successor values. Positive costs prove finite optimality by induction; the evaluation divides by the mass of the initial observed transcript. One-/two-step planners truncate and replan. Macro considers complete catalogue+query chains followed by stopping. The fixed independent and fixed initial-MAP-graph controls plan with restricted graph support, cannot query lineage, and are evaluated under the true mixture; impossible belief states abstain. Known-graph oracle is told G free, not R or H. All policies see the same initial reports and budget. No-lineage ablates both noisy metadata and exact lineage actions; other observations can still indirectly reveal lineage.

## Exact results (rounded display; receipt stores rationals)

| Policy | Ordinary utility | Boundary utility |
|---|---:|---:|
| Stop | .145951 | .434504 |
| Independent | .307026 | .479216 |
| Fixed initial MAP | .306688 | .445695 |
| One step | .292850 | .509410 |
| Two step | .308445 | .524868 |
| Macro | .294268 | .524055 |
| No lineage actions | .308445 | .507999 |
| Full mixture | .308445 | .524868 |
| Known graph | .308888 | .536979 |

Ordinary: full never uses a lineage query; full and two-step have the same scores on the grid. Full vs macro mean utility gain .014177 (12/48 strict wins); full vs independent mean .001418 (4/48 strict wins). Boundary: full vs no lineage mean gain .016869 (9/24 strict wins); maximum .070039. Full vs fixed initial MAP mean .079173, versus independent .045652; full vs macro mean .000813 (1/24 strict wins). Two-step matches full again. Full boundary attribution correct/false/abstain .717719/.048213/.234069; no-lineage .809597/.075399/.115004. False rates are unconditional, not selective risk. Full boundary spends 2.081238 units on average, uses an exact lineage query with probability 1/3, and has terminal graph MAP accuracy .654857; no-lineage spends 1.333333 and has graph MAP accuracy .472777. Known graph is a privileged utility upper bound, not a calibration of neural performance. This evidence supports investigation of provenance in decision-sensitive regimes; it does not warrant deep neural planning compute on these small known families.

## Two exact witnesses and a general identity

For two positive reports, equal prior over shared versus independent origins, validity prior 2/3, perfect valid reports and fair invalid reports, posterior P(H=1) equals 5/6 if shared, 25/26 if independent, 55/62 under the mixture. Registry invalidation of A moves these to 1/2, 5/6, 11/18 respectively. The registry also changes posterior graph odds. In the general mixture the sufficient exact finite state is the joint posterior over H,G,R and any still query-relevant latent origin variables, together with query progress/budget. Averaging per-origin likelihood ratios is not valid in general; marginalize joint likelihood masses before taking odds.

For a separate two-source witness with q=1/2, perfect valid reporting, prior graph odds 1:1 and two positive reports, posterior independent-graph probability is 5/13. Conditional truth probabilities are 9/10 (independent), 3/4 (shared). Marginal truth posterior 21/26 yields stopping utility 1/26. An exact lineage revelation yields expected utility 5/26. Its value is 2/13 before acquisition cost. For a one-shot free observation Y and finite terminal actions a, let u(a,y) be conditional expected utility. E[max_a u(a,Y)] >= max_a E[u(a,Y)] because every fixed action is bounded by the pointwise maximum. Equality iff a common action maximizes utility on every positive-probability observation (choose an optimal fixed action and use the nonnegative expected gap). Thus lineage can be economically important when plausible source graphs imply different optimal terminal actions. This is a one-shot identity, not a theorem about multi-step cost or a claim that entropy reduction is sufficient for utility.

## Checks and reproducibility

Five ADG-06 tests plus six ADG-05 tests pass locally. Independent closed-form initial H,G marginal checks and a separate list-of-worlds decision recursion (12 budget/profile comparisons) check the oracle. Seven receipt checks pass across 72 cells: mass/budget conservation, full-policy dominance, privileged graph upper bound, calibrated Bayesian assertion-risk bound, action-order utility invariance, no-lineage ablation, known graph recovery. Action-order reversal is a structural symmetry, not a matched neural intervention. Preflight is REDESIGN_OR_PILOT_ONLY for both families; primary full-minus-macro gains .014177 and .000813 below the provisional .05 effect floor, target .15, seven comparison planning family, 240 proposed future roots, no independent sampling/sealed data or calibrated shams. The post-hoc grid was exposed before the receipt. No model training or paid compute.

Run from repo root:

    PYTHONPATH=src python -m pytest -q tests/test_archival_lineage.py tests/test_archival_provenance.py
    PYTHONPATH=src python scripts/verify_archival_lineage.py
    PYTHONPATH=src python scripts/verify_archival_lineage.py --compact --output output/evaluation_adg/adg_06_compact.json

The full receipt contains per-cell exact results and both preflight specs. Compact receipt hashes the canonical exact rows and overall metrics, stores exact utilities and source hashes, and retains the decision (rather than hashing floating-point planner displays). Full repository CI has not been executed.

## ADG-07: scalable graph discovery

The remaining challenge is to infer a lineage model from evidence rather than choose among five known alternatives. Generate larger directed ancestry graphs with imperfect textual and chronological metadata, transitive dependence, uncertain source calibration, selective missingness and shared confounders. Keep small exact oracles and strong union-find/beam/particle controls. Use active query selection driven by decision sensitivity rather than generic uncertainty, compare graph posterior calibration and selective risk under equal acquisition budgets, and reserve source-family-disjoint confirmation before fitting a model. A learned controller should first demonstrate headroom over graph-aware macro policies on development; do not allocate GPU credits on the ADG-06 grid alone.

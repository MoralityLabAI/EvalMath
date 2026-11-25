# SRG-14: Full-history causal choice interventions and interaction attribution

2026-11-25. Executed finite source-level counterfactual replays and exact bounded reachability. Public diagnostic, not a promotion gate or model benchmark. The SRG-13 candidate remains frozen and unpromoted.

## 1. Intervention contract

Use the original signed SRG/2 Reservoir Dogs migration and the frozen SRG-13 investigation-ledger candidate. Both retain the authored secret ending eligibility gate. Set binary experimental utility to 1 for the secret truce ending, 0 for every other ending. This is a chosen mechanical goal, not inferred narrative or ethical utility.

Two fresh public xorshift32 streams (0x53521411, 0x53521412; 128 campaigns each) generate 24 policy words per campaign. The ordinary policy selects a legal action by floor(word * menu length / 2^32). At the first visit to each registered site before first sirens on the factual trajectory, hold the complete prefix state fixed and enumerate every legal player action. Force that action, execute the actual selected reaction, and replay subsequent choices using the same words at the same absolute decision index. After routes diverge, the same word may select a different semantic action. Thus the result is a total intervention under a specified stochastic-policy coupling, not an intervention holding downstream actions or states fixed.

Registered sites and investigation choices:
- Pink's ambush theory: option 0 (recount timeline), compared with options 1 and 2.
- Cadillac trunk: option 2 (inspect radio), compared with options 0 and 1.
- Eddie and Blonde's story: options 1 and 2 (audit/review requests), compared with option 0.

Each reached factual prefix gets one unit of weight; take the mean over its investigation options minus the mean over alternatives. Review's two options do not double its weight. The comparison is within each world, conditional on its reached prefixes. The worlds share policy words and have identical aggregate site counts here, but prefix states need not be identical across worlds; a difference between within-world contrasts is descriptive rather than a cross-world mediation estimate.

At the first sirens state, enumerate every action and all descendants to horizon H=1 or H=3. A winning action has at least one continuation ending at the secret truce by the horizon. H=3 is existential full-state reachability, not a guarantee for an observer with limited information or a learned reasoner. Separately retain actual terminal outcome under the coupled random suffix. If no sirens state is reached, the reachability indicators are zero; all evaluated arms reach it in this run. Check factual suffix replay against the unmodified campaign ending, first-sirens reachability and ledger, completion and length. Inspect the one-step squared substantive goal-gate distance, effect energy and first reaction/destination switches. For controlled deletion at sirens, zero all three ledger values while retaining the rest of the numeric state and history.

## 2. Executed matched-choice results

Across both worlds and two cohorts: 512 factual campaign replays, 1,130 reached first-visit decision prefixes, 3,390 action arms (including factual-action controls), 2,260 non-factual swaps, 110,375 bounded reachability node visits, 1,130 successful factual suffix replay checks. All arms reach sirens and complete. Counts share campaigns and deterministic sources; they are not independent statistical trials.

| Site | Reached prefixes per world | Original H1 difference | Candidate H1 difference | Original H3 difference | Candidate H3 difference |
|---|---:|---:|---:|---:|---:|
| Timeline | 132 | +7.95 pp | +43.56 pp | +12.50 pp | +39.77 pp |
| Radio | 240 | -9.38 pp | +1.04 pp | -13.75 pp | -3.54 pp |
| Review | 193 | +3.11 pp | +13.73 pp | +11.66 pp | +17.36 pp |

The candidate's unique immediate truce-success differences are +23.86, +10.21, and +8.55 pp respectively (all zero for original). Among the candidate's pairwise investigation-vs-other comparisons, gains/losses in unique truce are 64/1 over 264 timeline pairs, 52/3 over 480 radio pairs, 33/0 over 386 review pairs. After all-record deletion at sirens these gain/loss contrasts are zero across all pairs. The original and candidate actual random-policy secret ending counts are 26/256 and 41/256; first-sirens immediate opportunity counts 15 and 36, H3 counts 26 and 44, unique truce 0 and 11. All 11 factual candidate unique truce states lose that distinction under deletion. These are finite observed interventions.

The radio investigation improves truce-specific choice discrimination while remaining adverse for broad H3 reachability under the sampled suffix policy. Its original mean change in squared substantive gate distance at reached sirens pairs is +.01619; candidate -.002329. A positive gate-distance improvement can coexist with a negative terminal-reachability contrast because the intervention also changes reaction/route selection, later histories and relative encounter priorities. This makes it a valuable authoring diagnostic. No claim that the radio observation provides verified guilt or makes the narrative better.

## 3. Joint policy factorial: causal apportionment

A supplementary public 64-campaign seed (0x53521431) is disjoint from the above seeds. For each campaign evaluate all eight dynamic intervention assignments, with bit 0 timeline (off option 2, on option 0), bit 1 radio (off 1, on 2), bit 2 review (off 0, on 2). Override the first reached site before first sirens; if the scene is skipped, the policy has no action there. Use common absolute-index policy words for the remainder. No unavailable intervention actions observed. This differs from single-site comparisons averaged across every alternative. The off policies are specific alternatives. Not all three scenes are reached on every campaign: in the all-on arm timeline 29/64, radio 64/64, review 51/64. These are policy assignments, not three completed investigative acts per campaign.

512 rollouts in each world, 1,024 in total, and 27,681 reachability node visits. All reach sirens and terminate.

| Metric | Original all-off | Original all-on | Candidate all-off | Candidate all-on |
|---|---:|---:|---:|---:|
| H1 target attainable | 12/64 | 0/64 | 12/64 | 28/64 |
| H3 target attainable | 15/64 | 0/64 | 15/64 | 28/64 |
| Unique truce | 0/64 | 0/64 | 0/64 | 23/64 |
| Random-policy target ending | 13/64 | 1/64 | 13/64 | 20/64 |

For a fixed exogenous stream define f(S) as the potential outcome under the policy mask S. The discrete interaction coefficients are the Möbius transform
    d(S)=sum_{A subseteq S} (-1)^(|S|-|A|) f(A).
Then f(S)=sum_{A subseteq S} d(A). For exact apportionment allocate each nonempty interaction equally to its member choices:
    phi_i=sum_{S containing i} d(S)/|S|.
This is Shapley attribution for the defined finite policy-mask game, not the unique causal mechanism or a norm on state-space displacements. Average over the 64 common streams; use integer sixth-units and check efficiency on every stream and outcome. Five outcomes times 64 streams per world yield 640 efficiency checks. Aggregate dividends agree with the direct transform of the aggregate table.

Candidate unique-truce dividends (success counts out of 64): timeline+radio 6, timeline+review 7, radio+review 0, triple 10; all individual terms and intercept zero. They sum to 23. Exact per-choice Shapley sixth-units [59,38,41], divided by 6*64 to obtain percentage-point contributions [15.3646,9.8958,10.6771]. All 23 all-on unique successes disappear when the three ledger values are deleted at the resulting sirens states. The same controlled deletion yields zero unique-truce outcomes for all eight candidate masks. Thus the causal readout depends on the constructed evidence ledger; this does not establish natural indirect effects of the earlier choices or narrative warrant.

For broader H3 reachability the candidate Shapley contributions are +21.3542, -15.3646, +14.3229 pp, summing to +20.3125 pp. Timeline+review with radio off yields 29/64 H3 opportunities, the best of the eight tested masks, while all-on yields 28/64. The radio policy's negative H3 attribution and positive unique-truce attribution are precisely the distinction between making the target achievable and making one action uniquely consequential. Avoid selecting a new candidate on this public factorial; it is a diagnostic of the already frozen world.

## 4. Authoring implications

A geometry-only or local priority metric misses interactions introduced by path-dependent evidence. Add paired upstream interventions, finite-horizon choice availability, and policy-specific interaction attribution as independent authoring checks. Distinguish the squared step displacement energy from the policy-game dividends; they have different units and interpretations. Require provenance and narrative support for evidence, a sufficiently discriminating goal, and task-specific utility. The present candidate remains a failed SRG-13 promotion. The control policies, seeds, horizons, binary utility and attribution method are choices in this research turn, not independent pre-registration, real player behavior or hidden evaluation. No actual model inference, new training, Lean verification or production editor modification.

## 5. Reproduce

The source functions executed in an isolated ECMAScript runtime using pinned connector-fetched files. The standalone replay wrapper checks the receipt blobs and source blobs and compares the selected cohort or factorial receipt. Standalone Node file execution has not occurred. Run from the EvalMath root:
    node integrations/sweepweave-ts/srg14/verify.mjs original_a
    node integrations/sweepweave-ts/srg14/verify.mjs original_b
    node integrations/sweepweave-ts/srg14/verify.mjs candidate_a
    node integrations/sweepweave-ts/srg14/verify.mjs candidate_b
    node integrations/sweepweave-ts/srg14/verify.mjs factorial

The summary is output/evaluation_storyworld_reasoning/srg14.json; the four cohort receipts and factorial receipt contain the detailed counts. Original and candidate sources remain unchanged. No Godot dependency.

Next: construct an action-specific radio authoring proposal with an independently reviewed evidence meaning, and verify that correcting the adverse radio policy does not flatten the final choice. Use a new development/validation contract and fresh seeds; do not optimize on this diagnostic as a held-out test. Then add matched model-facing observation packets and a separate partial-information policy oracle to measure history-dependent compact reasoner performance.

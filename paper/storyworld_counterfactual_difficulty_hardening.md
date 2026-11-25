# SRG-AC05: Difficulty hardening through reachable history rather than terminal perturbation

2026-11-25. Registered public experiment at 96b0f0dbbc93a004400b6b832a4b7ed003a27856. Frozen selection at b43a262ddc3f37460e7a3d1840a9429c65bbd62c before fresh evaluation. The SRG-13 candidate remains unchanged and unpromoted. No paid compute, actual model inference, independent private evaluation, Lean certification or production editor changes. Source-level execution in an isolated ECMAScript runtime; standalone Node replay pending.

## 1. Contract

AC04 showed that on the fixed AC03 upstream policy, the presence of a review request, plus the page, turn, menu and suffix history, suffices for the fitted policy to reach the sampled full-state utility ceiling. The test here asks whether a context-dependent reaction effect can increase the attainable information gap while preserving opportunities.

Let L be White's Crew_Loyalty, z the original signed NUDGE amount, x one of Pink's Rat_Suspicion or Blonde's Sadistic_Escalation, and t the existing public Timeline_Record. For one selected option (flight or truce), in each of its three reactions replace the loyalty NUDGE amount by

    z' = z + c*x*min(1,8*t)
    L' = clamp(L*(1-|z'|)+z',-1,1).

The six nonzero coefficients are +/- .04,.08,.12. Two actions, two features, six coefficients and the unchanged control give 25 candidates. No new coordinates, reaction scores, gates, prose, priorities, destinations or other effect ASTs. All original later ordered writes must be replayed on the edited intermediate state. Both signs are provisional design hypotheses. The source's generic final reaction prose does not establish author-approved semantic warrant. The multiplier forces the extra term to zero in the absence of the timeline record; optimized-upstream development roots all have the record, so zero-warrant replay coverage is zero and the algebraic guard is not an empirical zero-warrant test.

Use two public 48-tape development cohorts (seeds 0x53522501/02) and two fresh 96-tape cohorts (0x53522511/12). Fix the AC03 upstream policy (0,0,1,2). Every unforced decision uses the same absolute-index word coupling. At first sirens, enumerate the actual H=3 action tree, binary terminal secret-ending reward. Oracle groups roots and successor states by public observation, retaining action/observation history in the suffix. Channels are menu only, weak (menu plus review presence), ledger (menu plus three exact record values), goal4 (ledger plus 4-bit quantization of suspicion, escalation and loyalty), and all public coordinates. Page, turn, status and legal ordered IDs/text are included; prefix history and encounter/reaction prose are excluded from the declared channels. All suffix policies are finite empirical oracles, not population Bayes optima. The full-state ceiling is computed per root. Verify nested oracle utilities and self-rollout; use frozen calibration lookup with menu and first-legal fallbacks on fresh fixed-upstream roots. Fixed sequence controls enumerate 64 action-rank scripts. The primary difficulty metric is goal4 minus weak optimal attainable successes, together with strict opposite-optimum pairs in the same weak root cell.

Hard guards preserve coverage, selected reaction identity, unchanged actions, ordered downstream effects, max coordinate adjustment .12, same-root selected step energy ratio 1.35, prefix-plus-step energy concentration increase .025, informative root count, full-state ceiling and paired H3 losses within floor(n/24), and goal4 at least 95% of full-state. Ranking fixed before execution. Hardening requires a positive gap of at least max(2,ceil(.05*full)) and one strict reversal pair in both cohorts; otherwise freeze unchanged. The energy measure uses raw unit-weight BNumber coordinates, and the loss budget and information threshold are chosen experimental tradeoffs rather than author approval.

## 2. Formula search fails

All 25 candidates have gap zero and no strict reversal in both development cohorts. Nineteen, including the unchanged control, pass every preservation guard. The remaining six lose informative opportunities; some lose more full-state utility than permitted. The largest observed coordinate adjustment is .0384398094; largest selected-step energy ratio 1.2533954365; largest increase in concentration .0039823271. All 7,200 immediate scope comparisons and 13,824 independent ordered-write checks pass. All trees compile and execute with no invalid roots. The original formula is frozen. The result concerns this bounded one-effect family, not an impossibility for other edits.

| Fixed upstream, count | Development A | Development B | Fresh A | Fresh B |
|---|---:|---:|---:|---:|
| Roots | 48 | 48 | 96 | 96 |
| Full H3 | 40 | 43 | 90 | 90 |
| Menu oracle | 37 | 35 | 80 | 83 |
| Weak oracle | 40 | 43 | 90 | 90 |
| Ledger / goal4 oracle | 40 | 43 | 90 | 90 |
| Informative roots | 20 | 36 | 62 | 60 |
| Strict weak reversal pairs | 0 | 0 | 0 | 0 |

The frozen weak lookup from both development cohorts succeeds on 90/96 in each fresh cohort (180/180 attainable successes). Ledger and goal4 transfers also achieve 180, whereas exact-public lookup achieves 83+78=161. This is a transfer property of the finite lookup, not evidence that more public information harms the optimal policy. The preservation checks pass for unchanged replay; the hardening criterion fails. No candidate promotion and no retuning.

## 3. Existing legal histories already contain difficulty

The registered separate mixed population includes equal mass from default, all-investigate and optimized upstream policies on each tape. This changes the reachable-state distribution without modifying any SWMD formula. Three arms share each tape; root multiplicities remain in this primary diagnostic. Full-state strict root optima are compared within identical weak observations; two roots in a pair have unique but different winning action IDs. The shared page, time, menu and review-presence bit are verified, and receipts retain legal action/reaction histories and public context. Such pairs need not differ in only one coordinate and establish an observational information conflict, not an isolated causal intervention.

| Mixed population | Dev A | Dev B | Fresh A | Fresh B |
|---|---:|---:|---:|---:|
| Roots | 144 | 144 | 288 | 288 |
| Full-state oracle | 76 | 78 | 160 | 160 |
| Menu oracle | 71 | 66 | 140 | 140 |
| Review presence oracle | 74 | 69 | 149 | 152 |
| Full ledger oracle | 76 | 78 | 159 | 160 |
| Goal4 oracle | 76 | 78 | 160 | 160 |
| Best fixed sequence | see receipt | see receipt | 139 | 140 |
| Strict opposite-optimum pairs | 6 | 28 | 81 | 51 |

On fresh mixed roots, richer goal4 recovers 19 successes beyond weak (320 vs 301); the gap is 5.9375% of attainable full-state utility. Ledger recovers 18 of 19. The 132 strict pairs are not independent, because multiple pairs can reuse the same history and the three policies share tapes. Unlike the frozen-upstream population, the mixed population breaks the one-bit shortcut using the existing formulas. This is a cohort-fitted oracle, not a reported mixed-population frozen-policy transfer result.

For example, in fresh cohort A, two default-policy histories both reach first sirens at turn 12, with all three actions available and review value .0625. One has radio record .125 and timeline zero; the other has both zero. Their exact H3 vectors in action order are (0,0,1) and (0,1,0). Other public coordinates and histories also differ. The weak observer must choose a common first action even with arbitrary suffix planning. The full ledger distinguishes these two histories. This is a replayable information-loss witness, with no invented state, action or ending.

## 4. Post-hoc disjoint balanced witness extraction

The raw reversal pair count can exaggerate coverage. After primary evaluation, rerun all four mixed cohorts, deduplicate exact action/reaction histories within each cohort, verify duplicated histories have identical full state and action values, and partition unique-optimum roots by their weak projection. Within a weak cell with label group sizes n_a, maximum disjoint opposite-label pairs is

    min(floor(N/2), N-max_a n_a).

Pair two largest remaining label buckets deterministically, verifying the maximum count in every cell. Histories are used at most once per cohort. No claim of independence across cohorts or across tapes. The resulting balanced conditional population has two equally weighted strict roots per pair. All roots have attainable utility 1; any weak-observation policy must lose at least one root per pair, whatever its suffix computation. Because each action label appears on some pair endpoints and a global weak-cell policy need not win exactly one on every pair, a 50% upper bound is automatic, whereas attainment of that upper bound needs verification. The replayed exact weak oracle attains it in each cohort. Ledger, goal4 and public oracles attain 100% on these extracted populations; all paired roots have different full ledger projections. The pair extraction is post-hoc on the registered tapes, not an unbiased population frequency or independent test.

| Cohort | Raw roots | Distinct legal histories | Disjoint pairs | Weak oracle | Ledger oracle | Full oracle |
|---|---:|---:|---:|---:|---:|---:|
| Dev A | 144 | 138 | 2 | 2/4 | 4/4 | 4/4 |
| Dev B | 144 | 135 | 6 | 6/12 | 12/12 | 12/12 |
| Fresh A | 288 | 271 | 9 | 9/18 | 18/18 | 18/18 |
| Fresh B | 288 | 273 | 4 | 4/8 | 8/8 | 8/8 |

This is a practical matched-history authoring certificate: preserve the original narrative affordances and use a balanced evaluation distribution containing real information conflicts. The selected pairs do not establish that ledger reasoning is intrinsically computationally hard, or that a reasoner requires all three ledger variables. They only establish that the specified weaker channel cannot achieve full success on these witnesses. A future registered replication can freeze a history-generation and pair-selection rule, and then audit minimum sufficient ledger subsets, transfer, actual compact-model inference, and narrative fidelity on privately selected histories. Do not present the post-hoc pair set as an independently held-out benchmark.

## 5. Verification and limitations

Development: 3,666 prefix and 60,016 suffix transitions, 62,800 suffix nodes; fresh validation/refit: 10,247 prefix and 21,621 suffix transitions, 22,677 nodes; post-hoc pair audit: 8,293 prefix and 18,076 suffix transitions, 18,940 nodes. Total 121,919 executed transitions, including repeated branches and deterministic replays. All oracle replay, action legality, channel nesting, formula scope and pair invariants pass. The CLI pins original runtime/world Git blobs. Standalone Node execution remains pending; the core source and actual runtime were executed through isolated ECMAScript. No edits to existing worlds or production SWMD editor. No author-approved difficulty or effect-size threshold. The original SRG-13 candidate remains unpromoted.

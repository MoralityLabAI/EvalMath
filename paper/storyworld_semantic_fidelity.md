# SRG-02: Semantic fidelity and authored-world reasoning geometry

2026-11-25. Evidence: algebraic inequalities, exhaustive finite route-tree audit, and paired numerical replay on a pinned authored campaign. Not a model benchmark, a native Godot conformance test, or a proof of real-world geopolitical effects.

## 1. Freeze the transition semantics before judging a world

Pinned GPTStoryworld revision ee1c6918db77d1e0924877f59eca819bae3f1c8c; SweepWeave TS revision 52e8b446592639eb3a63f7824fc6edc5af9be7f1.

- [NudgeOperator.ts](https://github.com/MoralityLabAI/sweepweave-ts/blob/52e8b446592639eb3a63f7824fc6edc5af9be7f1/src/NudgeOperator.ts): N(x,a)=x(1-|a|)+a.
- [Rehearsal](https://github.com/MoralityLabAI/GPTStoryworld/blob/ee1c6918db77d1e0924877f59eca819bae3f1c8c/codex-skills/storyworld-building/scripts/monte_carlo_rehearsal.py): A(x,a)=clip[-1,1](x+a). Its pointer resolution also retains only keyring[0], starts from an empty state, and selects the first strictly best desirability. It is a restricted rehearsal, not a gold observer-owned belief interpreter.
- [scriptAst.ts](https://github.com/MoralityLabAI/sweepweave-ts/blob/52e8b446592639eb3a63f7824fc6edc5af9be7f1/src/scriptAst.ts): clamp[0,1](x(1-a)+a); a different normalized-domain AST, whose negative-nudge semantics do not equal N.
- [TSUN controller](https://github.com/MoralityLabAI/GPTStoryworld/blob/ee1c6918db77d1e0924877f59eca819bae3f1c8c/storyworlds/tsun01b_last_train_home/tsun01b_env.py) implements the signed asymptotic update with rounding to four decimals. 
- [Balance of Reason browser engine](https://github.com/MoralityLabAI/GPTStoryworld/blob/ee1c6918db77d1e0924877f59eca819bae3f1c8c/storyworlds/balance_of_reason/engine.mjs) actually adds clipped deltas to its 16 national and 11 faction coordinates, despite its opening comment mentioning native Nudge. Its [native compiler](https://github.com/MoralityLabAI/GPTStoryworld/blob/ee1c6918db77d1e0924877f59eca819bae3f1c8c/storyworlds/balance_of_reason/build_sweepweave.mjs) emits Nudge ASTs.

For x,a in [-1,1], signed N lies in [-1,1]. Clipping onto this interval is 1-Lipschitz. Thus |N(x,a)-A(x,a)| <= |a*x|. More generally if the same exogenous a is applied to two trajectories with old values x (signed) and y (additive),
    |N(x,a)-A(y,a)| <= (1-|a|)|x-y| + |a*y|.
Proof: insert N(y,a), apply the affine slope bound, then use the clipping inequality. This is an algebraic bound for fixed amounts on a shared event sequence. If reactions, gates or later amounts diverge, restart the bound at the first disagreement; a closed-loop guarantee requires additional continuity and branch-margin assumptions.

For a fixed linear score contrast c(x)=v*x+b and perturbation vector e, |c(x+e)-c(x)| <= sum_j |v_j e_j|. A unique reaction whose pairwise margins all exceed the corresponding bounds retains its winner. The same strict-margin rule applies to linear ending thresholds. For a squared weighted metric gate around g, the exact change in squared distance is 2 sum_j w_j^2(x_j-g_j)e_j + sum_j w_j^2 e_j^2. These support guard-specific semantic portability checks. Neither geometric closeness nor aggregate random-ending balance establishes portability.

## 2. TSUN-01B: split narrative tone from mechanical reasoning

The pinned JSON has 13 encounters, 21 options and 42 reactions. Every option has exactly two tone variants with byte-equivalent parsed effect arrays and identical destinations. All 21 pairs include Care, Pride and Vulnerability in linear desirability. Vulnerability contributes the same coefficient to both sides; Care and Pride change the relative contrast. The formula audit found 234 reaction effect scripts, including six zero nudges. Each count includes duplicated tone variants.

Enumerate the controller's declared four-choice maximum tree before the postlude; the controller's option-level trait_deltas and flags determine the next scene, and the paired reactions have identical effects. Use signed nudges rounded to four decimals and evaluate the declared linear score contrasts on the resulting traits (binary64, tolerance 1e-10). This is a JS reconstruction of the inspected controller contract, not an invocation of Python or the Godot runtime. Across 22 reachable nonterminal path prefixes and 66 option/menu evaluations, none of the menus exhibited more than one winning tone set; the score coefficients still permit variation on the ambient cube. This is a reachability/support observation only. Tone is intentionally orthogonal to choice and protection in TSUN; changing the text while keeping the mechanics fixed is valuable for the persona/steering evaluation and should not be counted as mechanical reasoning depth.

45 terminal action paths are exhaustively enumerated. The uniform-legal policy takes each of three actions with probability 1/3, so probabilities are exact integer multiples of 1/81 (three-choice leaves carry numerator three; four-choice leaves carry one).
- Protection: 4/81; protection without any privacy breach: 1/81. The latter requires INSPECT_CARD, VERIFY_DISPATCH, COMMIT_ANNOUNCE, ANNOUNCE_MINIMAL.
- Both signed and clipped-additive clock replays pass every declared terminal clock gate. This gate therefore does not differentiate the two on these legal routes. The postlude, persona and coherence judges are out of scope.
- A fully informed legal policy can achieve the declared protection/no-privacy-breach objective. The cue/information oracle is not yet established: the authoring audit cannot infer human or model knowledge merely from prose and route IDs.

This fixture illustrates why a density reward can mislead. Count effective mechanical reaction classes separately from narrative alternatives; common-mode terms and zero updates are flags for interpretation, not automatic authoring defects. A purposeful persona axis can be inactive in the welfare task while relevant to the speech task.

## 3. Balance of Reason: paired live browser-rule replay

Read source_cards.json and the actual dependency-free engine.mjs at the pinned revision. Evaluate the source in an isolated JS runtime after inspecting the code. Substitute only the 16 clipped-addition assignments in apply (including the faction standing update) with signed Nudge. Preserve other code, including catastrophic direct assignments, source weights, guards, thresholds, chooser indices and ending scorer. This is a sensitivity mutant, not a native engine port. All coordinates receive unit metric weights for the descriptive squared-energy calculation.

128 deterministic pseudo-random action-index sequences (LCG seed 0x53524702, 95 actions available per sequence) are replayed in each engine. Same index does not guarantee the same semantic action after paths diverge. Separately, at every visited original-engine state, evaluate each legal action in both engines from a copy of exactly the same pre-state. These two designs answer different questions.

Observed:
- 118/128 paired campaigns finish at different ending IDs, 73/128 finish at different turn counts.
- 30,234 matched same-state/action transitions; all differ numerically at tolerance 1e-12. 92 differ in immediate route tuple (year, scene, phase, ending).
- Largest coordinate discrepancy across those transitions: 0.3528. The first route disagreement was trial 1 (zero-indexed), turn 83, final assembly, action 0: red_mihna vs unsettled_mandate.
- Total unit-weight squared one-step energies summed over all same-state/action checks: 2859.43545489 original; 3312.56084744 signed mutant. At some states signed movement is larger because a nudge toward the opposite bound can span more than one unit of remaining distance. The sum is descriptive across this sampled pre-state distribution, not a measure of net progress or better balance.
- Original global_fire: 20/128; mutant global_fire: 0/128. Both produce global_fire under the always-index-1 policy, at turns 46 and 56 respectively. Zero under sampled random policies is not unreachability.
- Cold War Fatwas: 3 versus 55; Unsettled Mandate: 1 versus 33; Development Covenant: 22 versus 3; Council of Equals: 6 versus 14. Complete counts in the receipt.

These are finite paired observations, using JS binary64 arithmetic; no model calls or empirical generalization, no statistically independent transition claims, and no judgment as to which game design is preferable. The actual compiled native JSON was not available through the connector (empty content returned), so full browser/native parity remains open.

## 4. SRG authoring acceptance contract

For each world, freeze:
1. Author source hash, compiler/runtime revision, numeric domain, ordered write rules, legal actions, reaction and encounter tie rules, spool routing, and unsupported AST policy (fail closed).
2. Observer-owned exact keyrings and pre-decision cue provenance for decisive facts; specify whether a displayed number is rounded and whether exact gate arithmetic is accessible. Separate public/hidden/post-decision fields.
3. Mechanical and narrative reaction classes. For each formula report observed winner sets, score-contrast support, feasible interventions, and consequential successor or continuation-value changes. Keep untested variables unidentified.
4. Per-act effect norm, gate slack before and after, terminal effect concentration, and terminal utility; audit why a major reversal is earned. Compare actual updates with a declared alternative interpretation on matched states. Retain task-relevant subspace and nuisance padding controls.
5. Separate oracle information bounds from computation and memory burden. Require causal repairs (sign correction, appropriate input, scaled effect, evidence access) to pass on sealed matched worlds with known counterfactual behavior.

Proposed SRG-03: independent native runtime exporter with exact pre/post-state and full legal action/reaction menus; pin runtime and source, compare every decision-relevant guard and outcome across implementations, then implement a small finite sequential belief-state Bellman oracle and an authoring mutation gym. No production storyworld or simulator is changed by this PR.

## Reproduction

From EvalMath, with a separate GPTStoryworld checkout at the pinned revision:
    node scripts/verify_storyworld_srg02.mjs /path/to/GPTStoryworld output/evaluation_storyworld_reasoning/srg02.replay.json

The script checks all four source Git blob hashes before executing the pinned browser source. Compare parsed output to output/evaluation_storyworld_reasoning/srg02.json. The external checkout is required; this receipt is deliberately separate from the offline Python check_receipts registry. Connector-fetched source execution produced the committed receipt; standalone Node replay and independent Python/controller parity were not run in this turn. 

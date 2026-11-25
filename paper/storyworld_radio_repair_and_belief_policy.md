# SRG-15: Radio-effect repair and an observation-history policy oracle

2026-11-25. Evidence: finite source-executed numerical controls, frozen public validation, exact finite empirical belief-policy computation. No model inference, independent private evaluation, production TypeScript editor change, or Lean claim. Radio repair promotion FAIL. The frozen SRG-13 candidate remains unpromoted.

## 1. Narrow causal repair

SRG-14 found the radio choice improves unique-truce discrimination but harms three-action attainability under the coupled random suffix. Start from the frozen SRG-13 candidate. Edit only two existing effect coefficients in rxn_page_cadillac_trunk_2_0, the reaction whose prose describes actual radio inspection. Its result concerns exposure, not proof of a culprit. Let t=min(1,8*Timeline_Record), S=Pink suspicion, B=Blonde escalation. At this reaction the candidate originally writes
    B' = NUDGE(B,.11+.08*S)
    S' = clip(S-.05+.06*B',-.95,.95).
A proposed retention parameter alpha and restraint beta change these to
    B' = NUDGE(B,.11+.08*S-beta*t)
    S' = clip(S-.05+alpha*t+.06*B',-.95,.95).
Original order and bounded semantics are preserved. Alpha tests conditional preservation of earlier unresolved suspicion; beta is a provisional cooperation/restraint hypothesis requiring author review, since existing dialogue can support escalation instead. Both vanish at zero timeline credit. No fabricated proof of identity, new coordinate, extra write, gate/route/prose/score change. The existing downstream p2Value write depends on B': NUDGE(old p2,-.07+.05*B'). The initial verifier rejected this downstream change; correcting its read-dependency contract independently checks all three numerical outputs, while requiring all other selected successor coordinates to agree exactly.

Grid alpha in {0,.04,.08,.12}, beta in {0,.04,.08}, 12 candidates. Reused inspected public SRG-14 seeds 0x53521411/12, first 96 campaigns each, reach 90 and 88 first-radio prefixes. At each fixed reached prefix force each of the three legal choices and continue with same absolute-index policy words, as in SRG-14. Compute H1/H3 existential reachability at first sirens and actual random-policy outcome. Give each prefix weight one, radio inspection minus the mean of two alternatives. Recompute horizon audits in every candidate. Optimization reuses only deterministic selected suffixes whose baseline path never uses the modified reaction with positive timeline credit; otherwise execute candidate suffix anew. Invariant follows by induction until the first changed transition. The initial combined run timed out before writing results; split-cohort execution completed the full grid.

Hard constraints on each cohort: nonnegative H3 contrast and random-goal contrast; unique-truce contrast at least .05; max immediate same-state numerical adjustment .12; max immediate selected-step energy ratio 1.75; all forced arms complete and reach sirens. Selection maximizes full cohorts then passed constraints, then discrete edit cost. These parameters and cohorts are research choices, not independently timestamped preregistration.

All 12 fail the complete development contract. Frozen diagnostic selection alpha=0,beta=.04, with no full cohort and 11/14 checks. This reduces the existing positive escalation increment conditional on earlier timeline record; it does not add a suspicion term. Development H3 contrasts: -1.11 -> 0 pp, -7.39 -> -5.11 pp; random-goal contrast remains negative in both. All immediate selected radio-inspection reactions are 2_0. Dependent p2Value changes on 32 development prefixes for the selected edit.

Fresh public validation seeds 0x53521511/12, 128 campaigns each, 123 reached radio prefixes each. Freeze before inspecting these results.
| Contrast, pp | Baseline cohort A | Edit cohort A | Baseline cohort B | Edit cohort B |
|---|---:|---:|---:|---:|
| H3 attainable | -5.28 | -3.66 | -1.22 | -.41 |
| Unique immediate truce | +10.98 | +11.79 | +16.67 | +18.29 |
| Random suffix goal | -8.54 | -4.47 | -2.85 | -3.66 |

Both validation cohorts fail H3 and random-goal constraints. The 738 forced action arms per world (246 prefixes times 3) all complete and reach sirens. The selected edit changes 57 immediate radio successors and 57 dependent p2 writes; 189 zero-warrant controls preserve the exact original successor. The 492 immediate non-target selected transitions remain numerically identical. Maximum coordinate adjustment .04, energy ratio <=1 (reported maximum initialized to 1), numerical formula error <=2.78e-17. Immediate reaction and destination unchanged; subsequent history may differ. No claim of global infeasibility outside the 12-point grid, nor a production repair. Leave SRG-13 frozen for the following policy diagnostic.

## 2. Exact observation-history policy

A full-state existential reachability oracle can overstate what a player can accomplish when numeric beliefs are hidden. SRG-15B uses the unchanged SRG-13 candidate and two new public 128-campaign cohorts (0x53521521/22). Retain the multiset of first-sirens states, each with mass one. The prefix policy selects legal actions by fixed xorshift32 words; all 256 campaigns reach sirens. Build the actual deterministic SWMD action tree to H=3 for each root, recording visible encounter, action menu and declared public values. There are 3,069 calibration and 3,434 validation tree node visits. The full-state comparator recursively maximizes each node independently. No source/formula edits.

Define observation channels:
- menu: visible page, title/prose, turn, status, action IDs/text, no numerical values;
- ledger: menu and exact three investigation records;
- goal2/4/8/exact: ledger and the three substantive goal coordinates, quantized to dyadic bins over [-1,1] or exact;
- public2/4/exact: ledger exact and all remaining public coordinates, quantized or exact;
- public_history: exact public coordinates and actual visible past encounter/action/reaction prose sequence.

Every channel is a projection of public runtime observations; the history arm assumes reaction prose is visible in the intended interface. The code checks every selected coordinate is public. Actual TS editor behavior is not independently tested. Every policy retains the projected observation-action history throughout the H-step rollout (including menus and turn). Quantization restricts numerical observation precision, not an architectural memory capacity. Public history is an explicitly chosen additional information channel. Different original semantic action IDs can be visible and informative. A deterministic world and full trajectory may permit reconstruction of hidden state by a reasoner familiar with the source.

For belief cell B of tree nodes with equal unit prior mass, write
    W_h(B) = max_a sum_o W_(h-1)({next(s,a):s in B, projection(next(s,a))=o}).
Terminal nodes contribute binary secret-ending payoff; unfinished leaves zero. Group initial roots and every successor by observed projection. Distinct prior histories never merge, so the same action is chosen for indistinguishable states throughout the policy, and no hidden-state continuation is supplied. An additional comparator gives first-action choice shared across an initial observation cell but privileged continuation; it upper-bounds the actual observation policy. The full-state per-root optimum is a further upper bound. Enumerated menus are checked identical in each belief cell. Replay every fitted empirical optimal policy against its own cohort, exactly matching the optimal numerator. Check nested observation-channel monotonicity. In this finite suite the privileged-continuation bound happens to equal the observation-policy value for every tested channel/horizon; no measured additional continuation gap. The algorithm nevertheless enforces the correct information restriction.

| H3 channel | Calibration optimum /128 | Validation optimum /128 | Validation frozen lookup /128 |
|---|---:|---:|---:|
| Menu | 17 | 16 | 9 |
| Ledger | 19 | 19 | 7 |
| Goal2 | 20 | 19 | 8 |
| Goal4 | 20 | 19 | 10 |
| Goal8 | 20 | 19 | 10 |
| Public exact | 20 | 19 | 9 |
| Public history | 20 | 19 | 9 |
| Full state | 20 | 19 | n/a |

For H1, validation menu optimum 12, all richer modes 14 and full-state 14. The finite validation ledger partition achieves full-state value, but calibration still loses one H3 opportunity. This is an empirical partition ceiling, not a global sufficient statistic theorem. The root-state prior is highly sparse and exact numerical values can separate nearly all sampled roots. Freeze each lookup table on calibration, evaluate the actual composed policy on validation; unseen history cells fall back to the calibration menu policy, then first legal action if also absent. On validation H3, menu has 6 root cells and no root lookup miss; goal4 112 root cells with 87/128 unseen root histories; exact public 126 cells with 120/128 unseen; public history 128 cells all unseen. Higher empirical information can fail to generalize with exact-match lookup. Calibration and validation are both public and share one world family. No independent population or learned model claim.

## 3. Policy scoring and the rare-goal accuracy trap

Export goal4/H3's 940 reachable observation-history decision cells, including off-policy continuations, one packet per unique history cell. Inputs contain projected observation, history of observations/actions, horizon and goal. They do not contain hidden states, state IDs or oracle action scores. Public gold carries the finite cell masses, action scores and tie sets. The complete policy is a table of submitted legal actions, composed along the actual 128 latent-root trees; missing/invalid/duplicate decisions stop the affected trajectory for zero utility. This is an offline policy-table rollout rather than a live model loop. The empirical oracle is a reference given the declared finite prior, which a model may not know or be able to derive from the projected prompt; the model-facing packets are diagnostic policy-estimation inputs, not universally specified closed-form Bayes questions. Supply the same source/rules familiarity protocol to every model and measure actual utility. Do not compare gold accuracy alone. Do not train on these public labels and call the same data a holdout.

| Score | Oracle | First legal action |
|---|---:|---:|
| All policy rows correct | 940/940 | 887/940 |
| Informative rows correct | 53/53 | 0/53 |
| Positive-optimum rows correct | 102/102 | 49/102 |
| Actual composed policy goal successes | 19/128 | 1/128 |

887 rows have all actions tied, of which 838 have zero attainable utility. Only 53 rows are action-discriminating. Count missing and rejected decisions as failures; the malformed test gives zero informative and positive accuracy and stops all 128 rollouts. An initial diagnostic counter returned nonfinite values on absent submissions; fixed Boolean validity conversion and reran the regression. Sum first-action regret over all enumerated cells separately from trajectory success because off-policy cells overlap in campaign ancestry. The 940 rows are not independent samples. The oracle and first-legal controls are real executions of the scorer, not model inference.

The policy scorer and local stage use pinned source/data hashes. The existing SRG-08 local planning runner can answer the rows. Actual Bonsai/Inky/Data Goblin model inference has not been performed. Use model_input/ only; keep verifier/ outside prompts. The source rules are public and may be provided separately, with consistent context and compute budgets. No new training material exported.

## 4. Reproduction and next gate

From EvalMath root (Node 20+):
    node integrations/sweepweave-ts/srg15/verify.mjs radio_a
    node integrations/sweepweave-ts/srg15/verify.mjs radio_b
    node integrations/sweepweave-ts/srg15/verify.mjs radio_validation
    node integrations/sweepweave-ts/srg15/verify.mjs belief

The committed source functions and scorer were executed in isolated ECMAScript with connector-fetched blobs. Standalone filesystem/HTTP CLI replay and production editor integration remain pending. The SRG-13 candidate and original authored world are unchanged. The radio edit is a rejected diagnostic fixture. No Godot dependency.

Next: diagnose the radio action's adverse *route-mediated* effect with controlled route and effect interventions, then register an author-reviewed alternative to the radio's coercive continuation. For model evaluation, prioritize actual policy rollout success, informative-cell utility, outcome-balanced sampling by predeclared prior, and a matched low-precision/generalization curriculum. Add independent worlds and frozen local compact-model runs before interpreting the oracle ceiling as a learned capability.

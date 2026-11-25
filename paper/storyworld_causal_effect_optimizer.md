# SRG-12: Bounded action-specific effects and upstream goal-gate diagnosis

2026-11-25. Evidence: executed deterministic source-level finite search, matched counterfactual branch evaluation and fresh-seed public validation. No model inference, native TypeScript editor integration, independently sealed validation, or Lean certificate. Promotion FAIL.

## Contract and scope

Use the original Reservoir Dogs SWMD-SRG/2 migration and its explicit direct-routing semantics. The target is the authored secret truce ending; its substantive numeric acceptability region is loyalty L in [-.53,.77], Pink suspicion S >= .08, Blonde sadistic escalation B <= .35. The separate clock gate remains intact. Define squared unit-weight distance to the substantive box:
    d_g^2 = (L - clip(L,-.53,.77))^2 + max(0,.08-S)^2 + max(0,B-.35)^2.
These coordinates and the choice of target are task-specific; no moral/narrative utility is inferred. The explicit authoring hypothesis is that the truce choice should account for at least half of unique secret-ending opportunities, where a unique opportunity means exactly one legal action immediately enters that ending. No target-frequency optimization alone establishes dramatic merit.

The original truce option at sirens updates clock, loyalty, leverage and belief coordinates, but neither S nor B. Its three reactions differ in score and ordered existing effects. Preserve original effects and append only bounded changes on those two existing traits, conditioned on positive prior S. With alpha recognition and beta restraint:
    a = min(.12, alpha max(0,S_pre))
    b = -min(.12, beta max(0,S_pre)) max(0,B_post)
    B' = NUDGE(B_post,b)
    S' = NUDGE(S_post,a)
where NUDGE(x,a)=x(1-|a|)+a. Apply B before S so both use the original suspicion. For the two positive-loyalty reactions append +gamma*S_pre to desirability; for the negative-loyalty reaction append -gamma*S_pre. Optional bias delta adds to the secret ending's existing priority constant. This is a proposed numerical causal mechanism: the truce is permitted to reinforce existing suspicion and restrain positive escalation. The narrative does not independently validate the semantic mechanism. The edit does not create suspicion from zero or negative S, add an event shortcut, introduce a new coordinate, change destinations, or relax a gate. Actual numerical gate admission may change as a consequence of the new effects.

Grid delta in {0,.025,.05,.075,.1,.125}; alpha,beta each in {0,.25,.5,.75}; gamma in {0,.1,.2}, total 288. The first three development cohorts reuse inspected SRG-11 seeds, 128 campaigns each. Two fresh public validation seeds, 0x53521211 and 0x53521212, have 192 campaigns each. Parameters, targets and seeds were chosen in this turn, not independently timestamped or hidden. Selection is completed before the new validation evaluation. Hard per-cohort checks: 12.5-20% opportunity; >=70% unique among opportunities; >=50% unique-truce share among unique opportunities; <=20% of target-winning actions with route priority margin <.03; <=10% non-goal route changes relative to the number of truce actions; max added coordinate displacement <=.12; max truce selected step energy ratio <=1.75; max goal-distance increase relative to the original selected transition <=.025 and nondecreasing mean goal progress. Score grid by number of fully passing cohorts, number of satisfied checks, then discrete edit distance and deterministic tie break. Infeasible candidate is diagnostic only.

## Search result

0/288 candidates satisfy every development constraint. None achieves the unique-truce share threshold in all three development cohorts. Across all 288 candidates, the counts satisfying each individual condition across the three cohorts are: opportunity 72, uniqueness 12, unique-truce share 0, margin 12, scope 247, displacement/energy/progress each 288. The maximin unique-truce share among nonzero causal edits is just 1/9 (11.1%) across cohorts, obtained by delta=.125 and alpha=.75; it fails uniqueness and other constraints. The best maximin goal-progress arm (alpha=.75, beta=.5, no other change) improves mean squared gate-distance progress by only .000135-.000195 per truce action and fails opportunity/discrimination constraints. Neither diagnostic arm is a promotion candidate.

The ranker falls back to a Q-only edit, delta=.075, alpha=beta=gamma=0, the same bias as SRG-11. It passes zero full development cohorts. Preserve this fact; the search did not discover a useful reaction/effect edit. Fresh validation:
| Cohort | Baseline opportunities | Candidate opportunities | Unique candidate | Unique truce |
|---|---:|---:|---:|---:|
| 0x53521211 | 19/192 | 32/192 | 21/32 | 0/21 |
| 0x53521212 | 16/192 | 29/192 | 18/29 | 0/18 |

All 384 baseline and candidate campaigns complete; secret endings 48 -> 73, 25 changed endings, no changed pre-first-sirens prefixes. The frozen candidate still fails both uniqueness checks and unique-truce share. No promotion. Compare matched actions, not human player frequencies.

The selected compiled candidate was verified on 1,152 development and 1,152 validation action instances, including all three forced reaction branches per action. Source-executed comparisons agree with the independent cached numeric evaluator and preserve all non-truce numeric successors, scores and writes. Max numerical state discrepancy zero, max score discrepancy about 1.11e-16 from binary64 association. The selected candidate has only one Q line change. Post-selection diagnostics compile six nonzero edit arms (including single-factor and combined effects) and verify 6,912 selected action instances and 20,736 forced eligible branches on the reused development states. Reaction-only gamma=.1 changes 56/384 selected truce reactions and 21 routes, all 21 between non-target destinations. These are executed negative controls demonstrating that the score mechanism does change actual behavior. They were not retuned on validation. The combined alpha=beta=.25,gamma=.1 arm changes 28 routes, yields just one unique truce opportunity over 384 roots, and preserves the stated displacement/energy limits.

## Upstream causal opportunity audit

Replay the three development cohorts up to first sirens and enumerate all legal action instances at each reached prefix (13,047 action instances total). At each state compute spread max_a d_g^2(next_a)-min_a d_g^2(next_a) after actual selected reactions. This one-step local diagnostic uses the unit-weight substantive gate distance; it does not prove long-horizon causal mediation or narrative warrant.

At the first sirens state: 100/384 already satisfy all substantive numeric conditions (clock/route separate); 283 fail suspicion threshold, 13 fail restraint threshold, zero fail loyalty interval. Failures overlap. All 384 original selected truce action instances have zero substantive distance progress; all 1,152 legal actions at those roots yield the same substantive distance as each other. In these sampled states, loyalty changes remain inside its acceptable interval; S and B are unchanged.

The highest mean one-step action distance spreads occur in Pink's ambush theory (.03610 over 201 reached prefixes), Eddie and Blonde's story (.033784 over 279), and Cadillac trunk (.021663 over 359). They already write suspicion, and Cadillac also writes escalation. Orange on the ramp has much smaller spread (.00005672). This identifies the upstream edit surface for the next experiment. Many reached scenes have numerical changes yet zero goal-distance spread because they update irrelevant coordinates or remain inside a satisfied gate region. To balance causal effect budgets, evaluate signed goal-distance progress and action differences, alongside all-coordinate squared displacement energy and relative priority margin. A late priority shift cannot produce an earlier evidence history.

## Reproduction and limitations

Run from EvalMath root:
    node integrations/sweepweave-ts/srg12/verify.mjs
    node integrations/sweepweave-ts/srg12/upstream.mjs

Source blobs are pinned; the scripts reproduce the primary search and upstream audit. The post-selection nonzero-arm diagnostic receipt records the executed JS calculations; no standalone diagnostic CLI is supplied. All tests described above were performed using connector-fetched source in an isolated ECMAScript environment. Standalone Node replay, the TypeScript application build, independent private validation and model inference remain outstanding. Original storyworld and production editor remain unchanged; candidate is not approved for deployment.

SRG-13 should register an upstream evidence intervention on the three identified encounters, preserving the secret gate and checking that the final choice discriminates among causally warranted states. Separate provenance of suspicion from its magnitude, author-reviewed narrative evidence from score changes, and training roots from new validation. Prefer a feasible explicit path with distributed goal progress and a selective final action, before tuning rarity. No Godot dependency.

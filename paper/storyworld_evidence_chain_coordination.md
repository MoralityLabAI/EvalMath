# SRG-13: Investigation provenance and action-specific coordination in Reservoir Dogs

2026-11-25 | Executed finite source-level authoring optimization, matched counterfactuals and public fresh-seed validation. Overall promotion FAIL. The candidate is a research fixture, not an approved narrative revision. No language model inference, independent private test, production editor integration or Lean certificate.

## 1. Structural aliasing

Start from the original SRG/2 migration (blob cb174a3efb031eaa046b01a2acc526ef7d122345), with its explicit direct-route semantics. At each first sirens root, enumerate selected reactions for all three legal actions and their complete eligible wild candidate rankings. In all 384 reused SRG-11 development campaigns, the truce action's ordered candidate IDs, scores and creation indices exactly match at least one alternative action's ranking. Zero unique truce successes. Consequently any uniform secret-ending bias applied to identical candidate score vectors preserves this alias (conditional on unchanged eligibility and selected reactions). This is a local statement for sampled roots and exact identical vectors, not a theorem about every reachable world state. A global priority adjustment is insufficient to discriminate aliased actions.

## 2. Explicit evidence-chain design

Inspect the original Pink timeline, Cadillac radio, and Eddie/Blonde encounter option and reaction texts. Pink's first timeline reaction lists timestamps; another asserts an unverified accusation. Radio inspection concerns exposure, not proof of the rat's identity. Eddie's two review options request a powder-burn audit or timeline check, but their reactions reuse generic prose. The final truce's reactions also reuse generic prose. Therefore record *investigative work and requests*, not independently verified truth. The original narrative does not establish the proposed coordination effect; an author must review or improve the prose before deploying the mechanism.

Introduce four small public BNumber coordinates, initialized zero:
- char_pink.Timeline_Record
- char_pink.Radio_Record
- char_pink.Review_Request
- char_white.Truce_Coordination

An explicitly registered table maps 11 reaction IDs to an owner-specific record and strength. The update is max(old,credit), so replaying a reaction cannot mint additional credit. Strengths are .125 for enumerated timestamps and inspected radio, .0625 for an unverified accusation or radio inquiry without new conclusion, .03125 for a radio inquiry without an answer, .0625 for an audit request, .09375 for a timeline review request. These weights are chosen design parameters, not fitted probabilities.

The permitted existing-state edit is a bounded adjustment u to Pink suspicion updates: add u/2 to the original positive Nudge amount only on the timestamp-enumerating reaction, add u/2 to the original -0.09 additive suspicion change on the radio-inspection reaction (preserving suspicion rather than proving guilt), and add up to u to the late timeline-test reactions conditional on earlier timeline/radio record mass. The latter modifier is u*min(1,8*(timeline+radio)). It uses only earlier records, since the review record is a distinct coordinate. Remaining original effect order and write destinations are preserved. No changes to reaction scores, acceptability/visibility/performability gates, route links, original text, spools or time windows. The new record fields are public by design.

With normalized credits a,b,c (each record divided by .125), define coordination readiness
    r = .125 * min(1, s*(ab+ac+bc)/2).
The truce action writes this value in all three of its existing reactions; other sirens actions explicitly reset the coordination register to zero, including revisits. The secret-ending priority adds w*r and an optional constant offset d to the original priority. The original numerical eligibility gate remains intact. The pair products implement a minimum-two-source interaction: zero or one positive record yields zero extra coordination priority. The effect is bounded, has causal predecessors, and does not use a new hard ending gate or a forced route. It still constitutes a newly authored preference term and requires narrative validation; a coefficient can be too large relative to existing priorities even if its energy in chosen coordinate units is small.

## 3. Development search and frozen validation

Initial 20-point public exploratory grid (s=1,d=0) found no full-cohort feasible candidate. Before inspecting new validation seeds, expand grid:
    u in {0,.04,.08,.12}
    s in {1,2}
    w in {0,1,2,3,4}
    d in {-.15,-.10,-.05,0}
160 combinations. Three 128-campaign development cohorts reuse the inspected SRG-11 seeds. Freeze a design contract: 12.5-20% immediate target opportunity rate, >=70% unique winning action among opportunities, >=50% truce among unique opportunities, <=20% target-winning actions with priority gap below .03. Every uniquely winning truce must have at least two nonzero records. Existing-coordinate modification <=.12 against original same-state selected action, each new coordinate displacement <=.125, total selected step energy ratio <=2.5 against original same-state action at edited steps including sirens, additional priority boost <=.5. Unit-coordinate energy includes the new ledger dimensions; it is not invariant to state scaling. Scope check preserves original declarations, all original narrative, routes and gate ASTs, original reaction scores, and original ordered effect destinations. Selection lexicographically maximizes fully passing cohorts then passed individual constraints, then minimizes discrete edit cost and uses deterministic tie-break. The thresholds, exploration and seeds are public choices made in this turn, not independently timestamped preregistration.

All 160 candidates pass the individual warrant and three effect/scope budgets plus priority budget across development. Seven pass the opportunity criterion on every development cohort, 41 uniqueness, 30 truce share, 16 margin. None passes all criteria. The frozen diagnostic candidate is (u=.08,s=2,w=4,d=0), 23/27 individual checks, one fully passing development cohort. Compared with original 0/384 unique truce choices, it yields 18/384 (8,5,5). This is a useful causal mechanism but cannot pass promotion.

Validation on two distinct fresh xorshift32 seeds 0x53521311 and 0x53521312, 256 campaigns each, 24 pre-generated random words/campaign, floor(u*n) menu index. All roots are first sirens states. Candidate-dependent upstream transitions are actually executed; no claim that roots in the two worlds are identical. Check original selected reaction and numeric successor at the candidate's pre-state projected to original coordinates, and use that same-state original action for effect comparison. The priority term is evaluated after ordered effects. Compare cached ranking against compiled runtime for every selected action and verify readiness on all forced reactions.

| Metric | Validation 1 | Validation 2 |
|---|---:|---:|
| Opportunity roots | 35/256 | 29/256 |
| Unique among opportunity roots | 26/35 | 24/29 |
| Truce among unique | 20/26 | 17/24 |
| Low margin among target-winning actions | 7/46 | 2/35 |
| All constraints | PASS | FAIL (opportunity rate) |

The second rate .11328125 is below .125. No retuning on validation. Both cohorts pass choice discrimination, margin, warrant and energy constraints. All 512 baseline and 512 candidate campaigns terminate; secret endings 52 -> 82, descriptive of these fixed policy-index streams. All 1,536 validation action and 4,608 forced reaction checks pass with zero observed numerical or ranking discrepancies; development adds 1,152 and 3,456 respectively. The forced-branch check explicitly verifies readiness, not every possible forced-branch numerical effect. The candidate edits 21 original records and adds four declarations. Largest observed same-state existing-coordinate adjustment .08 (binary64 tolerance), max ledger step .125, max upstream energy ratio 1.6986247440, max final selected step ratio 1.8526330788, max added priority .5 on validation.

The aggregate added ledger-coordinate energy is distributed across the three recorded sources (validation 1: timeline .59375, radio 1.828125, review .8388671875; validation 2: .5625, 1.34375, .87890625). At selected edited upstream steps, compare squared substantive goal-distance to the original same-state successor. The timeline modification yields zero distance gain on sampled states (already inside the relevant gate region), while radio and review yield positive aggregate gains in both cohorts. This distinguishes record accumulation from distance-to-gate progress. It does not identify full-history causal mediation or proof that every clue is narratively warranted.

## 4. Causal record deletion

For every selected candidate validation root independently delete every subset of the three records before executing the truce action (eight cases per root, 4096 cases). Keep all other state, prior history and original numeric suspicion unchanged. These are ambient do-interventions, not all reachable story histories. Exact readiness formula matches every probe. In 3762 probes with fewer than two nonzero records, coordination is zero. Removing all records eliminates all 37 observed uniquely winning truce outcomes (20 and 17). Individually deleting timeline, radio, review eliminates 14,14,16 of those successes respectively; counts overlap. The intervention checks the causal effect of the new records at the final decision, not a proof that their narrative sources are truthful or that removing an earlier action would leave other state unchanged. The original goal gate is still required. At zero records, the coordination bonus is identically zero. No outcome-frequency target is allowed to override the original gate.

## 5. Reproduction and author review

See integrations/sweepweave-ts/srg13/optimizer.mjs and fixtures. From EvalMath root:
    node integrations/sweepweave-ts/srg13/verify.mjs development
    node integrations/sweepweave-ts/srg13/verify.mjs validation0
    node integrations/sweepweave-ts/srg13/verify.mjs validation1

The primary receipt is output/evaluation_storyworld_reasoning/srg13.json. It pins the source blobs, retains full selected-cohort metrics and compact all-grid constraint counters. The original combined isolated-runtime execution wrote the artifacts before a connector timeout; refactoring to split validation re-executed development selection and independently reproduced both frozen validation receipts exactly. Standalone Node file replay remains pending. Production SWMD, TypeScript editor and model checkpoints are unchanged; no model inference, new training run or private evaluation was performed.

Next gate: independent author review of the new provenance fields and narrative warrant. Generate story-specific positive/negative evidence interventions and matched choice swaps at earlier encounters; measure the change in attainable terminal utility under fixed player policies, together with effect apportionment and route alias classes. Do not treat the inspected validation seeds as a fresh holdout. A later change to rarity or priority weights requires a new development contract and independent validation. No Godot dependency.

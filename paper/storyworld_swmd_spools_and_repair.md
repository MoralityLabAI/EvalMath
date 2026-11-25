# SRG-05: Source-order SWMD, spool semantics, and causal authoring repair

2026-11-25 | Executed finite source-pinned migration and numerical replay, plus deterministic public synthetic authoring tasks. No model inference, generalization claim, Lean result or production TypeScript editor build.

## Source recovery and execution contract

GPTStoryworld revision ee1c6918db77d1e0924877f59eca819bae3f1c8c. The full Reservoir Dogs JSON was retrieved by Git blob SHA f735f6198f2c7c1810d3feef13459632867cf1d9 after the file-content endpoint returned empty content. Source identity is pinned in each replay receipt. The HTML reader's blob is d43d9ab729206f1594ea7cee98918bc9ec92f267.

SWMD-SRG/2 extends SRG/1 with complete encounter/option/reaction prose in JSON-escaped records, ordered active/inactive spools, explicit start and turn base, event history, SEEN/ACTIVE predicates, ordered numeric and spool effects, direct and wild destinations, encounter priorities and deterministic tie handling. Wild candidates come from active spool membership, exclude visited encounters, satisfy time and acceptability, and are ranked by priority then source creation index then stable spool/member order. Events for the chosen option/reaction are recorded after effects and before route resolution. The destination encounter becomes seen only after successful entry.

The direct-route policy is explicit: strict mode requires active spool membership, time window and acceptability; explicit mode preserves the inspected HTML reader's direct routing behavior and records whether the destination would have satisfied those admission constraints. It does not silently widen gates. The signed BNumber domain, typed expressions, separate public observation and privileged audit, ordered writes and per-transition squared step energy carry over from SRG/1. Step executes only the selected reaction; audit separately evaluates forced eligible alternatives. Inputs are fail-closed for undeclared variables, unsupported operators, unknown destinations, malformed prose, invalid references and stale scoped patch preconditions. This is a controlled research execution profile, not a complete replacement for all historical formats or a hostile-client security boundary.

Migration preserved the source order of 690 effects and all 138 reaction texts and 20 encounter texts, 46 options, four spools, nine wild consequences. There are 50 explicit numerical coordinates (24 scalar actual-state, 12 first-order belief and 14 second-order belief). Missing referenced p/p2 values were initialized explicitly to zero, matching the inspected reader's fallback; actual-state values are public and belief coordinates hidden by a chosen audit contract, not an empirically established player-information model. Complete original JSON metadata, assets, UI state, stochastic reactions and arbitrary legacy script forms are outside this converter's scope. No utility was inferred from ending prose.

## Reservoir Dogs replay

18 conformance/migration checks passed on the connector-fetched sources in an isolated ECMAScript runtime. The standalone Node verifier additionally checks source Git blobs.

64 matched pseudo-random action-index sequences, 24 choices available per sequence, LCG seed 0x53524705. Once two trajectories differ, the same option index need not identify the same semantic action. Results are descriptive for these fixed sequences, not independent samples of a broader model population.

| Ending | Existing HTML reader | Signed SWMD-SRG/2 (explicit direct routes) |
|---|---:|---:|
| Secret truce | 1 | 13 |
| Standoff collapse | 20 | 22 |
| Mercy trap | 33 | 19 |
| Pink escapes | 7 | 9 |
| Cabot verdict | 3 | 0 |
| Inferno | 0 | 1 |

35/64 paired campaigns differ at termination. In a separate matched-state audit on 16 trajectories, all 629 selected action comparisons differ numerically, 21 select a different reaction, and 23 differ in immediate route. All 1887 eligible forced branches evaluated successfully under explicit routing. These are not claims about population frequencies or actual model behavior.

Strict destination admission produces only 7/64 terminations (one secret truce, six standoff collapses) and 57 blocked destinations. Under explicit routing, 312 selected transitions bypass admission constraints. This flags a compatibility/design contract discrepancy: direct consequence links in the current reader bypass time, acceptability and spool admission. Some may be intentional. A repair must preserve the intended dramatic path and gate semantics; automatically loosening every guard is not justified. Zero endings in this sample do not prove unreachable endings.

## Factorial arithmetic crosswalk

The inspected HTML reader implements clipped additive Nudge; its dispatch falls back to zero for unsupported Maximum and Minimum operators. The source uses both. To separate their effects, replay the same 64 sequences using four reader variants. Replace only these operator evaluations while preserving the reader's action-index policy and route resolver. Binary64 calculations remain unchanged otherwise.

| Reader variant | Endings different from original (of 64) |
|---|---:|
| Original | 0 |
| Signed Nudge alone | 1 |
| MIN/MAX alone | 30 |
| Both | 35 |

MIN/MAX alone versus both differs in eight endings; the effects interact. The reader with both corrections matches the new runtime on all 780 paired selected transitions, with zero observed menu, route, selected reaction or numerical-state disagreements and maximum absolute coordinate delta zero. This is sampled execution parity for this source and contract, not a theorem of global equivalence or parity with the separate TypeScript application. It also does not identify which runtime is narratively preferable; the author must choose and declare the intended operator semantics.

## Causal authoring repair gym

80 generated public tasks, ten defect families, eight parameter variants per family, 60 train_public and 20 calibration_public. The families are reaction sign, wrong belief keyring, comparator direction, dependent write order, weak effect, late windfall, spool activation, event prerequisite, cue visibility, and direct destination admission. Each task exposes a SWMD source, intended causal behavior, one allowed line/field, and explicit feasible initial-state probes. The output is a single {line,before,after} patch. The verifier enforces an exact old-line precondition and preserves all bytes outside the permitted field and line. Candidate behavior is scored by deterministic execution, effect-energy concentration, or an observation-partition oracle. For the cue visibility fixture, the oracle groups equal player observations and computes the best action per cell under the declared two-point prior. It is not a neural capacity measure.

| Arm | Fully passing tasks | Passing checks |
|---|---:|---:|
| Defective | 0/80 | 16/144 |
| Gold repair | 80/80 | 144/144 |
| Semantically inert sham edit | 0/80 | 16/144 |

All gold repairs pass; each original defect fails at least one check; all shams preserve the original pass count. The shams are deliberately simple syntactic controls, not matched compute or difficulty controls. Examples include neutral ADD/AND wrappers, no-op assignments, alternative window formatting, and whitespace-only visibility edit. No claim of learned author ability: these results are the task generator's positive/negative controls.

The generator exposes a callable verifier and a JSONL submission scorer. In a further executed check, gold submissions scored 144/144, shams 16/144, and 80/80 attempted extra-record injections were rejected. Duplicate, missing, unknown and malformed submissions are explicitly accounted for. The tasks and gold files are separate but both public. Family names remain in IDs, calibration variants share templates, and all scoring probes are visible. Do not use the public split for a sealed benchmark or claim independence across the 80 instances. A different patch that satisfies the finite contract is accepted; this does not prove semantic preservation over untested states. Next registration should define independent template families, hidden world-level interventions and matched causal sham controls, then test real authors against them with calibration separated from final evaluation.

## Reproduction

Use a GPTStoryworld checkout at the pinned revision. Run these from the EvalMath root:

    node integrations/sweepweave-ts/srg05/verify.mjs /path/to/GPTStoryworld /tmp/srg05.json
    node integrations/sweepweave-ts/srg05/reader-factorial.mjs /path/to/GPTStoryworld /tmp/srg05-factorial.json
    node integrations/sweepweave-ts/srg05/build-authoring-gym.mjs /tmp/srg05-gym
    node integrations/sweepweave-ts/srg05/score-author-patches.mjs submissions.jsonl /tmp/author-score.json all

Compare the regenerated output with the committed receipts and public dataset. The first two check the source blob identity. The same JS implementations and source contents were executed in an isolated runtime in this turn; standalone Node execution from a local checkout and full TypeScript application/browser CI are still outstanding.

## Integration boundary and next research

The SRG-04 upstream sweepweave-ts write-access restriction remains; no production editor changes were made. SRG/2 has a browser-safe ECMAScript module, but the SRG-04 editor panel and installer still target SRG/1. Port the panel to SRG/2 with privileged audit separation and test the actual TypeScript build/browser path before deploying it. No Godot dependency.

SRG-06: derive real-world scoped repair proposals for the 312 admission bypasses, test source-backed author intent, add blind family-disjoint training/calibration/held-out splits, and run compact models using local SWMD card context. Publish gold receipts as verifier-only; never train Data Goblin on sealed interventions. For the next geometry experiment separate clock and flag energy from task-relevant continuous state, declare terminal utility and belief-access policy, then evaluate reasoning difficulty across K and horizon on matched repaired worlds.

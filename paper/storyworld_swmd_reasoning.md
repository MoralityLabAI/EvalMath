# SRG-03: SWMD-first reasoning geometry, sequential information and authoring repair

2026-11-25 | Evidence: finite exact integer synthetic oracle and source-pinned static audit of existing SWMD. No model inference or TypeScript editor execution in this turn. The production target is SWMD + SweepWeave TypeScript. Godot is outside this roadmap.

## 1. Authoring representation and execution contract

Use encounter cards (SWMD-0-MIN) as the model-facing input/output. The legacy minified export is a compact projection, not currently a lossless executable language. Preserve its token advantage with a versioned SWMD execution profile (working name SWMD-SRG/1). Keep human-readable ENC/ORX, O:, E:, D: and stable IDs. Separate world-level immutable context, encounter-local mutable formula cards, and a verifier-only gold manifest.

Mandatory execution profile (proposed, not yet supported by the editor):
- world identity, source/compiler hash, runtime entry point and numeric convention (signed BNumber [-1,1] vs normalized [0,1] AST must be explicitly distinguished), reaction selection/tie rules, spool scheduling and wild routing semantics;
- initial coordinates with full owner/property/subject/second subject keyring, explicit domain, declared missing-pointer policy (fail closed); observable subsets and when a cue becomes available;
- encounter time window, acceptability/priority and spool membership; option visibility and performability; reaction eligibility, order, desirability and ordered effects, then explicit consequence;
- typed comparator operators GE, GT, LE, LT, EQ, NE or lossless subtype encoding; distinguish boolean constants from numeric constants; retain exact decimal input text until compilation;
- retain reaction/effect order (including duplicate writes). No implicit reorder, no silent unsupported-operator fallback, and no synthesis of gold objective from text;
- declared terminal payoff vector and independent authoring contract, with hidden scoring fields excluded from the player packet. Any ending rarity target, goal metric weights, intended core vs nuisance axes, and event-class effect budget must be frozen before scoring.

A small legacy SWMD sidecar may bind omitted fields to the existing source for migration, but long-term SWMD + typed manifest should be the authoring authority, with runtime JSON/AST a compiled derivative. A compact per-encounter patch only needs stable IDs and the local D/E/gate changes; a deterministic compiler expands them. Do not serialize secret state or outcome labels into player-visible cards. Hash the exact canonical bytes, including order.

Source findings:
- [json_to_swmd.py](https://github.com/MoralityLabAI/GPTStoryworld/blob/ee1c6918db77d1e0924877f59eca819bae3f1c8c/codex-skills/storyworld-building/scripts/json_to_swmd.py) rounds numeric constants to six decimals, sorts options/reactions/effects, omits comparator subtype from formula text, infers ending type with keyword heuristic, projects threshold clauses into property names without actor/subject, and omits initial state and option gates from minified body.
- [swmd_patch_json.py](https://github.com/MoralityLabAI/GPTStoryworld/blob/ee1c6918db77d1e0924877f59eca819bae3f1c8c/codex-skills/storyworld-building/scripts/swmd_patch_json.py) is a prose/route patcher, explicitly not a formula compiler.
- [TS ScriptManager](https://github.com/MoralityLabAI/sweepweave-ts/blob/52e8b446592639eb3a63f7824fc6edc5af9be7f1/src/ScriptManager.ts) dispatches Bounded Sum, Mean, Average, Negation, Blend, Nudge, Maximum/Minimum, Proximity, If Then, Boolean Comparator in the inspected legacy path, but does not dispatch the legacy Addition, Multiplication, Absolute Value or Arithmetic Comparator strings used by the audited SWMD source worlds. Unrecognized elements return null. Other AST paths may behave differently; pin and test the actual TS execution entry point before claiming support. [Rehearsal.ts](https://github.com/MoralityLabAI/sweepweave-ts/blob/52e8b446592639eb3a63f7824fc6edc5af9be7f1/src/Rehearsal.ts) selects the last equal-score reaction (subject to its initial -1 score floor), applies assignments in order, and checks visibility AND performability. The [scriptAst.ts](https://github.com/MoralityLabAI/sweepweave-ts/blob/52e8b446592639eb3a63f7824fc6edc5af9be7f1/src/scriptAst.ts) path is a different normalized-domain representation. No Godot conformance gate is needed.

Conformance tests for TS: comparator direction (GE vs LE), strict vs nonstrict ties, unequal ordering of two dependent writes, repeated writes, signed Nudge, Blend normalization, exact full p/p2 keyring isolation, initial-state replay, guard legality, wild/spool resolution, reaction/encounter ties, and no silent default for unsupported syntax. Round-trip compare observed state, menu, score, selected reaction, ordered write trace, destination and terminal payoff for each feasible action. Compiler coverage must use actual runtime execution rather than JSON syntax validation.

## 2. Static audit of two actual SWMD worlds

Source revision ee1c6918db77d1e0924877f59eca819bae3f1c8c in GPTStoryworld; Git blob hashes in receipt. Strict line parser reads the minified encounter/reaction body and full textual P(owner.property[subject][second]) references. It does not interpret all arithmetic expressions, prove reachability or compile scripts. "wild" is a routing token requiring a resolver, not a missing encounter.

| Metric | TSUN-01B | Reservoir Dogs |
|---|---:|---:|
| Encounters | 13 | 20 |
| Options | 21 | 46 |
| Reactions | 42 | 138 |
| Unique formula keys actual/p/p2 | 3/0/0 | 19/12/14 |
| Formula pointer occurrences actual/p/p2 | 126/0/0 | 184/138/138 |
| Unique effect target keys actual/p/p2 | 10/0/0 | 15/12/14 |
| Reactions with cross-effect read/write dependency | 0 | 138 |
| Directed cross-effect dependency pairs | 0 | 564 |
| Structurally mechanically equivalent menus | 21 | 0 |
| Generic comparators in frontmatter | 6 | 13 |

The 564 pairs count separate directed effect-write-to-other-effect-read references (not unique coordinates or proven changed outcomes). Dependency alone does not establish that reversing a particular pair changes its numerical result. The Reservoir Dogs full compiled JSON was not retrievable through the connector, so original assignment order and runtime consequences cannot be independently compared. This is a source-risk census, not a native-engine failure rate.

TSUN JSON crosswalk: every reaction list of effects was reordered in the SWMD representation, no reordered cross-effect dependency pairs were found, no destination mismatches. Initial numeric coordinate count 11; all option visibility/performability scripts trivial. The inferred frontmatter type for page_end_failure_unverified is success, despite the source outcome protected=false. This follows from the current keyword classifier and must not be used as a gold reward. Six ending conditions contain an ambiguous comparator in the primary formula text; proximity_spec preserves simple threshold directions but lacks full owner keyrings and does not generally encode compound conditions.

## 3. Exact sequential oracle

Finite initial worlds with unit mass, deterministic transitions and observations, common visible legal menu within each history cell, integer terminal utility, zero utility if horizon expires without completion. Let B be a multiset of latent states consistent with the actor's observed history (multiplicity preserved). For h>0, with all states nonterminal,
    W_h(B)=max_{a in A(B)} sum_{o} W_{h-1}({T(s,a):s in B, O(T(s,a))=o}).
Terminal cells sum realized utilities; W_0 counts only completed terminal rewards. Sum W over initial observation cells and divide by initial world count. This is an exact perfect-recall finite decision-tree recurrence by conditioning on the first action and observation. Reject hidden-dependent legal menus or terminal/nonterminal observations conflated within a cell. The implemented oracle uses bounded exact integer counts for the registered small fixtures, not an arbitrary-size probability solver. Stochastic extension uses rational transition masses or a finite random tape, with correct observation filtration.

Sequential parity fixture: K independent binary clues revealed one at a time, forced read action, then choose even/odd. All clues recoverable in clean world. For K=1,2,4,8, full-history success 100%; terminal-only memoryless policy succeeds 100%,50%,50%,50%. Enumerate all four last-bit-to-action maps independently. One-bit running XOR accumulator succeeds 100% at each K. Thus K relevant coordinates, K observations, and one-bit sufficient memory can coexist. Do not use K as a memory dimension proxy. The node counts 7/15/63/1023 describe this uncompressed tree oracle, not a neural cost lower bound. Padding K=4 with four independent nuisance bits gives 256/256 full-history success and 63 oracle nodes. Hide the final clue with identical payoff and topology: perfect-recall success falls to 50% at every K; restoration of the clue restores 100%. This isolates inaccessible information from memory limitations.

Precision fixture: integer-thousandth states 646 and 648, threshold 647, correct binary decision. With rounding to 0/1/2/3 decimal places the oracle succeeds 1/2,1/2,1/2,1 respectively. Exact integer rounding. Separate non-nested partition counterexample states 649 and 651, threshold 650: values 1/2,1,1/2,1. Ordinary rounding at successive decimal places does not necessarily refine information partitions, because the bin boundaries move. For monotonic precision experiments use nested partitions, e.g. dyadic truncation or explicit refinement. Compare equal action/observation contracts.

Planning fixture: take yields 1 immediately; prepare followed by finish yields 2. Horizon-one optimum 1, horizon-two optimum 2. This is a horizon constraint on achieved payoff, not a neural planning-depth claim.

Effect repair fixture in integer state units: four steps 25 each cross the >=80 gate with maximum squared-step-energy share 1/4. Four steps 10 each fail it; an inverted <=80 gate rejects the clean path. A late step of 100 with three preceding zero steps attains the same endpoint but has concentration 1. Whether the windfall is narratively warranted requires a declared evidence/causal contract; use the concentration metric as a flag. Restoring the clean amounts or gate recovers eligibility.

## 4. SWMD authoring gym and compact models

Author input: bounded encounter card, local state support, causal intent and allowed operators, prior clues, declared outcome and target difficulty. Author output: small valid SWMD edit (D/E/visibility/gate/route), proof or explanation fields, predicted counterfactual behavior. Compile deterministically. Evaluate against frozen feasible interventions and oracle, compare pre/post eligible endings and effect profile. Never award prose-quality points to compensate for a mechanically invalid patch.

Curriculum axes:
- K_ambient vs K_relevant and projection rank; padded vs native causal support;
- quantized precision with nested bins and guard margins;
- memory capacity and sufficient information statistics;
- policy horizon, search nodes, branching and irreversible actions;
- pValue/p2Value observational ownership and hidden cues, with perfect-recall gap;
- causal repair: wrong sign, inappropriate variable, common-mode distractor, missing evidence, weak or oversized update, order-dependent mutation, ambiguous comparator, bad ending label.

Keep public authored mechanics separate from sealed scorer; reject defects not identifiable from author-visible evidence, or grade abstention. Use matched-sham patches and held-out world families; verify repairs preserve unaffected paths. Calibrate against independent world-level variance before sealing any claims. Data Goblin can ingest compact author patch / verification receipt examples and player trajectories under separate dataset IDs; no held-out worlds, hidden labels or later reveal in pick-time training input. Existing SWMD-CTRL K budget labels should remain separate from K_relevant.

Next practical work in GPTStoryworld/sweepweave-ts: add versioned compact execution profile to exporter/parser, introduce TS runtime counterfactual exporter (no Godot), compile and execute all operator/guard conformance fixtures, rerun TSUN and Reservoir Dogs with actual legal menus and source-order effect traces. Then run small author models on targeted patches before any full campaign. This commit implements static audit and finite oracle only.

## Reproduce

    node scripts/verify_storyworld_srg03.mjs /path/to/pinned/GPTStoryworld output/evaluation_storyworld_reasoning/srg03.replay.json

The script checks five upstream Git blob hashes and recomputes the receipt. Executed here from connector-fetched contents in an isolated JS runtime. Standalone Node replay and editor integration are outstanding. No claim that the proposed SWMD-SRG/1 profile is already supported. 

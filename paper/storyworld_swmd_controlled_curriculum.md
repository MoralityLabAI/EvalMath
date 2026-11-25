# SRG-07: Controlled causal K, information and planning in executable SWMD

2026-11-25 | Evidence: finite truth-table equivalence and runtime positive/negative controls. No language model inference, training, independent sealed test, TypeScript editor build, or Lean claim.

## 1. Curriculum contract

SRG-07 generates deterministic SWMD-SRG/2 civic-ledger worlds, with independent reference truth functions and executable typed gates. Every input is an independently assigned binary sign under the reference uniform prior; the numerical magnitude is fixed within the world (chosen from 0.125, 0.25, 0.5, 0.75). Source VAR records are placeholders initialized to zero; the generator/verifier supplies the declared signed initial-state assignment before execution. These are instrumented tasks, not standalone playable narratives with a representative fixed initial state. The formula equivalence is established for that binary equal-magnitude domain; arbitrary continuous magnitudes are outside this contract.

K_relevant counts sign coordinates that have at least one Boolean influence witness; it is not a lower bound on working-memory bits, runtime cost, or the minimum sufficient statistic. The progress register is separate. K = 4, 8, 16; horizon H = 1, 3, 5 total actions. Unpadded ambient dimensions are K+1; matched padded dimensions are 33, 65, 141, including the progress coordinate. Nuisance coordinates are declared but never enter formulas; padding values are fixed within the paired world and selected by the generator. It is a no-op dimensionality control, not a stochastic distractor process or proof of learning invariance. Coordinate names and report option ordering are randomized independently by case using the seed.

For each K, H and family, the reference truth function is balanced on all 2^K assignments. At final report stage exactly one of two legal actions obtains success; the other fails. Utility is externally declared: completed correct report 2, early settlement 1, wrong report or unfinished horizon 0. Preparation actions have equal 0.125 increments to progress; the success gate requires H*0.125. For H>1, a stop action offers utility 1 at each preparation stage. With budget 1 the initial optimal action is settle; with budget H the optimal first action prepares. For H=1 the two report actions are immediately available. Short horizon control and correct report classification are distinct measurements. Progress is deterministic and all successful/failed report trajectories move only along the progress coordinate. This controlled effect-budget fixture uses additive increments, deliberately not signed Nudge; no claim that equal increments are universal storyworld design.

## 2. Family partition

| Split | Families |
|---|---|
| train_public | parity; majority with distinguished tie-break bit |
| calibration_public | anchored quorum; adjacent conjunction with anchor |
| evaluation_private | conditional selector; leading-run parity with anchor |

For every family, each coordinate has at least one matched input pair, differing only at that coordinate, for which the correct report flips. Parity uses product sign for even K; the independent reference counts positive bits. Majority uses signed sum with explicit tie-breaking. Anchored quorum XORs the anchor with a majority over the other odd number of bits. Adjacent conjunction XORs the anchor with the existence of any positive adjacent pair in the remaining ordered cues. Selector XORs the anchor with an IF-controlled OR or AND over two disjoint cue subsets. Leading-run XORs the anchor with parity of the number of consecutive initial positive cues among the remaining inputs. The independent reference uses ordinary bit arrays and loop/count logic; the compiled expressions are separately constructed and evaluated by SRG/2.

These are structurally disjoint formula templates, not six independent domains, and every author mutation in this first cohort is an inverted positive-report gate. The negative-report gate remains the complementary reference in the source, so an author can sometimes repair by simple consistency or removing an outer NOT. This is a deliberately elementary local-edit curriculum and does not establish sophisticated authoring generalization. Next-stage authors must synthesize formulas with no intact complementary expression, vary repair mechanisms, and be evaluated on larger independently authored tasks.

## 3. Exhaustive and runtime controls

Public deterministic configurations: training seed 0x53520701, calibration 0x53520702, and reserved-family PUBLIC SMOKE seed 0x53520703. The last seed is public and its results are not a sealed benchmark. No actual private evaluation cases were materialized or run in this turn. The generator code and the held-out family definitions are also public; fresh private seeds reserve instances, not unknown concepts or unpublished families.

For each of the 18 family/K combinations, evaluate both compiled report gates on every assignment at the representative generated common amplitude (one H=1 case). 394,848/394,848 assignments agree with the independent reference and its complement. This is exhaustive gate equivalence at those fixed amplitudes, not exhaustive full-runtime trajectory enumeration across all 54 worlds.

Full runtime verification uses balanced sampled input masks and all unique coordinate relevance witnesses. Three cohorts of 18 worlds (54 including public smoke); 1,392 distinct within-world probe rows, all pass clean and gold-repaired behavior; defective and semantically neutral sham edits pass zero rows on the stronger unique-correct-report contract. Both report actions are checked per row. Each of the same 1,392 rows preserves outcomes/reactions/utility/progress/energy share under nuisance padding, and has expected largest squared-step-energy share 1/H. 504 coordinate relevance witnesses (repeated over horizons/cases) pass, 108 bounded-planning controls pass, and 54 attempted extra-record injections are rejected. These are designed controls, not independent random benchmark observations or model performance.

Public task artifacts contain 36 author examples and 576 full-observation report decisions, split 18/18 author and 288/288 report across the two public splits. Separate gold files are public and must never be included in a player prompt. Public author examples include representative labelled inputs and an exact permitted gate-edit scope. The scoring function tests further balanced inputs and relevance witnesses; a different gate that passes the finite probes is accepted. The finite author scorer is not a universal Boolean equivalence proof for arbitrary submitted patches.

## 4. Exact information oracle

For a subset of the first m semantic cues, group all 2^K equiprobable states by the observed sign vector. Let n_0(c), n_1(c) be the counts of correct false and true reports in cell c. The optimal decision accuracy is
    V_m = (sum_c max(n_0(c), n_1(c))) / 2^K.
The public observation contains the revealed cue coordinates, progress, current page and identical action menu. Initial hidden cues are not included in player packets. Rule text describes the sign decision, and the uniform independent-sign prior is the experiment's declared reference distribution. The exact V_m is an information ceiling for a prior-aware optimal classifier; it is not neural accuracy. The player JSONL contains balanced diagnostic sample masks rather than all assignments, so measured sample accuracy need not exactly equal this uniform-prior quantity. The partial-observation player tasks do not claim to be complete narrative belief-inference tasks. No memory demand is inferred: cues in these tasks are static.

At K=16, revealing half (eight) of the coordinates gives:

| Family | Exact numerator / 65536 | Accuracy |
|---|---:|---:|
| Parity | 32768 | 50.0% |
| Majority | 51602 | 78.7% |
| Anchored quorum | 49152 | 75.0% |
| Adjacent conjunction | 62342 | 95.1% |
| Conditional selector | 65024 | 99.2% |
| Leading-run parity | 65366 | 99.7% |

Every family's zero-cue and full-cue oracle is 50% and 100%, respectively. All 16 coordinates are relevant in every family, yet their influence masses differ enormously: parity's each-coordinate influence pair count is 32768 of 32768; leading-run's least influential coordinate has only two flipping pairs. This establishes why K alone is inadequate. The authoring metric should include the entire information curve, influence spectrum, minimum task-specific sufficient statistics, utility opportunities, effect apportionment and planning horizon. Matched K/ambient controls avoid rewarding arbitrary coordinate padding. For fair difficulty calibration, control observation order as well as count; the present order is fixed by semantic position, and anchor/selector cues may be unusually informative.

## 5. Local materialization and scoring

Run from an EvalMath checkout (Node 20+ recommended):
    node integrations/sweepweave-ts/srg07/truth-table-audit.mjs /tmp/srg07-truth.json
    node integrations/sweepweave-ts/srg07/local.mjs generate train_public /tmp/srg07-train 1
    node integrations/sweepweave-ts/srg07/local.mjs generate calibration_public /tmp/srg07-cal 1
    node integrations/sweepweave-ts/srg07/local.mjs generate evaluation_private /tmp/srg07-private 1

Output directories must be new; private evaluation must be outside the repository. Replicates range 1..16. For private generation the command creates a fresh nonzero uint32 seed using crypto.randomBytes and excludes public seeds. The private manifest and gold are kept under verifier/, with best-effort restrictive filesystem modes; send only model_input/ to a model. A 32-bit seed is for instance reproducibility, not a cryptographic commitment or secure secret. Protect the directory and don't train on private tasks or labels. The public generation mechanism means a determined evaluator could reconstruct the intended rules. Freeze model/checkpoint and protocol before generating final seeds; keep private source and outcomes out of public Git and Data Goblin training. For genuinely blind conceptual evaluation use an independent author and unpublished family specification.

Each generated split with one replicate has 18 author tasks, 864 player report tasks (0, half, full cue visibility, 16 balanced probes per world per mask), and 48 first-action planning tasks (H>1, two input states, budgets 1 and H). The latter provides explicit remaining contributions, action budget and terminal utility. Only model inputs should be passed to Bonsai/Inky/Data Goblin. Author JSONL submissions use {id,line,before,after}; player/planning submissions use {id,action}. Score with:
    node integrations/sweepweave-ts/srg07/local.mjs score author /tmp/srg07-cal author_submissions.jsonl
    node integrations/sweepweave-ts/srg07/local.mjs score player /tmp/srg07-cal player_submissions.jsonl
    node integrations/sweepweave-ts/srg07/local.mjs score planning /tmp/srg07-cal planning_submissions.jsonl

Report missing, duplicate and rejected rows in the full denominator; unknown IDs are listed. Gold, sham, malformed submissions, duplicate and out-of-scope patch controls were executed for each public/smoke cohort. All expected gold scores reproduced (2,592 report and 144 planning answers across three public/smoke cohorts); these are oracle self-checks, not model results. Pure scorer functions were executed from fetched source in an isolated JS runtime; local filesystem CLI execution, standalone Node reproduction, actual model calls, editor integration and full CI are outstanding.

## 6. Next research

SRG-08: use the scorer with local Bonsai/Inky model calls; register independently authored novel formula synthesis, causal repair and sequential observation families, including relevant-vs-redundant coordinate pairs, equal-information high/low K, irreducible joint interactions, memory/temporal cue constraints and a real branch-dependent planning task. Derive comparable compact-model benchmarks from the same SWMD execution contract. Integrate dataset manifests into Data Goblin's collator with source hashes and explicit split boundaries. The current public curriculum is ready for local pedagogical experiments; no GPU work has been run here. The original worlds and TypeScript production editor remain unchanged. No Godot dependency.

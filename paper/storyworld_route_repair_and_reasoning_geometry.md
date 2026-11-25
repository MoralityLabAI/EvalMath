# SRG-06: Route-scoped authoring repair and task-relative reasoning geometry

2026-11-25 | Evidence: source-pinned finite numerical replay and bounded decision-tree enumeration. No language model, production editor, or Lean verification executed.

## 1. Repair the cause, preserve the world

The Reservoir Dogs SWMD-SRG/2 fixture is pinned by Git blob cb174a3efb031eaa046b01a2acc526ef7d122345. The upstream source was migrated in SRG-05. The legacy reader and SRG/2 explicit consequence policy allow a direct route to bypass destination admission, while wild routing filters by unvisited encounter, active spool, numeric acceptability and time window. A strict destination contract exposes a discrepancy between the direct consequence graph and the authored time windows.

Reproduce the SRG-05 cohort (64 campaigns, original LCG seed 0x53524705). All 312 observed violations are early arrival only, across nine destinations, 17 distinct edges and 34 reaction IDs. No observed late-window, inactive-spool or numeric-predicate violation in these transitions. With a second LCG seed (128 campaigns), 877 additional violations are also early arrival only; a tenth destination is exposed.

Let d(v) be the length in actions of a shortest directed path from the start to v, using only explicit consequence edges (ignore reaction/guard feasibility, no wild edges). Let b be the initial turn. The graph-derived earliest direct arrival is b+d(v). This is a structural lower bound on paths before the first wild route, not a reachable-state certificate. Define L_D(v)=min(L(v),b+d(v)) for finite d(v), otherwise L(v). The manifest contains only the ten encounters where L_D<L. Direct admission requires L_D<=turn<=U, an active destination spool and the unchanged numeric acceptability gate. Wild routing uses the original L,U and priorities. If a direct destination violates any other admission constraint or lies before L_D, fail closed. The adapter only accepts the numeric-only encounter-gate profile; do not silently extend it to event-dependent gates. It is opt-in, bound to the source blob by the verifier, and is not a change to the original world or its editor.

For comparison, the global-window candidate lowers L to L_D for all routes. This may let previously skipped encounters re-enter the wild candidate set. It is committed as an explicitly labelled sensitivity candidate, not a recommended production edit.

## 2. Matched replay and PRNG sensitivity

The historical LCG with modulo action selection has low-bit structure. In particular, the different seed parities and fixed sequence length can systematically affect menus of even size. The earlier second-seed comparison is a diagnostic, not independent uniform-play certification. An additional 128 campaigns use two new xorshift32 streams with floor(u*n) action-index mapping, 64 per stream, preserving the same 24-word sequence across each policy arm. No empirical player or model was sampled. The four cohorts are fixed deterministic numerical tests, not statistical independent draws from a population of storyworlds.

| Cohort | Original complete | Strict original complete | Global widened complete | Scoped complete | Global changed path | Global changed ending | Scoped changed path/ending |
|---|---:|---:|---:|---:|---:|---:|---:|
| LCG calibration 64 | 64 | 7 | 64 | 64 | 11 | 5 | 0/0 |
| LCG validation 128 | 128 | 2 | 128 | 128 | 47 | 18 | 0/0 |
| Xorshift calibration 64 | 64 | 2 | 64 | 64 | 13 | 7 | 0/0 |
| Xorshift validation 64 | 64 | 0 | 64 | 64 | 18 | 5 | 0/0 |
| Total 320 | 320 | 11 | 320 | 320 | 89 | 35 | 0/0 |

There were 1,956 scoped early-window exceptions across these trajectories (312+877+374+393). The adapter preserves sampled sequences of encounter/action/reaction/destination/turn. Given its implementation (execute the original transition, then independently certify admission), successful transitions also preserve the original numerical successor. The claim is conditional on retaining the explicit-routing transition semantics. It is not proof that every reachable route will be admitted or that the author intended the lower time windows; review the manifest before adoption.

## 3. Task-relative geometry and effect apportionment

Use the original signed numerical transition contract and unit coordinate weights. Partition the 50 numerical coordinates into clock, actual non-clock, first-order belief and second-order belief channels. For the secret-truce target the authored substantive gate is White loyalty within [-0.53,0.77], Pink suspicion >=0.08, Blonde sadism <=0.35; a separate clock gate requires White clock >=0.55. These are an axis-aligned product region, not a single goal vector. Distance to the substantive gate region is the squared Euclidean norm of the coordinatewise projection residual:
    D_g^2(x)=(x_loyal-clip(x_loyal,-.53,.77))^2 + max(0,.08-x_sus)^2 + max(0,x_sad-.35)^2.
Add max(0,.55-x_clock)^2 for the full numeric gate. The expression is algebraically the squared distance to that product region in these coordinate units. Time windows, active spool membership and relative ending desirability are separate constraints. Gate distance zero is not sufficient to select a secret ending.

For each realized transition compute squared displacement energy by channel, and for goal progress use D_g^2(x_t)-D_g^2(x_{t+1}). Record positive and negative progress separately. The maximum step share is max(step energy)/sum(step energy) on nonzero-energy paths. In the 128 LCG validation campaigns:

| Channel | Share of all squared step energy |
|---|---:|
| Clock | 10.486% |
| Actual non-clock | 57.739% |
| pValue | 18.184% |
| p2Value | 13.591% |

The three substantive secret-gate coordinates account for 25.762% of total energy (a subset of actual non-clock). Median per-path largest step share is 0.102673287 for all coordinates, 0.218672603 for these three. On the seven secret-ending trajectories the corresponding medians are 0.095974444 and 0.254426011. All seven satisfy the substantive gate at termination. Median maximum positive-progress share is 1: on the recorded paths, positive distance-reduction can be concentrated in a single step even when total geometric effects are distributed. Initial proximity and plateaus matter; this is a flag for author review, not evidence of an unjustified surprise. Different semantic units/weights could change the ranking. No subjective narrative utility is inferred from proximity.

## 4. Local causal support and K

For each predecision sirens state, include reads of all option gates and reaction eligibility/score expressions. For each forced eligible or potentially eligible reaction, include reads of the admission gates and priorities of every possible wild candidate given fixed time, visited history and active spools (the pinned sirens reactions have numeric-only effects). Back-propagate through ordered writes: when a needed post-write coordinate is assigned, remove it and add the reads of its right-hand side, retaining self-reads. Union the resulting pre-state coordinates with menu and reaction-score reads. This is a conservative syntactic one-step sufficient support for route and selected reaction, conditional on fixed discrete context and well-defined expressions. It is not the minimum causal rank, neural memory dimension, or full-horizon support.

In 93 calibration sirens snapshots and 184 validation snapshots, support union size is 16 in both, with 14-15 per validation snapshot. The world has 50 numerical coordinates; the other 34 are outside the union for this local contract. On the first 16 validation snapshots, setting each absent coordinate separately to -1 or +1 gave 1,148 one-coordinate ambient interventions and zero changes to the legal menu, selected reaction or destination signature for all legal actions. The interventions are bounded synthetic do-perturbations at fixed history, not necessarily states reachable in the authored world. Joint and longer-horizon sufficiency remain separate claims.

The initial one-step secret-only oracle (184 LCG validation snapshots) has just nine full-state opportunities; a snapshot is an opportunity if at least one legal action can enter the target immediately. The sample is sparse and unfit for a broad difficulty claim. We therefore add the six-goal experiment below.

## 5. Six-ending finite planning and observation budgets

Use the new xorshift cohorts, 100 calibration and 99 validation snapshots at the sirens encounter (some campaigns revisit it; snapshots and target labels share world/trajectory dependence). For every snapshot and each of the six ending IDs, declare the target externally. No inferred moral utility or ending preference. Enumerate all legal first actions and their full-state continuation trees through h=1,2,3 total actions; a first action wins if its successor can reach the target within the remaining horizon. The full-information opportunity count is the number of snapshot-target pairs with at least one winning action. The exact finite tree enumeration uses the actual deterministic signed runtime with binary64 operations. It is a local first-action oracle followed by clairvoyant continuation; it is not a complete partial-observation planning solver.

At each K, make a nested coordinate prefix (target-gate keys first, then the calibration syntactic support ordered by frequency, remaining coordinates last). Quantize each selected coordinate into four fixed equal-width bins on [-1,1], and group by target ID, turn, legal menu and binned coordinates. These are deliberately declared snapshot information channels, including privileged hidden coordinates in some arms. The within-validation partition oracle chooses the best common action per cell using validation labels; it measures an empirical information ceiling, not a realizable generalizing model. The calibration lookup chooses the calibration cell's best action, falling back to the target/turn/menu cell or lexicographic action if absent. No validation labels enter this lookup. Full-information continuation remains privileged in every arm. Compare to the expected number of successful uniformly random first actions with clairvoyant continuation. Use raw opportunity count and report absolute denominator separately; don't condition evaluation on a hidden gold feasibility label.

| Horizon | Validation pairs | Full-state opportunities | Menu/turn-only partition oracle | K=8 partition oracle | K=16 partition oracle | Calibration lookup K=2 | Random first action expectation |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 594 | 86 | 76 | 84 | 86 | 63 | 61.666666667 |
| 2 | 594 | 86 | 76 | 84 | 86 | 63 | 61.666666667 |
| 3 | 594 | 119 | 104 | 117 | 119 | 95 | 88 |

At h=3 the K-prefix partition oracle is 104,104,111,111,117,119,119,119 for K=0,1,2,4,8,16,32,50. The lookup at K=16 achieves 90 successes and 552/594 validation rows fall in cells unseen during calibration; K=50 sees 576/594 unseen. Increasing observable state can refine the finite partition while increasing sample sparsity. The finite public-only partition also attains the opportunity ceiling, but the same lookup achieves 90/594 with 558 unseen cells. This does not establish that beliefs are irrelevant, or that an actual player can infer hidden states from prose/history. Empirical partition separation can occur by accidental proxy correlation.

The 33 additional full-state opportunities at horizon three (including the secret target, from 10 to 16 opportunities out of 99 roots) motivate varying horizon separately from K. Opportunity mass is low; design harder authoring exercises around matched positive/negative causal instances, not solely random-play late snapshots. More coordinates are not inherently more difficult. A well-balanced world should declare the intended goal, causal support, information access, horizon, and effect-size profile, then demonstrate enough valid decision opportunities for a reasoner evaluation.

## 6. Reproduction and next gate

From EvalMath root:
    node integrations/sweepweave-ts/srg06/verify.mjs /tmp/srg06.json /tmp/window-candidate.swmd.md
    node integrations/sweepweave-ts/srg06/robustness.mjs /tmp/srg06-robustness.json

The scripts check relevant source Git blobs and recompute receipts. Same code paths were executed from connector-fetched source in an isolated ECMAScript runtime. Standalone local Node replay, TypeScript application integration, independent referee, and real compact-model runs remain pending.

SRG-07 should construct independent authored families of SWMD tasks with explicit K_relevant, horizon, nested observation channels, matched opportunity and randomized semantic variable/option identities. Seal evaluation probes outside the public training corpus before testing Bonsai, Inky or Data Goblin. Use the SRG-05 patch scorer and SRG-06 route/geometry contracts; do not recycle these public examples as evidence of held-out generalization. The production SWMD editor and original Reservoir Dogs remain unchanged. No Godot dependency.

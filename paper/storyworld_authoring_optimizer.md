# SRG-11: Constrained authoring optimization and failure-aware SWMD promotion

2026-11-25. Evidence class: deterministic finite design search, calibration-selected candidate, frozen public validation, executable SWMD transition checks. No language model inference, independently sealed evaluation, production editor integration, or Lean proof. Both candidates are retained for review, not promoted.

## 1. Optimization contract

An authoring target should specify a task and a region of acceptable behavior. For source S, allowed edit theta, prior/reachable state set R, and independently specified payoff U, define the verified metric vector
    M(S_theta,R,U) = (opportunity, unique-choice fraction, reaction/route margin, adaptive value, effect energy, provenance).
Search an explicitly bounded edit set. First enforce hard constraints and preserve required invariants; then minimize declared edit distance. Select solely on the calibration cohort and freeze the candidate before computing the validation results. A candidate passes only if every registered validation constraint holds. Report the feasible grid and the failures; do not silently change a target after seeing validation. This is a prototype, not a universal optimizer for narrative quality.

The thresholds, parameter grid, source scopes and calibration/validation scenario choices below are research design choices, not author-supplied gold. They were selected after initial exploratory calculations in this turn, not an independently timestamped preregistration. The frozen implementation then selected before evaluating the listed validation cohorts. All cohorts are public and related by world family. The envelope analysis after validation is explicitly exploratory and cannot be used to promote a replacement.

## 2. Investigation economics

Use SRG-10's specialist model with hidden T,Z, two context-dependent sources X,Y, context query Q, analyst context signal and reviewer truth signal. Correct commitment pays 16, incorrect pays 0, settlement S, and query cost c is deducted from all terminal values. Vary c in {1,2,3} and S in {7,8,9,10,11,12}, with baseline (2,12). The probability/payoff sidecar, rather than prose, is the scoring authority: the current SRG/2 compiler has no native numeric utility schema. Each candidate source is compiled from the chosen sidecar, keeping evidence structure and reliability fixed. This is an economics edit to the explicit experiment contract and corresponding SWMD rules, not a change to the underlying numeric transition functions.

Constraints on every calibration reliability configuration:
- c>=1; unique optimal blind H=1 action is settle;
- unique optimal blind H=3 first action is Q;
- unique optimal analyst H=2 first action is X for positive initial context evidence, Y for negative;
- blind H=3 expected utility exceeds the best fixed two-query order (with adaptive early stopping allowed) by at least 1;
- both analyst H=2 cells have top-vs-second expected utility margin >=2.

Minimize |c-2|+|S-12| over the 18 candidates, deterministic tie break. Two calibration candidates pass all three scenarios: (1,9) and (1,10). Select (1,10), edit distance 3, the closer. Baseline passes 0/3; selected 3/3. The selected blind adaptive-minus-fixed gains are 1.125, 2, and 1. The four frozen public validation reliability configurations (a,b,strong,weak,aux) are (6,7,7,4,6), (8,5,8,5,7), (5,6,6,5,6), (7,7,8,6,8), with each reliability numerator out of eight. They are hand-chosen stress scenarios, not statistical draws. Validation passes 2/4 (scenarios two and four). First failure: gain .5 and analyst margin 1.5. Third: blind H3 settles, gain 0, analyst margin .25. All seven selected calibration/validation scenarios match the actual executable SRG-10 oracle, including 189 initial, 819 fixed-policy and 756 forced-continuation action-value cells. The prior tape distribution is shared; independent decision implementation is the tape-conditioned recursion.

Post-selection envelope: none of the 18 bounded edits passes all seven scenarios; the maximum validation passes for any grid point is two. Do not generalize infeasibility beyond this finite grid. Weakly distinguishing evidence can require changes to reliability, query availability or the observation contract, rather than further manipulation of the reward schedule. This is a failed promotion gate even though calibration succeeds.

## 3. Source-backed Reservoir Dogs ending priority

Use the pinned signed SWMD-SRG/2 migration, not the legacy reader or the production JSON. Direct routing remains explicit as in SRG-05. The only editable field is the additive constant in the secret ending encounter priority Q, originally C(0.22). Search delta in {-0.10,-0.05,0,0.025,0.05,0.075,0.10,0.125,0.15,0.20,0.30}. Other weights, gates, reaction scores, all 690 original effect assignments, routes, prose and state declarations remain frozen. The candidate does not force the secret ending if its numeric acceptability, time and spool gates fail.

For each campaign, stop at the first sirens encounter and enumerate every legal option's selected reaction and wild candidate set; all three options are legal at these sampled roots. Use xorshift32 with 24 fixed draws per campaign and floor(u*n) action-index mapping. At a root, an opportunity means at least one legal action's immediate next encounter is the target; uniqueness means exactly one legal action reaches the target immediately. This is not full-horizon reachability or a moral preference for an ending. For target-winning actions, measure priority margin against the next highest eligible candidate. No target-eligible alternative alone implies a player can select it directly: reaction choice remains endogenous. Scope constraint: no changed selected destination unless the original or new destination is the target.

The design contract: 12.5%-20% first-sirens roots have an immediate target opportunity; at least 70% of these opportunity roots have a unique winning action; at most 20% of target-winning actions have priority margin <0.03; scope constraint holds. Minimize |delta| subject to all. The opportunity range is for one-step decision opportunities, not a desired campaign ending probability.

Cached ranking search adds delta only to the target's eligible wild priority. Compare the selected compiled source to actual SWMD audit packets to verify ranking, candidate eligibility, selected reaction and numerical effects. Actual re-evaluation is important because floating-point association may differ; max observed score discrepancy is 1.11e-16 and no rank mismatch occurs. The one semantically inert priority wrapper ADD(Q,C(0)) preserves all sampled original outcomes.

Calibration (seed 0x53521101, 128 campaigns): baseline 9 opportunities, 7 unique, 12 winning actions, 4 low-margin; selected +0.075 (C(0.295)), the only passing grid point: 21 opportunities, 16 unique, 30 winning actions, 5 low-margin. The 384 legal action instances have unchanged numeric successors, squared step energy, eligibility sets and reaction selections; 18 change route to target. All source lines except the target Q line are identical.

Frozen validation, two new xorshift streams, 256 campaigns each:
| Cohort | Original opportunity rate | Candidate opportunity rate | Unique fraction candidate | Low-margin fraction candidate | Pass |
|---|---:|---:|---:|---:|---|
| Seed 0x53521102 | 19/256 | 33/256 | 20/33 | 12/57 | FAIL |
| Seed 0x53521103 | 23/256 | 34/256 | 22/34 | 10/58 | FAIL |

Both cohorts meet opportunity range and scope; both fail uniqueness (60.6%,64.7%), and the first fails the margin threshold (21.1%). Over 1,536 validation action instances, all reaction scores, selected reactions, writes, candidate eligibility and numerical successors match baseline; 59 selected routes change. This is equality of the immediate numeric state, not equality of the subsequent campaign trajectory once a route changes. No new effects, flag writes, or relaxed gates were introduced.

Full validation campaign replay: all 512 baseline and candidate campaigns complete within the registered 24-action budget. Secret endings 57 -> 83, 26 changed endings and 29 changed complete paths, zero changes to pre-first-sirens prefixes. The same random word is used by decision index, so actions after route divergence can have different semantics. Counts are descriptive deterministic replays, not a general estimate of how human players act.

Post-selection grid diagnostic: zero of the 11 bias values meet all validation constraints; indeed neither validation cohort has a passing bias. Uniformly raising a terminal priority can increase opportunities but make multiple player actions converge to the same ending. This is precisely the authoring failure the uniqueness constraint was designed to catch. Do not replace the original production world with this failed candidate. A next bounded edit should adjust local reaction consequences or the existing causal weights so the desired ending is earned by identifiable choices, with matched no-op and scope controls, then use fresh independent validation. Do not use the already inspected validation cohorts as a new holdout.

## 4. Formal interpretation and limits

An outcome gate and a desirability score play different roles: eligibility defines a feasible region; relative priority partitions that region into actual reachable successors. The SRG-06 goal-region distance can decrease while the chosen ending remains unchanged. In SRG-11 the priority-only candidate leaves Dirac effect vectors and their energy exactly unchanged at the audited decision, while changing the downstream partition. Thus an authoring metric must separately constrain geometric effects, causal choice discrimination and route margins. A constant priority shift cannot add a missing cue or create a new action-specific interaction. The current prototype measures an actual authored ending, but it does not validate its dramatic or moral appropriateness. Author intent and weights require review.

## 5. Reproduction

From EvalMath root:
    node integrations/sweepweave-ts/srg11/verify.mjs

The verifier checks pinned source Git blobs and regenerates the main receipt and candidate artifacts. The optimizer and source-level experiments ran in an isolated ECMAScript runtime from connector-fetched sources; standalone Node file execution is still pending. The separate srg11_envelope.json records the executed post-selection diagnostic, not an additional promotion test. No production SWMD/TS editor changes, GPU calls, or model training occurred. No Godot dependency.

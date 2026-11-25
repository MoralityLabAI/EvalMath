# SRG-09: Correlated evidence, observer ownership and nonlinear reaction margins

2026-11-25. Evidence: exact integer-mass finite belief-state oracle and deterministic SWMD-SRG/2 execution, plus binary64 dyadic interaction tests. No model inference, training, editor integration or Lean proof was executed.

## 1. Noisy sources and conflicting reports

Let T,Z be independent uniform signs, denoting objective truth and Bob's reporting stance. Alice's report A matches T with probability 6/8. Bob's first report B matches TZ with probability 7/8; conditional on T,Z, his second report D is either an independent report of the same reliability or an exact copy of B. The reviewer report M matches Z with probability 7/8. Conditional likelihoods multiply only when the specified conditional independence holds. In the copy variant D=B is a deterministic constraint. The source type is unobserved.

Enumerate every sign assignment with positive likelihood. Four prior states times a common noise denominator of 8^4 yields total integer mass 16384, represented by 64 distinct roots in the independent case and 32 in the copy case. These are exhaustive weighted finite supports, not 96 independent observations. The world stores latent truth, stance and reports under distinct keys. Forced reads expose only four public registers; exact audit exposes truth only after the decision to audit. Both the source and payoff contract are explicit.

For observation o define N(o) as its mass and P(o) as the mass where T is positive. The two commitment values are 8P and 8(N-P), settlement is 5N, and audit is 6N with two remaining actions (zero with one). The expectation is their maximum divided by N. The general weighted belief-state recurrence is
    W_h(B)=max_a sum_o W_(h-1)({(T(s,a),m_s): (s,m_s) in B, O(T(s,a))=o}).
Terminal cells sum reward times mass. The current experiment compares an actual SWMD recursion against an independently enumerated likelihood table for every observation and budget; all match. Observation cells are separated by the full public observation; hidden source assignments and random tapes never enter the player packet.

With p=P/N and signed posterior margin m=2p-1, best direct commitment value is 4(1+|m|). At budget one, commitment beats settlement when |m|>1/4, with equality a tie. With exact audit available at budget two, commitment beats audit when |m|>1/2. These are design-specific thresholds derived from the explicit payoffs. They do not depend on source prose or an inferred moral utility.

| Policy | Independent, H=1 | Copy, H=1 |
|---|---:|---:|
| Majority of A,B,D | 4.4375 | 4 |
| Ignore reviewer M, optimized over other evidence | 6 | 6 |
| Assume Bob reports are independent | 6.6875 | 6.25 |
| Correct joint model | 6.6875 | 6.484375 |

With audit at H=2, correct value is 6.84375 in both noise modes; removing M gives 6. The extra report is therefore useful only according to its conditional dependence and utility threshold. The equality of the two full-horizon values is specific to these priors/payoffs, not a theorem that duplication is harmless.

## 2. Observer ownership and causal provenance

The intended read is analyst.stance[reviewer][bob], a second-order attributed report. The matched distractors are observer.stance[reviewer][bob] (wrong owner) and analyst.stance[bob] (wrong depth). Their tape values are deliberately the negative of the intended report. This is a controlled authored encoding, not a general epistemic law about pValues.

The correct source remains invariant on 192 single-distractor interventions. The known-inversion variant preserves optimal utility when the inversion is part of the declared model; mistakenly interpreting the wrong source as the correct source reduces expected utility at H=1 to 2.1875 (independent), 4.515625 (copy). This separates invertible representation changes from silent misattribution. Removing the report loses information. An author must specify ownership and evidence access, rather than infer them from a numerical correlation.

Six scoped author repair cases replace the intended reviewer transfer with a wrong-owner, wrong-depth or missing-value read under each noise mode. The player-facing prose continues to specify the correct model; the author is explicitly given the intended p2Value key and allowed to edit only the relevant effect expression.

All 288 tape-level repairs pass. The defective sources and semantically inert shams pass zero on those tapes. Four negated-alias patches would also pass the original tape checks, since -wrong equals intended there. For each original root independently intervene on the three relevant key values over their full 2^3 sign cube; these are bounded counterfactual inputs, not necessarily probability-supported tapes. The strengthened gate also inspects the compiled expression read set, requiring exactly the intended owner/property/keyring. All six gold patches pass 2304/2304 counterfactual checks and exact provenance. All four negated aliases pass half their intervention cases and fail the contract. Shams pass 768/2304 counterfactual checks and zero contracts. An extra-write injection is rejected in each case. This is finite causal/source validation on the registered domain, not general equivalence for every possible expression or proof of subjective belief semantics.

## 3. Precision and nonlinear decision margins

For K=4,8,16 use K/2 pairs of first- and second-order numerical cues u_i,v_i. The authored contrast is
    F(u,v)=sum_i (s_i u_i v_i + u_i/4), s_i in {-1,+1}.
Two reaction scores are common + F/2 and common - F/2. First reaction wins ties. Both effects have equal squared energy 1/16. The shared term is a nuisance read: changes to it cancel exactly on the tested dyadic domain. A wrong-owner second-order coordinate is initialized to -v_i in the matched mutation. A linear-only mutant removes the product terms. Every semantic coordinate has a one-coordinate relevance witness at bounded intervention roots. The 28 witnesses certify relevance, not equal influence under a distribution.

| K | Probes | Wrong-owner selected-reaction flips | Linear-only flips |
|---:|---:|---:|---:|
| 4 | 512 | 373 | 197 |
| 8 | 512 | 387 | 211 |
| 16 | 512 | 386 | 194 |

Across 1536 dyadic probes, compiled correct, wrong-owner and linear-only results match their independent numerical references; changing unrelated owner values or the common term leaves all original selections unchanged. These are source-specific deterministic samples; the engineered anticorrelation is a stress condition, not an estimate of natural authoring error rates.

For coordinate errors delta_u,delta_v bounded by epsilon, the elementary bilinear expansion and triangle inequality yield
    |F(u+delta_u,v+delta_v)-F(u,v)|
       <= sum_i [|u_i| epsilon + |v_i| epsilon + epsilon^2 + epsilon/4].
If |F| is strictly greater than this bound, the selected reaction cannot change under that perturbation. The bound is sufficient, not necessary; ties and near-zero margins require separate handling. Check the actual SWMD transition at every quantized reconstruction. All 7680 runtime checks agree and there are zero bound violations. At K16 with 5-bit midpoint reconstruction 382/512 probes satisfy the conservative margin certificate; 13 decisions flip, all uncertified. At 3 bits the sample grid is represented exactly and zero decisions flip; at 4 bits midpoint reconstruction can shift even an exactly represented 3-bit center. The point-reconstruction flip rate is therefore not a monotone precision guarantee, even though the observation partitions refine.

For the evidence task, group exact posterior p by fixed dyadic interval index floor(2^b p), with endpoint clipping. Recompute the best common action in each group using exact weighted mass; these nested partition ceilings are monotone. At H=2 for both modes the zero-bit value is 6 and two bits attain the full 6.84375 value on this posterior support. Do not conflate an optimized coarsened information partition with evaluating a fixed formula on rounded coordinates.

## 4. Public diagnostic and evaluation contract

Public evidence rows enumerate 168 weighted decision cells across eight world configurations and two horizons. Score legal selected action against the oracle tie set and compute expected utility and regret weighted by the cell mass. Missing, rejected or duplicate responses receive zero utility; unknown IDs are listed separately. The scorer assumes optimal continuation after the submitted first action. Its gold control gives 168/168 optimal actions and zero regret over total mass 262144; majority vote gives 94/168 optimal actions and nonzero regret numerator 607488. The author scorer enforces the strengthened provenance contract, with observational and intervention coverage reported separately.

The fixed evidence family, task files, gold and source definitions are public. They are a diagnostic suite, not a sealed evaluation. Do not add these calibration labels to a compact model's training corpus and then claim generalization on the same suite. SRG-08's training-only export remains separate.

Use the SRG-09 local stage and scorer with the SRG-08 loopback runner (planning mode) for Bonsai or Inky. The author repair task requires a line-patch submission; the SRG-08 Boolean synthesis runner is not compatible with it without a prompt adapter. See README. The verifier replays the pinned source and public data. The exact JS source was executed in an isolated ECMAScript runtime, not standalone filesystem/HTTP mode. Production SWMD editor, model checkpoints, Data Goblin training corpus and real model scores are unchanged. No Godot dependency.

## 5. Next gate

SRG-10 should move from a single public probability model to independently authored families with calibrated source reliability, common-cause and temporal evidence variation; add observer-specific observation functions, weighted metric priors and semantic authoring constraints. Pre-register fresh hidden reliability configurations and probe interventions before local model evaluation, while retaining the exact conditional-likelihood and provenance baselines. Distinguish goal utility, belief reliability, K, precision, inference passes and externally constrained memory.

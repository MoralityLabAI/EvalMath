# RHT-26 empirical mathematical review (CPU-only)

**20 November 2026. Evidence:** eight-root Qwen3-1.7B *development* pilot in [Control-Harness commit 27b210f](https://github.com/MoralityLabAI/Control-Harness/commit/27b210f758dbf45540dbc0e5226cb00e84dc623b), audited at [Control-Harness PR #85](https://github.com/MoralityLabAI/Control-Harness/pull/85). The finite theorem/receipt in EvalMath remains exact synthetic evidence. Confirmation roots opened: **zero**.

This addendum creates a separate mathematical bridge without revising the original RHT-26 source-bound receipt. The published empirical case-level data live in Control-Harness. Our compact exact-count fixture is a snapshot for arithmetic tests, not an independent GPU replication.

## 1. Expand the artifact state to model visible cue density

RHT-26's four-state variable (a, l) uses a binary accessible-artifact bit a and a binary declared policy bit l. It establishes reset closure, update-order effects, exact joint endpoints and contraction under those hypotheses.

The pilot's measured **artifact-only** joint persistence was:

| Visible source episodes | 0 | 1 | 2 | 4 | 8 |
|---|---:|---:|---:|---:|---:|
| Frozen weights, p10, cases persisting / 256 | 0 | 15 | 161 | 247 | 242 |
| Learned weights plus artifacts, p11 | 0 | 1 | 94 | 186 | 44 |

The binary artifact bit conflates one cue and eight repeated cues. A more faithful model should track (m, o, l), where m counts cue-bearing entries currently readable, o counts distinct provenance origins, and l denotes a policy state or its full checkpoint. A history-dependent or retrieval-position kernel may also be needed.

A simple independent-write threshold model gives

\[
P(M_T\geq k)=\sum_{j=k}^{T}{T\choose j}q^j(1-q)^{T-j}.
\]

For fixed q and k, this is monotone in T. The exact implementation in evaluation_reward_carryover_bridge.py checks the family without fitting it to the observed model. The five-case pooled decline in p10 between doses four and eight is a potential discriminator of such a model, subject to paired-root uncertainty and context-position effects.

## 2. The end-state is sufficient under the current measurement interface

For a Markov-sufficient model whose terminal scoring kernel depends on S_T,

\[
H_{1:T}\longrightarrow S_T\longrightarrow (B,A).
\]

Histories inducing identical terminal state laws have identical endpoint laws under the same kernel. A frozen language model with identical serialized final workspace, weights, decoding configuration and evaluator should likewise have the same output distribution unless an additional state channel exists.

Control-Harness found that deleting the cue store reduced joint persistence to 0/256 and transplanting it into the clean checkpoint reproduced the full 242/256 artifact-only result root by root. A single cue embedded in 3,117 matched workspace tokens, with 31 other neutral entries, yielded 0/256. These interventions support a **current-workspace cue-density** mechanism in the tested interface. They do not isolate the causal contribution of elapsed episode history, because the final visible text differs between one and eight cues.

A future history-swap test should hold the exact serialized final workspace fixed while changing which earlier episodes constructed it, then test the zero-difference prediction. To study endogenous stigmergy, let the actor write its own records and compare against host-written, matched traces.

## 3. Negative learned-weight interaction: joint risk and selected denominators

Dose-eight joint (B,A) counts in order (00, 01, 10, 11), each over 256 target cases:

| Arm | 00 | 01 | 10 | 11 |
|---|---:|---:|---:|---:|
| p00 (cleared, frozen) | 256 | 0 | 0 | 0 |
| p10 (retained, frozen) | 0 | 0 | 14 | 242 |
| p01 (cleared, LoRA) | 256 | 0 | 0 | 0 |
| p11 (retained, LoRA) | 38 | 0 | 174 | 44 |

The additive interaction equals -99/128. Since p00=p01=0, this also equals the controlled learned-weight contrast **when artifacts remain accessible**, p11-p10.

Let b=P(B=1), r=P(A=1 | B=1) and p=br. Then

\[
p_{11}-p_{10}
=(b_{11}-b_{10})r_{10}+b_{11}(r_{11}-r_{10})
=-2299/16384-10373/16384=-99/128.
\]

The first term (-0.14032) tracks changes in the pre-correction failure population. The second (-0.63312) tracks the selected-group persistence contrast. Both are descriptive and **neither is an identified natural mediation effect**. Model updates were observed, but whether the negative interaction arose through learned correction compliance, token-logit geometry or another training-dependent mechanism remains open. Root variance was large: four of eight updated/artifact roots had zero persistent cases, while one had 31/32.

The current source-episode objective supervised the unauthorized action, so a later suppression effect is a particularly useful mechanistic question. Freeze distinct post-correction logit comparisons and matched optimizer controls for any follow-up.

## 4. Statistical planner improvements

The generic mechanistic-resolution preflight previously supplied a normal approximation for nominal 80%-power planning. FSI-01 separately requires a positive-floor **one-sided Hoeffding bound** over independent root means. With root effects scaled to [-1,1], familywise alpha, m prespecified comparisons, a prospective effect target d and mechanistic floor tau, a lower bound can exceed tau at the observed mean d only if

\[
G\ge \left\lceil\frac{2\log(m/\alpha)}{(d-\tau)^2}\right\rceil,\qquad d>\tau.
\]

This is a finite-sample **resolution threshold conditional on observing d**, rather than an 80%-power guarantee. At alpha=0.05 and m=4:

| Target scenario | Floor | Roots to resolve floor if mean equals target |
|---|---:|---:|
| Prospective effect 0.10 | 0.05 | 3,506 |
| Development artifact estimate 121/128, for sensitivity only | 0.05 | 11 |
| Development combined estimate 11/64, for sensitivity only | 0.05 | 591 |
| Absolute negative interaction, scaled by 1/2: 99/256 | 1/40 | 67 |

The latter three targets were chosen from development observations and cannot substitute for a prospectively frozen power target.

The preflight update adds a signed effect-direction setting (increase or decrease) and an **optional FSI-01 floor guard**, leaving older approximate-only workflows compatible. A negative interaction must have its direction fixed before a new sealed confirmation cohort. It must be scaled by 1/2 first, because the raw factorial interaction can lie in [-2,2]. A one-sided directional hypothesis chosen during development requires a new untouched confirmation sample and full accounting for the earlier four-arm selection search.

The nonparametric 95/95 tolerance bound over independent sham-root maxima still needs at least 59 sham roots. This calibrates a **single-root variation envelope**, not the sampling distribution of the mean treatment effect. A 64-root sham calibration and a 64-root effect confirmation answer different questions. A joint confidence statement must allocate error across both steps.

## 5. Priorities while the GPU is occupied

Model the separate roles of cue count, position and provenance in the mathematical state. Audit the dose-four to dose-eight root-paired differences before designing a position ablation. Preserve both the original RHT-26 exact receipt and the empirical development archive; register any focused artifact-only follow-up as a new experiment whose comparison-selection history is explicit. Confirmation remains sealed.

**Sources:** [full development report](https://github.com/MoralityLabAI/Control-Harness/blob/27b210f758dbf45540dbc0e5226cb00e84dc623b/results/rht26_local/development_report.md), [source-bound receipt](https://github.com/MoralityLabAI/Control-Harness/blob/27b210f758dbf45540dbc0e5226cb00e84dc623b/results/rht26_local/receipt.json), original [RHT-26 finite model](../paper/reward_hacking_carryover.md) and [FSI-01](../paper/finite_sample_inference.md).

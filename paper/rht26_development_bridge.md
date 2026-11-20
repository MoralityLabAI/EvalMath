# RHT-26 development bridge: cue multiplicity, snapshot sufficiency and inference resolution

**20 November 2026. Status:** mathematical extension and audit of the eight-root
Qwen3-1.7B *development* pilot. The original RHT-26 exact receipt at
`output/evaluation_reward_carryover/rht26_v2.json` remains pinned and unchanged.
This note is subsequent analysis, not a retroactive amendment to the original
prospective protocol or a confirmation result.

**Sources:** [RHT-26 exact finite note](reward_hacking_carryover.md),
[FSI-01](finite_sample_inference.md),
[Control-Harness development report](https://github.com/MoralityLabAI/Control-Harness/blob/27b210f758dbf45540dbc0e5226cb00e84dc623b/results/rht26_local/development_report.md),
and its [independently replayed archive, PR #85](https://github.com/MoralityLabAI/Control-Harness/pull/85).

## 1. What the original two-bit state leaves out

The original artifact/policy state `(a,ell) in {0,1}^2` can
represent the **presence** of a cue and one policy state. At frozen weights,
once `a=1`, another retained cue still projects to `a=1`. A fixed
terminal endpoint law `Q_(a,ell)` therefore gives the same joint persistence
risk for one and eight cues if `ell` is fixed and all other relevant state
is equal. This is a direct consequence of the chosen projection.

The completed development cohort found joint persistence for the frozen
artifact arm at exposure doses `0,1,2,4,8` of, respectively,
`0/256`, `15/256`, `161/256`, `247/256`, `242/256`.
The observed effect is close to saturation, with a small decrease between
doses 4 and 8. These are *fixed-checkpoint development observations*;
32 target cases per root do not create 256 independent training lineages.

A minimal count augmentation is `n in {0,...,8}`, with
`n' = min(8,n+X_t)` and `P(X_t=1|n)=lambda`. Its exact law for
`T <= 8` is binomial `P(n=k)=C(T,k)lambda^k(1-lambda)^(T-k)`
when started at zero. An endpoint `q_n=P(B=1,A=1|n)` may depend on
multiplicity. The original binary projection `a=1{n>0}` discards that
dependence. The CPU-only [finite bridge](../src/spiral_ln/evaluation_reward_carryover_count.py)
and [tests](../tests/test_evaluation_reward_carryover_count.py) verify this
mathematical distinction. The displayed synthetic endpoint is illustrative;
it is not a fitted law for the Qwen observations.

The updated-policy arm adds a separate dimension: optimizer depth/trajectory,
not merely the binary `ell` flag. The measured `p11` risk rose to
`186/256` at dose four, then fell to `44/256` at dose eight.
A model that aims to describe this trajectory should carry enough policy
state to distinguish its intermediate checkpoints, and use observed
intervention data to estimate its transitions.

## 2. Terminal snapshot sufficiency limits temporal claims

Let `H` be a source history, `theta(H)` its final model parameters,
`S(H)` its final visible store, and `x` a fixed target task.
Suppose the fresh target agent is evaluated from a reset context using a
shared terminal kernel

```
P((B,A)=y | H,x) = Q(y | theta(H), S(H), x).
```

If histories `H` and `H'` end at exactly the same
`(theta,S,x)`, then their conditional target-outcome distributions are
identical. Proof: the right-hand sides have identical arguments. The
statement requires the terminal tuple to contain every relevant channel,
including RNG state and caches if those are persistent.

In the Control-Harness frozen-weight arm, the runner begins each source
episode with a fresh task context, injects the cue records through the
**harness** before model generation, and keeps the model parameters fixed.
The final store is therefore the intended transmission channel. The actor
was not observed to write the cue as an autonomous strategy.

The exact artifact transplantation result (242/256 in both in-situ and
transplanted stores, identically for all eight roots) verifies the expected
behavior under fixed checkpoint and identical final store. Deleting the
store restores clean behavior. The one-versus-eight cue control has the
same final store token budget and 32 occupied record slots, but changes
the number of active instructions. It identifies an effect of **final
workspace cue density / repeated instructions**. The temporal history
that led to the store remains unidentifiable from that contrast alone.

A further experiment can distinguish temporal effects by holding the *exact
final bytes*, model parameters and target fixed while varying past histories
or additional retained channels. An endogenous-stigmergy experiment must
also let the agent choose whether to create the artifact. These extensions
are scientific design changes, not conclusions from this pilot.

## 3. The finite-sample gate that the normal planner omits

The current `evalmath-mechinterp-power` planner estimates normal-theory
sample size using measured root variation. FSI-01's **positive-effect-floor**
decision uses a separate conservative guarantee. For a root effect in
`[-1,1]`, family size `m`, error `alpha`, scientific/noise
floor `tau`, and a future observed root mean `dbar`, the final
one-sided lower bound is

```
L = dbar - sqrt(2 log(m/alpha)/G).
```

The final gate requires `L > tau`. A prospective target effect `delta`
can clear it only when

```
G > 2 log(m/alpha) / (delta-tau)^2,
```

where `delta > tau`. With `m=4`, `alpha=.05`,
`tau=.05`, and the *original planning target* `delta=.10`,
at least **3,506 independent roots** are required. An interaction on
`[-2,2]` must be halved before using the same formula; for the raw
.10/.05 values the requirement is **14,023** roots.

At 64 roots and four comparisons, the root-bound radius is about 0.370;
the target effect must exceed about **0.420** for this particular FSI
decision gate. An independently reproduced effect near the observed
artifact pilot mean `121/128` would comfortably clear that numerical
condition. The 8-root estimate is exploratory and cannot substitute for
a new prospective target commitment or independent confirmation readout.

The updated planner exposes `fsi01_final_effect_floor_resolution` and
can enforce it using `require_final_fsi_gate: true`. Historical clients
retain the prior normal-planning behavior by default.

The sham floor remains uncalibrated with eight roots. The registered
95%/95% nonparametric tolerance bound needs at least 59 independent
calibration roots, one family-wide maximum per root across the registered
contrast family after the interaction's half-scale transform. A focused
single-contrast confirmation requires an explicitly new frozen manifest
documenting its development-stage selection, and new unexamined confirmation
roots. Sham calibration from a reduced intervention family answers that
reduced question.

## Test commands

```bash
python -m unittest discover -s skills/evalmath-mechinterp-power/scripts -p 'test_*.py' -v
PYTHONPATH=src python -m unittest tests.test_evaluation_reward_carryover_count -v
python scripts/check_receipts.py --only reward_carryover
```

No GPU or neural model is required for these checks.

# NW-01: exact paired-world information boundary for recurrent witness models

## Source contract and evidence class

This note supplies **exact finite arithmetic** for the [NW-01 recurrent-model pilot](https://github.com/MoralityLabAI/LoopedTransformers/pull/171) using 64 publicly completed clean/hidden source pairs from [NOR42](https://github.com/MoralityLabAI/Compactification-Theory/blob/0a330602c72ec34017178857956e306710f724a1/research/nor42_paired_program_ood/prospective/RESULTS.md). The paired NOR42 program-grammar OOD result was originally registered and independently replayed over 64 public sources and 128 true worlds. The first original public source SHA is `f8bc6ef3db4fda78709f2b7cd1a6a09989dbc087bcfb963d00961cc23ce4f033`, and the original grade SHA is `bd57751d94ea49755888000675b0df8fce6490873683268b8f8625518701adae`. The full source/grade ZIP is frozen at `e60e97fd933f660c2274cb4a473ede7a98968d24eaf0dd3ae45ace1e1176cd0d`.

The formal paired public-prefix indistinguishability theorem is in [MathCan NOR42HiddenSuffix](https://github.com/patrickdugan/MathCan/blob/main/MathCan/NOR42HiddenSuffix.lean), merged at `748bddf39d868e9658d31aab0f3f5fa71ddadae8`. The exact results here are about **information supplied to a verifier**, independent of whether a neural model learns the right operation. An empirical recurrent decoder or causal intervention requires separate source-disjoint training/evaluation and dose-matched sham controls.

## The equal-prior paired root

Let source root `s` have the same public observations `X_s` under clean world `Y=0` and hidden world `Y=1`, each with probability 1/2. The hidden program differs after the public prefix by a suffix `β X^(D+32) T(F)`, with nonzero β and normalized `T(F)_0=1`. Suppose a deterministic public-only estimator issues a binary decision `d(X_s)∈{0,1}`. The root contributes exactly one correct label among the two possibilities:

`[d(X_s)=0]+[d(X_s)=1]=1`.

For any number n of independent source roots, the complete paired set has `n` correct predictions among `2n` worlds, giving **exact accuracy 1/2**. This is a same-observation theorem: a longer recurrent depth can change `d(X)` as a function of X, but it cannot give different decisions for the two worlds in the same pair without a further observation or asymmetric input.

If a public-only model reports hidden-world probability `p_s=P(Y=1 | X_s)`, its equal-prior pair-averaged binary Brier loss is

`B_s(p_s)=0.5 p_s²+0.5(1−p_s)²=1/4+(p_s−1/2)²`.

It has exact lower bound **0.25**, attained precisely at `p_s=1/2`. The complete source-root mean is `1/4+(1/n) Σ_s (p_s−1/2)²`. Therefore a public model may have **exactly 50% matched-pair accuracy and still be miscalibrated**, with Brier excess quantifying its unwarranted confidence.

## Different information inputs

An additional independently authenticated coefficient observation at D+32 can return a signed residual `δ=0` in the clean world and `δ=β≠0` in the hidden world. A deterministic checker `d(δ)=[δ≠0]` has **exact paired accuracy 1**. This is a *conditional oracle law*: the theorem assumes the true coefficient is independently authenticated. Constructing a deployed proof or trusted witness is outside the current NW-01 task.

A source-matched sham residual `δ'_s`, even if it has the same marginal distribution as authentic residuals, is presented **identically** to both paired truths. Every deterministic decision made from `(X_s,δ'_s)` again gets exactly one label correct and one wrong, leaving paired accuracy at **1/2**. Its average Brier can exceed 0.25 if a model falsely treats the sham as identifying evidence.

If a tied recurrent model receives the authentic residual only at pass zero, future passes can transport the information in their hidden state. A donor swap of the whole state between two paired worlds is an intervention on **the informative state**, and its observed final-logit effect tests whether the model uses that state. State-swap effect alone is weaker than a named BPD component certificate, because exchanging the full state can alter many circuits. Register the matched opposing-world donor *before* scoring, include an identity patch and an L2-dose-matched random vector control, and require the next readout to remain on the same input.

## Source-root statistics and prospective resolution

NOR42 contains **64 source pairs grouped into 16 original generator replicate blocks**. Both worlds in a pair share a root; samples across recurrent depth and many intervention directions are repeated views of the same source. The independent-root count for within-family generalization must therefore remain 64, with 16 replicate-block sensitivity units. An observed 128-row accuracy report does not give 128 independent root observations. More loops and multiple decoders do not increase the source count.

The [NW01 preregistration](https://github.com/MoralityLabAI/LoopedTransformers/blob/research/nor42-recurrent-witness-causal-20261118/experiments/nor42_recurrent_witness_v0/REGISTRATION.md) uses three fixed model seeds and a source-paired causal dose. Its registered practically meaningful intervention effect is a **0.10 absolute logit displacement** above the equal-norm random-direction control, and its source-block t intervals are descriptive. The 64 NOR42 roots were previously published, so NW01's neural evaluation is a *retrospective pilot* even if its model-seed choices and training code were frozen before fitting. Any comparison that selects a stronger learned intervention direction on these same roots requires another disjoint source cohort.

## Reproducibility

The implementation [`spiral_ln.evaluation_nw01_paired_information`](../src/spiral_ln/evaluation_nw01_paired_information.py) uses exact Python `fractions.Fraction`. Its test suite covers the Brier algebra over all rational `p=k/100`, exhaustive `2^10=1024` deterministic public labelings, 64 paired roots under authenticated and sham feedback, finite recurrent depth invariance, and malformed source controls.

```bash
PYTHONPATH=src python -m unittest discover -s tests \
  -p 'test_evaluation_nw01_paired_information.py' -v
```

**Evidence class:** `exact finite domain` for the equal-prior public-only and Brier calculations, `conditional oracle mathematics` for independently authenticated residuals, and **pending separate neural evidence** for the NW01 recurrent-model readout and causal state effects. The MathCan theorem supplies the prior formal equality of public prefixes. No P-value or small held-out sample can upgrade the information theorem to a real authenticated-witness capability.

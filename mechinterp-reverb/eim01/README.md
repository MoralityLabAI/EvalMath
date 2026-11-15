# EIM-01: Evaluation Interventions as Mechanistic Training Signals

This is an executable, bounded prototype connecting EvalMath's mechanism
separation theory to the reviewed BPD implementation in this repository.

**Result (CPU, 2026-11-15):** seven unit tests passed. Independent graph
closure reproduced all 384 host labels in BPD-LG-02. A deliberately
confounded two-component looped toy scored 0/16 on a fourth-family
cue-conflict development set following passive training, and 16/16 after
either selected BPD interchange-intervention training or ordinary
input-level cue augmentation. The two latter arms tie, so causal
interchange training has not yet shown an advantage over simpler data
augmentation.

## Files

- design.py: source-bound signed intervention-effect rows, validation of
  provenance/route/readout/split, exact two-column rank certificate,
  condition number, inverse-problem error bound, finite best-eval selection.
- gym.py: actual graph recurrence; frozen planted shared-factor BPD model;
  same-pass donor activation swaps; rank-selected eval templates; equal
  training-record/update controls; the internally intervened training arm.
- test_eim01.py: independent graph oracle, finite rank, source-gating,
  real causal factor isolation, and held-out-family training comparison.
- paper/eval_to_mechanism_eim01.md at repository root: formal interpretation,
  evidence and failure-to-generalize boundaries.

## Run

At EvalMath root, in Python 3.12 with CPU PyTorch and pytest:

    PYTHONPATH=mechinterp-reverb:. python -m pytest -q mechinterp-reverb/eim01/test_eim01.py
    PYTHONPATH=mechinterp-reverb:. python -m eim01.gym

The hosted workflow is .github/workflows/eim01-eval-mechinterp.yml.

## Experimental validity

- The model's two component directions are planted/frozen, so no discovery
  of BPD parameters is claimed.
- Synthetic cue correlation with the verified source label is intentional
  and motivates an adversarial contrast.
- Evaluation candidates come only from training roots. A proof-family
  holdout is separate within each run, but this cohort was examined during
  development and is not a fresh sealed confirmation experiment.
- Only the readout head is trained. Source/donor pairs are matched on the
  selected pass, and each effect is recorded at the next readout.
- A finite effect matrix having full column rank only identifies
  coefficients in a stipulated linear response model. Neural nonlinearities,
  changing component bases and source-dependent routing require more tests.
- Graph-closure is a perfect zero-neural oracle for these synthetic tasks.

The next experiment should fit a decomposition to an independently trained
looped Lean reasoner, acquire interventions before an untouched family
holdout, and measure held-out counterfactual effect predictions including
joint ablations. Input augmentation and strong symbolic solvers must remain
active controls.

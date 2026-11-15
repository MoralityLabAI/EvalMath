# BPD pre-run amendments from Fable review: 2026-11-15

**Prospective amendments.** The original [registration](registration.md) and [positive-control history](positive_control_history.md) remain intact. This file records changes before any new full-scale GPU experiment. No original thresholds are retroactively loosened.

## Execution order
Run exact synthetic and known-answer gates first (T=1 reduction, stationary B1, LoopedChase B3); freeze item, route, donor, mechanism and readout definitions; test target/collision donor swaps; then run B2 fragility diagnostics and B4 rank-k checkpoint edits. Engineering smokes are separate from scientific acceptance.

## B2 history and scope
The original eight-factor registration named o_proj and down_proj across four Huginn blocks at |z|<=2.5 and K>=16. In historical Run 1, core.0.o_proj reached z=5.0049; subsequent code rescoped to two down_proj factors per block. Tests used 2.8 in place of the registered 2.5. All differences remain visible as post-history changes.

Preserve two expected failures:
- Run 2: real dense amplified component raw=10.1582, rotation null mean=44.9369 (z=-3.2735).
- Run 4: real dense selective component raw=0.6691, null mean=0.5629, z=0.7691.
Run 5 used a sparse one-of-eight phase-locked positive control and passed without changing its z threshold.

The rotation null detects some sparse, phase-locked mechanisms while missing dense mechanisms. Null effects exceeding a real component's raw ablation invalidate using raw-minus-null as a general specialization criterion. Equality of raw and null on HUG-CAL-02 does not establish absence of specialization.

For future full B2 diagnostics, use K=255 RMS-matched rotations. Report upper-tail finite rank p=(1+#null>=raw)/(K+1) with Holm correction across the prespecified factor/pass family, alongside raw, null mean, z and the historical z criterion. K=12 has a smallest rank p of 1/13. The first eight-test Holm threshold at alpha=0.05 requires K>=159 for attainable rejection. Orthogonal RMS-matched rotations and the original aligned component are not necessarily exchangeable, so these ranks have inferential meaning only after that assumption is validated. Non-rejection alone is not evidence of mechanism absence.

The historical raw intervention is zero-subtraction, whereas train-time masks use pass-conditional mean replacement and optional sphere rescaling. Report both semantics. The revised scientific specificity measure is item-contrast donor swapping at matched recurrent passes.

## Minimality change
Under the actual level functional m+beta*m*log2(1+s), mean-pooling over time is neutral to binary temporal splitting when total per-pass usage is preserved. Switch cost can penalize splitting. It dilutes one-of-T usage by 1/T; a mechanism used on one pass in a 336-pass loop pays around 0.3% of the all-pass level charge. Adopt max pooling as the multi-pass default and retain explicit mean for T=1 VPD equivalence and ablation studies. Freeze max-vs-mean and switch-penalty controls before running.

## Local sensitivity and observation policy
Previously, the loss at pass tau was inverse-weighted by tolerance for injecting at tau and observing the *final* readout. This mismatches the measured loss. New training tolerance calibration observes at pass tau; final-readout injection sensitivity is a separately labelled diagnostic. Boundary-state matching now requires explicit readout_or_boundary selection. TRM opts in because inner z_L cycles lack readouts. All pass losses and weights must be logged.

## B4 redesign
Original B4 projects gaoxin492's factor direction onto yagizdevre and transplants the coefficient gap. It had no sham or outcome margin. Prospectively compare unchanged target, positive gap transplant, sign-reversed transplant, and seeded random rank-one directions of equal individual Frobenius edit magnitude. Freeze selected factors on calibration. The positive edit must beat the best comparator by at least 3 percentage points in exact board accuracy at s=64, decrease period-2 oscillation by 3 percentage points against untouched, and lose no more than 2 percentage points at s=16. These are new, stricter registered margins. A random-direction sham matches edit rank and norm, while task-sensitivity matching remains a future control. The code reports gate_b4_passed=null for engineering smokes outside the full horizon.

## Item-contrast primary hypothesis
Capture matched target and collision items, hold route and recurrent pass fixed, swap component activation from the opposite input, and score perturbations at an explicit next readout. The source interface enforces matching of tensor shapes and readout index; source, collision and label integrity remain host responsibilities. Require prediction of held-out fourth-tactic-family intervention effects and previously unmeasured joint ablations. Compare against taxonomy lookup, unrolled VPD, symbolic search, and rotations, with rank and compute matched. Assess stability across decomposition seeds.

## Evidence boundary
Only source edits and archival history are reported here. There is no new model training, pretrained checkpoint intervention, or demonstrated neural BPD mechanism separation. Historical failures remain historical rather than new reruns.
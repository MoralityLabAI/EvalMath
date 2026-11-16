# ROC-01 EvalMath: register and score causal observer interventions

**Public MathCan source pin:** patrickdugan/MathCan at
9ef4328e461d906fdfc0653467520a72d1a34982,
branch research/roc01-unified-observer-card-20261116.
It includes Parts 0–4, report-card code, exact-rational counterexamples,
a Lean finite witness and source-derived NRF v0.4 partial cards.

The canonical physical observer calculation lives in
MathCan/research/observer_calculus/observer_card.py. It measures A, B and C
from the computed-change Jacobian D=T-I and s from OLM-07's output
Gramian H. EvalMath's local roc01_evaluator.py scores the **declared
intervention hypothesis contract** through the existing BPD-01 exact
finite minimum-test-cover implementation.

For five idealized mechanism exemplars, BPD-01 identifies the three-arm
minimum set dark-to-observed, observed-to-dark and freeze-U. Readout ablation
remains mandatory as a control even if omitted from an optimal ideal
separating set. These labels can overlap in actual nonlinear networks, so
this table is a synthetic protocol demonstration, not a measurement
of real trained weights.

The audit_observer_card function refuses to certify a complete report with
missing or blank per-state A/B/C/s/MSE, missing D/H norms, fewer than 100
**distinct** rank-matched random bases, unpublished per-state rows,
unequal task-only training, absent norm-matched random intervention arms,
or an undeclared output. Existing NRF/SPC eight-way random controls fail
this gate. The function treats source publication and control counts as
caller attestations. The public source, checkpoint and null rows require
independent verification before a scientific claim. A categorical
intervention table can be separable while the observer card is incomplete,
so identify_types requires a complete card audit for causal promotion.

Run exact small tests from EvalMath root:

    PYTHONPATH=src:. python -m unittest tests.test_roc01_evaluator -v

For numeric card replay use the public MathCan script and exact source
inputs, including NRF's 1,584 per-state CSV rows and the per-seed paired
W_delta/rho_delta decomposition. The original checkpoint files are not
committed to public MathCan, and the new normalized card/closure sweep
cannot be credited with neural results from those missing inputs.

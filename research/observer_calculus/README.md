# ROC-01 EvalMath: register and score causal observer interventions

**Public MathCan source pin:** patrickdugan/MathCan at
37bbac210c175ccb98e0ff0d4aa8bdd2be0764e6,
branch research/roc01-unified-observer-card-20261116.
It includes Parts 0–4, report-card code, exact-rational counterexamples,
a Lean finite witness and source-derived NRF v0.4 partial cards.

The canonical physical observer calculation lives in
MathCan/research/observer_calculus/observer_card.py. It measures A, B and C
from the computed-change Jacobian D=T-I and s from OLM-07's output
Gramian H. EvalMath's local roc01_evaluator.py scores the **declared
intervention hypothesis contract** through the existing BPD-01 exact
finite minimum-test-cover implementation.

For five idealized mechanism exemplars, BPD-01 identifies one three-arm
minimum set as dark-to-observed, observed-to-dark and **observed-to-observed**. Two other size-three covers exist. Readout ablation remains mandatory as a
control even if omitted from one ideal separating set. Under a *physical*
freeze-U intervention, both A and B are removed together; the invariant
subspace and register signatures become indistinguishable. Thus the frozen
freeze-U four-arm table does not separate all five synthetic types. The
corrected selective within-observed arm and its exact KL allocation are
specified in MathCan's dated ROC01_AMENDMENT_2026-11-16C.md. These labels can overlap in actual nonlinear networks, so
this table is a synthetic protocol demonstration, not a measurement
of real trained weights.

The audit_observer_card function also requires the rank-specific null median,
a six-direction Holm-corrected p-value family and a verified rank-relative
B penalty, as stipulated by amendment C. It refuses to certify a complete
report with
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

## ROC-02 protocol boundary (amendment C, 2026-11-16)

The original ROC-01 registration and Part 4 remain frozen for provenance.
Prospective ROC-02 uses ranks {1,2,3,4,7,8,12,16,32}, with SPC rank 7
included explicitly. The new tag gate compares a,b,c,s against 128
rank-matched null bases on the same frozen state, rather than applying the
old absolute thresholds. Null degeneracy returns unclassified, and the
penalty uses squared B divided by its own rank-conditioned median.
A checkpoint-free demonstration or a caller-attested complete card remains
synthetic until its per-state null rows, checkpoint, observer, H and decoder
measurements can be independently replayed.

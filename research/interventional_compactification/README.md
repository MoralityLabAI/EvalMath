# Intervention-preserving compactification

Research import, 2026-10-28. Canonical mathematical note and exploratory Python reference for the Petersen–Zech / EvalMath reduction work.

## Evidence and ownership

[RESEARCH.md](RESEARCH.md) contains handwritten proofs under stated hypotheses, the source crosswalk, and an experiment proposal. The Python reference supplies five synthetic floating-point tests. The source-hashed [receipt.json](receipt.json) records their local replay. Lean compilation and real-model experiments are unperformed; repository-wide CI is outside this receipt.

This imported research sandbox is separate from EvalMath's exact-arithmetic production modules under `src/spiral_ln`. Its Euclidean norms and concentration formula use ordinary floating-point arithmetic. The tight-rollout test uses `assertAlmostEqual(..., places=12)`. Numeric outputs are exploratory estimates; they carry no outward-rounding or interval certificate. In particular, the phrase “certified lower bound” in the original reference docstring describes the real-arithmetic inequality, whose floating-point evaluation needs a separate rounding audit.

The [Compactification-Theory companion](https://github.com/MoralityLabAI/Compactification-Theory/blob/main/note/intervention-preserving-compactification.md) owns the capacity/precision interpretation. Its [experiment protocol](https://github.com/MoralityLabAI/Compactification-Theory/blob/main/experiments/interventional-compactification/README.md) specifies prospective SAE/VPD/percolation comparisons and points back to this implementation. Existing EvalLang owners retain their language and implementation work. E10's frozen selector comparison remains unchanged.

## Contents and replay

- `RESEARCH.md`: fiber obstruction, approximate factorization, behavioral quotient, trajectory bound, covering-number adaptation, falsifiers, and Lean handoff.
- `reference.py` and `test_reference.py`: the original v0.1 numeric reference and its five tests.
- `verify.py`: regenerates or checks the source-hashed receipt and fails on a failed, skipped, missing, or extra test.

From the repository root:

```bash
python -m unittest discover -s research/interventional_compactification -p test_reference.py -v
python research/interventional_compactification/verify.py --check
python -O research/interventional_compactification/verify.py --check
```

Regenerate after a reviewed source change with `python research/interventional_compactification/verify.py`. The repository's central `scripts/check_receipts.py` and CI configuration are unchanged; use the explicit command above for this research import.

## Scope before promotion

The state must include everything needed for the declared transition semantics: KV caches and positions for token processing, and optimizer/RNG state when a training process is modeled. Specify the intervention-closed domain and its reachable horizon. A finite cached pool certifies closure only when every specified successor is represented.

“Compactification” here names representation reduction. The quotient construction alone establishes neither topological compactness nor finite dimension. A finite-horizon equivalence consumes remaining horizon under a transition; a same-horizon quotient requires an additional congruence argument. Decidable EvalLang claims additionally need an effective representation and decision procedure.

A worst-case causal certificate needs certified bounds and coverage. Held-out averages support the named sampling distribution. Argmax preservation in a closed loop requires a margin check at each decision, together with compatible tie and action semantics.

Promotion into `src/spiral_ln`, `tests`, `scripts`, `output`, and `paper` should add exact-rational deterministic fixtures, fail-closed numeric validation, a rounding policy for irrational norms/concentration terms, and the normal central receipt integration. Lean claims must follow the existing theorem-fidelity process. This import makes no new implementation claim for EvalLang.

## Provenance

Imported from the conversation artifact `evalmath_interventional_compactification_v0_1.zip`.
Archive SHA-256: `167318ff77024f8909354e4372ff76aef66307759e2034a123b3581a6da1eb40`.
`reference.py` and `test_reference.py` retain their original bytes. The research note adds an import-status paragraph; mathematical sections retain the v0.1 text. The source map belongs to that research note and has not been re-audited during repository publication.

Repository baselines inspected before publication:

- EvalMath `main`: `80cea8fcf0a3eb8f560e9ba37fa21000d2a0b463`.
- Compactification-Theory `main`: `f33f6db451c081a8a4ec8c92f81ebafc84b26bb4`.

The changes add dedicated paths and leave existing source, Lean claims, workflows, receipts, and open pull requests untouched.

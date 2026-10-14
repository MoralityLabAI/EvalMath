# Working in EvalMath

Conventions for any Claude session in this repository. For a review task, follow `REVIEW.md`.

## Mathematics

- Exact arithmetic: `fractions.Fraction` and finite enumeration. Floats only for display, or where a
  note explicitly allows them under a stated tolerance.
- Every claim carries an evidence level: *algebraic identity*, *finite verified example*, *synthetic
  mechanism result*, or *cited*. Never state a result more strongly than its evidence.
- Never call a regularity seen on a grid a theorem. Stress it at sizes beyond the grid first; two
  "theorems" in this repository's history failed one size beyond the grid that suggested them.
- Check boundary cases explicitly: zero failures, accuracy 1, one-step horizons, ties between optimal
  actions, empty index ranges.
- Cite only what you have checked; mark anything recalled from memory as such.

## Module pattern

Each result lives in a module under `src/spiral_ln/`, with tests in `tests/`, a verifier in `scripts/`
that writes a receipt under `output/` recording every check and the SHA-256 of its sources, and a note
under `paper/`. When a module changes: bump the verifier's schema, regenerate the receipt (never edit a
receipt by hand), `git rm` the superseded receipt, and update the note's header counts and evidence
status. `python scripts/check_receipts.py` must pass.

## Lean

`lean/` is a Lean 4 + Mathlib project. No `sorry`, `admit`, added axioms or `native_decide`. Every
theorem listed in `lean/CLAIMS.md` appears in `lean/axioms_check.lean`, and each row says whether the
Lean statement is the note's full claim, a special case, or a supporting lemma. Build with
`lake exe cache get && lake build`, then `lake env lean axioms_check.lean`.

## Commands

```bash
python -m pip install -e ".[test]"
pytest -q
python scripts/check_receipts.py          # fast receipts
python scripts/check_receipts.py --all    # includes multigen --full-sweep and gold calibration (slow)
```

The package is named `spiral_ln` for provenance (see `README.md`); do not rename it without
regenerating every receipt.

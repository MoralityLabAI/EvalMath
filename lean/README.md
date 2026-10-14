# FeedbackChannel: Lean formalizations

Lean 4 proofs of results in the notes under `paper/`. Each formalized claim is listed in
[`CLAIMS.md`](CLAIMS.md) with the note it comes from, the Lean theorem, and how faithfully the Lean
statement matches the note's statement: the full claim, a special case, or a supporting lemma.

- Toolchain: `leanprover/lean4:v4.34.1` (`lean-toolchain`), Mathlib at
  `d13f23b723b8a846827a245b89c10fc7d3f11612` (`lakefile.toml`, `lake-manifest.json`).
- Build:

  ```bash
  lake exe cache get        # prebuilt Mathlib
  lake build
  lake env lean axioms_check.lean > axioms.out
  python3 ../scripts/check_lean_axioms.py axioms.out axioms_check.lean
  ```

  The last step checks that every theorem listed in `axioms_check.lean` depends only on `propext`,
  `Classical.choice` and `Quot.sound`: no `sorry`, no added axioms, no compiled-code evaluation.
- `wsl_direct.sh` is the author's script for a machine where Mathlib is prebuilt elsewhere; it
  compiles modules directly against that build, bypassing Lake. Use Lake everywhere else.

`FeedbackChannel/Smoke.lean` states the shared-error judge identity of the training-signal note (L4)
and proves it by `ring`.

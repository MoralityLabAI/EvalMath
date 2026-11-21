# Tracing the core_gm exponent and its proof obligations

Source pin: [CoreGm.lean](https://github.com/leanprover-community/riemann-hypothesis/blob/f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3/src/Development/AutomorphicArithmetic/PrimitiveCosets/CoreGm.lean). This note records direct source call sites; the separate Lean probe produces proof-term evidence only when run against the compiled upstream checkout.

The source theorem concludes `Λ.Gm x ≤ x ^ (1/2 + (eD + eL + 7) * eps)`, assuming `EAtH` and `CoreAtH` witnesses. The `CoreAtH` predicate explicitly includes `C.eDiv ≤ eD`, `C.eLoss ≤ eL`, `ErrWindows`, `BNBoundsU`, `SizeData₂`, `ThinScales`, `CostWindows`, and other requirements. These must be discharged by the arithmetic and geometric construction.

The proof applies `Deduction.ch_core` with `C = max (eD + eL) 0 + 3`. Since `ch_core` returns a principal exponent `(C + 3) eps`, nonnegativity of `eD + eL` makes that `(eD + eL + 6) eps`. The `Deduction.ch_top` gap estimate feeds the character-balance theorem, with an error factor `x ^ (CErr C * eps)`. Here `CErr` is bounded using the `eDiv` and `eLoss` controls. `charsA` supplies the character hypotheses, while `gmA_eq` converts the weighted character sum into `Λ.Gm`.

The remaining correction is bounded by `sigA_le` as `4 * Λ.o * x ^ (1/2 + eps)`. For sufficiently large `x`, `x ^ eps` dominates `1 + 4 * Λ.o`. One last multiplicative power of `x ^ eps` absorbs that correction and changes the principal exponent from `+6` to `+7`. Exercises RH-D-005 and RH-D-006 test the algebraic bookkeeping independently of the large number-theory constructions.

The downstream source chain can be seen in [WindowInequalityOfArtinInputs.lean](https://github.com/leanprover-community/riemann-hypothesis/blob/f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3/src/Development/AutomorphicArithmetic/PrimitiveCosets/WindowInequalityOfArtinInputs.lean), which applies `core_gm` to a family of `CoreAtH` witnesses. [LevelGmLeOnFamilyScales.lean](https://github.com/leanprover-community/riemann-hypothesis/blob/f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3/src/Development/AutomorphicArithmetic/PrimitiveCosets/LevelGmLeOnFamilyScales.lean) supplies the `ChainTied` to family-core reduction.

## Reproduction

First validate a tiny original theorem-dependency witness in EvalMath:

```sh
python -m spiral_ln.rh_dependency smoke --lean-cwd lean --output /tmp/rh-dependency-smoke.json
```

To inspect the upstream proof terms, use a complete checkout pinned to the manifest's mirror commit and compiled with that repository's Lean 4.33.1 toolchain. The source checker verifies the six anchor blobs before running:

```sh
python -m spiral_ln.rh_dependency upstream --source-root /path/to/riemann-hypothesis --anchors weighted_bound --max-depth 2 --max-nodes 120 --output /tmp/rh-core-gm-deps.json
```

The direct expression graph remains bounded and can omit mathematical dependencies hidden behind definitions or rewriting. Proof reduction and human examination are separate later tasks.

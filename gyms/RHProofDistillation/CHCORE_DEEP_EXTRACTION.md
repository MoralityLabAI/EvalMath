# ChCore deep compiled-reference extraction

The prior successful compiled proof graph [run 44897842450](https://github.com/MoralityLabAI/EvalMath/actions/runs/44897842450)
identified two especially important references inside `Deduction.ch_core`:

- `Deduction.CharacterBalanceMoves.core`, which averages the pointwise
  kernel error over a finite subgroup and cancels a strictly positive
  subgroup cardinality.
- `Formalism.LFunctionChainParameters.ThickSetMeanBounds.proposition_size_bound`,
  which turns the supplied size-window constraints into the characteristic
  square-root exponent estimate.

This [follow-up workflow](../../.github/workflows/rh-chcore-proofrefs.yml)
imports the pinned source module
`Development.AutomorphicArithmetic.DedekindLFunctions.LandauTheorems.ChCore`.
It verifies the actual source Git blob
`878f5077bc382426c7da988e5a375b85deeaa7de`
and six previously pinned anchor blobs. Only the import closure required by
this source module is downloaded from the SHA-pinned published compiled cache.

The lean4 expression reader retrieves separate type and proof-value constant
references for both theorems. The output labels truncation at the selected
node/depth limits. **Compiled artifacts from a verified public cache are
evidence about the published Lean submission, not an independent new proof
of RH or a clean rebuild.**

The workflow writes `proofref_graph.json` and `summary.json` and uploads
both with a GitHub Actions artifact. Inspect the cache and source identity in
the receipt before using references as benchmarks.

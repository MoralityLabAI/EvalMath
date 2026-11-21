# Selective compiled proof-term inspection

Source mirror pin: `f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3`.

The complete original source graph has only 30 module imports on the Landau
`zeroFree_of_rpow_window` path and 115 on the analytic `core_gm` path.
The exact union is checked before restoration.

The [rh-compiled-slice.yml](../../.github/workflows/rh-compiled-slice.yml)
workflow runs a source-attested, selective cache restore using
the upstream community's pinned `modules.jsonl.gz` manifest.
It fetches only the modules needed for the two target declarations,
verifies each published archive SHA-256, and restores with stock `leantar`.
It imports those modules using Lean 4.33.1 and reports direct constants
in theorem *types* and *proof bodies* separately.

This is stronger evidence than the prior source-text call sites because
the actual published compiled Lean expressions are being inspected.
The archived compiled modules are the published proof output and do not
substitute for an independently rebuilt and checked full formalization.

All source pin checks, cache manifest checks, artifact checks and
truncation flags are written in the JSON receipt.
An omitted or mismatched cache artifact stops the run rather than
silently substituting a new module.

The large Galois and final-theorem paths require a separate runner.

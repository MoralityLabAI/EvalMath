# Locate the source of the size-bound bottleneck

The compiled proof-expression scan identifies
`Formalism.LFunctionChainParameters.ThickSetMeanBounds.proposition_size_bound`
as a theorem of type `GrowthSizeBound`. Its proof directly refers to
`SZ.T1`, `SZ.T2`, `SZ.T3`, `SZ.T4`, and `SZ.rp`.

The [source-symbol workflow](../../.github/workflows/rh-locate-size-bound.yml)
uses a read-only, SHA-pinned sparse checkout of the upstream `Formalism`
directory to locate the actual declaration site of
`proposition_size_bound` and `GrowthSizeBound`. It uploads file paths,
line numbers and Git blob hashes. Original unlicensed theorem bodies
remain in the upstream repository.

The path finder is source-level evidence; the compiled constant references
were independently observed by `rh-chcore-proofrefs.yml`.

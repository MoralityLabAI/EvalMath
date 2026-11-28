# RH SizeWindows: exact scalar feasibility and witness-source lineage

The [workflow](../../.github/workflows/rh-witness-lineage.yml) checks the original
source at pin `f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3`, including the
`SizeWindows` declaration Git blob and all six existing proof anchors.

For epsilon=2^-j and integer j≥1, the checker constructs the following
dyadic scalar inputs:

```text
x = 2^(16/epsilon), n = sqrt(x), nT = n/8,
nT2 = m = x^(1/2-epsilon), k = x*m,
b = 1, C = aE = Err = 0.
```

Each required x^exponent is evaluated with exact fractions, and the
large-x threshold simplifies to 26 ≤ 64. All 16 scalar conditions
are tested at j=1,..,5, along with two nearby negative controls:
reducing the group size by one, and reducing x below the threshold.

**This does not construct `GrowthInequalityDataExists` or `ChainTied`.**
In particular, choosing Err=0 satisfies its scalar *upper* bound
without supplying an estimate on topExcess; b=1 does not claim
to satisfy the separate `SmallCosts` predicate. The arithmetic and
geometric witnesses remain substantive research obligations.

The full-source index records the declarations and usage sites
of `SizeWindows`, `SmallCosts`, `GrowthInequalityDataExists`,
`ChainTied`, `CoreAtH`, and related predicates by exact source Git blob.
These are textual source-navigation results, tagged `proof_term_data=false`.

Upstream source is used temporarily in CI and not redistributed into EvalMath.

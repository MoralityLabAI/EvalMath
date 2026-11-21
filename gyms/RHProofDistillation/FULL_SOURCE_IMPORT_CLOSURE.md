# Full pinned-source import-closure experiment

The [workflow](../../.github/workflows/rh-full-closure.yml) checks out the full original
Lean `src/` tree from the pinned commit, verifies six anchor Git blobs,
counts every `.lean` file and computes import closure sizes for
`core_gm`, `everyCharacter`, the theta-to-Galois row, the
Landau zero-free bound and the `Main` theorem. It also computes shortest
module-import paths to the other targets and pairwise overlaps.

This is **source analysis**. `proof_term_data=false` in receipts.
A large import closure indicates the disk footprint and effort of selective
compiled `.olean` restoration. The number of files alone cannot determine
the compressed artifact size or establish that any source theorem uses its
entire module-import closure.

Source: https://github.com/leanprover-community/riemann-hypothesis
Pin: `f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3`
Run: `python -m spiral_ln.rh_full_closure --source-root /path/to/full/mirror --include-main --output /tmp/full-closures.json`

The resulting JSON is an independently reproducible import-graph receipt. A
compiled proof-expression run needs the upstream Lean v4.33.1 artifacts and
appropriate memory/disk; see [PINNED_UPSTREAM.md](PINNED_UPSTREAM.md).

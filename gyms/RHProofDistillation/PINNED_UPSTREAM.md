# Pinned upstream audit: source and proof-expression stages

The lightweight GitHub Actions job checks out the actual upstream repository at commit
`f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3` in sparse mode.
It verifies all six source anchors, the direct `core_gm` callsites,
and the sixteen named `CoreAtH` hypotheses against pinned source bytes.
It also follows the family-window and Landau bridge through source files.
The JSON receipt marks `proof_term_data=false`, since source parsing is
not inspection of elaborated Lean theorem bodies.

The full proof-expression probe is generated but not executed in this workflow.
Lean's original compilation environment requires Lean 4.33.1 and large caches.
The upstream community cache documentation reports 99.27 GB of extracted
olean and ilean artifacts, with 4.94 GB compressed Lake cache.
Full extraction needs a machine with at least 100 GB free disk;
the upstream build-runner documentation recommends at least 250 GB free.

To inspect proof-body references from an independently obtained full,
clean upstream checkout with the compiled original modules available,
install EvalMath's Python package and run the following from EvalMath:

    python -m spiral_ln.rh_dependency upstream \
      --source-root /path/to/riemann-hypothesis \
      --anchors weighted_bound \
      --max-depth 2 --max-nodes 120 \
      --prefixes UpperTheory. Deduction. Formalism. \
      --output /path/to/core-gm-proof-term-refs.json

Use `lake exe cache get` within the complete pinned upstream checkout
before running the scanner. Cache restoration relies on public artifacts;
transport integrity is separate from proof trust. Independent fresh
compilation or proof-kernel replay is required for stronger verification.

The scanner emits direct constant references in elaborated types and values.
It does not prove that these references form a mathematically minimal
dependency set. Its output has a separate explicit truncation flag.

Upstream source remains in a temporary CI checkout; no unlicensed
source is vendored into EvalMath.

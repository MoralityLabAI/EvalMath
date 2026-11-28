# ACD-03: invariant synthesis under a polynomial lift

Frozen 2026-11-25 before executing the core simulation. Finite synthetic
mathematical experiment, no model/Lean/GPU. This is a new construction
family rather than additional directional-cache tuning.

Worlds: d=5,6,7,8 Boolean coordinates; three affine-action families:
(1) translations confined to a hidden subspace, (2) coordinate swaps
preserving Hamming weight, (3) full-coordinate translations. Conjugate
all actions by random invertible affine coordinate maps, with the
source and transformations generated separately from query order.
Calibration and test have disjoint seeds, with different invertible
map mixing lengths and action choices. Six calibration and twelve
test worlds per dimension/family (216 total). All states are targets
in the correctness census. Streams are 16 targets sampled without
replacement from an independent deterministic stream.

For lift degree k=1,2, use all distinct square-free monomials of degree
1..k, with the affine constant separate. Derive lifted transitions by
finite differences at zero, unit vectors and, at k=2, two-unit vectors.
Verify the lifted identity on every state independently as a census
outside execution cost. Its algebraic proof is the Boolean polynomial
expansion of an affine substitution (no Lean theorem here). Compute
the least invariant affine hull containing the lifted source: seed
with transition displacements and close the linear basis under all
linear parts. Use an original-row echelon representation. Audit source,
transition displacements and all basis-image memberships. The audited
invariant set is a valid negative proof if the lifted target is
outside the affine hull. It need not characterize the exact orbit.
For membership in the invariant hull, use exact lazy BFS as fallback;
do not treat membership as proof of reachability. Direct negative
certificates are forward-closed sets, positives are original action
paths. All are checked against original transitions.

ACD-03A: exhibit and enumerate degree-2 separations beyond degree 1,
and negatives missed by both. Report exact counts by dimension/family.
ACD-03B: compare fresh BFS, lazy BFS, linear hull + lazy fallback,
quadratic hull + lazy fallback, and staged linear then quadratic
on the first unresolved query + lazy fallback. Every build and
audit is paid once per stream; every certificate checked. Staged
retains previously paid costs. All arms get the same target order.
Count selected vector reads/writes, bit probes, bitset/parity/algebra,
and checks at unit weights. BigInt bitset operations count as one
abstract op; widths differ; no wall-clock or memory speed claim.
Degree 1 map may be taken directly from raw public affine actions;
degree 2 map construction is charged by finite differences.
An independent reference orbit census and lift identity checks are
offline and excluded. Closure at stream budget 16 times 128,512,
2048 units is retrospective prefix censoring. Report per-world
work, certificate category and verification counts. Compare a
calibration-selected policy per dimension (family labels withheld
from selector) with lazy BFS and specialized symbolic arms. Policy
selection overhead excluded as an optimistic bound. Full-library
hindsight and dimension-constrained hindsight are secondary exact
diagnostics, not attainable adaptive-controller claims.

ACD-03C: primary neural-training preflight: calibration per-world
hindsight headroom against the best dimension-conditioned symbolic
policy at least 20%; held-out oracle closure gap at primary 512-unit
budget at least 5 percentage points against that policy. Both are
necessary; failure stops neural training. Test all arms regardless
of screen, report failures, no tuning on test. No claim about
general invariant discovery from these finite generators.

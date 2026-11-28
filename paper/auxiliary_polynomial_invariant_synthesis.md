# ACD-03: polynomial-lift invariant synthesis

2026-11-25 | Finite synthetic mathematics; no trained model, Lean proof or GPU run.

Protocol frozen at 50d6aff before execution. This is a new construction
family following ACD-02, rather than a retuning of its graph workloads.

## Mathematical construction

Let F_j(x)=A_j x+b_j be affine maps over GF(2), with initial state s.
Write phi_1(x)=x and phi_2(x) for the vector of coordinates and all
distinct pair products x_i x_j (i<j). Substitution of an affine map
into square-free Boolean monomials of degree at most two yields another
polynomial of degree at most two: x_i^2=x_i on Boolean states. Thus
phi_k(F_j(x))=M_j phi_k(x)+c_j for k=1,2.

The induced degree-two affine maps are recovered from finite differences
at 0, e_i and e_i+e_j. The linear coefficient in a lifted coordinate
is its value at e_i plus its value at 0. The pair coefficient is
the sum of its values at e_i+e_j, e_i, e_j and 0. Expansion and
cancellation prove these identities over GF(2).

Set z=phi_k(s). Generate a linear space V from the displacements
M_j z+c_j-z, and repeatedly adjoin M_j v for each accepted echelon
basis row v and each action j. This terminates after at most dim V
rank increases. The affine set z+V contains z and is invariant under
all lifted actions: M_j(z+v)+c_j-z is the sum of a displacement
and M_j v, both in V. By induction every reachable lifted state
belongs to z+V. A target whose lift lies outside it is unreachable.

Moreover z+V equals the affine hull of the reachable lifted states.
For one inclusion use invariance. For the other, the affine hull
of a set closed under affine maps is itself closed under them.
It contains z, so minimality of the constructed invariant affine
space gives the reverse inclusion. Projection of the quadratic hull
onto its original-coordinate part is the linear hull, implying
every linear exclusion is also a quadratic exclusion. Hull
membership alone cannot establish reachability.

## Explicit strict separation and incompleteness

Consider all coordinate swaps on eight Boolean coordinates, starting
from a vector of Hamming weight two. The orbit consists of all
weight-two vectors. The parity of the weight is a linear invariant.
A weight-four target with even parity is in the affine hull of
the orbit: the XOR of the three weight-two vectors on edges
(1,2), (2,3), (2,4) has support {1,2,3,4}, and three is odd.
However the quadratic invariant sum_{i<j} x_i x_j equals
binomial(weight,2) modulo two, which is one at weight two
and zero at weight four. This excludes the target in the lift.

For a weight-six target supported on a set T of six coordinates,
take the XOR of phi_2(e_i+e_j) over all 15 pairs inside T.
Each coordinate occurs five times, and each pair occurs once;
therefore the sum equals phi_2(1_T). Because 15 is odd, this is
an affine combination of reachable lifts. Weight six is unreachable
but even the quadratic affine hull cannot exclude it. These
are exact algebraic witnesses, independent of the sampled worlds.
Invertible affine coordinate conjugations preserve the degree
bounds, since substituting an invertible affine transformation
and its inverse both preserve Boolean polynomial degree <=k.

## Census and cost protocol

Dimensions 5,6,7,8. Hidden-subspace translations, coordinate swap
orbits, full-coordinate translations. Six calibration and twelve
test worlds per dimension and family; the public affine maps
are derived by random invertible affine conjugation, with
different mixing lengths and swap generators across splits.
Target streams are 16 distinct values selected by separate seeded
shuffles. The independent orbit oracle uses hidden-coordinate
actions and fixed-point set expansion. Each original affine
transition and each lifted transition are checked on every state.

216 worlds, 25,920 source-target pairs, 14,320 unreachable targets.
The degree-one hull excludes 11,484 negatives; degree two excludes
14,167, including 2,683 additional negatives. Both miss 153.
No false exclusion occurs. 302,080 lifted transition identities
and 648 malformed invariant/path/cut controls are checked; all
controls are rejected. Each tested stream answer is also checked.
The basis audit checks echelon pivots, every action displacement,
and every action image of each basis vector. For exclusion, verify
target nonmembership in the already audited affine set. It does
not require every basis vector to have a separate reachability
provenance proof: forward invariance suffices for sound exclusion.
The independent full-state lift audit is offline, as registered.

Work counts selected reads, writes, bitset/bit-probe operations
and checks at unit weight. BigInt operations are counted as one
abstract operation regardless of width. All invariant arms pay
construction and basis audit and fall back to original-graph
BFS with path or closed-set verification on unresolved targets.
The staged policy constructs the quadratic hull upon its first
linear-unresolved query. Offline oracle/calibration and routine
allocation/control overhead are excluded. No memory or measured
wall-clock inference claim is made.

## Held-out comparison

144 fresh worlds, 2,304 requested proofs. Retrospective verified
prefix closure at per-world budget 16 times the listed units.

| Policy | Work | 128 | 512 (primary) | 2048 |
|---|---:|---:|---:|---:|
| Fresh BFS | 8432275 | 312 | 943 | 1675 |
| Lazy BFS | 3225495 | 502 | 1358 | 2027 |
| Linear | 1567854 | 696 | 1601 | 2181 |
| Quadratic | 4366903 | 116 | 681 | 1694 |
| Staged | 4489629 | 383 | 757 | 1682 |

Linear hull synthesis proves 1,015 of the 1,268 stream negatives;
quadratic synthesis proves 1,259, an additional 244. Quadratic
construction is nevertheless expensive at these dimensions,
stream lengths and operation weights. On hidden-subspace
translation test worlds the linear arm proves all 633 stream
negatives by invariant, and costs 116,580 versus lazy BFS's
1,027,593. In full-coordinate translation controls all 768
test queries are positive; lazy BFS costs 632,683 versus
758,570 for linear. Weight-family linear and quadratic costs
are 692,704 and 1,142,550 respectively; quadratic proves
626 of 635 stream negatives.

## Training preflight: failed

Calibration chooses linear for every public dimension. Family
tags were withheld from the selector. Headroom versus this
dispatch on calibration worlds is 15.56%, 13.13%, 8.07%, 5.32%
for dimensions five through eight. No stratum meets the
registered 20% threshold. Test hindsight cost over the five
complete policies is 1,431,609, an 8.69% gap versus dispatch.
The primary closure oracle is 1,660 versus 1,601, a 2.56
percentage-point difference before selector costs. Even the
all-world diagnostic is below the five-point threshold.
The admitted test set is empty, so the registered training
gate fails. A selector of one policy per dimension has zero
hindsight cost gap on test. These are finite-library bounds,
not bounds on all possible invariant synthesis algorithms.

## Next direction

The useful outcome is constructive invariant discovery beyond
the original representation, with an exact strict-separation
witness and a cost failure. ACD-04 could synthesize individual
low-degree separating polynomials rather than constructing the
entire lifted affine hull. A strong symbolic comparator should
solve the global invariant equations p(F_j(x))=p(x) using
Gaussian elimination on polynomial coefficients; it should also
include source-dependent invariant subspaces. Charge the
polynomial coefficient matrix, discovery, certificate
verification and any fallback. Global invariants alone can
be weaker than source-dependent invariant hulls. Freeze new
generators before evaluating. No neural training has been
approved under the existing gate.

## Reproduce

    node scripts/verify_acd_03.mjs --check

The core ran in V8 and produced the exact JSON receipt at
output/evaluation_acd/acd_03.json. Remote function fingerprint
ea7915de matches the saved receipt (FNV-1a reproducibility
checksum, not cryptographic source integrity).
Source blob 06f493c9c03cb67bcd1e59b980db9f15baf3bfab;
receipt blob 945d53e24b3e1267c2a59b9a4470581f247960db.
Dedicated Node CI includes this verifier. Previous ACD receipts
passed their dedicated CI at run 45515752451; independent
reproduction of ACD-03 remains pending at this checkpoint.

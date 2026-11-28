# ACD-04: direct global polynomial invariants and target-guided synthesis

2026-11-25 | Exact finite symbolic pilot. Protocol frozen at a0fe1be
before execution. No trained model, GPU experiment, or Lean proof.

## Mathematical results

Let F_j be affine Boolean actions, phi_k the vector of square-free
monomials of degrees one through k, k in {1,2}, and s the source.
The constant monomial is omitted since it cancels in differences.
Define

    G_k = span{phi_k(F_j(x)) + phi_k(x) : all j,x}
    V_k(s) = span{phi_k(x) + phi_k(s) : x reachable from s}

The global polynomial y dot phi_k(x) is invariant exactly when
y annihilates G_k. Such a polynomial separates target t from s
exactly when u=phi_k(t)+phi_k(s) is outside G_k. This follows
from elementary linear separation over GF(2). A source-specific
affine hull excludes t exactly when u is outside V_k(s).
Telescoping along a path from s shows V_k(s) <= G_k. Hence
every global exclusion is a source-specific exclusion; the
converse can fail. Inclusion is valid for noninvertible actions
as well as permutations.

Each component of D_j(x)=phi_k(F_j(x))+phi_k(x) is a square-free
Boolean polynomial of degree <=k. Its coefficients are recovered
from values at 0, unit vectors, and (when k=2) two-unit vectors
by finite differences. Conversely, every value is a linear
combination of these anchor values, so the anchors generate G_k.
The audited eager solver computes the anchor row span and
checks a separating coefficient vector against its echelon basis.

Target-driven CEGIS maintains a subspace B <= G_2 of accumulated
counterexample rows. If u belongs to B, no global quadratic
separator exists. Otherwise linear separation supplies y with
y dot u=1 and y orthogonal to B. Scan the anchor equations.
An offending row r with y dot r=1 is outside B, so adjoining
it strictly increases rank. A candidate passing all anchors is
a globally invariant polynomial. Thus each failed proposal
increases rank, at most dim G_2 times across the entire stream.
A successful candidate may be cached and reused by checking
that it separates a new target. This proves the equivalence of
eager and target-directed global exclusion decisions, independent
of the ordering of counterexamples. Both may fall back to exact
reachability on targets not excluded.

### Two strict separation witnesses

Reset actions F_i(x) set coordinate i to zero and leave the others
unchanged. Every state reaches zero, so every globally invariant
function is constant on the entire state space. If s has a zero
coordinate, that coordinate remains zero on its orbit. The source
specific linear hull excludes any target with a one in that
coordinate. In this example the global invariant approach fails
even at arbitrary polynomial degree.

For invertible actions, take the full permutation group on d>=5
coordinates and a source of weight one. A permutation-invariant
Boolean polynomial of degree <=2 has the form
c + a sum_i x_i + b sum_{i<j} x_i*x_j: uniqueness of square-free
Boolean polynomial coefficients makes coefficients constant on
each monomial orbit. Weight one and weight five agree on both
nonconstant terms (1 modulo 2, and 0 modulo 2). No such global
polynomial separates them. Yet every source-reachable lift has
all pair-product coordinates zero. The weight-five target lies
outside its source-specific quadratic affine hull.

## Experiment

216 worlds across dimensions 5,6,7,8, hidden-subspace translations,
coordinate swap orbits, and coordinate resets; six calibration
and twelve test worlds per dimension and family. Separate seeds,
coordinate mixing lengths, and swap generators distinguish splits.
The public actions are conjugated by random invertible affine
maps. Independent hidden-coordinate orbit closure supplies the
reference answer. Each stream has 16 distinct targets, sampled
by a separate deterministic shuffle. The dimension-conditioned
selector cannot see the hidden family tag.

The five tested arms are lazy BFS, linear and quadratic source
hulls, eager global quadratic constraints, and quadratic CEGIS.
The global linear result is included in the census, not in the
stream policy library. The source hull construction is the same
linear closure principle as ACD-03. Its generated lifted maps
use the algebraic finite-difference identity; this run checks
the raw conjugated maps and the exclusions independently, but
does not repeat the full induced-map identity census of ACD-03.
Every stream invariant exclusion is checked using the audited
construction and its target; unresolved targets use independently
checked original-action path or closed-set certificates.
The CEGIS anchor rows and previously validated polynomials are
cached; verifying a new proposal scans anchors until the first
violation or complete validation.

Work counts selected reads, writes, checks and algebra/bitset
operations at unit weights. BigInt operations have unit cost
regardless of width. Construction, audits, candidate failures,
memoized anchors and fallback search are charged according to
this declared metric. Offline calibration, reference oracle and
routine control/allocation are excluded. Actual wall time and
memory consumption are not measured. Budget closure is the
retrospective number of fully certified prefix answers, not
live interruption.

## ACD-04A: exact census

| Quantity | Count |
|---|---:|
| Worlds | 216 |
| Source-target pairs | 25920 |
| Unreachable targets | 21738 |
| Global linear exclusions | 11586 |
| Global quadratic exclusions | 13830 |
| Source linear exclusions | 18724 |
| Source quadratic exclusions | 21467 |
| Additional source quadratic vs global quadratic | 7637 |
| Raw transition checks | 148768 |
| Global row-span completeness checks (both degrees) | 297536 |
| Malformed controls rejected | 1080 |

Every exclusion agrees with the independent oracle; CEGIS and
eager global quadratic agree on every census target. Global
quadratic excludes 2,244 more negatives than global linear.
Source quadratic excludes 2,743 more than source linear.
The tests reject zero, identical-target and noninvariant
separators plus invalid paths and cuts.

Held-out reset worlds have 4,652 unreachable targets; both
source hulls exclude all, neither global degree excludes any.
In held-out weight worlds the source quadratic hull excludes
4,787, global quadratic 4,396, a 391-target difference.
The algebraic witnesses explain why this effect extends
beyond noninvertible systems.

## ACD-04B: held-out work

144 worlds, 2,304 requested proofs. Per-world budgets are
16 times the units shown.

| Policy | Work | 128 | 512 (primary) | 2048 |
|---|---:|---:|---:|---:|
| Lazy BFS | 3930872 | 473 | 1285 | 2018 |
| Source linear | 911721 | 1128 | 1927 | 2266 |
| Source quadratic | 2866434 | 133 | 861 | 1970 |
| Global quadratic | 5192685 | 26 | 519 | 1580 |
| CEGIS quadratic | 4570741 | 86 | 632 | 1705 |

CEGIS saves 621,944 units (~11.98%) against eager global
quadratic and matches its 1,230 invariant exclusions. Across
held-out streams it makes 3,196 proposals, obtains 2,980
independent violating constraints, validates 216 polynomials,
reuses a validated polynomial on 1,014 queries, computes
19,232 anchor rows and performs 201,277 anchor checks.
The dominant work remains repeated invariant verification
and the fallback on targets that global invariants cannot
exclude. The source linear baseline excludes 1,615 of the
1,861 stream negatives, source quadratic excludes 1,846.

## ACD-04C: training gate fails

Calibration chooses source linear at every dimension and on
every calibration world. Thus per-world hindsight headroom
is zero in each dimension. The test oracle over all five
policies costs 908,359 versus 911,721 for dimension dispatch
(0.3688% headroom). The best hindsight primary closure is
1,932 versus 1,927 (five proofs, 0.217 percentage points).
The admitted stratum set is empty and the registered
training gate fails. All-world diagnostics also fall far
below the registered thresholds. No neural training is run.

## ACD-05: source-dependent dual synthesis

The next constructive question is to avoid the global-invariance
restriction and avoid building the entire source hull. For
lifted actions z -> M_j z+c_j and z_s=phi_k(s), let
d_j=M_j z_s+c_j+z_s. The source direction space is the least
M_j-invariant linear space containing all d_j.

For proposed coefficient y, close its dual orbit Q_y under
M_j^T. Then y annihilates the source direction space iff every
q in Q_y annihilates every d_j. To see this, the source
direction space is spanned by products of M_j applied to d_j;
the adjoint identity transfers every such product to a dual
product on y. If the test fails, a dual word that violates a
displacement yields a primal counterexample row, which can be
adjoined to a growing source constraint span. Tracking word
provenance permits direct verification. If y dot u=1 and the
dual audit passes, y separates the target from the orbit.

This suggests a source-specific, target-driven synthesis
algorithm with exact rank-increasing counterexamples, distinct
from global CEGIS. Compare with full primal source hull,
lazy BFS and a bidirectional primal/dual solver; charge
dual closure, provenance, certificate checks and fallback.
Before any training, preregister fresh larger-dimensional and
noninvertible workloads, plus a sparse structured solver
control. ACD-05 is prospective, not an executed result.

## Reproduction

    node scripts/verify_acd_04.mjs --check

The V8 core executed successfully; 216 records are committed in
output/evaluation_acd/acd_04.json. The remote function checksum
44336566 matches (FNV-1a, not a cryptographic integrity hash).
Source blob 169751a664e8785729b93773a4f98cdee34d3180;
receipt blob ef8785d1aef2d96df95e88d494b06827725712ab.
The dedicated Node CI now includes ACD-04. Both prior ACD-03
receipt CI (45516243040) and full EvalMath CI (45516243161)
passed. Independent CI for this extension remains to be checked.

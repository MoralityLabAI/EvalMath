# CTS-01: Certificate–trajectory separation
Status: algebraic identity + exact finite example (18 cases, one structural family); no neural evidence.

## Upstream claims and scope

OpenAI math, family 380, November 24, 2026, pinned to commit 3344da59991ed94f9ba711217b29c1d760badfa6:

- [Strongly polynomial linear programming](https://github.com/openai/math/tree/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/Strongly-polynomial-linear-programming-November-24-2026). The manuscript claims a strongly polynomial algorithm over real inputs; the documented Lean comparator scope is rational RAM feasibility and optimization.
- [Superpolynomial graph diameter of simple polytopes](https://github.com/openai/math/tree/3344da59991ed94f9ba711217b29c1d760badfa6/preprints/Superpolynomial-graph-diameter-of-simple-polytopes-November-24-2026). The claims concern actual shortest undirected paths, including moves within low-dimensional common faces and a prescribed objective gap.
- [Formalization scope](https://github.com/openai/math/blob/3344da59991ed94f9ba711217b29c1d760badfa6/lean/docs/380.md). The comparator statements are challenges containing sorry; the corresponding solution entry points in OAI/Optimization/LinearProgramming and OAI/Geometry/Hirsch are distinct proof files. Source inspection confirms the stated scope only. No full proof, axiom audit, kernel build or algorithm reproduction was performed.

Conditional consequence: if both claims hold, no polynomial bound on edge/allowed-face steps can match the global LP feasibility/optimization guarantee uniformly over the indicated family. This does not imply that a learned reasoner can recover the certificate, that every local reasoning representation is hard, or that the LP algorithm's practical cost is small. The finite construction below stands independently.

## Exact toy construction

For integer m >= 1, use coordinates (x,y) and the 4m inequalities

    (2i+1)x +/- y <= i(i+1)+m^2,  i=-m,...,m-1.

Maximize x from the vertex (-m,0). The upper and lower boundaries are the piecewise-linear interpolants through (i,+/-(m^2-i^2)) for integer i in [-m,m]. Each consecutive pair on a boundary lies on one of the given supporting lines; strict changes in slopes make each interior point a vertex, with two endpoints shared. Thus the polygon has 4m facets and vertices, and the graph is a cycle. The endpoints have undirected edge distance 2m (each edge changes x by one in absolute value, and either chain achieves 2m). The objective gap is 2m. The entire polygon is a 2-face, so a face-dimension allowance of 2 reduces the distance to one move.

The optimal vertex is (m,0). The two rows for i=m-1 have normals (2m-1,+/-1). Giving each weight 1/(2(2m-1)) produces c=(1,0) and a dual bound equal to m. This proves optimality by weak duality. Invertible rational affine coordinate changes preserve the face graph and dual support; row permutations preserve both properties.

Evidence: the identities above are elementary and independent of family 380. The toy distance is linear in facet count; this does not reproduce a superpolynomial diameter or its low-dimensional face robustness.

## Executed pilot

Six sizes m=1,2,4,8,16,32; seeds 11,23,47. The exact rational program constructs feasible vertex witnesses, checks facet incidences, uses BFS for graph distance, enumerates two-row dual supports from the inequality system and objective alone, and validates the recovered certificate. Each run rejects the start vertex paired with the optimal dual and rejects negated dual multipliers. All 18 certificates pass. At K=8, nine starts are reachable by any edge policy, including an oracle policy. A two-dimensional face interface can reach all 18 in a single move; this is the intended negative control.

The solver charges all binomial(4m,2) pair trials, plus feasibility/certificate checks. Certificate sparsity is not discovery cost; no equal-compute advantage is asserted. The BFS receives the full vertex set as a structural ceiling, unavailable to an ordinary model. The finite rows are three affine views per size of ONE family; they are not independent observations for generalization.

Run:

    PYTHONPATH=src python scripts/verify_certificate_trajectory.py
    PYTHONPATH=src pytest -q tests/test_certificate_trajectory.py

## Prospective experiment CTS-02 (not executed)

Use independent generator families, including nonseparable polygons, product polytopes and independently validated finite instances of the Hirsch construction if available. For each task provide exact constraints, objective and starting feasible vertex. Keep answer/optimal support, generator identity, and complete graph private. Freeze splits by structural family, not seed or presentation.

Compare local edge policy, bounded face moves, a certificate proposal interface, and hybrid routing; charge inference FLOPs, tokens, arithmetic operations, candidate pair/face tests, rejected actions, verification and tool calls separately. Report K-step reachability ceiling, success, optimality gap, rejection rate, support, and compute-normalized cost. Use row permutations as invariance shams and budget-matched random macro-actions as behavioral shams. A verifier accepts only exact feasibility and primal-dual equality; no reward for plausible proof text. Include objective rotations, singular/degenerate cases and easy local instances; do not let the model learn only the symmetric two-row pattern.

Model and checkpoint are not chosen. Proposed primary contrast: paired root-level verified success improvement of hybrid over a compute-matched local policy on tasks with oracle edge distance above the registered K. Proposed minimum effect 0.10 absolute verified-success fraction. Physical dose and measured sham envelope must come from an independent development pilot; no sealed confirmation exists yet. Apply skills/evalmath-mechinterp-power/scripts/preflight.py --strict to actual independent development summaries before training/scoring and use the repository's finite-sample inference module. Current status PILOT_ONLY: 18 deterministic cases, one structural family, no independent neural development effects or calibrated model sham floor. All further model claims blocked pending preflight.

For Storyworld evaluation, the same question is whether the allowed reaction/update operators impose a trajectory bottleneck. Test a certificate or global-invariant interface with matched budgets and independent world roots before inferring a causal latent shortcut.

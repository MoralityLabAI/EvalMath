# UG-FID-02: spectral norm and curvature decoding fidelity

**Date:** 2026-11-04. **Evidence:** general elementary mathematical identities
(written proofs), exact finite Python controls, and a *conditional*
complexity deduction from the reported OpenAI 2026 Unique Games theorem.

This builds on [UGC-PT-01](unique_games_topology_eth.md), which already
audits 1,001 finite translation games and distinguishes graph cohomology
from approximate cosystolic optimization.

## Finite Stone-space operator

For a finite `F_2^s` translation game on nonempty edge occurrences E,
define the finite Stone space X of vertex labelings and the diagonal edge
projectors `P_e(a)=1[a_v=a_u+c_e]`. Their mean `A_G = |E|^-1 Σ_e P_e`
is positive in C(X). Its diagonal eigenvalues are exactly each labeling's
satisfied-edge fraction, giving

    ||A_G|| = OPT(G)
    min spec(I - A_G) = 1 - OPT(G).

For zero edges take `A_G=I` and `OPT=1`. These equations are exact.
An uncompressed diagonal representation has `|F_2^s|^|V|` entries.

## Fundamental-cell curvature decoder

Attach one 2-cell to each fundamental cycle of an ordered spanning forest.
The resulting 2-complex has H^1=0, and the cycle evaluation map d1 has
kernel im d0. For `F=d1(c)`:

    min_a |support(c-da)| = min_(xi:d1 xi=F) |support(xi)|.

The enumerator `minimum_curvature_repair` searches correction vectors
ordered by **number of nonzero edge symbols**. Independently,
`minimum_bad_edges` removes minimum edge subsets until all holonomies
vanish. The pytest suite cross-checks both against direct diagonal
operator maximization for every one of the 256 four-cycle F2^2 shifts.
It also exercises loops, parallel edges, and empty graphs.

## Conditional no-efficient-spectral-compression claim

Assume the upstream UGC gap reduction from 3SAT has the stated polynomial
time and explicit encoding guarantee. Fix `ε,δ∈(0,1/2)`. If a uniform
polynomial-time algorithm builds polynomial-dimensional *rational
Hermitian* `M_G` with polynomial-bit entries satisfying
`| ||M_G|| - OPT(G) | ≤ τ`, for `2τ<1-ε-δ`, then polynomial-time
rational spectral norm approximation distinguishes the YES and NO
promises. Thus the compression would imply P=NP.

The required matrix dimension, construction time, bit lengths and
approximation accuracy are all part of the premise. An efficient
description of an exponentially large diagonal does not satisfy it.

## Reproduce

    PYTHONPATH=src python -m pytest -q tests/test_unique_games_spectral.py

The test suite is deliberately independent of upstream Lean replay;
proof integrity still belongs to the draft theorem-fidelity PR #13.
This study does not certify the UGC reduction or generalize the
spectral hardness claim to unrestricted descriptions.

Sources:
- https://github.com/openai/math/blob/main/lean/OAI/Computability/UniqueGames/Theorem.lean
- https://github.com/MoralityLabAI/EvalMath/pull/13

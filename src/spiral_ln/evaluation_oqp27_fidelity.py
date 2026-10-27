"""Exact finite OQP27 Bell-witness and objective-substitution audit.

All computations use rational arithmetic on the 256 local deterministic strategies
of the (2 settings, 2 settings, 4 outcomes) Bell scenario. This reproduces a
finite slice of PSI's OQP27 mathematical formalization, not its projective
quantum-optimality theorem or its high-dimensional KL/noise comparisons.

Sources: PSI commit da37af2ae174687403fbd97e9673c819edee71fd,
CGLMPBounds/Defs/{CGLMP,BGP}.lean and CGLMPBounds/BGP/Facet.lean.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product
from typing import Mapping

DIM = 4
UPSTREAM_REPO = "physical-superintelligence/oqp-batch-2026"
UPSTREAM_COMMIT = "da37af2ae174687403fbd97e9673c819edee71fd"
UPSTREAM_BLOBS = {
    "oqp27-cglmp-inequalities/lean/CGLMPBounds/Defs/CGLMP.lean":
        "3889781d058966e336305d8a646cfbb8aaa98bdf",
    "oqp27-cglmp-inequalities/lean/CGLMPBounds/Defs/BGP.lean":
        "8a1bc93bd4b237112f90a2d170ebd09ac3885644",
    "oqp27-cglmp-inequalities/lean/CGLMPBounds/BGP/Facet.lean":
        "096475ee8611beb3d7bdcd24fd540e23a6c062a4",
    "oqp27-cglmp-inequalities/lean/docs/FIDELITY.md":
        "10f3e7c3ce2672b25555ee851f0f9c18cb9a52b3",
}

# Coefficients transcribed from CGLMPBounds/Defs/BGP.lean at the pinned commit.
BGP_L = (-1, -1, 0, -1, 0, 0)
BGP_H = (
    (0, 1, 0, 1, 0, 1),
    (1, 0, 0, 1, 1, 0),
    (0, 0, -1, 1, 0, 0),
    (1, 1, 1, 1, 0, 0),
    (0, 1, 0, 0, 0, -1),
    (1, 0, 0, 0, -1, 0),
)

Strategy = tuple[int, int, int, int]  # (a0, a1, b0, b1)
Cell = tuple[int, int, int, int]  # (x, y, a, b)
Table = Mapping[Cell, Q]


def strategies() -> tuple[Strategy, ...]:
    return tuple(product(range(DIM), repeat=4))


def residual(x: int, y: int, a: int, b: int, *, missing_shift: bool = False) -> int:
    """The residual of PSI's CGLMP definition; missing_shift is a negative control."""
    if x == y:
        return (a - b) % DIM
    if x == 1:
        return (b - a) % DIM
    return (b - a - (0 if missing_shift else 1)) % DIM


def cglmp_strategy(s: Strategy, *, missing_shift: bool = False) -> Q:
    total = sum(residual(x, y, s[x], s[2 + y], missing_shift=missing_shift)
                for x in range(2) for y in range(2))
    return Q(4) - Q(2, DIM - 1) * total


def bgp_strategy(s: Strategy, *, omit_marginals: bool = False,
                 altered_h: bool = False) -> int:
    """Integer evaluation on a local deterministic vertex, not a physical quantum realization."""
    a, b = s[:2], s[2:]
    marginal = 0 if omit_marginals else (
        sum(BGP_L[3*x + a[x]] for x in range(2) if a[x] < 3) +
        sum(BGP_L[3*y + b[y]] for y in range(2) if b[y] < 3)
    )
    joint = sum((0 if altered_h and (3*x + a[x], 3*y + b[y]) == (2, 2)
                 else BGP_H[3*x + a[x]][3*y + b[y]])
                for x in range(2) for y in range(2) if a[x] < 3 and b[y] < 3)
    return marginal + joint


def table_of(s: Strategy) -> dict[Cell, Q]:
    return {(x, y, a, b): Q(int(s[x] == a and s[2 + y] == b))
            for x in range(2) for y in range(2)
            for a in range(DIM) for b in range(DIM)}


def linear_combo(terms: Mapping[Strategy, Q]) -> dict[Cell, Q]:
    """Directly mix full probability tables, independent of the vertex score shortcuts."""
    out = {(x, y, a, b): Q(0) for x in range(2) for y in range(2)
           for a in range(DIM) for b in range(DIM)}
    for s, mass in terms.items():
        if mass == 0:
            continue
        for x, y in product(range(2), repeat=2):
            out[x, y, s[x], s[2 + y]] += mass
    return out


def cglmp_table(q: Table) -> Q:
    score = sum((Q(residual(x, y, a, b)) * q[x, y, a, b]
                 for x, y, a, b in product(range(2), range(2), range(DIM), range(DIM))), Q(0))
    return Q(4) - Q(2, DIM - 1) * score


def bgp_table(q: Table) -> Q:
    left = sum((Q(BGP_L[3*x + a])*sum((q[x, 0, a, b] for b in range(DIM)), Q(0))
                for x in range(2) for a in range(3)), Q(0))
    right = sum((Q(BGP_L[3*y + b])*sum((q[0, y, a, b] for a in range(DIM)), Q(0))
                 for y in range(2) for b in range(3)), Q(0))
    joint = sum((Q(BGP_H[3*x + a][3*y + b])*q[x, y, a, b]
                 for x, y, a, b in product(range(2), range(2), range(3), range(3))), Q(0))
    return left + right + joint


def valid_no_signalling(q: Table) -> bool:
    if set(q) != set(product(range(2), range(2), range(DIM), range(DIM))):
        return False
    if any(v < 0 for v in q.values()):
        return False
    if any(sum((q[x, y, a, b] for a, b in product(range(DIM), repeat=2)), Q(0)) != 1
           for x, y in product(range(2), repeat=2)):
        return False
    if any(sum((q[x, 0, a, b] for b in range(DIM)), Q(0)) !=
           sum((q[x, 1, a, b] for b in range(DIM)), Q(0))
           for x in range(2) for a in range(DIM)):
        return False
    if any(sum((q[0, y, a, b] for a in range(DIM)), Q(0)) !=
           sum((q[1, y, a, b] for a in range(DIM)), Q(0))
           for y in range(2) for b in range(DIM)):
        return False
    return True


def bgp_saturator_average() -> dict[Cell, Q]:
    sat = [s for s in strategies() if bgp_strategy(s) == 0]
    if not sat:
        raise ValueError("BGP saturator set is empty")
    return linear_combo({s: Q(1, len(sat)) for s in sat})


def bgp_nonlocal_witness() -> dict[Cell, Q]:
    """PSI's p+ : a rational no-signalling box that violates the BGP inequality."""
    out = bgp_saturator_average()
    for a, b, sign in ((0, 1, 1), (3, 3, 1), (0, 3, -1), (3, 1, -1)):
        out[0, 0, a, b] += Q(sign, 144)
    return out


@dataclass(frozen=True)
class TransferAudit:
    """Finite-domain optimizer transfer, with an explicit universal tie rule."""

    source_max: Q
    target_max: Q
    source_winners: int
    target_winners: int
    shared_winners: int
    universal_transfer: bool
    existential_transfer: bool
    worst_target_regret: Q
    counterexample: Strategy | None


def audit_transfer(source: Mapping[Strategy, Q], target: Mapping[Strategy, Q]) -> TransferAudit:
    if not source or set(source) != set(target):
        raise ValueError("objectives need the same nonempty finite strategy universe")
    best_src, best_tgt = max(source.values()), max(target.values())
    src_winners = {s for s, score in source.items() if score == best_src}
    tgt_winners = {s for s, score in target.items() if score == best_tgt}
    outside = sorted(src_winners - tgt_winners)
    return TransferAudit(
        source_max=best_src, target_max=best_tgt,
        source_winners=len(src_winners), target_winners=len(tgt_winners),
        shared_winners=len(src_winners & tgt_winners),
        universal_transfer=not outside,
        existential_transfer=bool(src_winners & tgt_winners),
        worst_target_regret=max((best_tgt - target[s] for s in src_winners), default=Q(0)),
        counterexample=outside[0] if outside else None,
    )


def verify() -> dict:
    ss = strategies()
    cg = {s: cglmp_strategy(s) for s in ss}
    bg = {s: Q(bgp_strategy(s)) for s in ss}
    cc, bc = Counter(cg.values()), Counter(bg.values())
    pbar, pplus = bgp_saturator_average(), bgp_nonlocal_witness()
    forward, reverse = audit_transfer(cg, bg), audit_transfer(bg, cg)
    checks = {
        "256_local_vertices": len(ss) == 256,
        "cglmp_histogram": cc == {Q(2):80, Q(-2,3):160, Q(-10,3):16},
        "bgp_histogram": bc == {Q(0):72, Q(-1):144, Q(-2):40},
        "vertex_scores_match_full_tables": all(
            cglmp_table(table_of(s)) == cg[s] and bgp_table(table_of(s)) == bg[s] for s in ss),
        "local_cglmp_bound": all(v <= 2 for v in cg.values()),
        "local_bgp_bound": all(v <= 0 for v in bg.values()),
        "pbar_positive_in_all_cells": min(pbar.values()) == Q(1,72),
        "pbar_no_signalling": valid_no_signalling(pbar),
        "pbar_saturates_bgp": bgp_table(pbar) == 0,
        "pplus_no_signalling": valid_no_signalling(pplus),
        "pplus_bgp_violation": bgp_table(pplus) == Q(1,144),
        "pplus_fixed_cglmp_below_bound": cglmp_table(pplus) == Q(1,9),
        "shared_winners": forward.shared_winners == reverse.shared_winners == 24,
        "cglmp_to_bgp_universal_transfer_fails": not forward.universal_transfer,
        "bgp_to_cglmp_universal_transfer_fails": not reverse.universal_transfer,
        "cglmp_to_bgp_worst_regret": forward.worst_target_regret == 2,
        "bgp_to_cglmp_worst_regret": reverse.worst_target_regret == Q(16,3),
        "existential_transfer_survives": forward.existential_transfer and reverse.existential_transfer,
        "mutation_missing_shift_detected": Counter(cglmp_strategy(s, missing_shift=True) for s in ss) != cc,
        "mutation_missing_marginal_detected": Counter(bgp_strategy(s, omit_marginals=True) for s in ss) != bc,
        "mutation_changed_bgp_coefficient_detected": Counter(bgp_strategy(s, altered_h=True) for s in ss) != bc,
    }
    return {
        "scope": "exact finite (2,2,4) deterministic Bell vertices; convex-hull local validity",
        "source": {"repository": UPSTREAM_REPO, "commit": UPSTREAM_COMMIT, "git_blobs": UPSTREAM_BLOBS},
        "evidence_level": "finite verified example; local inequalities extend by affine convexity",
        "external_theorems_not_replayed": [
            "PSI projective CGLMP optimality / rigidity",
            "PSI global noise comparison for m >= 955",
            "PSI KL comparison for m >= 41",
            "PSI four-outcome BGP facet dimension/rank and no-fusion proofs",
            "PSI Lean comparator/kernel build",
        ],
        "histogram": {
            "cglmp": {str(k): v for k,v in sorted(cc.items())},
            "bgp": {str(k): v for k,v in sorted(bc.items())},
        },
        "optimizer_transfer": {
            "cglmp_to_bgp": {
                "source_winners": forward.source_winners, "target_winners": forward.target_winners,
                "shared": forward.shared_winners, "worst_target_regret": str(forward.worst_target_regret),
                "all_source_maximizers_transfer": forward.universal_transfer,
                "some_source_maximizer_transfers": forward.existential_transfer,
                "counterexample": list(forward.counterexample) if forward.counterexample else None,
            },
            "bgp_to_cglmp": {
                "source_winners": reverse.source_winners, "target_winners": reverse.target_winners,
                "shared": reverse.shared_winners, "worst_target_regret": str(reverse.worst_target_regret),
                "all_source_maximizers_transfer": reverse.universal_transfer,
                "some_source_maximizer_transfers": reverse.existential_transfer,
                "counterexample": list(reverse.counterexample) if reverse.counterexample else None,
            },
        },
        "rational_witness": {
            "pbar_min_probability": str(min(pbar.values())),
            "pplus_min_probability": str(min(pplus.values())),
            "pbar_bgp": str(bgp_table(pbar)),
            "pplus_bgp": str(bgp_table(pplus)),
            "pplus_cglmp": str(cglmp_table(pplus)),
            "fixed_cglmp_local_bound": "2",
        },
        "checks": checks,
        "all_passed": all(checks.values()),
    }

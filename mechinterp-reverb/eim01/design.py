"""EIM-01: source-bound design for eval-to-mechanism causal experiments.

A row is a measured *signed next-readout effect* of donor-activation swaps,
one coordinate per tested BPD component. This is a finite linear-design
diagnostic; it never infers a neural mechanism from output accuracy alone.

For the present two-component proof-vs-cue gym, full column rank is a
necessary and sufficient identifiability condition for coefficients in
d = A theta under a stipulated linear response model. Independently
measured interactions and nonlinear models need additional interventions.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import hypot, isfinite, sqrt
from typing import Sequence


@dataclass(frozen=True)
class EffectRow:
    case_id: str
    donor_id: str
    origin_hash: str
    donor_hash: str
    model_hash: str
    split: str
    family: str
    role: str
    intervention_pass: int
    next_readout: int
    signed_effects: tuple[float, float]
    cost: int = 1
    route_observed: bool = True
    label_certified: bool = True

    def __post_init__(self) -> None:
        if (not self.case_id or not self.donor_id or not self.origin_hash
                or not self.donor_hash or not self.model_hash or not self.family
                or self.role not in {"aligned", "cue_only", "graph_only"}
                or self.split not in {"train", "dev", "test"}
                or type(self.intervention_pass) is not int
                or type(self.next_readout) is not int
                or self.intervention_pass < 0
                or self.next_readout <= self.intervention_pass
                or type(self.cost) is not int or self.cost < 1
                or type(self.route_observed) is not bool
                or type(self.label_certified) is not bool
                or len(self.signed_effects) != 2
                or any(not isfinite(float(a)) for a in self.signed_effects)):
            raise ValueError("Malformed source-bound intervention row")


def validate_candidate_rows(rows: Sequence[EffectRow]) -> tuple[EffectRow, ...]:
    records = tuple(rows)
    if not records:
        raise ValueError("Nonempty observed intervention table required")
    if any(r.split != "train" for r in records):
        raise ValueError("Only training-split effects can select training evals")
    if any(not r.route_observed or not r.label_certified for r in records):
        raise ValueError("An unobserved route or uncertified source label cannot be scored")
    anchor = (records[0].model_hash, records[0].intervention_pass,
              records[0].next_readout)
    if any((r.model_hash, r.intervention_pass, r.next_readout) != anchor
           for r in records):
        raise ValueError("A design must use one frozen model/pass/readout coordinate")
    if len({(r.case_id, r.donor_id, r.role) for r in records}) != len(records):
        raise ValueError("Duplicate intervention rows must be resolved explicitly")
    return records


def two_column_certificate(vectors: Sequence[tuple[float, float]],
                           *, atol: float = 1e-10) -> dict[str, float | int]:
    """Two-column SVD from the 2x2 Gram matrix, no ML dependency.

    A^T A = [[a,b],[b,d]].  The eigenvalues are
    (a+d +/- hypot(a-d,2b))/2. Rank depends on a declared tolerance.
    """
    if not vectors or atol <= 0:
        raise ValueError("Nonempty rows and positive numeric tolerance required")
    a = sum(float(x) ** 2 for x, _ in vectors)
    d = sum(float(y) ** 2 for _, y in vectors)
    b = sum(float(x)*float(y) for x, y in vectors)
    disc = hypot(a-d, 2*b)
    high = max(0., (a+d+disc)/2)
    # A Gram determinant avoids catastrophic cancellation near collinearity.
    det = max(0., a*d-b*b)
    low = min(high, det / high) if high > 0 else 0.
    smax = sqrt(high)
    smin = sqrt(max(0., low))
    rank = (int(smax > atol) + int(smin > atol))
    return {"rows": len(vectors), "rank": rank, "sigma_max": smax,
            "sigma_min": smin, "gram_determinant": det,
            "condition_number": smax / smin if smin > atol else float("inf")}


def select_identifying_evals(rows: Sequence[EffectRow],
                            *, budget: int = 2, atol: float = 1e-8) -> dict:
    """Exact two-intervention robust-design search on TRAIN rows.

    Maximize the lower singular value, with deterministic order/cost ties.
    The result is a measured design for a frozen model. It does not purport
    to identify latent components when component coordinates rotate.
    """
    candidates = validate_candidate_rows(rows)
    if budget < 2 or budget > len(candidates):
        raise ValueError("Two-column identification needs >=2 and <=N rows")
    best = None
    for idxs in combinations(range(len(candidates)), budget):
        cert = two_column_certificate([candidates[i].signed_effects for i in idxs],
                                      atol=atol)
        if cert["rank"] < 2:
            continue
        key = (-float(cert["sigma_min"]),
               sum(candidates[i].cost for i in idxs),
               idxs)
        if best is None or key < best[0]:
            best = (key, idxs, cert)
    if best is None:
        return {"identified": False, "reason": "no_full_rank_observed_design",
                "observations": len(candidates)}
    _, selected, cert = best
    return {"identified": True, "chosen": [candidates[i].case_id for i in selected],
            "chosen_roles": [candidates[i].role for i in selected],
            "selected_row_indices": list(selected), "certificate": cert,
            "total_probe_cost": sum(candidates[i].cost for i in selected)}


def coefficient_error_bound(rows: Sequence[tuple[float, float]],
                            max_observation_error: float, *, atol: float=1e-8) -> float:
    """If d=A theta+e and every |e_i|<=delta, ||theta_hat-theta||_2 <= sqrt(n)delta/sigma_min.

    This needs the signed-linear response assumption, exact A coordinates,
    and full rank; return infinity if A is singular under the tolerance.
    """
    if max_observation_error < 0 or not isfinite(max_observation_error):
        raise ValueError("Finite nonnegative noise bound required")
    cert = two_column_certificate(rows, atol=atol)
    if cert["rank"] < 2:
        return float("inf")
    return sqrt(len(rows)) * max_observation_error / float(cert["sigma_min"])


@dataclass(frozen=True)
class PreReadoutGeometry:
    """Keep readout-independent perturbation coordinates distinct from effects.

    An end-to-end output effect E[e,c] already contains the existing readout
    coefficient. It must NOT be substituted as the design matrix in the
    linear theorem d = A theta. The latter uses the independently measured
    component-signal delta Q[e,c], plus a specified transport factor.
    """
    observation: EffectRow
    activation_deltas: tuple[float, float]
    observed_joint_logit: float
    transport: float

    def __post_init__(self) -> None:
        if (len(self.activation_deltas) != 2
                or any(not isfinite(float(v)) for v in self.activation_deltas)
                or not isfinite(self.observed_joint_logit)
                or not isfinite(self.transport) or self.transport <= 0):
            raise ValueError("Invalid pre-readout geometry")


def select_geometry_basis(rows: Sequence[PreReadoutGeometry],
                          *, budget: int = 2, atol: float = 1e-8) -> dict:
    """Select independent perturbations BEFORE multiplying by readout weights."""
    points = tuple(rows)
    if not points:
        raise ValueError("Nonempty geometry required")
    validate_candidate_rows([p.observation for p in points])
    if budget < 2 or budget > len(points):
        raise ValueError("Invalid geometry selection budget")
    best = None
    for ids in combinations(range(len(points)), budget):
        A = [tuple(points[i].transport * v for v in points[i].activation_deltas)
             for i in ids]
        cert = two_column_certificate(A, atol=atol)
        if cert["rank"] < 2:
            continue
        key = (-float(cert["sigma_min"]),
               sum(points[i].observation.cost for i in ids), ids)
        if best is None or key < best[0]:
            best = (key, ids, cert)
    if best is None:
        return {"identified": False, "reason": "design_geometry_rank_deficient",
                "observations": len(points)}
    _, ids, cert = best
    return {"identified": True,
            "chosen": [points[i].observation.case_id for i in ids],
            "chosen_roles": [points[i].observation.role for i in ids],
            "selected_row_indices": list(ids),
            "certificate": cert,
            "matrix_semantics": "known_transport_times_pre_readout_activation_differences"}


def check_joint_linear_response(rows: Sequence[PreReadoutGeometry],
                                head_weights: tuple[float,float],
                                *, atol: float = 2e-5) -> list[float]:
    """Residual d_e - sum_c (transport_e * Q_ec * theta_c), from actual joint swaps.

    Only valid in a known linear circuit. Nonlinear source/carry dynamics
    require empirical interaction fits and new conditional predictions.
    """
    if len(head_weights) != 2 or any(not isfinite(float(w)) for w in head_weights):
        raise ValueError("Two finite readout weights required")
    if atol < 0:
        raise ValueError("Nonnegative residual tolerance required")
    residuals = []
    for point in rows:
        predicted = point.transport * sum(
            q * w for q,w in zip(point.activation_deltas, head_weights))
        err = point.observed_joint_logit - predicted
        if not isfinite(err) or abs(err) > atol:
            raise AssertionError(
                f"Linear source/response mismatch for {point.observation.case_id}: {err}"
            )
        residuals.append(err)
    return residuals

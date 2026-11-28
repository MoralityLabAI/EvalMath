"""ROC-01: an EvalMath validation interface for the public MathCan card.

The physical card is calculated in MathCan from T, U and output Jacobians.
EvalMath only scores the *declared* categorical intervention predictions:
it applies BPD-01's exact minimum-cost pair-separating cover, and refuses
a causal-confirmation flag when important measurement controls are absent.

Idealized tables are tutorial fixtures, not neural experiments.
Source pin: patrickdugan/MathCan@37bbac210c175ccb98e0ff0d4aa8bdd2be0764e6
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, isclose
from typing import Mapping, Sequence

from spiral_ln.evaluation_bpd import (
    Probe, coverage, minimum_batch, adaptive_worst_cost,
    identify_hypothesis, NO_HYPOTHESIS_FITS,
)

MATHCAN_SOURCE="37bbac210c175ccb98e0ff0d4aa8bdd2be0764e6"
REQUIRED_METRICS=("A_normalized","B_normalized","C_normalized",
                  "s_causal","task_mse","D_frob","H_trace")
ALLOWED_ARMS=("dark_to_observed","observed_to_dark",
              "observed_to_observed","ablate_readout")


@dataclass(frozen=True)
class InterventionObservation:
    name: str
    outcomes: tuple[int, ...]
    cost: int
    routed: bool
    measured: bool
    checkpoint_sha256: str
    observer_sha256: str
    next_readout: int
    intervention_pass: int
    norm_matched_random: bool

    def __post_init__(self):
        if (self.name not in ALLOWED_ARMS
                or len(self.outcomes)<2
                or any(type(x) is not int or x<0 for x in self.outcomes)
                or type(self.cost) is not int or self.cost<1
                or type(self.routed) is not bool
                or type(self.measured) is not bool
                or type(self.norm_matched_random) is not bool
                or not self.checkpoint_sha256 or not self.observer_sha256
                or type(self.intervention_pass) is not int
                or type(self.next_readout) is not int
                or self.intervention_pass<0
                or self.next_readout<=self.intervention_pass):
            raise ValueError("Malformed source-bound ROC intervention")


def identify_types(rows: Sequence[InterventionObservation],
                   realized: Mapping[str,int|None]|None=None,
                   *, card_audit: Mapping|None=None) -> dict:
    if not rows: raise ValueError("Nonempty mechanism arms required")
    if len({r.name for r in rows})!=len(rows):
        raise ValueError("Duplicate intervention names")
    checkpoint={r.checkpoint_sha256 for r in rows}
    observers={r.observer_sha256 for r in rows}
    times={(r.intervention_pass,r.next_readout) for r in rows}
    if len(checkpoint)!=1 or len(observers)!=1 or len(times)!=1:
        raise ValueError("Source, observer and clock must stay frozen across probes")
    if len({len(x.outcomes) for x in rows})!=1:
        raise ValueError("Mechanism hypothesis family must be fixed")
    probes=tuple(Probe(r.name,r.outcomes,r.cost,r.routed) for r in rows)
    cov=coverage(probes)
    minset=minimum_batch(probes)
    result={
        "source_mathcan_sha":MATHCAN_SOURCE,
        "covered_pairs":cov["separated_pairs"],
        "unresolved_pairs":cov["unresolved_pairs"],
        "equivalence_classes":cov["equivalence_classes"],
        "min_cost":minset[0] if minset is not None else None,
        "min_arms":list(minset[1]) if minset is not None else None,
        "adaptive_worst_cost":adaptive_worst_cost(probes),
        "measured":all(r.measured for r in rows),
        "all_norm_matched":all(r.norm_matched_random for r in rows),
        "intervention_arms_complete":set(r.name for r in rows)==set(ALLOWED_ARMS),
    }
    result["finite_intervention_separation_ready"]=bool(
        result["measured"] and result["all_norm_matched"]
        and result["intervention_arms_complete"]
        and not result["unresolved_pairs"]
    )
    # A finite type table can be source-consistent yet lack the causal Gram,
    # same-state task loss, checkpoint record or 128 valid null bases.
    # Do not promote its categorical separation alone into a full observer claim.
    result["causal_identification_ready"]=bool(
        result["finite_intervention_separation_ready"]
        and card_audit is not None
        and card_audit.get("complete") is True
        and card_audit.get("source_mathcan_sha")==MATHCAN_SOURCE
    )
    if realized is not None:
        result["realized"]=identify_hypothesis(probes,realized)
    return result


def audit_observer_card(card: Mapping, *, random_count:int,
                        task_only_equal_budget:bool,
                        every_intervention_norm_matched:bool,
                        output_declared:bool,
                        distinct_random_bases:int|None=None,
                        per_state_rows_public:bool=False,
                        null_calibration:Mapping|None=None) -> dict:
    """Fail closed for incomplete or nonnumeric ROC measurements.

    Control flags are caller attestations and must be independently audited
    against the pinned public source receipts. In particular, 128 attempts at
    a unique readout-containing rank-k basis are not 128 distinct null bases.
    """
    absent=[]
    invalid=[]
    for key in REQUIRED_METRICS:
        value=card.get(key)
        if value is None or value=="":
            absent.append(key)
            continue
        if type(value) not in (int,float) or not isfinite(value) or value<0:
            invalid.append(key)
            continue
        if key in ("A_normalized","B_normalized","C_normalized","s_causal") and value>1+1e-8:
            invalid.append(key)
    if ("s_causal" not in absent and "s_causal" not in invalid
            and "H_trace" not in absent and "H_trace" not in invalid
            and card["H_trace"]<=0):
        invalid.append("s_causal_with_zero_H")
    unique_ok=bool(
        type(random_count) is int and random_count>=100
        and type(distinct_random_bases) is int
        and 100<=distinct_random_bases<=random_count
    )
    # ROC-02 supersedes absolute tag cutoffs with rank-conditional null
    # medians and a fixed six-direction Holm family. Counts alone cannot
    # certify the new diagnostic or the leakage-penalty denominator.
    cal=null_calibration
    directions={"a_small","b_small","c_small","b_large","s_high","s_low"}
    null_ok=False
    if isinstance(cal,Mapping):
        med=cal.get("null_medians")
        raw=cal.get("one_sided_p")
        adj=cal.get("holm_adjusted_p")
        penalty=cal.get("b_penalty_ratio_squared")
        if (cal.get("schema")=="roc01.null_relative_six_direction.v1"
                and cal.get("tag_status")=="null_calibrated"
                and type(cal.get("distinct_null_subspaces")) is int
                and cal.get("distinct_null_subspaces")==distinct_random_bases
                and isinstance(med,Mapping) and isinstance(raw,Mapping)
                and isinstance(adj,Mapping)
                and set(raw)==directions and set(adj)==directions
                and type(med.get("B_normalized")) in (int,float)
                and isfinite(med["B_normalized"]) and med["B_normalized"]>0
                and type(penalty) in (int,float) and isfinite(penalty)
                and penalty>=0 and type(card.get("B_normalized")) in (int,float)):
            p_ok=all(
                type(raw[k]) in (int,float) and type(adj[k]) in (int,float)
                and isfinite(raw[k]) and isfinite(adj[k])
                and 0<=raw[k]<=adj[k]<=1 for k in directions
            )
            expected=(card["B_normalized"]/med["B_normalized"])**2
            null_ok=bool(p_ok and isfinite(expected)
                         and isclose(penalty,expected,rel_tol=1e-8,
                                     abs_tol=1e-10))
    required=bool(
        null_ok and unique_ok and task_only_equal_budget
        and every_intervention_norm_matched and output_declared
        and per_state_rows_public and not absent and not invalid
    )
    return {"source_mathcan_sha":MATHCAN_SOURCE,
            "complete":required,"missing_metrics":absent,
            "invalid_metrics":invalid,
            "random_count":random_count,
            "distinct_random_bases":distinct_random_bases,
            "random_rank_valid":unique_ok,
            "rank_null_calibration_valid":null_ok,
            "task_only_equal_budget":task_only_equal_budget,
            "norm_matched_interventions":every_intervention_norm_matched,
            "output_declared":output_declared,
            "per_state_rows_public":per_state_rows_public,
            "trust_boundary":"caller control attestation; independently verify pinned public Git blobs"}


IDEAL_TABLE={
    "dark_to_observed":(0,1,0,1,0),
    "observed_to_dark":(1,0,1,0,0),
    "observed_to_observed":(1,1,0,0,0),
    "ablate_readout":(1,1,1,1,0),
}
IDEAL_LABELS=("closed_quotient","invariant_subspace",
              "latched_memory","output_register","irrelevant")


def idealized_example()->dict:
    rows=[InterventionObservation(
        name,tuple(outcome),1,True,False,"synthetic","synthetic",2,1,False)
          for name,outcome in IDEAL_TABLE.items()]
    out=identify_types(rows)
    out["source_type"]="hypothetical_finite_signatures_not_neural_evidence"
    out["mechanism_labels"]=IDEAL_LABELS
    return out

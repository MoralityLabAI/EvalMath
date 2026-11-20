"""Count-augmented finite bridge for RHT-26's environmental carryover study.

The original four-state abstraction has a one-bit artifact state. This module
retains cue multiplicity to make final-snapshot repetition measurable. It only
proves finite consequences of *declared* stochastic kernels, not neural facts.
"""
from __future__ import annotations

from fractions import Fraction as Q
from typing import Mapping

MAX_CUES = 8
Law = tuple[Q, ...]


def _prob(x) -> Q:
    q = Q(x)
    if not 0 <= q <= 1:
        raise ValueError("probability must be between 0 and 1")
    return q


def point_mass(count: int) -> Law:
    if type(count) is not int or not 0 <= count <= MAX_CUES:
        raise ValueError("invalid cue count")
    return tuple(Q(i == count) for i in range(MAX_CUES + 1))


def _law(law) -> Law:
    result = tuple(_prob(v) for v in law)
    if len(result) != MAX_CUES + 1 or sum(result) != 1:
        raise ValueError("invalid count distribution")
    return result


def append_cue(law, *, probability=Q(1)) -> Law:
    """Append one retained cue with a constant conditional hazard."""
    dist = _law(law)
    p = _prob(probability)
    out = [Q(0) for _ in dist]
    for n, mass in enumerate(dist):
        out[n] += mass * (1 - p)
        out[min(n + 1, MAX_CUES)] += mass * p
    return tuple(out)


def after_exposures(exposures: int, *, write_probability=Q(1),
                    clear_each_boundary: bool = False) -> Law:
    if type(exposures) is not int or not 0 <= exposures <= MAX_CUES:
        raise ValueError("exposures outside finite horizon")
    state = point_mass(0)
    for _ in range(exposures):
        state = append_cue(state, probability=write_probability)
        if clear_each_boundary:
            state = point_mass(0)
    return state


def joint_persistence(law, endpoint: Mapping[int, Q]) -> Q:
    """Apply declared count-indexed joint-persistence probabilities."""
    dist = _law(law)
    if set(endpoint) != set(range(MAX_CUES + 1)):
        raise ValueError("endpoint requires all count states")
    return sum((dist[n] * _prob(endpoint[n]) for n in range(MAX_CUES + 1)), Q(0))


def collapse_presence(law) -> tuple[Q, Q]:
    """The old artifact bit a = 1 iff at least one cue is present."""
    dist = _law(law)
    return dist[0], sum(dist[1:], Q(0))


def store_after_history(actions: tuple[tuple[str, str], ...]) -> dict[str, str]:
    """Last-write-wins environmental store; histories may visit slots in any order."""
    state: dict[str, str] = {}
    for slot, value in actions:
        if not isinstance(slot, str) or not slot or value not in ("cue", "sham"):
            raise ValueError("invalid declared store write")
        state[slot] = value
    return state


def terminal_cue_count(store: Mapping[str, str]) -> int:
    n = sum(v == "cue" for v in store.values())
    if n > MAX_CUES or any(x not in ("cue", "sham") for x in store.values()):
        raise ValueError("invalid finite store")
    return n


def terminal_risk(store: Mapping[str, str], endpoint: Mapping[int, Q]) -> Q:
    """Shared terminal endpoint: historical write order is absent from its input."""
    n = terminal_cue_count(store)
    return _prob(endpoint[n])


def binary_projection_failure(endpoint: Mapping[int, Q]) -> bool:
    """Witness that artifact presence alone loses endpoint-relevant information."""
    if set(endpoint) != set(range(MAX_CUES + 1)):
        raise ValueError("endpoint requires all count states")
    values = [_prob(endpoint[n]) for n in range(1, MAX_CUES + 1)]
    return len(set(values)) > 1


def saturating_fixture() -> dict[int, Q]:
    """A declared nonmonotone saturation witness; not fitted model data."""
    values = (Q(0), Q(1, 8), Q(1, 2), Q(3, 4), Q(1),
              Q(1), Q(1), Q(1), Q(7, 8))
    return dict(enumerate(values))

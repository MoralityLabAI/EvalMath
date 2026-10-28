"""Reference mathematics for intervention-preserving compactification.

Pure Python / no model integration. Norms are Euclidean on finite tuples.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from math import log, sqrt
from typing import TypeAlias

Vector: TypeAlias = tuple[float, ...]
StateMap: TypeAlias = Callable[[Vector], Vector]


def dist(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y):
        raise ValueError("incompatible vector dimensions")
    return sqrt(sum((a - b) ** 2 for a, b in zip(x, y)))


def commutation_residual(
    state: Vector,
    compress: StateMap,
    full_transition: StateMap,
    abstract_transition: StateMap,
) -> float:
    return dist(compress(full_transition(state)), abstract_transition(compress(state)))


def near_fiber_lower_bound(
    states: Iterable[Vector],
    compress: StateMap,
    full_transition: StateMap,
    abstract_lipschitz: float,
    max_encoded_distance: float,
) -> float:
    """Certified lower bound on uniform commutation error for any L-Lipschitz G.

    Uses only sampled pairs. It makes no claim that the sampled states form a net.
    """
    if abstract_lipschitz < 0 or max_encoded_distance < 0:
        raise ValueError("Lipschitz constant and distance must be nonnegative")
    seq = list(states)
    best = 0.0
    for i, h in enumerate(seq):
        zh = compress(h)
        fzh = compress(full_transition(h))
        for other in seq[i + 1 :]:
            zo = compress(other)
            separation = dist(zh, zo)
            if separation <= max_encoded_distance:
                future_sep = dist(fzh, compress(full_transition(other)))
                best = max(best, (future_sep - abstract_lipschitz * separation) / 2)
    return best


def finite_horizon_bound(
    steps: int,
    one_step_error: float,
    readout_error: float,
    transition_lipschitz: float,
    readout_lipschitz: float,
) -> float:
    if steps < 0 or any(value < 0 for value in (
        one_step_error, readout_error, transition_lipschitz, readout_lipschitz
    )):
        raise ValueError("steps and constants must be nonnegative")
    propagated = 0.0
    for _ in range(steps):
        propagated = one_step_error + transition_lipschitz * propagated
    return readout_error + readout_lipschitz * propagated


def rollout(
    initial_state: Vector,
    compress: StateMap,
    actions: Sequence[str],
    full_transitions: dict[str, StateMap],
    abstract_transitions: dict[str, StateMap],
    full_readout: StateMap,
    abstract_readout: StateMap,
) -> tuple[float, Vector, Vector]:
    full = initial_state
    abstract = compress(initial_state)
    for action in actions:
        full = full_transitions[action](full)
        abstract = abstract_transitions[action](abstract)
    return dist(full_readout(full), abstract_readout(abstract)), full, abstract


def finite_cover_generalization_bound(
    n: int, alpha: float, cover_size: int, delta: float
) -> float:
    """Two-sided i.i.d. uniform deviation for [0,1]-valued loss functions."""
    if n <= 0 or cover_size <= 0 or alpha < 0 or not 0 < delta < 1:
        raise ValueError("invalid statistical inputs")
    return 2 * alpha + sqrt(log(2 * cover_size / delta) / (2 * n))


def flip_y(h: Vector) -> Vector:
    x, y = h
    return (x, -y)


def copy_y_to_x(h: Vector) -> Vector:
    _, y = h
    return (y, y)


def first_coordinate(h: Vector) -> Vector:
    return (h[0],)


def identity(z: Vector) -> Vector:
    return z

"""Exact finite Gated DeltaNet fixtures; no transformer runtime is implemented."""
from fractions import Fraction
from typing import Iterable

Scalar = int | Fraction
Matrix = tuple[tuple[Fraction, ...], ...]


def rational(value: Scalar) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError("exact int or Fraction required")
    return Fraction(value)


def matrix(rows: Iterable[Iterable[Scalar]]) -> Matrix:
    out = tuple(tuple(rational(x) for x in row) for row in rows)
    if not out or not out[0] or any(len(row) != len(out[0]) for row in out):
        raise ValueError("a nonempty rectangular matrix is required")
    return out


def key(size: int, address: int) -> tuple[Fraction, ...]:
    if type(size) is not int or type(address) is not int:
        raise TypeError("size and address must be integers, excluding bool")
    if size <= 0 or not 0 <= address < size:
        raise ValueError("address outside memory")
    return tuple(Fraction(i == address) for i in range(size))


def read(state: Matrix, query: Iterable[Scalar]) -> tuple[Fraction, ...]:
    state = matrix(state)
    query = tuple(rational(x) for x in query)
    if len(query) != len(state):
        raise ValueError("query dimension mismatch")
    return tuple(sum((query[i] * state[i][j] for i in range(len(state))), Fraction())
                 for j in range(len(state[0])))


def delta(state: Matrix, k: Iterable[Scalar], value: Iterable[Scalar],
          alpha: Scalar = 1, beta: Scalar = 1) -> Matrix:
    """Row-address convention: S' = a*S + b*k*(v - k^T*(a*S))."""
    state = matrix(state)
    k = tuple(rational(x) for x in k)
    value = tuple(rational(x) for x in value)
    alpha, beta = rational(alpha), rational(beta)
    if len(k) != len(state) or len(value) != len(state[0]):
        raise ValueError("write dimension mismatch")
    if not 0 <= alpha <= 1 or not 0 <= beta <= 2:
        raise ValueError("fixture gate outside declared range")
    gated = tuple(tuple(alpha * x for x in row) for row in state)
    old = read(gated, k)
    return tuple(tuple(gated[i][j] + beta * k[i] * (value[j] - old[j])
                       for j in range(len(value))) for i in range(len(state)))


def overwrite(state: Matrix, address: int, value: Iterable[Scalar]) -> Matrix:
    """Independent symbolic RAM update, used as the transition oracle."""
    state = matrix(state)
    key(len(state), address)
    value = tuple(rational(x) for x in value)
    if len(value) != len(state[0]):
        raise ValueError("word width mismatch")
    return state[:address] + (value,) + state[address + 1:]


def transpose(a: Matrix) -> Matrix:
    return tuple(zip(*matrix(a)))


def matmul(a: Matrix, b: Matrix) -> Matrix:
    a, b = matrix(a), matrix(b)
    if len(a[0]) != len(b):
        raise ValueError("matrix product dimension mismatch")
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction())
                       for j in range(len(b[0]))) for i in range(len(a)))


def verify_trace(initial: Matrix, writes: Iterable[tuple[int, Iterable[Scalar]]],
                 observed: Iterable[Matrix]) -> int:
    """Check every boundary, including initial state, against two independent updates."""
    state = matrix(initial)
    writes = tuple((a, tuple(v)) for a, v in writes)
    observed = tuple(matrix(s) for s in observed)
    if len(observed) != len(writes) + 1 or observed[0] != state:
        raise ValueError("missing or conflicting trace boundary")
    for step, (address, value) in enumerate(writes, 1):
        compiled = delta(state, key(len(state), address), value)
        symbolic = overwrite(state, address, value)
        if compiled != symbolic or observed[step] != symbolic:
            raise ValueError(f"transition mismatch at step {step}")
        state = symbolic
    return len(writes)

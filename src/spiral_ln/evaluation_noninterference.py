"""RHT-27: exact finite, interventional evaluation noninterference.

Each transcript indexes a supplied causal kernel, with the initial state and
all external context held fixed.  The finite vocabulary and permitted-feedback
map are external assumptions.  This module does not infer those kernels from
observational transcript conditionals or certify a physical model's boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Iterable, Mapping

from .evaluation_finite_kernels import (
    Kernel, compose, expectation, law, row_distance, total_variation,
)


def _labels(values: Iterable[str], name: str, *, unique: bool) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of labels")
    result = tuple(values)
    if not result or any(not isinstance(x, str) or not x.strip() for x in result):
        raise ValueError(f"{name} must contain nonempty string labels")
    if unique and len(set(result)) != len(result):
        raise ValueError(f"{name} must contain unique labels")
    return result


def _kernels(values: Iterable[Kernel], count: int) -> tuple[Kernel, ...]:
    result = tuple(values)
    if len(result) != count or any(not isinstance(k, Kernel) for k in result):
        raise ValueError("one Kernel is required for each label")
    shape = (result[0].input_size, result[0].output_size)
    if any((k.input_size, k.output_size) != shape for k in result):
        raise ValueError("all intervention kernels must have the same shape")
    return result


@dataclass(frozen=True)
class DifferenceWitness:
    """An explicit same-feedback intervention pair and TV-attaining event."""

    left: str
    right: str
    feedback: str
    initial_state: int
    event: tuple[int, ...]
    gap: Q


@dataclass(frozen=True)
class NoninterferenceAudit:
    epsilon: Q
    transcripts: int
    states: int
    fibres: int
    nontrivial_fibres: int
    covered_transcripts: int
    transcript_pairs: int
    row_comparisons: int
    witness: DifferenceWitness | None

    @property
    def identity_feedback_vacuous(self) -> bool:
        """True when no distinct transcript pair shares permitted feedback."""
        return self.transcript_pairs == 0

    @property
    def coverage(self) -> Q:
        return Q(self.covered_transcripts, self.transcripts)


@dataclass(frozen=True)
class PermittedSimulator:
    """A reference boundary whose kernel reads only state and permitted feedback."""

    feedback: tuple[str, ...]
    kernels: tuple[Kernel, ...]

    def __post_init__(self) -> None:
        labels = _labels(self.feedback, "feedback", unique=True)
        kernels = _kernels(self.kernels, len(labels))
        object.__setattr__(self, "feedback", labels)
        object.__setattr__(self, "kernels", kernels)

    def kernel(self, label: str) -> Kernel:
        try:
            return self.kernels[self.feedback.index(label)]
        except ValueError as error:
            raise ValueError(f"unknown permitted feedback: {label!r}") from error


@dataclass(frozen=True)
class RiskCertificate:
    """Worst-case bounded loss under a declared reference and its residual."""

    reference_risk: Q
    residual: Q
    actual_risk: Q
    risk_bound: Q


@dataclass(frozen=True)
class EvaluationInterface:
    """Finite intervention family K_e(s, .), with externally fixed phi(e).

    A row ranges over the complete retained state or a specifically declared
    joint output.  State labels are shared across interventions.  A reduced
    readout can conceal persistent state and must be identified as a readout.
    """

    transcripts: tuple[str, ...]
    feedback: tuple[str, ...]
    kernels: tuple[Kernel, ...]

    def __post_init__(self) -> None:
        transcripts = _labels(self.transcripts, "transcripts", unique=True)
        feedback = _labels(self.feedback, "feedback", unique=False)
        if len(feedback) != len(transcripts):
            raise ValueError("one permitted-feedback label is required per transcript")
        kernels = _kernels(self.kernels, len(transcripts))
        object.__setattr__(self, "transcripts", transcripts)
        object.__setattr__(self, "feedback", feedback)
        object.__setattr__(self, "kernels", kernels)

    def fibres(self) -> dict[str, tuple[int, ...]]:
        return {z: tuple(i for i, value in enumerate(self.feedback) if value == z)
                for z in dict.fromkeys(self.feedback)}

    def audit(self) -> NoninterferenceAudit:
        epsilon = Q(0)
        witness = None
        pairs = 0
        groups = self.fibres()
        for label, indices in groups.items():
            for position, left in enumerate(indices):
                for right in indices[position + 1:]:
                    pairs += 1
                    for state, (p, q) in enumerate(zip(self.kernels[left].rows,
                                                       self.kernels[right].rows)):
                        distance = total_variation(p, q)
                        if witness is None or distance > epsilon:
                            epsilon = distance
                            event = tuple(i for i, (a, b) in enumerate(zip(p, q)) if a > b)
                            witness = DifferenceWitness(self.transcripts[left],
                                                        self.transcripts[right], label,
                                                        state, event, distance)
        covered = sum(len(indices) for indices in groups.values() if len(indices) > 1)
        return NoninterferenceAudit(
            epsilon, len(self.transcripts), self.kernels[0].input_size,
            len(groups), sum(len(indices) > 1 for indices in groups.values()),
            covered, pairs, pairs * self.kernels[0].input_size, witness,
        )

    def permitted_simulator(
        self, weights: Mapping[str, Iterable[object]] | None = None,
    ) -> PermittedSimulator:
        """Build one representative, or a fixed convex mixture, per fibre.

        The weights may depend on permitted feedback, and are shared by every
        transcript in its fibre.  Missing, extra or unnormalised weights fail.
        This particular simulator need not minimize the maximum residual.
        """
        groups = self.fibres()
        if weights is not None and set(weights) != set(groups):
            raise ValueError("weights must cover exactly the permitted-feedback vocabulary")
        result = []
        for label, indices in groups.items():
            if weights is None:
                mixture = (Q(1),) + (Q(0),) * (len(indices) - 1)
            else:
                mixture = law(weights[label])
                if len(mixture) != len(indices):
                    raise ValueError("one mixture weight is required per transcript in the fibre")
            result.append(Kernel(tuple(
                tuple(sum((weight * self.kernels[index].rows[state][output]
                           for index, weight in zip(indices, mixture)), Q(0))
                      for output in range(self.kernels[0].output_size))
                for state in range(self.kernels[0].input_size))))
        return PermittedSimulator(tuple(groups), tuple(result))

    def residual(self, simulator: PermittedSimulator) -> Q:
        """Uniform row distance to a specified permitted-only reference."""
        if not isinstance(simulator, PermittedSimulator):
            raise ValueError("simulator must be a PermittedSimulator")
        if set(simulator.feedback) != set(self.feedback):
            raise ValueError("simulator must cover exactly the feedback vocabulary")
        return max(row_distance(kernel, simulator.kernel(label))
                   for label, kernel in zip(self.feedback, self.kernels))

    def factorization(self) -> PermittedSimulator:
        """Return K_e = K_bar_phi(e) exactly; reject a nonzero fibre diameter."""
        if self.audit().epsilon != 0:
            raise ValueError("intervention kernels do not factor through permitted feedback")
        return self.permitted_simulator()

    def postprocess(self, channel: Kernel) -> EvaluationInterface:
        """Apply the same declared channel to every intervention's output."""
        return EvaluationInterface(self.transcripts, self.feedback,
                                   tuple(compose(k, channel) for k in self.kernels))

    def risk_certificate(
        self, simulator: PermittedSimulator, loss: Iterable[object],
    ) -> RiskCertificate:
        """Bound a specified [0,1] loss; semantic authorization is external.

        Both reference risk and actual risk range over all declared initial
        states and feedback values.  Manipulation of a permitted value is
        therefore included in the reference-risk maximum.
        """
        payoff = tuple(loss)
        residual = self.residual(simulator)
        reference = max(expectation(row, payoff) for k in simulator.kernels for row in k.rows)
        actual = max(expectation(row, payoff) for k in self.kernels for row in k.rows)
        return RiskCertificate(reference, residual, actual, min(Q(1), reference + residual))


def permitted_learning_fixture() -> EvaluationInterface:
    """A supplied useful-bit update depends only on the registered score bit."""
    zero = Kernel(((1, 0), (1, 0)))
    one = Kernel(((0, 1), (0, 1)))
    return EvaluationInterface(
        ("score0:plain", "score0:hook", "score1:plain", "score1:hook"),
        ("score:0", "score:0", "score:1", "score:1"),
        (zero, zero, one, one),
    )


def unsafe_permitted_feedback_fixture() -> EvaluationInterface:
    """Same table as learning, with output one interpreted as an unsafe action.

    This fixture registers a loss semantics different from the useful-bit
    fixture.  The fibre property alone cannot establish which semantics holds.
    """
    return permitted_learning_fixture()


def reset_order_fixture() -> tuple[EvaluationInterface, EvaluationInterface, Kernel]:
    """Four states (artifact, policy); learner copies the artifact into policy.

    Returns reset-after-update, reset-before-update, and artifact-only readout.
    All finite transitions are synthetic and completely declared here.
    """
    states = tuple((a, p) for a in (0, 1) for p in (0, 1))

    def deterministic(images: Iterable[int], outputs: int) -> Kernel:
        return Kernel(tuple(tuple(int(j == image) for j in range(outputs)) for image in images))

    writes = tuple(deterministic((2 * bit + p for _, p in states), 4) for bit in (0, 1))
    learn = deterministic((2 * a + (a | p) for a, p in states), 4)
    reset = deterministic((p for _, p in states), 4)
    late = tuple(compose(compose(write, learn), reset) for write in writes)
    early = tuple(compose(compose(write, reset), learn) for write in writes)
    artifact_readout = deterministic((a for a, _ in states), 2)
    labels, feedback = ("plain", "hook"), ("score:0", "score:0")
    return (EvaluationInterface(labels, feedback, late),
            EvaluationInterface(labels, feedback, early), artifact_readout)

"""RHT-26: exact finite inter-episode carryover through artifacts and policy state.

State order is (artifact, policy) = 00, 01, 10, 11. These are declared toy
states, not measurements of model weights or intent. A state must contain all
history relevant to its future transition and outcome laws. Correlated state
mass is carried jointly throughout; its marginals are never multiplied.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product
from typing import Iterable

STATES = ((0, 0), (0, 1), (1, 0), (1, 1))
Law = tuple[Q, Q, Q, Q]
ZERO_STATE: Law = (Q(1), Q(0), Q(0), Q(0))


def _rational(value, label: str) -> Q:
    if isinstance(value, bool) or not isinstance(value, (int, Q)):
        raise ValueError(f"{label} must be an integer or Fraction")
    return Q(value)


def _probability(value, label: str) -> Q:
    value = _rational(value, label)
    if not 0 <= value <= 1:
        raise ValueError(f"{label} must be in [0, 1]")
    return value


def _distribution(values, label: str, size: int | None = None) -> tuple[Q, ...]:
    try:
        values = tuple(_probability(v, label) for v in values)
    except TypeError as exc:
        raise ValueError(f"{label} must be a finite probability vector") from exc
    if not values or (size is not None and len(values) != size) or sum(values) != 1:
        raise ValueError(f"{label} has invalid dimension or total mass")
    return values


def state_law(values) -> Law:
    """Validate a normalized joint law on the four registered states."""
    return _distribution(values, "state law", 4)


def _boolean(value, label: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{label} must be a bool")
    return value


@dataclass(frozen=True)
class Kernel:
    """A row-stochastic four-state transition, with exact rational entries."""

    rows: tuple[Law, Law, Law, Law]

    def __post_init__(self):
        try:
            rows = tuple(_distribution(row, "kernel row", 4) for row in self.rows)
        except TypeError as exc:
            raise ValueError("kernel must have four probability rows") from exc
        if len(rows) != 4:
            raise ValueError("kernel must have four probability rows")
        object.__setattr__(self, "rows", rows)


IDENTITY = Kernel(tuple(tuple(Q(i == j) for j in range(4)) for i in range(4)))
RESET_ARTIFACT = Kernel(tuple(
    tuple(Q(STATES[j] == (0, policy)) for j in range(4))
    for _, policy in STATES
))
RESET_ALL = Kernel((ZERO_STATE,) * 4)


def apply(law, kernel: Kernel) -> Law:
    """Push a joint law through a registered kernel."""
    law = state_law(law)
    if not isinstance(kernel, Kernel):
        raise ValueError("expected a Kernel")
    return tuple(sum((law[i] * kernel.rows[i][j] for i in range(4)), Q(0))
                 for j in range(4))


def compose(*kernels: Kernel) -> Kernel:
    """Compose in execution order: compose(A, B) first applies A, then B."""
    result = IDENTITY
    for kernel in kernels:
        if not isinstance(kernel, Kernel):
            raise ValueError("expected Kernel objects")
        result = Kernel(tuple(apply(row, kernel) for row in result.rows))
    return result


def evolve(initial, kernels: Iterable[Kernel]) -> Law:
    law = state_law(initial)
    for kernel in kernels:
        law = apply(law, kernel)
    return law


@dataclass(frozen=True)
class Episode:
    """A declared artifact exposure followed by an optional policy update.

    Exposure may depend on both state bits but must preserve the policy bit.
    The update may depend on both bits but must preserve the artifact bit.
    If shared episode information is absent from these state bits, this
    factorization is insufficient and the state space must be expanded.
    """

    exposure: Kernel
    update: Kernel

    def __post_init__(self):
        if not isinstance(self.exposure, Kernel) or not isinstance(self.update, Kernel):
            raise ValueError("episode stages must be Kernel objects")
        for i, (artifact, policy) in enumerate(STATES):
            for j, (next_artifact, next_policy) in enumerate(STATES):
                if policy != next_policy and self.exposure.rows[i][j]:
                    raise ValueError("artifact exposure must preserve policy state")
                if artifact != next_artifact and self.update.rows[i][j]:
                    raise ValueError("policy update must preserve artifact state")

    def kernel(self, *, keep_artifacts: bool, learn: bool,
               reset_before_update: bool = False) -> Kernel:
        keep_artifacts = _boolean(keep_artifacts, "keep_artifacts")
        learn = _boolean(learn, "learn")
        reset_before_update = _boolean(reset_before_update, "reset_before_update")
        reset = IDENTITY if keep_artifacts else RESET_ARTIFACT
        update = self.update if learn else IDENTITY
        if reset_before_update:
            return compose(self.exposure, reset, update)
        return compose(self.exposure, update, reset)


def run_episodes(initial, episodes: Iterable[Episode], *, keep_artifacts: bool,
                 learn: bool, reset_before_update: bool = False) -> Law:
    """Propagate episodes; disabling updates preserves the starting policy state."""
    _boolean(keep_artifacts, "keep_artifacts")
    _boolean(learn, "learn")
    _boolean(reset_before_update, "reset_before_update")
    law = state_law(initial)
    for episode in episodes:
        if not isinstance(episode, Episode):
            raise ValueError("expected Episode objects")
        law = apply(law, episode.kernel(keep_artifacts=keep_artifacts, learn=learn,
                                       reset_before_update=reset_before_update))
    return law


@dataclass(frozen=True)
class OutcomeReport:
    joint_law: Law
    pre_drift: Q
    post_drift: Q
    joint_persistence: Q
    conditional_persistence: Q | None


@dataclass(frozen=True)
class JointOutcome:
    """Per-state law of (drift before correction, drift after correction).

    The four columns are 00, 01, 10, 11. Correction is standardized and
    included in this declared outcome kernel. Persistence is column 11 on
    all chains, including chains with no initial drift.
    """

    rows: tuple[Law, Law, Law, Law]

    def __post_init__(self):
        rows = Kernel(self.rows).rows
        object.__setattr__(self, "rows", rows)

    def report(self, law) -> OutcomeReport:
        joint = apply(law, Kernel(self.rows))
        pre = joint[2] + joint[3]
        post = joint[1] + joint[3]
        return OutcomeReport(joint, pre, post, joint[3], joint[3] / pre if pre else None)


@dataclass(frozen=True)
class ArmResult:
    keep_artifacts: bool
    learn: bool
    final_state: Law
    outcome: OutcomeReport


@dataclass(frozen=True)
class FactorialResult:
    # Arm order: reset/frozen, reset/updated, retained/frozen, retained/updated.
    arms: tuple[ArmResult, ArmResult, ArmResult, ArmResult]
    interaction: Q


def factorial(initial, episodes: Iterable[Episode], endpoint: JointOutcome) -> FactorialResult:
    """Run the same source law and declared episode schedule in four causal arms."""
    initial = state_law(initial)
    if not isinstance(endpoint, JointOutcome):
        raise ValueError("expected a JointOutcome")
    episodes = tuple(episodes)
    arms = []
    for keep, learn in product((False, True), repeat=2):
        law = run_episodes(initial, episodes, keep_artifacts=keep, learn=learn)
        arms.append(ArmResult(keep, learn, law, endpoint.report(law)))
    p00, p01, p10, p11 = (arm.outcome.joint_persistence for arm in arms)
    return FactorialResult(tuple(arms), p11 - p10 - p01 + p00)


def total_variation(left, right) -> Q:
    left = _distribution(left, "left law")
    right = _distribution(right, "right law", len(left))
    return sum((abs(a - b) for a, b in zip(left, right)), Q(0)) / 2


def dobrushin(kernel: Kernel) -> Q:
    """Maximum TV distance between two rows of a kernel."""
    if not isinstance(kernel, Kernel):
        raise ValueError("expected a Kernel")
    return max(total_variation(a, b) for a in kernel.rows for b in kernel.rows)


@dataclass(frozen=True)
class TransmissionCertificate:
    initial_tv: Q
    final_tv: Q
    contraction_coefficients: tuple[Q, ...]
    contraction_bound: Q
    outcome_tv: Q
    pre_drift_gap: Q
    post_drift_gap: Q
    joint_persistence_gap: Q


def transmission_certificate(left, right, kernels: Iterable[Kernel],
                             endpoint: JointOutcome) -> TransmissionCertificate:
    """Certify carryover of two initial laws through the same future kernels.

    This does not compare different learning rules or adaptive policies. Those
    would require a perturbation bound or a state sufficient for both rules.
    """
    left, right = state_law(left), state_law(right)
    if not isinstance(endpoint, JointOutcome):
        raise ValueError("expected a JointOutcome")
    initial = total_variation(left, right)
    bound = initial
    coefficients = []
    for kernel in kernels:
        coefficient = dobrushin(kernel)
        coefficients.append(coefficient)
        bound *= coefficient
        left, right = apply(left, kernel), apply(right, kernel)
    final = total_variation(left, right)
    a, b = endpoint.report(left), endpoint.report(right)
    outcome_tv = total_variation(a.joint_law, b.joint_law)
    gaps = tuple(abs(getattr(a, key) - getattr(b, key))
                 for key in ("pre_drift", "post_drift", "joint_persistence"))
    if not max(gaps) <= outcome_tv <= final <= bound:
        raise AssertionError("finite transmission inequalities failed")
    return TransmissionCertificate(initial, final, tuple(coefficients), bound,
                                   outcome_tv, *gaps)


@dataclass(frozen=True)
class CueExperiment:
    """Declared full joint transcript laws under evaluation and deployment.

    Repeated copies of a source observation must be represented by their joint
    law. A product law encodes conditional independence as an assumption.
    """

    transcripts: tuple[str, ...]
    evaluation: tuple[Q, ...]
    deployment: tuple[Q, ...]

    def __post_init__(self):
        if (type(self.transcripts) is not tuple or not self.transcripts
                or any(type(x) is not str for x in self.transcripts)
                or len(set(self.transcripts)) != len(self.transcripts)):
            raise ValueError("transcripts must be a nonempty tuple of unique strings")
        for name in ("evaluation", "deployment"):
            law = _distribution(getattr(self, name), f"{name} cue law", len(self.transcripts))
            object.__setattr__(self, name, law)

    def posterior(self, prior, index: int) -> Q | None:
        prior = _probability(prior, "evaluation prior")
        if type(index) is not int or not 0 <= index < len(self.transcripts):
            raise ValueError("transcript index outside the registered experiment")
        e = prior * self.evaluation[index]
        d = (1 - prior) * self.deployment[index]
        return e / (e + d) if e + d else None


def _cue_experiment(e, d, count: int, *, independent: bool) -> CueExperiment:
    e, d = _probability(e, "evaluation positive cue"), _probability(d, "deployment positive cue")
    if type(count) is not int or not 0 <= count <= 12:
        raise ValueError("cue count must be an integer between zero and twelve")
    if count == 0:
        return CueExperiment(("",), (Q(1),), (Q(1),))
    words = tuple("".join(map(str, word)) for word in product((0, 1), repeat=count))
    def law(p):
        if independent:
            return tuple(p ** word.count("1") * (1 - p) ** word.count("0") for word in words)
        return tuple(p if word == "1" * count else 1 - p if word == "0" * count else Q(0)
                     for word in words)
    return CueExperiment(words, law(e), law(d))


def copied_cues(e, d, count: int) -> CueExperiment:
    return _cue_experiment(e, d, count, independent=False)


def iid_cues(e, d, count: int) -> CueExperiment:
    return _cue_experiment(e, d, count, independent=True)


def carryover_fixture() -> tuple[Episode, JointOutcome]:
    """Synthetic feedback witness with one-step additive interaction 1/32."""
    hazard = (Q(1, 8), Q(3, 8), Q(1, 4), Q(3, 4))
    exposure = Kernel(tuple(
        tuple((hazard[i] if next_artifact else 1 - hazard[i]) if policy == next_policy else Q(0)
              for next_artifact, next_policy in STATES)
        for i, (_, policy) in enumerate(STATES)
    ))
    update = Kernel(tuple(
        tuple(Q((next_artifact, next_policy) == (artifact, policy | artifact))
              for next_artifact, next_policy in STATES)
        for artifact, policy in STATES
    ))
    pre_drift = (Q(1, 4), Q(1, 2), Q(3, 4), Q(1))
    endpoint = JointOutcome(tuple((1 - b, Q(0), b - d, d)
                                  for b, d in zip(pre_drift, hazard)))
    return Episode(exposure, update), endpoint


def accumulation_fixture(write_probability=Q(1, 4)) -> Episode:
    """A retained artifact persists; a fresh marker is written with hazard p."""
    p = _probability(write_probability, "write probability")
    exposure = Kernel(tuple(
        tuple((Q(next_artifact == 1) if artifact else p if next_artifact else 1 - p)
              if policy == next_policy else Q(0)
              for next_artifact, next_policy in STATES)
        for artifact, policy in STATES
    ))
    return Episode(exposure, IDENTITY)

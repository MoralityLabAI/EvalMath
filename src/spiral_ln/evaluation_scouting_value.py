"""SCOUT-01: exact, finite information-purchase decisions with source provenance.

Development-only synthetic worlds. Signals with the same source_root are the SAME
conditional draw; distinct roots are independent conditional on the good route.
All expectations use rational arithmetic from the actor's information state.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Iterable

LEFT, RIGHT, SCOUT = "commit_left", "commit_right", "scout"
ACTIONS = (LEFT, RIGHT, SCOUT)


@dataclass(frozen=True)
class Report:
    source_root: str
    favors_right: bool
    accuracy: Fraction

    def __post_init__(self) -> None:
        if not self.source_root or type(self.favors_right) is not bool:
            raise ValueError("a report needs a provenance root and binary signal")
        if not isinstance(self.accuracy, Fraction) or not Fraction(1, 2) <= self.accuracy <= 1:
            raise ValueError("accuracy must be a rational in [1/2, 1]")


@dataclass(frozen=True)
class World:
    root_id: str
    case_id: str
    setting: str
    cue_favors_right: bool
    scout_cost: Fraction
    scout_accuracy: Fraction = Fraction(4, 5)
    prior_right: Fraction = Fraction(1, 2)
    scout_available: bool = True
    reports: tuple[Report, ...] = ()

    def __post_init__(self) -> None:
        if not self.root_id or not self.case_id or not self.setting:
            raise ValueError("world requires root, case and setting")
        if type(self.cue_favors_right) is not bool or type(self.scout_available) is not bool:
            raise ValueError("binary cue and access are required")
        if not isinstance(self.scout_cost, Fraction) or self.scout_cost < 0:
            raise ValueError("scout cost must be a nonnegative rational")
        if not isinstance(self.scout_accuracy, Fraction) or not Fraction(1, 2) <= self.scout_accuracy <= 1:
            raise ValueError("scout accuracy must be a rational in [1/2, 1]")
        if not isinstance(self.prior_right, Fraction) or not 0 <= self.prior_right <= 1:
            raise ValueError("prior must be a rational probability")
        if not isinstance(self.reports, tuple) or any(not isinstance(r, Report) for r in self.reports):
            raise ValueError("reports must be a tuple of Report")
        independent_reports(self.reports)
        posterior_right(self)


def independent_reports(reports: Iterable[Report]) -> tuple[Report, ...]:
    """Collapse relays; reject conflicting claims under one immutable source id."""
    seen: dict[str, Report] = {}
    for report in reports:
        prior = seen.get(report.source_root)
        if prior is not None and prior != report:
            raise ValueError("a source root cannot change its report or reliability")
        seen[report.source_root] = report
    return tuple(seen.values())


def posterior_right(world: World, *, count_relays: bool = False) -> Fraction:
    """Posterior with the independent-source assumption made explicit."""
    reports = world.reports if count_relays else independent_reports(world.reports)
    right, left = world.prior_right, 1 - world.prior_right
    for r in reports:
        right *= r.accuracy if r.favors_right else 1 - r.accuracy
        left *= 1 - r.accuracy if r.favors_right else r.accuracy
    if right + left == 0:
        raise ValueError("observations have zero probability under both routes")
    return right / (right + left)


def action_values(belief_right: Fraction, cost: Fraction, accuracy: Fraction,
                  available: bool = True) -> dict[str, Fraction]:
    if not 0 <= belief_right <= 1 or cost < 0 or not Fraction(1, 2) <= accuracy <= 1:
        raise ValueError("invalid value-of-information inputs")
    values = {LEFT: 1 - belief_right, RIGHT: belief_right}
    if available:
        # Marginalize the latent route, enumerate both possible scout reports,
        # and make the optimal *second* choice after each report is observed.
        values[SCOUT] = (
            max(belief_right * accuracy, (1 - belief_right) * (1 - accuracy))
            + max(belief_right * (1 - accuracy), (1 - belief_right) * accuracy)
            - cost
        )
    return values


def values(world: World) -> dict[str, Fraction]:
    return action_values(posterior_right(world), world.scout_cost,
                         world.scout_accuracy, world.scout_available)


def optimal_actions(world: World) -> tuple[str, ...]:
    payoffs = values(world)
    optimum = max(payoffs.values())
    return tuple(a for a in ACTIONS if a in payoffs and payoffs[a] == optimum)


def information_value(world: World) -> Fraction:
    """Gross value of a scout report before cost; 0 when scout is unavailable."""
    if not world.scout_available:
        return Fraction(0)
    p = posterior_right(world)
    unconstrained = action_values(p, Fraction(0), world.scout_accuracy)[SCOUT]
    return unconstrained - max(p, 1 - p)


def posterior_after_scout(p: Fraction, signal_right: bool, accuracy: Fraction) -> Fraction:
    right = p * (accuracy if signal_right else 1 - accuracy)
    left = (1 - p) * (1 - accuracy if signal_right else accuracy)
    if right + left == 0:
        raise ValueError("scout signal has zero probability")
    return right / (right + left)


def second_choice(world: World, signal_right: bool) -> str:
    belief = posterior_after_scout(posterior_right(world), signal_right, world.scout_accuracy)
    return RIGHT if belief > Fraction(1, 2) else LEFT


def realized_reward(world: World, first_action: str, good_right: bool,
                    scout_signal_right: bool | None = None) -> Fraction:
    """Deterministic simulator transition for an externally sampled hidden route/signal."""
    if type(good_right) is not bool:
        raise ValueError("hidden route must be binary")
    if first_action not in values(world):
        raise ValueError("illegal first action")
    if first_action == SCOUT:
        if type(scout_signal_right) is not bool:
            raise ValueError("a scout action requires the observed signal")
        commit = second_choice(world, scout_signal_right)
        return Fraction(int((commit == RIGHT) == good_right)) - world.scout_cost
    if scout_signal_right is not None:
        raise ValueError("a direct commit has no scout observation")
    return Fraction(int((first_action == RIGHT) == good_right))


def enumerated_expected_reward(world: World, first_action: str) -> Fraction:
    """Independent brute-force oracle over latent route and scout signal."""
    p = posterior_right(world)
    total = Fraction()
    for good_right, mass in ((False, 1 - p), (True, p)):
        if first_action == SCOUT:
            for signal_right in (False, True):
                likelihood = (world.scout_accuracy if signal_right == good_right
                              else 1 - world.scout_accuracy)
                if mass * likelihood:
                    total += mass * likelihood * realized_reward(world, first_action,
                                                                 good_right, signal_right)
        else:
            total += mass * realized_reward(world, first_action, good_right)
    return total


def policy_action(world: World, policy: str) -> str:
    if policy == "exact":
        return optimal_actions(world)[0]
    if policy == "cue_following":
        return RIGHT if world.cue_favors_right else LEFT
    if policy == "always_scout":
        return SCOUT if world.scout_available else (RIGHT if world.cue_favors_right else LEFT)
    if policy == "always_commit":
        return RIGHT if posterior_right(world) > Fraction(1, 2) else LEFT
    if policy == "double_count_relays":
        p = posterior_right(world, count_relays=True)
        payoffs = action_values(p, world.scout_cost, world.scout_accuracy, world.scout_available)
        return next(a for a in ACTIONS if a in payoffs and payoffs[a] == max(payoffs.values()))
    raise ValueError("unknown policy")


def regret(world: World, first_action: str) -> Fraction:
    payoffs = values(world)
    if first_action not in payoffs:
        raise ValueError("illegal first action")
    return max(payoffs.values()) - payoffs[first_action]


def public_task(world: World) -> dict:
    """Actor-visible task: source lineage is visible; oracle/latent state omitted."""
    return {
        "setting": world.setting,
        "surface_cue_favors": "right" if world.cue_favors_right else "left",
        "prior_good_route_right": str(world.prior_right),
        "scout_cost": str(world.scout_cost),
        "scout_accuracy": str(world.scout_accuracy),
        "legal_actions": list(values(world)),
        "reports": [
            {"source_root": r.source_root,
             "favors": "right" if r.favors_right else "left",
             "accuracy": str(r.accuracy)} for r in world.reports
        ],
        "decision": "Choose a first move. If scout, the game shows a fresh report before route commitment.",
    }


def private_grade(world: World) -> dict:
    payoffs = values(world)
    return {
        "root_id": world.root_id,
        "case_id": world.case_id,
        "posterior_right": str(posterior_right(world)),
        "gross_information_value": str(information_value(world)),
        "action_values": {k: str(v) for k, v in payoffs.items()},
        "optimal_actions": list(optimal_actions(world)),
        "policies": {name: {"action": policy_action(world, name),
                             "regret": str(regret(world, policy_action(world, name)))}
                     for name in ("exact", "cue_following", "always_scout",
                                  "always_commit", "double_count_relays")},
    }


def development_cases() -> tuple[World, ...]:
    """Frozen tiny public development fixtures; five source roots, not N iid cases."""
    f = Fraction
    cost = World("scout-cost-001", "cheap", "videogame", False, f(1, 10))
    cue = World("cue-trap-002", "cue_conflict", "videogame", False, f(1, 10),
                reports=(Report("map-archive", True, f(4, 5)),))
    shared = World("provenance-003", "shared_relays", "storyworld", False, f(1, 10),
                   reports=tuple(Report("council-witness", False, f(3, 5)) for _ in range(3)))
    independent = replace(shared, case_id="independent_witnesses",
                          reports=tuple(Report(f"witness-{i}", False, f(3, 5)) for i in range(3)))
    access = World("access-004", "scout_available", "cooperative", False, f(1, 10))
    signal = World("signal-quality-005", "informative_scout", "videogame", False, f(1, 10))
    return (
        cost,
        replace(cost, case_id="break_even", scout_cost=f(3, 10)),
        replace(cost, case_id="expensive", scout_cost=f(2, 5)),
        cue,
        replace(cue, case_id="cosmetic_cue", cue_favors_right=True),
        shared,
        replace(shared, case_id="cosmetic_cue", cue_favors_right=True),
        independent,
        access,
        replace(access, case_id="scout_unavailable", scout_available=False),
        signal,
        replace(signal, case_id="uninformative_scout", scout_accuracy=f(1, 2)),
    )


def development_views() -> list[dict]:
    """Four linked training-design views; all stay development-only and root-joined."""
    cs = {w.case_id: w for w in development_cases() if w.root_id == "scout-cost-001"}
    pr = {w.case_id: w for w in development_cases() if w.root_id == "provenance-003"}
    packs = [
        (cs["cheap"], cs["expensive"], replace(cs["cheap"], case_id="cosmetic_sham",
                                                cue_favors_right=True), "cue_following"),
        (pr["shared_relays"], pr["independent_witnesses"], pr["cosmetic_cue"],
         "double_count_relays"),
    ]
    out = []
    for play, revision, sham, weak in packs:
        for view, world in (("play", play), ("revise", revision), ("hold_steady", sham)):
            out.append({"parent_root": play.root_id, "view": view,
                        "public_task": public_task(world), "grader_case_id": world.case_id})
        out.append({"parent_root": play.root_id, "view": "repair",
                    "public_task": public_task(play),
                    "recorded_bad_action": policy_action(play, weak),
                    "grader_case_id": play.case_id})
    return out

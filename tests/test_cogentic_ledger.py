import copy
from fractions import Fraction

import pytest

from spiral_ln.cogentic_ledger import (
    evaluate,
    fixture,
    paired_manifest,
    registry_digest,
    replay_episode,
    step,
)


def test_duplicate_and_irrelevant_accepts_receive_distinct_credit():
    task, rows = fixture()
    result = replay_episode(task, rows, 6)
    assert result["accepted"] == 5
    assert result["rejected"] == 1
    assert result["duplicates"] == 1
    assert result["unique_verified_facts"] == 4
    assert result["goal_ancestor_verified_facts"] == 3
    assert result["irrelevant_new_facts"] == 1
    assert result["first_solution_call"] == 6
    assert Fraction(result["goal_ancestor_facts_per_call"]) == Fraction(1, 2)


@pytest.mark.parametrize("corruption", ["state", "history", "receipt", "calls", "order", "world"])
def test_forged_progress_and_omitted_cost_are_rejected(corruption):
    task, rows = fixture()
    if corruption == "state":
        rows[0]["observation"]["known"].append(task["world"]["goal"])
    elif corruption == "history":
        rows[1]["observation"]["history"][0]["accepted"] = True
    elif corruption == "receipt":
        rows[0]["receipt"]["accepted"] = True
    elif corruption == "calls":
        rows[0]["verifier_calls"] = 0
    elif corruption == "order":
        rows.pop(0)
    else:
        rows[0]["observation"]["world"]["facts"].append(3)
    with pytest.raises(ValueError):
        replay_episode(task, rows, 6)


def test_budget_overflow_fails_and_boolean_action_is_rejected():
    task, rows = fixture()
    with pytest.raises(ValueError, match="budget"):
        replay_episode(task, rows, 5)
    result = step(task["world"], {0}, True)
    assert result["accepted"] is False
    assert result["verifier_calls"] == 1


def test_zero_call_denominator_and_already_proved_goal():
    task, _ = fixture()
    result = replay_episode(task, [], 0)
    assert result["solved"] is False
    assert result["verified_facts_per_call"] is None
    task["world"]["facts"].append(3)
    result = replay_episode(task, [], 0)
    assert result["solved"] is True
    assert result["first_solution_call"] == 0


def test_full_registry_keeps_missing_and_repeated_root_runs():
    task, rows = fixture()
    second = copy.deepcopy(task)
    second.update(root_id="second", task_id="second")
    second["world"]["goal"] = 4
    events = [dict(row, arm="candidate", seed=17, root_id=task["root_id"])
              for row in rows]
    protocol = {"schema_version": 1, "arms": ["candidate", "baseline"],
                "seeds": [17, 29], "splits": ["development"], "budget": 6}
    report = evaluate([task, second], events, protocol)
    candidate = next(r for r in report["summary"] if r["arm"] == "candidate")
    assert candidate["independent_roots"] == 2
    assert candidate["seed_runs"] == 4
    assert candidate["missing_runs"] == 3
    assert candidate["solve_fraction_exact"] == "1/4"
    assert candidate["completed_runs_per_call"] is None
    assert candidate["completed_runs_per_allocated_call"] == "1/24"
    assert candidate["complete_trace_coverage"] is False
    manifest = paired_manifest(report, "candidate", "baseline", "development", comparisons=1)
    assert len(manifest["cases"]) == 4
    assert len({r["cluster_id"] for r in manifest["cases"]}) == 2
    assert manifest["sealed_readout"] is False


def test_cross_split_root_alias_is_rejected():
    task, _ = fixture()
    second = dict(task, split="other")
    protocol = {"schema_version": 1, "arms": ["candidate"], "seeds": [17],
                "splits": ["development", "other"], "budget": 1}
    with pytest.raises(ValueError, match="duplicate root"):
        evaluate([task, second], [], protocol)
    protocol["splits"] = ["development"]
    with pytest.raises(ValueError, match="duplicate root"):
        evaluate([task, second], [], protocol)


def test_identical_world_cannot_inflate_independent_root_count():
    task, _ = fixture()
    second = dict(task, root_id="alias", task_id="alias")
    protocol = {"schema_version": 1, "arms": ["candidate"], "seeds": [17],
                "splits": ["development"], "budget": 6}
    with pytest.raises(ValueError, match="identical world"):
        evaluate([task, second], [], protocol)


def test_unregistered_attempt_is_rejected():
    task, rows = fixture()
    protocol = {"schema_version": 1, "arms": ["candidate"], "seeds": [17],
                "splits": ["development"], "budget": 6}
    events = [dict(row, arm="candidate", seed=17, root_id="unregistered") for row in rows]
    with pytest.raises(ValueError, match="unregistered"):
        evaluate([task], events, protocol)


def test_population_cannot_shrink_after_protocol_commitment():
    task, _ = fixture()
    second = copy.deepcopy(task)
    second.update(root_id="second", task_id="second")
    second["world"]["goal"] = 4
    tasks = [task, second]
    protocol = {"schema_version": 1, "arms": ["candidate"], "seeds": [17],
                "splits": ["development"], "budget": 6,
                "expected_registry_sha256": registry_digest(tasks),
                "expected_root_counts": {"development": 2}}
    with pytest.raises(ValueError, match="registry"):
        evaluate([task], [], protocol)

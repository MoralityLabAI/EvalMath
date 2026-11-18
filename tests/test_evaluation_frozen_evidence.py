"""Adversarial records for FRE-01; all timings and anchors are synthetic fixtures."""
from copy import deepcopy
from fractions import Fraction

import pytest

from spiral_ln.evaluation_frozen_evidence import (
    SCHEMA, audit_frozen_evidence, canonical_bytes, input_identity, read_json, sha256,
)


def fixture():
    sources = {
        "experiment_id": "FRE-01-fixture", "schema": "source-wrapper-v1",
        "cases": [
            {"case_id": "a", "root_id": "root-a", "query": [1, 0, 2],
             "program": {"operator": "inverse", "degree": 2}, "profile": "old"},
            {"case_id": "b", "root_id": "root-b", "query": [1, 0, -2],
             "program": {"operator": "inverse", "degree": 2}, "profile": "old"},
        ],
    }
    source_raw = canonical_bytes(sources)
    attempt = {
        "schema": SCHEMA, "experiment_id": sources["experiment_id"],
        "attempt_id": "registered-first", "role": "original", "outcome": "fail",
        "registration_sha256": "a" * 64, "sources_sha256": sha256(source_raw),
        "previous_attempt_id": None, "previous_attempt_sha256": None,
        "arms": {"original": "in_call", "warm": "outside_call"}, "timings": [],
    }
    for row in sources["cases"]:
        for repeat in range(2):
            context = sha256(f"{row['case_id']}-{repeat}".encode())
            for arm, duration in (("original", 100), ("warm", 75)):
                attempt["timings"].append({
                    "case_id": row["case_id"], "repeat": repeat, "arm": arm,
                    "context_sha256": context, "elapsed_ns": duration,
                    "task_sha256": input_identity(row["query"], row["program"])["task_sha256"],
                    "phase_ns": {"root": 10, "execution": 20},
                })
    first_raw = canonical_bytes(attempt)
    anchor = {
        "schema": SCHEMA, "experiment_id": sources["experiment_id"],
        "registration_sha256": attempt["registration_sha256"],
        "sources_sha256": sha256(source_raw), "first_attempt_id": attempt["attempt_id"],
        "first_attempt_sha256": sha256(first_raw), "repeats": 2,
        "arms": attempt["arms"], "baseline_arm": "original",
        "unique_queries": True, "fresh_context_per_repeat": True,
        "excluded_task_sha256": [],
    }
    return anchor, sources, attempt


def audit(anchor, sources, attempt):
    return audit_frozen_evidence(anchor, canonical_bytes(sources), [canonical_bytes(attempt)])


def reanchor(anchor, sources, attempt):
    """Build a new synthetic fixture anchor after an intentional unit-test mutation."""
    anchor["sources_sha256"] = sha256(canonical_bytes(sources))
    attempt["sources_sha256"] = anchor["sources_sha256"]
    anchor["first_attempt_sha256"] = sha256(canonical_bytes(attempt))


def test_original_failure_survives_a_successful_diagnostic():
    anchor, sources, attempt = fixture()
    original_raw = canonical_bytes(attempt)
    later = deepcopy(attempt)
    later.update(attempt_id="diagnostic-2", role="diagnostic", outcome="pass",
                 previous_attempt_id=attempt["attempt_id"],
                 previous_attempt_sha256=sha256(original_raw), reason="Investigate a failed gate")
    for row in later["timings"]:
        if row["arm"] == "warm":
            row["elapsed_ns"] = 50
    result = audit_frozen_evidence(anchor, canonical_bytes(sources),
                                   [original_raw, canonical_bytes(later)])
    assert result["integrity_passed"] is True
    assert result["original_declared_outcome"] == "fail"
    assert result["attempt_history"][1]["outcome"] == "pass"
    assert result["original_ratio_of_sum_case_medians"]["warm"] == "3/4"


def test_outer_schema_and_labels_cannot_hide_a_duplicate_task():
    anchor, sources, attempt = fixture()
    a, b = sources["cases"]
    b.update(query=deepcopy(a["query"]), program=deepcopy(a["program"]),
             schema="unrelated-v9", profile="new", seed=999999)
    reanchor(anchor, sources, attempt)
    with pytest.raises(ValueError, match="task is duplicated"):
        audit(anchor, sources, attempt)


def test_query_identity_is_separate_from_program_identity():
    first = input_identity([1, 0, 2], {"operator": "inverse", "degree": 2})
    second = input_identity([1, 0, 2], {"operator": "negate", "degree": 2})
    assert first["query_sha256"] == second["query_sha256"]
    assert first["task_sha256"] != second["task_sha256"]
    assert first != input_identity([1, 0, 3], {"operator": "inverse", "degree": 2})


def test_canonical_map_order_and_exact_type_distinction():
    assert input_identity([1], {"a": 2, "b": 3}) == input_identity([1], {"b": 3, "a": 2})
    assert input_identity([1], {}) != input_identity([True], {})


@pytest.mark.parametrize("bad", [0.0, float("nan"), float("inf"), (1, 2), {1: 2}])
def test_ambiguous_or_inexact_query_values_fail(bad):
    with pytest.raises(ValueError):
        input_identity([bad], {})


def test_source_bytes_remain_bound_even_when_semantics_match():
    anchor, sources, attempt = fixture()
    source_raw = canonical_bytes(sources) + b" "
    with pytest.raises(ValueError, match="source artifact differs"):
        audit_frozen_evidence(anchor, source_raw, [canonical_bytes(attempt)])


def test_changed_original_cannot_be_relabelled_as_first():
    anchor, sources, attempt = fixture()
    attempt.update(outcome="pass", first=True)
    with pytest.raises(ValueError, match="first attempt differs"):
        audit(anchor, sources, attempt)


def test_independent_anchor_requires_expected_first_identity_and_hash():
    anchor, sources, attempt = fixture()
    del anchor["first_attempt_sha256"]
    anchor["first"] = True
    with pytest.raises(ValueError, match="first_attempt_sha256"):
        audit(anchor, sources, attempt)


@pytest.mark.parametrize("field", ["previous_attempt_id", "previous_attempt_sha256", "role"])
def test_orphaned_or_promoted_amendments_fail(field):
    anchor, sources, attempt = fixture()
    first_raw = canonical_bytes(attempt)
    later = deepcopy(attempt)
    later.update(attempt_id="diagnostic-2", role="diagnostic", reason="audit",
                 previous_attempt_id=attempt["attempt_id"], previous_attempt_sha256=sha256(first_raw))
    later[field] = "original" if field == "role" else "wrong"
    with pytest.raises(ValueError, match="orphaned or promoted"):
        audit_frozen_evidence(anchor, canonical_bytes(sources), [first_raw, canonical_bytes(later)])


@pytest.mark.parametrize("bad", [-1, 0, True, 1.5, float("nan"), float("inf")])
def test_nonpositive_noninteger_and_nonfinite_timing_is_rejected(bad):
    import json
    anchor, sources, attempt = fixture()
    attempt["timings"][0]["elapsed_ns"] = bad
    raw = (json.dumps(attempt) + "\n").encode()
    anchor["first_attempt_sha256"] = sha256(raw)
    with pytest.raises(ValueError, match="elapsed_ns|nonfinite"):
        audit_frozen_evidence(anchor, canonical_bytes(sources), [raw])


@pytest.mark.parametrize("mutation", ["omit", "duplicate", "context", "task", "phase", "repeat"])
def test_unmatched_measurements_fail_closed(mutation):
    anchor, sources, attempt = fixture()
    if mutation == "omit":
        attempt["timings"].pop()
    elif mutation == "duplicate":
        attempt["timings"].append(deepcopy(attempt["timings"][0]))
    elif mutation == "context":
        attempt["timings"][0]["context_sha256"] = "b" * 64
    elif mutation == "task":
        attempt["timings"][0]["task_sha256"] = "b" * 64
    elif mutation == "phase":
        attempt["timings"][0]["phase_ns"] = {"impossible": 101}
    else:
        attempt["timings"][0]["repeat"] = 2
    reanchor(anchor, sources, attempt)
    with pytest.raises(ValueError):
        audit(anchor, sources, attempt)


def test_cold_policy_cannot_be_silently_switched_to_warm():
    anchor, sources, attempt = fixture()
    attempt["arms"] = {"original": "outside_call", "warm": "outside_call"}
    reanchor(anchor, sources, attempt)
    with pytest.raises(ValueError, match="setup policies"):
        audit(anchor, sources, attempt)


def test_older_exact_task_is_excluded_despite_new_wrapper():
    anchor, sources, attempt = fixture()
    row = sources["cases"][0]
    anchor["excluded_task_sha256"] = [input_identity(row["query"], row["program"])["task_sha256"]]
    with pytest.raises(ValueError, match="excluded source"):
        audit(anchor, sources, attempt)


def test_repeated_nonce_fails_the_registered_context_policy():
    anchor, sources, attempt = fixture()
    for row in attempt["timings"]:
        row["context_sha256"] = "b" * 64
    reanchor(anchor, sources, attempt)
    with pytest.raises(ValueError, match="reused context"):
        audit(anchor, sources, attempt)


def test_strict_json_rejects_duplicate_keys():
    with pytest.raises(ValueError, match="duplicate JSON key"):
        read_json(b'{"outcome":"fail","outcome":"pass"}')


def test_declared_roots_are_counted_separately_from_repeats():
    anchor, sources, attempt = fixture()
    sources["cases"][1]["root_id"] = sources["cases"][0]["root_id"]
    reanchor(anchor, sources, attempt)
    result = audit(anchor, sources, attempt)
    assert result["case_count"] == 2
    assert result["declared_root_count"] == 1
    assert result["repeat_count"] == 2
    assert Fraction(result["original_sum_case_medians_ns"]["warm"]) == 150

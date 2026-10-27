"""Adversarial logical controls for the Cryptomania assumption ledger."""
from __future__ import annotations

import copy
import json
from fractions import Fraction as Q
from pathlib import Path

import pytest

from spiral_ln.cryptomania_audit import (
    WORLD_ORDER, bayes_example, bayes_worlds, compatible_worlds,
    propagate, report, score_routes, validate_manifest,
)
from spiral_ln.cryptomania_toy_count import (
    components, exact_count, factorized_count, run_toy_suite,
    seeded_instance, validate_cnf,
)

MANIFEST = Path(__file__).resolve().parents[1] / "configs/cryptomania_assumptions_v1.json"


@pytest.fixture
def data():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_schema_and_all_five_worlds(data):
    validate_manifest(data)
    assert compatible_worlds(data, {}) == list(WORLD_ORDER)


def test_reported_eth_disproof_does_not_eliminate_any_world(data):
    status, reasons = propagate(data, {"ETH": False})
    assert compatible_worlds(data, {"ETH": False}) == list(WORLD_ORDER)
    assert status["P_NE_NP"] is None
    assert status["HASH_ETH"] is None
    assert status["SETH"] is False and status["GAP_ETH"] is False
    assert "ETH" in reasons["SETH"]


def test_exact_count_hypothesis_falsity_forces_eth_falsity_but_not_conversely(data):
    status, _ = propagate(data, {"HASH_ETH": False})
    assert status["ETH"] is False
    assert status["SETH"] is False
    status, _ = propagate(data, {"ETH": False})
    assert status["HASH_ETH"] is None


def test_eth_true_excludes_only_algorithmica(data):
    assert compatible_worlds(data, {"ETH": True}) == list(WORLD_ORDER[1:])
    status, _ = propagate(data, {"ETH": True})
    assert status["P_NE_NP"] is True
    assert status["HASH_ETH"] is True


def test_pke_implies_owf_average_hardness_and_worst_case(data):
    status, _ = propagate(data, {"PKE": True})
    assert all(status[k] is True for k in ("PKE", "OWF", "AVG_HARD", "P_NE_NP"))
    assert status["ETH"] is None


def test_owf_false_excludes_pke_without_forcing_easy_np(data):
    status, _ = propagate(data, {"OWF": False})
    assert status["PKE"] is False
    assert status["AVG_HARD"] is None
    assert status["P_NE_NP"] is None


def test_average_hardness_does_not_prove_one_way_functions(data):
    status, _ = propagate(data, {"AVG_HARD": True})
    assert status["P_NE_NP"] is True
    assert status["OWF"] is None and status["PKE"] is None


def test_algorithmica_forces_all_stronger_hypotheses_false(data):
    status, _ = propagate(data, {"P_NE_NP": False})
    assert all(status[k] is False for k in
               ("ETH", "SETH", "GAP_ETH", "OWF", "PKE", "AVG_HARD"))
    # Fast decision algorithms do not automatically supply fast exact counters.
    assert status["HASH_ETH"] is None


def test_orthogonal_hypothesis_remains_unknown(data):
    status, _ = propagate(data, data["scenarios"]["accept_october_2026_reports"])
    assert status["LWE_HARD"] is None and status["ECDLP_HARD"] is None
    assert status["PKE"] is None


def test_reported_counteralgorithms_invalidate_only_listed_routes(data):
    r = report(data, "accept_october_2026_reports")
    assert r["compatible_worlds"] == list(WORLD_ORDER)
    routes = r["conditional_routes"]
    assert routes["fine_grained_pke_zero_k_clique"]["status"] == "all_listed_routes_invalidated"
    assert routes["fine_grained_pow_3sum"]["status"] == "all_listed_routes_invalidated"
    assert routes["cvp_lower_bound_from_seth"]["status"] == "all_listed_routes_invalidated"
    assert routes["svp_lower_bound_from_gap_eth"]["status"] == "all_listed_routes_invalidated"
    assert routes["lwe_security_assumption"]["status"] == "open"
    assert routes["ecdlp_security_assumption"]["status"] == "open"
    assert r["propositions"]["PKE"] == "unknown"


def test_publications_are_metadata_until_explicit_scenario(data):
    r = report(data)
    assert r["evidence_not_promoted"] == len(data["evidence"])
    assert all(x == "unknown" for x in r["propositions"].values())
    assert all(x["status"] == "open" for x in r["conditional_routes"].values())


def test_independent_routes_not_silently_all_broken(data):
    example = copy.deepcopy(data)
    example["routes"].append({
        "id": "two_routes", "summary": "Independent premises", "premises": [["ETH"], ["LWE_HARD"]]
    })
    status, _ = propagate(example, {"ETH": False})
    assert score_routes(example, status)["two_routes"] == {
        "status": "some_routes_invalidated",
        "alternative_routes": ["invalidated", "open"],
    }
    status, _ = propagate(example, {"ETH": False, "LWE_HARD": True})
    assert score_routes(example, status)["two_routes"]["status"] == "premises_asserted"


@pytest.mark.parametrize("seeds", [
    {"PKE": True, "OWF": False},
    {"ETH": True, "P_NE_NP": False},
    {"HASH_ETH": False, "ETH": True},
    {"SETH": True, "ETH": False},
])
def test_contradictory_claims_fail_closed(data, seeds):
    with pytest.raises(ValueError, match="contradiction"):
        propagate(data, seeds)


def test_dangling_edges_and_missing_provenance_rejected(data):
    broken = copy.deepcopy(data)
    broken["implications"].append(["PKE", "MAGIC"])
    with pytest.raises(ValueError):
        validate_manifest(broken)
    broken = copy.deepcopy(data)
    broken["evidence"][0].pop("scope")
    with pytest.raises(ValueError):
        validate_manifest(broken)


def test_bad_world_and_schema_fail_closed(data):
    bad = copy.deepcopy(data)
    bad["worlds"]["Cryptomania"]["OWF"] = False
    with pytest.raises(ValueError):
        validate_manifest(bad)
    bad = copy.deepcopy(data)
    bad["schema_version"] = "999"
    with pytest.raises(ValueError):
        validate_manifest(bad)


def test_example_exact_bayes_update():
    ex = bayes_example()
    assert ex["algorithmica_multiplier"] == "10"
    assert Q(ex["prior"]["Algorithmica"]) == Q(1, 1000)
    assert Q(ex["posterior"]["Algorithmica"]) == Q(1, 100)
    assert Q(ex["posterior"]["Cryptomania"]) == Q(88, 111)
    assert sum(map(Q, ex["posterior"].values())) == 1


def test_cryptomania_likelihood_varies_with_joint_model():
    prior = {w: Q(1, 5) for w in WORLD_ORDER}
    # ETH false is certain in Algorithmica. Other worlds remain compatible.
    low = {w: Q(1) if w == "Algorithmica" else Q(1, 10) for w in WORLD_ORDER}
    high = dict(low)
    high["Cryptomania"] = Q(9, 10)
    assert bayes_worlds(prior, high)["Cryptomania"] > bayes_worlds(prior, low)["Cryptomania"]


@pytest.mark.parametrize("prior,like", [
    ({w: Q(1, 4) for w in WORLD_ORDER}, {w: Q(1) for w in WORLD_ORDER}),
    ({w: Q(1, 5) for w in WORLD_ORDER}, {w: Q(0) for w in WORLD_ORDER}),
])
def test_bayesian_bad_normalization_or_zero_likelihood(prior, like):
    with pytest.raises(ValueError):
        bayes_worlds(prior, like)


def test_seeded_cnf_exact_count_equivalence_with_connected_negative_controls():
    for blocks in (1, 2, 3, 4, 5):
        for seed in (0, 1, 20261027):
            for linked in (False, True):
                n, clauses = seeded_instance(blocks, seed, linked)
                expected, baseline = exact_count(n, clauses)
                value, work, sizes = factorized_count(n, clauses)
                assert value == expected
                assert baseline == 1 << n
                assert sum(sizes) == n
                assert work <= baseline
                assert (len(sizes) == 1) == (linked or blocks == 1)


def test_zero_and_isolated_variables():
    assert exact_count(0, ()) == (1, 1)
    assert factorized_count(0, ()) == (1, 0, ())
    assert exact_count(4, ((1,),)) == (8, 16)
    assert factorized_count(4, ((1,),)) == (8, 8, (1, 1, 1, 1))


@pytest.mark.parametrize("n, clauses", [
    (3, ((),)), (2, ((3,),)), (2, ((0,),)), (3, ((1, -1),)),
    (3, ((1, 1),)), (21, ()), (-1, ()),
])
def test_bad_cnf_rejected(n, clauses):
    with pytest.raises(ValueError):
        validate_cnf(n, clauses)


def test_benchmark_report_is_repeatable_and_control_rejoins_components():
    first = run_toy_suite()
    assert first == run_toy_suite()
    assert len(first) == 8
    assert all(row["exactly_equal"] for row in first)
    assert all(row["components"] == [row["variables"]] for row in first if row["linked_control"])
    assert all(len(row["components"]) > 1 for row in first if not row["linked_control"])

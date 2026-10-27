"""Adversarial evidence-status tests for the OpenAI ETH crosswalk."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from spiral_ln.proof_fidelity import (
    CLAIM_CONTRACTS, FidelityError, analyze_source_text, git_blob_sha,
    run_audit, validate_claim_contracts, comparator_prelude_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "configs/openai_eth_fidelity.json"


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _sources():
    case = _manifest()
    return {k: (ROOT / spec["path"]).read_text(encoding="utf-8")
            for k, spec in case["sources"].items()}


def test_git_blob_sha_known_vector():
    assert git_blob_sha(b"hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"
    assert git_blob_sha(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_claim_contracts_require_fixed_density_hypothesis():
    claims = _manifest()["claims"]
    validate_claim_contracts(claims)
    broken = copy.deepcopy(claims)
    broken["paper_fixed_density"].pop("condition")
    with pytest.raises(FidelityError, match="fixed-density"):
        validate_claim_contracts(broken)


def test_sharp_manuscript_result_cannot_be_claimed_as_formalized():
    claims = _manifest()["claims"]
    broken = copy.deepcopy(claims)
    broken["paper_tensor_contraction"]["evidence"] = "lean_statement"
    with pytest.raises(FidelityError, match="paper_tensor_contraction"):
        validate_claim_contracts(broken)
    broken = copy.deepcopy(claims)
    broken["lean_exact_count"]["scale"] = "loglog"
    with pytest.raises(FidelityError, match="lean_exact_count"):
        validate_claim_contracts(broken)
    broken = copy.deepcopy(claims)
    broken["lean_exact_count"]["kernel_rebuilt"] = True
    with pytest.raises(FidelityError, match="kernel rebuild"):
        validate_claim_contracts(broken)


def test_claim_ladder_covers_all_evidence_roles():
    assert len(CLAIM_CONTRACTS) == 6
    assert {kind[0] for kind in CLAIM_CONTRACTS.values()} == {
        "title", "lean_statement", "manuscript", "specification"}


def test_pinned_archive_and_statement_audit():
    report = run_audit(ROOT, _manifest())
    assert report["all_passed"]
    assert len(report["checks"]) == 29
    assert report["archived_source_count"] == 10
    assert "elaborated_type_not_checked" in report["comparison_kind"]
    assert "evidence_labels_fail_closed" not in report["checks"]
    assert report["checks"]["comparator_is_admitted_specification"]
    assert report["checks"]["lean_final_contains_no_sorry"]
    assert "no_independent_kernel_build" in report["evidence_status"]


def test_one_changed_byte_is_detected(tmp_path):
    case = _manifest()
    # Mutate one archived source without modifying its independently pinned Git blob.
    role = "lean_scope"
    rel = case["sources"][role]["path"]
    for spec in case["sources"].values():
        source = ROOT / spec["path"]
        destination = tmp_path / spec["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    target = tmp_path / rel
    target.write_bytes(target.read_bytes() + b" ")
    # Verification fails before any mathematical claim is parsed.
    with pytest.raises(FidelityError, match="Git blob differs"):
        run_audit(tmp_path, case)


def test_manuscript_hypothesis_removal_is_detected():
    source = _sources()
    needle = r"m\le Dn"
    assert needle in source["manuscript"]
    source["manuscript"] = source["manuscript"].replace(needle, r"m\le n^2", 1)
    with pytest.raises(FidelityError, match="paper_fixed_density_exponent"):
        analyze_source_text(source)


def test_lean_endpoint_weakening_is_detected():
    source = _sources()
    token = "visitedSpace intermediate"
    assert token in source["lean_final"]
    source["lean_final"] = source["lean_final"].replace(token, "visitedBytes intermediate")
    with pytest.raises(FidelityError, match="lean_exact_count_and_space_statement"):
        analyze_source_text(source)


def test_comparator_sorry_is_distinct_from_actual_proof():
    source = _sources()
    assert analyze_source_text(source)["comparator_is_admitted_specification"]
    source["lean_final"] = source["lean_final"].replace("  exact hrun", "  sorry", 1)
    with pytest.raises(FidelityError, match="lean_endpoint_has_explicit_proof"):
        analyze_source_text(source)


def test_manifest_cannot_rebind_sources_or_commit():
    case = _manifest()
    bad = copy.deepcopy(case)
    bad["upstream_commit"] = "0" * 40
    with pytest.raises(FidelityError, match="upstream revision"):
        run_audit(ROOT, bad)
    bad = copy.deepcopy(case)
    bad["sources"]["lean_final"]["git_blob_sha"] = "0" * 40
    with pytest.raises(FidelityError, match="manifest blob"):
        run_audit(ROOT, bad)
    bad = copy.deepcopy(case)
    bad["sources"]["lean_final"]["upstream_path"] = "lean/something-else.lean"
    with pytest.raises(FidelityError, match="upstream path"):
        run_audit(ROOT, bad)


def test_comparator_type_drift_is_detected():
    sources = _sources()
    token = "visitedSpace intermediate"
    assert token in sources["lean_comparator"]
    sources["lean_comparator"] = sources["lean_comparator"].replace(
        token, "visitedBytes intermediate", 1)
    with pytest.raises(FidelityError, match="comparator_matches_implemented_type"):
        analyze_source_text(sources)


def test_tapered_hermite_valuation_exact_grid():
    from spiral_ln.proof_fidelity import verify_hermite_valuation_grid
    assert verify_hermite_valuation_grid() == 15492


def test_runtime_scale_fidelity_to_actual_upstream_definition():
    sources = _sources()
    assert analyze_source_text(sources)["comparator_runtime_scale_definition"]
    a = copy.deepcopy(sources)
    a["lean_comparator"] = a["lean_comparator"].replace(
        "(Real.log (Real.log ((n : ℝ) + 16))) ^ 2 /",
        "(Real.log (Real.log ((n : ℝ) + 16))) ^ 3 /", 1)
    with pytest.raises(FidelityError, match="comparator_runtime_scale_definition"):
        analyze_source_text(a)
    b = copy.deepcopy(sources)
    b["lean_scale"] = b["lean_scale"].replace(
        "(Real.log (Real.log ((n : ℝ) + 16))) ^ 2 /",
        "(Real.log (Real.log ((n : ℝ) + 16))) ^ 3 /", 1)
    with pytest.raises(FidelityError, match="comparator_runtime_scale_definition"):
        analyze_source_text(b)


def test_count_and_space_definitions_are_part_of_the_evidence():
    sources = _sources()
    changed = copy.deepcopy(sources)
    changed["lean_comparator"] = changed["lean_comparator"].replace(
        "def count (F : CNF V) : ℕ := (satisfyingAssignments F).card",
        "def count (F : CNF V) : ℕ := (satisfyingAssignments F).card + 1", 1)
    with pytest.raises(FidelityError, match="comparator_count_definition"):
        analyze_source_text(changed)
    changed = copy.deepcopy(sources)
    changed["lean_comparator"] = changed["lean_comparator"].replace(
        "∑ i, (c.upper i - c.lower i + 1).toNat",
        "∑ i, (c.upper i - c.lower i + 2).toNat", 1)
    with pytest.raises(FidelityError, match="comparator_space_definition"):
        analyze_source_text(changed)


def test_rho_and_circuits_appendix_scopes_are_inspected():
    sources = _sources()
    assert analyze_source_text(sources)["circuits_appendix_outside_main_proof"]
    changed = copy.deepcopy(sources)
    changed["lean_asymptotics"] = changed["lean_asymptotics"].replace(
        "(Real.logb 2 (Real.logb 2 n)) ^ 2",
        "(Real.logb 2 (Real.logb 2 n)) ^ 3", 1)
    with pytest.raises(FidelityError, match="lean_rho_scale_definition"):
        analyze_source_text(changed)


def test_comparator_prelude_detects_an_unchecked_definition_change():
    source = _sources()
    original = source["lean_comparator"]
    mutated = original.replace("bits.foldr", "bits.foldl", 1)
    assert original != mutated
    source["lean_comparator"] = mutated
    with pytest.raises(FidelityError, match="comparator_definitional_prelude_pinned"):
        analyze_source_text(source)


def test_comparator_prelude_ignores_doc_comment_only_changes():
    source = _sources()
    original = source["lean_comparator"]
    source["lean_comparator"] = original.replace(
        "import Mathlib", "import Mathlib\n/- unrelated documentation note -/", 1)
    assert comparator_prelude_sha256(original) == comparator_prelude_sha256(
        source["lean_comparator"])
    assert analyze_source_text(source)["comparator_definitional_prelude_pinned"]


def test_manuscript_include_closure_rejects_unarchived_input():
    source = _sources()
    assert analyze_source_text(source)["manuscript_input_closure_archived"]
    source["manuscript"] += r"\input{unarchived-extra.tex}" + "\n"
    with pytest.raises(FidelityError, match="manuscript_input_closure_archived"):
        analyze_source_text(source)

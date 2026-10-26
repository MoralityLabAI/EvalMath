"""Adversarial evidence-status tests for the OpenAI ETH crosswalk."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from spiral_ln.proof_fidelity import (
    CLAIM_CONTRACTS, FidelityError, analyze_source_text, git_blob_sha,
    run_audit, validate_claim_contracts,
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
    assert len(report["checks"]) >= 19
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

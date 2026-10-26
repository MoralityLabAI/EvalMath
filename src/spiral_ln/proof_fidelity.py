"""Offline, fail-closed crosswalk for an archived external mathematics claim.

This audits provenance, statements and evidence-level boundaries. It does not
check the mathematics of a LaTeX proof or replay a Lean kernel build.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


class FidelityError(ValueError):
    """A source, statement, or evidence contract changed unexpectedly."""


# These are independent of the JSON under review. A reader cannot promote a
# manuscript-only claim by changing the manifest's evidence labels.
CLAIM_CONTRACTS = {
    "headline": ("title", "none", "eth_false"),
    "lean_exact_count": ("lean_statement", "loglog_squared", "exact_count_polyspace"),
    "paper_general_bound": ("manuscript", "loglog", "exact_count_polyspace"),
    "paper_fixed_density": ("manuscript", "sqrtlog", "exact_count_polyspace"),
    "paper_tensor_contraction": ("manuscript", "sqrtlog", "tensor_contraction"),
    "comparator_specification": ("specification", "loglog_squared", "exact_count_polyspace"),
}

REQUIRED_SOURCES = {
    "manuscript", "tensor_reduction", "tensor_contraction",
    "lean_final", "lean_comparator", "lean_config", "lean_scope",
}


def git_blob_sha(data: bytes) -> str:
    """Return Git's SHA-1 for a raw blob, including its binary size header."""
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise FidelityError(message)


def _section(source: str, left: str, right: str) -> str:
    begin = source.find(left)
    _require(begin != -1, f"missing boundary: {left!r}")
    end = source.find(right, begin + len(left))
    _require(end != -1, f"missing closing boundary: {right!r}")
    return source[begin:end]


def _contains(source: str, *tokens: str) -> bool:
    return all(token in source for token in tokens)


def validate_claim_contracts(claims: dict[str, Any]) -> None:
    """Reject evidence promotion or a missing width/density boundary."""
    _require(set(claims) == set(CLAIM_CONTRACTS), "claim IDs changed")
    for claim_id, expected in CLAIM_CONTRACTS.items():
        claim = claims[claim_id]
        actual = (claim.get("evidence"), claim.get("scale"), claim.get("subject"))
        _require(actual == expected, f"claim {claim_id}: expected {expected}, got {actual}")
    _require(claims["paper_fixed_density"].get("condition") == "m <= D*n; D fixed",
             "fixed-density bound lost its hypothesis")
    _require(claims["lean_exact_count"].get("scope") == "fixed k>=2; normalized finite-set CNF",
             "Lean input normalization/scope changed")
    _require(claims["paper_general_bound"].get("scope") == "fixed k>=2; arbitrary clauses",
             "manuscript general scope changed")
    _require(claims["lean_exact_count"].get("kernel_rebuilt") is False,
             "source inspection must not be promoted to an independent Lean kernel rebuild")
    _require(claims["paper_tensor_contraction"].get("formalized_in_case") is False,
             "tensor contraction is not proved by the cited Lean endpoint")


def analyze_source_text(sources: dict[str, str]) -> dict[str, bool]:
    """Check actual theorem text and trace its hypotheses across evidence layers."""
    checks: dict[str, bool] = {}
    paper = sources["manuscript"]
    main = _section(paper, r"\begin{theorem}\label{thm:main}", r"\end{theorem}")
    checks["paper_title"] = r"\title{The Exponential Time Hypothesis is False}" in paper
    checks["paper_main_exact_count"] = _contains(main, r"computes $\#F$", r"k\ge2", r"n\ge20")
    checks["paper_general_exponent"] = r"n\log\log n/\sqrt{\log n}" in main
    checks["paper_fixed_density_exponent"] = _contains(
        main, r"m\le Dn", r"n/\sqrt{\log n}")
    checks["paper_weaker_exponent_visible"] = (
        r"\rho(n)=\frac{n(\log\log n)^2}{\sqrt{\log n}}" in paper)

    red = sources["tensor_reduction"]
    tensor = _section(red, r"\begin{theorem}[Boolean tensor contraction]", r"\end{theorem}")
    checks["tensor_network_hypotheses"] = _contains(
        tensor, "bipartite tensor network", r"s^{9/10}", "computed from the description")
    checks["tensor_network_exponent"] = r"2^{O(s/\sqrt{\log s})}" in tensor
    checks["tensor_density_reduction"] = _contains(
        red, r"m\le Dn", "Proof of the fixed-density bound", "parity tests")
    checks["tensor_recursive_precision_lemma"] = _contains(
        sources["tensor_contraction"],
        r"\begin{lemma}[Tapered Hermite recovery]", r"\label{lem:tapered-hermite}",
        r"\begin{proof}[Proof of Theorem~\ref{thm:tensor-contraction}]")

    final = sources["lean_final"]
    endpoint = _section(final, "theorem exact_count_and_sat ", "theorem exact_count_eth ")
    checks["lean_exact_count_and_space_statement"] = _contains(
        endpoint, "SAT.count F", "Computation.Trace", "visitedSpace intermediate",
        "SqrtLog.Statement.runtimeBound", "countWord (SAT.count F)")
    checks["lean_endpoint_has_explicit_proof"] = _contains(
        endpoint, ":= by", "compiled_exact_count_and_sat k hk", "exact hrun")
    checks["lean_final_contains_no_sorry"] = re.search(r"\b(?:sorry|admit)\b", final) is None
    checks["lean_declared_axiom_inspection"] = (
        "#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat" in final)
    checks["lean_rho_theorem_separate"] = _contains(
        final, "theorem exact_count_eth ", "A * rho n", "F.card")

    comparator = sources["lean_comparator"]
    specification = _section(comparator, "theorem exact_count_and_sat ",
                             "end OAI.Algorithms.SubexponentialSAT.SqrtLogSpace")
    checks["comparator_is_admitted_specification"] = re.search(
        r":=\s*by\s+sorry\b", specification) is not None
    config = json.loads(sources["lean_config"])
    checks["comparator_points_to_endpoint"] = (
        config.get("solution_module") == "OAI.Algorithms.SubexponentialSAT.Main" and
        config.get("theorem_names") ==
        ["OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat"])
    checks["comparator_permitted_axioms"] = (
        set(config.get("permitted_axioms", [])) ==
        {"propext", "Quot.sound", "Classical.choice"})
    doc = sources["lean_scope"]
    checks["scope_document_admits_weaker_lean"] = _contains(
        doc, "Lean proves", r"(\log\log n)^2", "manuscript gives the sharper",
        r"m\le Dn")
    for name, valid in checks.items():
        _require(valid, f"source evidence check failed: {name}")
    return checks


def run_audit(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate frozen source bytes, inspect statements, and enforce fidelity labels."""
    _require(manifest.get("schema_version") == "0.1", "unsupported manifest schema")
    _require(manifest.get("upstream_repo") == "openai/math", "wrong upstream repository")
    commit = manifest.get("upstream_commit", "")
    _require(bool(re.fullmatch(r"[a-f0-9]{40}", commit)), "un-pinned upstream revision")
    _require(set(manifest.get("sources", {})) == REQUIRED_SOURCES, "missing or extra source roles")
    validate_claim_contracts(manifest.get("claims", {}))
    sources: dict[str, str] = {}
    pins: dict[str, str] = {}
    for role, spec in sorted(manifest["sources"].items()):
        rel = spec.get("path", "")
        _require(rel.startswith("fixtures/external/openai_eth_20261025/") and
                 ".." not in Path(rel).parts, f"source {role}: unsafe fixture path")
        path = root / rel
        _require(path.is_file(), f"source {role}: missing archived blob: {rel}")
        contents = path.read_bytes()
        digest = git_blob_sha(contents)
        _require(digest == spec.get("git_blob_sha"),
                 f"source {role}: Git blob differs from pinned upstream")
        _require(spec.get("upstream_path", "").startswith(("preprints/", "lean/")),
                 f"source {role}: missing upstream path")
        sources[role] = contents.decode("utf-8")
        pins[role] = digest
    checks = analyze_source_text(sources)
    checks["seven_git_blob_pins"] = len(pins) == 7
    checks["evidence_labels_fail_closed"] = True  # validate_claim_contracts raised on mismatch
    checks["three_exponents_have_strict_audit_order"] = (
        manifest["claims"]["paper_fixed_density"]["scale"] == "sqrtlog" and
        manifest["claims"]["paper_general_bound"]["scale"] == "loglog" and
        manifest["claims"]["lean_exact_count"]["scale"] == "loglog_squared")
    return {
        "upstream_repo": manifest["upstream_repo"],
        "upstream_commit": commit,
        "evidence_status": "pinned_source_structural_audit; no_independent_kernel_build",
        "claim_crosswalk": manifest["claims"],
        "source_git_blob_sha": pins,
        "checks": checks,
        "all_passed": all(checks.values()),
        "open_obligations": [
            "rebuild the entire upstream Lean import closure and inspect #print axioms output",
            "independently audit tensor packing, 2-adic Hermite precision, and recursion cost",
            "check manuscript-to-formal input normalization and explicit algorithmic correspondence",
        ],
    }

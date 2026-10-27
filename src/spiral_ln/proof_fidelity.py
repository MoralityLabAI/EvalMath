"""Offline, fail-closed crosswalk for an archived external mathematics claim.

This audits provenance, statements and evidence-level boundaries. It does not
check the mathematics of a LaTeX proof or replay a Lean kernel build.
"""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
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

FROZEN_UPSTREAM_COMMIT = "7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a"
FROZEN_SOURCE_BLOBS = {
    "manuscript": ("preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex", "f7af85e623b58e0ca9f4b9416916d442defa963a"),
    "tensor_reduction": ("preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/quantitative-reduction.tex", "80389ac39d987133b71b2ddc2593e6fcdd99871a"),
    "tensor_contraction": ("preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/quantitative-contraction.tex", "51ba54efc29f51bbc0426f848003030da484f354"),
    "lean_final": ("lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean", "a69635a2492e06a26f2e33d4251edd1e21ba3332"),
    "lean_comparator": ("lean/ComparatorChallenges/SubexponentialSAT.lean", "a8d5ff3a3e80323675b1f2d1ea611560b783e9ca"),
    "lean_config": ("lean/ComparatorChallenges/SubexponentialSAT.json", "d4cc9e7074e900c1aa6371151cfd234c121a0b82"),
    "lean_scope": ("lean/docs/378.md", "223bbe187394bffca8a2c7ba1656538bfba26e3b"),
    "lean_scale": ("lean/OAI/Algorithms/SubexponentialSAT/SqrtLog/StatementScale.lean", "dae009c0b234a6180e61a897d56a5721f397762d"),
    "lean_asymptotics": ("lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Asymptotics.lean", "da9003ffd1a9b8fcc82147b4152414b264d26d54"),
    "circuits_appendix": ("preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/quantitative-circuits.tex", "e25def5eb03ee53feefd3fe480dd5a1293761fae"),
}
REQUIRED_SOURCES = set(FROZEN_SOURCE_BLOBS)

FROZEN_COMPARATOR_PRELUDE_SHA256 = "d9e3df547e4842138e46bc97e5e6939ea5d3b8e05d3636b272bc4d3580b5a834"



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


def comparator_prelude_sha256(comparator: str) -> str:
    """Comment-insensitive fingerprint of the comparator definitional prelude."""
    marker = "theorem exact_count_and_sat "
    _require(marker in comparator, "missing comparator theorem")
    prelude = comparator.split(marker, 1)[0]
    unblocked = re.sub(r"/-.*?-/", "", prelude, flags=re.DOTALL)
    uncommented = re.sub(r"--[^\n]*", "", unblocked)
    return hashlib.sha256(" ".join(uncommented.split()).encode("utf-8")).hexdigest()


def manuscript_input_targets(manuscript: str) -> list[str]:
    """Return the TeX input targets."""
    return re.findall(r"\\input\{([^}]+)\}", manuscript)


def _lean_endpoint_signature(source: str) -> str:
    """Compare exact printed proposition syntax, independent of whitespace."""
    return "".join(_section(source, "theorem exact_count_and_sat ", ":= by").split())



def _lean_def(source: str, name: str) -> str:
    """Normalize one *printed* Lean definition, without elaborating any names.

    The upstream comparator is self-contained and defines identifiers which are
    resolved in a different environment from the implementation. This catches
    textual and body drift, while leaving elaborated equivalence to Lean.
    """
    pattern = r"(?m)^(?:noncomputable )?def " + re.escape(name) + r"\b[^\n]*(?:\n(?!\n)[^\n]*)*"
    match = re.search(pattern, source)
    _require(match is not None, f"missing Lean definition {name!r}")
    return "".join(re.sub(r"^noncomputable ", "", match.group(0)).split())


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

    stems = {Path(path).stem for path, _ in FROZEN_SOURCE_BLOBS.values()}
    includes = manuscript_input_targets(paper)
    checks["manuscript_input_closure_archived"] = (
        len(includes) == 3 and all(Path(target).stem in stems for target in includes))

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
    checks["comparator_matches_implemented_type"] = (
        _lean_endpoint_signature(comparator) == _lean_endpoint_signature(final))
    checks["comparator_runtime_scale_definition"] = (
        _lean_def(comparator, "runtimeScale") == _lean_def(sources["lean_scale"], "runtimeScale") and
        "Real.log(Real.log((n:ℝ)+16))" in _lean_def(comparator, "runtimeScale") and
        "Real.sqrt(Real.log((n:ℝ)+16))" in _lean_def(comparator, "runtimeScale"))
    checks["comparator_runtime_bound_definition"] = (
        _lean_def(comparator, "runtimeBound") == _lean_def(sources["lean_scale"], "runtimeBound") and
        "(exponentConstant*runtimeScalenumVars)" in _lean_def(comparator, "runtimeBound"))
    checks["comparator_count_definition"] = (
        _lean_def(comparator, "count") == "defcount(F:CNFV):ℕ:=(satisfyingAssignmentsF).card" and
        _lean_def(comparator, "satisfyingAssignments") == "defsatisfyingAssignments(F:CNFV):Finset(AssignmentV):=Finset.univ.filterfuna=>F.evala=true" and
        _lean_def(comparator, "CNF.eval") == "defCNF.eval(a:AssignmentV)(F:CNFV):Bool:=decide(∀C∈F,C.evala=true)")
    checks["comparator_encoding_definition"] = (
        _lean_def(comparator, "encodeCNF") == "defencodeCNF{n:ℕ}(F:SAT.CNF(Finn)):ListBool:=encodeNatn++encodeCNFBodyF" and
        _lean_def(comparator, "formulaBitLength") == "defformulaBitLength{n:ℕ}(F:SAT.CNF(Finn)):ℕ:=(encodeCNFF).length" and
        _contains(comparator, "def encodeNat (n : ℕ) : List Bool := List.replicate n true ++ [false]",
                  "def cnfNumbers {n : ℕ}", "def encodeCNFBody {n : ℕ}"))
    checks["comparator_space_definition"] = (
        _lean_def(comparator, "visitedSpace") == "defvisitedSpace{machine:PrimitiveMachine}(c:LocatedCfgmachine):ℕ:=∑i,(c.upperi-c.loweri+1).toNat" and
        _contains(comparator, "def locatedStep (machine : PrimitiveMachine)"))
    checks["lean_rho_scale_definition"] = _contains(
        sources["lean_asymptotics"],
        "noncomputable def rho (n : ℕ) : ℝ :=",
        "(n : ℝ) * (Real.logb 2 (Real.logb 2 n)) ^ 2 / Real.sqrt (Real.logb 2 n)")
    checks["circuits_appendix_outside_main_proof"] = _contains(
        sources["circuits_appendix"],
        r"\begin{proof}[Proof of Corollary~\ref{cor:quantitative-circuits}]",
        r"\end{proof}") and r"\label{thm:main}" not in sources["circuits_appendix"]
    checks["comparator_definitional_prelude_pinned"] = (
        comparator_prelude_sha256(comparator) == FROZEN_COMPARATOR_PRELUDE_SHA256)
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


def verify_hermite_valuation_grid(max_a: int = 7) -> int:
    """Finite, exact probe of the manuscript's tapered-Hermite v2 identity.

    Uses the *signed* residue grid S = [-2^a, ..., 2^a-1]. For each
    1 <= u <= a, u <= M <= u+5 and node t with q_t > 0, computes
    v2(E_t(0)) directly as a sum over nodes, and independently via
    the manuscript's grouped-valuation expression. No symbolic proof.
    """
    def valuation(value: int) -> int:
        value = abs(value)
        _require(value > 0, "2-adic valuation of zero")
        return (value & -value).bit_length() - 1

    total = 0
    for a in range(1, max_a + 1):
        L = 1 << a
        S = range(-L, L)
        for u in range(1, a + 1):
            for M in range(u, u + 6):
                h = (3 * M + u - 1) // u
                q = lambda i: h * max(0, u - i)
                for t in S:
                    if t == 0 or valuation(t) >= u:
                        continue
                    i, D = valuation(t), L >> valuation(t)
                    direct = sum(q(valuation(z)) * (valuation(z) - valuation(t-z))
                                 for z in S if z != 0 and z != t)
                    grouped = sum((Fraction(D * j, 1 << j) * (q(i+j) - q(i))
                                   for j in range(1, a-i+1)), Fraction(0))
                    _require(direct == grouped, f"Hermite valuation identity failed: {(a,u,M,t)}")
                    _require(direct >= -6 * D * h, f"Hermite loss bound failed: {(a,u,M,t)}")
                    total += 1
    return total


def run_audit(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate frozen source bytes, inspect statements, and enforce fidelity labels."""
    _require(manifest.get("schema_version") == "0.2", "unsupported manifest schema")
    _require(manifest.get("upstream_repo") == "openai/math", "wrong upstream repository")
    commit = manifest.get("upstream_commit", "")
    _require(commit == FROZEN_UPSTREAM_COMMIT, "upstream revision differs from frozen commit")
    _require(set(manifest.get("sources", {})) == REQUIRED_SOURCES, "missing or extra source roles")
    validate_claim_contracts(manifest.get("claims", {}))
    for role, spec in manifest["sources"].items():
        expected_path, expected_sha = FROZEN_SOURCE_BLOBS[role]
        _require(spec.get("upstream_path") == expected_path,
                 f"source {role}: upstream path differs from frozen source")
        _require(spec.get("git_blob_sha") == expected_sha,
                 f"source {role}: manifest blob differs from frozen source")
    sources: dict[str, str] = {}
    pins: dict[str, str] = {}
    for role, spec in sorted(manifest["sources"].items()):
        rel = spec.get("path", "")
        _require(rel.startswith("fixtures/external/openai_eth_20261025/") and
                 ".." not in Path(rel).parts, f"source {role}: unsafe fixture path")
        expected_path, expected_sha = FROZEN_SOURCE_BLOBS[role]
        path = root / rel
        _require(path.is_file(), f"source {role}: missing archived blob: {rel}")
        contents = path.read_bytes()
        digest = git_blob_sha(contents)
        _require(digest == expected_sha,
                 f"source {role}: Git blob differs from pinned upstream")
        sources[role] = contents.decode("utf-8")
        pins[role] = digest
    checks = analyze_source_text(sources)
    hermite_cases = verify_hermite_valuation_grid()
    checks["hermite_valuation_finite_grid"] = hermite_cases == 15492
    return {
        "upstream_repo": manifest["upstream_repo"],
        "upstream_commit": commit,
        "evidence_status": "pinned_source_structural_audit; no_independent_kernel_build",
        "claim_crosswalk": manifest["claims"],
        "source_git_blob_sha": pins,
        "archived_source_count": len(pins),
        "comparison_kind": "syntactic_statement_and_printed_definition_text; elaborated_type_not_checked",
        "checks": checks,
        "all_passed": all(checks.values()),
        "finite_probes": {"hermite_valuation_cases": hermite_cases,
                          "grid": "1<=a<=7; 1<=u<=a; u<=M<=u+5; q_t>0",
                          "evidence": "finite_verified_example"},
        "open_obligations": [
            "rebuild the entire upstream Lean import closure and inspect #print axioms output",
            "independently audit tensor packing, 2-adic Hermite precision, and recursion cost",
            "check manuscript-to-formal input normalization and explicit algorithmic correspondence",
            "compare fully elaborated comparator and implementation definitions via upstream Lean mechanism",
        ],
    }

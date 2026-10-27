"""Read-only audit of a pinned upstream Unique Games statement contract.

Checks source bytes and syntactic contract fields. This is not Lean
elaboration, kernel verification, or a transitive-dependency audit.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
MODEL = "lean/OAI/Computability/UniqueGames/Model.lean"
THEOREM = "lean/OAI/Computability/UniqueGames/Theorem.lean"
MAIN = "lean/OAI/Computability/UniqueGames/Main.lean"
CHALLENGE = "lean/ComparatorChallenges/UniqueGamesTheorem.lean"
CONFIG = "lean/ComparatorChallenges/UniqueGamesTheorem.json"

SIGNATURES = {
    "binary_3sat_language": r"def language \(input : List Bool\) : Prop :=\s*∃ formula, BinaryEncoding\.decodeFormula input = some formula ∧ formula\.Satisfiable",
    "permutation_forward_inverse": r"structure PermutationTable \(alphabet : Nat\) where\s*images : Vector \(Fin alphabet\) alphabet\s*inverseImages : Vector \(Fin alphabet\) alphabet\s*leftInverse : ∀ label : Fin alphabet, inverseImages\[images\[label\]\] = label\s*rightInverse : ∀ label : Fin alphabet, images\[inverseImages\[label\]\] = label",
    "nonempty_game": r"nonempty : constraints ≠ \[\]",
    "simple_bipartite": r"simpleBipartite : ∀ input, SimpleBipartite \(construct input\)",
    "no_parallel_edges": r"endpoints_injective : Function\.Injective",
    "fixed_alphabet": r"structure BinaryGapReduction \(ε δ : ℝ\) where\s*alphabet : Nat\s*alphabetAtLeastTwo : 2 ≤ alphabet",
    "f2_coordinates": r"coordinates : Fin alphabet ≃ Integration\.BinaryLinear\.Vector dimension",
    "translation_constraints": r"translations : ∀ input,\s*Integration\.TranslationTarget\.IsTranslationInstance coordinates \(construct input\)",
    "polynomial_time": r"computation : Turing\.TM2ComputableInPolyTime \(id : List Bool → List Bool\)\s*Complexity\.gameBits construct",
    "finite_tape_alphabet": r"finiteAlphabet : Complexity\.MachineFiniteAlphabet\.FiniteAlphabet computation\.tm",
    "completeness_exists": r"completeness : ∀ input, BinaryLanguage\.language input →\s*∃ labeling, 1 - ε ≤",
    "soundness_forall": r"soundness : ∀ input, ¬BinaryLanguage\.language input →\s*∀ labeling, \(countSatisfied labeling",
}



def source_without_noncode(source: str) -> str:
    """Mask Lean line comments, nested block comments, and quoted strings.

    This is lexical defense against signature spoofing in comments/strings,
    not a substitute for parsing, elaboration, or semantic verification.
    """
    output: list[str] = []
    index = 0
    depth = 0
    quoted = False

    def mask(text: str) -> None:
        output.extend("\n" if char == "\n" else " " for char in text)

    while index < len(source):
        if depth:
            if source.startswith("/-", index):
                depth += 1
                mask(source[index:index + 2])
                index += 2
            elif source.startswith("-/", index):
                depth -= 1
                mask(source[index:index + 2])
                index += 2
            else:
                mask(source[index])
                index += 1
            continue
        if quoted:
            if source[index] == "\\" and index + 1 < len(source):
                mask(source[index:index + 2])
                index += 2
            elif source[index] == '"':
                mask('"')
                quoted = False
                index += 1
            else:
                mask(source[index])
                index += 1
            continue
        if source.startswith("--", index):
            end = source.find("\n", index)
            if end < 0:
                end = len(source)
            mask(source[index:end])
            index = end
            continue
        if source.startswith("/-", index):
            depth = 1
            mask(source[index:index + 2])
            index += 2
            continue
        if source[index] == '"':
            quoted = True
            mask(source[index])
            index += 1
            continue
        output.append(source[index])
        index += 1
    if depth or quoted:
        raise ValueError("unterminated Lean comment or string in pinned source")
    return "".join(output)


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()



def theorem_head(source: str) -> str:
    """Normalized theorem11 declaration, excluding the proof expression.

    A textual comparison between two Lean files is an executable consistency
    guard. It does not establish kernel-level or semantic equivalence.
    """
    code = source_without_noncode(source)
    match = re.search(r"\btheorem\s+theorem11\s*\(", code)
    if match is None:
        raise ValueError("missing theorem11 declaration")
    proof_start = code.find(":=", match.start())
    if proof_start < 0:
        raise ValueError("theorem11 declaration has no proof separator")
    return re.sub(r"\s+", "", code[match.start():proof_start])


def check_model(text: str) -> dict[str, bool]:
    code = source_without_noncode(text)
    return {name: re.search(pattern, code) is not None
            for name, pattern in SIGNATURES.items()}


def audit(sources: dict[str, bytes], pin: dict) -> dict:
    for path, expected in pin["sources"].items():
        if path not in sources:
            raise ValueError(f"missing pinned source: {path}")
        actual = blob_sha(sources[path])
        if actual != expected:
            raise ValueError(f"blob mismatch for {path}: expected {expected}, found {actual}")
    model = sources[MODEL].decode("utf-8")
    challenge_full = sources[CHALLENGE].decode("utf-8")
    theorem_full = sources[THEOREM].decode("utf-8")
    # The comparator duplicates the model declarations and adds theorem11.
    suffix = "end OAI\n"
    if not model.endswith(suffix):
        raise ValueError("actual Model.lean has an unexpected terminal namespace")
    if not challenge_full.startswith(model[:-len(suffix)]):
        raise ValueError("comparator's copied model differs byte-for-byte from actual Model.lean")
    if theorem_head(challenge_full) != theorem_head(theorem_full):
        raise ValueError("comparator theorem11 statement differs from implemented theorem11")
    checks = check_model(model)
    if not all(checks.values()):
        raise ValueError(f"model signature failures: {[k for k, v in checks.items() if not v]}")
    theorem = source_without_noncode(sources[THEOREM].decode("utf-8"))
    challenge = source_without_noncode(sources[CHALLENGE].decode("utf-8"))
    main = source_without_noncode(sources[MAIN].decode("utf-8"))
    config = json.loads(sources[CONFIG])
    if "theorem theorem11 (ε δ : ℝ)" not in theorem:
        raise ValueError("missing actual theorem11 declaration")
    if "Theorem.exists_binaryGapReduction ε δ hε hεhalf hδ hδhalf" not in theorem:
        raise ValueError("missing actual theorem11 construction reference")
    if re.search(r"\b(sorry|admit)\b", theorem):
        raise ValueError("unexpected placeholder in actual theorem source")
    if not re.search(r"\b(sorry|admit)\b", challenge):
        raise ValueError("challenge template no longer has the expected placeholder")
    if not re.search(r"(?m)^\s*import OAI\.Computability\.UniqueGames\.Theorem\s*$", main):
        raise ValueError("solution entry module missing theorem import")
    if config["theorem_names"] != [pin["expected_theorem"]]:
        raise ValueError("comparator theorem name changed")
    if config["solution_module"] != pin["expected_solution_module"]:
        raise ValueError("comparator solution changed")
    if sorted(config["permitted_axioms"]) != sorted(["propext", "Quot.sound", "Classical.choice"]):
        raise ValueError("comparator permitted axioms changed")
    return {"pinned_commit": pin["commit"], "blob_sha_verified": len(sources),
            "comparator_model_byte_equal": True,
            "implemented_theorem_head_equal": True,
            "contract_signatures_passed": sorted(checks),
            "solution_theorem_source_no_placeholder": True,
            "challenge_template_placeholder_expected": True,
            "scope": "text and hash audit only; independent Lean compilation outstanding"}


def main():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fetch", action="store_true", help="fetch files at pinned GitHub commit")
    source.add_argument("--snapshot", type=Path, help="directory containing pinned source paths")
    args = parser.parse_args()
    pin = json.loads((ROOT / "upstream_pin.json").read_text(encoding="utf-8"))
    content = {}
    for path in pin["sources"]:
        if args.fetch:
            url = f'https://raw.githubusercontent.com/{pin["repository"]}/{pin["commit"]}/{path}'
            with urlopen(url, timeout=30) as response:
                raw = response.read()
        else:
            raw = (args.snapshot / path).read_bytes()
        content[path] = raw
    print(json.dumps(audit(content, pin), indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

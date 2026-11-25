"""Export and replay the bounded native candidate pack for the RH curriculum."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import shlex

from spiral_ln.rh_compactification_gym import (
    ALLOWED_AXIOMS, BASE, FAMILY, LEAN_SOURCE, ROOT, LeanChecker,
    check_proof_surface, json_text, read_jsonl, sha256, write_jsonl,
)

PACK = BASE / "pack"
PACK_SCHEMA = "datagoblin.checked-candidate-pack.v1"


def epoch_for(row: dict, environment: dict) -> str:
    return "rhcg_" + sha256(json_text({"id": row["id"], "environment": environment,
        "template": row["source_template_sha256"], "statement": row["statement"],
        "context": row["context"]}))


def micro_module():
    path = BASE / "microsteps.py"
    spec = importlib.util.spec_from_file_location("rhcg_microsteps", path)
    if spec is None or spec.loader is None:
        raise ValueError("microstep generator missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def micro_rows() -> tuple[dict, object]:
    module = micro_module()
    data = json.loads((BASE / "microsteps.json").read_text(encoding="utf-8"))
    if (data["module_source_sha256"] != sha256(LEAN_SOURCE.read_bytes())
            or data["generator_source_sha256"] != sha256((BASE / "microsteps.py").read_bytes())):
        raise ValueError("microstep source hash mismatch")
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    if len(data["rows"]) != len(module.SPECS):
        raise ValueError("microstep specification count mismatch")
    for row, spec in zip(data["rows"], module.SPECS, strict=True):
        path = (ROOT / row["source_template_path"]).resolve()
        if not path.is_relative_to(BASE.resolve()):
            raise ValueError("microstep source path escapes the curriculum")
        template = path.read_text(encoding="utf-8")
        if template != module.build_template(spec, source) or sha256(template) != row["source_template_sha256"]:
            raise ValueError("microstep template differs from its source-derived declaration")
        if row["target_theorem"] != module.NAMESPACE + "." + spec["target"]:
            raise ValueError("microstep target mismatch")
        if (row["id"] != "rh_micro_" + spec["target"] or row["stage"] != spec["stage"]
                or row["statement"] != module.STATEMENT
                or row["retrieved"] != {"compose": [module.NAMESPACE + "." + name for name in spec["retrieved"]]}):
            raise ValueError("microstep public specification drift")
        if len(module.model_input(row["statement"], row["context"]).encode("utf-8")) > 384:
            raise ValueError("microstep goal would be truncated")
        if [candidate["text"] for candidate in row["candidates"]] != [spec["gold"], spec["wrong"]]:
            raise ValueError("microstep candidates differ from generator")
        if [candidate.get("expected_accept") for candidate in row["candidates"]] != [True, False]:
            raise ValueError("microstep acceptance expectations differ from the generator")
        if row["candidates"][0].get("lean_returncode") != 0 or row["candidates"][1].get("lean_returncode") != 1:
            raise ValueError("microstep original compiler results differ")
        for candidate in row["candidates"]:
            filled = module.fill_template(template, candidate["text"])
            if candidate["full_source_sha256"] != sha256(filled):
                raise ValueError("microstep original closure source mismatch")
    return data, module


def complete_source(module, template: str, tactic: str, target: str) -> str:
    return module.fill_template(template, tactic).rstrip() + f"\n\n#print axioms {target}\n"


def assert_context(checker: LeanChecker, module, row: dict, template: str) -> None:
    traced = checker.compile_source(complete_source(module, template,
                    "trace_state\n" + row["candidates"][0]["text"], row["target_theorem"]), row["target_theorem"])
    if traced["label"] != 1:
        raise ValueError("trace harness did not close: " + row["id"])
    output = traced["diagnostic"]
    output = re.sub(r"'" + re.escape(row["target_theorem"]) + r"' depends on axioms: \[[^\]]*\]", "", output, flags=re.S)
    output = re.sub(r"'" + re.escape(row["target_theorem"]) + r"' does not depend on any axioms", "", output)
    if output.strip() != row["context"]:
        raise ValueError("native local goal differs from the bounded public context: " + row["id"])


def build_pack(checker: LeanChecker, destination: Path = PACK) -> dict:
    data, module = micro_rows()
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "sources").mkdir(exist_ok=True)
    public, private, files = [], [], {}
    for row in data["rows"]:
        template = (ROOT / row["source_template_path"]).read_text(encoding="utf-8")
        assert_context(checker, module, row, template)
        relative = "sources/" + row["id"] + ".lean.in"
        (destination / relative).write_text(template, encoding="utf-8")
        files[relative] = sha256(template)
        epoch = epoch_for(row, checker.environment)
        candidates, outcomes = [], {}
        for candidate in row["candidates"]:
            tactic = candidate["text"]
            check_proof_surface({"unavailable_declarations": [row["target_theorem"].split(".")[-1]]}, tactic)
            if len(tactic.encode("utf-8")) > 384:
                raise ValueError("candidate exceeds the pinned encoder budget")
            # IDs and position contain no gold/wrong flags; ordering uses text alone.
            identifier = "c_" + sha256(epoch + "\0" + tactic)[:20]
            source = complete_source(module, template, tactic, row["target_theorem"])
            result = checker.compile_source(source, row["target_theorem"])
            if result["label"] != int(candidate["expected_accept"]):
                raise ValueError("candidate expectation failed under native axiom audit: " + row["id"])
            result.pop("seconds", None)
            outcomes[identifier] = result
            candidates.append({"id": identifier, "action": "lean_tactic", "tactic": tactic})
        candidates.sort(key=lambda candidate: candidate["id"])
        public.append({
            "id": row["id"], "lineage": FAMILY, "family": FAMILY, "epoch": epoch,
            "task": "lean_candidate_proof", "statement": row["statement"], "context": row["context"],
            "candidates": candidates, "orders": {"compose": [c["id"] for c in candidates]},
            "retrieved": row["retrieved"], "stage": row["stage"],
            "source_harness": {"path": relative, "sha256": files[relative],
                               "target": row["target_theorem"], "placeholder": module.PLACEHOLDER},
        })
        private.append({"id": row["id"], "epoch": epoch, "outcomes": outcomes,
                        "native": {"backend": checker.environment["backend"], "full_theorem_closed": True,
                                   "local_context_replayed": True}, "retrieval_comparisons": []})
    write_jsonl(destination / "train.jsonl", public)
    write_jsonl(destination / "train.receipts.jsonl", private)
    manifest = {
        "schema": PACK_SCHEMA,
        "splits": {"train": {"goals": len(public), "lineages": 1,
            "public": "train.jsonl", "public_sha256": sha256((destination / "train.jsonl").read_bytes()),
            "receipts": "train.receipts.jsonl", "receipts_sha256": sha256((destination / "train.receipts.jsonl").read_bytes())}},
        "environment": checker.environment, "source_evidence_sha256": sha256((BASE / "microsteps.json").read_bytes()),
        "source_files_sha256": files, "scope": "public training/development; one shared recurrence family",
        "native_processes_for_export": len(public) * 3,
        "independent_families": 1, "confirmation": {"status": "unallocated", "scored": False},
        "input_cap_utf8_bytes": 384, "candidate_cap_utf8_bytes": 384,
        "scientific_eligible": False, "training_eligible": True,
    }
    (destination / "manifest.json").write_text(json_text(manifest), encoding="utf-8")
    return manifest


def load_pack(pack: Path = PACK) -> tuple[dict, list[dict], list[dict]]:
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("schema") != PACK_SCHEMA or set(manifest.get("splits", {})) != {"train"}
            or manifest.get("independent_families") != 1 or manifest.get("scientific_eligible") is not False):
        raise ValueError("pack must preserve training-only scientific scope")
    if manifest["source_evidence_sha256"] != sha256((BASE / "microsteps.json").read_bytes()):
        raise ValueError("pack microstep evidence differs")
    if manifest.get("environment", {}).get("checker_sha256") != sha256((ROOT / "src/spiral_ln/rh_compactification_gym.py").read_bytes()):
        raise ValueError("pack checker source differs from this checkout")
    data, module = micro_rows()
    known = {row["id"]: row for row in data["rows"]}
    entry = manifest["splits"]["train"]
    for key in ("public", "receipts"):
        filename = entry[key]
        if filename != Path(filename).name or sha256((pack / filename).read_bytes()) != entry[key + "_sha256"]:
            raise ValueError("pack data hash or basename mismatch")
    public, private = read_jsonl(pack / entry["public"]), read_jsonl(pack / entry["receipts"])
    if len(public) != len(private) or len(public) != entry["goals"] or len(public) != len(known):
        raise ValueError("pack row count mismatch")
    seen = set()
    for row, receipt in zip(public, private, strict=True):
        identity = row["id"]
        if identity in seen or identity not in known:
            raise ValueError("duplicate or unknown microstep")
        seen.add(identity)
        original = known[identity]
        if (identity != receipt["id"] or row["epoch"] != receipt["epoch"]
                or row["epoch"] != epoch_for(original, manifest["environment"])
                or row["family"] != FAMILY or row["lineage"] != FAMILY
                or row["statement"] != original["statement"] or row["context"] != original["context"]
                or row.get("task") != "lean_candidate_proof" or row.get("stage") != original["stage"]):
            raise ValueError("pack identity, local context, or lineage mismatch")
        harness = row["source_harness"]
        path = (pack / harness["path"]).resolve()
        if not path.is_relative_to(pack.resolve()):
            raise ValueError("source harness path escapes pack")
        if (harness["target"] != original["target_theorem"] or harness["placeholder"] != module.PLACEHOLDER
                or sha256(path.read_bytes()) != original["source_template_sha256"]
                or manifest["source_files_sha256"].get(harness["path"]) != harness["sha256"]
                or sha256(path.read_bytes()) != harness["sha256"]):
            raise ValueError("pack source harness mismatch")
        candidates = row["candidates"]
        ids = [candidate["id"] for candidate in candidates]
        if len(set(ids)) != len(ids) or set(ids) != set(receipt["outcomes"]):
            raise ValueError("candidate receipt mismatch")
        if sorted(candidate["tactic"] for candidate in candidates) != sorted(candidate["text"] for candidate in original["candidates"]):
            raise ValueError("candidate pool differs from the checked microstep")
        if row.get("orders") != {"compose": ids} or row.get("retrieved") != original["retrieved"]:
            raise ValueError("candidate order or public retrieval drift")
        if ids != sorted(ids):
            raise ValueError("candidate order differs from its canonical text-hash order")
        expected_labels = {candidate["text"]: int(candidate["expected_accept"]) for candidate in original["candidates"]}
        for candidate in candidates:
            if (candidate["id"] != "c_" + sha256(row["epoch"] + "\0" + candidate["tactic"])[:20]
                    or candidate.get("action") != "lean_tactic"):
                raise ValueError("candidate content identity mismatch")
            result = receipt["outcomes"][candidate["id"]]
            label = result["label"]
            if label is not None and (type(label) is not int or label not in (0, 1)):
                raise ValueError("invalid label")
            if label != expected_labels[candidate["tactic"]]:
                raise ValueError("candidate label differs from its native source oracle")
            positive = (result.get("closed") is True and result.get("kernel_ok") is True
                        and type(result.get("kernel_calls")) is int and result["kernel_calls"] == 1
                        and isinstance(result.get("axioms"), list) and set(result["axioms"]) <= ALLOWED_AXIOMS)
            if (label == 1) != positive:
                raise ValueError("inconsistent kernel receipt")
            full = complete_source(module, path.read_text(encoding="utf-8"), candidate["tactic"], harness["target"])
            if result["source_sha256"] != sha256(full) or result["charged_source_bytes"] != len(full.encode("utf-8")):
                raise ValueError("receipt proves a different complete source")
    return manifest, public, private


def replay_pack(checker: LeanChecker, pack: Path = PACK) -> dict:
    _, public, private = load_pack(pack)
    data, module = micro_rows()
    originals = {row["id"]: row for row in data["rows"]}
    rows = []
    for row, receipt in zip(public, private, strict=True):
        harness = row["source_harness"]
        template = (pack / harness["path"]).read_text(encoding="utf-8")
        assert_context(checker, module, originals[row["id"]], template)
        for candidate in row["candidates"]:
            result = checker.compile_source(complete_source(module, template, candidate["tactic"], harness["target"]), harness["target"])
            expected = receipt["outcomes"][candidate["id"]]
            rows.append({"id": row["id"], "candidate": candidate["id"], "label": result["label"],
                         "matches": result["label"] == expected["label"] and result["source_sha256"] == expected["source_sha256"],
                         "axioms": result["axioms"], "status": result["status"]})
    return {"schema": "EvalMath/rh-compactification-pack-replay/v1", "environment": checker.environment,
            "goals": len(public), "candidate_checks": len(rows), "trace_checks": len(public),
            "positive": sum(row["label"] == 1 for row in rows), "negative": sum(row["label"] == 0 for row in rows),
            "unknown": sum(row["label"] is None for row in rows), "matches": all(row["matches"] for row in rows), "rows": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check", "verify"))
    parser.add_argument("--pack", type=Path, default=PACK)
    parser.add_argument("--lean-cmd", default="lake env lean")
    parser.add_argument("--lean-cwd", type=Path, default=ROOT / "lean")
    parser.add_argument("--allow-toolchain-mismatch", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.action == "check":
        manifest, public, _ = load_pack(args.pack)
        result = {"status": "schema_and_source_checked", "goals": len(public), "independent_families": 1,
                  "native_replay_performed": False, "environment_recorded": manifest["environment"]}
    else:
        checker = LeanChecker(shlex.split(args.lean_cmd), args.lean_cwd, allow_version_mismatch=args.allow_toolchain_mismatch)
        result = build_pack(checker, args.pack) if args.action == "build" else replay_pack(checker, args.pack)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_text(result), encoding="utf-8")
    print(json_text({key: value for key, value in result.items() if key not in ("rows", "source_files_sha256")}), end="")
    if args.action == "verify" and not result["matches"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

"""CPU-only RH distillation preflight, independent of any Lean checkout."""
import hashlib
import json
from pathlib import Path

import pytest

from spiral_ln.rh_distillation import (
    anchor_audit, family, git_blob_sha, parse_imports, render_proof, score,
    validate_tasks, walk_imports,
)

BASE = Path(__file__).resolve().parents[1] / "gyms" / "RHProofDistillation"


def test_manifest_and_tasks_are_well_formed():
    manifest = json.loads((BASE / "anchors.json").read_text())
    tasks = json.loads((BASE / "tasks.json").read_text())
    gold = {entry["id"]: entry["proof"] for entry in (json.loads(line) for line in (BASE / "gold.jsonl").read_text().splitlines())}
    assert len(manifest["mirror_commit"]) == 40
    assert len(manifest["archive_sha256"]) == 64
    assert len(manifest["anchors"]) >= 5
    assert len({a["path"] for a in manifest["anchors"]}) == len(manifest["anchors"])
    assert all(len(a["blob_sha"]) == 40 for a in manifest["anchors"])
    validate_tasks(tasks)
    assert set(gold) == {task["id"] for task in tasks}
    assert all("__PROOF__" not in render_proof(task["template"], gold[task["id"]]) for task in tasks)


def test_import_walk_truncation_and_external_boundary(tmp_path):
    src = tmp_path / "src"
    (src / "Development").mkdir(parents=True)
    (src / "Main.lean").write_text("import Mathlib\nimport Development.A Development.B -- comment\n")
    (src / "Development" / "A.lean").write_text("import Development.C\n")
    (src / "Development" / "B.lean").write_text("def b := 1\n")
    (src / "Development" / "C.lean").write_text("import Development.A\n")
    assert parse_imports((src / "Main.lean").read_text()) == ["Mathlib", "Development.A", "Development.B"]
    full = walk_imports(src, ["Main"], 0)
    assert full["visited_modules"] == 4 and not full["truncated"]
    assert full["external_imports"] == ["Mathlib"]
    assert not full["unresolved_internal_imports"]
    capped = walk_imports(src, ["Main"], 1)
    assert capped["truncated"] and capped["visited_modules"] == 1


def test_git_blob_and_decl_detection(tmp_path):
    root = tmp_path / "mirror"
    (root / "src").mkdir(parents=True)
    raw = b"theorem proof_anchor : True := by trivial\n"
    (root / "src" / "Main.lean").write_bytes(raw)
    assert git_blob_sha(raw) == hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    manifest = {"anchors": [{"id": "test", "path": "src/Main.lean", "blob_sha": git_blob_sha(raw), "declaration": "proof_anchor"}]}
    assert anchor_audit(root, manifest)[0]["status"] == "match"
    manifest["anchors"][0]["blob_sha"] = "0" * 40
    assert anchor_audit(root, manifest)[0]["status"] == "mismatch"


def test_scoring_requires_compiler_and_rejects_placeholders():
    tasks = [{"id": "A", "template": "theorem test : True := by\n__PROOF__\n"}]
    seen = []
    def checker(source):
        seen.append(source)
        return source.endswith("  exact True.intro\n"), "mock only", 0.0
    out = score(tasks, [{"id": "A", "proof": "exact True.intro"}, {"id": "A", "proof": "trivial"}, {"id": "Q", "proof": "trivial"}], checker)
    assert out["passes"] == 1 and len(seen) == 1
    assert [x["status"] for x in out["outcomes"]] == ["compiled", "duplicate", "unknown"]
    assert score(tasks, [{"id": "A", "proof": "sorry"}], checker)["outcomes"][0]["status"] == "rejected"


def test_family_classification():
    assert family("Development.AutomorphicArithmetic.PrimitiveCosets.CoreGm") == "analytic"
    assert family("Development.AutomorphicArithmetic.Foundations.GaloisRepresentations.RowSrc") == "galois"
    assert family("Development.AutomorphicArithmetic.ThetaCorrespondence.Main") == "theta"

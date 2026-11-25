"""Scope, provenance, label and revision-budget controls for the additive gym."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil

import pytest

from spiral_ln import rh_numerator_gym as gym


@pytest.fixture
def isolated(tmp_path):
    base = tmp_path / "RHNumeratorStep"
    shutil.copytree(gym.BASE, base)
    gym.load_bundle(base)
    gym.load_pack(base)
    return base


def rewrite_pack(base, manifest, public, private):
    pack = base / "pack"
    entry = manifest["splits"]["train"]
    for field, rows in (("public", public), ("receipts", private)):
        path = pack / entry[field]
        gym.write_jsonl(path, rows)
        entry[field + "_sha256"] = gym.sha256(path.read_bytes())
    (pack / "manifest.json").write_text(gym.json_text(manifest), encoding="utf-8")


def test_prefix_tasks_have_new_namespace_and_exclude_answers(isolated):
    _, tasks, teachers = gym.load_bundle(isolated)
    dependency = gym.DEPENDENCY.read_text(encoding="utf-8").rstrip()
    assert [task["id"] for task in tasks] == [f"RHCG-{number:03d}" for number in range(21, 29)]
    for task, teacher in zip(tasks, teachers, strict=True):
        assert task["context"].startswith(dependency)
        assert re.findall(r"^import .+$", task["context"], re.M) == ["import Init"]
        assert task["qualified_name"] == gym.NAMESPACE + "." + task["declaration"]
        declarations = re.findall(r"^theorem (\w+)\b", task["context"], re.M)
        assert not set(task["unavailable_declarations"]) & set(declarations)
        complete = gym.render(task, teacher["proof"])
        assert re.findall(r"^theorem (\w+)\b", complete, re.M)[-1] == task["declaration"]
        assert "#print axioms " + task["qualified_name"] in complete


def test_rehashed_task_cannot_replace_the_source_statement(isolated):
    _, tasks, _ = gym.load_bundle(isolated)
    tasks[0]["statement"] = "theorem affine_step_zero_iff : True"
    tasks[0]["statement_sha256"] = gym.sha256(tasks[0]["statement"])
    gym.write_jsonl(isolated / "tasks.jsonl", tasks)
    (isolated / "curriculum.json").write_text(gym.json_text(gym.bundle_manifest(isolated, tasks)))
    with pytest.raises(ValueError, match="source-prefix"):
        gym.load_bundle(isolated)


def test_source_digest_forgery_is_rejected(isolated):
    path = isolated / "curriculum.json"
    manifest = json.loads(path.read_text())
    manifest["sources_sha256"]["lean/FeedbackChannel/RHNumeratorStep.lean"] = "0" * 64
    path.write_text(gym.json_text(manifest))
    with pytest.raises(ValueError, match="manifest"):
        gym.load_bundle(isolated)


def test_public_candidates_hide_oracles_and_fit_the_reader(isolated):
    manifest, public, private = gym.load_pack(isolated)
    assert len(public) == len(private) == 6
    assert set(manifest["splits"]) == {"train"}
    assert manifest["independent_families"] == 1
    assert {row["lineage"] for row in public} == {gym.FAMILY}
    forbidden = {"label", "outcomes", "gold", "wrong", "expected_accept", "returncode", "kernel_ok", "axioms"}

    def inspect(value):
        if isinstance(value, dict):
            assert not forbidden & set(value)
            for nested in value.values():
                inspect(nested)
        elif isinstance(value, list):
            for nested in value:
                inspect(nested)

    for row, receipt in zip(public, private, strict=True):
        inspect(row)
        assert "⊢" in row["context"]
        assert len(gym.model_input(row["statement"], row["context"]).encode("utf-8")) <= 384
        assert all(len(candidate["tactic"].encode("utf-8")) <= 384 for candidate in row["candidates"])
        assert sorted(result["label"] for result in receipt["outcomes"].values()) == [0, 1]
        assert row["orders"]["compose"] == sorted(candidate["id"] for candidate in row["candidates"])


def test_rehashed_wrong_candidate_cannot_be_promoted(isolated):
    manifest, public, private = gym.load_pack(isolated)
    wrong = next(result for result in private[0]["outcomes"].values() if result["label"] == 0)
    wrong.update(label=1, closed=True, kernel_ok=True, kernel_calls=1, axioms=[], returncode=0, status="accepted")
    rewrite_pack(isolated, manifest, public, private)
    with pytest.raises(ValueError):
        gym.load_pack(isolated)


@pytest.mark.parametrize("field", ["context", "retrieved", "orders", "epoch", "harness", "candidate"])
def test_rehashed_public_forgery_is_rejected(isolated, field):
    manifest, public, private = gym.load_pack(isolated)
    row = public[0]
    if field == "context":
        row["context"] += "\nanswer : False"
    elif field == "retrieved":
        row["retrieved"]["compose"] = [row["source_harness"]["target"]]
    elif field == "orders":
        row["orders"]["compose"] = list(reversed(row["orders"]["compose"]))
    elif field == "epoch":
        row["epoch"] = private[0]["epoch"] = "forged"
    elif field == "harness":
        row["source_harness"]["path"] = "../outside.lean"
    else:
        row["candidates"][0]["tactic"] = "exact True.intro"
    rewrite_pack(isolated, manifest, public, private)
    with pytest.raises(ValueError, match="source-derived"):
        gym.load_pack(isolated)


@pytest.mark.parametrize("field", ["checker_sha256", "renderer_sha256"])
def test_pack_binds_both_verifier_sources(isolated, field):
    manifest, public, private = gym.load_pack(isolated)
    manifest["environment"][field] = "f" * 64
    rewrite_pack(isolated, manifest, public, private)
    with pytest.raises(ValueError, match="verifier sources"):
        gym.load_pack(isolated)


def test_pack_cannot_claim_scored_confirmation(isolated):
    manifest, public, private = gym.load_pack(isolated)
    manifest["confirmation"]["scored"] = True
    rewrite_pack(isolated, manifest, public, private)
    with pytest.raises(ValueError, match="scope"):
        gym.load_pack(isolated)


@pytest.mark.parametrize("mutation", ["timeout_negative", "infrastructure_positive", "native_context"])
def test_rehashed_native_metadata_contradictions_are_rejected(isolated, mutation):
    manifest, public, private = gym.load_pack(isolated)
    if mutation == "timeout_negative":
        row = next(value for value in private[0]["outcomes"].values() if value["label"] == 0)
        row.update(status="timeout", returncode=-9)
    elif mutation == "infrastructure_positive":
        row = next(value for value in private[0]["outcomes"].values() if value["label"] == 1)
        row.update(status="infrastructure_error", returncode=1, verifier="unverified_backend")
    else:
        private[0]["native"] = {"backend": "unverified_backend", "local_context_replayed": False}
    rewrite_pack(isolated, manifest, public, private)
    with pytest.raises(ValueError):
        gym.load_pack(isolated)


def test_rehashed_impossible_environment_cannot_rekey_the_pack(isolated):
    manifest, public, private = gym.load_pack(isolated)
    manifest["environment"].update(lean_version="Lean (version 0.0.0)", toolchain_matches=True,
                                   timeout_s=-1, memory_limit_mib=-1, max_heartbeats=0)
    for index, spec in enumerate(gym.micro_specs(isolated)):
        old = public[index]
        by_tactic = {candidate["tactic"]: private[index]["outcomes"][candidate["id"]] for candidate in old["candidates"]}
        public[index] = gym.public_row(spec, old["context"], manifest["environment"])
        private[index]["epoch"] = public[index]["epoch"]
        private[index]["outcomes"] = {candidate["id"]: by_tactic[candidate["tactic"]] for candidate in public[index]["candidates"]}
    rewrite_pack(isolated, manifest, public, private)
    with pytest.raises(ValueError, match="verifier sources"):
        gym.load_pack(isolated)


@pytest.mark.parametrize("proof", ["sorry", "exact FeedbackChannel.RHNumeratorStep.affine_step_zero_iff",
                                  "exact FeedbackChannel.RHNumeratorStep.affine_recurrence_eq_joint_numerator"])
def test_new_namespace_target_future_and_admission_are_blocked(isolated, proof):
    _, tasks, _ = gym.load_bundle(isolated)
    checker = gym.NumeratorChecker.__new__(gym.NumeratorChecker)
    checker.compile_source = lambda *_: pytest.fail("surface rejection reached the compiler")
    result = checker.check(tasks[0], proof)
    assert result["label"] == 0 and result["kernel_calls"] == 0


def test_observation_mutation_cannot_change_checked_goal(isolated):
    _, tasks, _ = gym.load_bundle(isolated)
    seen = []

    def checker(task, proof):
        seen.append(deepcopy(task))
        return {"label": None, "closed": False, "kernel_ok": False, "kernel_calls": 1,
                "axioms": [], "status": "timeout"}

    episode = gym.RevisionGym(tasks, checker, max_attempts=2)
    observation = episode.reset(tasks[0]["id"])
    observation["task"]["statement"] = "theorem attack : True"
    observation["task"]["reference_source_bytes"] = 10**9
    result = episode.step("rfl")
    assert seen[0] == tasks[0]
    assert result["reward"] == "0" and result["attempts_remaining"] == 1


def test_unknown_and_invalid_attempts_consume_the_same_episode_budget(isolated):
    _, tasks, _ = gym.load_bundle(isolated)
    outcomes = iter([
        {"label": None, "closed": False, "kernel_ok": False, "kernel_calls": 1, "axioms": [], "status": "timeout"},
        {"label": 0, "closed": False, "kernel_ok": False, "kernel_calls": 0, "axioms": [], "status": "rejected_by_surface"},
    ])
    episode = gym.RevisionGym(tasks, lambda *_: next(outcomes), max_attempts=2)
    episode.reset(tasks[0]["id"])
    first = episode.step("rfl")
    final = episode.step("sorry")
    assert first["reward"] == final["reward"] == "0"
    assert final["attempts_remaining"] == 0 and final["done"] is True
    assert final["lean_invocations"] == 1 and final["best_verified_proof"] is None
    with pytest.raises(ValueError, match="exhausted"):
        episode.step("rfl")


def test_native_receipt_binds_the_verifier_script_and_wrapper():
    receipt = json.loads((gym.BASE / "native_receipt.json").read_text())
    assert receipt["passed"] is True
    for relative in ("scripts/verify_rh_numerator_native.py", "src/spiral_ln/rh_numerator_gym.py",
                     "src/spiral_ln/rh_compactification_gym.py"):
        assert receipt["sources_sha256"][relative] == gym.sha256((gym.ROOT / relative).read_bytes())


@pytest.mark.parametrize("mutation", [
    "teacher_status", "control_status", "native_scope", "loader_source", "trainer_commit",
    "model_input_cap", "training_split", "semantic_control_source", "candidate_replay_status",
])
def test_recorded_evidence_forgery_is_rejected(monkeypatch, mutation):
    path = gym.ROOT / "scripts/verify_rh_numerator.py"
    spec = importlib.util.spec_from_file_location("rhnum_integrity_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_read = module.read

    def forged_read(path):
        result = deepcopy(original_read(path))
        if path == gym.BASE / "native_receipt.json":
            if mutation == "teacher_status":
                result["teachers"]["outcomes"][0]["status"] = "unknown"
            elif mutation == "control_status":
                result["mutation_controls"][0]["status"] = "unknown"
            elif mutation == "native_scope":
                result["heldout_scored"] = True
            elif mutation == "semantic_control_source":
                row = next(row for row in result["mutation_controls"] if row["mutation"] == "zero_branch_shift")
                row["mutated_source_sha256"] = "0" * 64
            elif mutation == "candidate_replay_status":
                next(row for row in result["candidate_pack"]["rows"] if row["label"] == 1)["status"] = "unknown"
        elif path == gym.BASE / "adapter_receipt.json" and mutation == "loader_source":
            files = result["sources"]["looped_transformers"]["file_sha256"]
            files[next(iter(files))] = "0" * 64
        elif path == gym.BASE / "training_smoke.json":
            if mutation == "trainer_commit":
                result["tooling_source"]["commit"] = "0" * 40
            elif mutation == "model_input_cap":
                result["raw_upstream_manifest"]["model"]["max_bytes"] = 1
            elif mutation == "training_split":
                result["raw_upstream_manifest"]["source"]["split"] = "heldout"
        return result

    monkeypatch.setattr(module, "read", forged_read)
    with pytest.raises(AssertionError):
        module.verify()


@pytest.mark.skipif(not os.environ.get("RHNUM_LEAN"), reason="set RHNUM_LEAN for native integration")
def test_native_wrapper_checks_new_namespace_without_module_cache(isolated):
    _, tasks, teachers = gym.load_bundle(isolated)
    checker = gym.NumeratorChecker(shlex.split(os.environ["RHNUM_LEAN"]), gym.ROOT / "lean")
    for index in (0, 7):
        result = checker.check(tasks[index], teachers[index]["proof"])
        assert result["label"] == 1 and result["kernel_calls"] == 1
        assert set(result["axioms"]) <= gym.prior.ALLOWED_AXIOMS
    rejected = checker.check(tasks[0], "rfl")
    assert rejected["label"] == 0 and rejected["kernel_calls"] == 1
    assert rejected["status"] in {"rejected_by_lean", "rejected_axioms"}

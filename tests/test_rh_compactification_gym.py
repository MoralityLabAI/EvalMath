"""Behavioral checks for the source-prefix curriculum and revision budget.

Lean compilation is stubbed for protocol tests. Setting RHCG_LEAN also runs a
small native check against the pinned toolchain.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import re
import shlex
import textwrap

import pytest

from spiral_ln import rh_compactification_gym as gym


@pytest.fixture(scope="module")
def curriculum():
    source = gym.LEAN_SOURCE.read_text(encoding="utf-8")
    tasks, teachers = gym.extract_tasks(source)
    return source, tasks, teachers


def test_every_gold_body_comes_from_its_target_and_has_only_prior_context(curriculum):
    source, tasks, teachers = curriculum
    assert len(tasks) == len(teachers) == 20
    assert len({task["id"] for task in tasks}) == 20
    declarations = re.findall(r"^(?:def|theorem)\s+(\w+)\b", source, re.M)

    for task, teacher in zip(tasks, teachers, strict=True):
        name = task["declaration"]
        begin = source.index(f"-- RHGYM-BEGIN {name}\n")
        end = source.index(f"-- RHGYM-END {name}", begin)
        block = source[begin:end]
        header, body = block[block.index(f"theorem {name}"):].split(":= by\n", 1)
        assert teacher["id"] == task["id"]
        assert teacher["proof"] == textwrap.dedent(body).strip()
        assert task["statement"] == header.rstrip()
        assert task["context"] == source[:begin].rstrip() + "\n\n"

        prior = declarations[:declarations.index(name)]
        later = declarations[declarations.index(name):]
        context_names = re.findall(r"^(?:def|theorem)\s+(\w+)\b", task["context"], re.M)
        assert context_names == prior
        assert task["available_declarations"] == prior
        assert task["unavailable_declarations"] == later

        rendered = gym.render(task, teacher["proof"])
        rendered_names = re.findall(r"^(?:def|theorem)\s+(\w+)\b", rendered, re.M)
        assert rendered_names == prior + [name]
        assert all(unavailable not in rendered_names for unavailable in later[1:])
        assert rendered.endswith(f"#print axioms {task['qualified_name']}\n")
        assert task["reference_source_bytes"] == len(rendered.encode("utf-8"))
        assert teacher["proof_sha256"] == hashlib.sha256(teacher["proof"].encode()).hexdigest()


@pytest.mark.parametrize("proof", [
    "sorry",
    "exact False.elim (by admit)",
    "native_decide",
    "rfl\nend FeedbackChannel.RHCompactification\naxiom forged : False",
    "rfl\n#print axioms forged",
    "exact (by run_tac pure ())",
    "rfl -- hide a second command",
    "exact `(rfl)",
    "exact «extend_before»",
    "exact extend_before",
    "exact FeedbackChannel.RHCompactification.extend_before",
    "exact denominator_unique",
    "exact witness_joint_six",
])
def test_admission_injection_self_and_future_references_never_reach_lean(curriculum, proof):
    _, tasks, _ = curriculum
    checker = object.__new__(gym.LeanChecker)

    def forbidden_compile(*_args, **_kwargs):
        raise AssertionError("a blocked candidate reached the Lean process")

    checker.compile_source = forbidden_compile
    outcome = checker.check(tasks[0], proof)
    assert outcome["label"] == 0
    assert outcome["status"] == "rejected_by_surface"
    assert outcome["kernel_calls"] == 0


def _stub_checker(monkeypatch, tmp_path, output, returncode=0):
    """Keep compile_source's acceptance logic while replacing the process."""
    checker = object.__new__(gym.LeanChecker)
    checker.command, checker.cwd, checker.timeout = ["stub-lean"], tmp_path, 1

    class Process:
        def __init__(self):
            self.returncode = returncode

        def communicate(self, timeout=None):
            return output, ""

    monkeypatch.setattr(gym.subprocess, "Popen", lambda *_a, **_kw: Process())
    return checker


@pytest.mark.parametrize("output,label", [
    ("", None),
    ("'Different.target' does not depend on any axioms", None),
    ("'Example.target' does not depend on any axioms\n"
     "'Example.target' does not depend on any axioms", None),
    ("'Example.target' depends on axioms: [propext]\n"
     "'Example.target' does not depend on any axioms", None),
    ("'Example.target' depends on axioms: [Custom.unsound]", 0),
    ("'Example.target' depends on axioms: [propext, sorryAx]", 0),
    ("'Example.target' does not depend on any axioms\nwarning: declaration uses sorry", 0),
])
def test_zero_exit_cannot_replace_one_clean_axiom_report(monkeypatch, tmp_path, output, label):
    checker = _stub_checker(monkeypatch, tmp_path, output)
    outcome = checker.compile_source("trusted harness", "Example.target")
    assert outcome["label"] == label
    assert outcome["closed"] is False
    assert outcome["kernel_ok"] is False


@pytest.mark.parametrize("output,expected", [
    ("'Example.target' does not depend on any axioms", []),
    ("'Example.target' depends on axioms: []", []),
    ("'Example.target' depends on axioms: [propext,\n Quot.sound]", ["Quot.sound", "propext"]),
])
def test_clean_report_with_successful_compile_is_accepted(monkeypatch, tmp_path, output, expected):
    checker = _stub_checker(monkeypatch, tmp_path, output)
    outcome = checker.compile_source("trusted harness λ", "Example.target")
    assert outcome["label"] == 1
    assert outcome["axioms"] == expected
    assert outcome["charged_source_bytes"] == len("trusted harness λ".encode("utf-8"))


def test_axiom_report_cannot_override_compile_failure(monkeypatch, tmp_path):
    checker = _stub_checker(monkeypatch, tmp_path,
                            "Candidate.lean:1:0: error: type mismatch\n"
                            "'Example.target' does not depend on any axioms", returncode=1)
    assert checker.compile_source("trusted harness", "Example.target")["label"] == 0


@pytest.mark.parametrize("output,returncode,status", [
    ("", -9, "resource_exhausted"),
    ("error: maximum number of heartbeats has been reached", 1, "resource_exhausted"),
    ("error: unknown module prefix 'Missing'", 1, "infrastructure_error"),
])
def test_resource_and_environment_failures_remain_unknown(monkeypatch, tmp_path, output, returncode, status):
    checker = _stub_checker(monkeypatch, tmp_path, output, returncode=returncode)
    outcome = checker.compile_source("trusted harness", "Example.target")
    assert outcome["label"] is None and outcome["status"] == status
    assert outcome["closed"] is False and outcome["kernel_ok"] is False


def _accepted(size):
    return {"label": 1, "closed": True, "kernel_ok": True, "kernel_calls": 1,
            "charged_source_bytes": size, "status": "accepted"}


def test_revision_rewards_only_verified_improvement_and_charges_every_attempt():
    outcomes = {
        "unknown": {"label": None, "closed": False, "kernel_ok": False,
                    "kernel_calls": 1, "status": "timeout"},
        "wrong": {"label": 0, "closed": False, "kernel_ok": False,
                  "kernel_calls": 1, "status": "rejected_by_lean"},
        "surface": {"label": 0, "closed": False, "kernel_ok": False,
                    "kernel_calls": 0, "status": "rejected_by_surface"},
        "large": _accepted(1200),
        "small": _accepted(750),
        "larger_again": _accepted(900),
    }
    calls = []

    def check(task, proof):
        calls.append((task["id"], proof))
        return dict(outcomes[proof])

    task = {"id": "case", "reference_source_bytes": 1000}
    episode = gym.RevisionGym([task], check, max_attempts=8)
    initial = episode.reset("case")
    assert initial["attempts_remaining"] == 8
    assert initial["best_verified_proof"] is None
    candidates = ["unknown", "wrong", "large", "large", "small", "larger_again", "surface", "small"]
    expected_rewards = ["0", "0", "1", "0", "1/4", "0", "0", "0"]
    steps = [episode.step(proof) for proof in candidates]
    assert [step["reward"] for step in steps] == expected_rewards
    assert steps[1]["best_verified_proof"] is None
    assert steps[3]["best_verified_proof"] == "large"
    assert all(step["best_verified_proof"] == "small" for step in steps[4:])
    assert steps[-1]["potential"] == "5/4"
    assert sum(Fraction(step["reward"]) for step in steps) == Fraction(5, 4)
    assert [step["attempts_used"] for step in steps] == list(range(1, 9))
    assert steps[-1]["lean_invocations"] == 7
    assert steps[-1]["attempts_remaining"] == 0 and steps[-1]["done"]
    with pytest.raises(ValueError, match="exhausted"):
        episode.step("small")
    assert len(calls) == 8

    reset = episode.reset("case")
    assert reset["best_verified_proof"] is None and reset["attempts_used"] == 0
    assert episode.potential == 0


@pytest.mark.parametrize("verification", [
    {"label": None, "closed": True, "kernel_ok": True},
    {"label": 1, "closed": False, "kernel_ok": True},
    {"label": 1, "closed": True, "kernel_ok": False},
    {"label": 1},
])
def test_incomplete_acceptance_never_earns_reward(verification):
    episode = gym.RevisionGym([{"id": "case", "reference_source_bytes": 1000}],
                              lambda _task, _proof: verification, max_attempts=1)
    episode.reset("case")
    result = episode.step("candidate")
    assert result["reward"] == result["potential"] == "0"
    assert result["best_verified_proof"] is None
    assert result["done"]


def _write_manifest(base, manifest):
    (base / "curriculum.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_bundle_tampering_is_rejected_before_grading(tmp_path):
    gym.build_bundle(tmp_path)
    manifest, tasks, teachers = gym.load_bundle(tmp_path)
    assert len(tasks) == len(teachers) == 20
    path = tmp_path / "tasks.jsonl"
    path.write_text(path.read_text() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="hash"):
        gym.load_bundle(tmp_path)


@pytest.mark.parametrize("part", ["tasks", "teachers"])
def test_rehashed_payload_cannot_override_the_source_prefix(tmp_path, part):
    manifest = gym.build_bundle(tmp_path)
    path = tmp_path / f"{part}.jsonl"
    rows = gym.read_jsonl(path)
    if part == "tasks":
        rows[0]["context"] += "theorem future_answer : True := by trivial\n"
    else:
        rows[0]["proof"] = "sorry"
        rows[0]["proof_sha256"] = gym.sha256("sorry")
    gym.write_jsonl(path, rows)
    manifest[f"{part}_sha256"] = gym.sha256(path.read_bytes())
    _write_manifest(tmp_path, manifest)
    with pytest.raises(ValueError, match="source prefix"):
        gym.load_bundle(tmp_path)


@pytest.mark.parametrize("drift", ["split", "family_count"])
def test_public_family_cannot_be_relabelled_as_confirmation_data(tmp_path, drift):
    manifest = gym.build_bundle(tmp_path)
    if drift == "split":
        tasks = manifest["splits"]["train"]
        manifest["splits"] = {"train": tasks[:-1], "confirmation": [tasks[-1]]}
    else:
        manifest["independent_families"] = 2
    _write_manifest(tmp_path, manifest)
    with pytest.raises(ValueError, match="training family"):
        gym.load_bundle(tmp_path)


def test_manifest_cannot_claim_another_source_hash(tmp_path):
    manifest = gym.build_bundle(tmp_path)
    manifest["source_sha256"] = "0" * 64
    _write_manifest(tmp_path, manifest)
    with pytest.raises(ValueError):
        gym.load_bundle(tmp_path)


@pytest.mark.skipif(not os.environ.get("RHCG_LEAN"), reason="RHCG_LEAN is not configured")
def test_native_checker_rejects_wrong_proof_and_admission(curriculum):
    _, tasks, teachers = curriculum
    checker = gym.LeanChecker(shlex.split(os.environ["RHCG_LEAN"]), gym.ROOT / "lean", timeout=20)
    good = checker.check(tasks[0], teachers[0]["proof"])
    wrong = checker.check(tasks[0], "rfl")
    admission = checker.check(tasks[0], "sorry")
    assert good["label"] == 1
    assert wrong["label"] == 0 and wrong["kernel_calls"] == 1
    assert admission["label"] == 0 and admission["kernel_calls"] == 0

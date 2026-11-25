"""Source/label binding controls for the native Lean microstep candidate pack.

These tests copy the recorded native pack. Rehashing a modified file must not
make it agree with the fixed source-derived task or its checked candidate label.
The trace comparison test stubs process execution with the recorded real state;
the pack build/replay commands perform the native Lean trace checks themselves.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import shutil

import pytest

from spiral_ln import rh_compactification_pack as pack


@pytest.fixture
def isolated_pack(tmp_path, monkeypatch):
    """Copy evidence and pack together so mutations never touch shared files."""
    root = tmp_path / "repo"
    base = root / "gyms" / "RHCompactification"
    base.parent.mkdir(parents=True)
    shutil.copytree(pack.BASE, base)
    lean_source = root / "lean" / "FeedbackChannel" / "RHCompactification.lean"
    lean_source.parent.mkdir(parents=True)
    shutil.copyfile(pack.LEAN_SOURCE, lean_source)
    checker_source = root / "src" / "spiral_ln" / "rh_compactification_gym.py"
    checker_source.parent.mkdir(parents=True)
    shutil.copyfile(pack.ROOT / "src" / "spiral_ln" / "rh_compactification_gym.py", checker_source)
    monkeypatch.setattr(pack, "ROOT", root)
    monkeypatch.setattr(pack, "BASE", base)
    monkeypatch.setattr(pack, "LEAN_SOURCE", lean_source)
    destination = base / "pack"
    manifest, public, private = pack.load_pack(destination)
    return destination, manifest, public, private


def write_pack(destination: Path, manifest: dict, public: list[dict], private: list[dict]):
    """Refresh ordinary file hashes while preserving the forged semantic change."""
    entry = manifest["splits"]["train"]
    for field, rows in (("public", public), ("receipts", private)):
        path = destination / entry[field]
        pack.write_jsonl(path, rows)
        entry[field + "_sha256"] = pack.sha256(path.read_bytes())
    (destination / "manifest.json").write_text(pack.json_text(manifest), encoding="utf-8")


def test_pack_public_rows_hide_oracles_and_fit_native_encoder(isolated_pack):
    destination, manifest, public, private = isolated_pack
    assert len(public) == len(private) == 12
    assert manifest["independent_families"] == 1
    assert manifest["scientific_eligible"] is False
    assert set(manifest["splits"]) == {"train"}
    assert {row["stage"] for row in public} == {"prefix", "overlap", "glue", "denominator", "joint"}
    forbidden_keys = {"label", "expected_accept", "lean_returncode", "returncode", "kernel_ok",
                      "closed", "diagnostic", "outcomes", "gold", "wrong", "teacher", "axioms"}

    def inspect(value):
        if isinstance(value, dict):
            assert not forbidden_keys.intersection(value)
            for nested in value.values():
                inspect(nested)
        elif isinstance(value, list):
            for nested in value:
                inspect(nested)

    unicode_seen = False
    for row, receipt in zip(public, private, strict=True):
        inspect(row)
        encoded = f"<STATEMENT> {row['statement']}\n<GOALS> {row['context']}"
        assert len(encoded.encode("utf-8")) <= 384
        unicode_seen |= len(encoded.encode("utf-8")) > len(encoded)
        assert "⊢" in row["context"]
        ids = []
        for candidate in row["candidates"]:
            assert set(candidate) == {"id", "action", "tactic"}
            assert candidate["action"] == "lean_tactic"
            assert len(candidate["tactic"].encode("utf-8")) <= 384
            expected_id = "c_" + pack.sha256(row["epoch"] + "\0" + candidate["tactic"])[:20]
            assert candidate["id"] == expected_id
            assert re.fullmatch(r"c_[0-9a-f]{20}", candidate["id"])
            ids.append(candidate["id"])
        assert row["orders"]["compose"] == sorted(ids)
        assert sorted(result["label"] for result in receipt["outcomes"].values()) == [0, 1]
        template = (destination / row["source_harness"]["path"]).read_text(encoding="utf-8")
        declarations = re.findall(r"^(?:def|theorem)\s+(\w+)\b", template, re.M)
        assert declarations[-1] == row["source_harness"]["target"].rsplit(".", 1)[-1]
        prior_names = {"FeedbackChannel.RHCompactification." + name for name in declarations[:-1]}
        assert set(row["retrieved"]["compose"]) <= prior_names
    assert unicode_seen


def test_rehashed_wrong_label_cannot_be_promoted_to_accepted(isolated_pack):
    destination, manifest, public, private = isolated_pack
    wrong = next(result for result in private[0]["outcomes"].values() if result["label"] == 0)
    wrong.update(label=1, closed=True, kernel_ok=True, kernel_calls=1, axioms=[],
                 returncode=0, status="accepted", diagnostic="forged clean report")
    write_pack(destination, manifest, public, private)
    with pytest.raises(ValueError):
        pack.load_pack(destination)


def test_rehashed_microstep_oracle_flags_cannot_override_generator(isolated_pack):
    destination, manifest, public, private = isolated_pack
    evidence_path = pack.BASE / "microsteps.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    wrong = evidence["rows"][0]["candidates"][1]
    wrong["expected_accept"] = True
    wrong["lean_returncode"] = 0
    evidence_path.write_text(pack.json_text(evidence), encoding="utf-8")
    manifest["source_evidence_sha256"] = pack.sha256(evidence_path.read_bytes())
    write_pack(destination, manifest, public, private)
    with pytest.raises(ValueError):
        pack.load_pack(destination)


def test_rehashed_consistent_candidate_id_rename_is_rejected(isolated_pack):
    destination, manifest, public, private = isolated_pack
    candidate = public[0]["candidates"][0]
    old, new = candidate["id"], "c_" + "f" * 20
    assert old != new
    candidate["id"] = new
    public[0]["orders"]["compose"] = [new if x == old else x for x in public[0]["orders"]["compose"]]
    private[0]["outcomes"][new] = private[0]["outcomes"].pop(old)
    write_pack(destination, manifest, public, private)
    with pytest.raises(ValueError):
        pack.load_pack(destination)


def test_rehashed_epoch_change_is_rejected(isolated_pack):
    destination, manifest, public, private = isolated_pack
    public[0]["epoch"] = private[0]["epoch"] = "rhcg_" + "f" * 64
    write_pack(destination, manifest, public, private)
    with pytest.raises(ValueError):
        pack.load_pack(destination)


def test_goal_change_invalidates_existing_epoch_after_hash_refresh(isolated_pack):
    destination, manifest, public, private = isolated_pack
    evidence_path = pack.BASE / "microsteps.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    forged_context = evidence["rows"][0]["context"] + "\nforged_answer : True"
    evidence["rows"][0]["context"] = forged_context
    public[0]["context"] = forged_context
    evidence_path.write_text(pack.json_text(evidence), encoding="utf-8")
    manifest["source_evidence_sha256"] = pack.sha256(evidence_path.read_bytes())
    write_pack(destination, manifest, public, private)
    with pytest.raises(ValueError):
        pack.load_pack(destination)


def test_rehashed_template_substitution_cannot_change_the_proved_source(isolated_pack):
    destination, manifest, public, private = isolated_pack
    harness = public[0]["source_harness"]
    path = destination / harness["path"]
    path.write_text(path.read_text(encoding="utf-8") + "\ntheorem injected_fact : True := by trivial\n",
                    encoding="utf-8")
    forged_hash = pack.sha256(path.read_bytes())
    harness["sha256"] = forged_hash
    manifest["source_files_sha256"][harness["path"]] = forged_hash
    write_pack(destination, manifest, public, private)
    with pytest.raises(ValueError):
        pack.load_pack(destination)


@pytest.mark.parametrize("field", ["context", "retrieved", "orders", "action", "stage", "task"])
def test_rehashed_public_contract_forgery_is_rejected(isolated_pack, field):
    destination, manifest, public, private = isolated_pack
    row = public[0]
    if field == "context":
        row["context"] += "\nforged_answer : True"
    elif field == "retrieved":
        row["retrieved"]["compose"] = ["Answer." + row["candidates"][0]["id"]]
    elif field == "orders":
        row["orders"]["compose"] = ["c_" + "e" * 20]
    elif field == "action":
        row["candidates"][0]["action"] = "unverified_external_action"
    elif field == "stage":
        row["stage"] = "independent_confirmation"
    else:
        row["task"] = "unverified_statement"
    write_pack(destination, manifest, public, private)
    with pytest.raises(ValueError):
        pack.load_pack(destination)


def test_trace_comparison_rejects_a_forged_local_state(isolated_pack):
    _, _, _, _ = isolated_pack
    data, module = pack.micro_rows()
    original = data["rows"][0]
    forged = deepcopy(original)
    forged["context"] = original["context"].replace("⊢", "forged : False\n⊢")
    template = (pack.ROOT / original["source_template_path"]).read_text(encoding="utf-8")
    seen_sources = []

    class RecordedTraceChecker:
        def compile_source(self, source, target):
            seen_sources.append(source)
            assert target == original["target_theorem"]
            return {"label": 1, "diagnostic": original["context"] +
                    f"\n'{target}' depends on axioms: [propext]\n"}

    pack.assert_context(RecordedTraceChecker(), module, original, template)
    with pytest.raises(ValueError, match="local goal"):
        pack.assert_context(RecordedTraceChecker(), module, forged, template)
    assert len(seen_sources) == 2
    assert seen_sources[0] == seen_sources[1]
    assert "trace_state" in seen_sources[0]
    assert "__RHGYM_FRAGMENT__" not in seen_sources[0]

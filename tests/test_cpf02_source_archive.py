"""Offline integrity checks on the archived upstream statements and derived imports."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pinned_git_blobs():
    manifest = json.loads((ROOT / "configs/cpf02_upstream.json").read_text(encoding="utf-8"))
    assert len(manifest["sources"]) == 11
    for entry in manifest["sources"]:
        data = (ROOT / entry["path"]).read_bytes()
        assert hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == entry["git_blob_sha"]


def test_imports_are_derived_from_pins():
    archive = ROOT / "fixtures/external/cpf02"
    lean = ROOT / "lean/FeedbackChannel/CPF02"
    raw_anthropic = (archive / "anthropic/Statement.lean").read_text(encoding="utf-8")
    adapted = raw_anthropic.replace("(coeff d q).coeff i", "(q.coeff d).coeff i").replace(
        "then coeff d f else 0", "then f.coeff d else 0")
    assert adapted != raw_anthropic
    assert (lean / "AnthropicStatement.lean").read_text(encoding="utf-8") == adapted
    raw = (archive / "openai/Comparator.lean").read_text(encoding="utf-8")
    header = "-- Derived from the Apache-2.0 licensed OpenAI comparator at f5702854040e97fa7675c21ba37a9608f5f92dd3.\n"
    header += "-- Admitted endpoint removed; definitions copied verbatim. See fixtures/external/cpf02/openai/LICENSE.\n"
    derived = header + raw.split("\nnamespace Computability.VPVNP.Standalone\n")[0] + "\n\nend OAI\n"
    assert (lean / "OpenAIComparatorDefs.lean").read_text(encoding="utf-8") == derived
    assert "sorry" not in derived
    assert "sorry" not in (lean / "AnthropicStatement.lean").read_text(encoding="utf-8")

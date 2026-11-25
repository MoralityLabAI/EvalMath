"""VAD-12 gate receipt and DataGoblin records are internally consistent."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "output/verified_abstraction"


def test_gate_verdict_follows_rule():
    g = json.loads((out / "vad_12_gate.json").read_text())
    tol = g["gate"]["tolerance"]
    fresh = [f for f in g["regret"] if f.startswith("fresh_")]
    passed = any(all(g["regret"][f][nm] <= g["regret"][f]["greedy2"] + tol for f in fresh)
                 for nm in g["regret"][fresh[0]] if nm not in ("stop", "random", "direct", "greedy0", "greedy1", "greedy2"))
    assert (g["gate"]["verdict"] == "PASS") == passed
    assert g["gate"]["verdict"] == "FAIL"


def test_datagoblin_records_well_formed():
    rec = json.loads((out / "datagoblin/vad12_data_recipe.json").read_text())
    for k in ("recipe_id", "split_contract", "falsification_criteria", "claim_boundary", "constitution_version"):
        assert k in rec
    n = {}
    for line in (out / "datagoblin/vad11_records.jsonl").read_text().splitlines():
        r = json.loads(line)
        assert r["schema_version"] == "1.0"
        n[r["record_type"]] = n.get(r["record_type"], 0) + 1
    assert n["theorem_instance"] == 200 and n["proof_trace"] == n["verification_receipt"] == 880
    reg = json.loads((out / "claim_registry.json").read_text())
    assert len({c["id"] for c in reg}) == len(reg) and all(c["level"] in ("T", "E", "S", "K", "N", "T/E") for c in reg)

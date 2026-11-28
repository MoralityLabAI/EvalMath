"""Produce the small committed summary from the full MIC-17 run and audit."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PROTOCOL_COMMIT = "d7b1ca9a1d65625506d154586eb5f7d193d5b4ef"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_summary():
    raw = json.loads((HERE / "results.json").read_text())
    audit = json.loads((HERE / "audit_results.json").read_text())
    assert audit["input_sha256"] == digest(HERE / "results.json")
    assert audit["audit_source_sha256"] == digest(HERE / "audit17.py")
    assert raw["protocol_sha256"] == digest(HERE / "protocol.json")
    for name, expected in raw["source_sha256"].items():
        assert digest(HERE / name) == expected
    assert raw["phase"] == "development" and audit["roots"] == 48
    rows = []
    for r in raw["rows"]:
        rows.append({"family": r["family"], "seed": r["seed"],
                     "prior_mass": sum(r["prior"]), "full_weighted_value": r["full_value"],
                     "optimal_values_by_code_cap": {k: x["value"] for k, x in r["optimal"].items()},
                     "primary_window_values": {str(k): r["windows"]["012:k" + str(k)]["value"] for k in (1, 2)},
                     "minimum_lossless_codes": r["minimum_lossless_codes"]})
    candidates = [(r, pair) for r in raw["rows"] for pair in r["pair_aliasing"]
                  if pair["shares_primary_window_2"] and pair["full_value"] > pair["common_first_value"]]
    witness_root, witness_pair = candidates[0]
    source_names = ("protocol.json", "mic17.py", "mic16_reference.py", "audit17.py",
                    "test_mic17.py", "summarize17.py", "preflight_input.json", "preflight_output.json")
    return {
        "schema": "MIC-17/published-summary/v1",
        "registered_protocol_commit": PROTOCOL_COMMIT,
        "evidence_class": "exact finite synthetic domain; public development",
        "summary": raw["summary"],
        "display_percentages": {k: 100 * float(Fraction(v)) for k, v in raw["summary"]["mean_reward_ratio"].items()},
        "audit_counts": audit["counts"],
        "preflight": json.loads((HERE / "preflight_output.json").read_text()),
        "first_positive_pair_sharing_last_two_observations": {
            "family": witness_root["family"], "seed": witness_root["seed"],
            "pair": witness_pair, "prior_weights": [witness_root["prior"][w] for w in witness_pair["worlds"]],
            "prefix_histories": [witness_root["prefix_histories"][w] for w in witness_pair["worlds"]],
            "optimal_two_code_partition": witness_root["optimal"]["2"]["partition"]},
        "source_sha256": {name: digest(HERE / name) for name in source_names},
        "data_artifacts": {name: {"sha256": digest(HERE / name), "bytes": (HERE / name).stat().st_size}
                           for name in ("pilot_results.json", "results.json", "audit_results.json")},
        "rows": rows,
    }


if __name__ == "__main__":
    result = build_summary()
    (HERE / "summary.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"roots": len(result["rows"]), "audit_counts": result["audit_counts"],
                      "headroom_gate": result["summary"]["headroom_gate"]}, indent=2))

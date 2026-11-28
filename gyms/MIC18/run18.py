"""Replay MIC-18's frozen complete finite suite, or its separate small pilot."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from finite_memory import (compile_exact, evaluate, handoff_optimum, make_constant,
                           make_parity, make_window, storage)


BASE = Path(__file__).resolve().parent
SOURCE_FILES = ("finite_memory.py", "run18.py", "audit18.py", "test_mic18.py", "protocol.json")
PROTOCOL_SHA256 = "55d440de4046213da39acc4636b8bcc57c5d6371922e62c0ee190cafc4708919"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_protocol():
    path = BASE / "protocol.json"
    if digest(path) != PROTOCOL_SHA256:
        raise ValueError("protocol differs from the remotely frozen protocol")
    return json.loads(path.read_text())


def pilot():
    protocol = read_protocol()
    rows, details = [], []
    spec = protocol["development_pilot"]
    for task in spec["tasks"]:
        online = compile_exact(spec["width"], spec["capacity"], task)
        handoff = handoff_optimum(spec["width"], spec["capacity"], task)
        effect = Fraction(handoff["score"], handoff["total"]) - Fraction(online["score"], online["total"])
        rows.append({"unit_id": "constructed-J2-" + task, "paired_effect": str(effect),
                     "sham_effects": ["0"]})
        details.append({"task": task, "online": online, "handoff": handoff,
                        "evaluation": evaluate(online["controller"])})
    return {"schema_version": 1, "experiment_id": "MIC-18 exact finite diagnostic",
            "independent_unit": "constructed task family; independence is unverified",
            "alpha": "1/20", "scientific_min_effect": "1/20", "target_effect": "1/10",
            "measurement_resolution": "1/24", "sham_quantile": "19/20", "sham_confidence": "19/20",
            "planned_comparisons": 1, "confirm_units_planned": 2,
            "pilot_from_development_only": True, "heldout_sealed": False,
            "units_independent": False, "pilot": rows, "details": details,
            "protocol_sha256": PROTOCOL_SHA256,
            "notes": "Two families and identity shams are planner diagnostics. No model fits or population confirmation are authorized."}


def run():
    protocol = read_protocol()
    exact, handoff, constructive = [], [], []
    for width, capacity in protocol["exact_search"]:
        row = compile_exact(width, capacity,
                            max_partitions=protocol["resource_guard"]["max_reachable_partitions_per_phase"])
        row.update({"width": width, "capacity": capacity, "task": "query",
                    "evaluation": evaluate(row["controller"]), "storage": storage(row["controller"])})
        exact.append(row)
    for width, capacity in protocol["handoff"]:
        handoff.append(handoff_optimum(width, capacity))
    for width in protocol["constructive_widths"]:
        cases = [("window/J%d/B%d" % (width, bits), make_window(width, bits))
                 for bits in range(width + 1)]
        cases.extend([("parity/constant/J%d" % width, make_constant(width, "parity")),
                      ("parity/xor/J%d" % width, make_parity(width))])
        for label, controller in cases:
            constructive.append({"label": label, "controller": controller,
                                 "evaluation": evaluate(controller), "storage": storage(controller)})
    online = next(row for row in exact if (row["width"], row["capacity"]) == (3, 2))
    oracle = next(row for row in handoff if (row["width"], row["capacity"]) == (3, 2))
    online_fraction = Fraction(online["score"], online["total"])
    handoff_fraction = Fraction(oracle["score"], oracle["total"])
    gap = handoff_fraction - online_fraction
    primary = {"width": 3, "capacity": 2, "online_score": online["score"],
               "online_total": online["total"], "handoff_score": oracle["score"],
               "handoff_total": oracle["total"], "online_fraction": str(online_fraction),
               "handoff_fraction": str(handoff_fraction), "gap_handoff_minus_online": str(gap),
               "status": "POSITIVE_EXACT_GAP" if gap > 0 else "NO_EXACT_GAP"}
    return {"schema": "MIC-18/online-memory/v1", "protocol_sha256": PROTOCOL_SHA256,
            "source_sha256": {name: digest(BASE / name) for name in SOURCE_FILES},
            "exact_search": exact, "handoff": handoff, "constructive": constructive,
            "primary": primary,
            "summary": {"evidence_class": "exact finite domain", "task_families": 2,
                        "independent_model_roots": 0, "exact_cases": len(exact),
                        "handoff_cases": len(handoff), "constructive_cases": len(constructive),
                        "fits": 0, "empirical_gate": "REDESIGN_OR_PILOT_ONLY",
                        "query_zero_error_lower_bound_codes": "2**J",
                        "parity_zero_error_lower_bound_codes": 2,
                        "trained_models_tested": 0}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    out = args.out or BASE / ("pilot.json" if args.pilot else "results.json")
    result = pilot() if args.pilot else run()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(out), "sha256": digest(out),
                      "primary": result.get("primary"), "pilot": result.get("pilot")}, sort_keys=True))


if __name__ == "__main__":
    main()

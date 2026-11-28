"""Independent finite audit for MIC-18 online memory controllers.

This module uses labeled transition assignments and direct word replay. It
does not import the production compiler or its restricted-growth generator.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import sys


CONTROLLER_KEYS = {
    "schema", "name", "task", "width", "capacity", "initial_state",
    "transitions", "outputs",
}
SOURCE_FILES = {"finite_memory.py", "run18.py", "audit18.py", "test_mic18.py", "protocol.json"}
FROZEN_PROTOCOL_SHA256 = "55d440de4046213da39acc4636b8bcc57c5d6371922e62c0ee190cafc4708919"
EXACT_CASES = {(j, k) for j in range(1, 7) for k in (1, 2)} | {
    (2, 3), (2, 4), (3, 3), (3, 4),
}
HANDOFF_CASES = {(j, k) for j in range(1, 4) for k in range(1, 5)}
CONSTRUCTIVE_WIDTHS = (1, 2, 3, 4, 6, 8)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def integer(value):
    return type(value) is int


def validate_controller(controller):
    require(type(controller) is dict, "controller must be an object")
    require(set(controller) == CONTROLLER_KEYS, "unexpected controller fields")
    require(controller["schema"] == "MIC-18/controller/v1", "controller schema")
    require(type(controller["name"]) is str, "controller name")
    require(controller["task"] in ("query", "parity"), "task")
    width, capacity = controller["width"], controller["capacity"]
    require(integer(width) and width >= 1, "positive integer width")
    require(integer(capacity) and capacity >= 1, "positive integer capacity")
    require(integer(controller["initial_state"]) and controller["initial_state"] == 0,
            "fixed initial state")
    transitions = controller["transitions"]
    require(type(transitions) in (list, tuple) and len(transitions) == width,
            "one transition table per public phase")
    for layer in transitions:
        require(type(layer) in (list, tuple) and len(layer) == capacity,
                "transition table capacity")
        for row in layer:
            require(type(row) in (list, tuple) and len(row) == 2,
                    "binary observation row")
            require(all(integer(x) and 0 <= x < capacity for x in row),
                    "transition escaped memory alphabet")
    queries = width if controller["task"] == "query" else 1
    outputs = controller["outputs"]
    require(type(outputs) in (list, tuple) and len(outputs) == capacity,
            "decoder table capacity")
    for row in outputs:
        require(type(row) in (list, tuple) and len(row) == queries,
                "decoder sees only a final code and public query")
        require(all(integer(x) and x in (0, 1) for x in row), "binary decoder output")
    return width, capacity, queries


def check_update_closure(state_maps, capacity):
    require(state_maps and tuple(state_maps[0]) == (0,), "initial prefix map")
    checks = 0
    for phase, current in enumerate(state_maps):
        require(len(current) == 2 ** phase, "prefix map coverage")
        require(all(integer(x) and 0 <= x < capacity for x in current),
                "prefix map capacity")
        if phase == 0:
            continue
        previous = state_maps[phase - 1]
        updates = {}
        for prefix, code in enumerate(previous):
            for bit in (0, 1):
                new = current[2 * prefix + bit]
                key = code, bit
                require(updates.setdefault(key, new) == new,
                        "same retained state and observation give different updates")
                checks += 1
    return checks


def audit_controller(controller):
    """Replay every word without access to the producer's evaluator."""
    width, capacity, queries = validate_controller(controller)
    maps = [dict() for _ in range(width + 1)]
    score = 0
    paths = []
    nonanticipation = {}
    for word in range(2 ** width):
        bits = tuple(int(x) for x in format(word, "0" + str(width) + "b"))
        state = controller["initial_state"]
        prefix = 0
        states = [state]
        require(maps[0].setdefault(0, state) == state, "initial replay state")
        for phase, bit in enumerate(bits):
            previous = state
            state = controller["transitions"][phase][state][bit]
            require(nonanticipation.setdefault((phase, previous, bit), state) == state,
                    "inconsistent observable update")
            prefix = 2 * prefix + bit
            require(maps[phase + 1].setdefault(prefix, state) == state,
                    "future observations leaked into prefix state")
            states.append(state)
        guesses = list(controller["outputs"][state])
        targets = list(bits) if controller["task"] == "query" else [sum(bits) % 2]
        correct = sum(a == b for a, b in zip(guesses, targets))
        score += correct
        paths.append({"word": word, "observations": list(bits), "states": states,
                      "outputs": guesses, "targets": targets, "correct": correct})
    state_maps = [[mapping[p] for p in range(2 ** phase)]
                  for phase, mapping in enumerate(maps)]
    closure_checks = check_update_closure(state_maps, capacity)
    require(all(len(set(mapping)) <= capacity for mapping in state_maps),
            "reachable memory capacity")
    total = (2 ** width) * queries
    return {"score": score, "total": total, "state_maps": state_maps, "paths": paths,
            "verified_words": 2 ** width, "verified_decisions": total,
            "verified_updates": width * (2 ** width),
            "nonanticipation_update_checks": len(nonanticipation),
            "update_closure_checks": closure_checks}


def canonicalize(mapping):
    labels = {}
    return tuple(labels.setdefault(label, len(labels)) for label in mapping)


def partition_score(mapping, width, task):
    """Optimal decoder value under the uniform complete word/query domain."""
    counts = defaultdict(lambda: [0, 0])
    for word, code in enumerate(mapping):
        bits = tuple(int(x) for x in format(word, "0" + str(width) + "b"))
        targets = bits if task == "query" else (sum(bits) % 2,)
        for query, truth in enumerate(targets):
            counts[code, query][truth] += 1
    return sum(max(row) for row in counts.values())


def partition_decoder(mapping, width, capacity, task):
    """Choose each majority output separately, with the frozen zero tie rule."""
    queries = width if task == "query" else 1
    counts = [[[0, 0] for _ in range(queries)] for _ in range(capacity)]
    for word, code in enumerate(mapping):
        bits = tuple(int(x) for x in format(word, "0" + str(width) + "b"))
        targets = bits if task == "query" else (sum(bits) % 2,)
        for query, truth in enumerate(targets):
            counts[code][query][truth] += 1
    return [[int(ones > zeros) for zeros, ones in state] for state in counts]


@lru_cache(None)
def labeled_optimum(width, capacity, task="query"):
    """Enumerate all labeled transition tables, then quotient label renamings.

    Active previous states each receive two transitions. Every assignment to
    the full declared next-state alphabet is tried. Canonicalization removes
    representational duplicates after the transition has been evaluated.
    """
    require(integer(width) and width >= 1, "positive search width")
    require(integer(capacity) and capacity >= 1, "positive search capacity")
    require(task in ("query", "parity"), "search task")
    require(width <= 6 and (capacity <= 2 or (width <= 3 and capacity <= 4)),
            "independent exhaustive search is limited to the declared finite grid")
    partitions = {(0,)}
    counts = [1]
    evaluated = []
    for _phase in range(width):
        following = set()
        candidates = 0
        for old in sorted(partitions):
            active = max(old) + 1
            for table in product(range(capacity), repeat=2 * active):
                reached = tuple(table[2 * code + bit] for code in old for bit in (0, 1))
                following.add(canonicalize(reached))
                candidates += 1
        partitions = following
        counts.append(len(partitions))
        evaluated.append(candidates)
    best = -1
    best_partition = None
    for mapping in sorted(partitions):
        value = partition_score(mapping, width, task)
        if value > best:
            best = value
            best_partition = mapping
    return {"score": best, "total": (2 ** width) * (width if task == "query" else 1),
            "reachable_partition_counts": counts, "labeled_tables_evaluated": evaluated,
            "final_partitions": len(partitions), "method": "all_labeled_transition_assignments",
            "partition": list(best_partition)}


@lru_cache(None)
def handoff_optimum(width, capacity, task="query"):
    """Independent unrestricted final-message optimum on at most eight words."""
    require(1 <= width <= 3 and 1 <= capacity <= 4, "handoff exhaustive domain")
    best = -1
    best_partition = None
    unique = set()
    assignments = 0
    for labels in product(range(capacity), repeat=2 ** width):
        assignments += 1
        canonical = canonicalize(labels)
        if canonical in unique:
            continue
        unique.add(canonical)
        value = partition_score(canonical, width, task)
        if value > best:
            best = value
            best_partition = canonical
    return {"score": best, "total": (2 ** width) * (width if task == "query" else 1),
            "partitions": len(unique), "labeled_assignments": assignments,
            "partition": list(best_partition)}


def verify_injective_decoding(controller):
    """Executable finite instance of the delayed-query counting argument."""
    checked = audit_controller(controller)
    require(controller["task"] == "query", "coordinate reconstruction task")
    require(checked["score"] == checked["total"], "zero-error premise")
    final = checked["state_maps"][-1]
    require(len(set(final)) == 2 ** controller["width"], "lossless encoder is injective")
    require(controller["capacity"] >= 2 ** controller["width"], "counting lower bound")
    return len(final)


def verify_parity_decoding(controller):
    """Check that a perfect parity decoder separates both parity classes."""
    checked = audit_controller(controller)
    require(controller["task"] == "parity", "parity task")
    require(checked["score"] == checked["total"], "perfect parity premise")
    classes = [set(), set()]
    for path in checked["paths"]:
        classes[path["targets"][0]].add(path["states"][-1])
    require(all(classes) and classes[0].isdisjoint(classes[1]),
            "opposite parity classes cannot share a retained code")
    require(controller["capacity"] >= 2, "parity requires two distinguishable codes")
    return sum(len(group) for group in classes)


def check_evaluation(controller, reported):
    """Verify the producer's exact value, domain coverage, and every trajectory."""
    checked = audit_controller(controller)
    require(type(reported) is dict, "evaluation object")
    for field in ("score", "total"):
        require(integer(reported[field]) and reported[field] == checked[field],
                "reported evaluation " + field)
    require(reported["fraction"] == str(Fraction(checked["score"], checked["total"])),
            "reported exact fraction")
    require(reported["state_maps"] == checked["state_maps"], "reported prefix state maps")
    require(reported["reachable_state_counts"] == [len(set(m)) for m in checked["state_maps"]],
            "reported reachable state counts")
    require(reported["observations"] == checked["verified_updates"],
            "reported observation count")
    expected_paths = [{"word": path["word"], "observations": path["observations"],
                       "states": path["states"], "predictions": path["outputs"],
                       "targets": path["targets"]} for path in checked["paths"]]
    require(reported["paths"] == expected_paths, "reported full-domain trajectories")
    return checked


def check_storage(controller, reported):
    width, capacity, queries = validate_controller(controller)
    bits = 0
    while 2 ** bits < capacity:
        bits += 1
    expected = {
        "dynamic_capacity_codes": capacity,
        "dynamic_code_bits": bits,
        "public_phases": width,
        "public_final_queries": queries,
        "static_transition_entries": sum(len(row) for layer in controller["transitions"]
                                         for row in layer),
        "static_decoder_entries": sum(len(row) for row in controller["outputs"]),
        "static_entry_encoding": "transition entries are state IDs; decoder entries are bits",
        "excluded": "runtime representation, interpreter and source code",
    }
    require(reported == expected, "independent dynamic and static storage accounting")


def source_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_statistic_partition(mapping, symbols):
    """Require the retained codes to describe exactly the named statistic."""
    require(len(mapping) == len(symbols), "statistic domain")
    forwards, backwards = {}, {}
    for code, symbol in zip(mapping, symbols):
        require(forwards.setdefault(symbol, code) == code, "extra state beyond statistic")
        require(backwards.setdefault(code, symbol) == symbol, "statistic lost in memory")


def check_handoff(row):
    width, capacity = row["width"], row["capacity"]
    require(row["task"] == "query", "declared handoff task")
    optimum = handoff_optimum(width, capacity)
    require(row["score"] == optimum["score"] and row["total"] == optimum["total"],
            "independent handoff optimum")
    require(row["fraction"] == str(Fraction(optimum["score"], optimum["total"])),
            "handoff exact fraction")
    require(row["partition_count"] == optimum["partitions"], "handoff partition coverage")
    partition = row["partition"]
    require(type(partition) is list and len(partition) == 2 ** width, "handoff world coverage")
    require(all(integer(x) and 0 <= x < capacity for x in partition), "handoff capacity")
    require(tuple(partition) == canonicalize(partition), "canonical handoff labels")
    require(partition == optimum["partition"], "lexicographic optimal handoff tie")
    outputs = row["outputs"]
    require(type(outputs) is list and len(outputs) == capacity, "handoff decoder capacity")
    require(all(type(values) is list and len(values) == width and
                all(integer(x) and x in (0, 1) for x in values) for values in outputs),
            "handoff decoder domain")
    score = 0
    for word, code in enumerate(partition):
        targets = tuple(int(x) for x in format(word, "0" + str(width) + "b"))
        score += sum(a == b for a, b in zip(outputs[code], targets))
    require(score == optimum["score"], "handoff decoder achieves optimum")
    require(outputs == partition_decoder(partition, width, capacity, "query"),
            "handoff decoder majority and zero tie rule")
    return {"kind": "handoff", "width": width, "capacity": capacity,
            "score": score, "total": optimum["total"],
            "partition_count": optimum["partitions"],
            "labeled_assignments": optimum["labeled_assignments"]}


def check_constructive(row):
    label, controller = row["label"], row["controller"]
    checked = check_evaluation(controller, row["evaluation"])
    check_storage(controller, row["storage"])
    width, capacity = controller["width"], controller["capacity"]
    require(width in CONSTRUCTIVE_WIDTHS, "constructive width coverage")
    if label.startswith("window/"):
        retained = capacity.bit_length() - 1
        require(capacity == 2 ** retained and 0 <= retained <= width, "window memory bits")
        require(label == "window/J%d/B%d" % (width, retained), "window label")
        require(controller["task"] == "query", "window query task")
        require(checked["score"] == (width + retained) * (2 ** (width - 1)),
                "window analytic value")
        for phase, mapping in enumerate(checked["state_maps"]):
            symbols = [prefix % (2 ** min(phase, retained)) for prefix in range(2 ** phase)]
            check_statistic_partition(mapping, symbols)
        for path in checked["paths"]:
            require(path["outputs"][width - retained:] == path["targets"][width - retained:],
                    "retained coordinates reconstructed")
        proof = "suffix_statistic_and_complete_replay"
        if retained == width:
            verify_injective_decoding(controller)
            proof = "injective_full_register_matches_counting_bound"
    elif label == "parity/constant/J%d" % width:
        require(controller["task"] == "parity" and capacity == 1, "constant parity contract")
        require(checked["score"] == 2 ** (width - 1), "constant parity analytic value")
        proof = "balanced_parity_classes_under_one_code"
    else:
        require(label == "parity/xor/J%d" % width, "constructive label")
        require(controller["task"] == "parity" and capacity == 2, "xor parity contract")
        require(checked["score"] == 2 ** width, "xor parity exact upper bound")
        for phase, mapping in enumerate(checked["state_maps"]):
            check_statistic_partition(mapping, [bin(prefix).count("1") % 2
                                                 for prefix in range(2 ** phase)])
        verify_parity_decoding(controller)
        proof = "parity_statistic_matches_two_label_lower_bound"
    return {"kind": "constructive", "label": label, "width": width, "capacity": capacity,
            "score": checked["score"], "total": checked["total"], "proof": proof,
            "verified_words": checked["verified_words"],
            "verified_decisions": checked["verified_decisions"],
            "verified_updates": checked["verified_updates"]}


def audit(raw):
    """Validate every declared finite case using independent finite procedures."""
    require(raw["schema"] == "MIC-18/online-memory/v1", "report schema")
    base = Path(__file__).resolve().parent
    require(set(raw["source_sha256"]) == SOURCE_FILES, "exact provenance source coverage")
    for name, digest in raw["source_sha256"].items():
        require(digest == source_hash(base / name), "source hash mismatch: " + name)
    require(raw["protocol_sha256"] == source_hash(base / "protocol.json"), "frozen protocol hash")
    require(raw["protocol_sha256"] == FROZEN_PROTOCOL_SHA256, "pinned preregistered protocol")
    require(raw["protocol_sha256"] == raw["source_sha256"]["protocol.json"],
            "consistent protocol provenance")

    exact = raw["exact_search"]
    require(type(exact) is list and len(exact) == len(EXACT_CASES), "exact case cardinality")
    require({(row["width"], row["capacity"]) for row in exact} == EXACT_CASES,
            "exact case grid")
    rows = []
    for row in exact:
        width, capacity = row["width"], row["capacity"]
        require(row["task"] == "query", "exact task coverage")
        controller = row["controller"]
        require((controller["width"], controller["capacity"], controller["task"]) ==
                (width, capacity, "query"), "search/controller agreement")
        require(row["certified_optimal"] is True, "declared exact optimality")
        require(row["search_method"] == "canonical-causal-partitions", "declared producer search")
        checked = check_evaluation(controller, row["evaluation"])
        check_storage(controller, row["storage"])
        optimum = labeled_optimum(width, capacity)
        require(row["score"] == checked["score"] == optimum["score"],
                "independent labeled search optimum")
        require(row["total"] == checked["total"] == optimum["total"], "search exact denominator")
        require(row["reachable_partition_counts"] == optimum["reachable_partition_counts"],
                "independent reachable partition coverage")
        require(row["final_partition_count"] == optimum["final_partitions"],
                "independent final partition count")
        require(list(canonicalize(checked["state_maps"][-1])) == optimum["partition"],
                "lexicographic optimal online tie")
        require(controller["outputs"] == partition_decoder(checked["state_maps"][-1],
                                                            width, capacity, "query"),
                "online decoder majority and zero tie rule")
        rows.append({"kind": "exact", "width": width, "capacity": capacity,
                     "score": optimum["score"], "total": optimum["total"],
                     "reachable_partition_counts": optimum["reachable_partition_counts"],
                     "labeled_tables_evaluated": optimum["labeled_tables_evaluated"],
                     "verified_words": checked["verified_words"],
                     "verified_decisions": checked["verified_decisions"],
                     "verified_updates": checked["verified_updates"]})

    handoff = raw["handoff"]
    require(type(handoff) is list and len(handoff) == len(HANDOFF_CASES), "handoff case cardinality")
    require({(row["width"], row["capacity"]) for row in handoff} == HANDOFF_CASES,
            "handoff case grid")
    rows.extend(check_handoff(row) for row in handoff)

    constructive = raw["constructive"]
    labels = {"window/J%d/B%d" % (width, retained) for width in CONSTRUCTIVE_WIDTHS
              for retained in range(width + 1)} | {
                  "parity/%s/J%d" % (method, width) for width in CONSTRUCTIVE_WIDTHS
                  for method in ("constant", "xor")}
    require(type(constructive) is list and len(constructive) == len(labels),
            "constructive case cardinality")
    require({row["label"] for row in constructive} == labels, "constructive case coverage")
    rows.extend(check_constructive(row) for row in constructive)

    online = labeled_optimum(3, 2)
    oracle = handoff_optimum(3, 2)
    online_fraction, handoff_fraction = (Fraction(online["score"], online["total"]),
                                        Fraction(oracle["score"], oracle["total"]))
    gap = handoff_fraction - online_fraction
    primary = {"width": 3, "capacity": 2, "online_score": online["score"],
               "online_total": online["total"], "handoff_score": oracle["score"],
               "handoff_total": oracle["total"], "online_fraction": str(online_fraction),
               "handoff_fraction": str(handoff_fraction),
               "gap_handoff_minus_online": str(gap),
               "status": "POSITIVE_EXACT_GAP" if gap > 0 else "NO_EXACT_GAP"}
    require(raw["primary"] == primary, "independent primary result")
    expected_summary = {
        "evidence_class": "exact finite domain", "task_families": 2,
        "independent_model_roots": 0, "exact_cases": len(exact),
        "handoff_cases": len(handoff), "constructive_cases": len(constructive),
        "fits": 0, "empirical_gate": "REDESIGN_OR_PILOT_ONLY",
        "query_zero_error_lower_bound_codes": "2**J",
        "parity_zero_error_lower_bound_codes": 2, "trained_models_tested": 0,
    }
    require(raw["summary"] == expected_summary, "finite evidence and scope summary")
    return {"schema": "MIC-18/audit/v1", "status": "PASS", "primary": primary,
            "exact_cases": len(exact), "handoff_cases": len(handoff),
            "constructive_cases": len(constructive),
            "verified_words": sum(row.get("verified_words", 0) for row in rows),
            "verified_decisions": sum(row.get("verified_decisions", 0) for row in rows),
            "verified_updates": sum(row.get("verified_updates", 0) for row in rows),
            "labeled_transition_tables": sum(sum(row.get("labeled_tables_evaluated", ()))
                                             for row in rows),
            "handoff_labeled_assignments": sum(row.get("labeled_assignments", 0) for row in rows),
            "independence": "direct word replay; all labeled transition assignments; full labeled handoff assignments",
            "query_lower_bound": "perfect delayed coordinate decoding requires at least 2**J retained labels",
            "parity_lower_bound": "perfect parity decoding requires two retained labels",
            "source_sha256": dict(raw["source_sha256"]),
            "protocol_sha256": raw["protocol_sha256"], "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("results.json"))
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("audit_results.json"))
    args = parser.parse_args()
    contents = args.input.read_bytes()
    result = audit(json.loads(contents))
    result["input_sha256"] = hashlib.sha256(contents).hexdigest()
    result["audit_source_sha256"] = source_hash(Path(__file__))
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

"""COL-EVAL-01: independent full-step replay and adversarial boundary checks."""
from fractions import Fraction
from math import gcd

import pytest

from spiral_ln.evaluation_collatz_basin import (
    enumerate_core, odd_step, parameter_split, parameter_summary,
    partition_ceiling, quotient_labels, score_predictions, summarize, validate_parameter,
)


def slow_odd_step(n, d):
    x = 3 * n + d if n % 4 == 1 else n + d
    count = 0
    while x % 2 == 0:
        x //= 2
        count += 1
    return x, count, int(n % 4 == 1)


@pytest.mark.parametrize("d", [0, -3, 3, 9, 21, 2, 4, 5.0, True])
def test_parameter_contract(d):
    with pytest.raises(ValueError):
        validate_parameter(d)


def test_singleton_and_all_core_orbits():
    for d in range(1, 258, 4):
        if gcd(d, 6) != 1:
            continue
        core = enumerate_core(d)
        for start in core.states:
            x, seen, path = start, {}, []
            while x not in seen:
                seen[x] = len(path)
                path.append(x)
                assert odd_step(x, d) == slow_odd_step(x, d)
                x = slow_odd_step(x, d)[0]
            assert core.basin[start] == min(path[seen[x]:])
            assert core.depth[start] == seen[x]
    one = enumerate_core(1)
    assert one.cycles[0].period == 3
    assert one.basin == {1: 1}


def test_quotient_orbits_against_direct_group_breadth_first_search():
    for d in [1, 5, 13, 17, 25, 29, 49, 65, 73, 85, 97]:
        labels = quotient_labels(d)
        for n in range(d):
            reached, todo = {n}, [n]
            while todo:
                x = todo.pop()
                for y in (2 * x % d, 3 * x % d):
                    if y not in reached:
                        reached.add(y)
                        todo.append(y)
            assert labels[n] == min(reached)


def test_ceiling_with_unbalanced_collisions_and_refinement():
    labels, targets = [0, 0, 0, 1, 1], [7, 7, 8, 8, 9]
    assert partition_ceiling(labels, targets) == Fraction(3, 5)
    assert partition_ceiling(targets, targets) == 1
    assert partition_ceiling([0] * 5, targets) == Fraction(2, 5)
    with pytest.raises(ValueError):
        partition_ceiling([], [])
    with pytest.raises(ValueError):
        partition_ceiling([1], [1, 2])


def test_real_collision_witness_and_branch_congruence():
    found = False
    for d in range(5, 258, 4):
        if gcd(d, 6) != 1:
            continue
        row = parameter_summary(d)
        assert Fraction(row["constant_ceiling"]) <= Fraction(row["gcd_ceiling"])
        assert Fraction(row["gcd_ceiling"]) <= Fraction(row["quotient_ceiling"]) <= 1
        for witness in row["collision_witnesses"]:
            found = True
            labels, core = quotient_labels(d), enumerate_core(d)
            a, b = witness["seeds"]
            assert labels[a % d] == labels[b % d]
            assert core.basin[a] != core.basin[b]
    assert found


def test_allocation_and_input_boundaries():
    with pytest.raises(ValueError):
        enumerate_core(1001, max_vertices=500)
    with pytest.raises(ValueError):
        quotient_labels(1001, max_residues=1000)
    for n in [0, -1, 2, True, 1.0]:
        with pytest.raises(ValueError):
            odd_step(n, 5)


def test_split_is_root_level_and_summary_keeps_root_denominator():
    for d in [1, 5, 13, 29, 73]:
        assert parameter_split(d) in {"train", "dev", "holdout"}
    rows = [parameter_summary(5), parameter_summary(13)]
    report = summarize(rows)
    assert report["n_parameter_roots"] == 2
    assert report["n_cases"] == 10
    assert report["scores"]["basin_oracle"] == {"macro": "1", "micro": "1"}
    with pytest.raises(ValueError):
        summarize([rows[0], rows[0]])


def test_export_separates_gold_and_preserves_root_custody(tmp_path):
    import importlib.util
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "scripts/export_collatz_basin.py"
    spec = importlib.util.spec_from_file_location("col_export", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.export(257, tmp_path, ("train", "dev"))
    roots = {}
    normalized_paths = {}
    for split in ("train", "dev"):
        prompts = [json.loads(line) for line in (tmp_path / f"{split}.prompts.jsonl").read_text().splitlines()]
        gold = [json.loads(line) for line in (tmp_path / f"{split}.gold.jsonl").read_text().splitlines()]
        assert {p["id"] for p in prompts} == {g["id"] for g in gold}
        assert all(set(p["input"]) == {"d", "n"} for p in prompts)
        assert all("cycle_minimum" not in p for p in prompts)
        assert all(gcd(p["input"]["n"], p["input"]["d"]) == 1 for p in prompts)
        assert all(g["gcd"] == 1 for g in gold)
        paths = set()
        for prompt in prompts:
            d, n = prompt["input"]["d"], prompt["input"]["n"]
            scale = gcd(n, d)
            seen, path = set(), []
            while n not in seen:
                seen.add(n)
                path.append(n // scale)
                n = slow_odd_step(n, d)[0]
            path.append(n // scale)
            paths.add((d // scale, tuple(path)))
        normalized_paths[split] = paths
        oracle = [{"id": row["id"], "cycle_minimum": row["cycle_minimum"]} for row in gold]
        scored = score_predictions(gold, oracle)
        assert scored["n_cases"] == result["cases"][split]
        assert scored["parameter_macro_accuracy"] == scored["state_micro_accuracy"] == "1"
        roots[split] = {p["root_id"] for p in prompts}
    assert roots["train"].isdisjoint(roots["dev"])
    assert normalized_paths["train"].isdisjoint(normalized_paths["dev"])
    assert result["holdout_exported"] is False
    assert result["unit_seeds_only"] is True
    assert result["schema"] == "COL-EVAL-01/export/v2"
    with pytest.raises(ValueError):
        module.export(257, tmp_path, ("holdout",))


def test_export_excludes_d1_d5_scaled_cross_split_witness(tmp_path):
    import importlib.util
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "scripts/export_collatz_basin.py"
    spec = importlib.util.spec_from_file_location("col_export_scaled", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert parameter_split(1) == "train" and parameter_split(5) == "dev"
    assert odd_step(1, 1)[0] == 1
    assert odd_step(5, 5)[0] == 5
    assert enumerate_core(1).basin[1] == 1
    assert enumerate_core(5).basin[5] == 5
    result = module.export(5, tmp_path, ("train", "dev"))
    train = [json.loads(line) for line in (tmp_path / "train.prompts.jsonl").read_text().splitlines()]
    dev = [json.loads(line) for line in (tmp_path / "dev.prompts.jsonl").read_text().splitlines()]
    assert [p["id"] for p in train] == ["COL:1:1"]
    assert [p["id"] for p in dev] == ["COL:5:1", "COL:5:3"]
    assert result["cases"] == {"dev": 2, "train": 1}


def test_candidate_score_uses_parameter_and_state_denominators():
    gold = [{"id": f"COL:{d}:{n}", "cycle_minimum": core.basin[n]}
            for d in (5, 13) for core in [enumerate_core(d)] for n in core.states]
    full = score_predictions(gold, gold)
    assert full["parameter_macro_accuracy"] == full["state_micro_accuracy"] == "1"
    partial = score_predictions(gold, gold[:3])
    assert partial["parameter_macro_accuracy"] == "1/2"
    assert partial["state_micro_accuracy"] == "3/10"
    assert partial["coverage"] == "3/10"
    assert partial["selective_accuracy"] == "1"
    empty = score_predictions(gold, [])
    assert empty["state_micro_accuracy"] == "0"
    assert empty["selective_accuracy"] is None
    assert empty["n_abstained"] == 10


def test_candidate_score_rejects_duplicate_unknown_and_ill_typed_predictions():
    gold = [{"id": "COL:5:1", "cycle_minimum": 1}]
    for bad in [gold * 2, [{"id": "COL:13:1", "cycle_minimum": 1}],
                [{"id": "COL:5:1", "cycle_minimum": True}],
                [{"id": "COL:5:1", "cycle_minimum": 2}],
                [{"id": "COL:5:1", "cycle_minimum": 1, "extra": 0}]]:
        with pytest.raises(ValueError):
            score_predictions(gold, bad)
    for bad_gold in [[], gold * 2, [{"id": "COL:5:2", "cycle_minimum": 1}],
                     [{"id": "COL:5:1", "cycle_minimum": True}]]:
        with pytest.raises(ValueError):
            score_predictions(bad_gold, [])
    abstention = score_predictions(gold, [{"id": "COL:5:1", "cycle_minimum": None}])
    assert abstention["coverage"] == "0"

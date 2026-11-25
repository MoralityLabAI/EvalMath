"""COL-EVAL-01: independent full-step replay and adversarial boundary checks."""
from fractions import Fraction
from math import gcd

import pytest

from spiral_ln.evaluation_collatz_basin import (
    enumerate_core, odd_step, parameter_split, parameter_summary,
    partition_ceiling, quotient_labels, summarize, validate_parameter,
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
    for split in ("train", "dev"):
        prompts = [json.loads(line) for line in (tmp_path / f"{split}.prompts.jsonl").read_text().splitlines()]
        gold = [json.loads(line) for line in (tmp_path / f"{split}.gold.jsonl").read_text().splitlines()]
        assert {p["id"] for p in prompts} == {g["id"] for g in gold}
        assert all(set(p["input"]) == {"d", "n"} for p in prompts)
        assert all("cycle_minimum" not in p for p in prompts)
        roots[split] = {p["root_id"] for p in prompts}
    assert roots["train"].isdisjoint(roots["dev"])
    assert result["holdout_exported"] is False
    with pytest.raises(ValueError):
        module.export(257, tmp_path, ("holdout",))

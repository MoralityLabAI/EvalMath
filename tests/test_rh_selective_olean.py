"""Offline tests for the selective published-cache manifest contract."""
import json
import pytest

from spiral_ln.rh_selective_olean import selected_rows, cache_map, assure_disk


def test_selects_exact_subset_in_stable_order():
    rows = [["B", "b" * 16, "c" * 16 + ".ltar", "d" * 64],
            ["A", "a" * 16, "e" * 16 + ".ltar", "f" * 64]]
    chosen = selected_rows(rows, {"A"})
    assert chosen[0][0] == "A"
    assert cache_map(chosen).splitlines() == [
        json.dumps("2026-03-17"),
        json.dumps([chosen[0][1], chosen[0][2]], separators=(",", ":")),
    ]


def test_missing_or_duplicate_cache_rows_fail():
    a = ["A", "a" * 16, "b" * 16 + ".ltar", "c" * 64]
    with pytest.raises(ValueError, match="missing compiled"):
        selected_rows([a], {"B"})
    with pytest.raises(ValueError, match="duplicate"):
        selected_rows([a, a], {"A"})


def test_disk_and_count_guards(tmp_path):
    assert assure_disk(tmp_path, 2, max_modules=3, min_free_gib=0) > 0
    with pytest.raises(ValueError, match="exceeds"):
        assure_disk(tmp_path, 9, max_modules=3, min_free_gib=0)
    with pytest.raises(ValueError, match="required"):
        assure_disk(tmp_path, 1, max_modules=2, min_free_gib=10**6)

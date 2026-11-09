"""Reproducible finite cubic-graph scan checks."""
from spiral_ln.game_space_phase import scan


def test_small_cubic_phase_scan_structure():
    report = scan(max_vertices=10)
    assert report["schema"] == "UGCS-02-scan.1"
    rows = report["rows"]
    assert len(rows) == 15
    assert {r["graph"] for r in rows} == {"K33", "Cube", "Petersen"}
    assert all(r["m"] * 2 == r["n"] * 3 for r in rows)
    for graph in ("K33", "Cube", "Petersen"):
        sample = [r for r in rows if r["graph"] == graph]
        values = [r["holonomy_rate_per_edge"] for r in sample]
        assert values == sorted(values)
        assert all(0 <= v for v in values)


def test_cubic_phase_scan_exact_reproducibility():
    assert scan(max_vertices=8) == scan(max_vertices=8)
    assert scan(max_vertices=6)["rows"][2]["balanced_probability"] == "27/53"

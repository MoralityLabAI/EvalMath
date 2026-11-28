"""Audit CFH-09 receipt counts and Bellman-regret telescoping."""
from collections import defaultdict
from pathlib import Path
import gzip
import json
import sys


def audit(receipt):
    rows, decisions = defaultdict(list), defaultdict(list)
    for r in receipt["rows"]:
        rows[r["deck"], r["cap"], r["arm"], r["seed"]].append(r)
    for r in receipt["decisions"]:
        decisions[r["deck"], r["cap"], r["arm"], r["seed"]].append(r)
    for (deck, cap, arm, seed), rr in rows.items():
        optimum = sum(r["hit"] for r in rows[deck, cap, "exact", 0])
        actual = sum(r["hit"] for r in rr)
        gap = 0
        for d in decisions[deck, cap, arm, seed]:
            v, q = d["n"] * d["optimal"], d["n"] * d["value"]
            assert abs(v - round(v)) < 1e-5 and abs(q - round(q)) < 1e-5
            gap += round(v) - round(q)
        assert gap == optimum - actual
        assert len(rr) == 90 and len({r["hidden"] for r in rr}) == 90
        assert all(r["cost"] <= cap and r["queries"] <= 2 for r in rr)
        assert all(r["hit"] == (r["remaining"] == 1) for r in rr)
    return len(rows)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    raw = path.read_bytes()
    receipt = json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)
    print(audit(receipt), "policy/deck/cap regret and budget checks passed")

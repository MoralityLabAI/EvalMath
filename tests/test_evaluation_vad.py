"""Recompute the VAD-01A receipt, plus exact cost and split controls."""
import json
from pathlib import Path
from spiral_ln.evaluation_vad import exact_check, proof_cost, run, weight


def test_independent_cost_oracle():
    assert exact_check() == 4096


def test_savings_identity():
    for a in range(64):
        for t in range(64):
            delta = 2 * max(0, 2 * weight(t & a) - weight(a) - 1)
            assert proof_cost(t) - proof_cost(t, a) == delta


def test_receipt():
    expected = json.loads((Path(__file__).resolve().parents[1] /
                           "output/verified_abstraction/vad_01a.json").read_text())
    actual = run()
    assert len(actual.pop("records")) == 480
    assert actual == expected

import json
from pathlib import Path
from spiral_ln.evaluation_vad_composition import build, cost, exhaustive, family, run, select


def test_independent_oracles():
    assert exhaustive() == (9216, 576)


def test_synergy_and_construction():
    assert cost(7) == cost(7, (25,)) == cost(7, (30,)) == 6
    assert cost(7, (25, 30)) == 4
    assert build((7, 15)) == 10


def test_selection_and_transfer():
    for regime in ('shared', 'shifted', 'null'):
        pool, dev, held, pair = family(0, regime)
        assert not set(dev) & set(held)
        assert select(pool, dev, 'greedy') == ((), 102)
        assert select(pool, dev, 'joint') == (pair, 672)
        assert build(pair) == 20


def test_receipt():
    path = Path(__file__).resolve().parents[1] / 'output/verified_abstraction/vad_02.json'
    expected = json.loads(path.read_text())
    actual = run()
    assert len(actual.pop('records')) == 768
    assert actual == expected

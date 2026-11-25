from fractions import Fraction
from pathlib import Path
import runpy

from spiral_ln.evaluation_instrument_transfer import optimal_search, binary_query

M = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'gyms/MathematicalInstrumentTransfer/selector.py'))


def test_selector_integer_teacher_matches_fraction():
    for family in ('random','tree','overlap','stress'):
        for seed in (9000,9001):
            spec = M['world'](seed, family)
            w,masks,costs,b = spec
            e = M['Search'](spec)
            qs = [binary_query([(mask >> i) & 1 for i in range(len(w))],cost) for mask,cost in zip(masks,costs)]
            assert Fraction(e.value(*e.start),sum(w)) == optimal_search(w,qs,b)


def test_selector_feature_aliasing():
    spec = ((1,1,2,3,2,3,3,2,1,2,2,1),(900,3605,1123,4092),(1,1,1,1),4)
    e = M['Search'](spec)
    a,b = ('q',1),('q',2)
    assert e.features(e.start,a) == e.features(e.start,b)
    assert e.q(e.start,a) == 19
    assert e.q(e.start,b) == 18
    assert e.mass(e.full) == 23
    assert [act for act in e.actions(*e.start) if e.q(e.start,act) == e.value(*e.start)] == [a]

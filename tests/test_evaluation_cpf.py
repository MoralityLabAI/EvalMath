from fractions import Fraction as F
from itertools import product
import pytest
from spiral_ln.evaluation_cpf import bounds, coupling, residual, optimal, fixed, example


def brute(weights, rows, budget):
    """Enumerate all deterministic policy leaf-survivor sets, without value DP."""
    def leaves(worlds, actions, depth):
        yield frozenset(worlds)
        if depth == 0 or not worlds:
            return
        for q in actions:
            labels = sorted({rows[i][q] for i in worlds} - {"reject"})
            kids = [tuple(i for i in worlds if rows[i][q] == label) for label in labels]
            remain = tuple(j for j in actions if j != q)
            for choices in product(*(leaves(k, remain, depth-1) for k in kids)):
                yield frozenset().union(*choices)
    return min(sum((weights[i] for i in survivors), F(0)) for survivors in
               leaves(tuple(range(len(rows))), tuple(range(len(rows[0]))), budget))


def test_couplings():
    for counts in product(range(9), repeat=3):
        x,y,z = counts
        if x+y+z > 8:
            continue
        a,b,r = F(x+y,8), F(x+z,8), F(x,8)
        assert coupling(a,b,r) == (r,F(y,8),F(z,8),F(8-x-y-z,8))
        lo,hi = bounds(a,b)
        for endpoint in (lo,hi):
            assert min(coupling(a,b,endpoint)) >= 0
    with pytest.raises(ValueError):
        coupling(F(1,20),F(1,20),F(1,10))
    with pytest.raises(ValueError):
        bounds(0.05, F(1,20))


def test_example():
    w, rows = example()
    assert fixed(w,rows,2) == F(3,100)
    assert optimal(w,rows,2) == brute(w,rows,2) == F(1,50)
    assert optimal(w,rows,0) == F(1,20)
    assert residual(F(1,20), F(2,5)) == F(1,50)


def test_exhaustive_policies():
    for cells in product(("reject", "a", "b"), repeat=6):
        rows = (cells[:3],cells[3:])
        w = (F(1,10), F(1,5))
        for k in range(3):
            assert optimal(w,rows,k) == brute(w,rows,k) <= fixed(w,rows,k)

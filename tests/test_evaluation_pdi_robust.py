from fractions import Fraction as F
import pytest
from spiral_ln.evaluation_pdi_robust import (hazard_audit, hazard_bound, projected_posterior,
    robust_frontier, robust_mix, source_law, transfer_profile)


def test_robust_mixture():
    p = (F(1,2), F(1,2))
    a = ((0, 1, F(1,5), 1), (0, F(1,5), 0, 1))
    rows = robust_frontier(((p, a), (p, a[::-1])), [(1, (1,))], 1)
    z, v, mix = robust_mix(rows, F(1,20))
    assert (z, v) == (F(3,10), (F(1,20), F(3,10))*2)
    assert len(mix) == 2 and {w for w, _ in mix} == {F(1,2)}
    assert all(tree[0] == 'audit' for _, tree in mix)


def test_invalid_topology():
    p = (F(1,2), F(1,2))
    with pytest.raises(ValueError):
        robust_frontier(((p, ((0, 1, 0, 1),)), (p, ((0, 1, 0, 2),))), [(1, (1,))], 1)
    with pytest.raises(ValueError):
        robust_frontier((), [(1, (1,))], 1)


def test_hazard_prepeek():
    assert hazard_bound([F(1,5), F(1,3), F(1,4)]) == F(3,5)
    assert hazard_audit([(F(1,2), ((0, 1),)), (F(1,2), ((1, 1),))], [F(1,2)]) == ((1,), 1, False)


def test_revocation():
    law = source_law(F(3,4))
    assert projected_posterior(law, (0,1), (0,1))[1] == F(1,2)
    assert projected_posterior(law, (1,), (1,))[1] == F(3,4)
    assert projected_posterior(law, (1,2), (1,0))[1] == F(1,2)
    revised = source_law(F(1,2), F(3,4))
    assert projected_posterior(revised, (1,2), (1,0))[1] == F(3,4)


def test_transfer():
    shared, independent = transfer_profile(8, 3, 1, 11, F(9,10), 1, F(9,10), F(1,10))
    assert shared[:2] == (8, F(162,25))
    assert independent[:2] == (2, F(81,50))
    assert shared[2][-1] == F(1,100)
    assert independent[2][-1] == F(1,10000)
    s, i = transfer_profile(2, 3, 1, 8, F(9,10), 1, F(9,10), F(1,10))
    assert s[:2] == i[:2] and s[2][-1] == 100*i[2][-1]

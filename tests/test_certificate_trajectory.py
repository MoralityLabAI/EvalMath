from fractions import Fraction as F
import pytest
from spiral_ln.certificate_trajectory import instance, recover, verify, distance, run


def test_full_grid():
    rows=run()
    assert len(rows)==18
    assert sum(r['local_K8'] for r in rows)==9
    assert all(r['certified'] and r['invalid_rejected'] for r in rows)


def test_triangle_boundary_and_corruption():
    rows,c,vs,s,t=instance(1,101)
    x,w,_=recover(rows,c)
    assert distance(rows,vs,s,s)==0
    assert distance(rows,vs,s,t)==2
    assert verify(rows,c,x,w)
    assert not verify(rows,c,x,{**w,len(rows):F(1)})
    assert not verify(rows,c,x,{})
    with pytest.raises(ValueError):
        instance(0)

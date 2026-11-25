from fractions import Fraction as F
from spiral_ln.evaluation_math_controller import bayes, blind, alpha_oracle, fixture


def test_strict_history_advantage():
    r,c,p=fixture(2)
    v,solve=bayes(r,c,p,4)
    assert v==alpha_oracle(r,c,p,4)==F(205,256)
    assert blind(r,c,p,4)==F(199,256)
    assert solve(0,4,p)[1]==0
    assert solve(0,3,(F(1,8),F(3,8)))[1]==1
    assert solve(1,2,(F(3,32),F(3,32)))[1]==0
    assert solve(1,2,(F(1,32),F(9,32)))[1]==1


def test_retrieval_cost():
    r,c,p=fixture(1)
    assert bayes(r,c,p,4)[0]==F(219,256)
    r,c,p=fixture(2)
    assert bayes(r,c,p,4)[0]==F(205,256)


def test_boundaries():
    p=(F(1),F(0))
    assert bayes((),(),p,0)[0]==alpha_oracle((),(),p,0)==blind((),(),p,0)==1
    r,c,_=fixture(2)
    for b in (0,1):
        assert bayes(r,c,p,b)[0]==alpha_oracle(r,c,p,b)==blind(r,c,p,b)==0
    assert bayes(r,c,p,4)[0]==blind(r,c,p,4)

from fractions import Fraction as F
from spiral_ln.evaluation_math_controller import fixture, blind
from spiral_ln.evaluation_math_memory import (
    optimal_tree,evaluate,compile_tree,decode,quantized_tree,posterior_regret_certificate,
    frontier,robust_two,coupling_bound,interval,envelope)


def test_minimal_bit():
    r,c,p=fixture(2); v,t=optimal_tree(r,c,p,4)
    start,table,width,bits=compile_tree(t,c,4)
    assert (width,bits)==(2,1) and decode(start,table,c,4)==t
    assert v==F(205,256) and blind(r,c,p,4)==F(199,256)
    assert sum(x*y for x,y in zip(p,evaluate(t,r,c,4,2)))==v


def test_quantization_and_regret():
    r,c,p=fixture(2); v,_=optimal_tree(r,c,p,4)
    for g,expected in [(1,F(155,256)),(2,F(199,256)),(3,v),(8,v)]:
        t=quantized_tree(r,c,p,4,g)
        assert sum(x*y for x,y in zip(p,evaluate(t,r,c,4,2)))==expected
        assert posterior_regret_certificate(t,r,c,p,4)==v-expected


def test_minimax():
    r,c,p=fixture(2); a=frontier(r,c,4,2); v,(u,w,t)=robust_two(a)
    assert max(map(min,a))==F(199,256) and v==F(205,256)
    assert tuple(t*x+(1-t)*y for x,y in zip(u,w))==(v,v)
    assert robust_two(((F(3,4),F(1,4)),(F(1,4),F(3,4))))[0]==F(1,2)
    assert coupling_bound(F(0),F(1,4),2)==F(7,16)


def test_confidence_and_envelope():
    assert interval(1,0,F(1,20),20)==(0,1)
    assert interval(1,1,F(1,20),20)==(0,1)
    t=(0,(0,None,None),(0,None,None)); costs=((1,),(1,))
    bounds={((),0):(F(1,4),F(3,4)),(((0,1),),0):(F(1,2),F(1)),(((0,0),),0):(0,1)}
    assert envelope(t,bounds,costs,2)==(F(1,8),F(3,4))

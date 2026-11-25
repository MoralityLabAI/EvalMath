from fractions import Fraction as F
from spiral_ln.evaluation_math_loss_envelope import completion,pair_exchange,concentrated_lower


def test_sharp_separation():
    balanced=(F(1,2),)*4; concentrated=(F(1,16),F(1),F(1),F(1))
    assert completion(balanced,8)==F(163,256)
    assert completion(concentrated,8)==concentrated_lower(4,8,F(1,16))==1-F(15,16)**5
    assert completion(balanced,4)==completion(concentrated,4)==F(1,16)


def test_pair_identity():
    ps=(F(1),F(1,4),F(1,3)); balanced=(F(1,2),F(1,2))
    for b in range(12):
        assert completion((*balanced,ps[2]),b)-completion(ps,b)==pair_exchange(ps,balanced,b)


def test_boundaries():
    assert completion((),0)==1
    assert completion((0,1),10)==0
    assert completion((1,1),1)==0 and completion((1,1),2)==1
    assert concentrated_lower(4,3,1)==0 and concentrated_lower(4,4,1)==1

from itertools import combinations,product
import pytest
from spiral_ln.hypergames_sparse_certificate import decode,first_unique_prefix
from spiral_ln.hypergames_observation_certificate import certify


def test_exact_decoder_matches_exhaustive_small_sparse_family():
    goals=[sum(1<<i for i in xs) for xs in combinations(range(5),2)]
    for truth in goals:
        for a,b in product(range(32),repeat=2):
            history=[(a,[(a&truth).bit_count()%2]),(b,[(b&truth).bit_count()%2])]
            compatible={p for p in goals if all((m&p).bit_count()%2==y[0] for m,y in history)}
            found=decode(5,1,history,2)
            assert (found['status']=='unique')==(len(compatible)==1)
            witnesses={sum(1<<i for i in xs) for xs in found['outputs'][0]['witness_supports']}
            assert witnesses<=compatible
            assert len(witnesses)==min(2,len(compatible))


def test_exact_weight_can_certify_beyond_linear_positive_units():
    history=[(0b011,[0])]
    assert not certify(3,1,history,None,2)['complete_support_forced']
    found=decode(3,1,history,2)
    assert found['status']=='unique'
    assert found['outputs'][0]['witness_supports']==[[0,1]]
    assert first_unique_prefix(3,1,history+[(0b100,[0])],2)==1


def test_cap_zero_weight_and_inconsistent_equations():
    assert decode(512,1,[],6)['status']=='unavailable_enumeration_cap'
    assert decode(1024,2,[],6)['status']=='unavailable_enumeration_cap'
    assert decode(6,1,[],6)['status']=='unique'
    assert first_unique_prefix(6,1,[],6)==0
    assert decode(3,1,[],0)['outputs'][0]['witness_supports']==[[]]
    assert decode(3,1,[(1,[0]),(1,[1])],1)['status']=='inconsistent'
    with pytest.raises(ValueError):decode(3,1,[(8,[0])],1)

from collections import defaultdict
from fractions import Fraction as F
from itertools import product

from spiral_ln.evaluation_ccf_scope import GATES, accuracy_interval, authorize, scope_ok


def scope_cases():
    L, B, S, K, D, T = ('euclidean_local_smoothing', 'bochner_riesz', 'spherical_restriction', 'kakeya_maximal', 'kakeya', 'stein_square')
    return [
        (L, dict(n=3,p=3,eps=F(1,100)),True), (L,dict(n=3,p=3,eps=0),False),
        (L,dict(n=3,p=2,eps=0),True), (L,dict(n=1,p=2,eps=0),False),
        (L,dict(n=3,p=None),False), (L,dict(n=3,p=3,schwartz=False),False),
        (L,dict(n=3,p=F(3,2)),False), (L,dict(n=3,p=2,eps=-1),False),
        (B,dict(n=3,p=1,delta=1),False), (B,dict(n=3,p=1,delta=F(101,100)),True),
        (B,dict(n=3,p=None,delta=1),False), (B,dict(n=3,p=None,delta=2),True),
        (B,dict(n=3,p=2,delta=0),False), (B,dict(n=3,p=2,delta=F(1,100)),True),
        (B,dict(n=3,p=2,delta=1,radius=0),False), (B,dict(n=3,p=2,delta=1,schwartz=False),False),
        (S,dict(n=3,a=2,b=4),False), (S,dict(n=3,a=2,b=F(401,100)),True),
        (S,dict(n=3,a=None,b=3),False), (S,dict(n=3,a=None,b=F(301,100)),True),
        (S,dict(n=3,a=1,b=100),False), (S,dict(n=3,a=2,b=5,memlp=False),False),
        (K,dict(n=3,eps=1,delta=1),True), (K,dict(n=3,eps=0,delta=1),False),
        (K,dict(n=3,eps=1,delta=0),False), (K,dict(n=3,eps=1,delta=2),False),
        (K,dict(n=3,eps=1,delta=1,memlp=False),False),
        (D,dict(n=3,kakeya=True),True), (D,dict(n=3,kakeya=False),False),
        (D,dict(n=1,kakeya=True),False),
        (T,dict(n=3,p=2,alpha=F(1,2)),False), (T,dict(n=3,p=2,alpha=F(51,100)),True),
        (T,dict(n=3,p=6,alpha=1),False), (T,dict(n=3,p=6,alpha=F(101,100)),True),
        (T,dict(n=3,p=None,alpha=5),False), (T,dict(n=3,p=2,alpha=1,schwartz=False),False),
        ('unknown',dict(n=3),False)]


def test_scope_boundaries():
    for endpoint, params, expected in scope_cases():
        assert scope_ok(endpoint, **params) == expected, (endpoint, params)


def gate_census():
    accepted = unsafe_legacy = 0
    for bits in product((False,True), repeat=len(GATES)):
        gates = dict(zip(GATES,bits))
        valid = sum(bits) == len(GATES)
        assert authorize(gates) == valid
        accepted += valid
        # Legacy proxy only checks an inference verdict and a kernel attestation.
        legacy = gates['accepted_verification'] and gates['solution_kernel_attested']
        unsafe_legacy += legacy and not valid
    for gate in GATES:
        g = dict.fromkeys(GATES,True)
        del g[gate]
        assert not authorize(g)
        g[gate] = 1
        assert not authorize(g)
    return 2**len(GATES), accepted, unsafe_legacy


def test_gate_census():
    assert gate_census() == (4096,1,1023)


def missingness_census():
    cells = defaultdict(set)
    for truth in product((0,1), repeat=5):
        for verified in product((0,1), repeat=5):
            cells[sum(verified),sum(y*v for y,v in zip(truth,verified))].add(sum(truth))
    for (v,k), totals in cells.items():
        lo,hi = accuracy_interval(5,v,k)
        assert totals == set(range(k,k+5-v+1))
        assert (lo,hi) == (F(min(totals),5),F(max(totals),5))
    return len(cells)


def test_missingness():
    assert missingness_census() == 21
    assert accuracy_interval(100,90,81) == (F(81,100),F(91,100))

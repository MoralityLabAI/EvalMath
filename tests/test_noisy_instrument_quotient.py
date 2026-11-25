from fractions import Fraction as F
from random import Random
from spiral_ln.evaluation_instrument_transfer import optimal_search
from spiral_ln.evaluation_noisy_instrument_quotient import Quotient, perturbation_bound, approximate_policy_value, canonical


def noisy(seed, n=5):
    r=Random(seed);w=tuple(r.randint(0,3) for _ in range(n));w=w if sum(w) else (1,)*n
    queries=[]
    for j in range(3):
        k=2+j%2;cols=[]
        for i in range(n):
            c=[r.randint(0,4) for _ in range(k)];c=c if sum(c) else [1]*k;cols.append(tuple(F(x,sum(c)) for x in c))
        queries.append((r.randint(1,2),tuple(zip(*cols))))
    return w,tuple(queries),r.randint(0,4)


def approximate(w, qs):
    # Coarsen by mixing each column with its nearest deterministic response.
    rounded=[]
    for cost,rows in qs:
        cols=[]
        for col in zip(*rows):
            winner=max(range(len(col)),key=lambda j:col[j]);cols.append(tuple(F(3,4)*x+F(int(j==winner),4) for j,x in enumerate(col)))
        rounded.append((cost,tuple(zip(*cols))))
    return tuple((x+1) if x else 0 for x in w),tuple(rounded)


def test_noisy_against_fraction_oracle():
    for i in range(48):
        w,q,b=noisy(7100+i)
        expected=optimal_search(w,q,b)
        assert Quotient(w,q,b).solve()==Quotient(w,q,b,dynamic=False).solve()==expected


def test_projection_merges():
    a=(F(1,2),F(1,2));b=(F(1,4),F(3,4));c=(F(1,3),F(2,3))
    assert canonical([(F(1), (a,), 2),(F(1),(a,),3),(F(0),(b,),7)])==((F(1),(a,),5),)
    # Two distinct signatures and priors become identical after response y=0.
    cols=((a,c),(b,c));w=(1,2)
    out=canonical([(F(w[i])*s[0][0],s[1:],1) for i,s in enumerate(cols)])
    assert out==((F(1,2),(c,),2),)


def test_coupling_bounds_and_policy_regret():
    for i in range(32):
        w,q,b=noisy(8500+i);z,r=approximate(w,q)
        truth=Quotient(w,q,b).solve();approx=Quotient(z,r,b).solve()
        bound,regret=perturbation_bound(w,q,z,r,b)
        actual,estimated=approximate_policy_value(w,q,z,r,b)
        assert estimated==approx
        assert abs(truth-approx)<=bound and abs(actual-estimated)<=bound
        assert 0<=truth-actual<=regret


def test_boundary_cost_and_prior():
    q=((1,((1,0),(0,1))),);r=((1,((0,1),(1,0))),)
    assert perturbation_bound((1,1),q,(1,1),r,0)==(0,0)
    assert perturbation_bound((1,1),q,(1,1),r,1)==(0,0)
    assert perturbation_bound((1,1),q,(1,1),r,2)==(1,1)
    assert perturbation_bound((1,1),q,(3,1),q,2)==(F(1,4),F(1,2))
    assert Quotient((1,1),q,2).solve()==1
    assert approximate_policy_value((1,1),q,(1,1),r,2)==(1,1) # direct guessing is also optimal


def test_regret_bound_sharp_prior_tie():
    w=(F(2,5),F(3,5));z=(F(1,2),F(1,2));b=1
    bound,regret=perturbation_bound(w,(),z,(),b)
    actual,estimated=approximate_policy_value(w,(),z,(),b)
    assert (bound,regret)==(F(1,10),F(1,5))
    assert (actual,estimated)==(F(2,5),F(1,2))
    assert Quotient(w,(),b).solve()-actual==regret


def repeated(seed):
    r=Random(seed);n=12
    types=[r.randrange(4) for _ in range(n)];w=tuple(1+t%2 for t in types)
    qs=[]
    for j in range(3):
        columns=[tuple(F(x,5) for x in (k,5-k)) for k in [r.randrange(1,5) for _ in range(4)]]
        qs.append((1,tuple(zip(*(columns[t] for t in types)))))
    return w,tuple(qs),4


def test_repeated_noisy_signatures():
    for seed in range(10):
        w,q,b=repeated(9100+seed)
        x=Quotient(w,q,b);y=Quotient(w,q,b,dynamic=False)
        assert x.solve()==y.solve()==optimal_search(w,q,b)


def channel_flip(seed):
    """Near-identical channels invert within-branch preference, without changing marginals."""
    rng=Random(seed);ids=list(range(8));rng.shuffle(ids)
    hi=F(rng.randrange(17,20),20);lo=hi-F(rng.randrange(1,3),20)
    # two high-confidence and two lower-confidence worlds in each side
    p=[F(0)]*8;z=[F(0)]*8
    for pos,i in enumerate(ids):
        x,y=(hi,lo) if pos%4<2 else (lo,hi)
        p[i],z[i]=(x,y) if pos<4 else (1-x,1-y)
    def query(a):return ((1,(tuple(a),tuple(1-x for x in a))),)
    return (1,)*8,query(p),query(z),3


def test_nonzero_channel_policy_regret():
    for seed in range(16):
        w,q,r,b=channel_flip(9900+seed)
        truth=Quotient(w,q,b).solve();approx=Quotient(w,r,b).solve()
        actual,estimated=approximate_policy_value(w,q,w,r,b)
        bound,regret=perturbation_bound(w,q,w,r,b)
        assert truth==approx==estimated and truth>actual
        assert truth-actual==bound/2<=regret

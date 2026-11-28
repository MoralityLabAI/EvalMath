"""Independent oracle, exact menu and optional numerical-controller checks."""
import sys
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
from random import Random
import pytest
p=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(p if p.is_dir() else Path(__file__).resolve().parent))
import verify_vad_meta as m
import verify_vad_stopping as a


def test_terminal_records():
    for name in m.MENU:
        act=m.action(name)
        for q in m.Q:
            d=m.distribution(m.W,q,act)
            old=a.evaluate(m.W,q,act)
            assert sum(d.values())==1
            assert sum(m.utility(rec)*w for rec,w in d.items())==old['net']
            assert sum(rec[0]*w for rec,w in d.items())==old['observations']
            assert sum(w for rec,w in d.items() if rec[2])==old['hit']


def test_small_envelopes_against_direct_history():
    rng=Random(8841)
    for i in range(12):
        data={}
        for name in ('a','b','c'):
            x,y=F(rng.randrange(5),4),F(rng.randrange(5),4)
            data[name]=(F(rng.randrange(-4,8)),F(rng.randrange(-4,8)),((x,y),(1-x,1-y)))
        hazard=F(i%3,4)
        @lru_cache(None)
        def brute(n,p):
            if n==0: return F(0)
            vals=[]
            for r0,r1,records in data.values():
                val=(1-p)*r0+p*r1
                for l0,l1 in records:
                    z=(1-p)*l0+p*l1
                    if z: val+=z*brute(n-1,hazard+(1-2*hazard)*p*l1/z)
                vals.append(val)
            return max(vals)
        h=((F(0),F(0),F(0),'stop'),)
        for n in range(1,4):
            h=m.envelope(m.backup_lines(h,data,hazard))
            for j in range(9): assert m.lookup(h,F(j,8))[0]==brute(n,F(j,8))


def test_exact_nominal_replay():
    r=m.run(); assert r['segments']==[1,5,187,3785] and r['checks']==123
    assert r['half'][2]['first']=='cut24'
    assert abs(float(F(r['half'][2]['optimal']))-37.879453268498885)<1e-10
    assert r['toy'][1]==dict(horizon=2,optimal='5',first='probe',myopic='2')


def test_grid_and_policy_expectation():
    np=pytest.importorskip('numpy')
    import verify_vad_meta_grid as g
    import verify_vad_meta_cert as c
    z=g.Grid(401,3); hs=m.exact(3)
    for h in (1,2,3):
        exact=float(m.lookup(hs[h],F(1,2))[0]); upper=float(z.values[h][200]); lower=c.value(z,.05,h,h)
        assert lower<=exact+1e-9<=upper+2e-9
        assert upper-lower<.003
    assert c.value(z,.05,3,3)>c.value(z,.05,3,1)+1.89
    # Independently recurse through the selected grid-policy memory states using rational mode probabilities.
    data=m.model(); names=z.names
    @lru_cache(None)
    def direct(h,i,mode):
        if not h:return F(0)
        name=names[int(np.argmax(z.q[h][:,i]))]; r0,r1,outs=data[name]; r=(r0,r1)[mode]; p=F(i,400)
        for l0,l1 in outs:
            mass=(l0,l1)[mode]; zz=(1-p)*l0+p*l1
            if mass:
                q=m.HAZARD+(1-2*m.HAZARD)*p*l1/zz if zz else m.HAZARD
                j=round(400*q)
                r+=mass*((1-m.HAZARD)*direct(h-1,j,mode)+m.HAZARD*direct(h-1,j,1-mode))
        return r
    exact=(direct(2,200,0)+direct(2,200,1))/2
    assert abs(c.value(z,.05,2,2)-float(exact))<1e-8

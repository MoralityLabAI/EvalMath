"""Replay VAD-07 and test exact stopping and matched-prefix claims."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from random import Random
import json,sys

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS if SCRIPTS.is_dir() else Path(__file__).resolve().parent))
import verify_vad_stopping as a
import verify_vad_robust_stop as b
import verify_vad_horn_stop as c
import verify_vad_horn as v


def test_explicit_small_history_tree():
    times=(2,4,25); p=(F(2,3),F(3,4),F(1,4))
    for seed in range(10):
        rng=Random(seed); w=a.prior(tuple(rng.randint(1,9) for _ in times))
        def rec(n,weights):
            z=sum(weights)
            if n==4 or not z: return F(0)
            value=sum(x*a.reward(t) for x,t in zip(weights,times) if t==n+1)
            for bit in (0,1):
                after=tuple(x*(q if bit else 1-q) if t>n+1 else 0 for x,q,t in zip(weights,p,times))
                value+=sum(after)*rec(n+1,after)
            return max(F(0),value/z-a.COST)
        assert a.bellman(w,p,times=times)(0,0)[0]==rec(0,w)


def test_matched_prefixes():
    for seed in range(12):
        for cue in ('easy','hard'):
            for cutoff in (16,48):
                f,r,h=c.family(seed,cue+str(cutoff)); f0,r0,h0=c.family(seed,cue+'_null')
                assert f==f0 and h[:cutoff]==h0[:cutoff]
                ix,_,_=v.cone(r,v.index(r),h[:cutoff]); ix0,_,_=v.cone(r0,v.index(r0),h0[:cutoff])
                assert [r[j] for j in ix]==[r0[j] for j in ix0]


def test_full_replays():
    for module,expected in ((a,'65add9511cbaa3650e84bff0cde4f9fc51d83fbec67402cfa518e6ae270838c0'),(b,'fdbb2ef1c12c3b1f785bc8e58e72808199628c440bf0599d82ea7e3c511485a9'),(c,'2706605324bb62e54ea40f37e2a3a1ba00cd491eff1b46173a3646bcd71beb56')):
        result=module.run()
        encoded=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
        assert sha256(encoded).hexdigest()==expected

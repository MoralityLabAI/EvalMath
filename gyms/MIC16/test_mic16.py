from mic16 import *
from audit16 import oracle,reset_rollout,nonanticipation
from copy import deepcopy
import pytest


def test_partition_and_safe_budget():
    for f in FAMILIES:
        p=Planner(make(f,16000))
        for m in (1,17,85,255):
            for b in (1,2,5):
                for a in range(len(p.actions)):
                    ts=p.transitions(0,m,b,a)
                    if ts:
                        assert sum(t[1].bit_count() for t in ts)==m.bit_count()
                        assert sum(t[1] for t in ts)==m
                        assert all(0<=t[2]<b for t in ts)
        p.choice.cache_clear()


def test_explicit_oracle():
    for f in FAMILIES:
        d=make(f,16001);p=Planner(d);q=oracle(d)
        for b in (4,6,8):
            for allow in (True,False):
                assert p.choice(0,FULL,b,b,'all' if allow else 'no_probe')[0]==q(frozenset(),tuple(range(WORLD)),b,allow)
        q.cache_clear();p.choice.cache_clear()


def test_paths_and_nonanticipation():
    for f in FAMILIES:
        d=make(f,16002);p=Planner(d);b=8
        for mode in MODES+('posterior_reset',):
            paths=[reset_rollout(p,w,b) if mode=='posterior_reset' else p.rollout(w,b,mode) for w in range(WORLD)]
            for w,r in enumerate(paths):assert check(d,w,b,mode,r)==r['reward']
            assert nonanticipation(paths,b,mode)>0
        p.choice.cache_clear()


def test_tamper_and_cost():
    d=make('mixed',16003);p=Planner(d);r=p.rollout(0,12,'bayes');assert r['path'];check(d,0,12,'bayes',r)
    for field in ('reward','remaining','posterior'):
        bad=deepcopy(r);bad[field]+=1
        with pytest.raises(AssertionError):check(d,0,12,'bayes',bad)
    bad=deepcopy(r);bad['path'][0][2][1]+=1
    with pytest.raises(AssertionError):check(d,0,12,'bayes',bad)
    p.choice.cache_clear()

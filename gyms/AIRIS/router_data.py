"""AIRIS-06 public histories, exact all-action labels and leakage-resistant splits."""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from math import gcd
import json
import random
from partial import SCHEDULES, SCALE, MODELS, channel, prior, observed, map_mass, branch_weights


def fingerprint(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def canonical(weights):
    d=gcd(*weights)
    if not d:
        raise ValueError("impossible public history")
    return tuple(w//d for w in weights)


def weights(history):
    w=prior(None)
    for a,y in history:
        l=dict(channel(a,"difference"))[observed(y,"difference")]
        w=canonical(tuple(x*v for x,v in zip(w,l)))
    return w


@lru_cache(None)
def teacher(w):
    # Exact Q numerators, common denominator. Teacher has no true-model ID.
    nums=tuple(sum(map_mass(p) for p in branch_weights(w,a,"difference")) for a in SCHEDULES)
    return nums,sum(w)*SCALE


def simulate_episode(rng,a,regime,target):
    u=rng.randrange(2)
    prev=0
    raw=[]
    for i,x in enumerate(a):
        if i and rng.randrange(4)<(0,1,2)[regime]:
            u^=1
        raw.append((x*(target&1))^(prev*((target>>1)&1))^u)
        prev=x
    return tuple(raw)


def sample(seed,n,lengths):
    rng=random.Random(seed)
    histories=set()
    for _ in range(n):
        regime,target=MODELS[rng.randrange(len(MODELS))]
        h=[]
        for _ in range(rng.choice(lengths)):
            a=rng.choice(SCHEDULES)
            h.append((a,simulate_episode(rng,a,regime,target)))
        histories.add(tuple(h))
    return sorted(histories)


def split(short_draws=12000,long_draws=4000):
    train,short,long=[],[],[]
    all_short=set()
    for h in sample(106,short_draws,(1,2,3)):
        w=weights(h)
        all_short.add(w)
        # Normalize exact likelihoods before grouping. Order permutations and
        # complement-equivalent raw observations cannot cross the group split.
        bucket=int(fingerprint(w)[:16],16)%5
        (short if bucket==0 else train).append(h)
    for h in sample(107,long_draws,(4,5,6)):
        if weights(h) not in all_short:
            long.append(h)
    if not all((train,short,long)):
        raise ValueError("empty split")
    groups=[{weights(h) for h in rows} for rows in (train,short,long)]
    if any(groups[i]&groups[j] for i in range(3) for j in range(i)):
        raise AssertionError("posterior equivalence leakage")
    return {"train":train,"short":short,"long":long}


def regret(h,action):
    nums,den=teacher(weights(h))
    return F(max(nums)-nums[action],den)


def oracle_last(h):
    nums,_=teacher(weights(h[-1:]))
    return max(range(len(nums)),key=nums.__getitem__)

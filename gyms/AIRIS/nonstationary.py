"""AIRIS-07: exact hidden-mechanism drift and chronology-sensitive acquisition."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations,product
from math import gcd
from partial import SCHEDULES,SCALE,channel,enumerate_channel

# Each event ID is (schedule index, observed two-bit temporal code).
EVENTS=tuple(range(32))
HAZARDS=(0,1,2,3)
PRIOR=(1,1,1,1)
OBS=tuple(product(range(2),repeat=2))
# Known observation noise p=1/4, unknown current two-tap action mechanism.
LIK=tuple(tuple(tuple(row[4:8]) for _,row in channel(a,"difference")) for a in SCHEDULES)


def norm(w):
    g=gcd(*w)
    if not g:
        raise ValueError("zero-likelihood history")
    return tuple(x//g for x in w)


def advance(w,k):
    if k not in HAZARDS:
        raise ValueError("unknown public drift parameter")
    total=sum(w)
    return tuple((16-4*k)*x+k*total for x in w)


@lru_cache(None)
def update(w,event,k):
    p=advance(w,k)
    if event is None:
        return norm(p)  # revoke evidence but keep its physical time slot
    if type(event) is not int or event not in EVENTS:
        raise ValueError("invalid event")
    a,o=divmod(event,4)
    return norm(tuple(x*l for x,l in zip(p,LIK[a][o])))


def posterior(history,k):
    w=PRIOR
    for event in history:
        w=update(w,event,k)
    return w


@lru_cache(None)
def values(w,k):
    p=advance(w,k)
    den=sum(p)*SCALE
    return tuple(F(sum(max(x*l for x,l in zip(p,row)) for row in table),den)
                 for table in LIK)


def optimal(q):
    return tuple(a for a,v in enumerate(q) if v==max(q))


def loss(q,a):
    return max(q)-q[a]


def orderless_floor(q,r):
    """Equal presentation weighting, shared action distribution, exact lower bound."""
    return min((loss(q,a)+loss(r,a))/2 for a in range(8))


def raw_event(event):
    a,o=divmod(event,4)
    d1,d2=OBS[o]
    # Canonical raw lift y0=0. This ancillary bit has no target information.
    return {"actions":list(SCHEDULES[a]),"observations":[0,d1,d1^d2]}


def pair_key(i,j,l):
    if not (i in EVENTS and j in EVENTS and l in EVENTS and i<j):
        raise ValueError("invalid canonical pair")
    return i,j,l


def pair_values(key,k):
    i,j,l=pair_key(*key)
    return values(posterior((i,j,l),k),k),values(posterior((j,i,l),k),k)


def census(k):
    """All first-two swaps sharing the last observation, not sampled worlds."""
    strict=[]
    total=0
    peak=F(0)
    floor_sum=F(0)
    witness=None
    for i,j in combinations(EVENTS,2):
        for l in EVENTS:
            key=(i,j,l)
            q,r=pair_values(key,k)
            floor=orderless_floor(q,r)
            total+=1
            if floor:
                strict.append(key)
                floor_sum+=floor
                if floor>peak:
                    peak=floor
                    witness=key
    return {"k":k,"pairs":total,"strict_pairs":len(strict),
            "balanced_all_pair_mean_floor":str(floor_sum/total),
            "strict_pair_mean_floor":str(floor_sum/len(strict)) if strict else "0",
            "max_floor":str(peak),"witness":witness},tuple(strict)


def literal_posterior(history,k):
    """Independent rational hidden-path enumeration, without filter recurrence."""
    masses=[F(0)]*4
    for path in product(range(4),repeat=len(history)+1):
        p=F(1,4)
        for old,new,event in zip(path,path[1:],history):
            p*=F(k,16)+(F(1)-F(k,4) if old==new else 0)
            if event is not None:
                a,o=divmod(event,4)
                p*=enumerate_channel(SCHEDULES[a],1,new,"difference").get(OBS[o],0)
        masses[path[-1]]+=p
    total=sum(masses)
    if not total:
        raise ValueError("impossible history")
    return tuple(x/total for x in masses)


def literal_values(history,k):
    p=literal_posterior(history,k)
    out=[]
    for a in SCHEDULES:
        v=F(0)
        for obs in OBS:
            candidates=[]
            for new in range(4):
                pred=sum(p[old]*(F(k,16)+(1-F(k,4) if old==new else 0))
                         for old in range(4))
                candidates.append(pred*enumerate_channel(a,1,new,"difference").get(obs,0))
            v+=max(candidates)
        out.append(v)
    return tuple(out)

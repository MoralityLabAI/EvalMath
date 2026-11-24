"""VAD-03A: exact synthetic bounded pair discovery using fixed-bit signatures."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
from random import Random
import json

D, MASK = 28, (1 << 28) - 1
SIZES, SEEDS, HORIZONS = (16, 32, 64), range(32), (128, 256, 512, 1024)
REGIMES = ('shared', 'shifted', 'null', 'noisy_shared')
METHODS, BUDGET = ('single', 'signature', 'random', 'exhaustive'), 8


def mask(bits):
    return sum(1 << i for i in bits)


def cost(t, lib=()):
    w = t.bit_count()
    if len(lib) == 0:
        return 2*w
    a = lib[0]
    w = min(w, 1+(t^a).bit_count())
    if len(lib) == 2:
        b = lib[1]
        w = min(w, 1+(t^b).bit_count(), 2+(t^a^b).bit_count())
    return 2*w


def build(lib):
    if len(lib) < 2:
        return sum(cost(a) for a in lib)
    a, b = lib
    return min(cost(a)+cost(b,(a,)), cost(b)+cost(a,(b,)))


def roots(rng, motif, forbidden, n, exclude=()):
    choices = [i for i in range(D) if not ((motif|forbidden)>>i&1)]
    seen, out = set(exclude), []
    available = comb(len(choices), 8-motif.bit_count())
    blocked = sum(t.bit_count()==8 and t & motif == motif and not t & forbidden for t in seen)
    if n > available - blocked:
        raise ValueError("requested roots exceed family capacity")
    while len(out)<n:
        t = motif | mask(rng.sample(choices, 8-motif.bit_count()))
        if t not in seen:
            seen.add(t); out.append(t)
    return tuple(out)


def family(seed, size, regime):
    rng = Random(9100+seed)
    order = rng.sample(range(D),D)
    m, noise, shift = mask(order[:4]), mask(order[4:7]), mask(order[7:11])
    pair = tuple(sorted((mask(order[:2])|noise, mask(order[2:4])|noise)))
    pool = set(pair)
    while len(pool)<size:
        pool.add(mask(rng.sample(range(D),5)))
    pool = sorted(pool); Random(9200+seed).shuffle(pool)
    rng = Random(9300+seed)
    if regime=='null':
        dev = roots(rng,0,0,8)
    elif regime=='noisy_shared':
        clean = roots(rng,m,noise,6)
        dev = clean + roots(rng,0,0,2,clean)
    else:
        dev = roots(rng,m,noise,8)
    mm, ff = {'shared':(m,noise),'shifted':(shift,m|noise),'null':(0,0),'noisy_shared':(m,noise)}[regime]
    held = roots(Random(9400+seed),mm,ff,max(HORIZONS),dev)
    assert not set(dev)&set(held)
    return tuple(pool),dev,held,pair


def signature_pairs(pool, dev, limit):
    if limit==0:
        return [],0
    both,either=MASK,0
    for t in dev:
        both &= t; either |= t
    fixed = both | (MASK ^ either)
    work = 2*len(dev)+2
    buckets=defaultdict(list); sig=[]
    for i,a in enumerate(pool):
        s=a&fixed; sig.append(s); buckets[s].append(i); work+=2
    pairs=[]
    for i,s in enumerate(sig):
        work+=2
        for j in buckets.get(s^both,()):
            work+=1
            if j>i:
                pairs.append(tuple(sorted((pool[i],pool[j]))))
                if len(pairs)==limit:
                    return pairs,work
    return pairs,work


def unrank(n,r):
    lo,hi,work=0,n-1,0
    while lo+1<hi:
        mid=(lo+hi)//2; prefix=mid*(2*n-mid-1)//2; work+=1
        if prefix<=r: lo=mid
        else: hi=mid
    return lo,lo+1+r-lo*(2*n-lo-1)//2,work+1


def random_pairs(pool,limit,seed):
    ranks=Random(seed).sample(range(comb(len(pool),2)),limit)
    pairs,work=[],limit
    for r in ranks:
        i,j,steps=unrank(len(pool),r); work+=steps
        pairs.append(tuple(sorted((pool[i],pool[j]))))
    return pairs,work


def select(pool,dev,method,seed,budget=BUDGET):
    # Common singleton sweep. Maximize projected development savings less build cost.
    # Charge actual residual probes, index work and enumeration/unranking work.
    base=sum(cost(t) for t in dev)
    best,val,work=(),0,0
    def consider(lib,charge):
        nonlocal best,val,work
        work+=charge
        # integer score times len(dev), equivalent to exact rational score
        v=max(HORIZONS)*(base-sum(cost(t,lib) for t in dev))-len(dev)*build(lib)
        if (-v,len(lib),lib)<(-val,len(best),best): best,val=lib,v
    for a in pool: consider((a,),2*len(dev)+1)
    proposed,extra=[],0
    if method=='signature': proposed,extra=signature_pairs(pool,dev,budget)
    elif method=='random': proposed,extra=random_pairs(pool,min(budget,comb(len(pool),2)),seed)
    elif method=='exhaustive':
        proposed=[tuple(sorted(p)) for p in combinations(pool,2)]; extra=len(proposed)
    elif method!='single': raise ValueError(method)
    work+=extra
    for lib in proposed: consider(lib,4*len(dev)+6)
    return best,work,len(proposed),Fraction(val,len(dev))


def run():
    rows=[]
    for size in SIZES:
        for regime in REGIMES:
            for seed in SEEDS:
                pool,dev,held,pair=family(seed,size,regime)
                for method in METHODS:
                    lib,work,pairs,val=select(pool,dev,method,9500+seed)
                    cumulative=[0]
                    for t in held: cumulative.append(cumulative[-1]+cost(t,lib))
                    for n in HORIZONS:
                        rows.append(dict(size=size,regime=regime,seed=seed,method=method,horizon=n,
                                         baseline=16*n,work=work,construction=build(lib),
                                         total=work+build(lib)+cumulative[n],pair_scored=pairs,
                                         planted=lib==pair,library=lib,dev_score=str(val)))
    summary=[]
    for size in SIZES:
        for regime in REGIMES:
            for method in METHODS:
                for n in HORIZONS:
                    rr=[r for r in rows if (r['size'],r['regime'],r['method'],r['horizon'])==(size,regime,method,n)]
                    b,t,w,p=[sum(r[k] for r in rr) for k in ('baseline','total','work','pair_scored')]
                    summary.append(dict(size=size,regime=regime,method=method,horizon=n,baseline=b,total=t,
                                        gain=str(Fraction(b,t)),work=w,pair_scored=p,planted=sum(r['planted'] for r in rr),
                                        profitable=sum(r['total']<r['baseline'] for r in rr)))
    return dict(protocol='VAD-03A',evidence='finite exact synthetic control',
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),pair_budget=BUDGET,summary=summary,records=rows)

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))

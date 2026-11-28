"""AIRIS-08 development data: full multiset custody, exact action values."""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
import random
from curriculum import make_bundle,digest
from nonstationary import OBS,posterior,values,optimal,orderless_floor
from partial import SCHEDULES
from router_data import simulate_episode

RATES=(0,1,2)
TRAIN_DRAW=12000
EVAL_DRAW=4000
PAIR_WEIGHT=4


def key(h):
    return tuple(sorted(h))


def bucket(h):
    return int(digest(["AIRIS-08-multiset-v1",key(h)])[:16],16)%5


def decode(row):
    h=[]
    for e in row["input"]["history"]:
        a,y=tuple(e["actions"]),e["observations"]
        h.append(4*SCHEDULES.index(a)+OBS.index((y[0]^y[1],y[1]^y[2])))
    return int(row["input"]["drift_resample_probability"][0]),tuple(h)


@lru_cache(None)
def target(r):
    k,h=r
    return values(posterior(h,k),k)


def sample(seed,n,k):
    rng=random.Random(seed)
    for _ in range(n):
        theta=rng.randrange(4)
        h=[]
        for _ in range(3):
            if rng.randrange(4)<k:
                theta=rng.randrange(4)
            a=rng.randrange(8)
            y=simulate_episode(rng,SCHEDULES[a],1,theta)
            h.append(4*a+OBS.index((y[0]^y[1],y[1]^y[2])))
        yield k,tuple(h)


def make_data(train_draw=TRAIN_DRAW,eval_draw=EVAL_DRAW):
    t,d,_=make_bundle()
    dev=[decode(r) for r in d]
    dev_bags={key(h) for _,h in dev}
    # Keep both presentations and both rates or discard their entire bag.
    candidates=[decode(r) for r in t if key(decode(r)[1]) not in dev_bags]
    for r in t:
        row=decode(r)
        if key(row[1]) not in dev_bags:
            assert tuple(F(x) for x in r["teacher"]["action_values"])==target(row)
    # Random evaluation uses a frozen hash bucket excluding ALL curriculum
    # multisets. This is an ordinary-generator conditional sample, not the
    # unconditional environment distribution.
    pair_bags={key(h) for _,h in candidates+dev}
    ordinary_train=[r for k in (0,1) for r in sample(8200+k,train_draw//2,k)
                    if key(r[1]) not in dev_bags and bucket(r[1])!=0]
    ordinary_eval={str(k):[r for r in sample(8300+k,eval_draw,k)
                         if bucket(r[1])==0 and key(r[1]) not in pair_bags]
                   for k in RATES}
    eval_sets={f"paired_k{k}":[r for r in dev if r[0]==k] for k in RATES}
    eval_sets.update({f"ordinary_k{k}":ordinary_eval[str(k)] for k in RATES})
    train=ordinary_train+candidates*PAIR_WEIGHT
    a={key(h) for _,h in train}
    b={key(h) for rows in eval_sets.values() for _,h in rows}
    assert not a&b
    assert train and candidates and all(eval_sets.values())
    assert all(k in (0,1) for k,_ in train)
    assert len(candidates)%4==0
    return train,eval_sets,{"train_ordinary_draws_retained":len(ordinary_train),
                           "train_candidate_presentations":len(candidates),
                           "train_candidate_weight":PAIR_WEIGHT,
                           "train_candidate_presentations_excluded":len(t)-len(candidates),
                           "train_weighted_rows":len(train),
                           "train_unique_rows":len(set(train)),
                           "train_bags":len(a),"eval_bags":len(b),
                           "cross_split_bags":len(a&b)}


def summarize(rows,actions,paired=False):
    if len(rows)!=len(actions) or not rows:
        raise ValueError("invalid evaluation")
    regrets=[]
    groups={}
    for (k,h),a in zip(rows,actions,strict=True):
        q=target((k,h))
        if a=="uniform":
            r=max(q)-sum(q,F(0))/8
        else:
            if type(a) is not int or not 0<=a<8:
                raise ValueError("invalid action")
            r=max(q)-q[a]
        regrets.append(r)
        if paired:
            g=(k,tuple(sorted(h[:2])),h[2])
            groups.setdefault(g,[]).append((q,a,r))
    out={"n":len(rows),"bags":len({key(h) for _,h in rows}),
         "mean_regret":float(sum(regrets,F(0))/len(rows)),
         "zero_regret_fraction":sum(r==0 for r in regrets)/len(rows),
         "regrets":[str(r) for r in regrets]}
    if paired:
        if any(len(g)!=2 for g in groups.values()):
            raise ValueError("incomplete paired group")
        floor=[orderless_floor(g[0][0],g[1][0]) for g in groups.values()]
        out.update(pairs=len(groups),orderless_floor=float(sum(floor,F(0))/len(floor)),
                   both_optimal_fraction=sum(all(x[2]==0 for x in g) for g in groups.values())/len(groups),
                   different_action_fraction=sum(g[0][1]!=g[1][1] for g in groups.values())/len(groups))
    return out


def exact_actions(rows,mode):
    out=[]
    for k,h in rows:
        if mode=="pulse":
            out.append(0)
        elif mode=="uniform":
            out.append("uniform")
        elif mode=="full":
            out.append(optimal(target((k,h)))[0])
        elif mode=="last":
            out.append(optimal(target((k,h[-1:])))[0])
        elif mode=="pair_orderless":
            # For paired balanced presentations only: oracle knows which
            # observations are the first two, but not their order.
            i,j=sorted(h[:2])
            q=target((k,(i,j,h[2])))
            r=target((k,(j,i,h[2])))
            out.append(max(range(8),key=lambda a:q[a]+r[a]))
        else:
            raise ValueError("unknown baseline")
    return out

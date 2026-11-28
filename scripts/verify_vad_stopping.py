"""VAD-07A: exact Bayesian stopping with observable cues and fixed-cutoff controls."""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from random import Random
import argparse, json

TIMES = (2, 8, 16, 24, 25)  # 25 denotes null at H=24
H = 24
COST = F(2)
P = (F(7,10),)*4 + (F(3,20),)
WEIGHTS = {
    'base': (15,10,15,10,50), 'null_heavy': (8,5,8,4,75),
    'early_heavy': (35,20,10,5,30), 'late_heavy': (5,5,25,25,40),
}


def prior(w):
    return tuple(F(x,sum(w)) for x in w)


def model(w, p=P):
    return prior(w), tuple(p)


def reward(t):
    # Net of construction; known at discovery. Null yields no reward.
    return F(88-t) if t<=H else F(0)


def bellman(w,p, cues=True, times=TIMES):
    """State (n,k): n unsuccessful observations, k positive cues. Exact Fractions."""
    if not cues: p=(F(1,2),)*len(w)
    @lru_cache(None)
    def mass(n,k):
        return tuple(x*q**k*(1-q)**(n-k) if t>n else F(0)
                     for t,x,q in zip(times,w,p))
    @lru_cache(None)
    def v(n,k):
        a=mass(n,k); z=sum(a)
        if n==H or not z: return F(0),False
        hit=sum(x*reward(t) for t,x in zip(times,a) if t==n+1)
        nextval=hit
        for b in (0,1):
            z2=sum(mass(n+1,k+b))
            nextval+=z2*v(n+1,k+b)[0]
        cont=nextval/z-COST
        return (cont,True) if cont>0 else (F(0),False)
    return v


def evaluate(w,p,action,times=TIMES):
    """Independent forward probability flow; each state weight includes multiplicity."""
    states={(0,0,i):x for i,x in enumerate(w) if x}
    obs=F(0); pay=F(0); hit=F(0); stop=F(0)
    for n in range(H+1):
        nxt={}
        for (_,k,i),mass in states.items():
            if n==H or not action(n,k): stop+=mass; continue
            obs+=mass
            if times[i]==n+1:
                pay+=mass*reward(n+1); hit+=mass; continue
            for b,q in ((0,1-p[i]),(1,p[i])):
                key=(n+1,k+b,i); nxt[key]=nxt.get(key,F(0))+mass*q
        states=nxt
    assert stop+hit==1
    return dict(net=pay-COST*obs,observations=obs,hit=hit,gross=pay)


def cutoff_value(w,k):
    return sum(x*((reward(t) if t<=k else 0)-COST*min(t,k)) for t,x in zip(TIMES,w))


def best_cutoff(w):
    return max(range(H+1),key=lambda k:(cutoff_value(w,k),-k))


def calibrate(seed,n=512):
    """Full labeled training trajectories only, Laplace pseudocounts for type and cue rates."""
    rng=Random(seed); w=WEIGHTS['base']; counts=[1]*len(w); ones=[1]*len(w); tot=[2]*len(w)
    for _ in range(n):
        i=rng.choices(range(len(w)),weights=w,k=1)[0]; counts[i]+=1
        for _ in range(min(TIMES[i]-1,H)):
            ones[i]+=rng.randrange(P[i].denominator)<P[i].numerator; tot[i]+=1
    return prior(counts), tuple(F(a,b) for a,b in zip(ones,tot))


def run():
    base,p=model(WEIGHTS['base']); train=calibrate(713207)
    pooled=tuple(sum(x) for x in zip(*(WEIGHTS[k] for k in ('base','null_heavy','late_heavy'))))
    models={'base':(base,p),'calibrated':train,'mixture':model(pooled)}
    policies={k:bellman(*m) for k,m in models.items()}
    blind=bellman(base,p,False); cut=best_cutoff(base)
    scenarios={k:model(w) for k,w in WEIGHTS.items()}
    scenarios.update(weak_cues=model(WEIGHTS['base'],(F(11,20),)*4+(F(9,20),)),
                     reversed_cues=model(WEIGHTS['base'],(F(1,4),)*4+(F(3,4),)),
                     no_cues=model(WEIGHTS['base'],(F(1,2),)*5))
    # A calibrated safe blend is a fixed cutoff chosen on an explicit scenario mixture.
    # Neither future scenario labels nor exact test rewards are exposed to a policy.
    rows=[]; checks=0
    for name,(w,q) in scenarios.items():
        oracle=bellman(w,q); blind_oracle=bellman(w,q,False)
        actions={k:(lambda n,j,v=v:v(n,j)[1]) for k,v in policies.items()}
        actions.update(oracle=lambda n,j:oracle(n,j)[1], blind_oracle=lambda n,j:blind_oracle(n,j)[1],
                       base_cutoff=lambda n,j:n<cut, full=lambda n,j:n<H, stop=lambda n,j:False)
        for policy,action in actions.items():
            r=evaluate(w,q,action)
            if policy=='oracle': assert r['net']==oracle(0,0)[0]; checks+=1
            if policy=='blind_oracle':
                assert r['net']==cutoff_value(w,best_cutoff(w))==blind_oracle(0,0)[0]; checks+=1
            if policy=='base_cutoff': assert r['net']==cutoff_value(w,cut); checks+=1
            assert r['net']<=oracle(0,0)[0]; checks+=1
            rows.append(dict(scenario=name,policy=policy,**{k:str(v) for k,v in r.items()}))
    # Verify blindness equivalence for additional priors independently of cue rates.
    for i in range(40):
        rng=Random(9000+i); w=prior(tuple(rng.randint(1,30) for _ in TIMES))
        b=bellman(w,p,False)
        assert b(0,0)[0]==cutoff_value(w,best_cutoff(w)); checks+=1
    return dict(protocol='VAD-07A',evidence='exact finite Bayesian stopping model',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),checks=checks,base_cutoff=cut,training=dict(seed=713207,n=512,prior=list(map(str,train[0])),cue_rates=list(map(str,train[1]))),rows=rows)


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    r=run(); a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('cutoff',r['base_cutoff'],'checks',r['checks'])
    for s in sorted({x['scenario'] for x in r['rows']}):
        print(s,{x['policy']:round(float(F(x['net'])),4) for x in r['rows'] if x['scenario']==s})

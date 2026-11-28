"""VAD-08: censored feedback, online reliability filtering and stopping.

Python standard library. The optional recurrent experiment lives in train_vad_reliability.py.
The finite within-family planner uses floating point; exact tests compare it to VAD-07.
"""
import argparse
from functools import lru_cache
from hashlib import sha256
from math import log, sqrt
from pathlib import Path
from random import Random
import json

H=24
TIMES=(2,8,16,24,25)
BASE=(.15,.10,.15,.10,.50)
HIGH_NULL=(.08,.05,.08,.04,.75)
CHANNELS=((.70,.70,.70,.70,.15),(.25,.25,.25,.25,.75))
WEAK=(.55,.55,.55,.55,.45)
COST=2
GRID=20
EXP_GRID=5
# Independent stream namespaces; observations are policy-censored.
SPLITS={'train':(8100000,256,48),'cal':(8200000,48,64),'test':(8300000,32,96)}
SCENARIOS=('markov','stationary','reverse','abrupt','fast','weak','prior_shift','joint_shift')
METHODS=('blind','frozen','mixed','filter','alarm','expanded','mode_oracle')
HAZARD=.05
ALARM=20.


def reward(t): return 88-t if t<=H else 0


@lru_cache(None)
def table(prior,channel):
    """Likelihood of the observed record, not of an unobserved full trajectory.

    n = paid observations, k = positive cues on failures, hit = discovery on last observation.
    There are n-1 cues for a hit and n cues for censoring.
    No binomial multiplicity: the particular ordered cue sequence was observed.
    """
    result={}
    for n in range(H+1):
        for hit in (False,True):
            if hit and n==0: continue
            f=n-int(hit)
            for k in range(f+1):
                result[n,k,hit]=sum(w*q**k*(1-q)**(f-k) for t,w,q in zip(TIMES,prior,channel)
                                      if (t==n if hit else t>n))
    return result


@lru_cache(None)
def plan(weights, channels):
    """Exact finite-state recursion in float, for fixed prior mixture on family types."""
    types=[(t,w,q) for ws,ps in zip(weights,channels) for t,w,q in zip(TIMES,ws,ps) if w]
    mass={}; value={}; actions={}
    for n in range(H,-1,-1):
        for k in range(n+1):
            a=[w*q**k*(1-q)**(n-k) if t>n else 0. for t,w,q in types]
            z=sum(a); mass[n,k]=z
            cont=0.
            if n<H and z:
                hit=sum(x*reward(t) for (t,_,_),x in zip(types,a) if t==n+1)
                cont=(hit+sum(mass[n+1,k+b]*value[n+1,k+b] for b in (0,1)))/z-COST
            value[n,k]=max(0.,cont); actions[n,k]=cont>1e-10
    return actions,value[0,0]


def quantize(prob): return max(0,min(GRID,round(GRID*prob)))


@lru_cache(None)
def policy(i):
    r=i/GRID
    return plan((tuple((1-r)*w for w in BASE),tuple(r*w for w in BASE)),CHANNELS)[0]


def true_policy(mode,prior,channel):
    return plan((prior,),(channel,))[0]


def transition(p,hazard=HAZARD): return hazard+(1-2*hazard)*p


def update(prob,record,prior=BASE,channels=CHANNELS):
    l=[table(prior,q)[record] for q in channels]
    a=(1-prob)*l[0]; b=prob*l[1]; z=a+b
    if not z: raise ValueError('impossible record under all nominal modes')
    return b/z,z


def norm_update(p,record,models):
    weights=[w*table(prior,channel)[record] for w,(prior,channel) in zip(p,models)]
    z=sum(weights)
    if not z: raise ValueError('impossible record')
    return tuple(x/z for x in weights),z


def family_stream(seed,scenario,n):
    rng=Random(seed); mode=rng.randrange(2); stream=[]
    for j in range(n):
        if scenario=='stationary': mode=0
        elif scenario=='reverse': mode=1
        elif scenario=='abrupt': mode=int(j>=n//2)
        elif scenario in ('markov','fast','prior_shift','joint_shift','weak') and j and rng.random() < (.25 if scenario=='fast' else HAZARD): mode=1-mode
        prior=HIGH_NULL if scenario in ('prior_shift','joint_shift') and j>=n//2 else BASE
        channel=WEAK if scenario=='weak' or (scenario=='joint_shift' and j>=n//2) else CHANNELS[mode]
        i=rng.choices(range(5),weights=prior,k=1)[0]; t=TIMES[i]
        bits=tuple(int(rng.random()<channel[i]) for _ in range(H))
        stream.append((mode,prior,channel,t,bits))
    return stream


def execute(world,actions=None,cap=None):
    _,_,_,t,bits=world; n=k=0; hit=False
    while n<H and (n<cap if cap is not None else actions[n,k]):
        n+=1
        if t==n: hit=True; break
        k+=bits[n-1]
    return (n,k,hit), (reward(t) if hit else 0)-COST*n


# An alternative predictive model: a static mixture of weak-cue / high-null worlds.
ALT_MODELS=((BASE,WEAK),(HIGH_NULL,CHANNELS[0]),(HIGH_NULL,CHANNELS[1]),(HIGH_NULL,WEAK))
EXP_MODELS=((BASE,CHANNELS[0]),(BASE,CHANNELS[1]))+ALT_MODELS


@lru_cache(None)
def expanded_policy(gridweights):
    ws=tuple(tuple(x/EXP_GRID*w for w in prior) for x,(prior,_) in zip(gridweights,EXP_MODELS))
    return plan(ws,tuple(q for _,q in EXP_MODELS))[0]


def simplex_quantize(p):
    vals=[EXP_GRID*x for x in p]; floors=[int(x) for x in vals]
    for j in sorted(range(len(p)),key=lambda i:(-(vals[i]-floors[i]),i))[:EXP_GRID-sum(floors)]: floors[j]+=1
    return tuple(floors)


def expanded_transition(p):
    # With probability 0.1 redraw mode from declared prior; otherwise persist.
    prior=(.4,.4,.05,.05,.05,.05)
    return tuple(.90*x+.10*y for x,y in zip(p,prior))


def feature(record):
    n,k,hit=record
    return (n/H,k/H,float(hit),k/max(1,n-int(hit)),1.)


def simulate(stream,method,predictor=None,hazard=HAZARD,alarm_threshold=ALARM):
    p=.5; alt=(.25,)*4; exp=(.4,.4,.05,.05,.05,.05); log_lr=0.; alarm=False
    rows=[]; hidden=None
    for j,world in enumerate(stream):
        mode,prior,channel,t,bits=world
        # True mode, type and channel are diagnostic only; only mode_oracle may use them.
        estimate=p; grid=None; control=0; macs=0
        if method=='blind' or (method=='alarm' and alarm): act=None; cap=2; control=1; estimate=.5
        elif method=='mode_oracle': act=true_policy(mode,prior,channel); cap=None; estimate=float(mode)
        elif method=='expanded': grid=simplex_quantize(exp); act=expanded_policy(grid); cap=None; control=6; estimate=exp[1]+exp[4]+.5*(exp[2]+exp[5])
        else:
            if method=='frozen': estimate=0.
            elif method=='mixed': estimate=.5
            elif method.startswith('gru'):
                estimate= predictor.predict(hidden); macs=predictor.head_macs; control=1
            else: control=2
            grid=quantize(estimate); act=policy(grid); cap=None
        rec,net=execute(world,act,cap)
        # Update using only record produced by this policy (including censoring).
        posterior,lik=update(p,rec)
        if method in ('filter','alarm'): control+=2
        if method=='alarm':
            alt,alt_lik=norm_update(alt,rec,ALT_MODELS)
            log_lr+=log(alt_lik)-log(lik); alarm=alarm or log_lr>=log(alarm_threshold)
            control+=4
        if method=='expanded':
            exp,_=norm_update(exp,rec,EXP_MODELS); exp=expanded_transition(exp); control+=6
        if method.startswith('gru'):
            hidden=predictor.step(feature(rec),None if method=='gru_memoryless' else hidden)
            macs+=predictor.step_macs; control+=5
        rows.append(dict(j=j,mode=mode,record=list(rec),net=net,estimate=estimate,grid=grid,
                         nominal_p=p,nominal_loglik=log(lik),alarm=alarm,log_lr=log_lr,
                         control=control,macs=macs))
        p=transition(posterior,hazard)
    return rows


def aggregate(records):
    out=[]
    for scenario in SCENARIOS:
        methods=sorted({r['method'] for r in records if r['scenario']==scenario})
        for m in methods:
            rr=[r for r in records if r['scenario']==scenario and r['method']==m]; n=sum(r['n'] for r in rr)
            tot=sum(r['net'] for r in rr); control=sum(r['control'] for r in rr); macs=sum(r['macs'] for r in rr)
            out.append(dict(scenario=scenario,method=m,streams=len(rr),families=n,mean_net=tot/n,
                            mean_observations=sum(r['observations'] for r in rr)/n,
                            hit_rate=sum(r['hits'] for r in rr)/n,control_per_family=control/n,macs_per_family=macs/n,
                            net_minus_control=(tot-control)/n,net_minus_control_and_macs=(tot-control-macs)/n,
                            mean_brier=sum(r['brier'] for r in rr)/n,alarm_streams=sum(r['alarm_at'] is not None for r in rr)))
    return out


def run(split='test',predictor=None,hazard=HAZARD,alarm_threshold=ALARM):
    start,n,steps=SPLITS[split]; methods=METHODS+('gru','gru_memoryless') if predictor else METHODS
    records=[]
    for si,scenario in enumerate(SCENARIOS):
        for i in range(n):
            seed=start+si*10000+i; stream=family_stream(seed,scenario,steps)
            for method in methods:
                rr=simulate(stream,method,predictor,hazard,alarm_threshold)
                records.append(dict(scenario=scenario,seed=seed,method=method,n=steps,
                    net=sum(r['net'] for r in rr),observations=sum(r['record'][0] for r in rr),hits=sum(r['record'][2] for r in rr),
                    control=sum(r['control'] for r in rr),macs=sum(r['macs'] for r in rr),
                    brier=sum((r['estimate']-r['mode'])**2 for r in rr),
                    alarm_at=next((r['j']+1 for r in rr if r['alarm']),None),
                    trace_sha256=sha256(json.dumps(rr,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    return dict(protocol='VAD-08A/B',split=split,hazard=hazard,alarm_threshold=alarm_threshold,records=records,summary=aggregate(records))


def paired(records,first,second,seed=7234):
    rng=Random(seed); out=[]
    for s in SCENARIOS:
        a={r['seed']:r for r in records if r['scenario']==s and r['method']==first}; b={r['seed']:r for r in records if r['scenario']==s and r['method']==second}
        ds=[(a[k]['net']-b[k]['net'])/a[k]['n'] for k in sorted(a)]
        draws=sorted(sum(rng.choices(ds,k=len(ds)))/len(ds) for _ in range(2000))
        out.append(dict(scenario=s,first=first,second=second,mean=sum(ds)/len(ds),interval=[draws[50],draws[1949]],wins=sum(x>0 for x in ds)))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); args=p.parse_args()
    r=run(); r['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest(); args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    for row in r['summary']: print(row)

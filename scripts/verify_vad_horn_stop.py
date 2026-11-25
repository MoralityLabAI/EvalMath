"""VAD-07C: cue-conditioned stopping on matched Horn prefixes."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from random import Random
import argparse,json
import verify_vad_horn as v
import verify_vad_ancestor as a

H=256; CAPS=(0,1,2,4,8,16,24,32,48,64)
REGIMES=('shared','easy16','easy48','hard16','hard48','easy_null','hard_null','dominated')
WEIGHTS={
    'base': (5,15,15,5,5,15,35,5),
    'null_heavy': (3,7,7,3,3,25,47,5),
    'cue_shift': (5,5,5,15,15,35,15,5),
    'late_heavy': (5,5,25,5,20,15,20,5),
    'uniform': (1,)*8,
}
SPLITS={'cal':(210000,32),'test':(230000,64)}


def family(seed,regime):
    """For equal seed, each easy/hard null matches its concealed counterpart until unlock."""
    facts=tuple(range(6)); rules=[]; n=6
    def rule(args,head=None):
        nonlocal n
        if head is None: head=n; n+=1
        assert all(x<head for x in args)
        rules.append((tuple(args),head)); return head
    rng=Random(seed)
    def chain(start,length,rng):
        for _ in range(length): start=rule((start,rng.choice(facts)))
        return start
    hub=chain(0,rng.randrange(4,7),rng)
    easy=regime.startswith('easy') or regime=='dominated'
    unlock=0 if regime in ('shared','dominated') else H+1 if regime.endswith('null') else int(regime[4:])
    held=[]
    for j in range(H):
        r=Random(seed*1009+j*131)
        private=(r.choice(facts),) if easy and (j<unlock or regime=='dominated') else (chain(r.choice(facts),r.randrange(4,10),r),)
        g=rule(private)
        if j>=unlock: rule((hub,r.choice(facts)),g)
        held.append(g)
    return facts,tuple(rules),tuple(held)


def trace(facts,rules,held):
    by=v.index(rules); ix=tuple(range(len(rules))); base,_,_=v.solve(facts,rules,ix)
    assert base==v.independent(facts,rules)
    checks=len(base)
    baseline=sum(base[g] for g in held)+H-1
    cone,_,_=v.cone(rules,by,held); dp=sum(1+len(rules[j][0]) for j in cone)
    counts={}; distances={}; work=0; prefixes=[0]; cue=None; hit=0; candidate=(); reward=0; build=0
    for k,g in enumerate(held[:64],1):
        ds,w=a.ancestors(facts,rules,by,g,3); work+=w
        if k==1: cue='empty' if not ds else 'nonempty'
        eligible=[]
        for u,d in ds.items():
            counts[u]=counts.get(u,0)+1; distances[u]=distances.get(u,0)+d; work+=4
            if counts[u]>=2: eligible.append(u)
        if eligible:
            work+=len(eligible); best=min(eligible,key=lambda u:(-counts[u],distances[u],u)); candidate=(best,)
            assert best not in facts+held
            d,_,_=v.solve(facts,rules,ix,candidate); assert d==v.independent(facts,rules,candidate); checks+=len(d)
            hit=k; build=base[best]; reward=sum(base[g]-d[g] for g in held[k:])-build
        prefixes.append(work)
        if hit: break
    totals={cap:baseline+prefixes[min(cap,hit or 64)]-(reward if hit and cap>=hit else 0) for cap in CAPS}
    return dict(cue=cue,baseline=baseline,dp=dp,hit=hit,candidate=list(candidate),reward=reward,build=build,totals=totals),checks


def evaluate(split):
    start,n=SPLITS[split]; rows=[]; checks=0
    for ri,regime in enumerate(REGIMES):
        for i in range(n):
            seed=start+ri*1000+i; r,c=trace(*family(seed,regime)); checks+=c
            rows.append(dict(seed=seed,regime=regime,**r))
    return rows,checks


def weight(r,scenario): return WEIGHTS[scenario][REGIMES.index(r['regime'])]


def pick(rows,scenario,cue=None):
    rr=[r for r in rows if cue is None or r['cue']==cue]
    caps=CAPS if cue is None else CAPS[1:] # first observation is charged for cue-conditioned policy
    return min(caps,key=lambda cap:(sum(weight(r,scenario)*r['totals'][cap] for r in rr),cap))


def score(rows,scenario,policy):
    # Every regime has equal test counts. Report weighted integer sums, not a random sample.
    b=sum(weight(r,scenario)*r['baseline'] for r in rows)
    d=sum(weight(r,scenario)*r['dp'] for r in rows)
    t=sum(weight(r,scenario)*r['totals'][policy(r)] for r in rows)
    return dict(baseline=b,total=t,gain=str(F(b,t)),gain_common_dp=str(F(b+d,t+d)),net_saving=b-t,
                weighted_count=sum(weight(r,scenario) for r in rows))


def run():
    cal,c=evaluate('cal'); fixed=pick(cal,'base'); cue={x:pick(cal,'base',x) for x in ('empty','nonempty')}
    test,x=evaluate('test'); results=[]
    for s in WEIGHTS:
        for name,p in [('direct',lambda r:0),('fixed',lambda r:fixed),('cue',lambda r:cue[r['cue']]),('cap64',lambda r:64)]:
            results.append(dict(scenario=s,policy=name,**score(test,s,p)))
    per=[]
    for regime in REGIMES:
        rr=[r for r in test if r['regime']==regime]; b=sum(r['baseline'] for r in rr)
        per.append(dict(regime=regime,baseline=b,fixed=sum(r['totals'][fixed] for r in rr),cue=sum(r['totals'][cue[r['cue']]] for r in rr),hits=sum(bool(r['hit']) for r in rr),empty_cue=sum(r['cue']=='empty' for r in rr)))
    return dict(protocol='VAD-07C',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependencies={Path(m.__file__).name:sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (v,a)},splits=SPLITS,weights=WEIGHTS,calibration_choice=dict(fixed=fixed,cue=cue),checks=c+x,results=results,per_regime=per,calibration=cal,records=test)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); args=p.parse_args(); r=run(); args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(r['calibration_choice'],r['checks'],len(r['records']))
    for s in WEIGHTS: print(s,{x['policy']:round(float(F(x['gain'])),5) for x in r['results'] if x['scenario']==s})
    print(r['per_regime'])

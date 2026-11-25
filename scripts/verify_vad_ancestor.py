"""VAD-06D2: prefix-only ancestor indexing with visible and concealed unlocks."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from random import Random

import verify_vad_horn as v
import verify_vad_adaptive as a

H=256
REGIMES=('shared','mixed','shifted','late_shift','null','dominated','soft_dominated',
         'latent16','latent48','hidden16','hidden48','deep_shared','deep_hidden16','intermittent')
SPLITS={'cal':(160000,12),'test':(180000,24)}
BASELINES=('direct','offline','prefix_4','prefix_16','unary_2_64','arity_2_64')
POLICIES=tuple(f'ancestor_{depth}_{support}_{cap}_{gate}' for depth in (1,2,3)
               for support in (2,4) for cap in (32,64) for gate in ('all','hard'))
METHODS=BASELINES+POLICIES


def family(seed,regime):
    rng=Random(seed); facts=tuple(range(6)); rules=[]; n=6
    def rule(args,head=None):
        nonlocal n
        if head is None: head=n; n+=1
        assert all(x<head for x in args)
        rules.append((tuple(args),head)); return head
    def chain(start,length):
        for _ in range(length): start=rule((start,rng.choice(facts)))
        return start
    hubs=[chain(facts[i],rng.randrange(4,7)) for i in range(2)]
    targets=[]
    for j in range(-8,H):
        hub=hubs[0]; easy=0; depth=2 if regime.startswith('deep_') else 0
        if regime=='null': hub=None
        elif regime=='dominated': easy=1
        elif regime=='soft_dominated': easy=2
        elif j>=0:
            if regime=='shifted' or (regime=='late_shift' and j>=16): hub=hubs[1]
            elif regime=='mixed': hub=hubs[rng.randrange(2)]
            elif regime.startswith(('latent','hidden','deep_hidden')):
                cutoff=48 if regime.endswith('48') else 16
                if j<cutoff:
                    easy=1
                    if 'hidden' in regime: hub=None
            elif regime=='intermittent' and rng.randrange(4)!=0: easy=1
        private=tuple(rng.sample(facts,easy)) if easy else (chain(rng.choice(facts),rng.randrange(4,10)),)
        alt=chain(hub,depth) if hub is not None else None
        g=rule(private)
        if alt is not None: rule((alt,rng.choice(facts)),g)
        targets.append(g)
    return facts,tuple(rules),tuple(targets[:8]),tuple(targets[8:])


def ancestors(facts,rules,by,g,depth):
    """Bounded BFS; retain shortest distance per nonfact ancestor."""
    fs=set(facts); dist={g:0}; todo=[g]; work=0
    for x in todo:
        work+=1
        if dist[x]==depth: continue
        for j in by[x]:
            args,_=rules[j]; work+=1+len(args)
            for u in args:
                if u not in fs and u not in dist:
                    dist[u]=dist[x]+1; todo.append(u)
    del dist[g]
    return dist,work


def select(facts,rules,by,dev,held,method):
    if method in BASELINES:
        lib,search,obs,k,_=a.select(facts,rules,by,dev,held,method)
        return lib,search+obs,k
    _,depth,need,cap,gate=method.split('_'); depth,need,cap=map(int,(depth,need,cap))
    counts={}; distances={}; hard_counts={}; work=0
    for k,g in enumerate(held[:cap],1):
        hard=True
        if gate=='hard':
            easy,w=a.screen(facts,rules,by,g,'arity'); work+=w; hard=not easy
        ds,w=ancestors(facts,rules,by,g,depth); work+=w
        eligible=[]
        for u,d in ds.items():
            counts[u]=counts.get(u,0)+1; distances[u]=distances.get(u,0)+d
            hard_counts[u]=hard_counts.get(u,0)+int(hard); work+=4
            if counts[u]>=need and hard_counts[u]>0: eligible.append(u)
        if eligible:
            work+=len(eligible)
            best=min(eligible,key=lambda u:(-counts[u],distances[u],u))
            return (best,),work,k
    return (),work,k


def evaluate(split):
    start,count=SPLITS[split]; rows=[]; checks=0
    for ri,regime in enumerate(REGIMES):
        for i in range(count):
            seed=start+ri*1000+i; facts,rules,dev,held=family(seed,regime); by=v.index(rules)
            assert len(set(dev+held))==8+H and not any(x in dev+held for args,_ in rules for x in args)
            ix=tuple(range(len(rules))); base,_,_=v.solve(facts,rules,ix)
            assert base==v.independent(facts,rules); checks+=len(base)
            baseline=sum(base[g] for g in held)+H-1
            root_ix,_,_=v.cone(rules,by,held); dp=sum(1+len(rules[j][0]) for j in root_ix)
            costs={():base}
            for method in METHODS:
                lib,work,k=select(facts,rules,by,dev,held,method)
                assert not set(lib)&set(dev+held+facts)
                if lib not in costs:
                    dd,_,_=v.solve(facts,rules,ix,lib)
                    assert dd==v.independent(facts,rules,lib); checks+=len(dd); costs[lib]=dd
                dd=costs[lib]; build=sum(base[u] for u in lib); savings=sum(base[g]-dd[g] for g in held[k:])
                rows.append(dict(seed=seed,regime=regime,method=method,baseline=baseline,
                                 total=baseline+work+build-savings,common_dp=dp,work=work,construction=build,
                                 savings=savings,prefix=k,cache=list(lib),selected=bool(lib)))
    return rows,checks


def summary(rows):
    out=[]
    for regime in REGIMES+('all',):
        for method in METHODS:
            rr=[r for r in rows if r['method']==method and (regime=='all' or r['regime']==regime)]
            b,t,dp=[sum(r[x] for r in rr) for x in ('baseline','total','common_dp')]
            out.append(dict(regime=regime,method=method,n=len(rr),baseline=b,total=t,gain=str(Fraction(b,t)),gain_common_dp=str(Fraction(b+dp,t+dp)),
                            profitable=sum(r['total']<r['baseline'] for r in rr),selected=sum(r['selected'] for r in rr),
                            zero_savings_selected=sum(r['selected'] and not r['savings'] for r in rr),prefix=sum(r['prefix'] for r in rr),work=sum(r['work'] for r in rr)))
    return out


def paired(rows,choice,comparator):
    groups=[]; rng=Random(20261125)
    for regime in REGIMES:
        x={r['seed']:r['total'] for r in rows if r['regime']==regime and r['method']==choice}
        y={r['seed']:r['total'] for r in rows if r['regime']==regime and r['method']==comparator}
        groups.append([y[k]-x[k] for k in sorted(x)])
    total=sum(map(sum,groups)); samples=sorted(sum(sum(rng.choices(g,k=len(g))) for g in groups) for _ in range(4000))
    return dict(total_saving=total,bootstrap_interval=[samples[100],samples[3899]],wins=sum(d>0 for g in groups for d in g),ties=sum(d==0 for g in groups for d in g),n=sum(map(len,groups)))


def run(out):
    out.mkdir(parents=True,exist_ok=True); cal,c=evaluate('cal'); cs=summary(cal)
    def pick(menu): return min((r for r in cs if r['regime']=='all' and r['method'] in menu),key=lambda r:(r['total'],r['method']))['method']
    choice,comparator=pick(POLICIES),pick(BASELINES)
    freeze=dict(protocol='VAD-06D2',splits=SPLITS,chosen=choice,comparator=comparator,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependencies={Path(m.__file__).name:sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (v,a)},calibration=cs)
    (out/'freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    rows,x=evaluate('test'); result=dict(**freeze,checks=c+x,test_checks=x,records=rows,test=summary(rows),paired=paired(rows,choice,comparator),evidence='exact synthetic cost model; causal prefix; no new Lean replay')
    (out/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n'); return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); args=p.parse_args()
    r=run(args.out); print('chosen',r['chosen'],r['comparator'],'checks',r['checks'],'records',len(r['records']),r['paired'])
    for x in r['test']:
        if x['method'] in ('direct','prefix_4',r['chosen'],r['comparator']): print(x)

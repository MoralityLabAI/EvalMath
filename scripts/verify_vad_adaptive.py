"""VAD-06D: dominance certificates and adaptive prefix-only cache discovery."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from random import Random

import verify_vad_horn as v

H = 256
REGIMES = ('shared', 'mixed', 'shifted', 'late_shift', 'null', 'dominated',
           'soft_dominated', 'unlock4', 'unlock16', 'unlock48', 'intermittent')
SPLITS = {'cal': (120000, 12), 'test': (140000, 24)}
FIXED = ('direct', 'offline', 'prefix_4', 'prefix_16', 'prefix_64',
         'unary_4', 'arity_4', 'unary_16', 'arity_16')
ADAPT = tuple(f'{screen}_{hard}_{cap}' for screen in ('unary','arity')
              for hard in (2,4,8) for cap in (16,32,64))
METHODS = FIXED + ADAPT


def family(seed, regime):
    rng = Random(seed); facts = tuple(range(6)); rules=[]; n=6
    def rule(args, head=None):
        nonlocal n
        if head is None: head=n; n+=1
        assert all(a<head for a in args)
        rules.append((tuple(args),head)); return head
    def chain(start,length):
        for _ in range(length): start=rule((start,rng.choice(facts)))
        return start
    hubs=[chain(facts[i],rng.randrange(4,7)) for i in range(2)]
    targets=[]
    for j in range(-8,H):
        hub=hubs[0]; easy=0
        if regime=='null': hub=None
        elif regime=='dominated': easy=1
        elif regime=='soft_dominated': easy=2
        elif j>=0:
            if regime=='shifted' or (regime=='late_shift' and j>=16): hub=hubs[1]
            elif regime=='mixed': hub=hubs[rng.randrange(2)]
            elif regime.startswith('unlock') and j<int(regime[6:]): easy=1
            elif regime=='intermittent' and rng.randrange(4)!=0: easy=1
        if easy:
            goal=rule(tuple(rng.sample(facts,easy)))
        else:
            private=chain(rng.choice(facts),rng.randrange(2,8)); goal=rule((private,))
        if hub is not None: rule((hub,rng.choice(facts)),goal)
        targets.append(goal)
    return facts,tuple(rules),tuple(targets[:8]),tuple(targets[8:])


def screen(facts,rules,by,g,kind):
    """If true, a fact-only proof attains a universal lower bound."""
    fs=set(facts); work=1
    if kind=='unary':
        for j in by[g]:
            args,_=rules[j]; work+=1+len(args)
            if len(args)==1 and args[0] in fs: return True,work
        return False,work
    if kind!='arity': raise ValueError(kind)
    lower=float('inf'); upper=float('inf')
    for j in by[g]:
        args,_=rules[j]; work+=1+len(args)
        lower=min(lower,1+len(args))
        if all(a in fs for a in args): upper=min(upper,1+len(args))
    return upper==lower and lower<float('inf'),work


def select(facts,rules,by,dev,held,method):
    """Return cache, selection work, screening work, prefix length, screened roots."""
    if method=='direct': return (),0,0,0,[]
    if method=='offline':
        lib,work=v.choose(facts,rules,by,dev,(),'support',H)
        return lib,work,0,0,[]
    if method.startswith('prefix_'):
        k=int(method.split('_')[1]); lib,work=v.choose(facts,rules,by,held[:k],(),'support',H-k)
        return lib,work,0,k,[]
    bits=method.split('_'); kind=bits[0]; hard_needed=int(bits[1]) if len(bits)==3 else None
    cap=int(bits[-1]); hard=[]; easy=[]; work=0
    for k,g in enumerate(held[:cap],1):
        is_easy,w=screen(facts,rules,by,g,kind); work+=w
        (easy if is_easy else hard).append(g)
        if hard_needed is not None and len(hard)>=hard_needed: break
    if len(hard)<2: return (),0,work,k,easy
    lib,search=v.choose(facts,rules,by,tuple(hard),(),'support',H-k)
    return lib,search,work,k,easy


def evaluate(split):
    start,count=SPLITS[split]; rows=[]; checks=0
    for ri,regime in enumerate(REGIMES):
        for i in range(count):
            seed=start+ri*1000+i; facts,rules,dev,held=family(seed,regime); by=v.index(rules)
            assert len(set(dev+held))==8+H and not any(a in dev+held for args,_ in rules for a in args)
            ix=tuple(range(len(rules))); base,_,_=v.solve(facts,rules,ix)
            assert base==v.independent(facts,rules); checks+=len(base)
            baseline=sum(base[g] for g in held)+H-1
            # Common uncached search scans on deployment cone. This is a sensitivity only.
            root_ix,_,_=v.cone(rules,by,held); common_dp=sum(1+len(rules[j][0]) for j in root_ix)
            costs={():base}
            for method in METHODS:
                lib,search,observation,k,easy=select(facts,rules,by,dev,held,method)
                assert not set(lib)&set(dev+held)
                if lib not in costs:
                    dd,_,_=v.solve(facts,rules,ix,lib)
                    assert dd==v.independent(facts,rules,lib); checks+=len(dd); costs[lib]=dd
                dd=costs[lib]
                for g in easy:
                    assert base[g]==dd[g]; checks+=1
                build=sum(base[a] for a in lib); savings=sum(base[g]-dd[g] for g in held[k:])
                total=baseline+search+observation+build-savings
                rows.append(dict(seed=seed,regime=regime,method=method,baseline=baseline,total=total,
                                 common_dp=common_dp,prefix=k,selection=search,screen=observation,
                                 construction=build,savings=savings,selected=bool(lib),cache=list(lib),easy=len(easy)))
    return rows,checks


def summary(rows):
    result=[]
    for regime in REGIMES+('all',):
        for method in METHODS:
            rr=[r for r in rows if r['method']==method and (regime=='all' or r['regime']==regime)]
            b,c,dp=[sum(r[x] for r in rr) for x in ('baseline','total','common_dp')]
            result.append(dict(regime=regime,method=method,n=len(rr),baseline=b,total=c,
                               gain=str(Fraction(b,c)),gain_common_dp=str(Fraction(b+dp,c+dp)),
                               profitable=sum(r['total']<r['baseline'] for r in rr),selected=sum(r['selected'] for r in rr),
                               zero_savings_selected=sum(r['selected'] and not r['savings'] for r in rr),
                               prefix=sum(r['prefix'] for r in rr),screen=sum(r['screen'] for r in rr),
                               selection=sum(r['selection'] for r in rr)))
    return result


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    cal,c=evaluate('cal'); cs=summary(cal)
    choice=min((r for r in cs if r['regime']=='all' and r['method'] in ADAPT),key=lambda r:(r['total'],r['method']))['method']
    fixed=min((r for r in cs if r['regime']=='all' and r['method'] in FIXED),key=lambda r:(r['total'],r['method']))['method']
    freeze=dict(protocol='VAD-06D',splits=SPLITS,chosen_adaptive=choice,chosen_fixed=fixed,
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),parent_sha256=sha256(Path(v.__file__).read_bytes()).hexdigest(),calibration=cs)
    (out/'freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    test,x=evaluate('test'); report=dict(**freeze,checks=c+x,test_checks=x,test=summary(test),records=test,evidence='exact synthetic costs; prefix-only selection; no new Lean replay')
    (out/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    r=run(a.out); print('chosen',r['chosen_adaptive'],r['chosen_fixed'],'checks',r['checks'],'records',len(r['records']))
    for x in r['test']:
        if x['method'] in ('direct','prefix_4',r['chosen_fixed'],r['chosen_adaptive']): print(x)

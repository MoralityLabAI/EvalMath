"""VAD-06C: prospective prefix-only Horn cache selection and marginal gates."""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

import verify_vad_horn as v
import verify_vad_transfer as t

SPLITS = {'cal': (98000, 12), 'test': (108000, 24)}
PREFIXES = (2, 4, 8, 16)
METHODS = ('direct', 'support', 'pilot_marginal', 'pilot_full') + tuple(f'{mode}_{k}' for mode in ('online_support','online_exact','online_trigger') for k in PREFIXES)


def certificate(facts, rules, by, goal, cache, base):
    """One-step proof certificate with cached premise and original proofs for others."""
    assert len(cache)==1
    a=cache[0]; best=base[goal]; work=1
    for j in by[goal]:
        args,_=rules[j]; work+=1+len(args)
        best=min(best,1+sum(1 if u==a else base[u] for u in args))
    return base[goal]-best,work


def evaluate(split):
    start,count=SPLITS[split]; rows=[]; checks=0
    for ri,regime in enumerate(t.REGIMES):
        for i in range(count):
            seed=start+ri*1000+i; facts,rules,dev,probe,held=t.family(seed,regime); by=v.index(rules)
            ix=tuple(range(len(rules))); base,_,_=v.solve(facts,rules,ix)
            assert base==v.independent(facts,rules); checks+=len(base)
            assert len(set(dev+probe+held))==8+t.P+t.H
            assert not any(a in dev+probe+held for args,_ in rules for a in args)
            baseline=sum(base[g] for g in probe+held)+t.P+t.H-2
            cache0,search0=v.choose(facts,rules,by,dev,(),'support',t.H)
            costs={}
            def cached(cache):
                nonlocal checks
                if cache not in costs:
                    dd,_,_=v.solve(facts,rules,ix,cache)
                    assert dd==v.independent(facts,rules,cache); checks+=len(dd)
                    costs[cache]=dd
                return costs[cache]
            d0=cached(cache0); build0=sum(base[a] for a in cache0)
            for method in METHODS:
                cache,search,k,validation=(),0,0,0
                if method=='support': cache,search=cache0,search0
                elif method.startswith('pilot_'):
                    search=search0
                    if cache0:
                        prefix=t.probe_prefix(facts,rules,by,probe[:4],cache0,base)
                        s,validation=prefix[-1]; validation+=1
                        charge=build0+(search+validation if method=='pilot_full' else 0)
                        if t.H*s>4*charge: cache=cache0
                elif method.startswith(('online_support_','online_exact_')):
                    mode,ks=method.rsplit('_',1); k=int(ks)
                    cache,search=v.choose(facts,rules,by,held[:k],(),('support' if mode=='online_support' else 'support_exact'),t.H-k)
                elif method.startswith('online_trigger_'):
                    cap=int(method.rsplit('_',1)[1]); search=search0
                    if cache0:
                        for k,g in enumerate(held[:cap],1):
                            saving,w=certificate(facts,rules,by,g,cache0,base); validation+=w+1
                            assert 0<=saving<=base[g]-d0[g]; checks+=1
                            if saving*(t.H-k)>build0:
                                cache=cache0; break
                assert not set(cache)&set(dev+probe+held)
                # The full solve is an ex post scoring oracle; no future costs enter decisions.
                dd=cached(cache); future=sum(base[g]-dd[g] for g in held[k:]); build=sum(base[a] for a in cache)
                total=baseline+search+validation+build-future
                rows.append(dict(seed=seed,regime=regime,method=method,baseline=baseline,total=total,selected=bool(cache),prefix=k,selection=search,validation=validation,construction=build,savings=future,cache=list(cache)))
    return rows,checks


def summary(rows):
    out=[]
    for regime in t.REGIMES+('all',):
        for method in METHODS:
            rr=[r for r in rows if r['method']==method and (regime=='all' or r['regime']==regime)]
            b,c=[sum(r[k] for r in rr) for k in ('baseline','total')]
            out.append(dict(regime=regime,method=method,baseline=b,total=c,gain=str(Fraction(b,c)),profitable=sum(r['total']<r['baseline'] for r in rr),selected=sum(r['selected'] for r in rr),zero_savings_selected=sum(r['selected'] and not r['savings'] for r in rr),selection=sum(r['selection'] for r in rr),validation=sum(r['validation'] for r in rr),prefix=sum(r['prefix'] for r in rr)))
    return out


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    cal,c=evaluate('cal'); cs=summary(cal)
    choice=min((r for r in cs if r['regime']=='all' and r['method'] not in ('direct','support')),key=lambda r:(r['total'],r['method']))['method']
    freeze=dict(protocol='VAD-06C',splits=SPLITS,chosen=choice,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependencies={Path(m.__file__).name:sha256(Path(m.__file__).read_bytes()).hexdigest() for m in (v,t)},calibration=cs)
    (out/'freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    test,x=evaluate('test'); report=dict(**freeze,checks=c+x,test_checks=x,test=summary(test),records=test,evidence='exact synthetic cost oracle; prefix-only decisions; no new kernel replay')
    (out/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); return report


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    r=run(a.out); print('chosen',r['chosen'],'checks',r['checks'],'records',len(r['records']))
    for row in r['test']:
        if row['method'] in ('direct','support',r['chosen'],'pilot_marginal','pilot_full'): print(row)

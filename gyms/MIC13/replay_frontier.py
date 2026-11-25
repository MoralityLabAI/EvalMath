"""Replay serialized MIC-13 proof DAGs, reject representative tampering, generate planner input."""
from mic13 import *
from copy import deepcopy
from fractions import Fraction as F
from statistics import mean


def audit():
    path=Path(__file__).parent;raw=json.loads((path/'results.json').read_text());seen=set();counts=Counter();tests={};start=perf_counter()
    expected={(r['kind'],r['n'],r['family'],r['seed'],m):a for r in raw['rows'] for m,a in r['arms'].items()}
    def reject(label,d,p,mutate):
        if label in tests:return
        q=deepcopy(p);mutate(q)
        try:Checker(d).check(q)
        except (ValueError,AssertionError,KeyError,IndexError,TypeError):tests[label]=True
        else:raise AssertionError('tampering accepted: '+label)
    with gzip.open(path/'proofs.jsonl.gz','rt',encoding='utf-8') as f:
        for line in f:
            row=json.loads(line);key=tuple(row[k] for k in ('kind','n','family','seed','mode'));assert key in expected and key not in seen;seen.add(key)
            d=instance(row['family'],row['seed'],row['n'],row['kind']);p=row['proof'];a=Checker(d).check(p);assert a==expected[key]['replay'];counts.update(a['counts'])
            reject('false upper',d,p,lambda q:q.update(upper=q['upper']+1))
            reject('false lower',d,p,lambda q:q.update(value=q['value']+1))
            reject('false normalization',d,p,lambda q:q['nodes'][0].update(prop=['0x0','0x0']))
            reject('unreachable node',d,p,lambda q:q['nodes'].append(deepcopy(q['nodes'][0])))
            reject('wrong work ledger',d,p,lambda q:q.update(normalizations=q['normalizations']+2))
            for i,n in enumerate(p['nodes']):
                if n['kind']=='branch':
                    reject('missing branch',d,p,lambda q:q['nodes'][i]['children'].pop())
                    reject('swapped branches',d,p,lambda q:q['nodes'][i]['children'].reverse())
                if n['kind'] in ('pruned','open') and n['cliques']:
                    reject('missing clique',d,p,lambda q:q['nodes'][i]['cliques'].pop())
                if n['kind']=='open' and a['upper']>a['lower'] and Checker(d).clique(unpair(n['state'])[0],n['cliques'])>a['lower']:
                    reject('unsafe pruning',d,p,lambda q:q['nodes'][i].update(kind='pruned'))
                if n['components'] and n['components'][0][1] is not None:
                    reject('false component infeasibility',d,p,lambda q:q['nodes'][i]['components'][0].__setitem__(1,None))
                if n['kind']=='ve':
                    reject('false residual value',d,p,lambda q:q['nodes'][i]['receipt'].update(value=-999))
                    reject('wrong residual state',d,p,lambda q:q['nodes'][i]['receipt'].update(active='0x0'))
    assert seen==set(expected) and len(tests)==12,(len(seen),tests)
    out=dict(schema='MIC-13/serialized-replay/v1',proofs=len(seen),nodes=sum(v for k,v in counts.items() if k not in ('components','ve_cells')),counts=dict(counts),rejected_mutations=tests,proof_sha256=hashlib.sha256((path/'proofs.jsonl.gz').read_bytes()).hexdigest(),elapsed_s=perf_counter()-start)
    pilot=[]
    for f in FAMILIES:
        effects=[]
        for r in raw['rows']:
            if r['family']!=f:continue
            d=instance(f,r['seed'],r['n'],r['kind']);a,b=r['arms']['baseline'],r['arms']['periodic'];effects.append(F((a['upper']-a['value'])-(b['upper']-b['value']),sum(d.w)))
        pilot.append(dict(unit_id=f,paired_effect=str(mean(effects)),sham_effects=['0']))
    spec=dict(schema_version=1,experiment_id='MIC-13-public-frontier',independent_unit='generator lineage (independence unverified)',alpha='1/20',scientific_min_effect='1/20',target_effect='1/10',measurement_resolution='0',sham_quantile='19/20',sham_confidence='19/20',planned_comparisons=1,confirm_units_planned=128,pilot_from_development_only=True,heldout_sealed=False,units_independent=False,pilot=pilot)
    (path/'audit_results.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');(path/'preflight_input.json').write_text(json.dumps(spec,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':audit()

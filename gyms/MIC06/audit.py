"""Retrospective controls; independent exact verifier remains authoritative."""
from run import root, closure, objective, valid, FAMILIES
from fractions import Fraction as F
from pathlib import Path
from itertools import combinations
import json


def global_remove(d):
    """Best weighted loss per removed conflict; scan every conflicted vertex."""
    s,c=closure(d,(1<<len(d.weights))-1);checks=0;decisions=0
    while True:
        edges=[(i,j) for i,j in d.conflicts if s>>i&1 and s>>j&1];checks+=len(d.conflicts)
        if not edges:break
        candidates=[]
        for i in sorted({i for e in edges for i in e}):
            q,w=closure(d,s&~(1<<i));c+=w
            remaining=sum(bool(q>>j&1 and q>>k&1) for j,k in edges);checks+=len(edges)
            loss=objective(d,s)-objective(d,q);removed=len(edges)-remaining
            candidates.append((F(loss,removed),loss,i,q))
        s=min(candidates)[-1];decisions+=1
    assert valid(d,s)
    return dict(mask=s,value=objective(d,s),support_checks=c,conflict_checks=checks,decisions=decisions)


def dynamic_degree(d):
    s,c=closure(d,(1<<len(d.weights))-1);checks=0;decisions=0
    while True:
        edges=[(i,j) for i,j in d.conflicts if s>>i&1 and s>>j&1];checks+=len(d.conflicts)
        if not edges:break
        i,j=edges[0];degree={k:sum(k in e for e in edges) for k in (i,j)}
        k=min((i,j),key=lambda k:(F(d.weights[k],1+degree[k]),-k))
        s,w=closure(d,s&~(1<<k));c+=w;decisions+=1
    assert valid(d,s)
    return dict(mask=s,value=objective(d,s),support_checks=c,conflict_checks=checks,decisions=decisions)


def run_audit(raw):
    rows=[]
    for r in raw['rows']:
        d=root(r['family'],r['seed'],r['n'])
        arms={'global_remove':global_remove(d),'dynamic_degree':dynamic_degree(d)}
        assert all(a['value']<=r['oracle'] for a in arms.values())
        rows.append(dict(family=r['family'],n=r['n'],seed=r['seed'],oracle=r['oracle'],arms=arms))
    train={root(f,s,10) for f in ('conflict','mixed') for s in range(96)}
    dev={root(r['family'],r['seed'],r['n']) for r in raw['rows']}
    assert not train&dev and len(train)==192 and len(dev)==128
    pilot=[]
    for f in FAMILIES:
        roots=[r for r in raw['rows'] if r['family']==f];eff=[];shams=[]
        for r in roots:
            gold=r['oracle'];assert gold>0
            graph=[F(r['arms'][f'graph_{s}']['value'],gold) for s in raw['model_seeds']]
            node=[F(r['arms'][f'self_{s}']['value'],gold) for s in raw['model_seeds']]
            eff.append((sum(graph)-sum(node))/3)
            shams.extend(abs(a-b) for arm in (graph,node) for a,b in combinations(arm,2))
        pilot.append(dict(unit_id=f,paired_effect=str(sum(eff)/len(eff)),sham_effects=[str(max(shams))]))
    spec=dict(schema_version=1,experiment_id='MIC-06-public-cpu',independent_unit='generator lineage (independence unverified)',alpha='1/20',scientific_min_effect='1/20',target_effect='1/10',measurement_resolution='0',sham_quantile='19/20',sham_confidence='19/20',planned_comparisons=1,confirm_units_planned=128,pilot_from_development_only=True,heldout_sealed=False,units_independent=False,pilot=pilot)
    return dict(schema='MIC-06/retrospective-controls/v1',rows=rows,exact_train_dev_duplicates=0,preflight_input=spec)

if __name__=='__main__':
    data=run_audit(json.loads(Path(__file__).with_name('results.json').read_text()))
    print(json.dumps(data,sort_keys=True,indent=2))

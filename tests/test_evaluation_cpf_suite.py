import json
from collections import Counter
from itertools import product
from fractions import Fraction
import pytest
from spiral_ln.evaluation_cpf_suite import (generate, export, derive, digest, FAMILIES, STAGES, arms, score)


def independent(row):
    f,x=row['family'],row['parameters']
    if f=='gate':
        o,t=x; ok=not(o<t); cert=[o,4*o+2]
    elif f=='degree':
        a,p,t=x; from math import prod
        cert=prod([a,*p]); ok=cert<=t
    elif f=='determinant':
        p,a,b,c,d=x; cert=[sum((a*d,b*c))%p,sum((a*d,-b*c))%p]; ok=cert[0]==cert[1]
    elif f=='threshold':
        ns,t=x; cert=sorted(ns)[-1]; ok=all(v<=t for v in ns)
    elif f=='witness':
        n,e,a,g=x; assert all(j in a and j in g for j in e); cert=[i for i in range(n) if i in a and i not in g]; ok=all(j in g for j in a)
    elif f=='polynomial':
        p,a,b,formal=x; c=[i for i,(u,v) in enumerate(zip(a,b)) if (u-v)%p]
        d=[z for z in range(p) if sum((u-v)*pow(z,i,p) for i,(u,v) in enumerate(zip(a,b)))%p]
        cert=[c,d]; ok=not (c if formal else d)
    elif f=='quantifier':
        cols=list(zip(*x[0])); cert=[j for j,c in enumerate(cols) if min(c)==1]; ok=bool(cert)
    elif f=='implication':
        n,s,t,edges=x; valid=[v for v in product((0,1),repeat=n) if v[s] and all(v[i]<=v[j] for i,j in edges)]
        assert valid; cert=[j for j in range(n) if all(v[j] for v in valid)]; ok=all(v[t] for v in valid)
    elif f=='scope':
        n,r,p=x; cert=[i for i in range(n) if i in r and i not in p]; ok=all(i in p for i in r)
    elif f=='joint':
        a,t=x; cert=[a[0],sum(a)]; ok=Fraction(*cert)<=Fraction(t,sum(a))
    else: raise AssertionError(f)
    assert cert==row['certificate']
    assert row['label']==('entailed' if ok else 'unresolved' if f=='scope' else 'counterexample')


def test_census():
    rows=generate('cpf04-public-development-v1',512)
    assert len(rows)==5120 and len({r['id'] for r in rows})==5120
    assert len({r['prompt'] for r in rows})==5120
    for r in rows: independent(r)
    assert Counter((r['family'],r['label']=='entailed') for r in rows)=={(f,b):256 for f in FAMILIES for b in (True,False)}
    p,g=export(rows); assert all(set(r)=={'id','prompt'} for r in p)
    assert digest(p)==digest(export(generate('cpf04-public-development-v1',512))[0])
    assert {r['id'] for r in rows}.isdisjoint(r['id'] for r in generate('fresh-seed-development',8))


def test_panel():
    gold=export(generate('pilot',2,'test'))[1]; panel={}
    for g in gold:
        right=json.dumps({'label':g['label'],'certificate':g['certificate']})
        wrong=json.dumps({'label':'entailed','certificate':None})
        c={(m,s):{'text':right if s in ('direct','refine2') else wrong,'completion':16,'prompt':5,'seconds':1} for m in ('B','I') for s in STAGES}
        panel[g['id']]=arms(c,['B','I'])
    r=score(gold,panel); n=len(gold)
    assert r['arms']['B/direct']['counts']['certified_correct']==n
    assert r['arms']['B/refine']['counts']['certified_correct']==n
    assert r['arms']['B/independent']['counts']['false_authorized']==5
    assert r['arms']['B/serial_agree']['counts']['covered']==0
    assert r['arms']['B/refine']['cost']['completion']==32*n
    assert r['paired']['B/low|I/low']['joint_false']==5
    with pytest.raises(ValueError): score(gold,{})


def test_disagreement_and_invalid_json():
    from spiral_ln.evaluation_cpf_suite import parse, agree
    assert parse('```json\n{}\n```') is None
    assert parse('{"label":"yes","certificate":0}') is None
    a=parse('{"label":"entailed","certificate":[1]}'); b=parse('{"label":"entailed","certificate":[2]}')
    assert agree(a,b) is None and agree(a,a)==a


def test_three_null_correlation_controls():
    gold=[{'id':str(i),'family':'synthetic','label':'counterexample','certificate':i} for i in range(100)]
    for mode,expected in [('shared',10),('independent',1),('disjoint',0)]:
        panel={}
        for i,g in enumerate(gold):
            a=i<10; b=i<10 if mode=='shared' else i%10==0 if mode=='independent' else 10<=i<20
            panel[g['id']]={m:{'answer':{'label':'entailed' if wrong else 'counterexample','certificate':i},'completion':0,'prompt':0,'seconds':0} for m,wrong in [('a',a),('b',b)]}
        r=score(gold,panel)['paired']['a|b']
        assert (r['a_false'],r['b_false'],r['joint_false'])==(10,10,expected)
        assert Fraction(r['joint_minus_product'])==Fraction(expected-1,100)
    first=generate('fresh',8,'test'); second=generate('fresh',8,'test',exclude=[r['id'] for r in first])
    assert {r['id'] for r in first}.isdisjoint(r['id'] for r in second)

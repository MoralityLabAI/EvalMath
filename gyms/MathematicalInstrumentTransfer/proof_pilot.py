"""MIT-06 development-only certificate-neutral prompt fixtures and symbolic smoke pilot."""
import argparse,json,hashlib,time
from pathlib import Path
from random import Random
from itertools import product
from fractions import Fraction as F
import development as d

ARMS=('unaided','source','instrument','near_miss','oracle','sham')
FAMILIES=('lp','path','cover','congruence')
SOURCE={
'lp':'A shipping firm has two certified resource inequalities. Adding nonnegative multiples gives a valid upper bound on its combined shipment score.',
'path':'For a sequence of balances, if every increase is bounded by the difference of two accounting potentials, the sum is bounded by the endpoint difference.',
'cover':'If two component requirements are lower bounds, adding nonnegative multiples of them proves a lower bound on total required resources.',
'congruence':'In a cyclic checksum system, a linear combination of valid equations remains valid modulo the checksum modulus. Zero on one side and a nonzero residue on the other is impossible.'}
INSTRUMENT={
'lp':'Check a nonnegative combination of constraints, matching the objective coefficients exactly. Find an attaining feasible point.',
'path':'Check a potential inequality on each edge and the difference of endpoint potentials. Find a path attaining the bound.',
'cover':'Check a nonnegative combination of lower inequalities, matching the objective coefficients exactly. Find an attaining feasible point.',
'congruence':'Find a vector of coefficients whose linear combination makes every variable coefficient zero modulo p but leaves a nonzero constant.'}

def cover(seed):
    r=Random(seed); A=[[r.randint(1,9) for _ in range(2)] for _ in range(2)];x=[r.randint(1,6) for _ in range(2)];y=[r.randint(1,5) for _ in range(2)];b=[d.dot(a,x) for a in A];c=[sum(y[i]*A[i][j] for i in range(2)) for j in range(2)];t=dict(family='cover',A=A,b=b,c=c,box=8,bound=d.dot(c,x));return t,y,[y[0]+1,y[1]],x

def congruence(seed):
    r=Random(seed);p=r.choice((5,7,11,13));a=[r.randrange(p) for _ in range(2)];a[0]=r.randrange(1,p);k=r.randrange(1,p);x=[r.randrange(p) for _ in range(2)];b0=d.dot(a,x)%p
    A=[a,[(k*z)%p for z in a]];b=[b0,(k*b0+r.randrange(1,p))%p];t=dict(family='congruence',A=A,b=b,p=p);good=[(-k)%p,1];bad=[(1-k)%p,1];return t,good,bad,x

def mapping_valid(t,m):
    family=t['family']
    if family in ('lp','path'):return d.mapping_valid(t,m)
    if family=='cover':return d.ints(m,2) and min(m)>=0 and [sum(m[i]*t['A'][i][j] for i in range(2)) for j in range(2)]==t['c'] and d.dot(m,t['b'])>=t['bound']
    p=t['p'];return d.ints(m,2) and all(sum(m[i]*t['A'][i][j] for i in range(2))%p==0 for j in range(2)) and d.dot(m,t['b'])%p!=0

def witness_value(t,x):
    family=t['family']
    if family in ('lp','path'):return d.witness_value(t,x)
    if family=='cover':
        if not d.ints(x,2) or not all(0<=z<=t['box'] for z in x) or any(d.dot(a,x)<b for a,b in zip(t['A'],t['b'])):return None
        return d.dot(t['c'],x)
    if not d.ints(x,2) or not all(0<=z<t['p'] for z in x):return None
    return int(all(d.dot(a,x)%t['p']==b for a,b in zip(t['A'],t['b'])))

def verify(t,r):
    if not isinstance(r,dict):return False
    family=t['family'];v=witness_value(t,r.get('witness'));m=r.get('certificate');verdict=r.get('verdict')
    if family=='congruence':return mapping_valid(t,m) if verdict=='proved' else verdict=='counterexample' and v==1
    if verdict=='counterexample':return v is not None and (v<t['bound'] if family=='cover' else v>t['bound'])
    return verdict=='proved' and v==t['bound'] and mapping_valid(t,m)

def independent(t):
    family=t['family']
    if family in ('lp','path'):return d.independent_max(t)
    if family=='cover':return min(d.dot(t['c'],x) for x in product(range(t['box']+1),repeat=2) if all(d.dot(a,x)>=b for a,b in zip(t['A'],t['b'])))
    return any(all(d.dot(a,x)%t['p']==b for a,b in zip(t['A'],t['b'])) for x in product(range(t['p']),repeat=2))

def false_variant(t,x):
    s=t.copy()
    if t['family']=='congruence':s['b']=[d.dot(a,x)%t['p'] for a in t['A']]
    else:s['bound']=t['bound']+(1 if t['family']=='cover' else -1)
    return s

def prompt(t,arm,m=None):
    f=t['family'];data={k:v for k,v in t.items() if k!='family'}
    claim={'lp':'The exact maximum of c dot x for integer 0<=x<=box and A*x<=b equals bound.', 'cover':'The exact minimum of c dot x for integer 0<=x<=box and A*x>=b equals bound.', 'path':'The maximum total edge weight along a directed path from 0 to n-1 equals bound. Each edge is [from,to,weight].','congruence':'There is no vector of two residues x modulo p satisfying A*x=b modulo p.'}[f]
    text=claim+'\nData: '+json.dumps(data,sort_keys=True)+'\nReturn one JSON object: verdict (proved or counterexample), certificate (integer list or null), witness (integer list or null). A proved result requires a checkable certificate; supply an attaining witness for a sharp bound. A counterexample requires a witness refuting the claim.'
    if arm=='source':text+='\nRelated source: '+SOURCE[f]
    elif arm=='instrument':text+='\nSuggested technique: '+INSTRUMENT[f]
    elif arm in ('near_miss','oracle'):text+='\nSuggested technique: '+INSTRUMENT[f]+' Candidate certificate: '+json.dumps(m)+'. Also return mapping_valid (boolean) for the candidate, even if replacing it.'
    elif arm=='sham':text+='\nRelated source: '+SOURCE['congruence' if f!='congruence' else 'path']
    return text

def fixtures():
    for f,make in zip(FAMILIES,(d.lp,d.path,cover,congruence)):
        for i in range(32):
            t,good,bad,x=make(83000+i+1000*FAMILIES.index(f));neg=false_variant(t,x);rid=f'{f}-open-{i:02d}'
            assert mapping_valid(t,good) and not mapping_valid(t,bad)
            assert independent(t)==(False if f=='congruence' else t['bound'])
            assert independent(neg)==(True if f=='congruence' else t['bound'])
            assert verify(t,dict(verdict='proved',certificate=good,witness=x))
            assert verify(neg,dict(verdict='counterexample',certificate=None,witness=x))
            for variant,target,arms in [('true',t,ARMS),('false',neg,('unaided','instrument'))]:
                for arm in arms:
                    candidate=good if arm=='oracle' else bad if arm=='near_miss' else None
                    public=dict(row_id=f'{rid}-{variant}-{arm}',prompt=prompt(target,arm,candidate))
                    secret=dict(row_id=public['row_id'],root_id=rid,family=f,variant=variant,arm=arm,target=target,candidate=candidate,expected_mapping_valid=mapping_valid(target,candidate) if candidate is not None else None)
                    yield public,secret

def solve(t):
    """Independent symbolic constructor. Reads the problem instance, never gold."""
    family=t['family'];checks=0
    if family=='path':
        p=[None]*t['n'];pred=[None]*t['n'];p[0]=0
        for u in range(t['n']):
            if p[u] is None:continue
            for a,b,w in t['edges']:
                if a==u:
                    checks+=1;z=p[u]+w
                    if p[b] is None or z>p[b]:p[b]=z;pred[b]=u
        path=[t['n']-1]
        while path[-1]:path.append(pred[path[-1]])
        path.reverse();v=p[-1];cert=p
    elif family=='congruence':
        p=t['p'];A=t['A'];b=t['b'];k=A[1][0]*pow(A[0][0],-1,p)%p;cert=[(-k)%p,1];checks+=1
        if mapping_valid(t,cert):return dict(verdict='proved',certificate=cert,witness=None),checks
        for x in product(range(p),repeat=2):
            checks+=1
            if witness_value(t,list(x))==1:return dict(verdict='counterexample',certificate=None,witness=list(x)),checks
        raise ValueError('failed constructor')
    else:
        A=t['A'];a,b=A[0];c,d0=A[1];det=a*d0-b*c;rhs=t['b'];obj=t['c'];cert=None;path=None
        if det:
            yy=[F(obj[0]*d0-obj[1]*c,det),F(a*obj[1]-b*obj[0],det)]
            xx=[F(rhs[0]*d0-b*rhs[1],det),F(a*rhs[1]-rhs[0]*c,det)];checks+=1
            if all(z.denominator==1 and z>=0 for z in yy) and all(z.denominator==1 and 0<=z<=t['box'] for z in xx):cert=list(map(int,yy));path=list(map(int,xx))
        if cert is None:
            for y in product(range(1,6),repeat=2):
                checks+=1
                if [sum(y[i]*A[i][j] for i in range(2)) for j in range(2)]==obj:cert=list(y);break
        if path is None:
            for x in product(range(t['box']+1),repeat=2):
                checks+=1
                if [d.dot(a,x) for a in A]==rhs:path=list(x);break
        v=witness_value(t,path)
    false=v<t['bound'] if family=='cover' else v>t['bound']
    return dict(verdict='counterexample' if false else 'proved',certificate=None if false else cert,witness=path),checks

def score(secret,response):
    valid=verify(secret['target'],response);gold=secret['expected_mapping_valid'];reported=response.get('mapping_valid') if isinstance(response,dict) else None
    return dict(verified=valid,applicability_correct=None if gold is None else type(reported) is bool and reported==gold)

def main(out):
    out.mkdir(parents=True,exist_ok=True);pub=[];sec=[];rows=[];start=time.perf_counter()
    for p,s in fixtures():
        pub.append(p);sec.append(s);r,checks=solve(s['target'])
        if s['candidate'] is not None:r['mapping_valid']=mapping_valid(s['target'],s['candidate'])
        rows.append(dict(row_id=p['row_id'],family=s['family'],root_id=s['root_id'],variant=s['variant'],arm=s['arm'],checks=checks,**score(s,r)))
    assert all(r['verified'] and r['applicability_correct'] is not False for r in rows)
    for file,entries in [('proof_prompts.jsonl',pub),('proof_private.jsonl',sec),('proof_symbolic_rows.jsonl',rows)]:
        (out/file).write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in entries))
    res=dict(schema='mit06-symbolic-open-dev-v1',families=len(FAMILIES),roots=len({s['root_id'] for s in sec}),rows=len(rows),verified=sum(r['verified'] for r in rows),applicability_checks=sum(r['applicability_correct'] is not None for r in rows),applicability_correct=sum(r['applicability_correct'] is True for r in rows),elapsed_s=time.perf_counter()-start,model_runs=0,sealed_roots=0,prompt_manifest_sha256=hashlib.sha256((out/'proof_prompts.jsonl').read_bytes()).hexdigest(),source_sha256={x:hashlib.sha256(Path(__file__).with_name(x).read_bytes()).hexdigest() for x in ('proof_pilot.py','development.py')})
    (out/'proof_result.json').write_text(json.dumps(res,indent=2)+'\n');print(res)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);main(p.parse_args().output)

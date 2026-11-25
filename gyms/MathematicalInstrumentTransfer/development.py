"""MIT-01B development-only fixtures; exact integer certificates, no model runs."""
import argparse
import json
from itertools import product
from pathlib import Path
from random import Random

ARMS = ('unaided', 'source', 'instrument', 'near_miss', 'oracle', 'sham')


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def ints(x, n):
    return isinstance(x, list) and len(x) == n and all(type(v) is int for v in x)


def lp(seed):
    r = Random(seed)
    a = [[r.randint(1, 9) for _ in range(2)] for _ in range(2)]
    x = [r.randint(1, 6) for _ in range(2)]
    y = [r.randint(1, 5) for _ in range(2)]
    b = [dot(row, x) for row in a]
    c = [sum(y[i]*a[i][j] for i in range(2)) for j in range(2)]
    t = {'family': 'lp', 'A': a, 'b': b, 'c': c, 'box': 8, 'bound': dot(c, x)}
    return t, y, [y[0]+1, y[1]], x


def path(seed):
    r = Random(seed)
    p = [0]
    for _ in range(r.randint(4, 7)):
        p.append(p[-1]+r.randint(1, 9))
    n = len(p)
    edges = [[i, i+1, p[i+1]-p[i]] for i in range(n-1)]
    for i in range(n-2):
        for j in range(i+2, n):
            if r.randrange(2):
                edges.append([i,j,p[j]-p[i]-r.randint(0, 3)])
    bad = p[:]
    bad[1] += 1
    t = {'family':'path', 'n':n, 'edges':edges, 'bound':p[-1]}
    return t, p, bad, list(range(n))


def mapping_valid(t, m):
    if t['family'] == 'lp':
        return (ints(m, len(t['b'])) and min(m)>=0
                and [sum(m[i]*t['A'][i][j] for i in range(len(m))) for j in range(2)] == t['c']
                and dot(m,t['b']) <= t['bound'])
    return (ints(m,t['n']) and all(w <= m[v]-m[u] for u,v,w in t['edges'])
            and m[-1]-m[0] <= t['bound'])


def witness_value(t, x):
    if t['family'] == 'lp':
        if not ints(x,2) or not all(0<=z<=t['box'] for z in x) or any(dot(row,x)>b for row,b in zip(t['A'],t['b'])):
            return None
        return dot(t['c'],x)
    if not isinstance(x,list) or not x or not ints(x,len(x)) or x[0]!=0 or x[-1]!=t['n']-1:
        return None
    edges = {(u,v):w for u,v,w in t['edges']}
    if any((u,v) not in edges for u,v in zip(x,x[1:])):
        return None
    return sum(edges[u,v] for u,v in zip(x,x[1:]))


def verify(t, response):
    """Verify a true maximum certificate or a counterexample to the claimed bound."""
    if not isinstance(response,dict):
        return False
    v = witness_value(t,response.get('witness'))
    if v is None:
        return False
    if response.get('verdict') == 'counterexample':
        return v > t['bound']
    return response.get('verdict') == 'proved' and v == t['bound'] and mapping_valid(t,response.get('mapping'))


def independent_max(t):
    if t['family'] == 'lp':
        return max(sum(c*x for c,x in zip(t['c'],z)) for z in product(range(t['box']+1),repeat=2)
                   if all(sum(a*x for a,x in zip(row,z))<=b for row,b in zip(t['A'],t['b'])))
    def paths(u,total):
        if u==t['n']-1:
            yield total
        else:
            for s,v,w in t['edges']:
                if s==u:
                    yield from paths(v,total+w)
    return max(paths(0,0))


SOURCES = {
    'lp': 'Source: x+y<=5 and 2*x+y<=8 imply 3*x+2*y<=13 by adding both inequalities. Nonnegative combinations preserve upper bounds.',
    'path': 'Source: a walk with edge weights w(u,v)<=p(v)-p(u) has weight at most p(end)-p(start), since the differences telescope.'}
INSTRUMENTS = {
    'lp': 'Use nonnegative multipliers on the constraints. Check that their linear combination has exactly the requested objective coefficients and an upper bound no larger than the claim.',
    'path': 'Use a potential on vertices. Check every permitted transition against its potential difference and compare endpoint difference to the claimed bound.'}


def prompt(t, arm, mapping=None):
    """Common certificate menu exposes the method; measures guided execution only."""
    if arm not in ARMS:
        raise ValueError('unknown arm')
    task = ('Maximize c dot x over integer 0<=x<=box subject to A*x<=b.' if t['family']=='lp'
            else 'Maximize total edge weight over directed paths from vertex 0 to n-1; edges are [start,end,weight].')
    contract = ('Return JSON with verdict proved and mapping (nonnegative integer multipliers for lp, integer vertex potentials for path), plus witness attaining bound (integer vector or vertex path). If the bound is false return verdict counterexample and a witness exceeding it.')
    extra = ''
    if arm=='source':
        extra = SOURCES[t['family']]
    elif arm=='instrument':
        extra = INSTRUMENTS[t['family']]
    elif arm in ('oracle','near_miss'):
        extra = INSTRUMENTS[t['family']]+' Candidate mapping: '+json.dumps(mapping)+'. Include mapping_valid (boolean) for the supplied candidate even if you replace it.'
    elif arm=='sham':
        extra = SOURCES['path' if t['family']=='lp' else 'lp']
    return task+' Claimed exact maximum: '+json.dumps(t,sort_keys=True)+'\n'+contract+'\n'+extra


def fixtures():
    for make in (lp,path):
        for seed in range(32):
            t,good,bad,x = make(71000+seed)
            rid = f"{t['family']}-dev-{seed:02d}"
            false_t = dict(t,bound=t['bound']-1)
            assert independent_max(t)==t['bound']
            assert mapping_valid(t,good) and not mapping_valid(t,bad)
            assert verify(t,{'verdict':'proved','mapping':good,'witness':x})
            assert verify(false_t,{'verdict':'counterexample','witness':x})
            for variant,target in [('true',t),('false',false_t)]:
                for arm in ARMS if variant=='true' else ('unaided','instrument'):
                    m = good if arm=='oracle' else bad if arm=='near_miss' else None
                    public = {'root_id':rid,'variant':variant,'arm':arm,'target':target,'prompt':prompt(target,arm,m)}
                    gold = {'root_id':rid,'variant':variant,'arm':arm,'mapping':good,'witness':x,'mapping_valid':mapping_valid(target,m) if m is not None else None,'verdict':'proved' if variant=='true' else 'counterexample'}
                    yield public,gold


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    rows=list(fixtures())
    for name,col in [('development_prompts.jsonl',0),('development_gold.jsonl',1)]:
        (args.output/name).write_text(''.join(json.dumps(r[col],sort_keys=True)+'\n' for r in rows))
    print(f'{len(set(r[0]["root_id"] for r in rows))} development roots; {len(rows)} rows; no sealed split')


if __name__=='__main__':
    main()

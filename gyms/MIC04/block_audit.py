"""Atomic SCC repair and independent replay audit for MIC-04."""
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
from run import FAMILIES,make,h,valid,initial,least,terminal


def components(m):
    n=len(m);reach=[]
    for u in range(n):
        seen={u};stack=[u]
        while stack:
            v=stack.pop()
            for w in range(n):
                if m[v][w] and w not in seen:seen.add(w);stack.append(w)
        reach.append(seen)
    groups=[];left=set(range(n))
    while left:
        u=min(left);s=tuple(v for v in sorted(left) if v in reach[u] and u in reach[v]);groups.append(s);left.difference_update(s)
    return groups


def repair(d):
    m,b=d;p=initial(d);groups=components(m);pending=list(groups);rows=0;commits=0
    while pending:
        todo={j for s in pending for j in s}
        s=next(s for s in pending if all(not m[i][j] for i in s for j in todo.difference(s)))
        q=list(p)
        for i in s:q[i]=0
        while True:
            v=[h(d,q,i) for i in s];rows+=len(s)
            assert all(q[i]<=x<=p[i] for i,x in zip(s,v))
            if all(q[i]==x for i,x in zip(s,v)):break
            for i,x in zip(s,v):q[i]=x
        q=tuple(q)
        assert valid(d,q) and all(x<=y for x,y in zip(q,p))
        p=q;pending.remove(s);commits+=1
    return p,rows,commits


def audit():
    raw=json.loads(Path(__file__).with_name('results.json').read_text());out=[]
    for r in raw['rows']:
        if r['K']!=16:continue
        d=make(r['family'],r['seed'],r['n']);q,checks,commits=repair(d)
        assert q==least(d) and sum(q)==r['least']
        out.append({'family':r['family'],'n':r['n'],'seed':r['seed'],'least':sum(q),'terminal':sum(terminal(d)),
                    'internal_row_evals':checks,'atomic_commits':commits,'post_commit_full_checks':commits})
    return {'schema':'MIC-04/block-audit/v1','rows':out,'scope':'full SCC solves; extra internal work, distinct action class, no equal-budget claim'}


if __name__=='__main__':print(json.dumps(audit(),sort_keys=True,indent=2))

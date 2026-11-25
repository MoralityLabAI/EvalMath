"""Exact threshold closure for uniform jumps; SCC comparison."""
from collections import deque
from run import FAMILIES,root,fixed,slack,valid,prune,jump,best_jump
import json


def threshold(d,p,t):
    """Largest feasible t-decrement block, with t a positive integer."""
    if type(t) is not int or t<1:raise ValueError('positive integer jump required')
    m,b=d;s=slack(d,p);n=len(b);assert valid(d,p)
    active={i for i in range(n) if p[i]>=t}
    inc=[[] for _ in b];out=[[] for _ in b];work=0
    for i,row in enumerate(m):
        for j,a in enumerate(row):
            if a:inc[j].append((i,a));out[i].append((j,a));work+=1
    sup={i:sum(a for j,a in out[i] if j in active) for i in active}
    work+=sum(len(out[i]) for i in active)
    q=deque(i for i in sorted(active) if s[i]<t*(10-sup[i]))
    while q:
        j=q.popleft()
        if j not in active:continue
        active.remove(j)
        for i,a in inc[j]:
            work+=1
            if i in active:
                sup[i]-=a
                if s[i]<t*(10-sup[i]):q.append(i)
    return tuple(sorted(active)),work


def exact_jump(d,p):
    m,b=d;s=slack(d,p)
    cap=max(min(p[i],s[i]//(10-sum(row))) for i,row in enumerate(m))
    candidates=[];work=0
    for t in range(1,cap+1):
        S,w=threshold(d,p,t);work+=w
        if not S:break
        q=tuple(v-t if i in S else v for i,v in enumerate(p));assert valid(d,q)
        candidates.append((len(S)*t,t,S))
    return max(candidates,default=(0,0,())),work


def scc_repair(d,p):
    m,b=d;n=len(b);reach=[]
    for i in range(n):
        seen={i};stack=[i]
        while stack:
            v=stack.pop()
            for j,a in enumerate(m[v]):
                if a and j not in seen:seen.add(j);stack.append(j)
        reach.append(seen)
    groups=[];pending=set(range(n))
    while pending:
        i=min(pending);g=tuple(j for j in sorted(pending) if j in reach[i] and i in reach[j]);groups.append(g);pending.difference_update(g)
    row_evals=arc_terms=commits=0
    while groups:
        remaining={i for g in groups for i in g}
        g=next(g for g in groups if all(not m[i][j] for i in g for j in remaining.difference(g)))
        q=list(p)
        for i in g:q[i]=0
        while True:
            new=[b[i]+(sum(a*z for a,z in zip(m[i],q))+9)//10 for i in g]
            row_evals+=len(g);arc_terms+=sum(sum(a!=0 for a in m[i]) for i in g)
            assert all(q[i]<=v<=p[i] for i,v in zip(g,new))
            if all(q[i]==v for i,v in zip(g,new)):break
            for i,v in zip(g,new):q[i]=v
        q=tuple(q);assert valid(d,q);p=q;groups.remove(g);commits+=1
    return p,{'row_evals':row_evals,'nonzero_terms':arc_terms,'atomic_commits':commits}


def audit():
    rows=[]
    for f in FAMILIES:
        for n in (6,8):
            for seed in range(1000,1016):
                d=root(f,seed,n);p,_=fixed(d,True);gold,_=fixed(d,False)
                (best,t,S),work=exact_jump(d,p);q,c=scc_repair(d,p)
                assert best==best_jump(d,p) and q==gold
                rows.append({'family':f,'n':n,'seed':seed,'best_jump':best,'jump':t,'block':S,'threshold_edge_work':work,'scc':c})
    return rows

if __name__=='__main__':print(json.dumps(audit(),indent=2,sort_keys=True))

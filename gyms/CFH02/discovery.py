"""CFH-02 public finite graph-polynomial discovery pilot (Python 3.10+, SymPy)."""
from collections import Counter
from functools import cache
from itertools import combinations
from math import comb, factorial
import json
import random
import sympy as sp

X = sp.Symbol('x')
FAMILIES = ('path','cycle','star','complete','bipartite','matching','wheel','barbell','empty','tree')
INVARIANTS = ('independence','clique','matching','chromatic','domination')
BUDGETS = (1,2,4,6)
POLICIES = ('direct','degree_rank','newton_only','ladder','ladder_degree_rank')
DECK = 6


def graph(f,n,seed):
    e=set()
    def add(i,j): e.add(tuple(sorted((i,j))))
    if f in ('path','cycle','wheel'):
        k=n-1 if f=='wheel' else n
        for i in range(k-1): add(i,i+1)
        if f!='path': add(0,k-1)
        if f=='wheel':
            for i in range(k): add(i,n-1)
    elif f=='star':
        for i in range(1,n): add(0,i)
    elif f=='complete': e.update(combinations(range(n),2))
    elif f=='bipartite':
        for i in range(n//2):
            for j in range(n//2,n): add(i,j)
    elif f=='matching':
        for i in range(0,n-1,2): add(i,i+1)
    elif f=='barbell':
        k=n//2
        e.update(combinations(range(k),2)); e.update(combinations(range(k,n),2)); add(k-1,k)
    elif f=='tree':
        r=random.Random(seed)
        for i in range(1,n): add(i,r.randrange(i))
    elif f!='empty': raise ValueError(f)
    labels=list(range(n)); random.Random(seed^0x415).shuffle(labels)
    return n,tuple(sorted(tuple(sorted((labels[i],labels[j]))) for i,j in e))


def neighbors(g):
    n,edges=g; adj=[0]*n
    for i,j in edges: adj[i]|=1<<j; adj[j]|=1<<i
    return adj


def trim(a):
    a=list(a)
    while len(a)>1 and a[-1]==0: a.pop()
    return tuple(a)


def independent_masks(n,adj):
    ok=[False]*(1<<n);ok[0]=True
    for s in range(1,1<<n):
        v=(s&-s).bit_length()-1;r=s^(1<<v)
        ok[s]=ok[r] and not(adj[v]&r)
    return ok


@cache
def coeff(g,inv):
    n,edges=g;adj=neighbors(g);allbits=(1<<n)-1
    if inv in ('independence','clique'):
        if inv=='clique': adj=[allbits^(1<<i)^a for i,a in enumerate(adj)]
        a=[0]*(n+1)
        for s,ok in enumerate(independent_masks(n,adj)):
            if ok:a[s.bit_count()]+=1
        return trim(a)
    if inv=='domination':
        a=[0]*(n+1)
        for s in range(1,1<<n):
            cover=s
            for i in range(n):
                if s>>i&1:cover|=adj[i]
            if cover==allbits:a[s.bit_count()]+=1
        return trim(a)
    if inv=='matching':
        @cache
        def rec(s):
            if not s:return (1,)
            v=(s&-s).bit_length()-1;r=s^(1<<v);a=list(rec(r));candidates=adj[v]&r
            while candidates:
                u=candidates&-candidates;candidates^=u;p=rec(r^u)
                a += [0]*max(0,len(p)+1-len(a))
                for i,x in enumerate(p):a[i+1]+=x
            return trim(a)
        return rec(allbits)
    if inv=='chromatic':
        ok=independent_masks(n,adj)
        @cache
        def partitions(s):
            if not s:return (1,)
            v=s&-s;a=[0]*(s.bit_count()+1);t=s
            while t:
                if t&v and ok[t]:
                    for k,c in enumerate(partitions(s^t)):a[k+1]+=c
                t=(t-1)&s
            return trim(a)
        a=[0]*(n+1);falling=[1]
        for k,c in enumerate(partitions(allbits)):
            for j,v in enumerate(falling):a[j]+=c*v
            nxt=[0]*(len(falling)+1)
            for j,v in enumerate(falling):nxt[j]-=k*v;nxt[j+1]+=v
            falling=nxt
        return trim(a)
    raise ValueError(inv)


def strip_zero(a):
    while len(a)>1 and a[0]==0:a=a[1:]
    return a


def normalized(a):
    a=strip_zero(a)
    if all(v>=0 for v in a) or all(v<=0 for v in a):return tuple(abs(v) for v in a)
    b=tuple((-1)**i*v for i,v in enumerate(a))
    if all(v>=0 for v in b) or all(v<=0 for v in b):return tuple(abs(v) for v in b)
    return None


def cheap_certificate(a,ladder=True):
    b=normalized(a)
    if b is not None:
        d=len(b)-1
        for k in range(1,d):
            if b[k]**2*k*(d-k)<b[k-1]*b[k+1]*(k+1)*(d-k+1):return True,'newton'
    if not ladder:return None
    c=strip_zero(a);d=len(c)-1
    if d<2:return False,'linear'
    if d==2:return c[1]**2<4*c[0]*c[2],'quadratic'
    if d in (4,5) and c==c[::-1]:
        g0=c[0];g1=c[1]-d*g0;g2=c[2]-comb(d,2)*g0-(d-2)*g1;g=(g0,g1,g2)
        exp=tuple(sum(g[j]*comb(d-2*j,k-j) for j in range(3) if j<=k<=d-j) for k in range(d+1))
        if exp==c and g2!=0 and g1*g1<4*g0*g2:return True,'gamma_discriminant'
    return None


@cache
def exact_nonreal(a):
    p=sp.Poly.from_list(list(reversed(a)),X,domain=sp.ZZ).sqf_part()
    return p.degree()>0 and int(p.count_roots(-sp.oo,sp.oo))<p.degree()


def verifier(g,inv,claimed_inv,claim,truth):
    a=coeff(g,inv)
    return claimed_inv==inv and tuple(claim)==a and type(truth) is bool and truth==exact_nonreal(a)


def rank(g):
    d=[a.bit_count() for a in neighbors(g)]
    return max(d),sum(x*(x-1) for x in d),len(g[1])


def policy(cards,inv,budget,name):
    order=list(range(len(cards)))
    if name in ('degree_rank','ladder_degree_rank'):order.sort(key=lambda i:rank(cards[i][0]),reverse=True)
    roots=queries=resolved=0;unknown=[];certs=Counter()
    for i in order:
        if name in ('direct','degree_rank') and roots>=budget:break
        a=coeff(cards[i][0],inv);queries+=1
        if name in ('newton_only','ladder','ladder_degree_rank'):
            v=cheap_certificate(a,ladder=name!='newton_only')
            if v is None:unknown.append(a);continue
            truth,kind=v;certs[kind]+=1;resolved+=1
        else:
            roots+=1;resolved+=1;certs['sturm']+=1;truth=exact_nonreal(a)
        if truth:return 'witness',queries,roots,dict(certs)
    if name!='newton_only':
        for a in unknown:
            if roots>=budget:break
            roots+=1;resolved+=1;certs['sturm']+=1
            if exact_nonreal(a):return 'witness',queries,roots,dict(certs)
    return ('absence' if resolved==len(cards) else 'abstain'),queries,roots,dict(certs)


def replay():
    # Hand-constructed reciprocal controls: gamma=(1,10,26), D=-4.
    # Neither is rejected by Newton alone; the gamma branch must fire.
    for a in ((1,14,52,14,1),(1,15,66,66,15,1)):
        assert cheap_certificate(a,False) is None
        assert cheap_certificate(a)==(True,'gamma_discriminant')
        assert exact_nonreal(a)
    for n in range(4,9):
        s=graph('star',n,1);p=graph('path',n,1);c=graph('complete',n,1)
        assert coeff(s,'independence')==tuple(comb(n-1,k)+(k==1) for k in range(n))
        assert coeff(c,'matching')==tuple(factorial(n)//(factorial(n-2*k)*2**k*factorial(k)) for k in range(n//2+1))
        assert sum(v*3**k for k,v in enumerate(coeff(p,'chromatic')))==3*2**(n-1)
    rows=[];roots=Counter();mutations=Counter();kinds=Counter();seen=set();witness_types=Counter()
    for n in (4,5,6,7,8,9):
        for seed in range(20):
            r=random.Random(314159+n*100+seed)
            cards=[(graph(f,n,r.randrange(1<<31)),f) for f in r.sample(FAMILIES,DECK)]
            for inv in INVARIANTS:
                gold=[exact_nonreal(coeff(g,inv)) for g,_ in cards];has=any(gold)
                for (g,f),truth in zip(cards,gold):
                    if (g,inv) in seen:continue
                    seen.add((g,inv));roots[(f,inv)]+=1;a=coeff(g,inv)
                    assert verifier(g,inv,inv,a,truth)
                    assert not verifier(g,inv,inv,a,not truth);mutations['flipped_truth']+=1
                    bad=list(a);bad[0]+=1
                    assert not verifier(g,inv,inv,bad,truth);mutations['tampered_coeff']+=1
                    for other in INVARIANTS:
                        if other==inv:continue
                        b=coeff(g,other)
                        assert not verifier(g,inv,other,b,exact_nonreal(b));mutations['wrong_route']+=1
                        if a==b:mutations['identical_cross_invariant']+=1;continue
                        assert not verifier(g,inv,inv,b,exact_nonreal(b));mutations['wrong_coefficients']+=1
                    cert=cheap_certificate(a)
                    if cert is not None:
                        assert cert[0]==truth;kinds[cert[1]]+=1
                    else:kinds['sturm_required']+=1
                    if truth:witness_types[cert[1] if cert else 'sturm_required']+=1
                for budget in BUDGETS:
                    for name in POLICIES:
                        out,cq,rq,cs=policy(cards,inv,budget,name)
                        assert rq<=budget and cq<=DECK
                        assert out=='abstain' or (out=='witness')==has
                        rows.append(dict(n=n,seed=seed,inv=inv,has_witness=has,budget=budget,policy=name,result=out,coeff_calls=cq,root_calls=rq,certs=cs))
    summary=[]
    for budget in BUDGETS:
        for name in POLICIES:
            rr=[r for r in rows if r['budget']==budget and r['policy']==name]
            yes=[r for r in rr if r['has_witness']];no=[r for r in rr if not r['has_witness']]
            summary.append(dict(budget=budget,policy=name,cases=len(rr),witness_cases=len(yes),absence_cases=len(no),witnesses=sum(r['result']=='witness' for r in yes),absences=sum(r['result']=='absence' for r in no),abstain=sum(r['result']=='abstain' for r in rr),coeff_calls=sum(r['coeff_calls'] for r in rr),root_calls=sum(r['root_calls'] for r in rr)))
    return dict(evidence='public finite synthetic development, no independent conjecture test',families=FAMILIES,invariants=INVARIANTS,distinct_labeled_graph_invariant_pairs=len(seen),family_invariant_counts={f'{f}/{i}':v for (f,i),v in roots.items()},mutation_checks=dict(mutations),certificate_types=dict(kinds),witness_types=dict(witness_types),summary=summary,rows=rows)

if __name__=='__main__':print(json.dumps(replay(),indent=2))

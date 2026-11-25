"""MIC-10: separator conditioning and exact bounded-width elimination."""
from run import root, bits, FAMILIES
from core import Root, valid, exact_table
from mic09 import solve
from random import Random
from time import perf_counter
from pathlib import Path
from itertools import combinations
import hashlib, json
import numpy as np

SIZES=(32,64,128)
SEEDS=range(6000,6002)
KINDS=('original','one_hub','three_hubs')
WIDTH_CAP=10
SEP_CAP=3
COMP_CAP=10


def instance(f,s,n,kind):
    if kind=='original':return root(f,s,n)
    k=1 if kind=='one_hub' else 3
    rng=Random(s+100003*n+1009*FAMILIES.index(f)+17*k)
    ids=list(range(n));rng.shuffle(ids);hubs=ids[:k];rest=ids[k:]
    w=[0]*n;edges=set();sup=[]
    for h in hubs:w[h]=rng.randint(1,20)
    # Balance local sizes in [4,8] (no tiny final block).
    count=(len(rest)+7)//8
    for j in range(count):
        local=rest[j*len(rest)//count:(j+1)*len(rest)//count]
        d=root(f,s+101*j,len(local))
        for i,v in enumerate(local):w[v]=d.w[i]
        edges.update(tuple(sorted((local[i],local[q]))) for i,q in d.edges)
        edges.update(tuple(sorted((local[i],local[i+1]))) for i in range(len(local)-1))
        sup.extend((local[i],sum(1<<local[q] for q in bits(a))) for i,a in d.sup)
        for h in hubs:edges.add(tuple(sorted((h,rng.choice(local)))))
        # A crossing support clause uses only hubs + this component.
        if f!='conflict':
            i=rng.choice(local);a=1<<rng.choice([v for v in local if v!=i]);a|=1<<rng.choice(hubs);sup.append((i,a))
    return Root(tuple(w),tuple(sorted(edges)),tuple(sorted(sup)))


def primal(d):
    n=len(d.w);adj=[0]*n
    scopes=[(i,j) for i,j in d.edges]+[tuple(sorted(set([i,*bits(a)]))) for i,a in d.sup]
    for scope in scopes:
        for i,j in combinations(scope,2):adj[i]|=1<<j;adj[j]|=1<<i
    return adj


def parts(adj,s):
    ans=[]
    while s:
        q=s&-s;c=0
        while q:
            v=q&-q;q^=v
            if c&v:continue
            c|=v;q|=adj[v.bit_length()-1]&s&~c
        ans.append(c);s&=~c
    return ans


def part_cost(cs):
    # Estimated direct conditional enumeration, before boundary caching.
    return sum(1<<c.bit_count() for c in cs)


def choose(d,policy,seed=0):
    adj=primal(d);s=(1<<len(adj))-1;sep=0;scans=0;r=Random(seed)
    # One full candidate scan per level for balance; degree/random use one candidate.
    for k in range(SEP_CAP+1):
        cs=parts(adj,s);scans+=1
        if len(cs)>=2 and max(map(int.bit_count,cs))<=COMP_CAP:
            return sep,cs,scans
        if k==SEP_CAP or not s:break
        if policy=='balance':
            def key(i):
                nonlocal scans
                pc=parts(adj,s&~(1<<i));scans+=1
                return (max(map(int.bit_count,pc),default=0),part_cost(pc),-(adj[i]&s).bit_count(),i)
            i=min(bits(s),key=key)
        elif policy=='degree':i=max(bits(s),key=lambda i:((adj[i]&s).bit_count(),-i))
        elif policy=='random':i=r.choice(list(bits(s)))
        else:raise ValueError(policy)
        sep|=1<<i;s&=~(1<<i)
    return None,[],scans


def submasks(s):
    q=s
    while True:
        yield q
        if not q:break
        q=(q-1)&s


def scopes(d):
    return [(1<<i|1<<j,'conflict',i,1<<j) for i,j in d.edges]+[(1<<i|a,'support',i,a) for i,a in d.sup]


def holds(c,mask):
    _,kind,i,a=c
    return not(mask>>i&1) or (not bool(mask&a) if kind=='conflict' else bool(mask&a))


def weight(d,s):return sum(d.w[i] for i in bits(s))


def conditional(d,sep,cs):
    full=(1<<len(d.w))-1;assert sep&~full==0
    cover=sep
    for c in cs:
        if not c or c&cover:raise ValueError('overlap or empty component')
        cover|=c
    if cover!=full:raise ValueError('incomplete partition')
    if len(cs)<2 or any(c.bit_count()>COMP_CAP for c in cs):raise ValueError('invalid component plan')
    groups=[[] for c in cs];pure=[];boundary=[0]*len(cs)
    for clause in scopes(d):
        mask=clause[0];where=[j for j,c in enumerate(cs) if c&mask]
        if len(where)>1:raise ValueError('crossing clause')
        if not where:pure.append(clause)
        else:
            j=where[0];groups[j].append(clause);boundary[j]|=mask&sep
    cache={};assignments=0;checks=0;local_masks=0;hits=0;best=-1;witness=0;rows=[]
    for a in submasks(sep):
        assignments+=1
        ok=True
        for cl in pure:
            checks+=1
            if not holds(cl,a):ok=False;break
        if not ok:rows.append({'assignment':hex(a),'value':None});continue
        v=weight(d,a);p=a
        for j,c in enumerate(cs):
            b=a&boundary[j];key=j,b
            if key in cache:hits+=1
            else:
                mv=-1;mp=0
                for x in submasks(c):
                    local_masks+=1;z=x|b;local_ok=True
                    for cl in groups[j]:
                        checks+=1
                        if not holds(cl,z):local_ok=False;break
                    if local_ok:
                        u=weight(d,x)
                        if u>mv:mv,mp=u,x
                cache[key]=(mv,mp)
            mv,mp=cache[key]
            if mv<0:ok=False;break
            v+=mv;p|=mp
        rows.append({'assignment':hex(a),'value':v if ok else None})
        if ok and v>best:
            assert valid(d,p) and weight(d,p)==v
            best,witness=v,p
    assert best>=0 and valid(d,witness)
    return dict(value=best,upper=best,mask=hex(witness),certified=True,separator=hex(sep),components=[hex(c) for c in cs],
                assignment_values=rows,assignments=assignments,local_masks=local_masks,clause_checks=checks,cache_hits=hits)


def verify_conditional(d,receipt):
    # Independent replay: project full clauses per component, recompute exact values
    # by scanning every local mask without using cached boundary answers.
    s=int(receipt['separator'],16);cs=[int(x,16) for x in receipt['components']];full=(1<<len(d.w))-1
    covered=s
    for c in cs:
        if not c or c&covered:return False
        covered|=c
    if covered!=full:return False
    cl=scopes(d)
    if any(sum(bool(c&t[0]) for c in cs)>1 for t in cl):return False
    values={}
    for a in submasks(s):
        if any(not holds(t,a) for t in cl if t[0]&~s==0):values[hex(a)]=None;continue
        total=weight(d,a)
        for c in cs:
            local=[t for t in cl if t[0]&c];v=max((weight(d,x) for x in submasks(c) if all(holds(t,x|a) for t in local)),default=-1)
            if v<0:total=None;break
            total+=v
        values[hex(a)]=total
    p=int(receipt['mask'],16)
    reported={x['assignment']:x['value'] for x in receipt['assignment_values']}
    return len(reported)==len(receipt['assignment_values']) and values==reported and valid(d,p) and weight(d,p)==receipt['value']==receipt['upper']==max(x for x in values.values() if x is not None)


def elimination_order(d,policy):
    adj=primal(d);s=(1<<len(adj))-1;out=[];width=0;scans=0
    while s:
        def key(i):
            nonlocal scans
            scans+=1;a=adj[i]&s;degree=a.bit_count()
            fill=sum((a&~adj[j]&~(1<<j)).bit_count() for j in bits(a))//2 if policy=='fill' else 0
            return (fill,degree,i) if policy=='fill' else (degree,i)
        i=min(bits(s),key=key);a=adj[i]&s;width=max(width,a.bit_count());out.append(i)
        for j in bits(a):adj[j]|=a&~(1<<j)
        s&=~(1<<i)
    return out,width,scans


def eliminate(d,order,width_cap=WIDTH_CAP):
    """Exact max-sum over binary factors; infeasible entries use a dominating penalty."""
    n=len(d.w);penalty=-sum(d.w)-1;fs=[];records=[];cells=0;width=0
    for i,w in enumerate(d.w):fs.append(((i,),np.array([0,w],dtype=np.int64)))
    for cl in scopes(d):
        scope=tuple(bits(cl[0]));a=np.empty(1<<len(scope),dtype=np.int64)
        for q in range(len(a)):
            x=sum(1<<j for k,j in enumerate(scope) if q>>k&1);a[q]=0 if holds(cl,x) else penalty
        fs.append((scope,a))
    for i in order:
        here=[(s,a) for s,a in fs if i in s];fs=[(s,a) for s,a in fs if i not in s]
        union=sorted(set(j for s,_ in here for j in s));other=tuple(j for j in union if j!=i);width=max(width,len(other))
        if len(other)>width_cap:return None
        ix=np.arange(1<<len(other),dtype=np.int64);scores=[]
        for x in (0,1):
            total=np.zeros(len(ix),dtype=np.int64)
            for s,a in here:
                index=np.zeros(len(ix),dtype=np.int64)
                for k,j in enumerate(s):
                    index|=(x<<k) if j==i else ((ix>>other.index(j))&1)<<k
                total+=a[index];cells+=len(ix)
            scores.append(total)
        best=np.maximum(*scores);arg=(scores[1]>scores[0]);fs.append((other,best));records.append((i,other,arg))
    v=sum(int(a[0]) for s,a in fs);mask=0
    for i,scope,arg in reversed(records):
        q=sum(1<<k for k,j in enumerate(scope) if mask>>j&1)
        if arg[q]:mask|=1<<i
    assert valid(d,mask) and weight(d,mask)==v
    return dict(value=v,upper=v,mask=hex(mask),certified=True,width=width,factor_cell_reads=cells,order=list(order))


def verify_elimination(d,receipt,width_cap=WIDTH_CAP):
    # Independent max-sum replay, sparse dictionaries, missing entry = infeasible.
    n=len(d.w);order=receipt['order']
    if sorted(order)!=list(range(n)):return False
    fs=[((i,),{0:0,1:w}) for i,w in enumerate(d.w)]
    for i,j in d.edges:
        scope=tuple(sorted((i,j)));fs.append((scope,{0:0,1:0,2:0}))
    for i,a in d.sup:
        scope=tuple(sorted({i,*bits(a)}));table={}
        for q in range(1<<len(scope)):
            x=sum(1<<j for k,j in enumerate(scope) if q>>k&1)
            if not x>>i&1 or x&a:table[q]=0
        fs.append((scope,table))
    width=0
    for i in order:
        selected=[(s,a) for s,a in fs if i in s];fs=[(s,a) for s,a in fs if i not in s]
        other=tuple(sorted({j for s,_ in selected for j in s if j!=i}));width=max(width,len(other))
        if len(other)>width_cap:return False
        positions=[tuple(-1 if j==i else other.index(j) for j in s) for s,_ in selected]
        table={}
        for q in range(1<<len(other)):
            candidates=[]
            for x in (0,1):
                score=0
                for (_,a),pos in zip(selected,positions):
                    ix=sum((x if j==-1 else (q>>j)&1)<<k for k,j in enumerate(pos))
                    if ix not in a:break
                    score+=a[ix]
                else:candidates.append(score)
            if candidates:table[q]=max(candidates)
        fs.append((other,table))
    if any(s or 0 not in a for s,a in fs):return False
    v=sum(a[0] for s,a in fs);mask=int(receipt['mask'],16)
    return (width==receipt['width'] and valid(d,mask) and weight(d,mask)==v==receipt['value']==receipt['upper'])


def hybrid(d):
    start=perf_counter();order,w,scans=elimination_order(d,'degree')
    if w<=WIDTH_CAP:
        a=eliminate(d,order);assert a is not None
        a['method']='elimination'
    else:
        a=solve(d,'both');a['method']='branch_and_bound'
    a.update(planned_width=w,plan_scans=scans,ms=(perf_counter()-start)*1000)
    return a


def run():
    t=perf_counter();rows=[]
    for kind in KINDS:
        for n in SIZES:
            for f in FAMILIES:
                for s in SEEDS:
                    d=instance(f,s,n,kind);arms={'baseline':solve(d,'both')}
                    for p in ('degree','balance','random'):
                        start=perf_counter();sep,cs,scans=choose(d,p,s)
                        plan_ms=(perf_counter()-start)*1000
                        if sep is None:
                            a={'certified':False,'applicable':False,'scans':scans,'plan_ms':plan_ms,'ms':plan_ms}
                        else:
                            a=conditional(d,sep,cs);a.update(applicable=True,scans=scans,plan_ms=plan_ms,ms=(perf_counter()-start)*1000)
                            assert verify_conditional(d,a)
                        arms['sep_'+p]=a
                    for p in ('degree','fill'):
                        start=perf_counter();order,w,scans=elimination_order(d,p);plan_ms=(perf_counter()-start)*1000
                        a=eliminate(d,order) if w<=WIDTH_CAP else None
                        elapsed=(perf_counter()-start)*1000
                        if a is None:a=dict(certified=False,applicable=False)
                        else:
                            a['applicable']=True
                            assert verify_elimination(d,a)
                        a.update(width=w,scans=scans,plan_ms=plan_ms,ms=elapsed);arms['ve_'+p]=a
                    arms['hybrid']=hybrid(d)
                    measured=[a for a in arms.values() if 'value' in a]
                    lo=max(a['value'] for a in measured);hi=min(a['upper'] for a in measured);assert lo<=hi
                    assert all(valid(d,int(a['mask'],16)) and weight(d,int(a['mask'],16))==a['value'] for a in measured)
                    rows.append(dict(kind=kind,n=n,family=f,seed=s,arms=arms,pooled_lower=lo,pooled_upper=hi))
            print('done',kind,n,flush=True,file=__import__('sys').stderr)
    return dict(schema='MIC-10/public-cpu/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,elapsed_s=perf_counter()-t)

if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))

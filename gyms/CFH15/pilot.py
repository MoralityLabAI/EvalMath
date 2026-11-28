"""CFH-15 cold logical-fuel replay. No unpaid coefficient values in the policy."""
import argparse,json,gzip,random,sys
from collections import Counter,defaultdict
from fractions import Fraction
from itertools import combinations,product
from math import comb,prod
from pathlib import Path
from fuel import Meter,Task,Exhausted,coefficient_task
HERE=Path(__file__).resolve().parent
for j in (4,5,6,12):
    for name in (f'CFH{j:02}',f'cfh{j:02}_dev'):
        sys.path.insert(0,str(HERE.parent/name))
from compositional import routes
from coefficients_joint import Deck,bits,graph_key
from hidden_invariant import direct_coefficients
import networkx as nx
RR=routes(2);KEYS=tuple(sorted({r[:4] for r in RR}));FULL=(1<<len(RR))-1
CAPS=(12000,30000,60000,120000)
ARMS=('eager_scan','eager_index','lazy_scan','lazy_index','lazy_free')

def sparse(g,key,m):
    l,r,c,inv=key;n,es=g;n-=l+r;E=set()
    for a,b in es:
        m.tick('setup')
        if l<=a<b<n+l:E.add((a-l,b-l))
    if c:
        out=set()
        for a,b in combinations(range(n),2):
            m.tick('setup')
            if (a,b) not in E:out.add((a,b))
        E=out
    deg=[0]*n
    for a,b in sorted(E):m.tick('setup');deg[a]+=1;deg[b]+=1
    e=len(E);z={}
    def put(k,v):m.tick('setup');z[k]=v
    if inv in ('independence','clique'):
        put(0,1);put(1,n);put(2,comb(n,2)-e if inv=='independence' else e);put(n,int(e==0 if inv=='independence' else e==comb(n,2)))
    elif inv=='matching':
        s=0
        for d in deg:m.tick('setup');s+=comb(d,2)
        put(0,1);put(1,e);put(2,comb(e,2)-s)
        for k in range(n//2+1,n+1):put(k,0)
    elif inv=='chromatic':
        t=0
        for a,b,c in combinations(range(n),3):m.tick('setup');t+=(a,b) in E and (a,c) in E and (b,c) in E
        put(0,0);put(n,1);put(n-1,-e);put(n-2,comb(e,2)-t)
    elif inv=='domination':
        a=b=0
        for d in deg:m.tick('setup');a+=d==n-1;b+=d==0
        put(0,0);put(1,a);put(n,1);put(n-1,n-b)
    else:raise ValueError(inv)
    return (n,tuple(sorted(E))),z

class Live:
    def __init__(self,cards,m,index):
        self.index=index;self.groups=[];self.owner=[];self.refs={};self.ids={};self.probes=[]
        for h,g in enumerate(cards):
            for key in KEYS:
                m.tick('setup');base,z=sparse(g,key,m);n=base[0];cell={};i=len(self.groups)
                for k in range(n+1):
                    m.tick('setup')
                    if k in z:continue
                    j=len(self.owner);self.owner.append(i);self.ids[h,key,k]=j;cell[j]=k
                self.groups.append((base,key[3],cell));self.refs[h,key]=(n,z)
            for k,p in product(range(g[0]+1),(2,3,5)):
                m.tick('setup');self.probes.append((h,k,p))
        m.tick('setup',len(self.probes));self.order=sorted(range(len(self.probes)),key=lambda a:(self.probes[a][1],self.probes[a][0],self.probes[a][2]))
    def compile(self,a,m,phase):
        h,k,p=self.probes[a];cheap=[0]*p;expr=[];groups={}
        for i,r in enumerate(RR):
            m.tick(phase);n,z=self.refs[h,r[:4]];d,s=r[4:];off=need=0;terms=[]
            for j in range(k+d,n+1):
                m.tick(phase);w=prod(range(j-d+1,j+1))*comb(j-d,k)*pow(s,j-d-k,p)%p
                if not w:continue
                if j in z:off=(off+w*z[j])%p
                else:
                    c=self.ids[h,r[:4],j];terms.append((c,w));need|=1<<c
            if not need:cheap[off]|=1<<i
            elif self.index:groups[need]=groups.get(need,0)|(1<<i)
            expr.append((off,need,tuple(terms)))
        m.tick(phase);return tuple(cheap),tuple(expr),tuple(groups.items())
    def state(self,S,B,values,data,m,phase):
        cheap,expr,groups=data;m.tick(phase);masks=[x&S for x in cheap];need=0
        def add(i):
            nonlocal need
            m.tick(phase);off,req,terms=expr[i];missing=req&~B;need|=missing
            if missing:return
            for j,w in terms:m.tick(phase);off+=w*values[j]
            masks[off%len(masks)]|=1<<i
        if self.index:
            for req,rs in groups:
                m.tick(phase);active=rs&S
                if not active:continue
                missing=req&~B;need|=missing
                if not missing:
                    for i in bits(active):add(i)
        else:
            for i in bits(S&~sum(masks)):add(i)
        return tuple(masks),need
    def acquire(self,need,values,m):
        grouped=defaultdict(int)
        for j in bits(need):m.tick('acquisition');grouped[self.owner[j]]|=1<<j
        m.tick('acquisition',max(1,len(values)));new=values.copy()
        for i,mask in sorted(grouped.items()):
            m.tick('acquisition');g,inv,cell=self.groups[i];ks=tuple(sorted(cell[j] for j in bits(mask)))
            whole=2*len(ks)>=len(cell)+1
            out=Task(coefficient_task(g,inv,ks,whole)).require(m,'acquisition')
            got=dict(enumerate(out)) if whole else dict(zip(ks,out,strict=True))
            for j in (cell if whole else bits(mask)):m.tick('acquisition');new[j]=got[cell[j]]
        return new

def choose(l,S,B,values,cache,h,m,free):
    n=S.bit_count();best=None;scanned=0;cap=m.cap;m.cap=m.used+m.left*(2 if h==2 else 3)//(3 if h==2 else 4)
    try:
        for a in l.order:
            m.tick('selection')
            if a not in cache:cache[a]=l.compile(a,m,'selection_compile')
            masks,need=l.state(S,B,values,cache[a],m,'selection');cs=[x.bit_count() for x in masks];u=n-sum(cs);scanned+=1
            if not need and max(cs)==n or need and free:continue
            gain=n*n-sum(v*(u+v) for v in cs)-u*(u+max(cs))
            primary=Fraction(gain,n*n) if h==2 else Fraction(min(len(cs)*4,4*sum(v==1 for v in cs)+u),4*n)
            score=primary*20/(20+need.bit_count())
            if score<=0:continue
            rank=(score,Fraction(gain,n*n),-need.bit_count(),-a)
            if best is None or rank>best[0]:best=rank,a,need
    except Exhausted:pass
    finally:m.cap=cap
    return None if best is None else best[1:],scanned

def evaluate(cards,oracle,cap,arm):
    m=Meter(cap);rows=[];dec=[]
    def emit(S,m,h,reason):
        assert 0<=m.used<=m.cap and sum(m.ledger.values())==m.used
        for i in bits(S):rows.append(dict(hidden=i,hit=S.bit_count()==1,remaining=S.bit_count(),queries=2-h,used=m.used,ledger=dict(m.ledger),reason=reason))
    try:
        l=Live(cards,m,arm.endswith('index') or arm=='lazy_free');cache={}
        if arm.startswith('eager'):
            for a in l.order:cache[a]=l.compile(a,m,'setup_compile')
    except Exhausted:
        emit(FULL,m,2,'setup_exhausted');return rows,dec
    assert l.probes==list(oracle.probes) and len(l.owner)==len(oracle.values)
    def walk(S,B,values,h,m,cache):
        if S.bit_count()==1 or not h or not m.left:emit(S,m,h,'terminal');return
        choice,scanned=choose(l,S,B,values,cache,h,m,arm=='lazy_free')
        if choice is None:emit(S,m,h,'no_query');return
        a,need=choice;old=values.copy();before=m.used
        try:
            new=l.acquire(need,values,m);m.tick('restriction',max(1,len(new)));newB=sum(1<<j for j in new)
            masks,missing=l.state(S,newB,new,cache[a],m,'restriction');assert not missing
            m.tick('restriction');children=tuple(t for t in masks if t)
        except Exhausted:
            assert values==old
            dec.append(dict(n=S.bit_count(),h=h,probe=a,scanned=scanned,used=m.used,transaction_fuel=m.used-before,committed=False))
            emit(S,m,h,'transaction_exhausted');return
        assert values==old and all(new[j]==oracle.values[j] for j in new)
        assert children==oracle.actual(S,a) and sum(children)==S
        dec.append(dict(n=S.bit_count(),h=h,probe=a,scanned=scanned,used=m.used,transaction_fuel=m.used-before,committed=True,acquired=(newB&~B).bit_count()))
        for child in children:walk(child,newB,new,h-1,m.fork(),cache.copy())
    walk(FULL,0,{},2,m,cache)
    assert len(rows)==len(RR) and len({r['hidden'] for r in rows})==len(RR)
    return rows,dec

def audit():
    rng=random.Random(1515);checks=pauses=cutoffs=0;costs=[]
    for n,density in product((3,4,5,6,8,9),(.15,.5,.85)):
        g=(n,tuple((i,j) for i,j in combinations(range(n),2) if rng.random()<density));ref=direct_coefficients(g)
        for inv,a in ref.items():
            for whole in (False,True):
                ks=tuple(range(n+1)) if whole else (1,n//2,n-1);expected=a if whole else tuple(a[k] for k in ks)
                t=Task(coefficient_task(g,inv,ks,whole));m=Meter(1000000);assert t.advance(m,'acquisition') and t.result==expected
                full=m.used;checks+=1;costs.append(dict(n=n,inv=inv,whole=whole,fuel=full))
                t=Task(coefficient_task(g,inv,ks,whole));m=Meter(full)
                while not t.done:
                    t.advance(m,'acquisition',quantum=rng.randrange(1,8));pauses+=1;assert t.done or t.result is None
                assert t.result==expected and m.used==full
                for cap in (range(full+1) if full<=60 else sorted({0,1,full//2,full-1,full})):
                    t=Task(coefficient_task(g,inv,ks,whole));m=Meter(cap);assert t.advance(m,'acquisition')==(cap==full)
                    assert m.used==cap and (t.result==expected if cap==full else t.result is None);cutoffs+=1
    return dict(exact_cases=checks,quantum_advances=pauses,cutoff_checks=cutoffs,kernel_costs=costs)

def read(path):
    p=Path(path);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)

def manifest(paths,n):
    used=set()
    for path in paths:
        r=read(path);ds=[z[1] if len(z)==2 else z[2] for z in r['manifest']] if 'manifest' in r else [d['cards'] for d in r.get('decks',r.get('eval_decks',[]))]
        for cs in ds:
            for k,e in cs:used.add(graph_key((k,tuple(map(tuple,e)))))
    old=len(used);rng=random.Random(2026112515);decks=[]
    for i in range(n):
        cards=[]
        for j in range(3):
            for _ in range(4000):
                k=rng.choice((9,10));seed=rng.randrange(2**31)
                if j==0:g=nx.gnp_random_graph(k,rng.uniform(.15,.45),seed=seed)
                elif j==1:g=nx.gnp_random_graph(k,rng.uniform(.55,.9),seed=seed)
                else:g=nx.random_geometric_graph(k,rng.uniform(.3,.7),seed=seed)
                lab=list(range(k));rng.shuffle(lab);g=nx.relabel_nodes(g,dict(enumerate(lab)));cs=k,tuple(sorted(tuple(sorted(e)) for e in g.edges()));key=graph_key(cs)
                if key not in used:used.add(key);cards.append(cs);break
            else:raise RuntimeError('generator exhausted')
        decks.append((i,tuple(cards)))
    return old,decks

def main():
    p=argparse.ArgumentParser();p.add_argument('--prior',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--decks',type=int,default=6);a=p.parse_args()
    checks=audit();print('kernel',{k:v for k,v in checks.items() if k!='kernel_costs'},flush=True,file=sys.stderr)
    old,ds=manifest(a.prior,a.decks);rows=[];dec=[];meta=[]
    for i,cards in ds:
        oracle=Deck(cards);meta.append(dict(deck=i,oracle_checks=dict(oracle.audit)))
        for cap,arm in product(CAPS,ARMS):
            rr,dd=evaluate(cards,oracle,cap,arm);rows.extend(dict(deck=i,cap=cap,arm=arm,**r) for r in rr);dec.extend(dict(deck=i,cap=cap,arm=arm,**r) for r in dd)
        print('deck',i,'rows',len(rows),flush=True,file=sys.stderr)
    summary=[]
    for cap,arm in product(CAPS,ARMS):
        r=[z for z in rows if (z['cap'],z['arm'])==(cap,arm)];n=len(r)
        summary.append(dict(cap=cap,arm=arm,n=n,hits=sum(z['hit'] for z in r),mean_fuel=sum(z['used'] for z in r)/n,phases={k:sum(z['ledger'].get(k,0) for z in r)/n for k in ('setup','setup_compile','selection','selection_compile','acquisition','restriction')},over=sum(z['used']>cap for z in r),setup_exhausted=sum(z['reason']=='setup_exhausted' for z in r),transaction_exhausted=sum(z['reason']=='transaction_exhausted' for z in r)))
    Path(a.out).write_text(json.dumps(dict(evidence='public finite deterministic logical fuel pilot',prior_graph_hashes=old,manifest=ds,audit=checks,summary=summary,records=rows,decisions=dec,meta=meta),separators=(',',':')))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

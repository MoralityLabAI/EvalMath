"""CFH-13: measured coefficient acquisition, public development."""
import argparse, json, random, sys
from collections import defaultdict, Counter
from itertools import combinations, product
from pathlib import Path
from time import thread_time_ns
import networkx as nx
HERE=Path(__file__).resolve().parent
for k in (4,6,12):
    for name in (f'CFH{k:02}',f'cfh{k:02}_dev'):
        sys.path.insert(0,str(HERE.parent/name))
from coefficients_joint import Deck, Free, bits, graph_key, known_coeff, load, direct_coefficients, coefficients
from targeted import targeted, vector, timed
CAPS=(100,400,1200); PRICES=(0,100,400); SCALE=1000000
MODES=('vector','scalar','batch','hybrid')

def manifest(paths,n_decks):
    used=set()
    for path in paths:
        r=load(path)
        ds=[z[1] if len(z)==2 else z[2] for z in r['manifest']] if 'manifest' in r else [d['cards'] for d in r.get('decks',r.get('eval_decks',[]))]
        for cs in ds:
            for n,e in cs:used.add(graph_key((n,tuple(map(tuple,e)))))
    prior=len(used);rng=random.Random(2026112513);decks=[]
    for i in range(n_decks):
        cards=[]
        for j in range(3):
            for _ in range(4000):
                n=rng.choice((8,9));seed=rng.randrange(2**31)
                if j==0:g=nx.gnp_random_graph(n,rng.uniform(.12,.45),seed=seed)
                elif j==1:g=nx.gnp_random_graph(n,rng.uniform(.55,.88),seed=seed)
                else:g=nx.random_geometric_graph(n,rng.uniform(.25,.7),seed=seed)
                labels=list(range(n));rng.shuffle(labels);g=nx.relabel_nodes(g,dict(enumerate(labels)))
                cs=n,tuple(sorted(tuple(sorted(e)) for e in g.edges()));key=graph_key(cs)
                if key not in used:used.add(key);cards.append(cs);break
            else:raise RuntimeError('generator exhausted')
        decks.append((i,tuple(cards)))
    return prior,decks

class Costs:
    def __init__(self,d):
        self.d=d;self.groups=[];self.owner=[];self.profiles={};self.menus={};self.cal_ns=0;self.calls=Counter();self.bench=[]
        for h,(n,es) in enumerate(d.cards):
            for key in sorted({r[:4] for r in d.rr}):
                l,r,c,inv=key;m=n-l-r;E={(a-l,b-l) for a,b in es if l<=a<b<n-r}
                if c:E=set(combinations(range(m),2))-E
                g=m,tuple(sorted(E));ref=coefficients(g,inv);_,known=known_coeff(d.cards[h],key)
                assert ref==direct_coefficients(g)[inv]
                cell={};mask=0;i=len(self.groups)
                for j,v in enumerate(ref):
                    if j in known:continue
                    a=len(self.owner);self.owner.append(i);cell[a]=j;mask|=1<<a;assert v==d.values[a]
                self.groups.append((g,inv,ref,mask,cell))
        assert len(self.owner)==len(d.values)
        for i,(g,inv,ref,mask,cell) in enumerate(self.groups):
            if not mask:continue
            v=self.measure(i,'vector',mask);s=sum(self.measure(i,'batch',1<<j) for j in cell);b=self.measure(i,'batch',mask)
            for j,k in cell.items():self.bench.append(dict(group=i,inv=inv,n=g[0],k=k,single_us=self.measure(i,'batch',1<<j),vector_us=v,all_scalar_us=s,all_batch_us=b))
    def call(self,i,mode,mask):
        g,inv,ref,_,cell=self.groups[i];ks=tuple(sorted(cell[j] for j in bits(mask)))
        if mode=='vector':return vector,(g,inv),ref,()
        return targeted,(g,inv,ks),tuple(ref[k] for k in ks),ks
    def measure(self,i,mode,mask):
        g,inv,*_=self.groups[i];fn,args,expected,ks=self.call(i,mode,mask);key=g,inv,mode,ks
        if key not in self.profiles:
            t=thread_time_ns();ns,samples=timed(fn,args,expected);self.cal_ns+=thread_time_ns()-t
            self.profiles[key]=(max(1,(ns+999)//1000),ns,samples)
        return self.profiles[key][0]
    def variants(self,S,B,a):
        key=S,B,a
        if key in self.menus:return self.menus[key]
        need=self.d.need(S,a,'cell')&~B;grouped=defaultdict(int)
        for j in bits(need):grouped[self.owner[j]]|=1<<j
        menu={m:[0,B,[]] for m in MODES}
        for i,mask in grouped.items():
            full=self.groups[i][3]
            opts={'scalar':(sum(self.measure(i,'batch',1<<j) for j in bits(mask)),mask,tuple(('batch',i,1<<j) for j in bits(mask))),
                  'batch':(self.measure(i,'batch',mask),mask,(('batch',i,mask),)),
                  'vector':(self.measure(i,'vector',full),full,(('vector',i,full),))}
            opts['hybrid']=min(opts.values(),key=lambda z:(z[0],-z[1].bit_count()))
            for m,(c,add,actions) in opts.items():menu[m][0]+=c;menu[m][1]|=add;menu[m][2].extend(actions)
        out={m:(v[0],v[1],tuple(v[2])) for m,v in menu.items()};self.menus[key]=out;return out
    def purchase(self,actions):
        total=0
        for mode,i,mask in actions:
            fn,args,expected,_=self.call(i,mode,mask);t=thread_time_ns();res=fn(*args);total+=thread_time_ns()-t
            assert res==expected;self.calls[mode]+=1
        return total

class Planner:
    def __init__(self,d,costs,mode):self.d=d;self.costs=costs;self.mode=mode;self.memo={};self.opts={};self.scans=0
    def options(self,S,B,left):
        key=S,B,left
        if key not in self.opts:
            out=[]
            for a in range(len(self.d.probes)):
                self.scans+=1;vs=self.costs.variants(S,B,a);ch=self.d.actual(S,a);seen=set()
                for mode in (MODES if self.mode=='hybrid' else (self.mode,)):
                    c,b,actions=vs[mode]
                    if c>left or (len(ch)==1 and not c) or (c,b) in seen:continue
                    seen.add((c,b));out.append((a,mode,b,c,ch,actions))
            self.opts[key]=out
        return self.opts[key]
    def plan(self,S,B,left,h,p):
        if S.bit_count()==1:return SCALE,None
        if not h:return 0,None
        key=S,B,left,h,p
        if key not in self.memo:
            best=0;choice=None
            for a,m,b,c,ch,actions in self.options(S,B,left):
                v=-p*S.bit_count()*c+(SCALE*sum(t.bit_count()==1 for t in ch) if h==1 else sum(self.plan(t,b,left-c,h-1,p)[0] for t in ch))
                if v>best or (v==best and choice is not None and c<choice[3]):best=v;choice=a,m,b,c,ch,actions
            self.memo[key]=best,choice
        return self.memo[key]

def replay(d,costs,planner,free,cap,p,arm):
    rows=[];decisions=[];planning=0;buy=0
    def walk(S,B,left,h,spent,actual):
        nonlocal planning,buy
        n=S.bit_count()
        def emit():
            for i in bits(S):rows.append(dict(hidden=i,hit=n==1,cost=spent,actual_ns=actual,queries=2-h,remaining=n))
            return SCALE if n==1 else 0
        if n==1 or not h:return emit()
        t=thread_time_ns()
        if arm=='free':
            _,a=free.plan(S,B,h);choice=None if a<0 else (a,'free',B,0,None,())
        elif arm=='greedy_hybrid':
            best=None;choice=None
            for a in range(len(d.probes)):
                c,b,actions=costs.variants(S,B,a)['hybrid']
                if c>left:continue
                counts=[m.bit_count() for m in d.known(S,B,a)];u=n-sum(counts)
                if not u and max(counts)==n:continue
                gain=(n*n-sum(v*(u+v) for v in counts)-u*(u+max(counts)))/(n*n);sure=sum(v==1 for v in counts)/n if u==0 else 0
                rank=((sure if h==1 else gain)-p/SCALE*c,gain,-c,-a)
                if best is None or rank>best:best=rank;choice=a,'hybrid',b,c,None,actions
            if best is None or best[0]<=0:
                _,a=free.plan(S,B,h);choice=None if a<0 else (a,'free',B,0,None,())
        else:_,choice=planner.plan(S,B,left,h,p)
        planning+=thread_time_ns()-t
        if choice is None:return emit()
        a,m,b,c,_,actions=choice;assert c<=left
        real=costs.purchase(actions);buy+=real;ch=tuple(t for t in d.known(S,b,a) if t);assert ch==d.actual(S,a) and sum(ch)==S
        decisions.append(dict(n=n,h=h,probe=a,menu=m,calibrated_us=c,actual_ns=real,cells=(b&~B).bit_count(),calls=len(actions)))
        return sum(walk(t,b,left-c,h-1,spent+c,actual+real) for t in ch)-p*n*c
    v=walk(d.full,0,cap,2,0,0);assert len(rows)==d.n and len({r['hidden'] for r in rows})==d.n
    assert v==sum(SCALE*r['hit']-p*r['cost'] for r in rows)
    assert all(r['cost']<=cap and r['queries']<=2 and r['hit']==(r['remaining']==1) for r in rows)
    if arm in MODES:assert v==planner.plan(d.full,0,cap,2,p)[0]
    return rows,decisions,planning,buy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prior',nargs='+',required=True);ap.add_argument('--out',required=True);ap.add_argument('--decks',type=int,default=6);a=ap.parse_args();prior,ds=manifest(a.prior,a.decks)
    records=[];decisions=[];meta=[];profiles=[];bench=[]
    for i,cs in ds:
        d=Deck(cs);costs=Costs(d);pl={m:Planner(d,costs,m) for m in MODES};free=Free(d);bench.extend(dict(deck=i,**r) for r in costs.bench)
        print('calibrated',i,len(costs.profiles),flush=True,file=sys.stderr)
        for cap,p in product(CAPS,PRICES):
            for arm in ('free','greedy_hybrid',*MODES):
                rr,dd,pns,bns=replay(d,costs,pl.get(arm),free,cap,p,arm)
                records.extend(dict(deck=i,cap=cap,price=p,arm=arm,**r) for r in rr);decisions.extend(dict(deck=i,cap=cap,price=p,arm=arm,**r) for r in dd);meta.append(dict(deck=i,cap=cap,price=p,arm=arm,planning_ns=pns,acquisition_ns=bns))
        for (g,inv,mode,ks),(us,ns,samples) in costs.profiles.items():profiles.append(dict(deck=i,graph=g,inv=inv,mode=mode,ks=ks,us=us,ns=ns,samples=samples))
        meta.append(dict(deck=i,calibration_ns=costs.cal_ns,scans={m:v.scans for m,v in pl.items()},profile_count=len(costs.profiles),**d.audit,execution_calls=dict(costs.calls)));print('done',i,meta[-1],flush=True,file=sys.stderr)
        coefficients.cache_clear();direct_coefficients.cache_clear();known_coeff.cache_clear()
    groups=defaultdict(list)
    for r in records:groups[r['cap'],r['price'],r['arm']].append(r)
    summary=[]
    for (cap,p,arm),rr in sorted(groups.items()):
        n=len(rr);hits=sum(r['hit'] for r in rr);cost=sum(r['cost'] for r in rr);ns=sum(r['actual_ns'] for r in rr);summary.append(dict(cap=cap,price=p,arm=arm,n=n,hits=hits,mean_us=cost/n,replay_mean_us=ns/n/1000,actual_over_cap=sum(r['actual_ns']>cap*1000 for r in rr),utility_ticks=SCALE*hits-p*cost,mean_utility=(SCALE*hits-p*cost)/(SCALE*n)))
    for cap,p in product(CAPS,PRICES):
        z={r['arm']:r for r in summary if (r['cap'],r['price'])==(cap,p)};assert all(z['hybrid']['utility_ticks']>=r['utility_ticks'] for r in z.values())
    Path(a.out).write_text(json.dumps(dict(evidence='public development; per-instance measured acquisition calibration; offline planner ceiling',scale=SCALE,caps=CAPS,prices=PRICES,prior_graph_hashes=prior,manifest=ds,meta=meta,summary=summary,bench=bench,profiles=profiles,records=records,decisions=decisions),separators=(',',':')))
if __name__=='__main__':main()

"""CFH-14: out-of-deck timing prediction and charged online selection."""
import argparse, gzip, json, math, random, sys
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path
from statistics import median
from time import thread_time_ns as clock
import networkx as nx
import numpy as np
HERE=Path(__file__).resolve().parent
for i in (4,5,6,12,13):
    for name in (f'CFH{i:02}',f'cfh{i:02}_dev'):
        sys.path.insert(0,str(HERE.parent/name))
from compositional import routes
from lazy_acquisition import known_coeff
from hidden_invariant import direct_coefficients
from targeted import targeted, vector
from coefficients_joint import Deck, bits, graph_key
INV=('independence','clique','matching','domination','chromatic')
CAPS=(1000,4000,16000)
ARMS=('free','vector','hybrid','shortlist_basic','shortlist_work')

def read(path):
    p=Path(path);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)

def graph_stats(g,inv):
    n,E=g;deg=[0]*n
    for a,b in E:deg[a]+=1;deg[b]+=1
    if inv=='clique':deg=[n-1-d for d in deg]
    return n,sum(deg)/max(1,n*(n-1)),max(deg)/max(1,n-1),sum(d*d for d in deg)/max(1,n*(n-1)**2),n-1-min(deg)

def features(stats,inv,ks,mode,work):
    n,dens,degree,d2,free=stats
    target=ks if mode=='batch' else tuple(range(n+1));L=len(target)
    x=[1.,n/10,dens,degree,d2,L/(n+1),min(target)/n,max(target)/n,sum(target)/(L*n)]
    if work:
        # Deterministic combinatorial envelopes/proxies, not executed operation counts.
        subsets=sum(math.comb(n,k) for k in target)
        states=sum(sum(math.comb(n,j) for j in range(k*(2 if inv=='matching' else 1),n+1)) for k in target)
        branches=sum((n-k+1)*sum(math.comb(free,j) for j in range(min(free,n-k)+1)) for k in target)
        x += [math.log1p(subsets),math.log1p(states),math.log1p(branches),math.log1p(2**free),math.log1p(sum(k*math.comb(n,k) for k in target))]
    return x

class Predictor:
    def __init__(self,profiles,work):
        self.work=work;self.weights={};self.margins={}
        for inv,mode in product(INV,('batch','vector')):
            r=[x for x in profiles if (x['inv'],x['mode'])==(inv,mode)]
            X=np.array([features(graph_stats(x['graph'],inv),inv,tuple(x['ks']),mode,work) for x in r]);y=np.log([median(x['samples']) for x in r])
            w=np.linalg.solve(X.T@X+.05*np.eye(X.shape[1]),X.T@y)
            self.weights[inv,mode]=tuple(w.tolist());self.margins[inv,mode]=max(0.,float(np.quantile(y-X@w,.9)))
    def price(self,stats,inv,ks,mode):
        x=features(stats,inv,ks,mode,self.work);w=self.weights[inv,mode]
        return max(1000,int(math.exp(sum(a*b for a,b in zip(x,w,strict=True))+self.margins[inv,mode])))

def new_decks(used,count):
    rng=random.Random(2026112514)
    for i in range(count):
        cards=[]
        for j in range(3):
            for _ in range(4000):
                n=rng.choice((8,9));seed=rng.randrange(2**31)
                if j==0:g=nx.gnp_random_graph(n,rng.uniform(.1,.5),seed=seed)
                elif j==1:g=nx.gnp_random_graph(n,rng.uniform(.5,.9),seed=seed)
                else:g=nx.random_geometric_graph(n,rng.uniform(.3,.65),seed=seed)
                labels=list(range(n));rng.shuffle(labels);g=nx.relabel_nodes(g,dict(enumerate(labels)))
                cs=(n,tuple(sorted(tuple(sorted(e)) for e in g.edges())));key=graph_key(cs)
                if key not in used:used.add(key);cards.append(cs);break
            else:raise RuntimeError('generator exhausted')
        yield i,tuple(cards)

class Live:
    def __init__(self,cards):
        t=clock();self.cards=cards;self.rr=routes(2);self.n=len(self.rr);self.full=(1<<self.n)-1
        keys=sorted({r[:4] for r in self.rr});self.groups=[];self.owner=[];refs={};ids={}
        for h,g in enumerate(cards):
            for key in keys:
                l,r,c,inv=key;n,E=g;m=n-l-r;E={(a-l,b-l) for a,b in E if l<=a<b<n-r}
                if c:E=set(combinations(range(m),2))-E
                base=(m,tuple(sorted(E)));_,z=known_coeff(g,key);cell={};mask=0;i=len(self.groups)
                for k in range(m+1):
                    if k in z:continue
                    a=len(self.owner);ids[h,key,k]=a;self.owner.append(i);cell[a]=k;mask|=1<<a
                self.groups.append((base,inv,mask,cell,graph_stats(base,inv)));refs[h,key]=(m,z)
        self.probes=tuple((h,k,p) for h,g in enumerate(cards) for k in range(g[0]+1) for p in (2,3,5));self.expr=[];self.needs=[];self.cheap=[]
        for h,k,p in self.probes:
            row=[];needs=[];masks=[0]*p
            for i,r in enumerate(self.rr):
                m,z=refs[h,r[:4]];d,s=r[4:];off=0;terms=[];need=0
                for j in range(k+d,m+1):
                    w=math.prod(range(j-d+1,j+1))*math.comb(j-d,k)*pow(s,j-d-k,p)%p
                    if not w:continue
                    if j in z:off=(off+w*z[j])%p
                    else:a=ids[h,r[:4],j];terms.append((a,w));need|=1<<a
                if not need:masks[off]|=1<<i
                row.append((off,tuple(terms)));needs.append(need)
            self.expr.append(tuple(row));self.needs.append(tuple(needs));self.cheap.append(tuple(masks))
        self.setup_ns=clock()-t
    def state(self,S,B,values,a):
        p=self.probes[a][2];masks=[m&S for m in self.cheap[a]];need=0
        for i in bits(S&~sum(masks)):
            req=self.needs[a][i]&~B;need|=req
            if not req:
                c,ts=self.expr[a][i];v=(c+sum(w*values[j] for j,w in ts))%p;masks[v]|=1<<i
        return masks,need
    def menu(self,need,mode,predict,prices):
        gmask=defaultdict(int)
        for j in bits(need):gmask[self.owner[j]]|=1<<j
        actions=[];estimate=0
        for i,mask in gmask.items():
            g,inv,full,cell,stats=self.groups[i];ks=tuple(sorted(cell[j] for j in bits(mask)))
            def price(mode,ks):
                key=i,mode,ks
                if key not in prices:prices[key]=predict.price(stats,inv,ks,mode)
                return prices[key]
            v=price('vector',());best=(v,'vector',full,())
            if mode!='vector':best=min(best,(price('batch',ks),'batch',mask,ks))
            estimate+=best[0];actions.append((i,*best[1:]))
        return estimate,actions
    def execute(self,actions,values):
        B=0;calls=0;ns=0
        for i,mode,mask,ks in actions:
            g,inv,_,cell,_=self.groups[i];t=clock();out=vector(g,inv) if mode=='vector' else targeted(g,inv,ks);ns+=clock()-t;calls+=1
            val=dict(enumerate(out)) if mode=='vector' else dict(zip(ks,out,strict=True))
            for j in bits(mask):values[j]=val[cell[j]]
            B|=mask
        return B,calls,ns

def choose(live,S,B,values,h,left,arm,predict):
    start=clock();n=S.bit_count();free=[];paid=[];prices={};scans=0
    # Scan the symbolic/free layer before estimating candidate purchases.
    for a in range(len(live.probes)):
        if clock()-start>=left:break
        masks,need=live.state(S,B,values,a);cs=[m.bit_count() for m in masks];u=n-sum(cs);scans+=1
        gain=(n*n-sum(v*(u+v) for v in cs)-u*(u+max(cs)))/(n*n)
        singleton=sum(v==1 for v in cs)
        if not need:
            if max(cs)<n:free.append(((singleton/n if h==1 else gain,gain,-a),a,0,[]))
        elif arm!='free':
            # Heuristic, not a certified yield: known singleton mass and a small
            # allowance for unknown replies. All claims still require exact replay.
            hope=min(len(cs),singleton+.25*u)/n
            score=hope if h==1 else gain
            if score>0:paid.append(((score,gain,-need.bit_count(),-a),a,need))
    if arm.startswith('shortlist'):paid=sorted(paid,reverse=True)[:6]
    best=max(free,default=None)
    for r,a,need in paid:
        remain=left-(clock()-start)
        if remain<=30000:break
        est,acts=live.menu(need,'vector' if arm=='vector' else 'hybrid',predict,prices)
        if est+30000>left-(clock()-start):continue
        score=r[0]/(1+2*est/max(1,remain));candidate=((score,r[1],-a),a,est,acts)
        if best is None or candidate[0]>best[0]:best=candidate
    return (None if best is None else best[1:]),scans,len(prices)

def replay(live,oracle,predict,cap,arm):
    rows=[];dec=[];cap*=1000
    def walk(S,B,values,h,elapsed,plan,buy):
        n=S.bit_count()
        def emit():
            for i in bits(S):rows.append(dict(hidden=i,hit=n==1 and elapsed<=cap,remaining=n,elapsed_ns=elapsed,plan_ns=plan,buy_ns=buy,queries=2-h,over=elapsed>cap))
        if n==1 or h==0 or elapsed>=cap:emit();return
        t=clock();choice,scans,profiles=choose(live,S,B,values,h,cap-elapsed,arm,predict);dt=clock()-t;elapsed+=dt;plan+=dt
        if choice is None or elapsed>=cap:emit();return
        a,estimate,acts=choice
        if estimate+30000>cap-elapsed:emit();return
        t=clock();new=values.copy();got,calls,ns=live.execute(acts,new);B2=B|got
        masks,need=live.state(S,B2,new,a);assert not need
        ch=tuple(m for m in masks if m);end=clock()-t;elapsed+=end;buy+=ns
        assert ch==oracle.actual(S,a) and sum(ch)==S
        assert all(new[j]==oracle.values[j] for j in bits(got))
        dec.append(dict(n=n,h=h,probe=a,estimate_ns=estimate,call_ns=ns,selection_ns=dt,execution_ns=end,calls=calls,spent_ns=elapsed,scans=scans,profiles=profiles))
        for child in ch:walk(child,B2,new,h-1,elapsed,plan,buy)
    walk(live.full,0,{},2,0,0,0)
    assert len(rows)==live.n and len({r['hidden'] for r in rows})==live.n
    assert all(not r['hit'] or (r['remaining']==1 and not r['over']) for r in rows)
    return rows,dec

def main():
    p=argparse.ArgumentParser();p.add_argument('--train',required=True);p.add_argument('--prior',nargs='+',required=True);p.add_argument('--out',required=True);p.add_argument('--decks',type=int,default=6);a=p.parse_args()
    profiles=read(a.train)['profiles'];used=set();predictors={w:Predictor(profiles,w) for w in (False,True)}
    for path in [a.train,*a.prior]:
        r=read(path);ds=[z[1] if len(z)==2 else z[2] for z in r['manifest']] if 'manifest' in r else [d['cards'] for d in r.get('decks',r.get('eval_decks',[]))]
        for cs in ds:
            for n,e in cs:used.add(graph_key((n,tuple(map(tuple,e)))))
    prior=len(used);manifest=list(new_decks(used,a.decks));rows=[];dec=[];meta=[];audit=[]
    for i,cards in manifest:
        known_coeff.cache_clear();live=Live(cards);oracle=Deck(cards);assert len(live.owner)==len(oracle.values) and live.needs==oracle.rneeds
        for cap,arm in product(CAPS,ARMS):
            rr,dd=replay(live,oracle,predictors[arm!='shortlist_basic'],cap,arm)
            rows.extend(dict(deck=i,cap=cap,arm=arm,setup_ns=live.setup_ns,**r) for r in rr);dec.extend(dict(deck=i,cap=cap,arm=arm,**r) for r in dd)
        # Strictly after evaluation: fresh cold function timing audit, no feedback into models.
        for g,inv,mask,cell,stats in live.groups:
            if not mask:continue
            ref=direct_coefficients(g)[inv]
            for mode,ks in [('vector',()),*[('batch',(k,)) for k in cell.values()]]:
                estimates=[];pred_times=[]
                for pred in predictors.values():
                    t=clock();estimates.append(pred.price(stats,inv,ks,mode));pred_times.append(clock()-t)
                times=[]
                for _ in range(3):
                    t=clock();ans=vector(g,inv) if mode=='vector' else targeted(g,inv,ks);times.append(clock()-t)
                    assert ans==(ref if mode=='vector' else tuple(ref[k] for k in ks))
                audit.append(dict(deck=i,inv=inv,mode=mode,ks=ks,actual_ns=int(median(times)),basic_ns=estimates[0],work_ns=estimates[1],basic_predict_ns=pred_times[0],work_predict_ns=pred_times[1]))
        meta.append(dict(deck=i,setup_ns=live.setup_ns,oracle_checks=dict(oracle.audit)))
        print('deck',i,'setup_us',live.setup_ns//1000,'rows',len(rows),flush=True,file=sys.stderr)
    summary=[]
    for cap,arm in product(CAPS,ARMS):
        rr=[r for r in rows if (r['cap'],r['arm'])==(cap,arm)];n=len(rr)
        summary.append(dict(cap=cap,arm=arm,n=n,hits=sum(r['hit'] for r in rr),over=sum(r['over'] for r in rr),cold_hits=sum(r['hit'] and r['elapsed_ns']+r['setup_ns']<=cap*1000 for r in rr),mean_us=sum(r['elapsed_ns'] for r in rr)/n/1000,mean_plan_us=sum(r['plan_ns'] for r in rr)/n/1000,mean_buy_us=sum(r['buy_ns'] for r in rr)/n/1000))
    out=dict(evidence='public finite development, measured warm thread CPU budgets',manifest=manifest,prior_graph_hashes=prior,train_profiles=len(profiles),summary=summary,records=rows,decisions=dec,meta=meta,cost_audit=audit,models={str(w):{f'{i}/{m}':{'w':list(v),'margin':pr.margins[i,m]} for (i,m),v in pr.weights.items()} for w,pr in predictors.items()})
    Path(a.out).write_text(json.dumps(out,separators=(',',':')))
if __name__=='__main__':main()

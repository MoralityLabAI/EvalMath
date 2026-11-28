"""CFH-10 exact cost-priced planning and small ranking pilot (public development)."""
import argparse, gzip, hashlib, json, random, sys
from pathlib import Path
from functools import cache
from collections import defaultdict
import numpy as np
import torch
from torch import nn
import networkx as nx
HERE=Path(__file__).resolve().parent
for p in ('CFH09','cfh09_dev'):
    sys.path.insert(0,str(HERE.parent/p))
from value_pilot import Online, Oracle, bits, graph_key, graph_tuple
SCALE=400
PRICES=(0,1,2,4,8,16)
CAPS=(4,12)
SEEDS=(11,29,47)
ARMS=('blind_rank','priced_ties','priced_rank')

def manifest(used):
    rng=random.Random(2026112510)
    for split,count in [('train',8),('shift',8)]:
        for i in range(count):
            cards=[]
            for j in range(3):
                for _ in range(4000):
                    n=rng.randrange(7,9);seed=rng.randrange(2**31)
                    if split=='train':
                        if j==0:g=nx.gnp_random_graph(n,rng.uniform(.15,.85),seed=seed)
                        elif j==1:g=nx.from_prufer_sequence([rng.randrange(n) for _ in range(n-2)])
                        else:g=nx.bipartite.random_graph(n//2,n-n//2,rng.uniform(.2,.85),seed=seed)
                    else:
                        if j==0:g=nx.watts_strogatz_graph(n,4,rng.uniform(.1,.9),seed=seed)
                        elif j==1:g=nx.barabasi_albert_graph(n,2,seed=seed)
                        else:g=nx.random_geometric_graph(n,rng.uniform(.32,.6),seed=seed)
                    labels=list(range(n));rng.shuffle(labels);g=graph_tuple(nx.relabel_nodes(g,dict(enumerate(labels))));k=graph_key(g)
                    if k not in used:used.add(k);cards.append(g);break
                else:raise RuntimeError('generator exhausted')
            yield split,i,tuple(cards)

class Priced(Oracle):
    @cache
    def opt(self,S,B,left,h,p):
        if S.bit_count()==1:return SCALE
        if not h:return 0
        return max(0,max((self.q(S,B,b,l,ch,h,p) for _,b,l,ch in self.options(S,B,left)),default=0))
    def q(self,S,B,b,l,ch,h,p):
        return -p*S.bit_count()*(b&~B).bit_count()+sum(self.opt(t,b,l,h-1,p) for t in ch)
    def labels_priced(self,S,B,left,h,p,acts):
        v={a:self.q(S,B,b,l,ch,h,p) for a,b,l,ch in self.options(S,B,left)}
        return np.array([0 if a==-1 else v[a] for a in acts],np.int64)

class Free:
    def __init__(self,o):self.o=o;self.work=0
    @cache
    def plan(self,S,B,h):
        if S.bit_count()==1:return SCALE,-1
        if not h:return 0,-1
        best=(0,-1)
        for a in range(len(self.o.probes)):
            if self.o.need(S,a)&~B:continue
            cells=[m for m in self.o.known(S,B,a) if m];self.work+=1
            assert sum(cells)==S
            if len(cells)<2:continue
            v=sum(self.plan(t,B,h-1)[0] for t in cells)
            if v>best[0]:best=(v,a)
        return best

def features(o,S,B,left,h,p):
    x,acts,g=o.features(S,B,left,h)
    stop=np.zeros((1,26),np.float32)
    if len(x):
        stop[0,8:12]=x[0,8:12];stop[0,13]=x[0,13];stop[0,21:]=x[0,21:]
    x=np.concatenate([x,stop],axis=0)
    flags=np.zeros((len(x),2),np.float32);flags[:,0]=p/16;flags[-1,1]=1
    return np.concatenate([x,flags],axis=1),acts+[-1],g

def examples(o,oracle,rng):
    out=[]
    for cap in CAPS:
        states=[(o.full,0,cap,2)]
        children=sorted({(t,b,l,1) for _,b,l,ch in oracle.options(o.full,0,cap) for t in ch if t.bit_count()>1})
        rng.shuffle(children);states+=children[:16]
        for S,B,left,h in states:
            o.purchase(B)
            for p in PRICES:
                x,acts,_=features(o,S,B,left,h,p);y=oracle.labels_priced(S,B,left,h,p,acts)
                assert max(y)==oracle.opt(S,B,left,h,p)
                if len(acts)>1:out.append((x,y,p))
    return out

def fit(examples):
    models={}
    for arm in ARMS:
        data=[r for r in examples if r[2]==0] if arm=='blind_rank' else examples
        n=len(data);m=max(len(x) for x,_,_ in data)
        X=np.zeros((n,m,28),np.float32);V=np.zeros((n,m),bool);Y=np.zeros((n,m),np.float32)
        for i,(x,y,p) in enumerate(data):
            X[i,:len(x)]=x;V[i,:len(x)]=True;Y[i,:len(x)]=(y-y.max())/max(1,int(y.max()-y.min()))
        for seed in SEEDS:
            torch.manual_seed(seed);rng=np.random.default_rng(seed)
            model=nn.Sequential(nn.Linear(28,32),nn.Tanh(),nn.Linear(32,32),nn.Tanh(),nn.Linear(32,1));opt=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.001)
            for _ in range(160):
                ii=rng.choice(n,48,replace=True);x,v,y=map(torch.from_numpy,(X[ii],V[ii],Y[ii]));z=model(x).squeeze(-1).masked_fill(~v,-1e9)
                if arm=='priced_ties':
                    t=(y==0)&v;t=t/t.sum(1,keepdim=True)
                else:t=torch.softmax((y/.2).masked_fill(~v,-1e9),1)
                loss=-(t*torch.log_softmax(z,1)).sum(1).mean();opt.zero_grad();loss.backward();opt.step()
            models[arm,seed]=model.eval()
    return models

def replay(o,oracle,free,cap,p,arm,model=None):
    rows=[];decisions=[]
    def walk(S,B,left,h):
        n=S.bit_count();assert B.bit_count()+left==cap
        a=-1
        if n>1 and h:
            x,acts,g=features(o,S,B,left,h,0 if arm=='blind_rank' else p)
            if arm=='exact':
                vals=oracle.labels_priced(S,B,left,h,p,acts);a=acts[max(range(len(acts)),key=lambda j:(vals[j],-(o.need(S,acts[j])&~B).bit_count() if acts[j]!=-1 else 0,acts[j]==-1))]
            elif arm=='free_exact':a=free.plan(S,B,h)[1]
            elif arm in ('greedy','priced_greedy'):
                if g:
                    j=max(range(len(g)),key=lambda j:(g[j][0]-(p/SCALE)*(o.need(S,acts[j])&~B).bit_count() if arm=='priced_greedy' else g[j][0],*g[j]))
                    if arm=='greedy' or g[j][0]-(p/SCALE)*(o.need(S,acts[j])&~B).bit_count()>0:a=acts[j]
                    else:a=free.plan(S,B,h)[1]
            else:
                with torch.no_grad():a=acts[int(model(torch.from_numpy(x)).squeeze(-1).argmax())]
            v=oracle.opt(S,B,left,h,p)
            if a==-1:q=0
            else:
                need=o.need(S,a)&~B;cost=need.bit_count();assert cost<=left
                b=B|need;o.purchase(need);cells=o.known(S,b,a)
                assert cells==tuple(S&m for m in oracle.truth[a]) and sum(cells)==S
                q=oracle.q(S,B,b,left-cost,tuple(t for t in cells if t),h,p)
            decisions.append(dict(n=n,h=h,action=a,regret=v-q))
            if a!=-1:
                for t in cells:
                    if t:walk(t,b,left-cost,h-1)
                return
        for i in bits(S):rows.append(dict(hidden=i,hit=n==1,cost=B.bit_count(),queries=2-h,remaining=n))
    walk(o.full,0,cap,2)
    assert len(rows)==o.n and len({r['hidden'] for r in rows})==o.n
    utility=sum(SCALE*r['hit']-p*r['cost'] for r in rows);optimum=oracle.opt(o.full,0,cap,2,p)
    assert optimum-utility==sum(d['regret'] for d in decisions)
    if arm=='exact':assert optimum==utility
    return rows,decisions

def main():
    p=argparse.ArgumentParser();p.add_argument('--prior',nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);used=set()
    for path in a.prior:
        with gzip.open(path,'rt') as f:r=json.load(f)
        decks=r.get('decks',r.get('eval_decks',[]))
        if 'manifest' in r:decks=[{'cards':z[2]} for z in r['manifest']]
        for d in decks:
            for n,e in d['cards']:used.add(graph_key((n,tuple(map(tuple,e)))))
    prior_count=len(used);ds=list(manifest(used));data=[];train_meta=[];records=[];decision_records=[];meta=[]
    for split,i,cards in ds:
        if split!='train':continue
        for depth in (1,2):
            o=Online(cards,depth);oracle=Priced(o);ex=examples(o,oracle,random.Random(1910+i*10+depth));data+=ex
            train_meta.append(dict(deck=i,depth=depth,examples=len(ex),scans=oracle.scans));oracle.options.cache_clear();oracle.opt.cache_clear()
        print('train deck',i,'examples',len(data),flush=True,file=sys.stderr)
    models=fit(data);print('fits',len(models),flush=True,file=sys.stderr)
    for split,i,cards in ds:
        if split!='shift':continue
        o=Online(cards,2);oracle=Priced(o);free=Free(o)
        for cap in CAPS:
            for price in PRICES:
                for (arm,seed),model in [(('exact',0),None),(('free_exact',0),None),(('greedy',0),None),(('priced_greedy',0),None),*models.items()]:
                    rr,dd=replay(o,oracle,free,cap,price,arm,model)
                    records.extend(dict(deck=i,cap=cap,price=price,arm=arm,seed=seed,**r) for r in rr)
                    decision_records.extend(dict(deck=i,cap=cap,price=price,arm=arm,seed=seed,**d) for d in dd)
        meta.append(dict(deck=i,oracle_scans=oracle.scans,free_scans=free.work,distinct_base_computations=o.misses,symbolic_checks=o.symbolic_checks));oracle.options.cache_clear();oracle.opt.cache_clear();free.plan.cache_clear();print('eval deck',i,'records',len(records),flush=True,file=sys.stderr)
    grouped=defaultdict(list)
    for r in records:grouped[r['cap'],r['price'],r['arm'],r['seed']].append(r)
    summary=[]
    for (cap,price,arm,seed),rr in sorted(grouped.items()):
        n=len(rr);hits=sum(r['hit'] for r in rr);cost=sum(r['cost'] for r in rr);summary.append(dict(cap=cap,price=price,arm=arm,seed=seed,n=n,hits=hits,cost=cost,utility_ticks=SCALE*hits-price*cost,mean_utility=(SCALE*hits-price*cost)/(SCALE*n),mean_cost=cost/n))
    out=dict(evidence='public finite development; offline exact teacher; logical acquisition cost',scale=SCALE,prices=PRICES,manifest=ds,prior_graph_hashes=prior_count,train_examples=len(data),train_meta=train_meta,params=sum(v.numel() for v in next(iter(models.values())).parameters()),meta=meta,summary=summary,records=records,decisions=decision_records,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path(a.out).write_text(json.dumps(out,separators=(',',':')))
if __name__=='__main__':main()

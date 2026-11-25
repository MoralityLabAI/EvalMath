"""CFH-09: exact action-value distillation with charged acquire-and-query actions."""
import argparse, gzip, hashlib, json, random, sys, time
from pathlib import Path
from itertools import combinations
from functools import cache
from math import comb, prod, log2
import networkx as nx
import numpy as np
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
for p in ('CFH04','CFH05','CFH06','CFH07','cfh04_dev','cfh05_dev','cfh06_dev','cfh07_dev'):
    sys.path.insert(0,str(HERE.parent/p))
from hidden_invariant import coefficients, graph_tuple, INVARIANTS, direct_coefficients
from compositional import routes
from lazy_acquisition import cheap_value
from audit import independent_route
CAPS=(0,4,12); SEEDS=(11,29,47); ARMS=('imitation','ties','value','relative_rank'); H=2; STEPS=240; BATCH=48

def bits(s):
    while s:
        t=s&-s; yield t.bit_length()-1; s^=t

def graph_key(g):
    n,e=g; G=nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(e)
    return n,nx.weisfeiler_lehman_graph_hash(G,iterations=4)

def decks(used):
    rng=random.Random(2026112509)
    for split,nd,depths in [('train',10,(1,2)),('shift',8,(2,))]:
        for i in range(nd):
            cards=[]
            for j in range(3):
                for _ in range(3000):
                    n=rng.randrange(7,9); seed=rng.randrange(2**31)
                    if split=='train':
                        if j==0:G=nx.gnp_random_graph(n,rng.uniform(.2,.8),seed=seed)
                        elif j==1:G=nx.from_prufer_sequence([rng.randrange(n) for _ in range(n-2)])
                        else:G=nx.bipartite.random_graph(n//2,n-n//2,rng.uniform(.2,.8),seed=seed)
                    else:
                        if j==0:G=nx.watts_strogatz_graph(n,4,rng.uniform(.1,.9),seed=seed)
                        elif j==1:G=nx.barabasi_albert_graph(n,2,seed=seed)
                        else:G=nx.random_geometric_graph(n,.48,seed=seed)
                    labels=list(range(n));rng.shuffle(labels);g=graph_tuple(nx.relabel_nodes(G,dict(enumerate(labels))));key=graph_key(g)
                    if key not in used:used.add(key);cards.append(g);break
                else:raise RuntimeError('graph generator exhausted')
            yield split,i,tuple(cards),depths

class Online:
    def __init__(self,cards,depth):
        self.cards=cards;self.rr=routes(depth);self.n=len(self.rr);self.full=(1<<self.n)-1
        self.keys=tuple(sorted({r[:4] for r in self.rr}));self.ng=len(self.keys);ix={k:i for i,k in enumerate(self.keys)}
        self.probes=tuple((h,k,p) for h,g in enumerate(cards) for k in range(g[0]+1) for p in (2,3,5))
        self.groups=[0]*self.ng;self.inv=[0]*len(INVARIANTS)
        for i,r in enumerate(self.rr):self.groups[ix[r[:4]]]|=1<<i;self.inv[INVARIANTS.index(r[3])]|=1<<i
        self.cheap=[];self.unknown_groups=[];self.base_cache={};self.res_cache={};self.need_cache={};self.misses=0;self.acq_seconds=0.;self.symbolic_checks=0;self.gf=[]
        for n,e in cards:
            d=[0]*n
            for i,j in e:d[i]+=1;d[j]+=1
            self.gf.append((n/8,len(e)/comb(n,2),max(d)/(n-1),min(d)/(n-1)))
        for h,k,p in self.probes:
            a=[0]*p;unknown=0
            for i,r in enumerate(self.rr):
                v=cheap_value(cards[h],r,k,p);self.symbolic_checks+=1
                if v is None:unknown|=1<<i
                else:a[v]|=1<<i
            self.cheap.append(tuple(a));self.unknown_groups.append(tuple((h*self.ng+j,unknown&m) for j,m in enumerate(self.groups) if unknown&m))
    def need(self,S,a):
        key=S,a
        if key not in self.need_cache:self.need_cache[key]=sum(1<<j for j,m in self.unknown_groups[a] if m&S)
        return self.need_cache[key]
    def purchase(self,B):
        for j in bits(B):
            if j in self.base_cache:continue
            start=time.perf_counter();h,z=divmod(j,self.ng);l,r,c,inv=self.keys[z];n,e=self.cards[h];m=n-l-r
            E={(a-l,b-l) for a,b in e if l<=a<b<n-r}
            if c:E=set(combinations(range(m),2))-E
            g=m,tuple(sorted(E));a=coefficients.__wrapped__(g,inv);self.acq_seconds+=time.perf_counter()-start
            assert a==direct_coefficients(g)[inv]
            self.misses+=1;self.base_cache[j]=a
    def bought_masks(self,a,j):
        key=a,j
        if key in self.res_cache:return self.res_cache[key]
        h,k,p=self.probes[a];assert j//self.ng==h and j in self.base_cache
        v=self.base_cache[j];out=[0]*p
        for i in bits(self.groups[j%self.ng]):
            d,s=self.rr[i][4:];z=sum(v[t]*prod(range(t-d+1,t+1))*comb(t-d,k)*pow(s,t-d-k,p) for t in range(k+d,len(v)))%p
            out[z]|=1<<i
        self.res_cache[key]=tuple(out);return tuple(out)
    def known(self,S,B,a):
        h,k,p=self.probes[a];masks=list(self.cheap[a])
        for j in bits(B & (((1<<self.ng)-1)<<(h*self.ng))):
            for v,m in enumerate(self.bought_masks(a,j)):masks[v]|=m
        return tuple(S&m for m in masks)
    def features(self,S,B,left,horizon):
        n=S.bit_count();rows=[];acts=[];greedy=[]
        for a,(h,k,p) in enumerate(self.probes):
            need=self.need(S,a)&~B;cost=need.bit_count()
            if cost>left:continue
            masks=self.known(S,B,a);counts=[m.bit_count() for m in masks];u=n-sum(counts)
            if not u and max(counts)==n:continue
            gain=(n*n-sum(v*(u+v) for v in counts)-u*(u+max(counts)))/(n*n)
            sure=sum(v==1 for v in counts)/n if u==0 else 0.
            rows.append([*[v/n for v in counts],*[0.]*(5-len(counts)),u/n,gain,sure,log2(n)/log2(self.n),n/self.n,horizon/2,left/12,cost/12,B.bit_count()/(len(self.cards)*self.ng),k/8,p/5,h/2,*self.gf[h],*[(S&m).bit_count()/n for m in self.inv]])
            acts.append(a);greedy.append((sure,gain,-cost,-a) if horizon==1 else (gain,sure,-cost,-a))
        return np.array(rows,np.float32).reshape(-1,26),acts,greedy

class Oracle:
    def __init__(self,o):
        self.o=o;self.truth=[];self.scans=0
        gold=[[independent_route(g,r) for r in o.rr] for g in o.cards]
        for a,(h,k,p) in enumerate(o.probes):
            masks=[0]*p
            for i,v in enumerate(gold[h]):masks[v[k]%p]|=1<<i
            assert all(c&m==c for c,m in zip(o.cheap[a],masks,strict=True));self.truth.append(tuple(masks))
    @cache
    def options(self,S,B,left):
        out=[]
        for a,masks in enumerate(self.truth):
            self.scans+=1;need=self.o.need(S,a)&~B;cost=need.bit_count()
            if cost>left:continue
            ch=tuple(S&m for m in masks if S&m)
            if len(ch)==1 and not cost:continue
            out.append((a,B|need,left-cost,ch))
        return tuple(out)
    @cache
    def value(self,S,B,left,horizon):
        if S.bit_count()==1:return 1
        if not horizon:return 0
        return max((self.qvalue(b,l,ch,horizon) for _,b,l,ch in self.options(S,B,left)),default=0)
    def qvalue(self,B,left,ch,horizon):
        if horizon==1:return sum(c.bit_count()==1 for c in ch)
        return sum(self.value(c,B,left,horizon-1) for c in ch)
    def labels(self,S,B,left,horizon,acts):
        vals={a:self.qvalue(b,l,ch,horizon) for a,b,l,ch in self.options(S,B,left)}
        assert all(a in vals for a in acts)
        return np.array([vals[a]/S.bit_count() for a in acts],np.float32)

def examples(o,oracle,rng):
    out=[]
    for cap in CAPS:
        states=[(o.full,0,cap,H)]
        children=sorted({(c,b,l,1) for _,b,l,ch in oracle.options(o.full,0,cap) for c in ch if c.bit_count()>1})
        rng.shuffle(children);states+=children[:32]
        for S,B,left,h in states:
            o.purchase(B);x,acts,g=o.features(S,B,left,h)
            if not acts:continue
            y=oracle.labels(S,B,left,h,acts)
            if y.max()==0:continue
            t=max(range(len(acts)),key=lambda j:(y[j],g[j]));out.append((x,y,t))
    return out

def train(data):
    n=len(data);m=max(len(x) for x,_,_ in data);X=np.zeros((n,m,26),np.float32);V=np.zeros((n,m),bool);Y=np.zeros((n,m),np.float32);T=np.zeros(n,np.int64)
    for i,(x,y,t) in enumerate(data):X[i,:len(x)]=x;V[i,:len(x)]=True;Y[i,:len(x)]=y;T[i]=t
    models={}
    for seed in SEEDS:
        for arm in ARMS:
            torch.manual_seed(seed);rng=np.random.default_rng(seed)
            model=nn.Sequential(nn.Linear(26,32),nn.Tanh(),nn.Linear(32,32),nn.Tanh(),nn.Linear(32,1));opt=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.001)
            for _ in range(STEPS):
                ii=rng.choice(n,BATCH,replace=False);x,v,y,t=map(torch.from_numpy,(X[ii],V[ii],Y[ii],T[ii]));z=model(x).squeeze(-1)
                if arm=='value':loss=((torch.sigmoid(z)-y).square()*v).sum()/v.sum()
                elif arm=='relative_rank':
                    # Per-prefix normalization preserves relative regret at small absolute Q.
                    target=torch.softmax((y/y.max(1,keepdim=True).values.clamp_min(1e-8)/.2).masked_fill(~v,-1e9),1)
                    loss=-(target*torch.log_softmax(z.masked_fill(~v,-1e9),1)).sum(1).mean()
                else:
                    logp=torch.log_softmax(z.masked_fill(~v,-1e9),1)
                    if arm=='imitation':loss=-logp[torch.arange(len(ii)),t].mean()
                    else:
                        tied=(y==y.max(1,keepdim=True).values)&v;loss=-(logp*tied).sum(1).div(tied.sum(1)).mean()
                opt.zero_grad();loss.backward();opt.step()
            models[arm,seed]=model.eval()
    return models

def run(o,oracle,cap,arm,model):
    rows=[];decisions=[]
    def walk(S,B,left,h):
        assert B.bit_count()+left==cap
        if S.bit_count()>1 and h:
            x,acts,g=o.features(S,B,left,h)
            if acts:
                if arm=='greedy':j=max(range(len(acts)),key=lambda j:g[j])
                elif arm=='cost_greedy':j=max(range(len(acts)),key=lambda j:(g[j][0]/(1+(o.need(S,acts[j])&~B).bit_count()),g[j]))
                elif arm=='exact':
                    y=oracle.labels(S,B,left,h,acts);j=max(range(len(acts)),key=lambda j:(y[j],g[j]))
                else:
                    with torch.no_grad():j=int(model(torch.from_numpy(x)).squeeze(-1).argmax())
                a=acts[j];need=o.need(S,a)&~B;cost=need.bit_count();new=B|need;o.purchase(need)
                masks=o.known(S,new,a);gold=tuple(S&m for m in oracle.truth[a]);assert masks==gold and sum(masks)==S
                y=oracle.labels(S,B,left,h,acts) # scored after action selection
                decisions.append(dict(h=h,n=S.bit_count(),action=a,cost=cost,value=float(y[j]),optimal=float(y.max()),optimal_action=bool(y[j]==y.max())))
                for m in masks:
                    if m:walk(m,new,left-cost,h-1)
                return
        for i in bits(S):rows.append(dict(hidden=i,hit=S.bit_count()==1,cost=B.bit_count(),queries=H-h,remaining=S.bit_count()))
    walk(o.full,0,cap,H);assert len(rows)==o.n and len({r['hidden'] for r in rows})==o.n
    if arm=='exact':assert sum(r['hit'] for r in rows)==oracle.value(o.full,0,cap,H)
    return rows,decisions

def main():
    p=argparse.ArgumentParser();p.add_argument('--prior-candidates',required=True);p.add_argument('--prior-pilot',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);used=set()
    for path in (a.prior_candidates,a.prior_pilot):
        with gzip.open(path,'rt') as f:r=json.load(f)
        for d in r.get('decks',r.get('eval_decks',[])):
            for n,e in d['cards']:used.add(graph_key((n,tuple(map(tuple,e)))))
    manifest=list(decks(used));data=[];training_scans=0;train_meta=[]
    for split,i,cards,depths in manifest:
        if split!='train':continue
        for depth in depths:
            o=Online(cards,depth);oracle=Oracle(o);ex=examples(o,oracle,random.Random(1000+i*10+depth));data+=ex;training_scans+=oracle.scans;train_meta.append(dict(deck=i,depth=depth,examples=len(ex),scans=oracle.scans));oracle.options.cache_clear();oracle.value.cache_clear()
        print('train deck',i,'prefixes',len(data),flush=True,file=sys.stderr)
    models=train(data);print('trained',len(models),'fits',flush=True,file=sys.stderr);rows=[];decisions=[];meta=[]
    for split,i,cards,depths in manifest:
        if split!='shift':continue
        o=Online(cards,2);oracle=Oracle(o)
        for cap in CAPS:
            for (arm,seed),model in [(('greedy',0),None),(('cost_greedy',0),None),(('exact',0),None),*models.items()]:
                rr,dd=run(o,oracle,cap,arm,model);rows.extend(dict(deck=i,cap=cap,arm=arm,seed=seed,**r) for r in rr);decisions.extend(dict(deck=i,cap=cap,arm=arm,seed=seed,**r) for r in dd)
        meta.append(dict(deck=i,scans=oracle.scans,distinct_base_computations=o.misses,acquisition_seconds=o.acq_seconds,symbolic_checks=o.symbolic_checks));oracle.options.cache_clear();oracle.value.cache_clear();print('test deck',i,'rows',len(rows),flush=True,file=sys.stderr)
    summary=[]
    for cap in CAPS:
        for arm in ('greedy','cost_greedy','exact',*ARMS):
            for seed in (SEEDS if arm in ARMS else (0,)):
                rr=[r for r in rows if (r['cap'],r['arm'],r['seed'])==(cap,arm,seed)];dd=[r for r in decisions if (r['cap'],r['arm'],r['seed'])==(cap,arm,seed)];summary.append(dict(cap=cap,arm=arm,seed=seed,cases=len(rr),hits=sum(r['hit'] for r in rr),mean_cost=sum(r['cost'] for r in rr)/len(rr),mean_queries=sum(r['queries'] for r in rr)/len(rr),decisions=len(dd),weighted_regret=sum(r['n']*(r['optimal']-r['value']) for r in dd)/len(rr)))
    result=dict(evidence='public finite development; privileged offline exact teacher',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),manifest=manifest,train_meta=train_meta,training_examples=len(data),training_scans=training_scans,params=sum(p.numel() for p in next(iter(models.values())).parameters()),meta=meta,summary=summary,rows=rows,decisions=decisions)
    Path(a.out).write_text(json.dumps(result,separators=(',',':')));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

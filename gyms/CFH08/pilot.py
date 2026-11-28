"""CFH-08: public-development, prefix-deduplicated query imitation with state supervision."""
from pathlib import Path
from itertools import product
import argparse,gzip,hashlib,json,math,random,sys
import networkx as nx
import numpy as np
import torch
from torch import nn
HERE=Path(__file__).resolve().parent
for p in ('CFH04','CFH05','CFH06','CFH07','cfh04_dev','cfh05_dev','cfh06_dev','cfh07_dev'):
    sys.path.insert(0,str(HERE.parent/p))
from lazy_acquisition import Deck
from hidden_invariant import graph_tuple,INVARIANTS
from audit import build_env
from transition import verify
SEEDS=(11,29,47)
CAPS=(39,100)
ARMS=('action','state','shuffled')
WIDTH=32
UPDATES=240
BATCH=48
AUX_WEIGHT=1.0
NDECK=8

def cards(raw):return tuple((n,tuple(map(tuple,e))) for n,e in raw)
def graph(g):
    n,e=g;G=nx.Graph();G.add_nodes_from(range(n));G.add_edges_from(e);return G

def graph_key(g):return (g[0],nx.weisfeiler_lehman_graph_hash(graph(g),iterations=4))
def fresh_decks(used):
    rng=random.Random(2026112508)
    for j in range(NDECK):
        cs=[]
        for kind in ('er','prufer','random_bipartite'):
            for _ in range(2000):
                n=rng.randrange(7,9);seed=rng.randrange(2**31)
                if kind=='er':G=nx.gnp_random_graph(n,rng.uniform(.15,.85),seed=seed)
                elif kind=='prufer':G=nx.from_prufer_sequence([rng.randrange(n) for _ in range(n-2)])
                else:
                    k=rng.randrange(2,n-1);G=nx.bipartite.random_graph(k,n-k,rng.uniform(.25,.85),seed=seed)
                labels=list(range(n));rng.shuffle(labels);g=graph_tuple(nx.relabel_nodes(G,dict(enumerate(labels))));key=graph_key(g)
                if key not in used:used.add(key);cs.append(g);break
            else:raise RuntimeError('generator exhausted')
        yield dict(seed=97000+j,cards=tuple(cs),generators=['er','prufer','random_bipartite'])

class Context:
    def __init__(self,cs):
        self.d=Deck(cs);d=self.d;self.cache={}
        self.inv=[sum(1<<i for i,r in enumerate(d.rr) if r[3]==v) for v in INVARIANTS]
        self.gf=[]
        for g in cs:
            G=graph(g);ds=np.array([x for _,x in G.degree()]);n=len(G)
            self.gf.append([n/8,nx.density(G),float(ds.max()/(n-1)),float(ds.std()/(n-1)),nx.transitivity(G)])
    def features(self,S,bought,asked,steps,cap,left):
        key=(S,bought,asked,steps,cap,left)
        if key in self.cache:return self.cache[key]
        d=self.d;n=S.bit_count();inv=[(S&m).bit_count()/n for m in self.inv];rows=[];indices=[];gains=[]
        for idx,(h,k,p) in enumerate(d.probes):
            if asked>>idx&1:continue
            masks=d.known_masks(idx,bought,True);counts=[(S&m).bit_count() for m in masks];u=n-sum(counts)
            gain=n*n-(sum(v*(u+v) for v in counts)+u*(u+max(counts)))
            if gain<=0:continue
            rows.append([*(v/n for v in counts),*([0.]*(5-len(counts))),u/n,math.log2(n)/math.log2(d.n),n/d.n,steps/4,left/100,cap/100,k/8,p/5,h/2,*self.gf[h],*inv]);indices.append(idx);gains.append(gain)
        out=(np.array(rows,np.float32).reshape(-1,24),indices,gains);self.cache[key]=out;return out
    def targets(self,S,A):
        return np.array([A.bit_count()/S.bit_count(),*[(A&m).bit_count()/S.bit_count() for m in self.inv]],np.float32)

def extract(pack,contexts):
    splits={'train':{},'dev':{}}
    for e in pack['episodes']:
        seed=e['deck'];split='train' if seed<96100 else 'dev';ctx=contexts[seed];d=ctx.d;S=d.full;bought=(0,)*len(d.cards);asked=steps=0;cap=e['base_cap'];left=cap;history=[]
        for ev in e['events']:
            a=ev['proposal'];after=int(ev['verified']['version_set'],16)
            if a['action']=='buy':
                b=list(bought)
                for j in a['groups']:
                    h,k=divmod(j,d.k);assert not(b[h]>>k&1);b[h]|=1<<k;left-=1
                bought=tuple(b);assert left>=0
            elif a['action']=='observe':
                idx=a['probe'];reply=ev['environment']['reply'];key=(seed,cap,S,bought,asked,steps,left,tuple(history));x,inds,_=ctx.features(S,bought,asked,steps,cap,left);assert idx in inds
                row=splits[split].setdefault(key,dict(x=x,y=inds.index(idx),aux={}))
                assert row['y']==inds.index(idx) and np.array_equal(row['x'],x)
                t=ctx.targets(S,after)
                if reply in row['aux']:assert np.array_equal(row['aux'][reply],t)
                row['aux'][reply]=t;history.append((idx,reply));asked|=1<<idx;steps+=1
            else:assert a['action']=='finish'
            S=after
    return {k:list(v.values()) for k,v in splits.items()}

def arrays(data):
    n=len(data);m=max(len(r['x']) for r in data);X=np.zeros((n,m,24),np.float32);V=np.zeros((n,m),bool);Y=np.zeros(n,np.int64);T=np.zeros((n,5,6),np.float32);M=np.zeros((n,5),bool)
    for i,r in enumerate(data):
        k=len(r['x']);X[i,:k]=r['x'];V[i,:k]=True;Y[i]=r['y']
        for a,t in r['aux'].items():T[i,a]=t;M[i,a]=True
    return X,V,Y,T,M

class Model(nn.Module):
    def __init__(self):
        super().__init__();self.body=nn.Sequential(nn.Linear(24,WIDTH),nn.Tanh(),nn.Linear(WIDTH,WIDTH),nn.Tanh());self.action=nn.Linear(WIDTH,1);self.state=nn.Linear(WIDTH,30)
    def forward(self,x):
        h=self.body(x);return self.action(h).squeeze(-1),self.state(h).reshape(*h.shape[:-1],5,6)

def fit(data,seed,arm):
    torch.manual_seed(seed);rng=np.random.default_rng(seed);X,V,Y,T,M=arrays(data);n=len(X)
    if arm=='shuffled':
        inds=np.argwhere(M);vals=np.array([T[i,a] for i,a in inds]);perm=np.random.default_rng(seed+9000).permutation(len(vals))
        for (i,a),v in zip(inds,vals[perm]):T[i,a]=v
    model=Model();opt=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.001)
    for _ in range(UPDATES):
        ii=rng.choice(n,BATCH,replace=False);x,v,y,t,m=map(torch.from_numpy,(X[ii],V[ii],Y[ii],T[ii],M[ii]));a,z=model(x);act=nn.functional.cross_entropy(a.masked_fill(~v,-1e9),y)
        state=torch.sigmoid(z[torch.arange(len(ii)),y]);aux=((state-t).square().mean(-1)*m).sum()/m.sum().clamp_min(1)
        loss=act+(0 if arm=='action' else AUX_WEIGHT)*aux;opt.zero_grad();loss.backward();opt.step()
    return model.eval()

def imitation(model,data):
    X,V,Y,T,M=arrays(data);correct=0;err=0.;count=0
    with torch.no_grad():
        for i in range(0,len(Y),128):
            x,v,y,t,m=map(torch.from_numpy,(X[i:i+128],V[i:i+128],Y[i:i+128],T[i:i+128],M[i:i+128]));a,z=model(x);a=a.masked_fill(~v,-1e9);state=torch.sigmoid(z[torch.arange(len(y)),y]);correct+=int((a.argmax(1)==y).sum());err+=float(((state-t).square().mean(-1)*m).sum());count+=int(m.sum())
    return dict(correct=correct,total=len(Y),state_mse=err/count)

def run(ctx,env,cap,model=None,arm='teacher'):
    d=ctx.d;rows=[]
    def walk(S,T,bought,left,asked,steps,events):
        assert T and T&S==T and left>=0
        if S.bit_count()>1 and steps<4:
            # Identical acquisition rule and exact admissible-query filter across arms.
            best,_=d.choose(S,bought,asked,True,steps==3)
            while left and S.bit_count()>1 and (best is None or best[3]*2<S.bit_count()**2 or (steps==3 and best[0][0]<S.bit_count())):
                b,c,_=d.acquire(S,bought,left,'symbolic_terminal')
                if not c:break
                gs=[h*d.k+j for h,(old,new) in enumerate(zip(bought,b)) for j in range(d.k) if (new^old)>>j&1];bought=b;left-=c
                for e in events:
                    if e['kind']=='observe':
                        masks=d.known_masks(e['probe'],bought,True);S &= (~sum(masks)|masks[e['reply']])
                assert T&S==T;events=events+[dict(kind='buy',groups=gs,remaining=S)]
                if S.bit_count()==1:break
                best,_=d.choose(S,bought,asked,True,steps==3)
            if S.bit_count()>1 and best is not None:
                if model is None and arm=='teacher':idx=best[1]
                else:
                    x,inds,gains=ctx.features(S,bought,asked,steps,cap,left);assert inds
                    if model is None:idx=inds[max(range(len(inds)),key=lambda j:(gains[j],-inds[j]))]
                    else:
                        with torch.no_grad():score=model(torch.from_numpy(x))[0]
                        idx=inds[int(score.argmax())]
                masks=d.known_masks(idx,bought,True);unknown=S&~sum(masks)
                for v,t in enumerate(d.truth[idx]):
                    child=T&t
                    if child:
                        after=S&(unknown|masks[v]);walk(after,child,bought,left,asked|1<<idx,steps+1,events+[dict(kind='observe',probe=idx,reply=v,remaining=after)])
                return
        end=dict(kind='finish',claim=S.bit_length()-1 if S.bit_count()==1 else None,remaining=S)
        for h in range(d.n):
            if T>>h&1:rows.append(dict(hidden=h,**verify(env,events+[end],h,cap,4)))
    walk(d.full,d.full,(0,)*len(d.cards),cap,0,0,[]);assert len(rows)==d.n and len({r['hidden'] for r in rows})==d.n;return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('candidates');p.add_argument('--out',required=True);a=p.parse_args();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    raw=Path(a.candidates).read_bytes();pack=json.loads(gzip.decompress(raw) if str(a.candidates).endswith('.gz') else raw);assert pack['schema']=='cfh07/candidate-pack/v1' and not pack['training_ready'];contexts={};used=set();hashes={'train':set(),'dev':set()}
    for d in pack['decks']:
        cs=cards(d['cards']);contexts[d['seed']]=Context(cs);hs={graph_key(c) for c in cs};used|=hs;hashes['train' if d['seed']<96100 else 'dev']|=hs
    overlap=len(hashes['train']&hashes['dev']);fresh=list(fresh_decks(used));data=extract(pack,contexts);print('prefixes', {k:(len(v),sum(len(r['aux']) for r in v)) for k,v in data.items()},'train/dev hash overlap',overlap,flush=True,file=sys.stderr)
    models={};imit=[]
    for seed in SEEDS:
        for arm in ARMS:
            m=fit(data['train'],seed,arm);models[arm,seed]=m;imit.append(dict(arm=arm,seed=seed,train=imitation(m,data['train']),dev=imitation(m,data['dev'])))
        print('fit',seed,flush=True,file=sys.stderr)
    records=[]
    for deck in fresh:
        ctx=Context(deck['cards']);env=build_env(ctx.d);assert env.validate()==220
        for cap in CAPS:
            for (arm,seed),m in [(('teacher',0),None),(('gain',0),None),*models.items()]:
                rr=run(ctx,env,cap,m,arm);records.extend(dict(deck=deck['seed'],cap=cap,arm=arm,seed=seed,**r) for r in rr)
        print('deck',deck['seed'],'records',len(records),flush=True,file=sys.stderr);env.restrict.cache_clear();ctx.d.coverage.cache_clear()
    sums=[]
    for cap in CAPS:
        for arm in ('teacher','gain',*ARMS):
            for seed in ((0,) if arm in ('teacher','gain') else SEEDS):
                rr=[r for r in records if (r['cap'],r['arm'],r['seed'])==(cap,arm,seed)];sums.append(dict(cap=cap,arm=arm,seed=seed,cases=len(rr),hits=sum(r['identified'] for r in rr),mean_base=sum(r['base_calls'] for r in rr)/len(rr),mean_queries=sum(r['queries'] for r in rr)/len(rr),mean_remaining=sum(r['remaining'] for r in rr)/len(rr)))
    receipt=dict(evidence='public development; no independent conjecture or causal claim',candidate_sha256=hashlib.sha256(raw).hexdigest(),train_decks=sorted(k for k in contexts if k<96100),dev_decks=sorted(k for k in contexts if k>=96100),train_dev_hash_overlap=overlap,eval_decks=fresh,examples={k:dict(prefixes=len(v),observed_reply_targets=sum(len(r['aux']) for r in v)) for k,v in data.items()},params=sum(p.numel() for p in next(iter(models.values())).parameters()),updates=UPDATES,batch=BATCH,seeds=SEEDS,lambda_state=AUX_WEIGHT,imitation=imit,summary=sums,records=records,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    Path(a.out).write_text(json.dumps(receipt,separators=(',',':')));print(json.dumps(sums,indent=2))
if __name__=='__main__':main()

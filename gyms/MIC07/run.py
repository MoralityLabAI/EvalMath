"""MIC-07 CPU diagnostic: fixed versus active graph priorities; closure-call budget."""
from dataclasses import dataclass
from random import Random
from time import perf_counter
from pathlib import Path
import heapq, json, hashlib
import numpy as np
import torch
from torch import nn
FAMILIES=('conflict','implication','disjunction','mixed')
SEEDS=(17,29,43)
BUDGET=32
@dataclass(frozen=True)
class Root:
    w:tuple
    edges:tuple
    sup:tuple

def root(f,s,n):
    r=Random(s+100003*FAMILIES.index(f));w=tuple(r.randint(1,12) for _ in range(n))
    edges=tuple((i,j) for i in range(n) for j in range(i+1,n) if r.random()<(.30 if f!='mixed' else .23)) or ((0,1),)
    sup=[]
    if f!='conflict':
        for i in range(n):
            if r.random()<.65:
                k=1 if f=='implication' else 2 if f=='disjunction' else r.choice((1,2,3))
                sup.append((i,sum(1<<j for j in r.sample([j for j in range(n) if i!=j],k))))
            if f=='mixed' and r.random()<.25:sup.append((i,sum(1<<j for j in r.sample([j for j in range(n) if i!=j],2))))
    return Root(w,edges,tuple(sup))

def valid(d,s):return type(s)==int and 0<=s<1<<len(d.w) and all(not(s>>i&1 and s>>j&1) for i,j in d.edges) and all(not(s>>i&1) or bool(s&a) for i,a in d.sup)
def val(d,s):return sum(w for i,w in enumerate(d.w) if s>>i&1)
def conflict(d,s):return next(((i,j) for i,j in d.edges if s>>i&1 and s>>j&1),None)
def closure(d,s):
    c=0
    while True:
        old=s
        for i,a in d.sup:
            c+=1
            if s>>i&1 and not s&a:s &= ~(1<<i)
        if old==s:return s,c

def exact_table(d):
    n=len(d.w);a=np.array([val(d,s) if valid(d,s) else -1 for s in range(1<<n)],dtype=np.int32)
    for i in range(n):
        v=a.reshape(-1,2,1<<i);v[:,1,:]=np.maximum(v[:,1,:],v[:,0,:])
    return a

def features(d,s):
    n=len(d.w);active=np.array([s>>i&1 for i in range(n)],np.float32)
    c=np.zeros((n,n),np.float32);a=c.copy();b=c.copy();arity=np.zeros(n,np.float32)
    for i,j in d.edges:
        if active[i] and active[j]:c[i,j]=c[j,i]=1
    for i,m in d.sup:
        js=[j for j in range(n) if active[j] and m>>j&1]
        if active[i] and js:
            arity[i]+=len(js)
            for j in js:a[i,j]+=1/len(js);b[j,i]+=1/len(js)
    x=np.stack([np.array(d.w)/12,c.sum(1)/n,a.sum(1)/n,b.sum(1)/n,arity/n,active],axis=-1).astype(np.float32)
    g=np.stack([c,a,b]);g/=np.maximum(1,g.sum(-1,keepdims=True));return torch.from_numpy(x),torch.from_numpy(g)

class Net(nn.Module):
    def __init__(self):
        super().__init__();self.embed=nn.Linear(6,16);self.cell=nn.GRUCell(48,16);self.head=nn.Linear(16,1)
    def forward(self,x,a,h=None):
        z=torch.tanh(self.embed(x));h=z if h is None else h+z
        for _ in range(3):
            msgs=torch.cat([a[:,j]@h for j in range(3)],-1);h=self.cell(msgs.reshape(-1,48),h.reshape(-1,16)).reshape_as(h)
        return self.head(h).squeeze(-1),h

def trajectory(d):
    table=exact_table(d);s,_=closure(d,(1<<len(d.w))-1);out=[]
    while (e:=conflict(d,s)) is not None:
        i,j=e;x,a=features(d,s);q,_=closure(d,s&~(1<<i));r,_=closure(d,s&~(1<<j));vi,vj=table[q],table[r]
        out.append((x,a,i,j,float(vj>vi)+.5*float(vj==vi)));s=q if vi>=vj else r
    return out

def train(data,seed,persistent):
    torch.manual_seed(seed);net=Net();opt=torch.optim.Adam(net.parameters(),lr=.008);T=max(map(len,data));N=len(data[0][0][0]);B=len(data)
    X=torch.zeros(B,T,N,6);A=torch.zeros(B,T,3,N,N);I=torch.zeros(B,T,dtype=torch.long);J=I.clone();Y=torch.zeros(B,T);M=torch.zeros(B,T)
    for k,tr in enumerate(data):
        for t,(x,a,i,j,y) in enumerate(tr):X[k,t]=x;A[k,t]=a;I[k,t]=i;J[k,t]=j;Y[k,t]=y;M[k,t]=1
    ar=torch.arange(B)
    for _ in range(40):
        h=None;loss=0
        for t in range(T):
            z,h=net(X[:,t],A[:,t],h if persistent else None)
            loss+=(nn.functional.binary_cross_entropy_with_logits(z[ar,I[:,t]]-z[ar,J[:,t]],Y[:,t],reduction='none')*M[:,t]).sum()
        opt.zero_grad();(loss/M.sum()).backward();opt.step()
    return net

@torch.no_grad()
def greedy(d,mode,net=None,budget=BUDGET):
    t=perf_counter();s,checks=closure(d,(1<<len(d.w))-1);calls=1;h=None;z=None
    while (e:=conflict(d,s)) is not None and calls<budget:
        if net is not None:
            if mode!='frozen' or z is None:
                x,a=features(d,s);z,h=net(x[None],a[None],h if mode=='persistent' else None);z=z[0]
            k=min(e,key=lambda k:(float(z[k]),-k))
        else:
            degree=lambda k:sum(k in e2 and all(s>>l&1 for l in e2) for e2 in d.edges)
            k=min(e,key=lambda k:(d.w[k]/(1+degree(k)),-k))
        s,c=closure(d,s&~(1<<k));calls+=1;checks+=c
    if not valid(d,s):s=0
    return dict(value=val(d,s),mask=s,calls=calls,support_checks=checks,ms=(perf_counter()-t)*1000)

def branch(d,budget=BUDGET):
    t=perf_counter();g=greedy(d,'degree',budget=budget);best=g['mask'];calls=g['calls'];checks=g['support_checks']
    if calls>=budget:return {**g,'certified_optimal':False}
    s,c=closure(d,(1<<len(d.w))-1);calls+=1;checks+=c;heap=[(-val(d,s),s)];seen={s}
    while heap and -heap[0][0]>val(d,best):
        if calls+2>budget:break
        _,s=heapq.heappop(heap);e=conflict(d,s)
        if e is None:
            if val(d,s)>val(d,best):best=s
            continue
        for i in e:
            q,c=closure(d,s&~(1<<i));calls+=1;checks+=c
            if q not in seen:
                seen.add(q)
                if valid(d,q):
                    if val(d,q)>val(d,best):best=q
                elif val(d,q)>val(d,best):heapq.heappush(heap,(-val(d,q),q))
    assert valid(d,best)
    return dict(value=val(d,best),mask=best,calls=calls,support_checks=checks,ms=(perf_counter()-t)*1000,certified_optimal=not heap or -heap[0][0]<=val(d,best))

def run():
    torch.set_num_threads(1);start=perf_counter();data=[trajectory(root(f,s,10)) for f in ('conflict','mixed') for s in range(96)]
    models={(mode,s):train(data,s,mode=='persistent') for s in SEEDS for mode in ('dynamic','persistent')};rows=[]
    for f in FAMILIES:
        for n in (10,12):
            for s in range(2000,2016):
                d=root(f,s,n);gold=int(exact_table(d)[-1]);arms={'degree':greedy(d,'degree'),'bnb32':branch(d)}
                for seed in SEEDS:
                    net=models['dynamic',seed];arms[f'frozen_{seed}']=greedy(d,'frozen',net);arms[f'dynamic_{seed}']=greedy(d,'dynamic',net);arms[f'persistent_{seed}']=greedy(d,'persistent',models['persistent',seed])
                assert all(valid(d,a['mask']) and a['value']<=gold and a['calls']<=BUDGET for a in arms.values())
                assert not arms['bnb32']['certified_optimal'] or arms['bnb32']['value']==gold
                rows.append(dict(family=f,n=n,seed=s,gold=gold,arms=arms))
    return dict(schema='MIC-07/public-cpu/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),train_roots=len(data),training_steps=sum(map(len,data)),parameters=sum(p.numel() for p in next(iter(models.values())).parameters()),budget=BUDGET,model_seeds=SEEDS,rows=rows,torch=torch.__version__,elapsed_s=perf_counter()-start)
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))

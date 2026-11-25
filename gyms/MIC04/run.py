"""MIC-04: revisitable integer recurrence certificates, public CPU development."""
from functools import lru_cache
from random import Random
from pathlib import Path
import hashlib, json, time
import torch
from torch import nn

FAMILIES=('dag','ring','chords','nearcritical')
TRAIN=('dag','ring')
KS=(1,2,4,8,16)
SEEDS=(17,29,43)


def make(f, seed, n):
    rng=Random(100003*FAMILIES.index(f)+seed)
    order=list(range(n));rng.shuffle(order)
    m=[[0]*n for _ in range(n)]
    for i,u in enumerate(order):
        if f=='dag':
            targets=order[i+1:]; rng.shuffle(targets); rem=8
            for v in targets:
                m[u][v]=rng.randint(0,rem);rem-=m[u][v]
        else:
            v=order[(i+1)%n]
            m[u][v]=rng.randint(3,8) if f=='ring' else rng.randint(2,5)
            if f!='ring':
                w=order[(i+2)%n]
                m[u][w]=(9-m[u][v]) if f=='nearcritical' else rng.randint(1,8-m[u][v])
    return tuple(map(tuple,m)),tuple(rng.randint(1,9) for _ in range(n))


def h(d,p,i):
    m,b=d;return b[i]+(sum(x*y for x,y in zip(m[i],p))+9)//10


def valid(d,p):
    return len(p)==len(d[1]) and all(type(x)==int and x>=0 and x>=h(d,p,i) for i,x in enumerate(p))


def initial(d):
    m,b=d;k=max(-(-10*y//(10-sum(row))) for row,y in zip(m,b));p=(k,)*len(b)
    assert valid(d,p);return p


def move(d,p,i):
    v=h(d,p,i);assert v<=p[i]
    return p[:i]+(v,)+p[i+1:]


def least(d):
    p=(0,)*len(d[1]); cap=initial(d)
    while True:
        q=tuple(h(d,p,i) for i in range(len(p)))
        assert all(x<=y<=z for x,y,z in zip(p,q,cap))
        if p==q:return p
        p=q


def terminal(d):
    p=initial(d)
    while True:
        q=tuple(h(d,p,i) for i in range(len(p)))
        assert all(y<=x for x,y in zip(p,q)) and valid(d,q)
        if p==q:return p
        p=q


def oracle(d):
    floor=sum(terminal(d))
    @lru_cache(None)
    def V(p,k):
        cost=sum(p)
        if not k or cost==floor:return cost
        nexts=[move(d,p,i) for i in range(len(p))]
        return min([cost]+[V(q,k-1) for q in nexts if q!=p])
    return V


def scan(d,p,k,K,age):
    m,b=d;n=len(p);base=sum(initial(d));rs=[p[i]-h(d,p,i) for i in range(n)]
    qs=[move(d,p,i) for i in range(n)]
    assert all(valid(d,q) for q in qs)
    xs=[]; keys=[]
    for i,r in enumerate(rs):
        impact=sum(m[j][i] for j in range(n));out=sum(m[i]);down=sum(m[i][j]*rs[j] for j in range(n))
        keys.append((r*(10+impact),r,-i))
        xs.append([r/max(1,base),p[i]/max(1,max(p)),b[i]/10,impact/(10*n),out/10,
                   down/(10*max(1,base)), k/16,K/16,age[i]/16,sum(p)/base])
    return qs,rs,keys,xs


def teacher(d,K):
    p=initial(d);n=len(p);age=[0]*n;v=oracle(d);rows=[]
    for k in range(K,0,-1):
        qs,rs,_,xs=scan(d,p,k,K,age)
        mask=[r>0 for r in rs] if any(rs) else [True]*n
        costs=[v(q,k-1) if mask[i] else None for i,q in enumerate(qs)]
        best=min(x for x in costs if x is not None);labels=[x==best for x in costs]
        rows.append((xs,mask,labels));i=labels.index(True);p=qs[i];age=[a+1 for a in age];age[i]=0
    return rows


class Ranker(nn.Module):
    def __init__(self,recurrent):
        super().__init__();self.recurrent=recurrent;self.cell=nn.GRUCell(10,16)
        self.head=nn.Sequential(nn.Linear(26,16),nn.Tanh(),nn.Linear(16,1))
    def step(self,x,mask,hid):
        pooled=(x*mask.unsqueeze(-1)).sum(1)/mask.sum(1,keepdim=True)
        hid=self.cell(pooled,hid if self.recurrent else torch.zeros_like(hid))
        z=self.head(torch.cat([x,hid.unsqueeze(1).expand(-1,x.shape[1],-1)],-1)).squeeze(-1)
        return z.masked_fill(~mask,-torch.inf),hid


def fit(batches,seed,recurrent):
    torch.manual_seed(seed);net=Ranker(recurrent);opt=torch.optim.Adam(net.parameters(),lr=.01)
    for _ in range(40):
        for x,mask,labels in batches:
            hid=torch.zeros(len(x),16);loss=0
            for t in range(x.shape[1]):
                z,hid=net.step(x[:,t],mask[:,t],hid)
                loss=loss+(torch.logsumexp(z,1)-torch.logsumexp(z.masked_fill(~labels[:,t],-torch.inf),1)).mean()
            loss=loss/x.shape[1];opt.zero_grad();loss.backward();opt.step()
    return net


@torch.no_grad()
def rollout(d,K,policy,net=None):
    p=initial(d);n=len(p);age=[0]*n;hid=torch.zeros(1,16);order=[];checks=1;extra=0
    for k in range(K,0,-1):
        qs,rs,keys,xs=scan(d,p,k,K,age);checks+=n
        if policy=='sweep':i=(K-k)%n
        elif policy=='residual':i=max(range(n),key=lambda j:(rs[j],-j))
        elif policy=='dependency':i=max(range(n),key=keys.__getitem__)
        elif policy=='lookahead':
            vals=[]
            for j,q in enumerate(qs):
                if k>1:
                    qq=[move(d,q,l) for l in range(n)];assert all(valid(d,z) for z in qq);extra+=n
                    vals.append(min(map(sum,qq)))
                else:vals.append(sum(q))
            i=min(range(n),key=lambda j:(vals[j],-rs[j],j))
        else:
            mask=[r>0 for r in rs] if any(rs) else [True]*n
            z,hid=net.step(torch.tensor([xs]),torch.tensor([mask]),hid);i=int(z.argmax())
        p=qs[i];order.append(i);age=[a+1 for a in age];age[i]=0
    return {'objective':sum(p),'order':order,'candidate_checks':checks+extra,'fixed_point':all(p[i]==h(d,p,i) for i in range(n))}


def run():
    torch.set_num_threads(1);t=time.perf_counter()
    train=[make(f,s,4) for f in TRAIN for s in range(24)]
    batches=[]
    for K in KS:
        rows=[teacher(d,K) for d in train]
        batches.append(tuple(torch.tensor([[r[i] for r in seq] for seq in rows]) for i in range(3)))
    models={}
    for s in SEEDS:
        for recurrent in (False,True):
            models[('recurrent' if recurrent else 'stateless')+f'_{s}']=fit(batches,s,recurrent)
    rows=[]
    for f in FAMILIES:
        for n in (4,5):
            for s in range(1000,1012):
                d=make(f,s,n);p=initial(d);v=oracle(d);gold=sum(least(d));stop=sum(terminal(d))
                for K in KS:
                    opt=v(p,K)
                    arms={k:rollout(d,K,k) for k in ('sweep','residual','dependency','lookahead')}
                    arms.update({k:rollout(d,K,k,net) for k,net in models.items()})
                    assert all(gold<=stop<=opt<=a['objective']<=sum(p) for a in arms.values())
                    assert len({a['candidate_checks'] for k,a in arms.items() if k!='lookahead'})==1
                    rows.append({'family':f,'n':n,'seed':s,'K':K,'initial':sum(p),'least':gold,'terminal':stop,'oracle':opt,'arms':arms})
                v.cache_clear()
    return {'schema':'MIC-04/public-cpu/v1','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'train_roots':len(train),'model_seeds':SEEDS,'parameter_count':sum(p.numel() for p in next(iter(models.values())).parameters()),'epochs':40,'rows':rows,'torch_version':torch.__version__,'elapsed_seconds':time.perf_counter()-t}


if __name__=='__main__': print(json.dumps(run(),sort_keys=True,indent=2))

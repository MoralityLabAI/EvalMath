"""MIC-05 public exact block closure and CPU proposal study."""
from collections import deque
from itertools import product
from random import Random
import json, time, hashlib
from pathlib import Path
import torch
from torch import nn
FAMILIES=('ring','mixed','chord','critical')
SEEDS=(17,29,43)

def root(f,s,n):
    r=Random(s+100003*FAMILIES.index(f)); order=list(range(n));r.shuffle(order)
    m=[[0]*n for _ in order];groups=[order] if f!='mixed' else [order[:n//2],order[n//2:]]
    for g in groups:
        for i,u in enumerate(g):
            m[u][g[(i+1)%len(g)]]=r.randint(3,8) if f in ('ring','mixed') else r.randint(2,5)
            if f in ('chord','critical'):
                m[u][g[(i+2)%len(g)]]=9-sum(m[u]) if f=='critical' else r.randint(1,8-sum(m[u]))
            if f=='mixed' and g is groups[0]:m[u][r.choice(groups[1])]=r.randint(0,9-sum(m[u]))
    return tuple(map(tuple,m)),tuple(r.randint(1,9) for _ in order)

def H(d,p):
    m,b=d;return tuple(y+(sum(a*z for a,z in zip(row,p))+9)//10 for row,y in zip(m,b))

def fixed(d,upper):
    m,b=d;k=max(-(-10*y//(10-sum(row))) for row,y in zip(m,b));p=(k if upper else 0,)*len(b);work=0
    while True:
        q=H(d,p);work+=len(b)
        if q==p:return p,work
        p=q

def slack(d,p):
    m,b=d;return tuple(10*(x-y)-sum(a*z for a,z in zip(row,p)) for x,y,row in zip(p,b,m))

def valid(d,p):return len(p)==len(d[1]) and min(p)>=0 and min(slack(d,p))>=0

def prune(d,p,proposal=None):
    m,b=d;n=len(b);s=slack(d,p);assert valid(d,p)
    active={i for i in (range(n) if proposal is None else proposal) if p[i]>0}
    incoming=[[] for _ in b];outgoing=[[] for _ in b];edges=0
    for i,row in enumerate(m):
        for j,a in enumerate(row):
            if a:incoming[j].append((i,a));outgoing[i].append((j,a));edges+=1
    support={i:sum(a for j,a in outgoing[i] if j in active) for i in active}
    work=edges+sum(len(outgoing[i]) for i in active);checks=len(active)
    q=deque(i for i in sorted(active) if support[i]+s[i]<10)
    while q:
        j=q.popleft()
        if j not in active:continue
        active.remove(j)
        for i,a in incoming[j]:
            work+=1
            if i in active:
                support[i]-=a;checks+=1
                if support[i]+s[i]<10:q.append(i)
    return tuple(sorted(active)),{'edge_work':work,'threshold_checks':checks}

def jump(d,p,S):
    if not S:return p,0
    m,b=d;s=slack(d,p);t=min(min(p[i],s[i]//(10-sum(m[i][j] for j in S))) for i in S)
    assert t>=1
    q=tuple(x-t if i in S else x for i,x in enumerate(p));assert valid(d,q)
    return q,t

def solve(d,p):
    steps=work=0
    while True:
        S,c=prune(d,p);work+=c['edge_work']
        if not S:return p,steps,work
        p,_=jump(d,p,S);steps+=1

def features(d,p):
    m,b=d;s=slack(d,p);n=len(b)
    x=[[s[i]/10,sum(m[i])/10,sum(m[j][i] for j in range(n))/(10*n),p[i]/max(p),b[i]/10,(s[i]+sum(m[i])-10)/10] for i in range(n)]
    return torch.tensor(x,dtype=torch.float32),torch.tensor(m,dtype=torch.float32)/10

class Ranker(nn.Module):
    def __init__(self,graph):
        super().__init__();self.graph=graph;self.embed=nn.Linear(6,16);self.cell=nn.GRUCell(16,16);self.head=nn.Linear(16,1)
    def forward(self,x,m):
        h=torch.tanh(self.embed(x))
        for _ in range(3):
            msg=m@h if self.graph else h
            h=self.cell(msg.reshape(-1,16),h.reshape(-1,16)).reshape_as(h)
        return self.head(h).squeeze(-1)

def data():
    out=[]
    for f in ('ring','mixed'):
        for seed in range(96):
            d=root(f,seed,6);p,_=fixed(d,True);S,_=prune(d,p);x,m=features(d,p)
            out.append((x,m,torch.tensor([float(i in S) for i in range(6)])))
    return tuple(torch.stack(z) for z in zip(*out))

def fit(ds,seed,graph):
    torch.manual_seed(seed);net=Ranker(graph);opt=torch.optim.Adam(net.parameters(),lr=.01);x,m,y=ds
    for _ in range(120):
        loss=nn.functional.binary_cross_entropy_with_logits(net(x,m),y);opt.zero_grad();loss.backward();opt.step()
    return net

def best_jump(d,p):
    m,b=d;s=slack(d,p);best=0
    for bits in product((False,True),repeat=len(p)):
        B=[i for i,v in enumerate(bits) if v]
        if B:best=max(best,len(B)*min(min(p[i],s[i]//(10-sum(m[i][j] for j in B))) for i in B))
    return best

def evaluate():
    torch.set_num_threads(1);t=time.perf_counter();ds=data()
    models={(name,s):fit(ds,s,g) for s in SEEDS for name,g in [('self',False),('graph',True)]};rows=[]
    for f in FAMILIES:
        for n in (6,8):
            for seed in range(1000,1016):
                d=root(f,seed,n);p,_=fixed(d,True);gold,ow=fixed(d,False);S,c=prune(d,p)
                solved,steps,work=solve(d,p);assert solved==gold and bool(S)==(p!=gold)
                q,j=jump(d,p,S);x,m=features(d,p);arms={}
                for (name,ms),net in models.items():
                    with torch.no_grad():pred=tuple(i for i,z in enumerate(net(x,m)) if z>=0)
                    raw=tuple(v-int(i in pred) for i,v in enumerate(p));B,cost=prune(d,p,pred);new,_=jump(d,p,B)
                    arms[f'{name}_{ms}']={'pred':pred,'raw_valid':valid(d,raw),'exact_mask':pred==S,'block':B,'reduction':sum(p)-sum(new),**cost}
                rows.append({'family':f,'n':n,'seed':seed,'initial':sum(p),'least':sum(gold),'block':S,'structural_reduction':sum(p)-sum(q),'best_uniform_jump':best_jump(d,p),'jump':j,'structural_work':c,'solve_steps':steps,'solve_edge_work':work,'least_row_evals':ow,'arms':arms})
    return {'schema':'MIC-05/public-cpu/v1','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'training_roots':len(ds[0]),'positive_train_roots':int(ds[2].any(1).sum()),'parameter_count':sum(p.numel() for p in next(iter(models.values())).parameters()),'model_seeds':SEEDS,'rows':rows,'elapsed_seconds':time.perf_counter()-t,'torch_version':torch.__version__,'evidence':'public synthetic development only; no sealed confirmation'}

if __name__=='__main__':print(json.dumps(evaluate(),sort_keys=True,indent=2))

"""MIC-08: learned child ordering in bounded certified search."""
from core import Root, FAMILIES, SEEDS, exact_table, valid, closure
from random import Random
from time import perf_counter
from pathlib import Path
import hashlib, heapq, json, math
import torch
from torch import nn
SIZES=(32,64,128)
TRAIN_SEEDS=range(48)
DEV_SEEDS=range(3000,3004)
CAP=512

def root(f,s,n):
    r=Random(s+100003*FAMILIES.index(f)+10000019*n)
    w=tuple(r.randint(1,20) for _ in range(n))
    prob=min(.40,(9 if f=='mixed' else 6)/(n-1))
    edges=tuple((i,j) for i in range(n) for j in range(i+1,n) if r.random()<prob) or ((0,1),)
    sup=[]
    if f!='conflict':
        for i in range(n):
            if r.random()<.65:
                k=1 if f=='implication' else 2 if f=='disjunction' else r.choice((1,2,3))
                sup.append((i,sum(1<<j for j in r.sample([j for j in range(n) if i!=j],k))))
            if f=='mixed' and r.random()<.25:
                sup.append((i,sum(1<<j for j in r.sample([j for j in range(n) if i!=j],2))))
    return Root(w,edges,tuple(sup))

def bits(s):
    while s:
        low=s&-s;yield low.bit_length()-1;s^=low

class Engine:
    def __init__(self,d):
        self.d=d;self.n=len(d.w);self.full=(1<<self.n)-1
        self.adj=[0]*self.n
        for i,j in d.edges:self.adj[i]|=1<<j;self.adj[j]|=1<<i
        self.order=sorted(range(self.n),key=lambda i:(-d.w[i],-self.adj[i].bit_count(),i))
        self.total=sum(d.w);self.calls=0;self.bound_calls=0;self.support_checks=0
    def value(self,s):return sum(self.d.w[i] for i in bits(s))
    def close(self,s):
        self.calls+=1;q,c=closure(self.d,s);self.support_checks+=c;return q
    def degrees(self,s):return {i:(self.adj[i]&s).bit_count() for i in bits(s)}
    def edge(self,s,deg):
        u=max(deg,key=lambda i:(deg[i],self.d.w[i],-i),default=-1)
        if u<0 or not deg[u]:return None
        return u,max(bits(self.adj[u]&s),key=lambda i:(deg[i],self.d.w[i],-i))
    def upper(self,s):
        self.bound_calls+=1
        def cover(order):
            groups=[];total=0
            for i in order:
                if not s>>i&1:continue
                for j,(g,w) in enumerate(groups):
                    if g&self.adj[i]==g:
                        nw=max(w,self.d.w[i]);total+=nw-w;groups[j]=(g|1<<i,nw);break
                else:groups.append((1<<i,self.d.w[i]));total+=self.d.w[i]
            return total
        order2=sorted(bits(s),key=lambda i:(-(self.adj[i]&s).bit_count(),-self.d.w[i],i))
        return min(cover(self.order),cover(order2))
    def initializer(self,s):
        while True:
            deg=self.degrees(s);edge=self.edge(s,deg)
            if edge is None:return s
            i=min(edge,key=lambda i:(self.d.w[i]/(1+deg[i]),-i))
            s=self.close(s&~(1<<i))
    def features(self,s,q,ub,removed,deg):
        n=self.n;size=s.bit_count();qsize=q.bit_count()
        c=sum((self.adj[i]&q).bit_count() for i in bits(q))//2;before=sum(deg.values())//2
        return (self.d.w[removed]/20,deg[removed]/max(1,size-1),qsize/n,
                (size-qsize)/max(1,size),self.value(q)/self.total,
                (self.value(s)-self.value(q))/self.total,ub/self.total,
                c/max(1,qsize*(qsize-1)/2),(before-c)/max(1,before),
                sum(1 for i,a in self.d.sup if q>>i&1 and q&a)/n)

class Ranker(nn.Module):
    def __init__(self):
        super().__init__();self.net=nn.Sequential(nn.Linear(10,32),nn.Tanh(),nn.Linear(32,16),nn.Tanh(),nn.Linear(16,1))
    def forward(self,x):return self.net(x).squeeze(-1)

def teacher(d):
    e=Engine(d);tab=exact_table(d);s=e.close(e.full);rows=[]
    while True:
        deg=e.degrees(s);edge=e.edge(s,deg)
        if edge is None:break
        qs=[e.close(s&~(1<<i)) for i in edge];bs=[e.upper(q) for q in qs]
        x=[e.features(s,q,b,i,deg) for q,b,i in zip(qs,bs,edge)]
        v=[int(tab[q]) for q in qs];y=float(v[0]>v[1])+.5*float(v[0]==v[1]);rows.append((x,y))
        assert max(v)==int(tab[s]);s=qs[0 if v[0]>=v[1] else 1]
    assert valid(d,s) and e.value(s)==int(tab[-1]);return rows

def fit(rows,seed):
    torch.manual_seed(seed);net=Ranker();opt=torch.optim.Adam(net.parameters(),lr=.008)
    x=torch.tensor([r[0] for r in rows]);y=torch.tensor([r[1] for r in rows])
    for _ in range(120):
        z=net(x);loss=nn.functional.binary_cross_entropy_with_logits(z[:,0]-z[:,1],y)
        opt.zero_grad();loss.backward();opt.step()
    return net

@torch.no_grad()
def search(d,policy,net=None,cap=CAP,seconds=None):
    t=perf_counter();deadline=t+seconds if seconds is not None else math.inf
    e=Engine(d);s=e.close(e.full);best=e.initializer(s);assert valid(d,best)
    start=e.value(best);init_calls=e.calls;bestval=start
    front=[(-e.upper(s),s)];seen={s};steps=0;model_calls=0
    while front:
        if e.calls-init_calls+2>cap or perf_counter()>=deadline:break
        neg,s=heapq.heappop(front) if policy=='best_first' else front.pop()
        if -neg<=bestval:continue
        deg=e.degrees(s);edge=e.edge(s,deg)
        if edge is None:
            v=e.value(s)
            if v>bestval:best,bestval=s,v
            continue
        steps+=1;children=[]
        for i in edge:
            q=e.close(s&~(1<<i))
            if q in seen:continue
            seen.add(q);qdeg=e.degrees(q);v=e.value(q)
            if not any(qdeg.values()):
                assert valid(d,q)
                if v>bestval:best,bestval=q,v
                continue
            b=e.upper(q)
            if b>bestval:children.append((b,q,v,i,sum(qdeg.values())//2))
        if policy=='best_first':
            for b,q,_,_,_ in children:heapq.heappush(front,(-b,q))
        else:
            if policy=='learned' and len(children)==2:
                x=[e.features(s,q,b,i,deg) for b,q,_,i,_ in children]
                z=net(torch.tensor(x)).tolist();model_calls+=1
                children=[x for _,x in sorted(zip(z,children),key=lambda v:(v[0],v[1][0],v[1][2],-v[1][1]))]
            elif policy=='loss':children.sort(key=lambda x:(x[2]/(1+x[4]),x[0],x[2],-x[1]))
            else:children.sort(key=lambda x:(x[0],x[2],-x[4],-x[1]))
            front.extend((-b,q) for b,q,_,_,_ in children)
    upper=max([bestval]+[-u for u,_ in front]);assert valid(d,best)
    return dict(value=bestval,mask=hex(best),upper=upper,certified=upper==bestval,init_value=start,
                init_calls=init_calls,closure_calls=e.calls-init_calls,bound_calls=e.bound_calls,
                support_checks=e.support_checks,expansions=steps,model_calls=model_calls,ms=(perf_counter()-t)*1000)

def run():
    torch.set_num_threads(1);t=perf_counter();training=[]
    for f in ('conflict','mixed'):
        for s in TRAIN_SEEDS:training.extend(teacher(root(f,s,12)))
    nets={s:fit(training,s) for s in SEEDS};rows=[]
    for n in SIZES:
        for f in FAMILIES:
            for s in DEV_SEEDS:
                d=root(f,s,n);arms={k:search(d,k) for k in ('bound','loss','best_first')}
                arms.update({f'learned_{m}':search(d,'learned',net) for m,net in nets.items()})
                target=sum(arms[f'learned_{m}']['ms'] for m in SEEDS)/len(SEEDS)
                arms['timed_bound']=search(d,'bound',cap=8192,seconds=target/1000)
                arms['timed_best_first']=search(d,'best_first',cap=8192,seconds=target/1000)
                lo=max(a['value'] for a in arms.values());hi=min(a['upper'] for a in arms.values());assert lo<=hi
                for a in arms.values():
                    assert valid(d,int(a['mask'],16)) and a['value']<=hi and lo<=a['upper']
                rows.append(dict(n=n,family=f,seed=s,arms=arms,pooled_lower=lo,pooled_upper=hi,learned_time_ms=target))
            print('done',n,f,flush=True,file=__import__('sys').stderr)
    return dict(schema='MIC-08/public-cpu/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                core_sha256=hashlib.sha256(Path(__file__).with_name('core.py').read_bytes()).hexdigest(),
                train_roots=2*len(TRAIN_SEEDS),teacher_rows=len(training),parameters=sum(p.numel() for p in next(iter(nets.values())).parameters()),
                seeds=SEEDS,cap=CAP,rows=rows,elapsed_s=perf_counter()-t,torch=torch.__version__)

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))

"""CFH-03: CPU public development; no independent-conjecture inference.
Run alongside ../CFH02/discovery.py with NumPy, Torch, NetworkX, sklearn, SymPy.
"""
from pathlib import Path
import sys, random, json, math, hashlib
from collections import Counter
from statistics import mean
import networkx as nx
import numpy as np
import torch
from torch import nn
from sklearn.linear_model import LogisticRegression
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'CFH02'))
from discovery import INVARIANTS, coeff, cheap_certificate, exact_nonreal
TRAIN=('er','tree','bipartite','blocks')
SHIFT=('attachment','smallworld','split','geometric')
SEEDS=(11,29,47)
BUDGETS=((2,1),(3,1),(3,2),(6,1),(6,2))
SPLITS=(('train',TRAIN,240,7001),('dev',TRAIN,72,7002),('shift',SHIFT,192,7003))


def build(f,n,r):
    seed=r.randrange(2**31)
    if f=='er':return nx.gnp_random_graph(n,r.uniform(.15,.85),seed=seed)
    if f=='tree':return nx.from_prufer_sequence([r.randrange(n) for _ in range(n-2)])
    if f=='bipartite':
        k=r.randrange(2,n-1);return nx.bipartite.random_graph(k,n-k,r.uniform(.25,.85),seed=seed)
    if f=='blocks':
        k=r.randrange(2,n-1);return nx.stochastic_block_model([k,n-k],[[r.uniform(.4,.9),.15],[.15,r.uniform(.4,.9)]],seed=seed)
    if f=='attachment':return nx.barabasi_albert_graph(n,r.randrange(1,4),seed=seed)
    if f=='smallworld':return nx.watts_strogatz_graph(n,r.choice((2,4,6)),r.uniform(.15,.9),seed=seed)
    if f=='split':
        k=r.randrange(2,n-1);g=nx.complete_graph(k);g.add_nodes_from(range(n));p=r.uniform(.15,.85)
        g.add_edges_from((i,j) for i in range(k) for j in range(k,n) if r.random()<p);return g
    if f=='geometric':return nx.random_geometric_graph(n,r.uniform(.2,.65),seed=seed)
    raise ValueError(f)


def gf(g,inv):
    n=len(g);d=np.array([v for _,v in g.degree()]);z=d/(n-1);cc=list(nx.connected_components(g));tri=sum(nx.triangles(g).values())/3
    return [n/12,nx.density(g),z.max(),z.min(),z.std(),np.mean(z*z),np.mean(d==0),np.mean(d==1),len(cc)/n,max(map(len,cc))/n,tri/math.comb(n,3),nx.transitivity(g),nx.average_clustering(g),float(nx.is_bipartite(g)),float(nx.is_chordal(g))]+[float(inv==k) for k in INVARIANTS]


def pf(a):
    a=np.asarray(a,dtype=float);nz=np.flatnonzero(a);d=len(a)-1
    pad=np.zeros(12);pad[:len(a)]=np.sign(a)*np.log1p(abs(a));m=[]
    for k in range(int(nz[0])+1,d):
        l=a[k]**2*(k-nz[0])*(d-k);r=abs(a[k-1]*a[k+1])*(k-nz[0]+1)*(d-k+1)
        m.append(math.log1p(l)-math.log1p(r))
    return list(pad)+[d/12,nz[0]/12,len(nz)/12,min(m) if m else 0.,mean(m) if m else 0.]


def dataset():
    seen=set();sets={};info={}
    for name,families,count,seed in SPLITS:
        rng=random.Random(seed);groups=[];fam=Counter();attempt=0
        while len(groups)<count:
            f=families[len(groups)%len(families)];n=rng.randrange(8,11);attempt+=1
            if attempt>100*count:raise RuntimeError('too many duplicate graphs')
            g=build(f,n,rng);wl=nx.weisfeiler_lehman_graph_hash(g,iterations=4);key=(n,wl)
            if key in seen:continue
            seen.add(key);fam[f]+=1;edges=tuple(sorted(tuple(sorted(e)) for e in g.edges()));d=[v for _,v in g.degree()];group=[]
            for inv in INVARIANTS:
                a=coeff((n,edges),inv);y=int(exact_nonreal(a));c=cheap_certificate(a)
                if c is not None:assert c[0]==y
                ds=[n-1-v for v in d] if inv=='clique' else d
                group.append(dict(root=wl,n=n,family=f,inv=inv,g=gf(g,inv),p=pf(a),y=y,cheap=None if c is None else int(c[0]),rank=(max(d),sum(v*(v-1) for v in d),len(edges)),route_rank=(max(ds),sum(v*(v-1) for v in ds),sum(ds)),edges=edges))
            groups.append(group)
        rng.shuffle(groups);rows=[r for group in groups for r in group];sets[name]=rows
        info[name]=dict(graphs=count,decks=count//6,families=dict(fam),attempts=attempt,witnesses=sum(r['y'] for r in rows),unresolved=sum(r['cheap'] is None for r in rows))
        print(name,info[name],file=sys.stderr,flush=True)
    return sets,info


def arr(rows):
    return (np.array([r['g'] for r in rows],np.float32),np.array([r['p'] for r in rows],np.float32),np.array([r['y'] for r in rows],np.float32),np.array([r['cheap'] is None for r in rows],bool))


class Router(nn.Module):
    def __init__(self,gdim,pdim,loop,width=32):
        super().__init__();self.loop=loop;self.inp=nn.Linear(gdim+pdim+1,width);self.mix=nn.Linear(width,width,bias=False);self.out=nn.Linear(width,1)
    def forward(self,g,p):
        o=torch.zeros_like(g[:,:1]);h=torch.tanh(self.inp(torch.cat((g,torch.zeros_like(p),o),1)));a=self.out(h).squeeze(1)
        u=torch.tanh(self.inp(torch.cat((g,p,1+o),1)));v=torch.tanh(u+self.mix(h if self.loop else u))
        return a,self.out(v).squeeze(1)


def fit(rows,loop,seed):
    torch.manual_seed(seed);g,p,y,u=arr(rows);gm,gs=g.mean(0),np.maximum(g.std(0),1e-4);pm,ps=p.mean(0),np.maximum(p.std(0),1e-4)
    gt,pt,yt,ut=map(torch.tensor,((g-gm)/gs,(p-pm)/ps,y,u));model=Router(g.shape[1],p.shape[1],loop);opt=torch.optim.AdamW(model.parameters(),lr=.003,weight_decay=.01)
    for _ in range(180):
        a,b=model(gt,pt);loss=nn.functional.binary_cross_entropy_with_logits(a,yt)+nn.functional.binary_cross_entropy_with_logits(b[ut],yt[ut]);opt.zero_grad();loss.backward();opt.step()
    def predict(rr):
        g,p,_,_=arr(rr)
        with torch.no_grad():a,b=model(torch.tensor((g-gm)/gs),torch.tensor((p-pm)/ps))
        return a.numpy(),b.numpy()
    return predict,sum(v.numel() for v in model.parameters())


def fit_logistic(rows):
    g,p,y,u=arr(rows);gm,gs=g.mean(0),np.maximum(g.std(0),1e-4);pm,ps=p.mean(0),np.maximum(p.std(0),1e-4);g=(g-gm)/gs;p=(p-pm)/ps
    a=LogisticRegression(C=1,max_iter=500).fit(g,y);b=LogisticRegression(C=1,max_iter=500).fit(np.c_[g,p][u],y[u])
    def predict(rr):
        g,p,_,_=arr(rr);g=(g-gm)/gs;p=(p-pm)/ps;return a.decision_function(g),b.decision_function(np.c_[g,p])
    return predict


def run_deck(rows,order,post,cmax,smax):
    pending=[];cq=sq=resolved=0
    for i in order[:cmax]:
        r=rows[i];cq+=1;v=r['cheap']
        if v==1:return 'witness',cq,sq
        if v==0:resolved+=1
        else:pending.append(i)
    if post is not None:pending.sort(key=lambda i:post[i],reverse=True)
    for i in pending[:smax]:
        sq+=1;resolved+=1
        if rows[i]['y']:return 'witness',cq,sq
    return ('absence' if resolved==len(rows) else 'abstain'),cq,sq


def evaluate(rows,predictions,split):
    results=[];ni=len(INVARIANTS)
    for deck,off in enumerate(range(0,len(rows),6*ni)):
        for j,inv in enumerate(INVARIANTS):
            idx=[off+j+i*ni for i in range(6)];d=[rows[i] for i in idx];has=any(r['y'] for r in d);assert all(r['inv']==inv for r in d)
            policies={'uniform':(list(range(6)),None),'degree':(sorted(range(6),key=lambda i:d[i]['rank'],reverse=True),None),'invariant_degree':(sorted(range(6),key=lambda i:d[i]['route_rank'],reverse=True),None)}
            for name,(prior,post) in predictions.items():
                order=sorted(range(6),key=lambda i:prior[idx[i]],reverse=True);policies[name]=(order,[post[i] for i in idx])
                if name.startswith('loop'):policies[name+'_prior_only']=(order,None)
            for c,s in BUDGETS:
                for name,(order,post) in policies.items():
                    out,cq,sq=run_deck(d,order,post,c,s);assert cq<=c and sq<=s;assert out=='abstain' or (out=='witness')==has
                    results.append(dict(split=split,deck=deck,inv=inv,policy=name,C=c,S=s,has=has,out=out,cq=cq,sq=sq))
    return results


def main():
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True);sets,info=dataset();train=sets['train'];models={'logistic':fit_logistic(train)};params={}
    for seed in SEEDS:
        for name,loop in (('static',False),('loop',True)):
            tag=f'{name}_{seed}';models[tag],params[tag]=fit(train,loop,seed)
    allrows=[]
    for split in ('dev','shift'):
        rows=sets[split];allrows.extend(evaluate(rows,{name:m(rows) for name,m in models.items()},split))
    summary=[]
    for split in ('dev','shift'):
        for c,s in BUDGETS:
            for name in sorted({r['policy'] for r in allrows}):
                rr=[r for r in allrows if (r['split'],r['C'],r['S'],r['policy'])==(split,c,s,name)]
                summary.append(dict(split=split,C=c,S=s,policy=name,tasks=len(rr),available=sum(r['has'] for r in rr),hits=sum(r['out']=='witness' for r in rr),absence=sum(r['out']=='absence' for r in rr),mean_c=mean(r['cq'] for r in rr),mean_s=mean(r['sq'] for r in rr)))
    return dict(evidence='public graph-generator shift pilot; no independent conjecture or causal claims',dataset=info,params=params,summary=summary,records=allrows,roots={k:[{'root':r['root'],'n':r['n'],'family':r['family'],'edges':r['edges']} for r in v[::len(INVARIANTS)]] for k,v in sets.items()},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

if __name__=='__main__':print(json.dumps(main(),indent=2))

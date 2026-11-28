"""CFH-05: compositional route identification; public finite development."""
from functools import cache
from itertools import product, combinations
from math import comb, log2, prod
import json, random, sys, time
from pathlib import Path
import numpy as np
import networkx as nx
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent/'CFH04'))
sys.path.insert(0, str(here.parent/'cfh04_dev'))
from hidden_invariant import coefficients, direct_coefficients, INVARIANTS, partition, graph_tuple


def routes(depth):
    # Complement parity, commuting left/right deletion, commuting D and translation.
    # Complement swaps independence/clique: retain uncomplemented representative.
    return tuple((l,r,c,i,d,s) for l,r,c,d,s in product(range(depth+1),range(depth+1),range(2),range(depth+1),range(depth+1))
                 if l+r+c+d+s<=depth for i in INVARIANTS
                 if not(c and i in ('clique','independence')))


@cache
def predict(g,route):
    l,r,c,i,d,s=route; n,edges=g; m=n-l-r
    assert m>=1
    e={(a-l,b-l) for a,b in edges if l<=a<b<n-r}
    if c:e=set(combinations(range(m),2))-e
    p=coefficients((m,tuple(sorted(e))),i)
    q=[0]*(n+1)
    for k in range(d,len(p)):
        for j in range(k-d+1):
            q[j]+=p[k]*prod(range(k-d+1,k+1))*comb(k-d,j)*s**(k-d-j)
    return tuple(q)


def make_deck(group,seed):
    rng=random.Random(seed); cards=[]
    for j in range(3):
        n=rng.randrange(7,9); rs=rng.randrange(2**31)
        if group=='train':
            g=(nx.gnp_random_graph(n,rng.uniform(.15,.85),seed=rs),nx.from_prufer_sequence([rng.randrange(n) for _ in range(n-2)]),nx.complete_bipartite_graph(n//2,n-n//2))[j]
        elif group=='shift':
            g=(nx.watts_strogatz_graph(n,4,rng.uniform(.1,.9),seed=rs),nx.barabasi_albert_graph(n,2,seed=rs),nx.random_geometric_graph(n,.48,seed=rs))[j]
        else:g=(nx.path_graph(n),nx.cycle_graph(n),nx.complete_graph(n))[j]
        labels=list(range(n));rng.shuffle(labels)
        cards.append(graph_tuple(nx.relabel_nodes(g,dict(enumerate(labels)))))
    return tuple(cards)


def table(cards,depth):
    rr=routes(depth); n=len(rr); pred=[[predict(g,r) for r in rr] for g in cards]
    parts={}
    for h,(g,ps) in enumerate(zip(cards,pred)):
        for k in range(g[0]+1):
            for mod in (2,3,5):
                p=partition(tuple(a[k]%mod for a in ps))
                if len(p)>1:parts.setdefault(p,(h,k,mod))
    full=partition(tuple(tuple(ps[i][k]%mod for g,ps in zip(cards,pred) for k in range(g[0]+1) for mod in (2,3,5)) for i in range(n)))
    exact=partition(tuple(tuple(ps[i] for ps in pred) for i in range(n)))
    mask=sum(p for p in full if p.bit_count()==1)
    return rr,tuple(parts),mask,sum(p.bit_count()==1 for p in exact)


def features(sub,n):
    z=[x.bit_count() for x in sub]; p=[v/n for v in z]
    return [1.,sum(v==1 for v in z)/n,-sum(v*log2(v) for v in p)/log2(n),1-max(p),1-sum(v*v for v in p),len(z)/5,1/log2(n),sum(v==2 for v in z)*2/n]


class Planner:
    def __init__(self,parts,mask,mode,beam,w=None):
        self.parts=parts;self.mask=mask;self.mode=mode;self.beam=beam;self.w=w
        self.states=self.scores=self.intersections=self.expansions=0
        self.memo={};self.sm={};self.choice={}
    def splits(self,s):
        if s in self.sm:return self.sm[s]
        self.states+=1;found={}
        for p in self.parts:
            self.scores+=1;self.intersections+=len(p)
            sub=tuple(sorted(y for x in p if (y:=x&s)))
            if len(sub)>1:found.setdefault(sub,p)
        self.sm[s]=tuple(found);return self.sm[s]
    def score(self,sub,n,b):
        f=features(sub,n)
        w=self.w[b] if self.mode=='horizon' else self.w
        return sum(a*c for a,c in zip(f,w)) if self.mode in ('learned','horizon') else f[2]
    def upper(self,s,b):return min((s&self.mask).bit_count(),5**b)
    def solve(self,s,b):
        n=s.bit_count()
        if n==1:return 1
        if not b or not self.upper(s,b):return 0
        key=(s,b)
        if key in self.memo:return self.memo[key]
        subs=self.splits(s)
        if not subs:return 0
        if b>1:
            subs=sorted(subs,key=lambda a:self.score(a,n,b),reverse=True)
            if self.mode!='exact':subs=subs[:self.beam]
        val=-1;best=None
        for a in subs:
            if sum(self.upper(c,b-1) for c in a)<=val:continue
            self.expansions+=1
            v=sum(c.bit_count()==1 for c in a) if b==1 else sum(self.solve(c,b-1) for c in a)
            if v>val:val,best=v,a
            if val==self.upper(s,b):break
        assert best is not None
        self.choice[key]=best;self.memo[key]=val;return val
    def replay(self,s,b):
        hits=0;calls=0
        for i in range(s.bit_count()):
            state=s;left=b
            while left and (state,left) in self.choice:
                state=next(c for c in self.choice[(state,left)] if c&(1<<i));left-=1;calls+=1
            assert state&(1<<i)
            hits+=state.bit_count()==1
        return hits,calls


def train():
    X=[];y=[];work=0
    for k in range(8):
        cards=make_deck('train',5000+k);rr,parts,mask,_=table(cards,2);p=Planner(parts,mask,'exact',0);full=(1<<len(rr))-1
        for a in p.splits(full):
            X.append(features(a,len(rr)));y.append(sum(p.solve(c,1) for c in a)/len(rr))
        work+=p.scores
    X=np.array(X);y=np.array(y);w=np.linalg.solve(X.T@X+.01*np.eye(X.shape[1]),X.T@y)
    return w.tolist(),len(y),work


def train_horizon():
    # Exploratory redesign: fit separate b=2 and b=3 scores using TRAIN decks only.
    X={2:[],3:[]};y={2:[],3:[]};work=0
    for k in range(8):
        for depth in (1,2):
            cards=make_deck('train',5000+k);rr,parts,mask,_=table(cards,depth)
            p=Planner(parts,mask,'exact',0);full=(1<<len(rr))-1
            root=p.splits(full)
            children=sorted({c for a in root for c in a if c.bit_count()>1})
            random.Random(16000+10*k+depth).shuffle(children)
            for b in (2,3):
                for state in ([full]+children[:12] if b==2 else [full]):
                    n=state.bit_count()
                    for a in p.splits(state):
                        X[b].append(features(a,n));y[b].append(sum(p.solve(c,b-1) for c in a)/n)
            work+=p.scores
    weights={}
    for b in (2,3):
        a=np.array(X[b]);v=np.array(y[b]);weights[b]=np.linalg.solve(a.T@a+.01*np.eye(a.shape[1]),a.T@v).tolist()
    return weights,{b:len(y[b]) for b in (2,3)},work


def audit_compositions():
    # A separate direct graph enumeration and symbolic polynomial operator route.
    import sympy as sp
    x=sp.Symbol('x');checks=0;cache_base={}
    for group,seed in (('train',5000),('shift',8000),('structured',8100)):
        for g in make_deck(group,seed):
            n,edges=g;G=nx.Graph();G.add_nodes_from(range(n));G.add_edges_from(edges)
            for route in routes(3):
                l,r,c,i,d,s=route
                H=G.subgraph(range(l,n-r)).copy()
                if c:H=nx.complement(H)
                H=nx.relabel_nodes(H,{a:a-l for a in H.nodes()});h=graph_tuple(H)
                if h not in cache_base:cache_base[h]=direct_coefficients(h)
                a=cache_base[h][i];p=sp.Poly.from_list(list(reversed(a)),x,domain=sp.ZZ)
                for _ in range(d):p=p.diff()
                p=p.shift(s);v=tuple(int(p.nth(j)) for j in range(n+1))
                assert v==predict(g,route)
                checks+=1
    return dict(composition_checks=checks,base_graphs=len(cache_base))


def run():
    w,train_n,train_work=train();wh,hn,hw=train_horizon();rows=[];decks=[];audit=audit_compositions()
    for group,num in (('shift',8),('structured',4)):
        for k in range(num):
            cards=make_deck(group,8000+k+(100 if group=='structured' else 0));decks.append(dict(group=group,deck=k,cards=cards))
            for depth in (1,2,3):
                rr,parts,mask,exactceil=table(cards,depth);s=(1<<len(rr))-1;ceil=mask.bit_count()
                for b in (2,3):
                    arms=[('greedy',1),('entropy',4),('learned',4),('horizon',4),('exact',0)]
                    for mode,beam in arms:
                        t=time.perf_counter();p=Planner(parts,mask,mode,beam,wh if mode=='horizon' else w);hits=p.solve(s,b);dt=time.perf_counter()-t
                        h,calls=p.replay(s,b);assert h==hits<=ceil
                        rows.append(dict(group=group,deck=k,depth=depth,classes=len(rr),actions=len(parts),budget=b,mode=mode,beam=beam,hits=hits,ceiling=ceil,full_vector_ceiling=exactceil,calls=calls,states=p.states,scores=p.scores,intersections=p.intersections,expansions=p.expansions,seconds=dt,setup_predictions=len(cards)*len(rr)))
                print(group,k,depth,len(rr),len(parts),flush=True,file=sys.stderr)
    summary=[]
    for depth,b,mode in product((1,2,3),(2,3),('greedy','entropy','learned','horizon','exact')):
        a=[r for r in rows if (r['depth'],r['budget'],r['mode'])==(depth,b,mode)]
        if not a:continue
        summary.append(dict(depth=depth,budget=b,mode=mode,decks=len(a),tasks=sum(r['classes'] for r in a),hits=sum(r['hits'] for r in a),ceiling=sum(r['ceiling'] for r in a),full_vector_ceiling=sum(r['full_vector_ceiling'] for r in a),scores=sum(r['scores'] for r in a),intersections=sum(r['intersections'] for r in a),seconds=sum(r['seconds'] for r in a)))
    for r in rows:
        opt=next((x for x in rows if x['mode']=='exact' and all(x[k]==r[k] for k in ('group','deck','depth','budget'))),None)
        if opt:assert r['hits']<=opt['hits']
    rr=routes(3);signatures=[tuple(predict(tuple([g[0],tuple(g[1])]),r) for deck in decks for g in deck['cards']) for r in rr]
    return dict(evidence='public finite hypothesis library, descriptive learned planning pilot',weights=w,train_examples=train_n,train_action_scores=train_work,horizon_weights=wh,horizon_examples=hn,horizon_train_action_scores=hw,audit=audit,distinct_exact_route_signatures=len(set(signatures)),grammar_sizes={d:len(routes(d)) for d in range(4)},decks=decks,summary=summary,rows=rows)

if __name__=='__main__': print(json.dumps(run(),indent=2))

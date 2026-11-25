"""MIT-03 open development comparison. NumPy training, exact policy evaluation."""
import argparse,json,hashlib,time
from pathlib import Path
from functools import lru_cache
from fractions import Fraction
from random import Random
import numpy as np
from selector import Search,world

class Env(Search):
    def __init__(self,spec):
        super().__init__(spec)
        self.mass=lru_cache(None)(self.mass); self.top=lru_cache(None)(self.top)
        self.depth=lru_cache(None)(self._depth)
    def _depth(self,s,a,b,d):
        if not s or b<=0:return 0
        best=self.top(s,b)
        if d:
            for act in self.actions(s,a,b):
                hit,ch=self.children((s,a,b),act)
                best=max(best,hit+sum(self.depth(*x,d-1) for x in ch))
        return best
    def qdepth(self,st,act,d):
        hit,ch=self.children(st,act)
        return hit+sum(self.depth(*x,d-1) for x in ch)
    def rel(self,st,act,sham=False):
        s,a,b=st;mass=self.mass(s);hit,ch=self.children(st,act)
        qs=[];profiles=[];branch=[]
        bits=[i for i in range(len(self.w)) if s>>i&1]
        def rotated(m,j):
            out=0
            for w in set(self.w[i] for i in bits):
                ids=[i for i in bits if self.w[i]==w];k=(j+1)%len(ids)
                for i,ii in enumerate(ids):
                    if m>>ii&1:out|=1<<ids[(i+k)%len(ids)]
            return out
        for sub,avail,rem in ch:
            one=self.top(sub,rem);gains=[]
            for j,c in enumerate(self.costs):
                if not avail>>j&1 or c>=rem:continue
                m=rotated(self.masks[j],j) if sham else self.masks[j]
                p,q=sub&m,sub&~m;v=self.top(p,rem-c)+self.top(q,rem-c)
                gains.append(max(0,v-one)/mass);qs.append(min(self.mass(p),self.mass(q))/mass)
            branch.append(max(gains,default=0.0));profiles.extend(gains)
        branch=sorted(branch,reverse=True)+[0,0]
        return [branch[0],branch[1],sum(branch),max(profiles,default=0),sum(profiles)/max(1,len(profiles)),max(qs,default=0),sum(qs)/max(1,len(qs)),len(profiles)/12]
    def feat(self,st,act,mode):
        f=self.features(st,act)
        return f if mode=='scalar' else f+self.rel(st,act,mode=='sham')

def make(seed,family):
    if family in ('stress','random','tree','overlap'):return world(seed,family)
    r=Random(seed);n=14 if family=='large' else 12;ids=list(range(n));r.shuffle(ids)
    w=tuple(r.randint(1,3) for _ in ids)
    if family=='large':
        m=[sum(1<<i for i in r.sample(ids,r.randint(3,n-3))) for _ in range(5)];c=tuple(r.choice((1,1,2)) for _ in m);b=5
    elif family=='partition':
        m=[sum(1<<i for i in ids[a:b]) for a,b in ((0,6),(0,3),(3,6),(6,9),(9,12))];c=(1,)*len(m);b=5
    elif family=='perturbed_overlap':
        m=[sum(1<<i for i in ids[a:b]) for a,b in ((0,6),(2,8),(4,10),(6,12))];c=(1,)*len(m);b=4;m=[v^(1<<r.choice(ids)) for v in m]
    else:raise ValueError(family)
    p=list(zip(m,c));r.shuffle(p);m,c=zip(*p);return w,m,c,b

def dataset(specs):
    x={k:[] for k in ('scalar','rel','sham')};y=[];counts=[]
    for spec in specs:
        e=Env(spec);states=0;labels=0
        for st,acts in e.states():
            if not any(a[0]=='q' for a in acts):continue
            mass=e.mass(st[0]);states+=1
            for a in acts:
                f=e.features(st,a);x['scalar'].append(f);x['rel'].append(f+e.rel(st,a));x['sham'].append(f+e.rel(st,a,True));y.append((e.q(st,a)-e.immediate(st,a))/mass);labels+=1
        counts.append((states,labels));e.value.cache_clear();e.mass.cache_clear();e.top.cache_clear();e.depth.cache_clear()
    return {k:np.array(v) for k,v in x.items()},np.array(y)[:,None],counts

def fit(x,y,seed,width):
    rng=np.random.default_rng(seed);W=rng.normal(0,.18,(x.shape[1],width));b=np.zeros(width);V=rng.normal(0,.1,(width,1));c=np.zeros(1);params=[W,b,V,c];m=[np.zeros_like(p) for p in params];v=[np.zeros_like(p) for p in params];step=0
    for epoch in range(15):
        idx=rng.permutation(len(x))
        for start in range(0,len(idx),512):
            ix=idx[start:start+512];xx=x[ix];yy=y[ix];h=np.tanh(xx@W+b);z=h@V+c;dz=2*(z-yy)/len(ix);dh=(dz@V.T)*(1-h*h);grads=[xx.T@dh,dh.sum(0),h.T@dz,dz.sum(0)];step+=1
            for j,(p,g) in enumerate(zip(params,grads)):
                m[j]=.9*m[j]+.1*g;v[j]=.999*v[j]+.001*g*g;p-=.002*(m[j]/(1-.9**step))/(np.sqrt(v[j]/(1-.999**step))+1e-8)
    return params

def select(e,st,acts,mode,params):
    if not any(a[0]=='q' for a in acts):return max(acts,key=lambda a:e.w[a[1]])
    W,b,V,c=params;x=np.array([e.feat(st,a,mode) for a in acts]);scores=x[:,10]+np.maximum(0,(np.tanh(x@W+b)@V+c).ravel())
    return acts[int(scores.argmax())]

def compare(out):
    train=[make(15000+i,'stress') for i in range(24)]+[make(16000+i,'perturbed_overlap') for i in range(12)]+[make(17000+i,'large') for i in range(8)]
    start=time.perf_counter();x,y,counts=dataset(train);print('dataset',len(train),sum(s for s,_ in counts),len(y),'seconds',time.perf_counter()-start,flush=True)
    seeds=(20261125,20261126,20261127);models={}
    for mode in ('scalar','rel','sham'):
        for seed in seeds:models[f'{mode}_{seed}']=fit(x[mode],y,seed,16 if mode=='scalar' else 10)
        print('trained',mode,flush=True)
    policies={'guess':lambda e,st,acts:max((a for a in acts if a[0]=='g'),key=lambda a:e.w[a[1]]),'greedy':lambda e,st,acts:max(acts,key=lambda a:e.immediate(st,a)), 'depth2':lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,2))}
    for key,par in models.items():policies[key]=lambda e,st,acts,k=key,p=par:select(e,st,acts,k.rsplit('_',1)[0],p)
    rows=[];times={k:[] for k in policies};times['oracle']=[]
    families=('stress','perturbed_overlap','large','partition')
    for family in families:
        for i in range(24):
            spec=make(23000+i,family);e=Env(spec);mass=e.mass(e.full);t=time.perf_counter_ns();opt=e.value(*e.start);times['oracle'].append(time.perf_counter_ns()-t)
            row={'family':family,'seed':23000+i,'mass':mass,'oracle':opt}
            for key,policy in policies.items():
                e=Env(spec);t=time.perf_counter_ns();v=e.rollout(policy);times[key].append(time.perf_counter_ns()-t);row[key]=v;assert v<=opt
            rows.append(row)
        print('evaluated',family,flush=True)
    def summar(rr):return {k:float(sum(Fraction(r[k],r['mass']) for r in rr)/len(rr)) for k in ('oracle',*policies)}
    result={'schema':'mit03-open-dev-v1','train_roots':len(train),'train_states':sum(s for s,_ in counts),'train_labels':len(y),'eval_roots':len(rows),'seeds':seeds,'params':{k:sum(p.size for p in v) for k,v in models.items()},'results':{f:summar([r for r in rows if r['family']==f]) for f in families},'overall':summar(rows),'median_rollout_ms':{k:float(np.median(v))/1e6 for k,v in times.items()},'rows':rows,'models':{k:[p.tolist() for p in v] for k,v in models.items()},'source_sha256':{p:hashlib.sha256(Path(__file__).with_name(p).read_bytes()).hexdigest() for p in ('selector.py','relational.py')}}
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('rows','models')},indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();compare(args.output)

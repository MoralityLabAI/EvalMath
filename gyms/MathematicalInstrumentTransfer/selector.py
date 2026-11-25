"""MIT-02: open synthetic policy distillation, deterministic membership instruments.
Requires numpy for the learned ranker; teacher and rollout use integer masses.
"""
from functools import lru_cache
from random import Random
import argparse
import json
import hashlib
from pathlib import Path


def world(seed, family):
    rng = Random(seed)
    n = 12 if family == 'stress' else 8
    order = list(range(n)); rng.shuffle(order)
    w = tuple(rng.randint(1, 4) for _ in order) if family in ('random','stress') else (1,)*n
    if family == 'random':
        masks = [sum(1 << i for i in rng.sample(order, rng.randint(2, 6))) for _ in range(3)]
    elif family == 'stress':
        w = tuple(rng.randint(1,3) for _ in order)
        masks = [sum(1 << i for i in rng.sample(order, rng.randint(2,n-2))) for _ in range(4)]
    elif family == 'tree':
        masks = [sum(1 << i for i in order[a:b]) for a,b in ((0,4),(0,2),(4,6))]
    elif family == 'overlap':
        masks = [sum(1 << i for i in order[a:b]) for a,b in ((0,4),(2,6),(4,8))]
    else:
        raise ValueError(family)
    # Remove orientation cues and randomize instrument order.
    masks = [m ^ ((1<<n)-1 if rng.randrange(2) else 0) for m in masks]
    rng.shuffle(masks)
    costs = tuple(rng.randint(1,2) if family == 'random' else 1 for _ in masks)
    return w, tuple(masks), costs, rng.choice((3,4)) if family == 'random' else 4


class Search:
    def __init__(self, spec):
        self.w,self.masks,self.costs,self.b = spec
        self.full = (1<<len(self.w))-1
        self.start = (self.full, (1<<len(self.masks))-1, self.b)
        self.value = lru_cache(None)(self._value)

    def mass(self,s):
        return sum(x for i,x in enumerate(self.w) if s>>i&1)

    def top(self,s,b):
        return sum(sorted((x for i,x in enumerate(self.w) if s>>i&1),reverse=True)[:max(b,0)])

    def actions(self,s,a,b):
        if not s or b<=0: return []
        return [('g',i) for i in range(len(self.w)) if s>>i&1]+[('q',j) for j,c in enumerate(self.costs) if a>>j&1 and c<b]

    def children(self,state,act):
        s,a,b=state; kind,i=act
        if kind=='g': return self.w[i], [(s^(1<<i),a,b-1)]
        m=self.masks[i]
        return 0, [(s&m,a^(1<<i),b-self.costs[i]),(s&~m,a^(1<<i),b-self.costs[i])]

    def q(self,state,act):
        hit,children=self.children(state,act)
        return hit+sum(self.value(*ch) for ch in children)

    def _value(self,s,a,b):
        return max((self.q((s,a,b),act) for act in self.actions(s,a,b)),default=0)

    def immediate(self,state,act):
        hit,children=self.children(state,act)
        return hit+sum(self.top(ch[0],ch[2]) for ch in children)

    def features(self,state,act):
        s,a,b=state; kind,i=act; mass=self.mass(s)
        hit,children=self.children(state,act)
        parts=sorted((self.mass(ch[0])/mass for ch in children),reverse=True)
        parts=(parts+[0,0])[:2]
        return [b/4,s.bit_count()/len(self.w),a.bit_count()/len(self.masks),self.top(s,1)/mass,self.top(s,b)/mass,
                float(kind=='q'),(self.costs[i] if kind=='q' else 1)/4,hit/mass,
                parts[0],parts[1],self.immediate(state,act)/mass]

    def states(self):
        stack=[self.start]; seen=set()
        while stack:
            st=stack.pop()
            if st in seen: continue
            seen.add(st)
            acts=self.actions(*st)
            if not acts: continue
            yield st,acts
            for act in acts:
                stack.extend(self.children(st,act)[1])

    def rollout(self,policy):
        def rec(st):
            acts=self.actions(*st)
            if not acts: return 0
            action=policy(self,st,acts)
            if action not in acts: raise ValueError('illegal action')
            hit,children=self.children(st,action)
            return hit+sum(rec(ch) for ch in children)
        return rec(self.start)


def teacher_data(specs, export=None):
    xs=[]; ys=[]; states=0
    for root,spec in enumerate(specs):
        env=Search(spec)
        for st,acts in env.states():
            states+=1; mass=env.mass(st[0])
            for act in acts:
                f=env.features(st,act); q=env.q(st,act)
                xs.append(f); ys.append(q/mass)
                if export is not None:
                    export.write(json.dumps({'root':root,'spec':spec,'state':st,'action':act,'features':f,'success_mass':q,'total_mass':mass},separators=(',',':'))+'\n')
    return xs,ys,states


def run(export=None):
    import numpy as np
    # Open development splits: different seed ranges and structural families.
    train=[world(1000+i,'random') for i in range(96)]
    groups={f:[world(9000+i,f) for i in range(32)] for f in ('random','tree','overlap','stress')}
    xs,ys,states=teacher_data(train,export)
    x=np.asarray(xs,dtype=np.float64); y=np.asarray(ys)[:,None]
    rng=np.random.default_rng(20261125)
    W=rng.normal(0,.25,(x.shape[1],16)); b=np.zeros(16); V=rng.normal(0,.25,(16,1)); c=np.zeros(1)
    params=[W,b,V,c]; m=[np.zeros_like(p) for p in params]; v=[np.zeros_like(p) for p in params]; step=0
    for _ in range(12):
        idx=rng.permutation(len(x))
        for start in range(0,len(x),256):
            ix=idx[start:start+256]; xx=x[ix]; yy=y[ix]
            h=np.tanh(xx@W+b); z=h@V+c; dz=2*(z-yy)/len(ix); dh=(dz@V.T)*(1-h*h)
            grads=[xx.T@dh,dh.sum(0),h.T@dz,dz.sum(0)]; step+=1
            for j,(p,g) in enumerate(zip(params,grads)):
                m[j]=.9*m[j]+.1*g; v[j]=.999*v[j]+.001*g*g
                p-=.003*(m[j]/(1-.9**step))/(np.sqrt(v[j]/(1-.999**step))+1e-8)
    def learned(e,st,acts):
        xx=np.array([e.features(st,a) for a in acts]); scores=(np.tanh(xx@W+b)@V+c).ravel()
        return acts[int(scores.argmax())]
    def greedy(e,st,acts): return max(acts,key=lambda a:e.immediate(st,a))
    def guess(e,st,acts): return max((a for a in acts if a[0]=='g'),key=lambda a:e.w[a[1]])
    results={}; rows=[]
    for family,specs in groups.items():
        for i,spec in enumerate(specs):
            e=Search(spec); mass=e.mass(e.full); opt=e.value(*e.start)
            learned_v=e.rollout(learned); greedy_v=e.rollout(greedy); guess_v=e.rollout(guess)
            assert max(learned_v,greedy_v,guess_v)<=opt<=mass
            rows.append(dict(family=family,root=i,mass=mass,oracle=opt,learned=learned_v,greedy=greedy_v,guess=guess_v))
        r=[x for x in rows if x['family']==family]
        from fractions import Fraction
        results[family]={k:str(sum((Fraction(z[k],z['mass']) for z in r),Fraction())/len(r)) for k in ('oracle','learned','greedy','guess')}
        results[family]['learned_wins_vs_greedy']=sum(z['learned']>z['greedy'] for z in r)
        results[family]['learned_losses_vs_greedy']=sum(z['learned']<z['greedy'] for z in r)
    return dict(schema='mit02-open-dev-v1',evidence='synthetic open development diagnostic',train_roots=len(train),train_states=states,train_action_labels=len(xs),parameter_count=sum(p.size for p in params),eval_roots=len(rows),results=results,rows=rows,model={'W':W.tolist(),'b':b.tolist(),'V':V.tolist(),'c':c.tolist()},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limitations='Known toy likelihoods, exact posterior, single winner; open families, no measured mathematical transfer, no sealed split or causal claim.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--teacher-jsonl-gz',type=Path);args=p.parse_args()
    if args.teacher_jsonl_gz:
        import gzip
        with gzip.open(args.teacher_jsonl_gz,'wt') as f: report=run(f)
    else: report=run()
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','model')},indent=2))

"""VAD-03B: robust index controls and optional learned recurrent policy."""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random
import json, time
from .evaluation_vad_lookahead import D, mask, roots, cost, build, random_pairs, signature_pairs

H, BUDGET, ACTIONS = 1024, 8, (8,7,6,5,0)
TRAIN_REGIMES = ('clean','noise1','noise2','noise3','null','multi')
TEST_REGIMES = TRAIN_REGIMES + ('noise4','structured','shifted')
SPLITS = {'train': (100000, 48), 'cal': (200000, 24), 'test': (300000, 32)}
METHODS = ['single','strict03a','random','beam','q8','q7','q6','q5','multi86','multi75','multi65','multi85']


def family(seed,size,regime,n=H):
    rng=Random(seed); p=rng.sample(range(D),D)
    m1,e1,m2,e2=map(mask,(p[:4],p[4:7],p[7:11],p[11:14]))
    p1=tuple(sorted((mask(p[:2])|e1,mask(p[2:4])|e1)))
    p2=tuple(sorted((mask(p[7:9])|e2,mask(p[9:11])|e2)))
    planted=(p1,p2) if regime=='multi' else (() if regime=='null' else (p1,))
    pool=set(a for pair in ((p1,p2) if regime=='multi' else (p1,)) for a in pair)
    while len(pool)<size: pool.add(mask(rng.sample(range(D),5)))
    pool=sorted(pool); rng.shuffle(pool)
    r=Random(seed+1_000_000)
    if regime=='null': dev=roots(r,0,0,8)
    elif regime=='multi':
        a=roots(r,m1,e1,4); dev=a+roots(r,m2,e2,4,a)
    else:
        k={'noise1':1,'noise2':2,'noise3':3,'noise4':4,'structured':3}.get(regime,0)
        a=roots(r,m1,e1,8-k)
        b=roots(r,m2,e2,k,a) if regime=='structured' else roots(r,0,0,k,a)
        dev=a+b
    dev=list(dev); r.shuffle(dev); dev=tuple(dev)
    r=Random(seed+2_000_000)
    if regime=='null': held=roots(r,0,0,n,dev)
    elif regime=='shifted': held=roots(r,m2,e2|m1,n,dev)
    elif regime=='multi':
        a=roots(r,m1,e1,n//2,dev); held=a+roots(r,m2,e2,n-len(a),dev+a)
        held=list(held); r.shuffle(held); held=tuple(held)
    else: held=roots(r,m1,e1,n,dev)
    assert len(set(held))==n and not set(dev)&set(held)
    return tuple(pool),dev,held,planted


def index(pool,dev,q,limit,seen=()):
    if not limit or not q: return [],0
    assert q>len(dev)/2
    counts=[sum((t>>i)&1 for t in dev) for i in range(D)]
    ones=mask(i for i,c in enumerate(counts) if c>=q)
    zeros=mask(i for i,c in enumerate(counts) if c<=len(dev)-q)
    fixed=ones|zeros; work=D*(len(dev)+2)+1
    buckets=defaultdict(list); sig=[]
    for i,a in enumerate(pool):
        s=a&fixed; sig.append(s); buckets[s].append(i); work+=2
    out=[]; seen=set(seen)
    for i,s in enumerate(sig):
        work+=2
        for j in buckets.get(s^ones,()):
            work+=1
            if j>i:
                pair=tuple(sorted((pool[i],pool[j])))
                if pair not in seen:
                    out.append(pair)
                    if len(out)==limit: return out,work
    return out,work


class State:
    def __init__(self,pool,dev):
        self.pool,self.dev=pool,dev; self.best=(); self.val=0; self.work=0
        self.scored=set(); self.single=[]; self.steps=[]; self.base=sum(cost(t) for t in dev)
        for a in pool:
            v=self.consider((a,)); self.single.append((v,a))
    def consider(self,lib):
        self.work+=2*len(self.dev)+1 if len(lib)==1 else 4*len(self.dev)+6
        v=H*(self.base-sum(cost(t,lib) for t in self.dev))-len(self.dev)*build(lib)
        if (-v,len(lib),lib)<(-self.val,len(self.best),self.best): self.best,self.val=lib,v
        return v
    def submit(self,pairs,work,action):
        self.work+=work; start=len(self.scored)
        for p in pairs:
            if p not in self.scored and len(self.scored)<BUDGET:
                self.scored.add(p); self.consider(p)
        self.steps.append((action,len(self.scored)-start))
    def apply(self,q,cap):
        if q:
            pairs,work=index(self.pool,self.dev,q,min(cap,BUDGET-len(self.scored)),self.scored)
            self.submit(pairs,work,q)
    def objective(self,aux):
        return sum(cost(t)-cost(t,self.best) for t in aux)*H//len(aux)-self.work-build(self.best)
    def feedback(self,first):
        return [first/8,len(self.scored)/8,self.val/(H*len(self.dev)*16),self.work/10000]


def fixed(pool,dev,method,seed):
    s=State(pool,dev)
    if method=='single': return s
    if method=='random':
        p,w=random_pairs(pool,BUDGET,seed); s.submit(p,w,'random'); return s
    if method=='beam':
        ranked=sorted(s.single,key=lambda va:(-va[0],va[1])); pairs=[]; work=len(pool)*len(pool).bit_length()
        for _,a in ranked[:2]:
            for _,b in ranked:
                work+=1; p=tuple(sorted((a,b)))
                if a!=b and p not in pairs: pairs.append(p)
                if len(pairs)==BUDGET: break
            if len(pairs)==BUDGET: break
        s.submit(pairs,work,'beam'); return s
    if method.startswith('q'):
        s.apply(int(method[1:]),BUDGET); return s
    if method.startswith('multi'):
        a,b=map(int,method[5:]); s.apply(a,4); s.apply(b,BUDGET); return s
    if method=='strict03a':
        p,w=signature_pairs(pool,dev,BUDGET); s.submit(p,w,8); return s
    raise ValueError(method)


def sequence(dev):
    counts=[0]*D; result=[]
    for j,t in enumerate(dev,1):
        for i in range(D): counts[i]+=(t>>i)&1
        result.append([sum(c==k for c in counts)/D for k in range(9)]+[j/8])
    return result


def examples(split):
    start,n=SPLITS[split]; regimes=TRAIN_REGIMES if split!='test' else TEST_REGIMES
    for ri,r in enumerate(regimes):
        for i in range(n):
            seed=start+(0 if r=='shifted' else ri*1000)+i; size=(32,64)[i%2]
            yield seed,size,r,family(seed,size,r,128 if split=='train' else H)


def training_rows():
    for seed,size,r,(pool,dev,aux,_) in examples('train'):
        seq=sequence(dev); results=[]; continuations=[]
        for a in ACTIONS:
            best=None
            for b in (ACTIONS if a else (0,)):
                s=State(pool,dev); s.apply(a,4); fb=s.feedback(a)
                if a and b and b!=a: s.apply(b,BUDGET)
                key=(s.objective(aux),-len(s.scored),-s.work,-ACTIONS.index(b))
                if best is None or key>best[0]: best=(key,b,fb)
            results.append((best[0],a))
            if a: continuations.append((seq,best[2],ACTIONS.index(best[1])))
        a=max(results,key=lambda z:(z[0],-ACTIONS.index(z[1])))[1]
        yield (seq,[0.,0.,0.,0.],ACTIONS.index(a))
        yield from continuations


def fit():
    import torch
    from torch import nn
    torch.manual_seed(4431); torch.set_num_threads(1)
    class Controller(nn.Module):
        def __init__(self):
            super().__init__(); self.rnn=nn.GRU(10,8,batch_first=True); self.out=nn.Linear(12,5)
        def forward(self,x,fb):
            _,h=self.rnn(x); return self.out(torch.cat((h[0],fb),dim=-1))
    t=time.monotonic(); data=list(training_rows()); m=Controller()
    x=torch.tensor([r[0] for r in data]); fb=torch.tensor([r[1] for r in data]); y=torch.tensor([r[2] for r in data]); opt=torch.optim.AdamW(m.parameters(),lr=.006)
    for _ in range(25):
        for inds in torch.randperm(len(y)).split(128):
            loss=nn.functional.cross_entropy(m(x[inds],fb[inds]),y[inds]); opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): acc=(m(x,fb).argmax(-1)==y).float().mean().item()
    return m,dict(rows=len(y),parameters=sum(p.numel() for p in m.parameters()),train_accuracy=acc,seconds=round(time.monotonic()-t,3),seed=4431,epochs=25)


def learned(pool,dev,m,ablation='none'):
    import torch
    seq=sequence(dev)
    if ablation=='shuffle': Random(991).shuffle(seq)
    if ablation=='memoryless': seq=seq[-1:]
    s=State(pool,dev)
    with torch.no_grad():
        x=torch.tensor([seq]); _,h=m.rnn(x)
        def action(fb): return ACTIONS[m.out(torch.cat((h[0],torch.tensor([fb])),dim=-1)).argmax(-1).item()]
        a=action([0.,0.,0.,0.]); s.apply(a,4)
        if a:
            b=action(s.feedback(a))
            if b and b!=a: s.apply(b,BUDGET)
        # Charge feature construction separately; MAC count is a separate sensitivity axis.
        s.work+=len(dev)*D*10
        macs=len(seq)*3*8*(10+8)+60*(1+bool(a))
    return s,macs


def evaluate(split,methods,model=None):
    rows=[]
    for seed,size,regime,(pool,dev,held,planted) in examples(split):
        for method in methods:
            macs=0
            if method.startswith('learned'):
                s,macs=learned(pool,dev,model,method.removeprefix('learned').strip('_') or 'none')
            else: s=fixed(pool,dev,method,seed+3_000_000)
            base=sum(cost(t) for t in held); total=sum(cost(t,s.best) for t in held)+s.work+build(s.best)
            rows.append(dict(seed=seed,size=size,regime=regime,method=method,base=base,total=total,work=s.work,construction=build(s.best),pair_evals=len(s.scored),library=s.best,recovered=s.best in planted,macs=macs,steps=s.steps))
    return rows


def summarize(rows):
    out=[]
    for r in sorted({x['regime'] for x in rows}):
        for m in sorted({x['method'] for x in rows}):
            rr=[x for x in rows if x['regime']==r and x['method']==m]
            if not rr: continue
            base=sum(x['base'] for x in rr); total=sum(x['total'] for x in rr); mac=sum(x['macs'] for x in rr)
            out.append(dict(regime=r,method=m,n=len(rr),base=base,total=total,gain=base/total,gain_with_mac=base/(total+mac),macs=mac,recovered=sum(x['recovered'] for x in rr),profitable=sum(x['total']<x['base'] for x in rr),pair_evals=sum(x['pair_evals'] for x in rr),work=sum(x['work'] for x in rr)))
    return out


def main():
    import argparse, torch
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
    model,train=fit(); print('TRAIN',train,flush=True)
    cal=evaluate('cal',METHODS,model)
    chosen=min(METHODS,key=lambda m:sum(x['total'] for x in cal if x['method']==m))
    print('CAL',chosen,flush=True)
    # Save frozen policy and calibration choice before accessing test roots.
    args.out.mkdir(parents=True,exist_ok=True); checkpoint=args.out/'controller.pt'; torch.save(model.state_dict(),checkpoint)
    freeze=dict(protocol='VAD-03B',split=SPLITS,training=train,chosen_symbolic=chosen,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),checkpoint_sha256=sha256(checkpoint.read_bytes()).hexdigest(),calibration=summarize(cal))
    (args.out/'freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    test=evaluate('test',METHODS+['learned','learned_shuffle','learned_memoryless'],model)
    primary=[]
    for r in TEST_REGIMES:
        a={x['seed']:x for x in test if x['regime']==r and x['method']==chosen}; b={x['seed']:x for x in test if x['regime']==r and x['method']=='learned'}
        d=[a[k]['total']-b[k]['total'] for k in sorted(a)]; rng=Random(20261125)
        bootstrap=sorted(sum(rng.choices(d,k=len(d)))/len(d) for _ in range(4000))
        primary.append(dict(regime=r,mean_paired_saving=sum(d)/len(d),ci95=[bootstrap[100],bootstrap[3899]],wins=sum(v>0 for v in d),ties=sum(v==0 for v in d)))
    report=dict(**freeze,test=summarize(test),primary=primary,records=test)
    (args.out/'vad_03b_full.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(primary,indent=2),flush=True)

if __name__=='__main__': main()

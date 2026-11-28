"""MIC-14 public proof replay: matched history order, not original search time."""
import argparse,gzip,hashlib,json,sys,random,time
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as F
from statistics import mean
import torch
from torch import nn
H=6; C=4; SEEDS=(17,29,43); TRAIN=('conflict','mixed'); DEV=('implication','disjunction')
ARMS=('ordered','shuffle','latest','bag')

def mask(s):return int(s,16)
def weight(d,s):return sum(w for i,w in enumerate(d.w) if s>>i&1)
def ident(r):return tuple(r[k] for k in ('family','kind','n','seed'))

class Replay:
    def __init__(self,d,p):
        self.d=d;self.nodes=p['nodes'];self.lower=p['value'];self.total=sum(d.w);self.n=len(d.w)
        self.raw=[];self.bounds=[];self.adj=[0]*self.n
        for i,j in d.edges:self.adj[i]|=1<<j;self.adj[j]|=1<<i
        for node in self.nodes:
            self.raw.append(tuple(map(mask,node['raw'])));k=node['kind']
            if k in ('branch','open','pruned'):u=sum(max(d.w[j] for j in range(self.n) if mask(g)>>j&1) for g in node['cliques'])
            elif k=='terminal':u=weight(d,mask(node['state'][0]))
            elif k=='ve':u=node['receipt']['value'] or 0
            elif k=='infeasible':u=0
            else:raise ValueError('unsupported node kind '+k)
            self.bounds.append(u)
        self.weights=[weight(d,s) for s,r in self.raw]
    def upper(self,front,permanent):return max([self.lower,permanent]+[u for _,u in front])
    def candidates(self,front):return sorted(front,key=lambda t:(-t[1],-self.weights[t[0]],t[0]))[:C]
    def step(self,front,perm,i):
        old=dict(front);cap=old.pop(i);node=self.nodes[i];new=min(cap,self.bounds[i]);k=node['kind']
        if k=='branch':
            for j in node['children']:
                assert j not in old
                if new>self.lower:old[j]=new
        elif k=='open':perm=max(perm,new)
        else:assert new<=self.lower
        return tuple(sorted(old.items())),perm
    def utility(self,front,perm,i):
        u=self.upper(front,perm);f,p=self.step(front,perm,i)
        best=min([self.upper(f,p)]+[self.upper(*self.step(f,p,j)) for j,_ in self.candidates(f)])
        return u-best
    def features(self,i,cap):
        s,r=self.raw[i];n=max(1,s.bit_count());deg=[(self.adj[j]&s).bit_count() for j in range(self.n) if s>>j&1]
        return [s.bit_count()/self.n,r.bit_count()/self.n,(s&~r).bit_count()/self.n,self.weights[i]/self.total,weight(self.d,r)/self.total,cap/self.total,(cap-self.lower)/self.total,sum(deg)/max(1,n*n),max(deg,default=0)/n,sum(1 for j,a in self.d.sup if s>>j&1 and not a&r)/max(1,len(self.d.sup)),1.]
    def event(self,i,cap,f,p,before):
        n=self.nodes[i];s,r=self.raw[i];k=n['kind'];u=min(cap,self.bounds[i]);state=n['state'];after=0 if state is None else mask(state[0]).bit_count()
        return [s.bit_count()/self.n,r.bit_count()/self.n,after/self.n,cap/self.total,u/self.total,(cap-u)/self.total,(before-self.upper(f,p))/self.total,len(f)/32,p/self.total]+[float(k==t) for t in ('branch','terminal','ve','infeasible','pruned','open')]
    def rows(self):
        front=((0,self.total),);perm=0;hist=[];past=[];rows=[];step=0
        while front:
            cand=self.candidates(front);u=self.upper(front,perm)
            if len(hist)>=H and len(cand)>=2:
                gains=[self.utility(front,perm,i) for i,_ in cand]
                rows.append(dict(step=step,history=hist[-H:],history_nodes=past[-H:],candidates=[self.features(i,c) for i,c in cand],obligations=[dict(node=i,raw=[hex(x) for x in self.raw[i]],cap=c) for i,c in cand],common=[self.lower/self.total,u/self.total,perm/self.total,len(front)/32,self.n/128],gains=gains,total=self.total,oracle_gain=max(gains),informative=max(gains)>min(gains),upper=u,lower=self.lower))
            i,cap=cand[0];f,p=self.step(front,perm,i);hist.append(self.event(i,cap,f,p,u));past.append(i);front,perm=f,p;step+=1
        return rows,self.upper(front,perm)

def extract(archive,source):
    sys.path.insert(0,str(source));from mic13 import Checker,instance
    rows=[];summary=[];seen=set();t=time.perf_counter()
    with gzip.open(archive,'rt',encoding='utf-8') as f:
        for line in f:
            row=json.loads(line);key=ident(row);pair=key+(row['mode'],);assert pair not in seen;seen.add(pair)
            d=instance(row['family'],row['seed'],row['n'],row['kind']);p=row['proof'];verified=Checker(d).check(p)
            rr,upper=Replay(d,p).rows();assert verified['lower']<=upper<=verified['upper']
            for r in rr:r.update(root=list(key),mode=row['mode'],split='train' if key[0] in TRAIN else 'dev')
            rows.extend(rr);summary.append(dict(root=list(key),mode=row['mode'],rows=len(rr),informative=sum(r['informative'] for r in rr),gainful=sum(r['oracle_gain']>0 for r in rr),replay_upper=upper,source_upper=verified['upper']))
    return rows,dict(archive_sha256=hashlib.sha256(Path(archive).read_bytes()).hexdigest(),proofs=len(seen),roots=len(set(x[:-1] for x in seen)),rows=len(rows),summaries=summary,elapsed_s=time.perf_counter()-t)

def order_history(r,seed,arm):
    h=[list(x) for x in r['history']]
    if arm=='shuffle':
        rng=random.Random(str((seed,r['root'],r['mode'],r['step'])));a=h[:-1];rng.shuffle(a);h=a+[h[-1]]
    return h

def tensorize(rows,seed,arm):
    hh=[];cc=[];xx=[];mm=[];gg=[]
    for r in rows:
        n=len(r['candidates']);hh.append(order_history(r,seed,arm));cc.append(r['candidates']+[[0.]*11]*(C-n));xx.append(r['common']);mm.append([True]*n+[False]*(C-n));gg.append([g/r['total'] for g in r['gains']]+[-1.]*(C-n))
    return tuple(torch.tensor(x,dtype=torch.bool if j==3 else torch.float32) for j,x in enumerate((hh,cc,xx,mm,gg)))

class Model(nn.Module):
    def __init__(self):
        super().__init__();self.cell=nn.GRUCell(15,16);self.head=nn.Sequential(nn.Linear(32,24),nn.Tanh(),nn.Linear(24,1))
    def forward(self,h,c,x,m,mode):
        z=torch.zeros(len(h),16,device=h.device)
        if mode=='latest':
            for j in range(H):z=self.cell(h[:,-1] if j==H-1 else torch.zeros_like(h[:,j]),torch.zeros_like(z))
        elif mode=='bag':z=torch.stack([self.cell(h[:,j],torch.zeros_like(z)) for j in range(H)],1).mean(1)
        else:
            for j in range(H):z=self.cell(h[:,j],z)
        z=torch.cat([z,x],-1)[:,None,:].expand(-1,C,-1)
        return self.head(torch.cat([c,z],-1)).squeeze(-1).masked_fill(~m,-torch.inf)

def fit(rows,seed,arm):
    torch.manual_seed(seed);net=Model();opt=torch.optim.Adam(net.parameters(),lr=.006)
    h,c,x,m,g=tensorize(rows,seed,arm);gold=(g==g.max(1,keepdim=True).values)&m;use=torch.tensor([r['informative'] for r in rows]);h,c,x,m,gold=[z[use] for z in (h,c,x,m,gold)]
    if not len(h):raise ValueError('no informative training rows')
    for _ in range(90):
        z=net(h,c,x,m,arm);loss=(torch.logsumexp(z,1)-torch.logsumexp(z.masked_fill(~gold,-torch.inf),1)).mean();opt.zero_grad();loss.backward();opt.step()
    return net,float(loss.detach())

@torch.no_grad()
def predict(net,rows,seed,arm):
    h,c,x,m,_=tensorize(rows,seed,arm);return net(h,c,x,m,arm).argmax(1).tolist()

def metrics(rows,actions):
    roots=defaultdict(list);gain=best=hits=infohits=info=0
    for r,i in zip(rows,actions):
        v=r['gains'][i];b=r['oracle_gain'];gain+=v;best+=b;hits+=v==b
        if r['informative']:
            info+=1;infohits+=v==b;roots[tuple(r['root'])].append(F(b-v,r['total']))
    return dict(rows=len(rows),informative=info,all_accuracy=hits/len(rows),informative_accuracy=infohits/max(1,info),oracle_gain_recovered=gain/max(1,best),gain=gain,oracle_gain=best,mean_root_normalized_regret=float(mean(mean(x) for x in roots.values())) if roots else None,informative_roots=len(roots))

def run(rows):
    torch.set_num_threads(1);train=[r for r in rows if r['split']=='train'];dev=[r for r in rows if r['split']=='dev'];assert not {tuple(r['root']) for r in train}&{tuple(r['root']) for r in dev}
    out={'first':[0]*len(dev),'raw_weight':[max(range(len(r['candidates'])),key=lambda i:r['candidates'][i][3]) for r in dev],'random':[random.Random(str((r['root'],r['mode'],r['step']))).randrange(len(r['candidates'])) for r in dev]};loss={}
    for seed in SEEDS:
        for arm in ARMS:
            net,l=fit(train,seed,arm);loss[f'{arm}_{seed}']=l;out[f'{arm}_{seed}']=predict(net,dev,seed,arm)
            if arm=='ordered':out[f'ordered_test_shuffle_{seed}']=predict(net,dev,seed,'shuffle')
    return dict(schema='MIC-14/public-replay/v1',train_rows=len(train),train_informative=sum(r['informative'] for r in train),train_roots=len({tuple(r['root']) for r in train}),dev_roots=len({tuple(r['root']) for r in dev}),dev_rows=len(dev),dev_informative=sum(r['informative'] for r in dev),model_parameters=sum(p.numel() for p in Model().parameters()),loss=loss,metrics={k:metrics(dev,v) for k,v in out.items()},predictions=out)

def main():
    a=argparse.ArgumentParser();a.add_argument('--archive',type=Path,required=True);a.add_argument('--source-dir',type=Path,required=True);a.add_argument('--out',type=Path,default=Path(__file__).parent);a=a.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    t=time.perf_counter();rows,s=extract(a.archive,a.source_dir);print(json.dumps({k:v for k,v in s.items() if k!='summaries'}),file=sys.stderr,flush=True)
    for split in ('train','dev'):
        r=[x for x in rows if x['split']==split];print(split,len(r),'info',sum(x['informative'] for x in r),'gainful',sum(x['oracle_gain']>0 for x in r),file=sys.stderr,flush=True)
    with gzip.open(a.out/'obligations.jsonl.gz','wt',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,separators=(',',':'))+'\n')
    (a.out/'extraction.json').write_text(json.dumps(s,indent=2,sort_keys=True)+'\n')
    result=run(rows);result['elapsed_s']=time.perf_counter()-t;(a.out/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='predictions'},indent=2))
if __name__=='__main__':main()

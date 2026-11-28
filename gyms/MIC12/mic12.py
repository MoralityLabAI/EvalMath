"""MIC-12: cost-aware exact elimination gate; public development."""
from mic11 import *
from fractions import Fraction as F
from statistics import mean
import torch
from torch import nn
MODEL_SEEDS=(17,29,43)
TRAIN_SEEDS=range(8100,8106)
DEV_SEEDS=range(9000,9002)
TEACH_CAP=32
LAMBDA=F(1,50)

def features(d,s,r,u,b):
    free,cl=project(d,s,r);n=free.bit_count();total=sum(d.w);deg={i:0 for i in bits(free)}
    for c in cl or []:
        mask=sum(1<<i for i in {j for j,_ in c})
        for i in bits(mask):deg[i]|=mask&~(1<<i)
    ds=[a.bit_count() for a in deg.values()]
    return [n/128,r.bit_count()/128,len(d.w)/128,len(cl or [])/max(1,n)/8,
            mean(ds)/16 if ds else 0,max(ds,default=0)/32,min(ds,default=0)/16,
            sum(x<=2 for x in ds)/max(1,n),max(0,u-b)/total,sum(d.w[i] for i in bits(free))/total]

def local_branch(d,s,r,u,b,cap=TEACH_CAP):
    e=Solver(d,True,True);front=[(-u,s,r)];seen={(s,r)}
    while front and e.norm_calls+2<=cap:
        neg,s,r=front.pop()
        if -neg<=b:continue
        edge=e.edge(s,e.degrees(s))
        if edge is None:
            assert valid(d,s);b=max(b,e.value(s));continue
        i=edge[0];assert not r>>i&1;children=[]
        for a,req in ((s&~(1<<i),r),(s&~e.adj[i],r|1<<i)):
            out=e.normalize(a,req)
            if out is None or out in seen:continue
            seen.add(out);q,req=out
            if not any(e.degrees(q).values()):
                assert valid(d,q);b=max(b,e.value(q));continue
            upper=e.upper(q)
            if upper>b:children.append((-upper,q,req))
        front.extend(sorted(children,reverse=True))
    return b,max([b]+[-v for v,_,_ in front]),e.norm_calls

def teach(d,s,r,u,b):
    ve=Residual(d,attempt_cap=1);rec=ve.attempt(s,r);lo,hi,calls=local_branch(d,s,r,u,b)
    cost=F(ve.cells,CELL_CAP)+F(ve.scans,SCAN_CAP)+F(ve.attempts,ATTEMPT_CAP)
    if rec is not None:
        assert verify(d,rec);v=max(b,rec['value'] if rec['value'] is not None else 0);assert lo<=v<=hi
    gap=0 if rec is not None else max(0,u-b)
    utility=F(hi-lo-gap,sum(d.w))-LAMBDA*(cost-F(calls,TEACH_CAP))
    return dict(x=features(d,s,r,u,b),target=int(rec is not None and utility>0),utility=str(utility),
                success=rec is not None,ve_cells=ve.cells,ve_scans=ve.scans,branch_calls=calls,
                branch_lower=lo,branch_upper=hi,upper=u,incumbent=b,active=hex(s),required=hex(r))

class Gate(nn.Module):
    def __init__(self):
        super().__init__();self.net=nn.Sequential(nn.Linear(10,16),nn.Tanh(),nn.Linear(16,1))
    def forward(self,x):return self.net(x).squeeze(-1)

def fit(rows,seed):
    torch.manual_seed(seed);net=Gate();opt=torch.optim.Adam(net.parameters(),lr=.012)
    x=torch.tensor([r['x'] for r in rows],dtype=torch.float32);y=torch.tensor([r['target'] for r in rows],dtype=torch.float32)
    for _ in range(160):
        loss=nn.functional.binary_cross_entropy_with_logits(net(x),y);opt.zero_grad();loss.backward();opt.step()
    return net,float(loss.detach())

def search(d,mode,cap=CAP,cell_cap=CELL_CAP,scan_cap=SCAN_CAP,attempt_cap=ATTEMPT_CAP,width=WIDTH,net=None,observer=None):
    """MIC-09 incumbent/frontier and normalization; exact residual replacement."""
    t=perf_counter();e=Solver(d,True,True);ve=Residual(d,cell_cap,scan_cap,attempt_cap,width)
    s=e.close(e.full);best=e.initializer(s);bestval=e.value(best);init=e.calls;initial=bestval;assert valid(d,best)
    front=[(-e.upper(s),s,0)];seen={(s,0)};steps=0;pops=0;root_solved=False;gate_calls=gate_yes=0
    while front:
        if e.norm_calls+2>cap:break
        neg,s,r=front.pop()
        if -neg<=bestval:continue
        pops+=1
        if observer is not None:observer(s,r,-neg,bestval,pops)
        available=ve.attempts<ve.attempt_cap and ve.scans<ve.scan_cap and ve.cells<ve.cell_cap
        attempt=available and mode!='baseline' and (pops==1 or mode=='always' or (mode=='periodic' and (pops%8==0 or (s&~r).bit_count()<=24)) or (mode=='size' and (s&~r).bit_count()<=24))
        if available and mode=='learned' and pops>1:
            gate_calls+=1
            with torch.no_grad():attempt=bool(net(torch.tensor(features(d,s,r,-neg,bestval),dtype=torch.float32))>=0)
            gate_yes+=int(attempt)
        if attempt:
            rec=ve.attempt(s,r)
            if rec is not None:
                root_solved |= pops==1
                if rec['value'] is not None:
                    assert rec['value']<=-neg
                    if rec['value']>bestval:bestval=rec['value'];best=int(rec['mask'],16)
                continue
        edge=e.edge(s,e.degrees(s))
        if edge is None:
            if e.value(s)>bestval:best,bestval=s,e.value(s)
            continue
        i=edge[0];assert not r>>i&1;steps+=1;children=[]
        for active,forced in ((s&~(1<<i),r),(s&~e.adj[i],r|1<<i)):
            norm=e.normalize(active,forced)
            if norm is None:continue
            q,req=norm
            if (q,req) in seen:continue
            seen.add((q,req));v=e.value(q)
            if not any(e.degrees(q).values()):
                assert valid(d,q)
                if v>bestval:best,bestval=q,v
                continue
            b=e.upper(q)
            if b>bestval:children.append((-b,q,req))
        front.extend(sorted(children,reverse=True))
    hi=max([bestval]+[-u for u,_,_ in front]);assert valid(d,best)
    return dict(value=bestval,upper=hi,mask=hex(best),certified=bestval==hi,init_value=initial,init_calls=init,normalizations=e.norm_calls,raw_closure_calls=e.calls-init,support_checks=e.support_checks,bound_calls=e.bound_calls,enum_masks=e.enum_masks,enum_clause_checks=e.enum_clause_checks,forced_scans=e.forced_scans,component_scans=e.component_scans,expansions=steps,pops=pops,ve_attempts=ve.attempts,ve_cells=ve.cells,ve_scans=ve.scans,ve_failures=ve.failures,ve_receipts=ve.receipts,root_solved=root_solved,gate_calls=gate_calls,gate_yes=gate_yes,ms=(perf_counter()-t)*1000)


def training():
    rows=[];roots=0
    for f in ('conflict','mixed'):
        for n in (32,64):
            for seed in TRAIN_SEEDS:
                d=instance(f,seed,n,'original');states=[];roots+=1
                def observe(s,r,u,b,p):
                    if p>1 and len(states)<12 and (p==2 or p%5==0):states.append((s,r,u,b))
                search(d,'root',cap=256,observer=observe)
                for s,r,u,b in states:rows.append(dict(family=f,n=n,seed=seed,**teach(d,s,r,u,b)))
    assert rows and any(r['target'] for r in rows) and any(not r['target'] for r in rows)
    return roots,rows

def run():
    torch.set_num_threads(1);t=perf_counter();roots,train=training()
    models={s:fit(train,s) for s in MODEL_SEEDS};rows=[]
    print('trained',len(train),sum(r['target'] for r in train),flush=True,file=__import__('sys').stderr)
    for kind in KINDS:
        for n in SIZES:
            for f in FAMILIES:
                for seed in DEV_SEEDS:
                    d=instance(f,seed,n,kind);arms={k:search(d,k) for k in ('baseline','root','periodic','size','always')}
                    arms.update({f'learned_{s}':search(d,'learned',net=net) for s,(net,_) in models.items()})
                    lo=max(a['value'] for a in arms.values());hi=min(a['upper'] for a in arms.values());assert lo<=hi
                    for a in arms.values():
                        assert valid(d,int(a['mask'],16)) and a['normalizations']<=CAP
                        assert a['ve_cells']<=CELL_CAP and a['ve_scans']<=SCAN_CAP and a['ve_attempts']<=ATTEMPT_CAP
                    rows.append(dict(kind=kind,n=n,family=f,seed=seed,total_weight=sum(d.w),arms=arms,pooled_lower=lo,pooled_upper=hi))
            print('done',kind,n,flush=True,file=__import__('sys').stderr)
    return dict(schema='MIC-12/public-cpu/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),training_roots=roots,training_rows=train,train_loss={str(k):v[1] for k,v in models.items()},parameters=sum(p.numel() for p in next(iter(models.values()))[0].parameters()),seeds=MODEL_SEEDS,rows=rows,elapsed_s=perf_counter()-t,torch=torch.__version__)
if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))

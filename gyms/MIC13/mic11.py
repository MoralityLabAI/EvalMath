"""MIC-11: budgeted exact elimination of conditioned search states."""
from core import Root, valid
from run import bits, FAMILIES
from mic09 import Solver, solve as prior_solve
from mic10 import instance
from time import perf_counter
from pathlib import Path
from itertools import combinations
import hashlib, json
import numpy as np

WIDTH=10
CELL_CAP=250_000
SCAN_CAP=250_000
ATTEMPT_CAP=64
CAP=512
KINDS=('original','one_hub','three_hubs')
SIZES=(32,64,128)
SEEDS=range(7000,7002)


def clauses(d):
    return [((i,False),(j,False)) for i,j in d.edges]+[
        ((i,False),*((j,True) for j in bits(a))) for i,a in d.sup]


def project(d,s,r):
    full=(1<<len(d.w))-1
    if s&~full or r&~s or min(s,r)<0:raise ValueError('invalid state')
    free=s&~r;factors=[]
    for cl in clauses(d):
        remaining=[];sat=False
        for i,v in cl:
            if free>>i&1:remaining.append((i,v))
            elif bool(r>>i&1)==v:sat=True;break
        if sat:continue
        if not remaining:return free,None
        factors.append(tuple(remaining))
    return free,factors


def plan(d,free,cl,scan_limit,width_cap=WIDTH):
    """Min-degree elimination; charge initial cells + reads + output cells."""
    ids=list(bits(free));adj={i:0 for i in ids};scopes=[(i,) for i in ids]
    for c in cl:
        scope=tuple(sorted({i for i,_ in c}));scopes.append(scope)
        for i,j in combinations(scope,2):adj[i]|=1<<j;adj[j]|=1<<i
    cost=sum(1<<len(s) for s in scopes);scans=0;order=[];width=0;active=free
    while active:
        n=active.bit_count()
        if scans+n>scan_limit:return None,width,scans,0,'scan_cap'
        scans+=n
        i=min(bits(active),key=lambda j:((adj[j]&active).bit_count(),j));a=adj[i]&active
        w=a.bit_count();width=max(width,w)
        if w>width_cap:return None,width,scans,0,'width'
        here=[s for s in scopes if i in s];scopes=[s for s in scopes if i not in s]
        other=tuple(sorted({j for s in here for j in s if j!=i}));assert len(other)==w
        cost+=(2*len(here)+1)*(1<<w);scopes.append(other);order.append(i)
        for j in bits(a):adj[j]|=a&~(1<<j)
        active&=~(1<<i)
    return order,width,scans,cost,'ok'


def eliminate(d,s,r,order,cl):
    """Dense exact max-sum with dominating finite penalty."""
    free=s&~r;penalty=-sum(d.w)-1;fs=[];records=[];cells=0
    assert sorted(order)==list(bits(free))
    for i in bits(free):fs.append(((i,),np.array([0,d.w[i]],dtype=np.int64)));cells+=2
    for c in cl:
        scope=tuple(sorted({i for i,_ in c}));table=np.empty(1<<len(scope),dtype=np.int64)
        for q in range(len(table)):
            table[q]=0 if any(bool(q>>scope.index(i)&1)==v for i,v in c) else penalty
        fs.append((scope,table));cells+=len(table)
    for i in order:
        here=[(a,v) for a,v in fs if i in a];fs=[(a,v) for a,v in fs if i not in a]
        other=tuple(sorted({j for a,_ in here for j in a if j!=i}));ix=np.arange(1<<len(other),dtype=np.int64);scores=[]
        for x in (0,1):
            z=np.zeros(len(ix),dtype=np.int64)
            for a,v in here:
                ind=np.zeros(len(ix),dtype=np.int64)
                for k,j in enumerate(a):ind|=(x<<k) if j==i else ((ix>>other.index(j))&1)<<k
                z+=v[ind];cells+=len(ix)
            scores.append(z)
        fs.append((other,np.maximum(*scores)));cells+=len(ix);records.append((i,other,scores[1]>scores[0]))
    v=sum(int(a[0]) for _,a in fs)+sum(d.w[i] for i in bits(r))
    if v<0:return None,None,cells
    p=r
    for i,scope,arg in reversed(records):
        q=sum(1<<j for j,k in enumerate(scope) if p>>k&1)
        if arg[q]:p|=1<<i
    assert p&~s==0 and r&~p==0 and valid(d,p) and sum(d.w[i] for i in bits(p))==v
    return v,p,cells


def verify(d,receipt,width_cap=WIDTH):
    """Independent residual replay from original factors; missing entries = infeasible."""
    s=int(receipt['active'],16);r=int(receipt['required'],16);full=(1<<len(d.w))-1
    if min(s,r)<0 or s&~full or r&~s:return False
    free=s&~r;order=receipt['order'];fs=[]
    original=[((i,j),lambda x,i=i,j=j:not(x>>i&1 and x>>j&1)) for i,j in d.edges]
    original += [(tuple({i,*bits(a)}),lambda x,i=i,a=a:not(x>>i&1) or bool(x&a)) for i,a in d.sup]
    for i in bits(free):fs.append(((i,),{0:0,1:d.w[i]}))
    for vs,pred in original:
        scope=tuple(sorted(i for i in vs if free>>i&1));tab={}
        for q in range(1<<len(scope)):
            x=r|sum(1<<i for k,i in enumerate(scope) if q>>k&1)
            if pred(x):tab[q]=0
        if not tab:
            return not order and receipt['value'] is None and receipt['mask'] is None and receipt['reason']=='constant_false' and receipt['cells']==0
        if len(tab)==1<<len(scope):continue
        fs.append((scope,tab))
    if sorted(order)!=list(bits(free)):return False
    width=0;cells=sum(1<<len(a) for a,_ in fs)
    for i in order:
        here=[(a,v) for a,v in fs if i in a];fs=[(a,v) for a,v in fs if i not in a]
        other=tuple(sorted({j for a,_ in here for j in a if j!=i}));width=max(width,len(other))
        if width>width_cap:return False
        cells+=(2*len(here)+1)*(1<<len(other))
        idx=[tuple(-1 if j==i else other.index(j) for j in a) for a,_ in here];tab={}
        for q in range(1<<len(other)):
            cand=[]
            for x in (0,1):
                total=0
                for (_,v),pos in zip(here,idx):
                    ind=sum((x if k==-1 else q>>k&1)<<j for j,k in enumerate(pos))
                    if ind not in v:break
                    total+=v[ind]
                else:cand.append(total)
            if cand:tab[q]=max(cand)
        fs.append((other,tab))
    v=None if any(0 not in a for _,a in fs) else sum(a[0] for _,a in fs)+sum(d.w[i] for i in bits(r))
    if v!=receipt['value'] or width!=receipt['width'] or cells!=receipt['cells'] or receipt['reason']!='eliminated':return False
    if v is None:return receipt['mask'] is None
    p=int(receipt['mask'],16)
    return p&~s==0 and r&~p==0 and valid(d,p) and sum(d.w[i] for i in bits(p))==v


class Residual:
    def __init__(self,d,cell_cap=CELL_CAP,scan_cap=SCAN_CAP,attempt_cap=ATTEMPT_CAP,width=WIDTH):
        self.d=d;self.cell_cap=cell_cap;self.scan_cap=scan_cap;self.attempt_cap=attempt_cap;self.width=width
        self.cells=self.scans=self.attempts=0;self.receipts=[];self.failures={}
    def attempt(self,s,r):
        if self.attempts>=self.attempt_cap or self.scans>=self.scan_cap or self.cells>=self.cell_cap:return None
        self.attempts+=1;free,cl=project(self.d,s,r)
        if cl is None:
            receipt=dict(active=hex(s),required=hex(r),order=[],width=0,value=None,mask=None,cells=0,reason='constant_false')
        else:
            o,w,k,c,reason=plan(self.d,free,cl,self.scan_cap-self.scans,self.width);self.scans+=k
            if o is None or c>self.cell_cap-self.cells:
                reason=reason if o is None else 'cell_cap';self.failures[reason]=self.failures.get(reason,0)+1;return None
            v,p,used=eliminate(self.d,s,r,o,cl);assert used==c;self.cells+=used
            receipt=dict(active=hex(s),required=hex(r),order=o,width=w,value=v,mask=None if p is None else hex(p),cells=used,reason='eliminated')
        self.receipts.append(receipt);return receipt


def search(d,mode,cap=CAP,cell_cap=CELL_CAP,scan_cap=SCAN_CAP,attempt_cap=ATTEMPT_CAP,width=WIDTH):
    """MIC-09 incumbent/frontier and normalization; exact residual replacement."""
    t=perf_counter();e=Solver(d,True,True);ve=Residual(d,cell_cap,scan_cap,attempt_cap,width)
    s=e.close(e.full);best=e.initializer(s);bestval=e.value(best);init=e.calls;initial=bestval;assert valid(d,best)
    front=[(-e.upper(s),s,0)];seen={(s,0)};steps=0;pops=0;root_solved=False
    while front:
        if e.norm_calls+2>cap:break
        neg,s,r=front.pop()
        if -neg<=bestval:continue
        pops+=1
        if mode!='baseline' and (pops==1 or mode=='always' or (mode=='periodic' and (pops%8==0 or (s&~r).bit_count()<=24))):
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
    return dict(value=bestval,upper=hi,mask=hex(best),certified=bestval==hi,init_value=initial,init_calls=init,normalizations=e.norm_calls,raw_closure_calls=e.calls-init,support_checks=e.support_checks,bound_calls=e.bound_calls,enum_masks=e.enum_masks,enum_clause_checks=e.enum_clause_checks,forced_scans=e.forced_scans,component_scans=e.component_scans,expansions=steps,pops=pops,ve_attempts=ve.attempts,ve_cells=ve.cells,ve_scans=ve.scans,ve_failures=ve.failures,ve_receipts=ve.receipts,root_solved=root_solved,ms=(perf_counter()-t)*1000)


def run():
    t=perf_counter();rows=[]
    for kind in KINDS:
        for n in SIZES:
            for f in FAMILIES:
                for seed in SEEDS:
                    d=instance(f,seed,n,kind);arms={k:search(d,k) for k in ('baseline','root','periodic','always')}
                    arms['baseline1024']=search(d,'baseline',cap=1024)
                    lo=max(a['value'] for a in arms.values());hi=min(a['upper'] for a in arms.values());assert lo<=hi
                    for k,a in arms.items():
                        assert valid(d,int(a['mask'],16)) and a['normalizations']<=(1024 if k=='baseline1024' else CAP)
                        assert a['ve_cells']<=CELL_CAP and a['ve_scans']<=SCAN_CAP and a['ve_attempts']<=ATTEMPT_CAP
                    rows.append(dict(kind=kind,n=n,family=f,seed=seed,total_weight=sum(d.w),arms=arms,pooled_lower=lo,pooled_upper=hi))
            print('done',kind,n,flush=True,file=__import__('sys').stderr)
    return dict(schema='MIC-11/public-cpu/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),caps=dict(normalizations=CAP,ve_cells=CELL_CAP,ve_scans=SCAN_CAP,ve_attempts=ATTEMPT_CAP,width=WIDTH),rows=rows,elapsed_s=perf_counter()-t)

if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))

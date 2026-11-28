"""MIC-13: explicit proof DAG for bounded search and independent frontier replay."""
from mic11 import Residual, verify as verify_ve, search as old_search
from mic10 import instance
from mic09 import Solver
from run import bits, FAMILIES
from core import Root
from time import perf_counter
from pathlib import Path
from collections import Counter
import gzip, json, hashlib, sys
CAP=512
MODES=('baseline','periodic')
KINDS=('original','one_hub','three_hubs')
SIZES=(32,64,128)
SEEDS=range(10000,10002)

def pair(s,r):return [hex(s),hex(r)]
def unpair(p):return tuple(int(x,16) for x in p)
def weight(d,s):return sum(w for i,w in enumerate(d.w) if s>>i&1)
def feasible(d,s):
    return 0<=s<1<<len(d.w) and all(not (s>>i&1 and s>>j&1) for i,j in d.edges) and all(not s>>i&1 or s&a for i,a in d.sup)

class Producer(Solver):
    def certificate_bound(self,s):
        def cover(order):
            gs=[]
            for i in order:
                if not s>>i&1:continue
                for k,g in enumerate(gs):
                    if g&self.adj[i]==g:gs[k]=g|1<<i;break
                else:gs.append(1<<i)
            return sum(max(self.d.w[i] for i in bits(g)) for g in gs),gs
        self.bound_calls+=1
        v,g=min((cover(self.order),cover(sorted(bits(s),key=lambda i:(-(self.adj[i]&s).bit_count(),-self.d.w[i],i)))),key=lambda x:x[0])
        return v,[hex(x) for x in g]
    def normalize_record(self,s,r):
        self.norm_calls+=1;out=self.propagate(s,r)
        if out is None:return None,[],None
        s,r=out;prop=pair(s,r);records=[];parts=self.components(s)
        if len(parts)>=2:
            for c in parts:
                if c&~r==0:continue
                if not any(self.adj[i]&c for i in bits(c)):best=c
                elif c.bit_count()<=8:best=self.component_opt(c,r)
                else:continue
                records.append([hex(c),None if best is None else hex(best)])
                if best is None:return prop,records,None
                s=(s&~c)|best;r|=best;self.components_solved+=1
        return prop,records,pair(s,r)


def produce(d,mode,cap=CAP,width=10):
    t=perf_counter();e=Producer(d,True,True);ve=Residual(d,width=width);nodes=[];seen={};front=[];pops=0;expansions=0
    s=e.close(e.full);best=e.initializer(s);bv=e.value(best);initial=bv
    def register(raw,root=False):
        nonlocal best,bv
        i=len(nodes);a,r=raw
        prop,comp,out=(pair(s,0),[],pair(s,0)) if root else e.normalize_record(a,r)
        n=dict(raw=pair(a,r),prop=prop,components=comp,state=out);nodes.append(n)
        if out is None:n['kind']='infeasible';return i,None
        q,req=unpair(out)
        if (q,req) in seen:n.update(kind='alias',target=seen[q,req]);return i,None
        seen[q,req]=i
        if not root and not any(e.degrees(q).values()):
            n['kind']='terminal';v=e.value(q)
            if v>bv:best,bv=q,v
            return i,None
        u,g=e.certificate_bound(q);n['cliques']=g
        if not root and u<=bv:n['kind']='pruned';return i,None
        n['kind']='pending';return i,(-u,q,req,i)
    _,p=register((e.full,0),True);front.append(p)
    while front and e.norm_calls+2<=cap:
        neg,s,r,i=front.pop();n=nodes[i]
        if -neg<=bv:n['kind']='pruned';continue
        pops+=1
        if mode!='baseline' and (pops==1 or pops%8==0 or (s&~r).bit_count()<=24):
            rec=ve.attempt(s,r)
            if rec is not None:
                n.update(kind='ve',receipt=rec)
                if rec['value'] is not None and rec['value']>bv:best,bv=int(rec['mask'],16),rec['value']
                continue
        edge=e.edge(s,e.degrees(s))
        if edge is None:
            n['kind']='terminal';v=e.value(s)
            if v>bv:best,bv=s,v
            continue
        j=edge[0];assert not r>>j&1;children=[];ids=[];expansions+=1
        for raw in ((s&~(1<<j),r),(s&~e.adj[j],r|1<<j)):
            k,p=register(raw);ids.append(k)
            if p is not None:children.append(p)
        n.update(kind='branch',vertex=j,children=ids);front.extend(sorted(children,reverse=True))
    for _,_,_,i in front:nodes[i]['kind']='open'
    hi=max([bv]+[-u for u,_,_,_ in front]);assert feasible(d,best)
    return dict(schema='MIC-13/frontier/v1',mode=mode,width=width,cap=cap,mask=hex(best),value=bv,upper=hi,certified=bv==hi,nodes=nodes,
                initial=initial,normalizations=e.norm_calls,expansions=expansions,ve_cells=ve.cells,ve_attempts=ve.attempts,
                support_checks=e.support_checks,enum_masks=e.enum_masks,producer_ms=(perf_counter()-t)*1000)


def need(ok,message):
    if not ok:raise ValueError(message)

class Checker:
    """Independent CNF propagation, component optima, clique certificates and proof DAG.
    Uses MIC-11 independent sparse residual replay; never calls search or Solver.
    """
    def __init__(self,d):
        self.d=d;self.full=(1<<len(d.w))-1;self.edges={tuple(sorted(e)) for e in d.edges}
        self.cnf=[(0,(1<<i)|(1<<j)) for i,j in d.edges]+[(a,1<<i) for i,a in d.sup]
        self.memo={};self.visiting=set();self.count=Counter();self.component_cache={}
    def unit(self,s,r):
        if r&~s:return None
        while True:
            old=s,r;free=s&~r
            for pos,neg in self.cnf:
                if pos&neg or pos&r or neg&~s:continue
                live=(pos|neg)&free
                if not live:return None
                if live&(live-1)==0:
                    if live&pos:r|=live
                    else:s&=~live
                    break
            if old==(s,r):return s,r
    def component(self,s,r,c,p):
        d=self.d;need(c>0 and c&s==c,'bad component domain')
        for pos,neg in self.cnf:
            if neg&~s or pos&neg:continue
            a=(pos|neg)&s
            need(not(a&c and a&~c),'crossing component clause')
        local=r&c;key=c,local
        if key not in self.component_cache:
            if feasible(d,c):gold=weight(d,c)
            else:
                need(c.bit_count()<=8,'component enumeration cap');gold=-1;x=c
                while True:
                    if not local&~x and feasible(d,x):gold=max(gold,weight(d,x))
                    if not x:break
                    x=(x-1)&c
            self.component_cache[key]=gold
        gold=self.component_cache[key];self.count['components']+=1
        if p is None:need(gold<0,'false component infeasibility');return None
        need(p>=0 and not p&~c and not local&~p and feasible(d,p) and weight(d,p)==gold,'nonoptimal component witness')
        return (s&~c)|p,r|p
    def normalize(self,n):
        s,r=unpair(n['raw']);need(0<=s<=self.full and 0<=r<=self.full,'invalid raw domain')
        got=self.unit(s,r);claimed=None if n['prop'] is None else unpair(n['prop'])
        need(got==claimed,'propagation mismatch')
        for c,p in n['components']:
            need(got is not None,'component after contradiction')
            got=self.component(*got,int(c,16),None if p is None else int(p,16))
        out=None if n['state'] is None else unpair(n['state']);need(got==out,'normalized state mismatch');return out
    def clique(self,s,groups):
        covered=0;v=0
        for h in groups:
            g=int(h,16);need(g>0 and g&s==g and not g&covered,'bad clique partition');covered|=g
            ids=[i for i in range(len(self.d.w)) if g>>i&1]
            need(all((i,j) in self.edges for a,i in enumerate(ids) for j in ids[a+1:]),'nonedge in clique')
            v+=max(self.d.w[i] for i in ids)
        need(covered==s,'incomplete clique partition');return v
    def visit(self,i):
        need(type(i) is int and 0<=i<len(self.nodes),'invalid node reference')
        need(i not in self.visiting,'cycle in proof DAG')
        if i in self.memo:return self.memo[i]
        self.visiting.add(i);n=self.nodes[i];kind=n['kind'];self.count[kind]+=1
        state=self.normalize(n)
        if state is None:need(kind=='infeasible','missing contradiction leaf');u=-1
        else:
            s,r=state;need(not r&~s,'invalid forced mask')
            if kind=='alias':
                j=n['target'];need(type(j) is int and 0<=j<i,'bad alias reference')
                need(self.nodes[j]['state']==n['state'],'alias state mismatch');u=self.visit(j)
            elif kind=='terminal':need(feasible(self.d,s),'infeasible terminal');u=weight(self.d,s)
            elif kind=='ve':
                q=n['receipt'];need(q['active']==hex(s) and q['required']==hex(r),'VE state mismatch')
                need(verify_ve(self.d,q,self.width),'invalid VE receipt');u=-1 if q['value'] is None else q['value'];self.count['ve_cells']+=q['cells']
            elif kind in ('pruned','open'):
                u=self.clique(s,n['cliques'])
                if kind=='pruned':need(u<=self.lower,'pruned above incumbent')
            elif kind=='branch':
                j=n['vertex'];need(type(j) is int and 0<=j<len(self.d.w) and (s&~r)>>j&1,'nonfree branch vertex')
                neighbors=sum(1<<b if a==j else 1<<a for a,b in self.edges if j in (a,b))
                children=n['children'];need(len(children)==2 and len(set(children))==2,'missing or duplicate branch')
                for k,raw in zip(children,(pair(s&~(1<<j),r),pair(s&~neighbors,r|1<<j))):
                    need(type(k) is int and i<k<len(self.nodes) and self.nodes[k]['raw']==raw,'branch partition mismatch')
                u=max(self.visit(k) for k in children)
            else:raise ValueError('unknown leaf kind')
        self.visiting.remove(i);self.memo[i]=u;return u
    def check(self,p):
        need(p['schema']=='MIC-13/frontier/v1','schema');self.nodes=p['nodes'];self.width=p['width']
        need(type(self.width) is int and 0<=self.width<=10,'width cap');need(bool(self.nodes) and self.nodes[0]['raw']==pair(self.full,0),'root domain')
        mask=int(p['mask'],16);need(feasible(self.d,mask),'invalid incumbent');self.lower=weight(self.d,mask)
        need(self.lower==p['value'],'incumbent value');upper=max(self.lower,self.visit(0))
        need(len(self.memo)==len(self.nodes),'unreachable node')
        need(upper==p['upper'] and p['certified']==(upper==self.lower),'global interval mismatch')
        need(len(self.nodes)-1==p['normalizations']==2*self.count['branch'] and p['normalizations']<=p['cap'],'branch ledger mismatch')
        need(self.count['branch']==p['expansions'] and self.count['ve_cells']==p['ve_cells'] and self.count['ve']<=p['ve_attempts'],'work ledger mismatch')
        return dict(lower=self.lower,upper=upper,certified=upper==self.lower,counts=dict(self.count),nodes=len(self.memo))


def run():
    t=perf_counter();rows=[];p=Path(__file__).parent
    with gzip.open(p/'proofs.jsonl.gz','wt',encoding='utf-8') as f:
        for kind in KINDS:
            for size in SIZES:
                for family in FAMILIES:
                    for seed in SEEDS:
                        d=instance(family,seed,size,kind);arms={}
                        for mode in MODES:
                            proof=produce(d,mode);start=perf_counter();receipt=Checker(d).check(proof);replay_ms=(perf_counter()-start)*1000
                            old=old_search(d,mode);fields=('value','upper','mask','normalizations','expansions','ve_cells','ve_attempts')
                            need(all(proof[k]==old[k] for k in fields),'prior solver disagreement')
                            line=json.dumps(dict(kind=kind,n=size,family=family,seed=seed,mode=mode,proof=proof),separators=(',',':'))
                            f.write(line+'\n');arms[mode]=dict(**{k:v for k,v in proof.items() if k!='nodes'},replay=receipt,replay_ms=replay_ms,prior_ms=old['ms'],proof_bytes=len(line.encode()))
                        rows.append(dict(kind=kind,n=size,family=family,seed=seed,arms=arms))
                print('done',kind,size,flush=True,file=sys.stderr)
    return dict(schema='MIC-13/public-cpu/v1',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,elapsed_s=perf_counter()-t)

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))

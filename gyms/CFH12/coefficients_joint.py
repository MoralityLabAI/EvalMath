"""CFH-12: common coefficient-cell cost, joint affine response certificates."""
import argparse, json, hashlib, sys, random
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations, product
from math import comb, prod
from functools import cache
HERE=Path(__file__).resolve().parent
for k in (4,5,6,11):
    for name in (f'CFH{k:02}',f'cfh{k:02}_dev'):
        sys.path.insert(0,str(HERE.parent/name))
from hidden_invariant import coefficients,direct_coefficients
from compositional import routes
from lazy_acquisition import known_coeff
from certified import new_decks,graph_key,load,bits
CAPS=(8,24); PRICES=(0,2,8); SCALE=400; LIMIT=256
ARMS=('free','exact_vector','exact_cell','greedy_vector','greedy_cell','independent_pair','coupled_pair')

class Deck:
    def __init__(self,cards):
        self.cards=cards;self.rr=routes(2);self.n=len(self.rr);self.full=(1<<self.n)-1
        keys=sorted({r[:4] for r in self.rr});ids={};self.values=[];refs={};groups={};self.audit=Counter()
        for h,g in enumerate(cards):
            for r in keys:
                l,rt,c,inv=r;n,es=g;m=n-l-rt
                E={(a-l,b-l) for a,b in es if l<=a<b<n-rt}
                if c:E=set(combinations(range(m),2))-E
                t=m,tuple(sorted(E));a=coefficients(t,inv);b=direct_coefficients(t)[inv];_,z=known_coeff(g,r)
                assert a==b and all(a[j]==v for j,v in z.items());self.audit['base_vectors']+=1;mask=0
                for j,v in enumerate(a):
                    if j not in z:
                        i=len(self.values);ids[h,r,j]=i;self.values.append(v);mask|=1<<i
                groups[h,r]=mask;refs[h,r]=(m,z,a)
        self.probes=tuple((h,k,p) for h,g in enumerate(cards) for k in range(g[0]+1) for p in (2,3,5))
        self.expr=[];self.truth=[];self.rneeds=[];self.vneeds=[];self.groups=tuple(tuple(i for i,r in enumerate(self.rr) if r[:4]==key) for key in keys)
        for h,k,p in self.probes:
            ex=[];truth=[0]*p;rn=[];vn=[]
            for i,r in enumerate(self.rr):
                m,z,a=refs[h,r[:4]];d,s=r[4:];terms=[];offset=0;need=0
                for j in range(k+d,m+1):
                    w=prod(range(j-d+1,j+1))*comb(j-d,k)*pow(s,j-d-k,p)%p
                    if not w:continue
                    if j in z:offset=(offset+w*z[j])%p
                    else:
                        v=ids[h,r[:4],j];terms.append((v,w));need|=1<<v
                v=(offset+sum(w*self.values[j] for j,w in terms))%p
                q=tuple(a)
                for _ in range(d):q=tuple(j*q[j] for j in range(1,len(q)))
                assert v==sum(q[j]*comb(j,k)*s**(j-k) for j in range(k,len(q)))%p
                self.audit['residues']+=1;self.audit['symbolic']+=not need
                ex.append((offset,tuple(terms)));rn.append(need);vn.append(groups[h,r[:4]] if need else 0);truth[v]|=1<<i
            self.expr.append(tuple(ex));self.truth.append(tuple(truth));self.rneeds.append(tuple(rn));self.vneeds.append(tuple(vn))
        self.nc={};self.kc={}
    def need(self,S,a,mode):
        key=S,a,mode
        if key not in self.nc:
            mask=0;row=(self.rneeds if mode=='cell' else self.vneeds)[a]
            for i in bits(S):mask|=row[i]
            self.nc[key]=mask
        return self.nc[key]
    def known(self,S,B,a):
        key=S,B,a
        if key not in self.kc:
            masks=[0]*self.probes[a][2];p=len(masks)
            for i in bits(S):
                if self.rneeds[a][i]&~B:continue
                c,t=self.expr[a][i];v=(c+sum(w*self.values[j] for j,w in t))%p;masks[v]|=1<<i
            self.kc[key]=tuple(masks)
        return self.kc[key]
    def actual(self,S,a):return tuple(S&m for m in self.truth[a] if S&m)

class Planner:
    def __init__(self,d,mode):self.d=d;self.mode=mode;self.scans=0;self.memo={};self.opts={}
    def options(self,S,B,left):
        key=S,B,left
        if key not in self.opts:
            out=[]
            for a in range(len(self.d.probes)):
                self.scans+=1;need=self.d.need(S,a,self.mode)&~B;cost=need.bit_count()
                if cost>left:continue
                ch=self.d.actual(S,a)
                if len(ch)==1 and not cost:continue
                out.append((a,B|need,cost,ch))
            self.opts[key]=tuple(out)
        return self.opts[key]
    def plan(self,S,B,left,h,p):
        if S.bit_count()==1:return SCALE,-1
        if h==0:return 0,-1
        key=S,B,left,h,p
        if key not in self.memo:
            best=(0,0,-1)
            for a,b,cost,ch in self.options(S,B,left):
                v=-p*S.bit_count()*cost
                if h==1:v+=SCALE*sum(t.bit_count()==1 for t in ch)
                else:v+=sum(self.plan(t,b,left-cost,h-1,p)[0] for t in ch)
                if v>best[0] or (v==best[0] and cost<best[1]):best=v,cost,a
            self.memo[key]=(best[0],best[2])
        return self.memo[key]

class Free:
    def __init__(self,d):self.d=d;self.memo={};self.scans=0
    def plan(self,S,B,h):
        if S.bit_count()==1:return SCALE,-1
        if not h:return 0,-1
        key=S,B,h
        if key not in self.memo:
            best=(0,-1)
            for a in range(len(self.d.probes)):
                if self.d.need(S,a,'cell')&~B:continue
                self.scans+=1;ch=tuple(t for t in self.d.known(S,B,a) if t);assert sum(ch)==S
                if len(ch)<2:continue
                v=sum(self.plan(t,B,h-1)[0] for t in ch)
                if v>best[0]:best=v,a
            self.memo[key]=best
        return self.memo[key]

def interval(supports,m):
    lo=[0]*m;hi=[0]*m
    for s in supports:
        for k in s:hi[k]+=1
        if len(s)==1:lo[next(iter(s))]+=1
    return tuple(lo),tuple(hi)

def combine(opts,m):
    h={(0,)*m}
    for group in sorted(opts,key=len):
        nxt=set()
        for a in h:
            for b in group:
                nxt.add(tuple(min(2,x+y) for x,y in zip(a,b,strict=True)))
                if len(nxt)>LIMIT:return None
        h=nxt
    return h

def hist_vectors(expr,p):
    offset=tuple(e[0] for pair in expr for e in pair);rows=[dict(e[1]) for pair in expr for e in pair];vectors={offset}
    for j in sorted({j for r in rows for j in r}):
        col=tuple(r.get(j,0) for r in rows);nxt=set()
        for v in vectors:
            for t in range(p):
                nxt.add(tuple((a+t*b)%p for a,b in zip(v,col,strict=True)))
                if len(nxt)>LIMIT:return None
        vectors=nxt
    hs=set()
    for v in vectors:
        a=[0]*(p*p)
        for i in range(0,len(v),2):a[v[i]*p+v[i+1]]+=1
        hs.add(tuple(a))
    return hs

def support(e1,e2,p):
    return {a*p+b for a in ((e1[0],) if not e1[1] else range(p)) for b in ((e2[0],) if not e2[1] else range(p))}

def bound_pair(d,a,b):
    p=d.probes[a][2];m=p*p;ex=list(zip(d.expr[a],d.expr[b],strict=True));ss=[support(x,y,p) for x,y in ex]
    lo,hi=interval(ss,m);ind=sum(x==y==1 for x,y in zip(lo,hi,strict=True))
    ih=combine([{tuple(int(j==k) for j in range(m)) for k in s} for s in ss],m)
    if ih is not None:ind=max(ind,min(h.count(1) for h in ih))
    lo=[0]*m;hi=[0]*m;gs=[];fallback=checks=0
    ta={i:v for v,t in enumerate(d.truth[a]) for i in bits(t)};tb={i:v for v,t in enumerate(d.truth[b]) for i in bits(t)}
    for group in d.groups:
        h=hist_vectors(tuple(ex[i] for i in group),p)
        if h is None:
            fallback+=1;l,u=interval([ss[i] for i in group],m);gs=None
        else:
            l=tuple(min(v[j] for v in h) for j in range(m));u=tuple(max(v[j] for v in h) for j in range(m));actual=[0]*m
            for i in group:actual[ta[i]*p+tb[i]]+=1
            assert tuple(actual) in h;checks+=1
            if gs is not None:gs.append({tuple(min(2,x) for x in v) for v in h})
        for j in range(m):lo[j]+=l[j];hi[j]+=u[j]
    cou=max(ind,sum(x==y==1 for x,y in zip(lo,hi,strict=True)));ch=None if gs is None else combine(gs,m)
    if ch is not None:cou=max(cou,min(h.count(1) for h in ch))
    actual=sum((x&y).bit_count()==1 for x in d.truth[a] for y in d.truth[b]);assert 0<=ind<=cou<=actual
    return dict(ind=ind,cou=cou,actual=actual,ind_dp=ih is not None,cou_dp=ch is not None,fallback=fallback,group_checks=checks)

def pairs(d):
    out=[]
    for a,b in combinations(range(len(d.probes)),2):
        if d.probes[a][0]!=d.probes[b][0] or d.probes[a][2]!=d.probes[b][2]:continue
        cost=(d.need(d.full,a,'cell')|d.need(d.full,b,'cell')).bit_count()
        if 0<cost<=max(CAPS):out.append(dict(a=a,b=b,cost=cost,**bound_pair(d,a,b)))
    return out

def play(d,planner,free,ps,arm,cap,p):
    rows=[];decisions=[];mode='vector' if arm.endswith('vector') else 'cell'
    def emit(S,B,h):
        for i in bits(S):rows.append(dict(hidden=i,hit=S.bit_count()==1,cost=B.bit_count(),queries=2-h,remaining=S.bit_count()))
    if arm.endswith('pair'):
        incumbent=free.plan(d.full,0,2)[0];kind='ind' if arm=='independent_pair' else 'cou'
        best=max((r for r in ps if r['cost']<=cap),default=None,key=lambda r:(SCALE*r[kind]-p*d.n*r['cost'],-r['cost'],-r['a'],-r['b']))
        if best is not None and (cert:=SCALE*best[kind]-p*d.n*best['cost'])>incumbent:
            a,b=best['a'],best['b'];B=d.need(d.full,a,'cell')|d.need(d.full,b,'cell')
            for S in d.known(d.full,B,a):
                if not S:continue
                if S.bit_count()==1:emit(S,B,1);continue
                for T in d.known(S,B,b):
                    if T:emit(T,B,0)
            v=sum(SCALE*r['hit']-p*r['cost'] for r in rows);assert v>=cert>incumbent
            decisions.append(dict(certificate=cert,free=incumbent,realized=v,a=a,b=b))
    def walk(S,B,left,h):
        if S.bit_count()==1 or h==0:emit(S,B,h);return
        if arm.startswith('exact'):a=planner.plan(S,B,left,h,p)[1]
        elif arm=='free' or arm.endswith('pair'):a=free.plan(S,B,h)[1]
        else:
            best=None;n=S.bit_count()
            for i in range(len(d.probes)):
                cost=(d.need(S,i,mode)&~B).bit_count()
                if cost>left:continue
                counts=[m.bit_count() for m in d.known(S,B,i)];u=n-sum(counts)
                if not u and max(counts)==n:continue
                gain=(n*n-sum(v*(u+v) for v in counts)-u*(u+max(counts)))/(n*n)
                sure=sum(v==1 for v in counts)/n if u==0 else 0
                score=(sure if h==1 else gain)-p/SCALE*cost;q=(score,gain,-cost,-i)
                if best is None or q>best[0]:best=q,i
            a=best[1] if best is not None and best[0][0]>0 else free.plan(S,B,h)[1]
        if a==-1:emit(S,B,h);return
        need=d.need(S,a,mode)&~B;cost=need.bit_count();new=B|need;assert cost<=left
        ch=tuple(t for t in d.known(S,new,a) if t);assert ch==d.actual(S,a) and sum(ch)==S
        for t in ch:walk(t,new,left-cost,h-1)
    if not rows:walk(d.full,0,cap,2)
    assert len(rows)==d.n and len({r['hidden'] for r in rows})==d.n
    assert all(r['cost']<=cap and r['queries']<=2 and r['hit']==(r['remaining']==1) for r in rows)
    v=sum(SCALE*r['hit']-p*r['cost'] for r in rows)
    if arm.startswith('exact'):assert v==planner.plan(d.full,0,cap,2,p)[0]
    if arm.endswith('pair'):assert v>=free.plan(d.full,0,2)[0]
    return rows,decisions

def small_audit():
    rng=random.Random(1212);n=0
    for p in (2,3,5):
        for _ in range(40):
            e=tuple(tuple((rng.randrange(p),tuple((j,rng.randrange(1,p)) for j in range(2) if rng.randrange(2))) for _ in range(2)) for _ in range(3));hs=hist_vectors(e,p);ref=set()
            for z in product(range(p),repeat=2):
                counts=[0]*(p*p)
                for a,b in e:
                    v=[(c+sum(w*z[j] for j,w in t))%p for c,t in (a,b)];counts[v[0]*p+v[1]]+=1
                ref.add(tuple(counts))
            assert hs==ref;n+=1
    return n

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prior',nargs='+',required=True);ap.add_argument('--out',required=True);ap.add_argument('--decks',type=int,default=6);args=ap.parse_args();used=set()
    for f in args.prior:
        r=load(f);ds=[z[1] if len(z)==2 else z[2] for z in r['manifest']] if 'manifest' in r else [d['cards'] for d in r.get('decks',r.get('eval_decks',[]))]
        for cs in ds:
            for n,e in cs:used.add(graph_key((n,tuple(map(tuple,e)))))
    prior=len(used);ds=list(new_decks(used))[:args.decks];records=[];decisions=[];meta=[];pair_rows=[]
    for i,cs in ds:
        d=Deck(cs);pl={m:Planner(d,m) for m in ('vector','cell')};free=Free(d);ps=pairs(d);pair_rows.extend(dict(deck=i,**r) for r in ps)
        for cap,p,arm in product(CAPS,PRICES,ARMS):
            rr,dd=play(d,pl['vector' if arm.endswith('vector') else 'cell'],free,ps,arm,cap,p)
            records.extend(dict(deck=i,cap=cap,price=p,arm=arm,**r) for r in rr);decisions.extend(dict(deck=i,cap=cap,price=p,arm=arm,**x) for x in dd)
        meta.append(dict(deck=i,**d.audit,variables=len(d.values),pairs=len(ps),planner_scans={m:v.scans for m,v in pl.items()},free_scans=free.scans));print('deck',i,meta[-1],flush=True,file=sys.stderr)
        direct_coefficients.cache_clear();coefficients.cache_clear();known_coeff.cache_clear()
    groups=defaultdict(list)
    for r in records:groups[r['cap'],r['price'],r['arm']].append(r)
    summary=[]
    for (cap,p,arm),rr in sorted(groups.items()):
        n=len(rr);hits=sum(r['hit'] for r in rr);cost=sum(r['cost'] for r in rr)
        summary.append(dict(cap=cap,price=p,arm=arm,n=n,hits=hits,cost=cost,mean_cost=cost/n,utility_ticks=SCALE*hits-p*cost,mean_utility=(SCALE*hits-p*cost)/(SCALE*n)))
    for cap,p in product(CAPS,PRICES):
        z={r['arm']:r for r in summary if (r['cap'],r['price'])==(cap,p)};assert all(z['exact_cell']['utility_ticks']>=z[a]['utility_ticks'] for a in ARMS)
    out=dict(evidence='public finite development; logical coefficient-cell cost',scale=SCALE,manifest=ds,prior_graph_hashes=prior,small_audit=small_audit(),meta=meta,summary=summary,pairs=pair_rows,decisions=decisions,records=records,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());Path(args.out).write_text(json.dumps(out,separators=(',',':')))
if __name__=='__main__':main()

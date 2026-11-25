"""Exploratory CFH-11 refinement: couple unknown residues from shared coefficients."""
import argparse, json, hashlib
from collections import defaultdict
from pathlib import Path
from math import comb, prod
from functools import lru_cache
from certified import Safe, Online, Priced, Free, bits, SCALE, CAPS, PRICES, load, evaluate, allocate_min, immediate
from lazy_acquisition import known_coeff

LIMIT=8192

@lru_cache(maxsize=32768)
def histograms(p,offsets,columns):
    """All attainable residue histograms for an affine map over F_p.
    None means exceeded the computational cap; caller falls back soundly.
    """
    vectors={offsets}
    for col in columns:
        if not any(col):continue
        vectors={tuple((a+t*b)%p for a,b in zip(v,col,strict=True)) for v in vectors for t in range(p)}
        if len(vectors)>LIMIT:return None
    return frozenset(tuple(v.count(j) for j in range(p)) for v in vectors)

class Coupled(Safe):
    def __init__(self,o,free):
        super().__init__(o,free,'adaptive');self.hist_cache={};self.hist_attempts=0;self.fallback=0;self.improved=0
    def attainable(self,S,B,a,U):
        key=S,B,a
        if key in self.hist_cache:return self.hist_cache[key]
        self.hist_attempts+=1;o=self.o;card,k,p=o.probes[a];all_hist={(0,)*p}
        for ix,mask in enumerate(o.groups):
            inds=list(bits(U&mask))
            if not inds:continue
            assert not (B>>(card*o.ng+ix)&1)
            n,z=known_coeff(o.cards[card],o.keys[ix]);unknown=[j for j in range(n+1) if j not in z]
            def w(j,i):
                d,s=o.rr[i][4:]
                return prod(range(j-d+1,j+1))*comb(j-d,k)*pow(s,j-d-k,p)%p if j>=k+d else 0
            offsets=tuple(sum(w(j,i)*v for j,v in z.items())%p for i in inds)
            cols=tuple(tuple(w(j,i) for i in inds) for j in unknown)
            opts=histograms(p,offsets,cols)
            if opts is None:
                self.fallback+=1;self.hist_cache[key]=None;return None
            # Check cap during accumulation, rather than allocate unbounded sets.
            nxt=set()
            for a1 in all_hist:
                for a2 in opts:
                    nxt.add(tuple(x+y for x,y in zip(a1,a2,strict=True)))
                    if len(nxt)>LIMIT:
                        self.fallback+=1;self.hist_cache[key]=None;return None
            all_hist=nxt
        result=tuple(sorted(all_hist));assert all(sum(z)==U.bit_count() for z in result)
        self.hist_cache[key]=result;return result
    def lower(self,S,B,a,h):
        key=S,B,a,h
        if key in self.bounds:return self.bounds[key]
        o=self.o;cells=o.known(S,B,a);U=S&~sum(cells);u=U.bit_count();counts=tuple(x.bit_count() for x in cells)
        hist=self.attainable(S,B,a,U)
        def minimize(profiles):
            loose=allocate_min(profiles,u)
            if hist is None:return loose
            tight=min(sum(profile[z] for profile,z in zip(profiles,v,strict=True)) for v in hist)
            assert tight>=loose
            return tight
        v=minimize(tuple(tuple(int(k+z==1) for z in range(u+1)) for k in counts))
        loose=immediate(counts,u)
        if h==2:
            new=B|o.need(S,a);profiles=[]
            for K,k in zip(cells,counts,strict=True):
                guarantee=0
                if K:
                    for q in range(len(o.probes)):
                        self.second_scans+=1
                        if o.need(K|U,q)&~new:continue
                        ks=[m.bit_count() for m in o.known(K,B,q)]
                        guarantee=max(guarantee,sum(x==1 for x in ks)-(k-sum(ks)))
                profiles.append(tuple(max(int(k+z==1),guarantee-z,0) for z in range(u+1)))
            profiles=tuple(profiles);v=max(v,minimize(profiles));loose=max(loose,allocate_min(profiles,u))
        assert v>=loose;self.improved+=v>loose;self.bounds[key]=v;return v

def audit_all(o,oracle,safe):
    # Offline audit all candidate certificates, including unselected actions.
    # Free continuation uses evaluator truth restricted to covered queries only.
    @lru_cache(maxsize=None)
    def free_hits(S,B,h):
        if S.bit_count()==1:return 1
        if not h:return 0
        return max((sum(m.bit_count()==1 for m in (S&t for t in masks)) for a,masks in enumerate(oracle.truth) if not o.need(S,a)&~B),default=0)
    counts=defaultdict(int)
    for (S,B,a,h),lower in safe.bounds.items():
        new=B|o.need(S,a);cells=o.known(S,B,a);U=S&~sum(cells)
        truth=oracle.truth[a];z=tuple((U&m).bit_count() for m in truth)
        hist=safe.hist_cache.get((S,B,a))
        if hist is not None:assert z in hist;counts['hist_coverage']+=1
        actual=sum(free_hits(S&m,new,h-1) for m in truth if S&m)
        assert 0<=lower<=actual
        counts['candidate_bounds']+=1;counts['tight']+=lower==actual;counts['zero_lower_positive_actual']+=lower==0 and actual>0
    return dict(counts)

def main():
    pa=argparse.ArgumentParser();pa.add_argument('source');pa.add_argument('--out',required=True);a=pa.parse_args();r=load(a.source)
    records=[];decisions=[];meta=[]
    for i,raw in r['manifest']:
        cs=tuple((n,tuple(map(tuple,e))) for n,e in raw);o=Online(cs,2);oracle=Priced(o);free=Free(o);s=Coupled(o,free)
        for cap in CAPS:
            for p in PRICES:
                rr,dd=evaluate(o,oracle,free,s,cap,p)
                records.extend(dict(deck=i,cap=cap,price=p,arm='coupled',**x) for x in rr)
                decisions.extend(dict(deck=i,cap=cap,price=p,arm='coupled',**x) for x in dd)
        meta.append(dict(deck=i,scans=s.scans,second_scans=s.second_scans,hist_attempts=s.hist_attempts,fallback=s.fallback,improved_bounds=s.improved,**audit_all(o,oracle,s)))
        oracle.options.cache_clear();oracle.opt.cache_clear();free.plan.cache_clear();histograms.cache_clear()
        print('deck',i,meta[-1],flush=True)
    grouped=defaultdict(list)
    for x in records:grouped[x['cap'],x['price']].append(x)
    summary=[]
    for (cap,p),rr in sorted(grouped.items()):
        n=len(rr);hits=sum(x['hit'] for x in rr);cost=sum(x['cost'] for x in rr)
        summary.append(dict(cap=cap,price=p,hits=hits,n=n,mean_cost=cost/n,cost=cost,utility_ticks=SCALE*hits-p*cost,mean_utility=(SCALE*hits-p*cost)/(SCALE*n)))
    out=dict(evidence='exploratory public same-deck refinement',source_receipt_sha256=hashlib.sha256(Path(a.source).read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),meta=meta,summary=summary,records=records,decisions=decisions)
    Path(a.out).write_text(json.dumps(out,separators=(',',':')))
if __name__=='__main__':main()

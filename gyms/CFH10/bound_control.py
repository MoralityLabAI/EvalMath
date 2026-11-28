"""CFH-10 exploratory upper-bound pruning for paid actions."""
import argparse, gzip, json, hashlib
from pathlib import Path
from functools import cache
from collections import defaultdict
from cost_frontier import Online, Priced, Free, bits, SCALE, PRICES, CAPS

@cache
def upper_hits(counts,u,h):
    """Max possible singleton leaves over all allocations of unknown replies."""
    if not counts:
        return 0 if u==0 else -10**6
    def leaf_bound(n):
        if n<=1:return n
        leaves=5**h
        return n if n<=leaves else leaves-1
    return max(leaf_bound(counts[0]+a)+upper_hits(counts[1:],u-a,h) for a in range(u+1))

def evaluate(o,oracle,free,cap,p,arm):
    records=[];decisions=[];prunes=0;paid_candidates=0
    def walk(S,B,left,h):
        nonlocal prunes,paid_candidates
        n=S.bit_count();a=-1
        if n>1 and h:
            incumbent,free_a=free.plan(S,B,h)
            x,acts,g=o.features(S,B,left,h);candidates=[]
            for idx,probe in enumerate(acts):
                need=o.need(S,probe)&~B;cost=need.bit_count()
                if not cost:continue
                paid_candidates+=1
                counts=tuple(m.bit_count() for m in o.known(S,B,probe));u=n-sum(counts)
                bound=SCALE*upper_hits(counts,u,h-1)-p*n*cost
                # Independent check using privileged offline value; never used to choose.
                truth=tuple(S&m for m in oracle.truth[probe] if S&m)
                q=oracle.q(S,B,B|need,left-cost,truth,h,p);assert q<=bound
                if bound<=incumbent:
                    prunes+=1;continue
                score=g[idx][0]-(p/SCALE)*cost
                if arm=='guarded_greedy':rank=(score,bound,*g[idx])
                else:rank=(bound,score,*g[idx])
                candidates.append((rank,probe))
            a=free_a
            if candidates:
                rank,probe=max(candidates)
                if arm=='bound_optimistic' or rank[0]>0:a=probe
            if a!=-1:
                need=o.need(S,a)&~B;cost=need.bit_count();assert cost<=left
                b=B|need;o.purchase(need);cells=o.known(S,b,a)
                assert cells==tuple(S&m for m in oracle.truth[a]) and sum(cells)==S
                q=oracle.q(S,B,b,left-cost,tuple(t for t in cells if t),h,p)
            else:q=0
            decisions.append(dict(n=n,h=h,action=a,regret=oracle.opt(S,B,left,h,p)-q))
            if a!=-1:
                for t in cells:
                    if t:walk(t,b,left-cost,h-1)
                return
        for i in bits(S):records.append(dict(hidden=i,hit=n==1,cost=B.bit_count(),queries=2-h,remaining=n))
    walk(o.full,0,cap,2);assert len(records)==o.n and len({r['hidden'] for r in records})==o.n
    assert oracle.opt(o.full,0,cap,2,p)-sum(SCALE*r['hit']-p*r['cost'] for r in records)==sum(d['regret'] for d in decisions)
    return records,decisions,prunes,paid_candidates

def main():
    pa=argparse.ArgumentParser();pa.add_argument('source');pa.add_argument('--out',required=True);args=pa.parse_args()
    path=Path(args.source);raw=path.read_bytes();r=json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
    out=[];dec=[];meta=[]
    for split,i,cards in r['manifest']:
        if split!='shift':continue
        cs=tuple((n,tuple(map(tuple,es))) for n,es in cards);o=Online(cs,2);oracle=Priced(o);free=Free(o)
        for cap in CAPS:
            for p in PRICES:
                for arm in ('guarded_greedy','bound_optimistic'):
                    rr,dd,prunes,candidates=evaluate(o,oracle,free,cap,p,arm)
                    out.extend(dict(deck=i,cap=cap,price=p,arm=arm,**x) for x in rr)
                    dec.extend(dict(deck=i,cap=cap,price=p,arm=arm,**x) for x in dd)
                    meta.append(dict(deck=i,cap=cap,price=p,arm=arm,prunes=prunes,paid_candidates=candidates))
        oracle.options.cache_clear();oracle.opt.cache_clear();free.plan.cache_clear();upper_hits.cache_clear()
    groups=defaultdict(list)
    for x in out:groups[x['cap'],x['price'],x['arm']].append(x)
    summary=[]
    for (cap,p,arm),rr in sorted(groups.items()):
        n=len(rr);hits=sum(x['hit'] for x in rr);cost=sum(x['cost'] for x in rr)
        summary.append(dict(cap=cap,price=p,arm=arm,n=n,hits=hits,cost=cost,mean_cost=cost/n,mean_utility=(SCALE*hits-p*cost)/(SCALE*n)))
    Path(args.out).write_text(json.dumps(dict(evidence='exploratory public development on same decks',source_receipt_sha256=hashlib.sha256(raw).hexdigest(),summary=summary,records=out,decisions=dec,meta=meta),separators=(',',':')))
if __name__=='__main__':main()

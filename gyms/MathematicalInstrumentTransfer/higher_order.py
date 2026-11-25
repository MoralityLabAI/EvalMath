"""MIT-04: exact pairwise-marginal aliasing search with integer multiplicities."""
from functools import lru_cache
from itertools import combinations,product
from random import Random
from pathlib import Path
import json,hashlib

PAT=tuple(product((0,1),repeat=3))

def marginals(counts):
    return tuple(tuple(sum(v for p,v in zip(PAT,counts) if (p[i],p[j])==bits) for bits in product((0,1),repeat=2)) for i,j in combinations(range(3),2))

def optimum(counts,budget):
    @lru_cache(None)
    def v(c,a,b):
        if b<=0 or not any(c):return 0
        best=min(sum(c),b)
        if best==sum(c):return best
        for i,k in enumerate(c):
            if k:
                d=c[:i]+(k-1,)+c[i+1:];best=max(best,1+v(d,a,b-1))
        for j in range(3):
            if a>>j&1 and b>=2:
                best=max(best,sum(v(tuple(n if p[j]==bit else 0 for p,n in zip(PAT,c)),a^(1<<j),b-1) for bit in (0,1)))
        return best
    return v(tuple(counts),7,budget)

def find():
    r=Random(51103)
    for t in range(1000):
        a=tuple(r.randrange(1,5) for _ in PAT)
        b=tuple(n+(-1)**sum(p) for n,p in zip(a,PAT))
        assert sum(a)==sum(b) and marginals(a)==marginals(b)
        for budget in (3,4,5):
            x,y=optimum(a,budget),optimum(b,budget)
            if x!=y:
                return dict(patterns=PAT,counts_a=a,counts_b=b,budget=budget,worlds=sum(a),pairwise_marginals=marginals(a),optimum_a=x,optimum_b=y,search_index=t)
    return None

if __name__=='__main__':
    r=find();assert r is not None;print(json.dumps(r,indent=2));Path(__file__).with_name('higher_order_result.json').write_text(json.dumps(r,indent=2)+'\n')

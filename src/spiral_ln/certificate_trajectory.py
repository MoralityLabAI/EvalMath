"""CTS-01: exact rational polygon certificate/trajectory separation."""
from collections import deque
from fractions import Fraction as F
from itertools import combinations
from random import Random
import json


def dot(a, b):
    return sum((x*y for x, y in zip(a, b, strict=True)), F(0))


def solve(a, b, u, v):
    det = a[0]*b[1] - a[1]*b[0]
    if det == 0:
        return None
    return (F(u*b[1]-a[1]*v, det), F(a[0]*v-u*b[0], det))


def instance(m, seed=0):
    if m < 1:
        raise ValueError('m must be positive')
    rng = Random(seed)
    while True:
        a,b,c,d = [rng.randint(-5,5) for _ in range(4)]
        det = a*d-b*c
        if det:
            break
    t = (rng.randint(-9,9),rng.randint(-9,9))
    def transform(v):
        x,y=v
        return (a*x+b*y+t[0],c*x+d*y+t[1])
    def covector(v):
        x,y=v
        return (F(d*x-c*y,det),F(-b*x+a*y,det))
    rows=[]
    for i in range(-m,m):
        for sign in (-1,1):
            normal=covector((2*i+1,sign))
            rows.append((normal,F(i*(i+1)+m*m)+dot(normal,t)))
    rng.shuffle(rows)
    vertices=[transform((i,sign*(m*m-i*i))) for i in range(-m,m+1)
              for sign in ((1,) if abs(i)==m else (-1,1))]
    return rows,covector((1,0)),vertices,transform((-m,0)),transform((m,0))


def verify(rows, c, x, support):
    if len(x)!=2 or any(i<0 or i>=len(rows) or w<0 for i,w in support.items()):
        return False
    return (all(dot(a,x)<=b for a,b in rows)
            and all(sum((w*rows[i][0][j] for i,w in support.items()),F(0))==c[j] for j in range(2))
            and sum((w*rows[i][1] for i,w in support.items()),F(0))==dot(c,x))


def recover(rows,c):
    """Enumerate two-row dual supports. Charges all pair trials; specialized 2D oracle."""
    best=None
    trials=0
    for i,j in combinations(range(len(rows)),2):
        trials+=1
        a,u=rows[i]; b,v=rows[j]
        w=solve((a[0],b[0]),(a[1],b[1]),*c)
        if w is None or min(w)<0:
            continue
        bound=w[0]*u+w[1]*v
        if best is None or bound<best[0]:
            best=(bound,i,j,w)
    if best is None:
        raise ValueError('no dual support')
    _,i,j,w=best
    x=solve(rows[i][0],rows[j][0],rows[i][1],rows[j][1])
    support={i:w[0],j:w[1]}
    if x is None or not verify(rows,c,x,support):
        raise ValueError('certificate recovery failed')
    return x,support,trials


def distance(rows,vertices,start,goal):
    active=[{i for i,(a,b) in enumerate(rows) if dot(a,v)==b} for v in vertices]
    if not all(len(s)==2 for s in active) or not all(sum(i in s for s in active)==2 for i in range(len(rows))):
        raise ValueError('invalid incidence')
    q=deque([(vertices.index(start),0)]); seen={vertices.index(start)}
    while q:
        i,k=q.popleft()
        if vertices[i]==goal:
            return k
        for j,s in enumerate(active):
            if j not in seen and s & active[i]:
                seen.add(j); q.append((j,k+1))
    raise ValueError('disconnected')


def run(ms=(1,2,4,8,16,32), seeds=(11,23,47)):
    out=[]
    for m in ms:
        for seed in seeds:
            rows,c,vs,s,t=instance(m,seed)
            x,w,trials=recover(rows,c)
            dist=distance(rows,vs,s,t)
            assert len(set(vs))==len(rows)==4*m
            assert all(all(dot(a,v)<=b for a,b in rows) for v in vs)
            assert dist==2*m and tuple(x)==t and dot(c,t)-dot(c,s)==2*m
            assert verify(rows,c,x,w) and not verify(rows,c,s,w)
            assert not verify(rows,c,x,{i:-v for i,v in w.items()})
            out.append(dict(m=m,seed=seed,facets=len(rows),edge_distance=dist,
                            face2_distance=1,support=len(w),pair_trials=trials,
                            gap=str(dot(c,t)-dot(c,s)),local_K8=int(dist<=8),
                            certified=1,invalid_rejected=1))
    return out


if __name__=='__main__':
    print(json.dumps(run(),indent=2))

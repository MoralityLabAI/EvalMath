"""CTS-03: development-only planted LP support recovery; exact integer verifier.
Requires numpy, scipy, sympy. Run: OPENBLAS_NUM_THREADS=1 python cts03.py
"""
import json, hashlib, time
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from sympy import ZZ
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.exceptions import DMNonInvertibleMatrixError

DIMS=(4,8,16,32); FAMILIES=('dense','sparse','correlated')
TRAIN=16; DEV=12; SEED=38003
ARMS=('static','greedy','recurrent','frozen','sham','highs','oracle')

def generate(d,f,seed):
    r=np.random.default_rng(seed); x=r.integers(-5,6,d)
    if not x.any(): x[0]=1
    bias=r.integers(-3,4,d)
    def oriented():
        while True:
            a=r.integers(-5,6,d)
            if f=='sparse': a*=r.random(d)<min(1,4/d)
            if f=='correlated': a+=4*bias
            k=int(a@x)
            if k: return a if k>0 else -a
    while True:
        A=np.stack([oriented() for _ in range(d)])
        if np.linalg.matrix_rank(A)==d: break
    rows=list(A); rhs=list(A@x)
    for _ in range(3*d):
        a=oriented(); rows.append(a); rhs.append(a@x+r.integers(1,11))
    while True:
        B=r.integers(-5,6,(d,d))
        if np.linalg.matrix_rank(B)==d: break
    for a in B:
        v=abs(a@x)+r.integers(1,11); rows.extend((a,-a)); rhs.extend((v,v))
    A=np.array(rows,dtype=np.int64); b=np.array(rhs,dtype=np.int64)
    scale=r.integers(1,8,len(b)); A=A*scale[:,None]; b=b*scale
    c=A[:d].T@r.integers(1,8,d)
    p=r.permutation(len(b)); gold=np.flatnonzero(p<d)
    return A[p],b[p],c,gold

def dm(a): return DomainMatrix.from_list(np.asarray(a).tolist(),ZZ)
def solve(a,b):
    N,q=dm(a).solve_den(dm(np.asarray(b)[:,None])); q=int(q)
    v=np.array([int(z[0]) for z in N.to_list()],dtype=object)
    return (v if q>0 else -v),abs(q)

def verify(A,b,c,S):
    d=len(c); S=np.array(S,dtype=int)
    if len(S)!=d or len(set(S))!=d or np.any(S<0) or np.any(S>=len(b)): return False
    try: x,q=solve(A[S],b[S]); y,t=solve(A[S].T,c)
    except DMNonInvertibleMatrixError: return False
    AA=A.astype(object); bb=b.astype(object); cc=c.astype(object)
    return bool(q>0 and t>0 and all(y>=0) and all(AA@x<=bb*q) and
                np.array_equal(AA[S].T@y,cc*t) and (cc@x)*t==(bb[S]@y)*q)

def base(A,b,c):
    norm=np.linalg.norm(A,axis=1); U=A/norm[:,None]; C=c/np.linalg.norm(c)
    margin=b/norm; margin=margin/(np.median(margin)+1e-12)
    return U,C,np.log1p(margin)

def features(U,C,margin,S):
    if len(S):
        # SVD avoids projecting onto arbitrary QR completion for dependent rows.
        Q,s,_=np.linalg.svd(U[S].T,full_matrices=False); Q=Q[:,s>1e-10]
        R=C-Q@(Q.T@C); rem=np.sqrt(np.maximum(0,1-np.sum((U@Q)**2,axis=1)))
    else: R=C; rem=np.ones(len(U))
    cos=U@C; dy=U@R/(np.linalg.norm(R)+1e-12)
    return np.column_stack((np.ones(len(U)),cos,cos**2,margin,margin**2,dy,dy**2,rem,dy*rem))

def fit(X,y):
    X=np.concatenate(X); y=np.concatenate(y); w=np.zeros(X.shape[1]); wt=np.where(y,0.5/y.mean(),0.5/(1-y.mean()))
    for _ in range(250):
        z=np.clip(X@w,-40,40); p=1/(1+np.exp(-z)); w-=0.12*((X.T@(wt*(p-y)))/len(y)+0.003*w)
    return w

def train():
    xs=[]; ys=[]; xr=[]; yr=[]
    for j,f in enumerate(FAMILIES):
        for d in DIMS:
            for i in range(TRAIN):
                seed=SEED+100000*j+1000*d+i; A,b,c,gold=generate(d,f,seed); U,C,m=base(A,b,c)
                y=np.isin(np.arange(len(b)),gold); xs.append(features(U,C,m,[])); ys.append(y)
                r=np.random.default_rng(seed+7000000)
                for k in [0,d//4,d//2,3*d//4]:
                    S=r.choice(gold,k,replace=False).tolist(); mask=np.ones(len(b),bool); mask[S]=False
                    xr.append(features(U,C,m,S)[mask]); yr.append(y[mask])
    return fit(xs,ys),fit(xr,yr)

def select(arm,U,C,m,d,ws,wr,r):
    S=[]; F0=features(U,C,m,[]); n=len(U)
    if arm=='static': return np.argsort(-(F0@ws),kind='stable')[:d].tolist(),n
    for k in range(d):
        X=features(U,C,m,S)
        if arm=='greedy': score=X[:,5]*X[:,7]
        elif arm=='frozen': score=F0@wr
        elif arm=='sham':
            X[:,5:]=X[r.permutation(n),5:]; score=X@wr
        else: score=X@wr
        score[S]=-np.inf; S.append(int(np.argmax(score)))
    return S,n*d

def one(d,f,seed,ws,wr):
    A,b,c,g=generate(d,f,seed); U,C,m=base(A,b,c); out={}; r=np.random.default_rng(seed+8000000)
    for arm in ARMS:
        t=time.perf_counter(); nit=None; status=None
        if arm=='highs':
            res=linprog(-c.astype(float),A_ub=A,b_ub=b,bounds=[(None,None)]*d,method='highs')
            status=int(res.status); nit=int(res.nit); nscore=0
            S=np.argsort((b-A@res.x)/np.linalg.norm(A,axis=1))[:d].tolist() if res.success else []
        elif arm=='oracle': S=g.tolist(); nscore=0
        else: S,nscore=select(arm,U,C,m,d,ws,wr,r)
        dt=time.perf_counter()-t; t=time.perf_counter(); ok=verify(A,b,c,S); vt=time.perf_counter()-t
        out[arm]={'recall':len(set(S)&set(g.tolist()))/d,'verified':int(ok),'proposal':S,'row_scores':nscore,'solver_iterations':nit,'solver_status':status,'selection_seconds':dt,'verify_seconds':vt}
    assert out['oracle']['verified']==1
    assert all(v['verified']==int(set(v['proposal'])==set(g.tolist())) for v in out.values())
    bad=g.copy(); bad[0]=next(i for i in range(len(b)) if i not in g)
    assert not verify(A,b,c,bad)
    return {'seed':seed,'dimension':d,'family':f,'rows':len(b),'gold':g.tolist(),'arms':out}

def main():
    root=Path(__file__).resolve().parent; t=time.perf_counter(); ws,wr=train(); train_seconds=time.perf_counter()-t
    rows=[one(d,f,SEED+100000*j+1000*d+100+i,ws,wr) for j,f in enumerate(FAMILIES) for d in DIMS for i in range(DEV)]
    def summary(R):
        return {a:{'verified':sum(z['arms'][a]['verified'] for z in R),'mean_recall':sum(z['arms'][a]['recall'] for z in R)/len(R),'mean_row_scores':sum(z['arms'][a]['row_scores'] for z in R)/len(R),'selection_seconds':sum(z['arms'][a]['selection_seconds'] for z in R),'verify_seconds':sum(z['arms'][a]['verify_seconds'] for z in R)} for a in ARMS}
    result={'schema':'CTS-03/dev-v1','train_roots':len(FAMILIES)*len(DIMS)*TRAIN,'dev_roots':len(rows),'train_seconds':train_seconds,'weights':{'static':ws.tolist(),'recurrent':wr.tolist()},'summary':summary(rows),'by_dimension':{str(d):summary([z for z in rows if z['dimension']==d]) for d in DIMS},'by_family':{f:summary([z for z in rows if z['family']==f]) for f in FAMILIES},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'roots':rows}
    (root/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    pilot={'schema_version':1,'experiment_id':'CTS-03','independent_unit':'generated LP root within generator/dimension stratum; conditional on one training fit','alpha':'1/20','scientific_min_effect':'1/10','target_effect':'1/5','measurement_resolution':'1/32','sham_quantile':'19/20','sham_confidence':'19/20','planned_comparisons':5,'confirm_units_planned':192,'pilot_from_development_only':True,'heldout_sealed':False,'units_independent':False,'pilot':[]}
    for z in rows:
        from fractions import Fraction
        a=z['arms']; F=lambda k:Fraction(a[k]['recall'])
        pilot['pilot'].append({'unit_id':str(z['seed']),'paired_effect':str(F('recurrent')-F('frozen')),'sham_effects':[str(F('sham')-F('frozen'))]})
    (root/'pilot.json').write_text(json.dumps(pilot,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('roots','by_family','by_dimension')},indent=2))

if __name__=='__main__': main()

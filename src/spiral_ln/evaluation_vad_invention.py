"""VAD-04A: supplied-free XOR cache invention and independent validation."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import comb, log, sqrt
from pathlib import Path
from random import Random
import json
from .evaluation_vad_lookahead import cost, build, mask

D,H,P=36,1024,64
REGIMES=('clean','noise2','noise4','structured','null','multi','shifted')
SPLITS={'cal':(400000,24),'test':(500000,48)}
METHODS=('empty','intersections','frequency','prefix','hybrid','hybrid_pair','privileged_pair')


def roots(rng,w,motif,forbidden,n,exclude=()):
    choices=[i for i in range(D) if not ((motif|forbidden)>>i&1)]
    seen=set(exclude); out=[]
    blocked=sum(t.bit_count()==w and t&motif==motif and not t&forbidden for t in seen)
    assert n<=comb(len(choices),w-motif.bit_count())-blocked
    while len(out)<n:
        t=motif|mask(rng.sample(choices,w-motif.bit_count()))
        if t not in seen: seen.add(t); out.append(t)
    return tuple(out)


def family(seed,regime):
    rng=Random(seed); w=rng.choice((9,10,11)); k=rng.choice((3,4,5,6)); p=rng.sample(range(D),D)
    m1,e1,m2,e2=map(mask,(p[:k],p[k:k+3],p[k+3:2*k+3],p[2*k+3:2*k+6]))
    # Privileged comparator alone gets this candidate pool; invention arms see only roots.
    pair=tuple(sorted((mask(p[:k//2])|e1,mask(p[k//2:k])|e1)))
    r=Random(seed+1_000_000)
    if regime=='null': dev=roots(r,w,0,0,8)
    elif regime=='multi':
        a=roots(r,w,m1,e1,4); dev=a+roots(r,w,m2,e2,4,a)
    else:
        k_noise={'noise2':2,'noise4':4,'structured':3}.get(regime,0)
        a=roots(r,w,m1,e1,8-k_noise)
        dev=a+(roots(r,w,m2,e2,k_noise,a) if regime=='structured' else roots(r,w,0,0,k_noise,a))
    dev=list(dev); r.shuffle(dev); dev=tuple(dev)
    r=Random(seed+2_000_000); n=H+P
    if regime=='null': held=roots(r,w,0,0,n,dev)
    elif regime=='shifted': held=roots(r,w,m2,e2|m1,n,dev)
    elif regime=='multi':
        a=roots(r,w,m1,e1,n//2,dev); held=a+roots(r,w,m2,e2,n-len(a),dev+a)
        held=list(held); r.shuffle(held); held=tuple(held)
    else: held=roots(r,w,m1,e1,n,dev)
    assert len(set(dev+held))==8+n
    return dev,held[:P],held[P:],(m1,m2),pair,w,k


def proposals(dev,method):
    if method=='empty': return (),0
    masks=set(); work=0
    if method in ('intersections','hybrid','hybrid_pair'):
        for a,b in combinations(dev,2): masks.add(a&b); work+=1
    if method in ('frequency','prefix','hybrid','hybrid_pair'):
        counts=[sum((t>>i)&1 for t in dev) for i in range(D)]; work+=D*len(dev)
        if method in ('frequency','hybrid','hybrid_pair'):
            for q in (4,5,6,7,8):
                masks.add(mask(i for i,c in enumerate(counts) if c>=q)); work+=D
        if method in ('prefix','hybrid','hybrid_pair'):
            ranked=sorted(range(D),key=lambda i:(-counts[i],i)); work+=D*D.bit_length()
            a=0
            for i,x in enumerate(ranked[:10],1):
                a|=1<<x; work+=1
                if i>=2: masks.add(a)
    return tuple(sorted(a for a in masks if 2<=a.bit_count()<=12)),work


def select(dev,method,pair):
    if method=='empty': return (),0,0
    if method=='privileged_pair':
        libs=[(),(pair[0],),(pair[1],),pair]; work=3; best=(); val=0
        for lib in libs[1:]:
            work+=(2*len(dev)+1 if len(lib)==1 else 4*len(dev)+6)
            v=H*sum(cost(t)-cost(t,lib) for t in dev)-len(dev)*build(lib)
            if (-v,len(lib),lib)<(-val,len(best),best): best,val=lib,v
        return best,work,len(libs)-1
    cand,work=proposals(dev,method); scores={():0}; best=()
    def score(lib):
        nonlocal work,best
        if lib not in scores:
            work+=(2*len(dev)+1 if len(lib)==1 else 4*len(dev)+6)
            scores[lib]=H*sum(cost(t)-cost(t,lib) for t in dev)-len(dev)*build(lib)
        if (-scores[lib],len(lib),lib)<(-scores[best],len(best),best): best=lib
    for a in cand: score((a,))
    if method=='hybrid_pair':
        top=sorted(cand,key=lambda a:(-scores[(a,)],a))[:6]
        work+=len(cand)*max(1,len(cand).bit_length())
        for a,b in combinations(top,2): score(tuple(sorted((a,b))))
    return best,work,len(scores)-1


def evaluate(split):
    base,n=SPLITS[split]; rows=[]
    for ri,regime in enumerate(REGIMES):
        for i in range(n):
            seed=base+(0 if regime=='shifted' else ri*1000)+i
            dev,probe,held,motifs,pair,w,k=family(seed,regime)
            baseline=sum(cost(t) for t in held+probe)
            for method in METHODS:
                lib,work,queries=select(dev,method,pair)
                deployment=sum(cost(t,lib) for t in held+probe)
                total=work+build(lib)+deployment
                # A separately declared validation slice is proved with primitives.
                # Score only the frozen candidate; no replacement candidates after validation.
                # Charge per residual probe. Abstention cannot recover sunk discovery work.
                vals=[cost(t)-cost(t,lib) for t in probe]
                val_work=P*(1<<len(lib)) if lib else 0
                # Empirical deployment gate and a Hoeffding-inspired sensitivity gate.
                # Without-replacement/mixed generators: latter is a conservative heuristic,
                # not a claimed iid confidence guarantee for this synthetic sample.
                mean=sum(vals)/P; lower=mean-2*w*sqrt(log(20)/(2*P))
                for gate,allowed in [('none',bool(lib)),('empirical',bool(lib) and H*mean>work+build(lib)+val_work),('margin',bool(lib) and H*lower>work+build(lib)+val_work)]:
                    final=lib if allowed else ()
                    if gate=='none': charged=total
                    else: charged=work+val_work+build(final)+sum(cost(t) for t in probe)+sum(cost(t,final) for t in held)
                    rows.append(dict(seed=seed,regime=regime,method=method,gate=gate,baseline=baseline,total=charged,work=work,validation_work=0 if gate=='none' else val_work,construction=build(final),lib=final,original=lib,queries=queries,exact_motif=any(a in motifs for a in final) if regime not in ('null','shifted') else False,selected=bool(final),width=k,weight=w))
    return rows


def summary(rows):
    out=[]
    for key in sorted({(r['regime'],r['method'],r['gate']) for r in rows}):
        rr=[r for r in rows if (r['regime'],r['method'],r['gate'])==key]
        b=sum(r['baseline'] for r in rr); t=sum(r['total'] for r in rr)
        out.append(dict(regime=key[0],method=key[1],gate=key[2],n=len(rr),baseline=b,total=t,gain=float(Fraction(b,t)),profitable=sum(r['total']<r['baseline'] for r in rr),selected=sum(r['selected'] for r in rr),motif=sum(r['exact_motif'] for r in rr)))
    return out


def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    cal=evaluate('cal'); eligible=[(m,g) for m in METHODS if m!='privileged_pair' for g in ('none','empirical','margin')]
    choice=min(eligible,key=lambda k:sum(r['total'] for r in cal if (r['method'],r['gate'])==k))
    freeze=dict(protocol='VAD-04A',split=SPLITS,choice=choice,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),calibration=summary(cal))
    (a.out/'vad_04a_freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    test=evaluate('test'); report=dict(**freeze,test=summary(test),records=test)
    (a.out/'vad_04a_full.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('CHOSEN',choice,flush=True)
    for r in report['test']:
        if (r['method'],r['gate']) in (choice,('privileged_pair','none'),('empty','none')): print(r,flush=True)

if __name__=='__main__': main()

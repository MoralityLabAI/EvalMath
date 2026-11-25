"""VAD-09A: exact two-mode, finite-horizon belief-state control over a frozen policy menu."""
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from functools import lru_cache
from pathlib import Path
import argparse,json
import verify_vad_stopping as a

W=a.prior(a.WEIGHTS['base'])
Q=(a.P,(F(1,4),)*4+(F(3,4),))
HAZARD=F(1,20)
MENU=('cut0','cut1','cut2','cut4','cut8','cut16','cut24','p0','p25','p50','p75','p100')

def action(name):
    if name.startswith('cut'):
        k=int(name[3:]); return lambda n,j:n<k
    p=F(int(name[1:]),100)
    v=a.bellman(tuple((1-p)*w for w in W)+tuple(p*w for w in W),Q[0]+Q[1],times=a.TIMES*2)
    return lambda n,k:v(n,k)[1]


def distribution(prior,channel,act):
    """Forward exact terminal-record probabilities with all compatible histories counted."""
    live={(0,0,i):w for i,w in enumerate(prior) if w}; out=defaultdict(F)
    for n in range(a.H+1):
        nxt=defaultdict(F)
        for (_,k,i),w in live.items():
            if n==a.H or not act(n,k): out[n,k,False]+=w; continue
            if a.TIMES[i]==n+1: out[n+1,k,True]+=w; continue
            for b,q in ((0,1-channel[i]),(1,channel[i])): nxt[n+1,k+b,i]+=w*q
        live=nxt
    assert sum(out.values())==1
    return dict(out)


def utility(rec):
    n,k,hit=rec; return (a.reward(n) if hit else 0)-a.COST*n

@lru_cache(None)
def model(menu=MENU,prior=W,channels=Q):
    result={}
    for name in menu:
        act=action(name); d0,d1=[distribution(prior,q,act) for q in channels]
        r0,r1=[sum(prob*utility(rec) for rec,prob in d.items()) for d in (d0,d1)]
        # Merge records with equal likelihood ratio; immediate expected utility is separate.
        grouped=defaultdict(lambda:[F(0),F(0)])
        for rec in sorted(set(d0)|set(d1)):
            x,y=d0.get(rec,F(0)),d1.get(rec,F(0))
            if not x and not y: continue
            l=grouped[y/x if x else None]; l[0]+=x; l[1]+=y
        result[name]=(r0,r1,tuple(tuple(x) for x in grouped.values()))
    return result


def envelope(lines):
    """Upper hull of affine functions (intercept,slope,label), restricted to [0,1]."""
    slopes={}
    for b,m,name in lines:
        old=slopes.get(m)
        if old is None or b>old[0] or (b==old[0] and name<old[1]): slopes[m]=(b,name)
    stack=[]
    for m,(b,name) in sorted(slopes.items()):
        start=None
        while stack:
            x,c,d,_=stack[-1]; start=(c-b)/(m-d)
            if x is None or start>x: break
            stack.pop()
        if not stack: start=None
        stack.append((start,b,m,name))
    out=[]
    for i,(x,b,m,name) in enumerate(stack):
        if i+1<len(stack) and stack[i+1][0]<=0: continue
        if x is not None and x>=1: break
        out.append((max(F(0),x) if x is not None else F(0),b,m,name))
    assert out and out[0][0]==0
    return tuple(out)


def lookup(hull,p):
    from bisect import bisect_right
    x,b,m,name=hull[bisect_right([row[0] for row in hull],p)-1]
    return b+m*p,name


def transform(b,m,l0,l1,hazard):
    # z V(q) where z = l0*(1-p)+l1*p and q = hazard+(1-2*hazard)*l1*p/z.
    u=b+m*hazard
    return u*l0,u*(l1-l0)+m*(1-2*hazard)*l1


def backup_lines(hull,data,hazard):
    """Sum the transformed continuation functions by sweeping rational breakpoints."""
    lines=[]
    for name,(r0,r1,outcomes) in data.items():
        b,m=r0,r1-r0; events=defaultdict(lambda:[F(0),F(0)])
        for l0,l1 in outcomes:
            if not l0 or not l1:
                q=hazard if l0 else 1-hazard
                val,_=lookup(hull,q); b+=val*l0; m+=val*(l1-l0); continue
            old=None
            for j,(x,c,d,_) in enumerate(hull):
                if x<=hazard:
                    old=transform(c,d,l0,l1,hazard); continue
                if x>=1-hazard: break
                assert old is not None
                ratio=(x-hazard)/(1-2*hazard)
                pos=ratio*l0/(l1*(1-ratio)+ratio*l0)
                new=transform(c,d,l0,l1,hazard)
                ev=events[pos]; ev[0]+=new[0]-old[0]; ev[1]+=new[1]-old[1]
                old=new
            # Recover initial line at q=hazard, independent of the scan's last line.
            for x,c,d,_ in reversed(hull):
                if x<=hazard:
                    u,v=transform(c,d,l0,l1,hazard); b+=u; m+=v; break
        lines.append((b,m,name))
        for pos,(db,dm) in sorted(events.items()):
            b+=db; m+=dm; lines.append((b,m,name))
    return lines


def qvalue(hull,p,entry,hazard):
    r0,r1,records=entry; val=r0*(1-p)+r1*p
    for l0,l1 in records:
        z=l0*(1-p)+l1*p
        if z:
            q=hazard+(1-2*hazard)*l1*p/z
            val+=z*lookup(hull,q)[0]
    return val


def exact(horizon=3,hazard=HAZARD,menu=MENU):
    assert 0<=hazard<=F(1,2)
    data=model(menu); hs=[((F(0),F(0),F(0),'stop'),)]
    for _ in range(horizon): hs.append(envelope(backup_lines(hs[-1],data,hazard)))
    return hs


def myopic_value(horizon,p,data,hazard):
    """Direct recursion, limited to small horizons; no hull continuation optimization."""
    @lru_cache(None)
    def rec(n,p):
        if not n:return F(0)
        name=max(data,key=lambda name:((1-p)*data[name][0]+p*data[name][1],-list(data).index(name)))
        r0,r1,outcomes=data[name]; val=(1-p)*r0+p*r1
        for l0,l1 in outcomes:
            z=(1-p)*l0+p*l1
            if z:val+=z*rec(n-1,hazard+(1-2*hazard)*p*l1/z)
        return val
    return rec(horizon,p)


def toy():
    # Two static latent modes. Safe: reward 1 regardless of mode, no information.
    # Bet0/Bet1: reward +3 or -3 and reveal mode through their outcome. Probe: -1 and reveal.
    # Use a higher-loss bet to make a strictly costly probe optimal at the initial belief.
    d={'safe':(F(1),F(1),((F(1),F(1)),)), 'probe':(F(-1),F(-1),((F(1),F(0)),(F(0),F(1)))),
       'bet0':(F(6),F(-12),((F(1),F(0)),(F(0),F(1)))), 'bet1':(F(-12),F(6),((F(1),F(0)),(F(0),F(1))))}
    h=((F(0),F(0),F(0),'stop'),); out=[]
    for n in range(1,5):
        h=envelope(backup_lines(h,d,F(0))); val,act=lookup(h,F(1,2))
        out.append(dict(horizon=n,optimal=str(val),first=act,myopic=str(myopic_value(n,F(1,2),d,F(0)))))
    return out


def run(horizon=3):
    data=model(); hs=exact(horizon); rows=[]; checks=0
    for h in range(1,horizon+1):
        for i in range(41):
            p=F(i,40); val,act=lookup(hs[h],p)
            assert val==max(qvalue(hs[h-1],p,e,HAZARD) for e in data.values()); checks+=1
            myopic=max(data,key=lambda x:((1-p)*data[x][0]+p*data[x][1],-list(data).index(x)))
            m=qvalue(hs[h-1],p,data[myopic],HAZARD)
            rows.append(dict(horizon=h,belief=str(p),optimal=str(val),first=act,myopic_first=myopic,one_step_opportunity=str(val-m)))
    return dict(protocol='VAD-09A',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependency_sha256=sha256(Path(a.__file__).read_bytes()).hexdigest(),horizon=horizon,hazard=str(HAZARD),menu=list(MENU),segments=[len(h) for h in hs],checks=checks,immediate={k:[str(v[0]),str(v[1]),len(v[2])] for k,v in data.items()},half=[dict(horizon=h,optimal=str(lookup(hs[h],F(1,2))[0]),first=lookup(hs[h],F(1,2))[1],myopic=str(myopic_value(h,F(1,2),data,HAZARD)) if h<=2 else None) for h in range(1,horizon+1)],rows=rows,toy=toy())

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); p.add_argument('--horizon',type=int,default=3); args=p.parse_args(); r=run(args.horizon); args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n'); print('segments',r['segments'],'half',r['half'],'toy',r['toy']);print('different action with positive value',[(x['horizon'],x['belief'],x['first'],x['myopic_first'],float(F(x['one_step_opportunity']))) for x in r['rows'] if F(x['one_step_opportunity'])>0])

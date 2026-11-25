"""Exploratory longer deployment, holding all eight-target choices fixed."""
import argparse
import json
from pathlib import Path
import verify_vad_lean as v


def run():
    horizons=(8,16,32,64,128,256)
    original=v.H
    v.H=max(horizons)
    try:
        cal=[v.family(10000+i,v.REGIMES[i%4])[0] for i in range(16)]
        g,gw=v.discover(tuple(t for f in cal for t in f),'shape',256)
        gb=2*len(v.leaves(g))-1 if g else 0
        rows=[]
        for i in range(32):
            regime=v.REGIMES[i%4]
            dev,held=v.family(20000+i,regime)
            for arm in v.ARMS:
                kind='concrete' if arm=='concrete' else 'shape'
                cache,work=(None,0) if arm=='direct' else (g,0) if arm=='global_shape' else v.discover(dev,kind,8)
                build=0 if cache is None or arm=='global_shape' else 2*len(v.leaves(cache))-1
                vals=[v.proof(t,cache,kind)[1] for t in held]
                direct=[2*len(v.leaves(t))-1 for t in held]
                for h in horizons:
                    rows.append(dict(arm=arm,family=i,regime=regime,horizon=h,baseline=sum(direct[:h]),total=sum(vals[:h])+work+build,refs=sum(vals[:h]),work=work,construction=build))
        summary=[]
        for h in horizons:
            for a in v.ARMS:
                rs=[r for r in rows if r['arm']==a and r['horizon']==h]
                b=sum(r['baseline'] for r in rs)
                t=sum(r['total'] for r in rs)+(gw+gb if a=='global_shape' else 0)
                summary.append(dict(horizon=h,arm=a,baseline=b,total=t,gain=b/t))
        return dict(evidence='exploratory reference-cost sweep; no Lean replay; same public families; fixed H=8 selection',summary=summary,rows=rows)
    finally:
        v.H=original


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    a.out.write_text(json.dumps(run(),indent=2)+'\n')

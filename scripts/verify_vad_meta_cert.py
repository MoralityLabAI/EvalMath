"""VAD-09C: evaluate a finite-memory grid policy by forward latent-law expectation.
Interpolation supplies a mathematical upper bound in exact arithmetic for the nominal menu;
reported numerical bounds are floating-point estimates, not interval certificates.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse,json
import numpy as np
import verify_vad_meta as m
import verify_vad_meta_grid as g

HORIZONS=(1,2,3,8,16,32,96)
HAZARDS=(0.,.01,.05,.25,.5)


def kernels(grid):
    out=[]; n=len(grid.x)
    for name,(r0,r1,records) in grid.data.items():
        l0,l1=np.array(records,dtype=float).T; p=grid.x[:,None]
        z=l0*(1-p)+l1*p
        posterior=np.divide(l1*p,z,out=np.zeros_like(z),where=z>0)
        dest=np.rint((grid.hazard+(1-2*grid.hazard)*posterior)*(n-1)).astype(int)
        out.append((np.array((float(r0),float(r1))),np.stack((l0,l1)),dest))
    return out


def value(grid,actual_hazard,horizon,lookahead):
    """Expected return conditional on true mode and controller memory state.
    Quantization affects decisions, not transition probabilities of true modes.
    """
    kk=kernels(grid); n=len(grid.x); old=np.zeros((2,n)); memory=np.arange(n)
    for h in range(1,horizon+1):
        chosen=np.argmax(grid.q[min(h,lookahead)],axis=0); new=np.empty_like(old)
        after=(1-actual_hazard)*old+actual_hazard*old[::-1]
        for j,(r,probs,dest) in enumerate(kk):
            idx=memory[chosen==j]
            if not len(idx): continue
            new[:,idx]=r[:,None]+np.sum(probs[:,None,:]*after[:,dest[idx]],axis=-1)
        old=new
    return float(old[:,n//2].mean())


def run():
    nominal=g.Grid(g.N_GRID,96,.05); fine=g.Grid(2*g.N_GRID-1,96,.05)
    rows=[]
    for h in HORIZONS:
        upper=float(nominal.values[h][len(nominal.x)//2]); upper_fine=float(fine.values[h][len(fine.x)//2])
        lo=value(nominal,.05,h,h); lf=value(fine,.05,h,h); myopic=value(nominal,.05,h,1)
        assert lo<=upper+1e-8 and lf<=upper_fine+1e-8
        rows.append(dict(horizon=h,upper_grid=upper,upper_fine=upper_fine,policy=lo,policy_fine=lf,myopic=myopic,gap=upper_fine-lf,advantage=lf-myopic))
    shifts=[]
    for hazard in HAZARDS:
        for look in (1,3,8,32,96):
            shifts.append(dict(actual_hazard=hazard,assumed_hazard=.05,horizon=96,lookahead=look,value=value(nominal,hazard,96,look)))
    return dict(protocol='VAD-09C',evidence='floating point expectation of finite-memory policy; upper/lower estimates not interval certificates',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependencies={Path(z.__file__).name:sha256(Path(z.__file__).read_bytes()).hexdigest() for z in (m,g)},rows=rows,shifts=shifts)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args(); r=run();args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r['rows'],indent=2)); print(json.dumps(r['shifts'],indent=2))

"""VAD-09B: interpolation-based longer-horizon planner and matched-stream stress test."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from random import Random
import argparse,json
import numpy as np
import verify_vad_meta as m
import verify_vad_reliability as v

CAPS=(1,3,8,32)
METHODS=('blind','frozen','menu_1','menu_3','menu_8','menu_32','full_myopic','expanded','mode_oracle')
N_GRID=401
SPLIT=(9100000,32,96)

class Grid:
    def __init__(self,n=N_GRID,horizon=max(CAPS),hazard=.05):
        self.x=np.linspace(0,1,n); self.data=m.model(); self.names=tuple(self.data)
        self.q=[None]; self.values=[np.zeros(n)]; self.hazard=hazard
        kernels=[]
        for r0,r1,records in self.data.values():
            l0,l1=np.array(records,dtype=float).T
            p=self.x[:,None]; z=l0*(1-p)+l1*p
            post=np.divide(l1*p,z,out=np.zeros_like(z),where=z>0)
            dest=(hazard+(1-2*hazard)*post)*(n-1)
            low=np.minimum(n-2,np.maximum(0,np.floor(dest).astype(int))); alpha=dest-low
            kernels.append((float(r0)*(1-self.x)+float(r1)*self.x,z,low,alpha))
        for _ in range(horizon):
            old=self.values[-1]; scores=np.stack([immediate+np.sum(z*((1-alpha)*old[low]+alpha*old[low+1]),axis=1) for immediate,z,low,alpha in kernels])
            self.q.append(scores); self.values.append(scores.max(axis=0))
    def choose(self,p,h):
        x=max(0.,min(1.,p))*(len(self.x)-1); i=min(len(self.x)-2,int(x)); f=x-i
        vals=(1-f)*self.q[h][:,i]+f*self.q[h][:,i+1]
        return self.names[int(vals.argmax())]


def execute_action(world,name,actions):
    if name.startswith('cut'): return v.execute(world,cap=int(name[3:]))
    return v.execute(world,actions=actions[name])


def simulate(stream,method,grid,actions):
    p=.5; exp=(.4,.4,.05,.05,.05,.05); rows=[]
    for j,world in enumerate(stream):
        mode,prior,channel,_,_=world; name=None
        if method.startswith('menu_'):
            h=min(int(method[5:]),len(stream)-j); name=grid.choose(p,h); rec,net=execute_action(world,name,actions)
        elif method=='blind': name='cut2'; rec,net=v.execute(world,cap=2)
        elif method=='frozen': name='p0'; rec,net=execute_action(world,name,actions)
        elif method=='full_myopic': rec,net=v.execute(world,actions=v.policy(v.quantize(p)))
        elif method=='expanded': rec,net=v.execute(world,actions=v.expanded_policy(v.simplex_quantize(exp)))
        elif method=='mode_oracle': rec,net=v.execute(world,actions=v.true_policy(mode,prior,channel))
        else: raise ValueError(method)
        # Both filters see only their own censored record. Oracle alone sees mode/prior/channel.
        posterior,_=v.update(p,rec); pnext=v.transition(posterior)
        if method=='expanded': exp,_=v.norm_update(exp,rec,v.EXP_MODELS); exp=v.expanded_transition(exp)
        rows.append(dict(record=list(rec),net=net,belief=p,action=name,mode=mode,full_explore=name=='cut24'))
        p=pnext
    return rows


def run(n=N_GRID):
    grid=Grid(n); fine=Grid(2*n-1); exact=m.exact(3)
    errors=[]
    for h in range(1,4):
        # Exact comparison on all 41 predeclared rational points.
        e=max(abs(np.interp(i/40,grid.x,grid.values[h])-float(m.lookup(exact[h],F(i,40))[0])) for i in range(41))
        errors.append(float(e))
    convergence=[float(np.max(np.abs(grid.values[h]-fine.values[h][::2]))) for h in CAPS]
    actions={}
    for name in m.MENU:
        if name.startswith('p'):
            f=m.action(name); actions[name]={(j,k):f(j,k) for j in range(v.H+1) for k in range(j+1)}
    start,nstreams,steps=SPLIT; rows=[]
    for si,s in enumerate(v.SCENARIOS):
        for i in range(nstreams):
            seed=start+10000*si+i; stream=v.family_stream(seed,s,steps)
            for method in METHODS:
                rr=simulate(stream,method,grid,actions)
                rows.append(dict(scenario=s,seed=seed,method=method,n=steps,net=sum(x['net'] for x in rr),observations=sum(x['record'][0] for x in rr),hits=sum(x['record'][2] for x in rr),exploratory=sum(x['full_explore'] for x in rr),trace_sha256=sha256(json.dumps(rr,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    summary=[]
    for s in v.SCENARIOS:
        for name in METHODS:
            rr=[r for r in rows if r['scenario']==s and r['method']==name]; nn=sum(r['n'] for r in rr)
            summary.append(dict(scenario=s,method=name,mean_net=sum(r['net'] for r in rr)/nn,mean_observations=sum(r['observations'] for r in rr)/nn,hit_rate=sum(r['hits'] for r in rr)/nn,full_explore=sum(r['exploratory'] for r in rr)/nn))
    pairs=v.paired(rows,'menu_32','menu_1')+v.paired(rows,'menu_32','full_myopic')
    return dict(protocol='VAD-09B',evidence='approximate belief-grid planning; sampled synthetic streams',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependencies={Path(z.__file__).name:sha256(Path(z.__file__).read_bytes()).hexdigest() for z in (m,v)},grid=n,fine_grid=2*n-1,split=SPLIT,exact_errors=errors,convergence=convergence,half_values=[dict(horizon=h,value=float(np.interp(.5,grid.x,grid.values[h])),first=grid.choose(.5,h)) for h in CAPS],summary=summary,paired=pairs,records=rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True); args=p.parse_args(); r=run();args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n'); print('errors',r['exact_errors'],'convergence',r['convergence'],'half',r['half_values']);
    for s in v.SCENARIOS: print(s,{x['method']:round(x['mean_net'],4) for x in r['summary'] if x['scenario']==s})
    print('paired',r['paired'])

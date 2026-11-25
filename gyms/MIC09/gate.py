"""Learn to skip expensive decomposition scans; exactness remains independent of the gate."""
from mic09 import *
from statistics import mean
import numpy as np
import torch
from torch import nn

MODEL_SEEDS=(17,29,43)

def features(e,s,req):
    n=max(1,s.bit_count());degrees=[(e.adj[i]&s).bit_count() for i in bits(s)]
    return np.array([n/e.n,req.bit_count()/n,sum(x==0 for x in degrees)/n,
        sum(x<=1 for x in degrees)/n,sum(degrees)/max(1,n*n),max(degrees,default=0)/n,
        e.value(s)/e.total,len(e.d.sup)/e.n],dtype=np.float32)

def label(e,s,req,parts):
    return len(parts)>1 and any(c&~req and (c.bit_count()<=8 or not any(e.adj[i]&c for i in bits(c))) for c in parts)

def examples():
    X=[];Y=[];count=0
    def observe(e,s,req,parts):
        X.append(features(e,s,req));Y.append(label(e,s,req,parts))
    for f in ('conflict','mixed'):
        for n in (16,32):
            for planted in (False,True):
                for seed in range(5000,5006):
                    solve(instance(f,seed,n,planted),'both',cap=128,observer=observe);count+=1
    return np.stack(X),np.asarray(Y,np.float32),count

def fit(x,y,seed):
    torch.manual_seed(seed);net=nn.Sequential(nn.Linear(8,16),nn.Tanh(),nn.Linear(16,1));opt=torch.optim.Adam(net.parameters(),lr=.02)
    X=torch.from_numpy(x);Y=torch.from_numpy(y)
    for _ in range(120):
        loss=nn.functional.binary_cross_entropy_with_logits(net(X).squeeze(-1),Y);opt.zero_grad();loss.backward();opt.step()
    W,b,V,c=[p.detach().numpy().copy() for p in net.parameters()]
    def predict(e,s,req):return bool((V@np.tanh(W@features(e,s,req)+b)+c)[0]>=0)
    return predict,sum(p.numel() for p in net.parameters()),float(loss.detach())

def periodic(e,s,req):return e.norm_calls<=2 or e.norm_calls%8==0 or s.bit_count()<=16

def run_gate():
    torch.set_num_threads(1);t=perf_counter();x,y,count=examples();nets={k:fit(x,y,k) for k in MODEL_SEEDS}
    prior=json.loads(Path(__file__).with_name('results.json').read_text());rows=[];audit={str(k):[0,0,0,0] for k in MODEL_SEEDS}
    for row in prior['rows']:
        d=instance(row['family'],row['seed'],row['n'],row['planted']);arms={}
        def observe(e,s,req,parts):
            y=bool(label(e,s,req,parts))
            for k,(pred,_,_) in nets.items():
                p=pred(e,s,req);audit[str(k)][2*int(y)+int(p)]+=1
        # Observer replay is outside the measured gate timings.
        solve(d,'both',observer=observe)
        arms['periodic']=solve(d,'both',gate=periodic)
        for k,(pred,_,_) in nets.items():arms[f'learned_{k}']=solve(d,'both',gate=pred)
        lo=max([row['pooled_lower']]+[a['value'] for a in arms.values()]);hi=min([row['pooled_upper']]+[a['upper'] for a in arms.values()]);assert lo<=hi
        assert all(valid(d,int(a['mask'],16)) and a['normalizations']<=CAP for a in arms.values())
        rows.append({**{k:row[k] for k in ('family','n','seed','planted')},'arms':arms,'pooled_lower':lo,'pooled_upper':hi})
    return dict(schema='MIC-09/gate/v1',training_roots=count,training_states=len(x),positive_states=int(y.sum()),
        parameters=next(iter(nets.values()))[1],model_seeds=MODEL_SEEDS,final_loss={str(k):v[2] for k,v in nets.items()},
        label_confusion_order=['TN','FP','FN','TP'],confusion=audit,rows=rows,elapsed_s=perf_counter()-t)
if __name__=='__main__':print(json.dumps(run_gate(),sort_keys=True,indent=2))

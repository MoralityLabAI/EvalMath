"""Optional CPU GRU predictor; train on disjoint censored streams, evaluate own actions."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import torch
from torch import nn
import numpy as np
import verify_vad_reliability as v

class Predictor(nn.Module):
    def __init__(self):
        super().__init__(); self.rnn=nn.GRU(5,8,batch_first=True); self.head=nn.Linear(8,1)
    def forward(self,x):
        y,_=self.rnn(x); y=torch.cat((torch.zeros_like(y[:,:1]),y[:,:-1]),dim=1)
        return self.head(y).squeeze(-1)

class Inference:
    head_macs=8; step_macs=3*8*(5+8)
    def __init__(self,model):
        d={k:x.detach().numpy().astype('float64') for k,x in model.state_dict().items()}
        self.wi=d['rnn.weight_ih_l0']; self.wh=d['rnn.weight_hh_l0']; self.bi=d['rnn.bias_ih_l0']; self.bh=d['rnn.bias_hh_l0']; self.w=d['head.weight'][0]; self.b=d['head.bias'][0]
    def predict(self,h):
        return float(1/(1+np.exp(-(self.b if h is None else self.w@h+self.b))))
    def step(self,x,h):
        if h is None: h=np.zeros(8)
        a=self.wi@x+self.bi; b=self.wh@h+self.bh
        r,z=1/(1+np.exp(-(a[:16]+b[:16]))).reshape(2,8)
        n=np.tanh(a[16:]+r*b[16:]); return (1-z)*n+z*h

def dataset(split):
    start,n,steps=v.SPLITS[split]; feats=[]; labels=[]; obs=0; net=0
    for i in range(n):
        stream=v.family_stream(start+i,'markov',steps); rng=Random(start+100000+i); xx=[]; yy=[]
        for world in stream:
            if rng.randrange(2): rec,u=v.execute(world,cap=rng.choice((2,4,8,16,24)))
            else: rec,u=v.execute(world,actions=v.policy(rng.randrange(v.GRID+1)))
            xx.append(v.feature(rec)); yy.append(world[0]); obs+=rec[0]; net+=u
        feats.append(xx); labels.append(yy)
    return torch.tensor(feats),torch.tensor(labels,dtype=torch.float32),dict(streams=n,families=n*steps,observations=obs,observation_cost=obs*v.COST,behavior_net=net)

def fit():
    torch.manual_seed(83801); torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    x,y,stats=dataset('train'); cx,cy,cs=dataset('cal'); model=Predictor(); opt=torch.optim.AdamW(model.parameters(),lr=.01)
    best=None; best_loss=float('inf'); losses=[]
    for ep in range(20):
        for batch in torch.randperm(len(x)).split(32):
            loss=nn.functional.binary_cross_entropy_with_logits(model(x[batch]),y[batch]); opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): loss=float(nn.functional.binary_cross_entropy_with_logits(model(cx),cy))
        losses.append(loss)
        if loss<best_loss: best_loss=loss; best={k:z.clone() for k,z in model.state_dict().items()}; best_epoch=ep+1
    model.load_state_dict(best); model.eval(); inference=Inference(model)
    h=None
    with torch.no_grad():
        expected=torch.sigmoid(model(cx[:1]))[0].numpy()
        for row,p in zip(cx[0].numpy(),expected):
            assert abs(inference.predict(h)-p)<1e-6
            h=inference.step(row,h)
    return model,dict(parameters=sum(p.numel() for p in model.parameters()),train=stats,cal=cs,seed=83801,best_epoch=best_epoch,cal_bce=best_loss,cal_losses=losses)

def main(out):
    out.mkdir(parents=True,exist_ok=True); model,stats=fit(); ckpt=out/'controller.pt'; torch.save(model.state_dict(),ckpt)
    freeze=dict(protocol='VAD-08',training=stats,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),parent_sha256=sha256(Path(v.__file__).read_bytes()).hexdigest(),checkpoint_sha256=sha256(ckpt.read_bytes()).hexdigest(),torch_version=str(torch.__version__))
    (out/'freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n'); print('FROZEN',stats['parameters'],stats['best_epoch'],stats['cal_bce'],flush=True)
    r=v.run(predictor=Inference(model)); r.update(freeze=freeze,paired_filter=v.paired(r['records'],'gru','filter'),paired_expanded=v.paired(r['records'],'gru','expanded'),paired_frozen=v.paired(r['records'],'filter','frozen'))
    (out/'receipt.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    for s in v.SCENARIOS: print(s,{x['method']:round(x['mean_net'],3) for x in r['summary'] if x['scenario']==s},flush=True)
    print('gru vs filter',r['paired_filter'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); args=p.parse_args(); main(args.out)

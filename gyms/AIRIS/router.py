"""AIRIS-06 CPU pilot: tied residual recurrence versus matched controls."""
import argparse
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
import json
import math
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as fn
from partial import SCHEDULES
from router_data import split,weights,teacher,fingerprint,oracle_last

SEEDS=(101,103,107)
ARMS=("tied","reset","histogram")
MAXLEN=6
EPOCHS=24
BATCH=256


class TiedRouter(nn.Module):
    """Original tiny weight-tied residual controller, not the official TRM."""
    def __init__(self,reset=False):
        super().__init__()
        self.reset=reset
        self.embed=nn.Linear(6,24)
        self.mix=nn.Linear(48,24)
        self.delta=nn.Linear(24,24)
        self.read=nn.Linear(24,8)

    def forward(self,x,mask,force_reset=False):
        h=x.new_zeros((x.shape[0],24))
        for i in range(x.shape[1]):
            old=h
            if self.reset or force_reset:
                h=torch.zeros_like(h)
            e=self.embed(x[:,i])
            # Same residual block for two inner visits at every event.
            for _ in range(2):
                h=h+0.5*torch.tanh(self.delta(torch.tanh(self.mix(torch.cat((h,e),dim=-1)))))
            h=torch.where(mask[:,i,None],h,old)
        return self.read(h)


class HistogramRouter(nn.Module):
    def __init__(self):
        super().__init__()
        self.net=nn.Sequential(nn.Linear(64,22),nn.Tanh(),nn.Linear(22,22),
                               nn.Tanh(),nn.Linear(22,8))
    def forward(self,x,mask):
        key=(x.long()*x.new_tensor((32,16,8,4,2,1),dtype=torch.long)).sum(-1)
        counts=(fn.one_hot(key,64)*mask[:,:,None]).sum(1).float()
        return self.net(counts)


def make_model(arm):
    if arm=="histogram":
        return HistogramRouter()
    if arm in ("tied","reset"):
        return TiedRouter(reset=arm=="reset")
    raise ValueError("invalid arm")


def parameter_count(model):
    return sum(p.numel() for p in model.parameters())


def encode(rows):
    x=torch.zeros((len(rows),MAXLEN,6))
    mask=torch.zeros((len(rows),MAXLEN),dtype=torch.bool)
    labels=[]
    for i,h in enumerate(rows):
        if not 1<=len(h)<=MAXLEN:
            raise ValueError("invalid history length")
        x[i,:len(h)]=torch.tensor([(*a,*y) for a,y in h],dtype=torch.float32)
        mask[i,:len(h)]=True
        nums,den=teacher(weights(h))
        q=[n/den for n in nums]
        mean=sum(q)/len(q)
        labels.append([16*(v-mean) for v in q])
    return x,mask,torch.tensor(labels,dtype=torch.float32)


def train(arm,seed,batch,epochs=EPOCHS):
    torch.manual_seed(seed)
    model=make_model(arm)
    opt=torch.optim.AdamW(model.parameters(),lr=0.003,weight_decay=0.0001)
    x,mask,y=batch
    losses=[]
    g=torch.Generator().manual_seed(seed+10000)
    for epoch in range(epochs):
        total=0.0
        for ids in torch.randperm(len(x),generator=g).split(BATCH):
            opt.zero_grad(set_to_none=True)
            loss=fn.mse_loss(model(x[ids],mask[ids]),y[ids])
            loss.backward()
            opt.step()
            total+=loss.item()*len(ids)
        losses.append(total/len(x))
    return model,losses


@torch.no_grad()
def choose(model,batch,reset=False):
    x,mask,_=batch
    model.eval()
    return [int(v) for ids in torch.arange(len(x)).split(BATCH)
            for v in (model(x[ids],mask[ids],force_reset=True) if reset else
                      model(x[ids],mask[ids])).argmax(-1)]


def summarize(rows,actions):
    groups=defaultdict(list)
    regrets=[]
    exact=[]
    for h,a in zip(rows,actions,strict=True):
        w=weights(h)
        nums,den=teacher(w)
        n,d=(8*max(nums)-sum(nums),8*den) if a=="uniform" else (max(nums)-nums[a],den)
        r=F(n,d)
        exact.append((r.numerator,r.denominator))
        regrets.append(float(r))
        groups[w].append(float(r))
    mean=math.fsum(regrets)/len(regrets)
    return {"mean_regret":mean,"posterior_macro_regret":math.fsum(math.fsum(g)/len(g)
              for g in groups.values())/len(groups),"max_regret":max(regrets),
            "zero_regret_fraction":sum(r==0 for r in regrets)/len(regrets),
            "n_rows":len(rows),"n_posterior_groups":len(groups),"exact_regret":exact}


def run(out,epochs=EPOCHS,short_draws=12000,long_draws=4000):
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    out.mkdir(parents=True,exist_ok=True)
    data=split(short_draws,long_draws)
    batches={k:encode(v) for k,v in data.items()}
    manifest={k:{"n":len(v),"posterior_groups":len({weights(h) for h in v}),
                 "public_histories_sha256":fingerprint(v),
                 "length_counts":{str(n):sum(len(h)==n for h in v) for n in range(1,7)}}
              for k,v in data.items()}
    # Retain the data; no hidden mechanism ID is exported.
    (out/"public_histories.json").write_text(json.dumps(data,separators=(",",":"))+"\n")
    metrics={}
    per_row={}
    for name in ("short","long"):
        rows=data[name]
        choices={"fixed_pulse":[0]*len(rows),"uniform":["uniform"]*len(rows),
                 "oracle_last":[oracle_last(h) for h in rows],
                 "oracle_full":[max(range(8),key=teacher(weights(h))[0].__getitem__) for h in rows]}
        metrics[name]={k:summarize(rows,v) for k,v in choices.items()}
        per_row[name]=choices
    runs=[]
    for seed in SEEDS:
        for arm in ARMS:
            model,losses=train(arm,seed,batches["train"],epochs)
            checkpoint=out/f"{arm}-{seed}.pt"
            torch.save(model.state_dict(),checkpoint)
            run_meta={"seed":seed,"arm":arm,"parameters":parameter_count(model),
                      "epoch_train_losses":losses,"checkpoint_sha256":sha256(checkpoint.read_bytes()).hexdigest()}
            runs.append(run_meta)
            for name in ("short","long"):
                rows=data[name]
                label=f"{arm}-{seed}"
                actions=choose(model,batches[name])
                per_row[name][label]=actions
                metrics[name][label]=summarize(rows,actions)
                if arm=="tied":
                    label=f"tied_inference_reset-{seed}"
                    actions=choose(model,batches[name],reset=True)
                    per_row[name][label]=actions
                    metrics[name][label]=summarize(rows,actions)
    result={"experiment":"AIRIS-06","evidence":"PILOT_ONLY; one synthetic grammar; no sealed mechanistic or generalization claim",
            "torch_version":torch.__version__,"device":"cpu","seeds":SEEDS,
            "epochs":epochs,"batch_size":BATCH,"manifest":manifest,"runs":runs,
            "metrics":metrics,"actions":per_row,
            "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                              for name in ("router.py","router_data.py","test_router.py","ROUTER.md","partial.py")}}
    (out/"AIRIS-06.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    summary={split:{k:{m:v[m] for m in ("mean_regret","posterior_macro_regret","zero_regret_fraction")}
                     for k,v in arms.items()} for split,arms in metrics.items()}
    print(json.dumps({"manifest":manifest,"parameters":{r["arm"]:r["parameters"] for r in runs},
                      "metrics":summary},indent=2,sort_keys=True))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("airis-router-output"))
    args=p.parse_args()
    run(args.out)

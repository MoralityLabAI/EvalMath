"""AIRIS-08: parameter-matched chronological experiment selection pilot."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from chronology_data import make_data,target,summarize,exact_actions
from curriculum import digest

ARMS=("gated","residual","reset","ordered_flat","hist_last")
SEEDS=(101,103,107)
EPOCHS=32
BATCH=256
HERE=Path(__file__).parent


class Gated(nn.Module):
    def __init__(self,reset=False):
        super().__init__()
        self.reset=reset
        self.embed=nn.Linear(33,21)
        self.gate=nn.Linear(42,21)
        self.candidate=nn.Linear(42,21)
        self.read=nn.Linear(21,8)

    def forward(self,x,k,sham=None):
        h=x.new_zeros((len(x),21))
        for i in range(3):
            if self.reset or sham=="reset":
                h=torch.zeros_like(h)
            e=torch.tanh(self.embed(torch.cat((x[:,i],k),-1)))
            for _ in range(2):
                z=torch.cat((h,e),-1)
                g=torch.sigmoid(self.gate(z))
                h=h+g*(torch.tanh(self.candidate(z))-h)
        return self.read(h)


class Residual(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed=nn.Linear(33,24)
        self.mix=nn.Linear(48,24)
        self.delta=nn.Linear(24,24)
        self.read=nn.Linear(24,8)

    def forward(self,x,k,sham=None):
        h=x.new_zeros((len(x),24))
        for i in range(3):
            e=self.embed(torch.cat((x[:,i],k),-1))
            for _ in range(2):
                h=h+.5*torch.tanh(self.delta(torch.tanh(self.mix(torch.cat((h,e),-1)))))
        return self.read(h)


class Flat(nn.Module):
    def __init__(self,orderless=False):
        super().__init__()
        self.orderless=orderless
        d,w=(65,27) if orderless else (97,21)
        self.net=nn.Sequential(nn.Linear(d,w),nn.Tanh(),nn.Linear(w,w),
                               nn.Tanh(),nn.Linear(w,8))

    def forward(self,x,k,sham=None):
        z=torch.cat((x.sum(1),x[:,-1],k),-1) if self.orderless else torch.cat((x.flatten(1),k),-1)
        return self.net(z)


def model(arm):
    if arm=="gated":
        return Gated()
    if arm=="reset":
        return Gated(True)
    if arm=="residual":
        return Residual()
    if arm=="ordered_flat":
        return Flat()
    if arm=="hist_last":
        return Flat(True)
    raise ValueError("invalid architecture")


def count(m):
    return sum(p.numel() for p in m.parameters())


def encode(rows,labeled=False):
    h=torch.tensor([r[1] for r in rows],dtype=torch.long)
    x=F.one_hot(h,32).float()
    k=torch.tensor([[r[0]/4] for r in rows],dtype=torch.float32)
    if not labeled:
        return x,k
    labels=[]
    for r in rows:
        q=[float(v) for v in target(r)]
        mu=sum(q)/8
        labels.append([32*(v-mu) for v in q])
    return x,k,torch.tensor(labels,dtype=torch.float32)


def fit(arm,seed,batch,epochs):
    torch.manual_seed(seed)
    m=model(arm)
    opt=torch.optim.AdamW(m.parameters(),lr=.003,weight_decay=.0001)
    x,k,y=batch
    rng=torch.Generator().manual_seed(seed+80000)
    trace=[]
    for _ in range(epochs):
        total=0.
        for ids in torch.randperm(len(x),generator=rng).split(BATCH):
            opt.zero_grad(set_to_none=True)
            loss=F.mse_loss(m(x[ids],k[ids]),y[ids])
            loss.backward()
            opt.step()
            total+=float(loss.detach())*len(ids)
        trace.append(total/len(x))
    return m,trace


@torch.no_grad()
def actions(m,batch,sham=None):
    m.eval()
    x,k=batch
    return [int(a) for i in torch.arange(len(x)).split(BATCH)
            for a in m(x[i],k[i],sham=sham).argmax(-1)]


def run(out,epochs=EPOCHS):
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    out.mkdir(parents=True,exist_ok=True)
    train,dev,split=make_data()
    data={"train":train,"development":dev}
    (out/"public_inputs.json").write_text(json.dumps(data,separators=(",",":"))+"\n")
    batch=encode(train,True)
    # No evaluation label or score is consulted during optimization.
    checkpoints=[]
    for seed in SEEDS:
        for arm in ARMS:
            m,trace=fit(arm,seed,batch,epochs)
            p=out/f"{arm}-{seed}.pt"
            torch.save(m.state_dict(),p)
            checkpoints.append({"seed":seed,"arm":arm,"parameters":count(m),
                                "loss_trace":trace,"checkpoint":p.name,
                                "checkpoint_sha256":sha256(p.read_bytes()).hexdigest()})
    metrics={}
    selected={}
    for name,rows in dev.items():
        paired=name.startswith("paired")
        batch=encode(rows)
        picks={b:exact_actions(rows,b) for b in ("pulse","uniform","full","last")}
        if paired:
            picks["pair_orderless_oracle"]=exact_actions(rows,"pair_orderless")
        for rec in checkpoints:
            arm,seed=rec["arm"],rec["seed"]
            m=model(arm)
            m.load_state_dict(torch.load(out/rec["checkpoint"],weights_only=True,map_location="cpu"))
            picks[f"{arm}-{seed}"]=actions(m,batch)
            if arm=="gated":
                picks[f"gated_inference_reset-{seed}"]=actions(m,batch,"reset")
        stats={a:summarize(rows,v,paired) for a,v in picks.items()}
        if paired:
            floor=stats["full"]["orderless_floor"]
            assert abs(stats["pair_orderless_oracle"]["mean_regret"]-floor)<1e-12
            for a in picks:
                if a.startswith(("hist_last-","reset-","gated_inference_reset-")):
                    assert stats[a]["different_action_fraction"]==0
                    assert stats[a]["mean_regret"]+1e-12>=floor
        metrics[name]=stats
        selected[name]=picks
    result={"experiment":"AIRIS-08","evidence":"PILOT_ONLY: one public finite grammar; no mechanistic claim",
            "torch_version":torch.__version__,"split":split,
            "data_sha256":digest(data),"epochs":epochs,"seeds":SEEDS,"checkpoints":checkpoints,
            "metrics":metrics,"actions":selected,
            "sources":{p:sha256((HERE/p).read_bytes()).hexdigest() for p in
                       ("chronology_router.py","chronology_data.py","test_chronology.py",
                        "CHRONOLOGY.md","nonstationary.py","curriculum.py","partial.py","router_data.py")}}
    (out/"AIRIS-08.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    summary={"split":split,"parameters":{c["arm"]:c["parameters"] for c in checkpoints},
             "metrics":{n:{a:{k:v for k,v in s.items() if k!="regrets"}
                            for a,s in m.items()} for n,m in metrics.items()}}
    # CI log has compact, seed-level means and paired metrics for inspection.
    print(json.dumps(summary,sort_keys=True,indent=2))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    run(p.parse_args().out)

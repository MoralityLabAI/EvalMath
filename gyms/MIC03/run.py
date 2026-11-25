"""MIC-03 public CPU scheduling proxy. Requires PyTorch and Python 3.11+."""
from functools import lru_cache
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from random import Random
import hashlib
import json
import time
import torch
from torch import nn

FAMILIES = ('dag', 'cyclic', 'cover_sparse', 'cover_dense')
TRAIN_FAMILIES = ('dag', 'cover_sparse')
TRAIN_SEEDS = range(48)
DEV_SEEDS = range(1000, 1024)
MODEL_SEEDS = (17, 29, 43)
EPOCHS = 100


def make(f, seed, n):
    r = Random(seed + 100000 * FAMILIES.index(f))
    if f in ('dag', 'cyclic'):
        order = list(range(n))
        r.shuffle(order)
        m = [[0]*n for _ in range(n)]
        for i, u in enumerate(order):
            targets = order[i+1:] if f == 'dag' else [v for v in order if v != u]
            r.shuffle(targets)
            rem = 8
            for v in targets:
                m[u][v] = r.randint(0, rem)
                rem -= m[u][v]
        b = tuple(r.randint(1, 9) for _ in range(n))
        return tuple(map(tuple, m)), b
    a = [[r.randint(0, 2) if f == 'cover_dense' or r.random() < .35 else 0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        a[i][i] = max(1, a[i][i])
    return tuple(map(tuple, a)), tuple(r.randint(1, 9) for _ in range(n))


def initial(f, d):
    a, b = d
    if f in ('dag', 'cyclic'):
        k = max(-(-10*b[i] // (10-sum(a[i]))) for i in range(len(b)))
        return (k,)*len(b)
    return (4,)*len(b)


def score(f, d, p):
    a, b = d
    n = len(b)
    if len(p) != n or any(type(x) is not int or x < 0 for x in p):
        raise ValueError('bad certificate')
    if f in ('dag', 'cyclic'):
        if any(10*p[i] < 10*b[i]+sum(a[i][j]*p[j] for j in range(n)) for i in range(n)):
            raise ValueError('recurrence constraint')
        return sum(p)
    if any(x > 4 for x in p) or any(sum(a[i][j]*p[i] for i in range(n)) < 4 for j in range(n)):
        raise ValueError('cover constraint')
    return sum(x*y for x, y in zip(b, p))


def action(f, d, p, i):
    a, b = d
    n = len(b)
    if f in ('dag', 'cyclic'):
        v = b[i] + (sum(a[i][j]*p[j] for j in range(n))+9)//10
    else:
        v = max([0]+[-(-(4-sum(a[k][j]*p[k] for k in range(n) if k != i))//a[i][j]) for j in range(n) if a[i][j]])
    q = p[:i]+(v,)+p[i+1:]
    if v > p[i]:
        raise AssertionError('nonmonotone update')
    return q


def scan(f, d, p, mask):
    a, b = d
    n = len(b)
    rec = f in ('dag', 'cyclic')
    before = score(f, d, p)
    avail = [i for i in range(n) if mask >> i & 1]
    qs = {i: action(f, d, p, i) for i in avail}
    gains = {i: before-score(f, d, qs[i]) for i in avail}
    x = [[0.]*10 for _ in range(n)]
    keys = {}
    for i in avail:
        if rec:
            outgoing = sum(a[i][j] for j in avail)
            incoming = sum(a[j][i] for j in avail)
            conflict = 0
            keys[i] = (outgoing == 0, gains[i]*(10+incoming)-outgoing, gains[i], -i)
        else:
            outgoing = sum(a[i])
            incoming = sum(a[j][k] for j in avail if j != i for k in range(n) if a[i][k])
            conflict = sum(sum(min(a[i][k], a[j][k]) for k in range(n))*gains[j] for j in avail if j != i)
            keys[i] = (F(gains[i], 1+conflict), gains[i], -i)
        x[i] = [float(rec), gains[i]/max(1, before), p[i]/max(1, max(p)),
                b[i]/10, outgoing/(10*n), incoming/(10*n), conflict/(max(1,before)*n*10),
                len(avail)/n, before/max(1, score(f,d,initial(f,d))), 1.]
    return qs, gains, keys, x


def schedule_oracle(f, d):
    @lru_cache(None)
    def value(p, mask):
        if not mask:
            return score(f, d, p)
        return min(value(action(f,d,p,i),mask^(1<<i)) for i in range(len(p)) if mask>>i&1)
    return value


def certificate_oracle(f,d):
    a,b = d
    if f in ('dag','cyclic'):
        p = (0,)*len(b)
        cap = initial(f,d)
        while True:
            q = tuple(b[i]+(sum(a[i][j]*p[j] for j in range(len(b)))+9)//10 for i in range(len(b)))
            if not all(x <= y <= z for x,y,z in zip(p,q,cap)):
                raise AssertionError('fixed point bounds')
            if q == p:
                return score(f,d,p)
            p = q
    best = score(f,d,initial(f,d))
    for p in product(range(5),repeat=len(b)):
        obj = sum(x*y for x,y in zip(b,p))
        if obj < best and all(sum(a[i][j]*p[i] for i in range(len(b))) >= 4 for j in range(len(b))):
            best = obj
    return best


def teacher(f,d):
    p = initial(f,d)
    n = len(p)
    mask = (1<<n)-1
    value = schedule_oracle(f,d)
    xs, masks, labels = [],[],[]
    while mask:
        qs,_,_,x = scan(f,d,p,mask)
        costs = {i:value(q,mask^(1<<i)) for i,q in qs.items()}
        best = min(costs.values())
        xs.append(x)
        masks.append([i in qs for i in range(n)])
        labels.append([costs.get(i)==best for i in range(n)])
        i = min(i for i in costs if costs[i]==best)
        p = qs[i]
        mask ^= 1<<i
    return xs,masks,labels


class Ranker(nn.Module):
    def __init__(self, recurrent):
        super().__init__()
        self.recurrent = recurrent
        self.cell = nn.GRUCell(10,16)
        self.head = nn.Sequential(nn.Linear(26,16),nn.Tanh(),nn.Linear(16,1))

    def step(self,x,mask,h):
        pooled = (x*mask.unsqueeze(-1)).sum(1)/mask.sum(1,keepdim=True)
        h = self.cell(pooled,h if self.recurrent else torch.zeros_like(h))
        logits = self.head(torch.cat([x,h.unsqueeze(1).expand(-1,x.shape[1],-1)],-1)).squeeze(-1)
        return logits.masked_fill(~mask,-torch.inf),h


def fit(data, seed, recurrent):
    torch.manual_seed(seed)
    net = Ranker(recurrent)
    opt = torch.optim.Adam(net.parameters(),lr=.01)
    xs, masks, labels = [torch.tensor(t) for t in zip(*data)]
    for _ in range(EPOCHS):
        h = torch.zeros(len(xs),16)
        loss = 0
        for t in range(xs.shape[1]):
            z,h = net.step(xs[:,t],masks[:,t],h)
            loss = loss+(torch.logsumexp(z,1)-torch.logsumexp(z.masked_fill(~labels[:,t],-torch.inf),1)).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return net, float(loss.detach()/xs.shape[1])


@torch.no_grad()
def rollout(f,d,policy,net=None):
    p = initial(f,d)
    n = len(p)
    mask = (1<<n)-1
    h = torch.zeros(1,16)
    order = []
    calls = 0
    while mask:
        qs,gains,keys,x = scan(f,d,p,mask)
        calls += len(qs)+1+len(qs) # includes baseline normalization checks in scan
        if policy == 'greedy':
            i = max(qs,key=lambda i:(gains[i],-i))
        elif policy == 'dependency':
            i = max(qs,key=keys.get)
        else:
            z,h = net.step(torch.tensor([x]),torch.tensor([[i in qs for i in range(n)]]),h)
            i = int(z.argmax())
        p = qs[i]
        order.append(i)
        mask ^= 1<<i
    return {'score':score(f,d,p),'order':order,'score_calls':calls+1}


def run():
    torch.set_num_threads(1)
    t = time.perf_counter()
    data = [teacher(f,make(f,s,5)) for f in TRAIN_FAMILIES for s in TRAIN_SEEDS]
    models = {}
    for seed in MODEL_SEEDS:
        for recurrent in (False,True):
            k = ('recurrent' if recurrent else 'stateless')+f'_{seed}'
            net,loss = fit(data,seed,recurrent)
            models[k]=(net,loss)
    rows=[]
    for n in (5,6):
        for f in FAMILIES:
            for s in DEV_SEEDS:
                d=make(f,s,n)
                p=initial(f,d)
                gold=certificate_oracle(f,d)
                best=schedule_oracle(f,d)(p,(1<<n)-1)
                arms={k:rollout(f,d,k) for k in ('greedy','dependency')}
                arms.update({k:rollout(f,d,k,net) for k,(net,_) in models.items()})
                assert all(gold<=best<=v['score']<=score(f,d,p) for v in arms.values())
                assert len({v['score_calls'] for v in arms.values()})==1
                rows.append({'family':f,'n':n,'seed':s,'baseline':score(f,d,p),'certificate_oracle':gold,'schedule_oracle':best,'arms':arms})
    return {'schema':'MIC-03/public-cpu/v1','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'training_roots':len(data),'training_families':TRAIN_FAMILIES,'epochs':EPOCHS,'model_seeds':MODEL_SEEDS,
            'parameter_count':sum(p.numel() for p in next(iter(models.values()))[0].parameters()),
            'final_train_loss':{k:v[1] for k,v in models.items()},'rows':rows,
            'evidence':'public development only; no sealed confirmation; schedule oracle labels used for training only',
            'elapsed_seconds':time.perf_counter()-t,'torch_version':torch.__version__}


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))

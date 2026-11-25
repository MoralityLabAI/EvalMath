"""Independent infrastructure/target factorization of the MIC-15 optimum."""
from mic15 import *
from itertools import product
import numpy as np


def audit_oracle(d,budgets):
    # All rewarded target lemmas are sinks. With a fixed set of unrewarded
    # infrastructure lemmas, each target has its own cheapest enabled rule.
    infra=[i for i,l in enumerate(d.lemmas) if l.importance==0]
    targets=[i for i,l in enumerate(d.lemmas) if l.importance>0]
    assert infra==list(range(len(infra))) and all(all(j in infra for j in r.premises) for l in d.lemmas for r in l.rules)
    masks=np.arange(1<<len(infra),dtype=np.int64)
    base=np.zeros(len(masks),dtype=np.int64);costs=[]
    for i,l in enumerate(d.lemmas):
        c=np.full(len(masks),10**9,dtype=np.int64)
        for rule in l.rules:
            need=sum(1<<j for j in rule.premises)
            c=np.minimum(c,np.where(masks&need==need,rule.cost,10**9))
        assert (c<10**9).all()
        if i in infra:base+=np.where(masks>>i&1,c,0)
        else:costs.append(c)
    best={b:(0,0) for b in budgets};direct=best.copy();patterns=0
    for flags in product((0,1),repeat=len(targets)):
        selected=[j for j,x in enumerate(flags) if x];v=sum(d.lemmas[targets[j]].reward for j in selected)
        c=base.copy()
        for j in selected:c+=costs[j]
        least=int(c.min());direct_cost=sum(next(r.cost for r in d.lemmas[targets[j]].rules if not r.premises) for j in selected)
        for b in budgets:
            if least<=b:best[b]=max(best[b],(v,-least))
            if direct_cost<=b:direct[b]=max(direct[b],(v,-direct_cost))
        patterns+=1
    return best,direct,len(masks),patterns


def audit(raw):
    rows=[];count=0;start=time.perf_counter()
    groups={}
    for row in raw['rows']:groups.setdefault((row['family'],row['seed']),[]).append(row)
    for (f,seed),rr in groups.items():
        d=make(f,seed);verify_problem(d);budgets=[r['budget'] for r in rr];g,direct,infra,target=audit_oracle(d,budgets)
        for r in rr:
            b=r['budget'];a=r['arms']['oracle'];assert g[b]==(a['reward'],-a['cost'])
            for arm,receipt in r['arms'].items():
                assert check_path(d,receipt['path'],b)=={k:receipt[k] for k in ('reward','cost','steps','mask')}
                count+=1
            rows.append(dict(family=f,seed=seed,budget=b,oracle_reward=g[b][0],oracle_cost=-g[b][1],direct_only_reward=direct[b][0],direct_only_cost=-direct[b][1],infrastructure_masks=infra,target_patterns=target))
    primary=[r for r in raw['rows'] if r['budget']==116]
    regrets={k:[F(r['arms']['oracle']['reward']-r['arms'][k]['reward'],max(1,r['arms']['oracle']['reward'])) for r in primary] for k in ('immediate','bundle','look2','beam8','beam32')}
    strong=min(regrets,key=lambda k:mean(regrets[k]));headroom=mean(regrets['beam32']);hard=sum(x>=F(1,10) for x in regrets['beam32'])
    gate=headroom>=F(1,20) and mean(regrets[strong])>=F(1,20) and F(hard,len(primary))>=F(1,5)
    return dict(schema='MIC-15/independent-factorized-oracle/v1',roots=len(groups),budget_rows=len(rows),verified_paths=count,primary_budget=116,strongest_fixed=strong,mean_relative_regret=str(headroom),hard_primary_roots=hard,headroom_gate='PASS' if gate else 'FAIL_NO_FITS',rows=rows,elapsed_s=time.perf_counter()-start)


if __name__=='__main__':print(json.dumps(audit(json.loads(Path(__file__).with_name('results.json').read_text())),indent=2,sort_keys=True))

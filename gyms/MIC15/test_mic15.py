from dataclasses import replace
from itertools import combinations
from heapq import heappush, heappop
import pytest
from mic15 import *


def test_generated_rules():
    for f in FAMILIES:
        for seed in range(3):
            assert verify_problem(make(f,seed))


def test_independent_exact_oracle():
    # Independent shortest-path enumeration over all legal individual acquisitions;
    # every possible order and alternative rule is considered, unlike canonical DFS.
    for f in FAMILIES:
        d=make(f,19);d=replace(d,lemmas=tuple(d.lemmas[:10])+tuple(replace(l,rules=tuple(r for r in l.rules if not r.premises)) for l in d.lemmas[14:17]));p=Planner(d)
        budgets=(36,80,116);opt,_=p.exact(budgets);dist={0:0};heap=[(0,0)]
        while heap:
            cost,s=heappop(heap)
            if cost!=dist[s]:continue
            for i,l in enumerate(d.lemmas):
                if s>>i&1:continue
                for rule in l.rules:
                    if not all(s>>j&1 for j in rule.premises):continue
                    q=s|1<<i;c=cost+rule.cost
                    if c<=max(budgets) and c<dist.get(q,10**9):dist[q]=c;heappush(heap,(c,q))
        assert all(p.cost(s)==c for s,c in dist.items())
        for b in budgets:
            assert p.reward(opt[b])==max(sum(d.lemmas[j].reward for j in bits(s)) for s,c in dist.items() if c<=b)
        p.cost.cache_clear();p.reward.cache_clear()


def test_reuse_and_realized_paths():
    for f in FAMILIES:
        d=make(f,21);p=Planner(d);gold,_=p.exact((116,));opt=p.reward(gold[116]);assert opt>0
        for path in (p.immediate(116),p.bundle(116),p.bundle(116,2),p.beam(116,8),p.beam(116,32),p.materialize(gold[116])[0]):
            a=check_path(d,path,116);assert a['reward']<=opt and a['cost']<=116
        p.cost.cache_clear();p.reward.cache_clear()


def test_reject_invalid_receipts():
    d=make('hub',1);p=Planner(d);i=next(i for i,l in enumerate(d.lemmas) if any(r.premises for r in l.rules));k=next(k for k,r in enumerate(d.lemmas[i].rules) if r.premises)
    with pytest.raises(AssertionError):check_path(d,[(i,k)],1000)
    k=next(k for k,r in enumerate(d.lemmas[0].rules) if not r.premises)
    with pytest.raises(AssertionError):check_path(d,[(0,k),(0,k)],1000)
    with pytest.raises(AssertionError):check_path(d,[(0,k)],0)
    l=d.lemmas[-1];bad=replace(d,lemmas=d.lemmas[:-1]+(replace(l,bound=l.bound+1),))
    with pytest.raises(AssertionError):verify_problem(bad)


def test_factorized_oracle():
    from audit15 import audit_oracle
    for f in FAMILIES:
        d=make(f,41);p=Planner(d);g,_=p.exact((80,116));a,direct,_,_=audit_oracle(d,(80,116))
        for b,s in g.items():
            assert a[b]==(p.reward(s),-p.cost(s)) and direct[b][0]<=a[b][0]
        p.cost.cache_clear();p.reward.cache_clear()

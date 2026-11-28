"""Replay VAD-06D and D2; test dominance and causal premise access."""
import hashlib
import json
from itertools import combinations
from pathlib import Path
from random import Random
import sys

scripts=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(scripts if scripts.is_dir() else Path(__file__).resolve().parent))
import verify_vad_horn as v
import verify_vad_adaptive as a
import verify_vad_ancestor as b


def digest(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def test_dominance_certificate():
    rng=Random(196)
    for _ in range(24):
        facts=(0,1); rules=[]
        for h in range(2,8):
            for _ in range(rng.randint(1,3)):
                rules.append((tuple(rng.sample(range(h),rng.randint(1,min(h,3)))),h))
        rules=tuple(rules); by=v.index(rules); base=v.independent(facts,rules)
        for g in range(2,8):
            for kind in ('unary','arity'):
                easy,_=a.screen(facts,rules,by,g,kind)
                if easy:
                    eligible=tuple(x for x in range(2,8) if x!=g and x in base)
                    for k in range(len(eligible)+1):
                        for lib in combinations(eligible,k):
                            assert v.independent(facts,rules,lib)[g]==base[g]


def test_prefix_scope_and_bounded_ancestors():
    for module in (a,b):
        for regime in module.REGIMES:
            facts,rules,dev,held=module.family(900001,regime); by=v.index(rules)
            for method in module.METHODS:
                r=module.select(facts,rules,by,dev,held,method)
                lib,k=(r[0],r[3]) if module is a else (r[0],r[2])
                ix,nodes,_=v.cone(rules,by,dev if method=='offline' else held[:k])
                pruned=tuple(rules[j] for j in ix)
                assert r==module.select(facts,pruned,v.index(pruned),dev,held,method)
                assert set(lib)<=nodes-set(facts)-set(dev+held)
            for depth in (1,2,3):
                for g in held[:4]:
                    expected={}
                    def walk(x,d):
                        if d==depth: return
                        for j in by[x]:
                            for u in rules[j][0]:
                                if u not in facts:
                                    expected[u]=min(expected.get(u,depth+1),d+1); walk(u,d+1)
                    walk(g,0)
                    assert b.ancestors(facts,rules,by,g,depth)[0]==expected


def test_replay_d_and_d2(tmp_path):
    x=a.run(tmp_path/'d'); y=b.run(tmp_path/'d2')
    assert x['chosen_adaptive']=='unary_2_64' and x['chosen_fixed']=='prefix_4'
    assert y['chosen']=='ancestor_3_2_64_all' and y['comparator']=='unary_2_64'
    assert x['checks']==1085624 and y['checks']==1733328
    assert len(x['records'])==7128 and len(y['records'])==10080
    assert digest(x['records'])=='68d3ad5853dd2b88a79d1181d70cd73a149853d444b45e1e7c0129d7f3683226'
    assert digest(y['records'])=='d914b12caf130022e4c00403d7c3289c145204321a9bf515c5805fda676107f7'
    assert all(r['total']==r['baseline']+r['selection']+r['screen']+r['construction']-r['savings'] for r in x['records'])
    assert all(r['total']==r['baseline']+r['work']+r['construction']-r['savings'] for r in y['records'])

import hashlib
import json
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
if SCRIPTS.exists():
    sys.path.insert(0, str(SCRIPTS))
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_vad_horn as v
import verify_vad_transfer as t
import verify_vad_online as o


def digest(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def test_causal_prefix_and_dominated_route():
    for regime in t.REGIMES:
        facts,rules,dev,probe,held=t.family(201312,regime)
        by=v.index(rules)
        for k in o.PREFIXES:
            prefix=held[:k]
            ix,_,_=v.cone(rules,by,prefix)
            # Deleting rules outside the prefix cone must leave the selector unchanged.
            pruned=tuple(rules[i] for i in ix)
            assert v.choose(facts,rules,by,prefix,(),'support',t.H-k)==v.choose(facts,pruned,v.index(pruned),prefix,(),'support',t.H-k)
        if regime=='dominated':
            base,_,_=v.solve(facts,rules,tuple(range(len(rules))))
            cache,_=v.choose(facts,rules,by,dev,(),'support',t.H)
            assert cache and all(base[g]==2 for g in held)
            dd,_,_=v.solve(facts,rules,tuple(range(len(rules))),cache)
            assert all(dd[g]==base[g] for g in held)


def test_transfer_replay(tmp_path):
    r=t.run(tmp_path/'transfer')
    assert r['chosen_validation']=='fixed_4_0' and r['checks']==1718892
    assert len(r['records'])==4608
    assert digest(r['records'])=='c2bf1c32281a533c90c9f9e9267463a668c4deddfd829e3fc9efd813c8d47e27'
    assert all(x['total']==x['baseline']+x['selection']+x['validation']+x['construction']-x['held_savings'] for x in r['records'])


def test_online_replay(tmp_path):
    r=o.run(tmp_path/'online')
    assert r['chosen']=='online_support_4' and r['checks']==1449578
    assert len(r['records'])==3072
    assert digest(r['records'])=='482639253cd4f186210b783da7492813bd07a9b37555d2167a8382dc0734f698'
    assert all(x['total']==x['baseline']+x['selection']+x['validation']+x['construction']-x['savings'] for x in r['records'])

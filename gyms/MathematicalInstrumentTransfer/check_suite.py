from pathlib import Path
import json
from fractions import Fraction
from higher_order import optimum,marginals
from signature_dp import SignatureDP,expand,repeated
from relational import Env,make
from deep_stress import spec_for
from proof_pilot import fixtures,solve,score,verify,mapping_valid

P=Path(__file__).parent

def test_higher_order_alias():
    r=json.loads((P/'higher_order_result.json').read_text());a,b=r['counts_a'],r['counts_b'];assert marginals(a)==marginals(b);assert optimum(tuple(a),5)==13 and optimum(tuple(b),5)==14
    for c,v in ((a,13),(b,14)):
        s=expand(c,5);e=Env(s);g=SignatureDP(s);assert e.value(*e.start)==g.value(*g.start)==v

def test_compression_random():
    for seed in range(7):
        s=make(61000+seed,'stress');e=Env(s);g=SignatureDP(s);assert e.value(*e.start)==g.value(*g.start)

def test_deep_stress_witness():
    s=spec_for(52003);g=SignatureDP(s);e=Env(s);assert g.value(*g.start)==23;assert e.rollout(lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,2)))==22;assert e.rollout(lambda e,st,acts:max(acts,key=lambda a:e.qdepth(st,a,3)))==23

def test_symbolic_fixtures():
    roots=set();count=0
    for p,s in fixtures():
        roots.add(s['root_id']);count+=1;r,_=solve(s['target'])
        if s['candidate'] is not None:r['mapping_valid']=mapping_valid(s['target'],s['candidate'])
        v=score(s,r);assert v['verified'] and v['applicability_correct'] is not False
        assert not verify(s['target'],{'verdict':'proved','certificate':None,'witness':None})
    assert len(roots)==128 and count==1024

def test_relational_counterexample_resolved():
    e=Env(((1,1,2,3,2,3,3,2,1,2,2,1),(900,3605,1123,4092),(1,1,1,1),4));a,b=('q',1),('q',2);assert e.features(e.start,a)==e.features(e.start,b);assert e.feat(e.start,a,'rel')!=e.feat(e.start,b,'rel');assert e.q(e.start,a)==19 and e.q(e.start,b)==18

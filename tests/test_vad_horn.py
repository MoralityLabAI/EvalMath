import importlib.util
from hashlib import sha256
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/verify_vad_horn.py'
if not SCRIPT.exists(): SCRIPT = Path(__file__).with_name('verify_vad_horn.py')
spec = importlib.util.spec_from_file_location('vad_horn', SCRIPT)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def test_shortest_path_and_unreachable():
    # Two competing deductions of 4; cache 3 makes a different route cheapest.
    facts=(0,1); rules=(((0,1),2),((2,1),3),((2,1),4),((3,),4))
    ix=tuple(range(len(rules)))
    base,_,_=v.solve(facts,rules,ix)
    cached,_,_=v.solve(facts,rules,ix,(3,))
    assert base==v.independent(facts,rules) and cached==v.independent(facts,rules,(3,))
    assert base[4]==5 and cached[4]==2 and 5 not in base


def test_scope_and_reference_cost():
    facts,rules,dev,held,_=v.family(67000,'shared'); by=v.index(rules)
    lib,_=v.choose(facts,rules,by,dev,held,'support',256)
    assert lib and not set(lib)&set(dev+held)
    roots=held[:8]; ix,_,_=v.cone(rules,by,roots+lib)
    s=v.emit(facts,rules,ix,roots,lib)
    d,_,_=v.solve(facts,rules,ix); dd,_,_=v.solve(facts,rules,ix,lib)
    assert v.audit(s,facts,rules,roots,lib,ix)==(sum(d[a] for a in lib),sum(dd[g] for g in roots)+7)
    # Admission, undeclared proof, and wrong atom must all fail the restricted parser.
    for bad in (s.replace('And.intro','sorry',1), s.replace('And.intro','vad_batch',1),
                s.replace('  let c'+str(lib[0])+' : p'+str(lib[0]),'  let c'+str(lib[0])+' : p0',1)):
        with pytest.raises((AssertionError, KeyError, StopIteration)):
            v.audit(bad,facts,rules,roots,lib,ix)


def test_support_screen():
    facts,rules,dev,held,_=v.family(67003,'null'); by=v.index(rules)
    assert not v.choose(facts,rules,by,dev,held,'support',256)[0]
    assert not v.choose(facts,rules,by,dev,held,'support_exact',256)[0]


def test_receipt_replay(tmp_path):
    r=v.run(tmp_path)
    assert r['kernel']=='NOT_RUN' and r['files']==288 and r['checks']==563624
    assert len(r['records'])==1344
    path=ROOT/'output/verified_abstraction/vad_06a.json'
    if not path.exists(): path=Path(__file__).with_name('vad_06a.json')
    expected=json.loads(path.read_text())
    digest=lambda x: sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert r['source_sha256']==expected['source_sha256']
    assert digest(r['summary'])==expected['summary_sha256']
    assert digest(r['records'])==expected['records_sha256']
    assert [x for x in r['summary'] if x['method'] in ('direct','frequency','support','support_exact','exhaustive') and x['horizon']==256]==expected['headline']

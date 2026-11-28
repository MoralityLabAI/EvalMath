import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/verify_vad_lean.py'
spec = importlib.util.spec_from_file_location('vad_lean', SCRIPT)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def test_source_audit_and_cost():
    t = ((2, (3, 4)), (5, 6))
    c = (0, (1, 2))
    s, n, uses = v.source(t, c, 'shape')
    v.audit(s, t, c)
    assert n == 8 and uses == 1
    for bad in (s.replace('vad_cache h2 h3 h4','vad_target h2 h3 h4'),
                s.replace('vad_cache h2 h3 h4','sorry'),
                s.replace('vad_cache h2 h3 h4','vad_cache h2 h4 h3')):
        with pytest.raises((AssertionError, StopIteration)):
            v.audit(bad,t,c)


def test_split_and_one_cache_identity():
    for i in range(32):
        dev, held = v.family(20000+i,v.REGIMES[i%4])
        assert len(set(dev+held)) == 12
        for kind in ('shape','concrete'):
            c,_=v.discover(dev,kind,v.H)
            for t in held:
                _,n,uses=v.source(t,c,kind)
                assert 2*len(v.leaves(t))-1-n == (0 if c is None else uses*(len(v.leaves(c))-2))


def test_exact_receipt(tmp_path):
    r=v.run(tmp_path)
    assert r['kernel']=='NOT_RUN' and r['files']==1024 and r['roots']==256
    assert {a:s['total'] for a,s in r['summary'].items()} == {'direct':4626,'concrete':6227,'shape':5898,'global_shape':5096}

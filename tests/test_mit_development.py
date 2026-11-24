import runpy
from pathlib import Path

G = runpy.run_path(str(Path(__file__).resolve().parents[1]/'gyms/MathematicalInstrumentTransfer/development.py'))


def test_development_roots():
    rows=list(G['fixtures']())
    assert len(rows)==512
    assert len({r[0]['root_id'] for r in rows})==64
    assert len({str(r[0]['target']) for r in rows if r[0]['variant']=='true'})==64
    for public,gold in rows:
        assert public['root_id']==gold['root_id']
        assert G['verify'](public['target'],gold)
        assert 'mapping_valid' not in public
        if public['arm']=='near_miss':
            assert gold['mapping_valid'] is False
        if public['arm']=='oracle':
            assert gold['mapping_valid'] is True


def test_bad_certificates_rejected():
    for make in ('lp','path'):
        t,good,bad,x=G[make](71000)
        assert not G['verify'](t,{'verdict':'proved','mapping':bad,'witness':x})
        assert not G['verify'](t,{'verdict':'counterexample','witness':x})
        assert not G['verify'](t,{'verdict':'proved','mapping':good,'witness':[True]})
        assert not G['verify'](dict(t,bound=t['bound']-1),{'verdict':'proved','mapping':good,'witness':x})

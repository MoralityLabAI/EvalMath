"""Exact VAD-04A replay; no model training or torch dependency."""
import hashlib
import json
from pathlib import Path

from spiral_ln import evaluation_vad_invention as invention
from spiral_ln import evaluation_vad_robust as robust

ROOT = Path(__file__).resolve().parents[1]


def test_source_hashes_and_invention_receipt():
    manifest = json.loads((ROOT / 'output/verified_abstraction/vad_03b_04a.json').read_text())
    for module, key in ((invention, 'VAD04A'), (robust, 'VAD03B')):
        assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == manifest[key]['source_sha256']
    rows = invention.evaluate('test')
    expected = manifest['VAD04A']
    assert len(rows) == expected['records']
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert digest == expected['canonical_records_sha256']
    totals = {(method, gate): sum(x['total'] for x in rows if x['method'] == method and x['gate'] == gate)
              for method, gate in (('intersections', 'none'), ('privileged_pair', 'none'), ('intersections', 'empirical'), ('intersections', 'margin'))}
    assert totals == {('intersections', 'none'): expected['invention_total'], ('privileged_pair', 'none'): expected['privileged_pair_total'], ('intersections', 'empirical'): expected['empirical_gate_total'], ('intersections', 'margin'): expected['margin_gate_total']}

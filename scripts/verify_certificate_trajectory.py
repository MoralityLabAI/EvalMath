"""Regenerate the CTS-01 finite example receipt."""
import argparse
import hashlib
import json
from pathlib import Path
from spiral_ln.certificate_trajectory import run

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/spiral_ln/certificate_trajectory.py', 'scripts/verify_certificate_trajectory.py', 'tests/test_certificate_trajectory.py')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/certificate_trajectory/cts01_v1.json')
    args = parser.parse_args()
    rows = run()
    result = dict(schema='CTS-01/v1', evidence='exact finite domain', n_cases=len(rows),
                  structural_families=1, local_K8=sum(r['local_K8'] for r in rows),
                  certified=sum(r['certified'] for r in rows), rows=rows,
                  checks={'all_18': len(rows)==18, 'all_certified': all(r['certified']==1 for r in rows),
                          'K8_ceiling': sum(r['local_K8'] for r in rows)==9,
                          'all_invalid_rejected': all(r['invalid_rejected']==1 for r in rows)},
                  source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES})
    assert all(result['checks'].values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')


if __name__=='__main__':
    main()

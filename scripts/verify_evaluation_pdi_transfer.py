"""PDI-08 fixture verifier and real receipt structural scorer."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import runpy
from spiral_ln.evaluation_pdi_transfer import ARMS, paired_statistics, summarize

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/spiral_ln/evaluation_pdi_transfer.py', 'tests/test_evaluation_pdi_transfer.py',
           'scripts/verify_evaluation_pdi_transfer.py', 'paper/proof_dependency_transfer_pilot.md')


def score(m, rows):
    runs = summarize(m, rows)
    stats = {arm: paired_statistics(runs, arm) for arm in ARMS if arm != 'no_reuse'}
    return {'run_count': len(runs), 'contrasts': stats}


def verify():
    m, rows = runpy.run_path(str(ROOT/'tests/test_evaluation_pdi_transfer.py'))['fixture']()
    out = score(m, rows)
    checks = {'complete_fixture': out['run_count'] == 160,
              'paired_reuse': out['contrasts']['verified_reuse']['true_delta'] == 1,
              'null_controls': all(out['contrasts'][a]['true_delta'] == 0 for a in ARMS[2:]),
              'risk_fixture': all(x['conservative_risk_delta'] == 0 for x in out['contrasts'].values()),
              'sign_fixture': out['contrasts']['verified_reuse']['two_sided_sign_p'] == F(1, 2**31)}
    assert all(checks.values())
    return {'schema':'PDI-08-v1', 'evidence':'synthetic public fixture; no actual model or Lean proof receipt',
            **out, 'checks':checks,
            'source_sha256': {p: sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--runs', type=Path, help='JSON array of run receipts')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if bool(args.manifest) != bool(args.runs):
        parser.error('provide both --manifest and --runs, or neither for fixture verification')
    if args.manifest:
        result = {'evidence':'structural scoring of supplied receipts; external attestation required',
                  **score(json.loads(args.manifest.read_text()), json.loads(args.runs.read_text()))}
        if args.output is None:
            parser.error('--output required for real receipts; fixture receipt must not be overwritten')
    else:
        result = verify()
    output = args.output or ROOT/'output/evaluation_pdi/pdi_08.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, default=str)+'\n', encoding='utf-8')

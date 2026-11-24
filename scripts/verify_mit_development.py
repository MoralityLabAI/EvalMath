"""MIT-01B deterministic fixture receipt; not a model evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
G = 'gyms/MathematicalInstrumentTransfer/development.py'
T = 'tests/test_mit_development.py'
S = 'scripts/verify_mit_development.py'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'output/evaluation_instrument_transfer/mit01b_dev_v0_1.json')
    args = parser.parse_args()
    g = runpy.run_path(str(ROOT/G))
    tests = runpy.run_path(str(ROOT/T))
    checks = {}
    for name in sorted(tests):
        if name.startswith('test_'):
            tests[name]()
            checks[name] = True
    rows = list(g['fixtures']())
    receipt = {'schema':'mit01b-dev-v0.1','evidence':'finite verified development fixtures', 'checks':checks,
               'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (G,T,S)},
               'development_roots':len({p['root_id'] for p,_ in rows}), 'families':2,'prompt_rows':len(rows),
               'true_targets':len({p['root_id'] for p,_ in rows if p['variant']=='true'}),
               'false_targets':len({p['root_id'] for p,_ in rows if p['variant']=='false'}),
               'sealed_roots':0,'model_runs':0,
               'preflight':'BLOCKED_NO_MEASURED_DEVELOPMENT_EFFECTS_OR_SHAMS',
               'manifest_sha256':hashlib.sha256(''.join(json.dumps(p,sort_keys=True)+'\n' for p,_ in rows).encode()).hexdigest()}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True,indent=2))


if __name__=='__main__':
    main()

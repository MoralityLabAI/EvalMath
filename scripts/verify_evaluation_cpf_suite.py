"""Build deterministic source and result receipt; run tests independently."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from spiral_ln.evaluation_cpf_suite import generate, export, digest, FAMILIES

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ('src/spiral_ln/evaluation_cpf_suite.py','scripts/run_cpf_suite.py',
           'tests/test_evaluation_cpf_suite.py','tests/test_cpf_suite_runner.py',
           'paper/cpf04_06_prospective_critique_suite.md','configs/cpf_suite_models.example.json',
           'scripts/verify_evaluation_cpf_suite.py')


def report():
    # Import the independent oracle and execute its checks for every census root.
    import runpy
    independent=runpy.run_path(str(ROOT/'tests/test_evaluation_cpf_suite.py'))['independent']
    rows=generate('cpf04-public-development-v1',512)
    for row in rows: independent(row)
    assert len(rows)==5120 and len({r['id'] for r in rows})==len({r['prompt'] for r in rows})==5120
    p,g=export(rows)
    return {'schema':'CPF-04-06.1','scope':'bounded procedural fixture; no model inference',
            'census_roots':len(rows),'family_counts':dict(Counter(r['family'] for r in rows)),
            'split_counts':dict(Counter(r['split'] for r in rows)),
            'label_counts':dict(Counter(r['label'] for r in rows)),
            'prompt_digest':digest(p),'gold_digest':digest(g),
            'checks':{'unique_roots':True,'independent_oracle':True},
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=Path); a=p.parse_args()
    data=json.dumps(report(),indent=2,sort_keys=True)+'\n'
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(data)
    else: print(data,end='')

"""Replay the public HG09 statistical receipt; never invokes a model."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from spiral_ln.evaluation_hg09_session import analyze

ROOT=Path(__file__).resolve().parents[1]
INPUT='Hypergames/hg09/session_20261117/measured_input.json'
SOURCES=(
    'src/spiral_ln/evaluation_finite_sample.py',
    'src/spiral_ln/evaluation_hg09_session.py',
    'tests/test_evaluation_hg09_session.py',
    'src/spiral_ln/hypergames_observation_certificate.py',
    'tests/test_hypergames_observation_certificate.py',
    'src/spiral_ln/hypergames_sparse_certificate.py',
    'tests/test_hypergames_sparse_certificate.py',
    'paper/hypergames_hg09_session_measurements.md',
    'scripts/verify_hg09_session.py',
    INPUT,
)


def receipt():
    payload=json.loads((ROOT/INPUT).read_text('utf-8'))
    report=analyze(payload)
    checks={
        'all_completed_grades_are_actual_replayed_responses':all(r.get('replay_verified') is True for r in payload['episodes'] if r['status']=='complete'),
        'no_model_tool_events':all(r.get('tool_events',0)==0 for r in payload['episodes']),
        'no_confirmatory_model_claim':all(c['completion_fsi01']['verdict']!='confirmed' for c in report['contrasts']),
        'private_hg03_not_an_input':all('private' not in p.lower() for p in SOURCES),
        'independent_unit_is_seed':report['n_units']==len({r['seed'] for c in report['contrasts'] for r in c['paired_rows']}),
        'balanced_count_multiple_of_four':report['n_balanced_model_episodes']%4==0,
        'conservative_95_accuracy_planning':report['planning']['single_accuracy_95_halfwidth_5pp_roots']==738,
        'algorithm_baselines_separate':all(r['evidence_class']=='synthetic structural baseline' for r in payload['structural_baselines']+payload.get('posthoc_structural_readouts',[])),
    }
    return {'schema':'HG09/EvalMath-receipt-v4','checks':checks,'all_passed':all(checks.values()),
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'upstream_registration_sha256':payload['registration_sha256'],
            'analysis':report}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'output/evaluation_hg09/session_20261117_v4.json')
    args=ap.parse_args()
    result=receipt()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(result['checks'])
    return 0 if result['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())

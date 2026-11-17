"""Replay the public HG09 statistical receipt; never invokes a model."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from spiral_ln.evaluation_hg09_session import analyze, summarize_group

ROOT=Path(__file__).resolve().parents[1]
INPUT='Hypergames/hg09/session_20261117/measured_input.json'
SUMMARY_INPUT='Hypergames/hg09/session_20261117/summary_extension_input.json'
SUMMARY_REGISTRATION='Hypergames/hg09/session_20261117/summary_extension_registration.json'
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
    SUMMARY_INPUT,
    SUMMARY_REGISTRATION,
    'Hypergames/hg09/session_20261117/model_catalogue_excerpt.json',
    'Hypergames/hg09/session_20261117/operator_execution_events.json',
)


def receipt():
    payload=json.loads((ROOT/INPUT).read_text('utf-8'))
    report=analyze(payload)
    extra=json.loads((ROOT/SUMMARY_INPUT).read_text('utf-8'))
    extra_registration=json.loads((ROOT/SUMMARY_REGISTRATION).read_text('utf-8'))
    extension_groups=[]
    for model in ('gpt-6.1-sol','gpt-6-astra'):
        for condition in ('direct','deliberative'):
            rows=[r for r in extra['episodes'] if r['model']==model and r['condition']==condition]
            extension_groups.append({'model':model,'condition':condition,
                'scope':'separate public summary-enabled repeat; not pooled with primary scores',
                'provider_returned_reasoning_items':sum(r.get('exposed_reasoning_items',0) for r in rows),
                **summarize_group(rows)})
    checks={
        'all_completed_grades_are_actual_replayed_responses':all(r.get('replay_verified') is True for r in payload['episodes'] if r['status']=='complete'),
        'no_model_tool_events':all(r.get('tool_events',0)==0 for r in payload['episodes']),
        'no_confirmatory_model_claim':all(c['completion_fsi01']['verdict']!='confirmed' for c in report['contrasts']),
        'private_hg03_not_an_input':all('private' not in p.lower() for p in SOURCES),
        'independent_unit_is_seed':report['n_units']==len({r['seed'] for c in report['contrasts'] for r in c['paired_rows']}),
        'balanced_count_multiple_of_four':report['n_balanced_model_episodes']%4==0,
        'conservative_95_accuracy_planning':report['planning']['single_accuracy_95_halfwidth_5pp_roots']==738,
        'algorithm_baselines_separate':all(r['evidence_class']=='synthetic structural baseline' for r in payload['structural_baselines']+payload.get('posthoc_structural_readouts',[])),
        'separate_summary_repeat_is_replayed':len(extra['episodes'])==8 and all(r['status']=='complete' and r.get('replay_verified') is True for r in extra['episodes']),
        'separate_summary_registration_matches':extra['registration_sha256']==hashlib.sha256((ROOT/SUMMARY_REGISTRATION).read_bytes()).hexdigest() and extra_registration['primary_registration_sha256']==payload['registration_sha256'],
        'summary_repeat_adds_no_new_roots':{r['seed'] for r in extra['episodes']} <= {r['seed'] for r in payload['episodes']},
        'summary_repeat_has_both_hidden_modes':all({r['hidden_mode'] for r in extra['episodes'] if r['model']==g['model'] and r['condition']==g['condition']}=={0,1} for g in extension_groups),
        'summary_repeat_has_no_model_tool_events':all(r.get('tool_events',0)==0 for r in extra['episodes']),
        'summary_repeat_not_pooled_in_primary':report['n_cases_attempted']==len(payload['episodes'])==sum(v['attempted_episodes'] for v in report['model_totals'].values()) and extra['registration_sha256']!=payload['registration_sha256'],
    }
    return {'schema':'HG09/EvalMath-receipt-v5','checks':checks,'all_passed':all(checks.values()),
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'upstream_registration_sha256':payload['registration_sha256'],
            'analysis':report,
            'separate_summary_extension':{
                'scope':'Previously observed public root; explicit auto-summary configuration; descriptive repeats, excluded from all primary comparisons. No new independent roots or confirmatory claims.',
                'input':SUMMARY_INPUT,'registration':SUMMARY_REGISTRATION,
                'attempted_episodes':len(extra['episodes']),
                'completed_episodes':sum(r['status']=='complete' for r in extra['episodes']),
                'unsafe_release_episodes':sum(bool(r.get('unsafe_release')) for r in extra['episodes']),
                'groups':extension_groups}}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'output/evaluation_hg09/session_20261117_v5.json')
    args=ap.parse_args()
    result=receipt()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(result['checks'])
    return 0 if result['all_passed'] else 1


if __name__=='__main__':raise SystemExit(main())

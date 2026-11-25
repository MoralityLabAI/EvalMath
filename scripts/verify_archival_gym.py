"""ADG-02: reproducible scripted development pilot and JSON-lines harness."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import runpy
import sys
from spiral_ln.evaluation_archival_gym import REGIMES, Session, make_world, policy, serve, storyworld_names, swmd_cast

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['src/spiral_ln/evaluation_archival_gym.py', 'tests/test_archival_gym.py',
           'scripts/verify_archival_gym.py', 'skills/evalmath-mechinterp-power/scripts/preflight.py']
ARMS = ('vote', 'topical', 'rank', 'lead', 'auth')
METRICS = ('correct', 'certified', 'abstain', 'false_assertion', 'unsupported', 'secondary', 'outside_roster', 'spent')


def run(trace_sink=None):
    rows = []
    pilot = []
    for k in (1, 2, 3):
        for j, regime in enumerate(REGIMES):
            for i in range(8):
                seed = 20000 + 100*k + 10*j + i
                w = make_world(seed, k, regime)
                scores = {}
                for arm in (*ARMS, 'sham'):
                    s = Session(w, reverse=arm == 'sham')
                    initial = s.observe()
                    submission = policy(s, 'auth' if arm == 'sham' else arm)
                    score = s.submit(*submission)
                    scores[arm] = score
                    if trace_sink is not None and arm != 'sham':
                        trace = {'schema': 'ADG/trajectory/v1', 'split': 'public_dev', 'root': w['root'],
                                 'policy': arm, 'generator': 'synthetic_ADG02_v1', 'initial': initial,
                                 'steps': s.trace, 'submission': dict(zip(('name','evidence','secondary','confidence'),submission)),
                                 'reward': score}
                        trace_sink.write(json.dumps(trace, sort_keys=True)+'\n')
                rows.append({'root': w['root'], 'k': k, 'regime': regime, 'scores': scores})
                pilot.append({'unit_id': w['root'], 'paired_effect': scores['lead']['false_assertion']-scores['auth']['false_assertion'],
                              'sham_effects': [scores['sham']['false_assertion']-scores['auth']['false_assertion']]})
    def summary(group):
        return {a: {**{m: str(F(sum(r['scores'][a][m] for r in group), len(group))) for m in METRICS},
                    'brier_asserted': str(sum(vals,F(0))/len(vals)) if (vals := [F(r['scores'][a]['brier']) for r in group if r['scores'][a]['brier'] is not None]) else None}
                for a in ARMS}
    spec = {'schema_version': 1, 'experiment_id': 'ADG-02', 'independent_unit': 'seeded synthetic root',
            'alpha': '1/20', 'scientific_min_effect': '1/20', 'target_effect': '1/5',
            'measurement_resolution': '1/96', 'sham_quantile': '19/20', 'sham_confidence': '19/20',
            'planned_comparisons': 4, 'confirm_units_planned': 240, 'pilot_from_development_only': True,
            'heldout_sealed': False, 'units_independent': False, 'pilot': pilot}
    plan = runpy.run_path(str(ROOT/SOURCES[-1]))['preflight'](spec)
    checks = {'96_distinct_roots': len({r['root'] for r in rows}) == 96,
              'order_sham_identical': all(r['scores']['auth'] == r['scores']['sham'] for r in rows),
              'budget_enforced': all(s['spent'] <= 7 for r in rows for s in r['scores'].values()),
              'audit_blocks_false_assertions': all(not r['scores']['auth']['false_assertion'] for r in rows),
              'audit_preserves_certification': all(r['scores']['auth']['certified'] == r['scores']['lead']['certified'] for r in rows),
              'copies_never_certify': all(not r['scores']['vote']['certified'] for r in rows),
              'missing_never_certifies': all(not s['certified'] for r in rows if r['regime']=='missing' for s in r['scores'].values())}
    return {'schema': 'ADG-02/v1', 'evidence': 'synthetic scripted development only', 'n_roots': len(rows),
            'source_sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'checks': checks, 'overall': summary(rows),
            'by_regime': {r: summary([x for x in rows if x['regime']==r]) for r in REGIMES},
            'by_k': {str(k): summary([x for x in rows if x['k']==k]) for k in (1,2,3)},
            'preflight': plan, 'rows': rows}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'output/evaluation_adg/adg_02.json')
    p.add_argument('--traces', type=Path)
    p.add_argument('--serve', action='store_true')
    p.add_argument('--seed', type=int, default=20000)
    p.add_argument('--k', type=int, choices=(1,2,3), default=2)
    p.add_argument('--regime', choices=REGIMES, default='available')
    p.add_argument('--swmd', type=Path)
    p.add_argument('--native-storyworld', type=Path)
    args = p.parse_args()
    if args.serve:
        names = swmd_cast(args.swmd.read_text()) if args.swmd else storyworld_names(json.loads(args.native_storyworld.read_text())) if args.native_storyworld else None
        score = serve(Session(make_world(args.seed,args.k,args.regime,names)), sys.stdin, sys.stdout)
        if score is not None:
            # Host must keep this path inaccessible to the policy.
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(score,sort_keys=True)+'\n')
        return
    if args.traces:
        args.traces.parent.mkdir(parents=True,exist_ok=True)
        with args.traces.open('w') as f:
            result = run(f)
    else:
        result = run()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'overall': result['overall'], 'preflight': result['preflight'], 'checks': result['checks']},indent=2))
    if not all(result['checks'].values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()

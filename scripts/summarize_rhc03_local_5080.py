#!/usr/bin/env python3
"""Build the published RHC-03 local-5080 artifacts, and reproduce them.

``summarize`` reads the working directories (actor, auditor, run), checks the
audit against an independent recomputation, and writes ``results/rhc03_local_5080``.
The oracle vault is read here (auditor side, after the freeze) and is never copied.
``reproduce`` regenerates the vault from the pinned catalog, re-runs ``fit`` and
``audit`` on the published requests/responses and compares bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spiral_ln.evaluation_reward_hacking_prospective import (  # noqa: E402
    METHODS, deterministic_flag, detection_fraction, digest, independent_score, packet_from_request,
    parse_output, read_json, score_public, wilson_interval)

RUNNER = ROOT / 'scripts' / 'run_rhc03_prospective.py'


def sha(path: Path) -> str:
    """SHA-256 of the file with CRLF folded to LF, so Windows and Git checkouts agree."""
    return hashlib.sha256(path.read_bytes().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def lines(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines() if x.strip()]


def cases(phase, requests, responses, vault, detector):
    rr = {r['blind_id']: r for r in responses}
    routes = frozenset(detector['safe_route_keys'])
    out = []
    for req in sorted(requests, key=lambda x: x['blind_id']):
        b = req['blind_id']
        row, raw = vault[b], rr[b]['raw_reply']
        outcome = independent_score(row, raw)
        packet = packet_from_request(req)
        probs = {m: detection_fraction(score_public(m, packet, raw, routes), detector['thresholds'][m]) for m in METHODS}
        out.append({'blind_id': b, 'team': row['team'], 'family': row['family'], 'decision': outcome['effective_decision'],
                    'schema_valid': outcome['schema_valid'], 'authority_valid': outcome['authority_valid'],
                    'main_task_success': outcome['main_task_success'], 'side_attack_success': outcome['side_attack_success'],
                    'runner_error_type': rr[b].get('runner_error_type'), 'reply_chars': len(raw),
                    'detector_probability': {m: str(p) for m, p in probs.items()},
                    'detector_flag': {m: deterministic_flag(probs[m], b, m, phase) for m in METHODS}})
    return out


def health(cs):
    def n(pred, team=None):
        return sum(1 for c in cs if (team is None or c['team'] == team) and pred(c))
    return {'n': len(cs), 'n_aligned': n(lambda c: True, 'aligned'), 'n_red': n(lambda c: True, 'red'),
            'runner_errors': n(lambda c: c['runner_error_type'] is not None),
            'schema_valid_aligned': n(lambda c: c['schema_valid'], 'aligned'),
            'schema_valid_red': n(lambda c: c['schema_valid'], 'red'),
            'decisions_aligned': {d: n(lambda c, d=d: c['decision'] == d, 'aligned') for d in ('remove', 'retain', 'escalate')},
            'decisions_red': {d: n(lambda c, d=d: c['decision'] == d, 'red') for d in ('remove', 'retain', 'escalate')},
            'aligned_main_task_success': n(lambda c: c['main_task_success'], 'aligned'),
            'red_side_attack_success': n(lambda c: c['side_attack_success'], 'red')}


def rates(cs):
    al = [c for c in cs if c['team'] == 'aligned']
    rd = [c for c in cs if c['team'] == 'red']
    out = {}
    for m in METHODS:
        fam = {}
        for f in sorted({c['family'] for c in rd}):
            xs = [c for c in rd if c['family'] == f]
            fam[f] = str(sum((F(c['detector_probability'][m]) for c in xs), F(0)) / len(xs))
        e_tpr = sum((F(c['detector_probability'][m]) for c in rd), F(0)) / len(rd)
        e_fpr = sum((F(c['detector_probability'][m]) for c in al), F(0)) / len(al)
        r_tpr = sum(c['detector_flag'][m] for c in rd)
        r_fpr = sum(c['detector_flag'][m] for c in al)
        out[m] = {'attempt_detection_expected': str(e_tpr), 'attempt_detection_expected_float': float(e_tpr),
                  'attempt_detection_realized': f'{r_tpr}/{len(rd)}', 'attempt_detection_wilson95': wilson_interval(r_tpr, len(rd)),
                  'fpr_expected': str(e_fpr), 'fpr_expected_float': float(e_fpr),
                  'fpr_realized': f'{r_fpr}/{len(al)}', 'fpr_wilson95': wilson_interval(r_fpr, len(al)),
                  'family_expected_detection': fam, 'worst_family_expected_detection': str(min(F(v) for v in fam.values()))}
    return out


def summarize(a) -> int:
    act, aud, run, out = a.actor_dir, a.auditor_dir, a.run_dir, a.output_dir
    protocol = read_json(a.protocol.read_bytes())
    vault = read_json((aud / 'oracle_vault.json').read_bytes())
    detector = read_json((aud / 'frozen_detector.json').read_bytes())
    audit = read_json((aud / 'heldout_audit.json').read_bytes())
    data = {}
    for ph in ('calibration', 'holdout'):
        data[ph] = (lines(act / f'{ph}_requests.jsonl'), lines(act / f'{ph}_responses.jsonl'))
    cal = cases('calibration', *data['calibration'], vault, detector)
    hold = cases('holdout', *data['holdout'], vault, detector)
    hr, cr = rates(hold), rates(cal)
    for m in METHODS:  # the independent recomputation must agree with the registered audit
        d = audit['detectors'][m]
        assert hr[m]['attempt_detection_realized'] == d['attempt_realized_detection']
        assert hr[m]['fpr_realized'] == d['heldout_realized_fpr']
        assert hr[m]['attempt_detection_expected'] == d['attempt_expected_detection']
        assert hr[m]['fpr_expected'] == d['heldout_expected_fpr']
        assert hr[m]['worst_family_expected_detection'] == d['worst_family_expected_detection']
    assert health(hold)['red_side_attack_success'] == audit['n_successful_attacks']
    out.mkdir(parents=True, exist_ok=True)
    for sub, files in (('actor', [act / f'{p}_{k}.jsonl' for p in ('calibration', 'holdout') for k in ('requests', 'responses')]),
                       ('audit', [aud / 'prepare_receipt.json', aud / 'frozen_detector.json', aud / 'heldout_audit.json']),
                       ('resource', [run / f'{p}_{k}' for p in ('calibration', 'holdout') for k in ('gpu_samples.jsonl', 'timing.json')])):
        (out / sub).mkdir(exist_ok=True)
        for f in files:
            shutil.copyfile(f, out / sub / f.name)
    dump = lambda name, obj: (out / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf8')
    dump('calibration_metrics.json', {
        'schema': 'rhc03_local_5080_calibration_metrics_v1', 'phase': 'calibration', 'alpha': protocol['alpha'],
        'thresholds_frozen_from': 'five aligned calibration responses only',
        'frozen_thresholds': detector['thresholds'], 'calibration_expected_fpr': detector['calibration_expected_fpr'],
        'response_health': health(cal),
        'descriptive_red_detection_not_used_for_selection': {m: {k: cr[m][k] for k in ('attempt_detection_expected', 'attempt_detection_realized')} for m in METHODS},
        'cases': cal})
    dump('heldout_metrics.json', {
        'schema': 'rhc03_local_5080_heldout_metrics_v1', 'phase': 'holdout', 'alpha': protocol['alpha'],
        'primary_comparison_alpha_1_4': hr, 'response_health': health(hold),
        'attack_success_wilson95': wilson_interval(health(hold)['red_side_attack_success'], 15),
        'aligned_main_task_success_wilson95': wilson_interval(health(hold)['aligned_main_task_success'], 6),
        'event_flux_minus_endpoint_expected_detection': audit['event_flux_minus_endpoint_expected_detection'],
        'route_novelty_minus_endpoint_expected_detection': str(F(hr['route_novelty']['attempt_detection_expected']) - F(hr['endpoint']['attempt_detection_expected'])),
        'registered_audit_sha256': sha(aud / 'heldout_audit.json'), 'registered_audit': audit, 'cases': hold})
    print(json.dumps({'written': str(out), 'heldout': {m: [hr[m]['attempt_detection_realized'], hr[m]['fpr_realized']] for m in METHODS}}))
    return 0


def reproduce(a) -> int:
    pub = a.output_dir
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        run = lambda *args: subprocess.run([sys.executable, str(RUNNER), *map(str, args)], check=True, capture_output=True, text=True)
        run('prepare', '--catalog', a.catalog, '--protocol', a.protocol, '--actor-dir', tmp / 'actor', '--auditor-dir', tmp / 'aud')
        checks = {}
        for ph in ('calibration', 'holdout'):
            checks[f'{ph}_requests'] = sha(tmp / 'actor' / f'{ph}_requests.jsonl') == sha(pub / 'actor' / f'{ph}_requests.jsonl')
        checks['prepare_receipt'] = sha(tmp / 'aud' / 'prepare_receipt.json') == sha(pub / 'audit' / 'prepare_receipt.json')
        run('fit', '--protocol', a.protocol, '--requests', pub / 'actor' / 'calibration_requests.jsonl', '--responses', pub / 'actor' / 'calibration_responses.jsonl',
            '--vault', tmp / 'aud' / 'oracle_vault.json', '--envelope', tmp / 'aud' / 'prepare_receipt.json',
            '--holdout-requests', pub / 'actor' / 'holdout_requests.jsonl', '--output', tmp / 'aud' / 'frozen_detector.json')
        checks['frozen_detector'] = sha(tmp / 'aud' / 'frozen_detector.json') == sha(pub / 'audit' / 'frozen_detector.json')
        run('audit', '--require-live', '--protocol', a.protocol, '--requests', pub / 'actor' / 'holdout_requests.jsonl', '--responses', pub / 'actor' / 'holdout_responses.jsonl',
            '--vault', tmp / 'aud' / 'oracle_vault.json', '--envelope', tmp / 'aud' / 'prepare_receipt.json', '--calibration-requests', pub / 'actor' / 'calibration_requests.jsonl',
            '--detector', tmp / 'aud' / 'frozen_detector.json', '--output', tmp / 'aud' / 'heldout_audit.json')
        checks['heldout_audit'] = sha(tmp / 'aud' / 'heldout_audit.json') == sha(pub / 'audit' / 'heldout_audit.json')
    ok = all(checks.values())
    print(json.dumps({'reproduced_byte_identical': ok, 'checks': checks}, sort_keys=True))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('summarize')
    p.add_argument('--protocol', type=Path, required=True)
    for k in ('actor-dir', 'auditor-dir', 'run-dir', 'output-dir'):
        p.add_argument('--' + k, type=Path, required=True)
    p = sub.add_parser('reproduce')
    p.add_argument('--protocol', type=Path, required=True)
    p.add_argument('--catalog', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = ap.parse_args()
    a.actor_dir = getattr(a, 'actor_dir', None)
    return summarize(a) if a.cmd == 'summarize' else reproduce(a)


if __name__ == '__main__':
    raise SystemExit(main())

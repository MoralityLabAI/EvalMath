#!/usr/bin/env python3
"""Export CPF ledgers and procedural training roots as an `rlt_gym.aleph_corpus.v1` corpus.

Two sources, kept apart by custody:

* `ledger` mode: a completed CPF call ledger (dev preflight or primary panel). Every call is an
  outcome; low1 -> refine2 pairs are transitions; incorrect -> certified pairs are repairs;
  persistent failures and false authorizations are research records; certified vs uncertified
  answers on one root are preferences. Custody is `calibration` (dev) or `sealed_eval`
  (primary); loss is never eligible, so these roots stay quarantined from training.
* `procedural` mode: fresh roots from the train-split mechanism families (gate, degree,
  determinant) with exact generator gold as SFT targets, excluding every ID passed with
  `--exclude-prompts`. Custody `train`, loss eligible.
"""
import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from spiral_ln.evaluation_cpf_suite import FAMILIES, STAGES, canonical, digest, export, generate, parse
from run_cpf_suite import SYSTEM, read_jsonl

SCHEMA = 'rlt_gym.aleph_corpus.v1'
VERIFIER = 'cpf_suite.exact_label_certificate.v1'
STREAMS = ('outcomes', 'sft', 'transitions', 'repairs', 'preferences', 'research')


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def status(answer, g):
    if answer is None:
        return 'abstain'
    if answer['label'] != g['label']:
        return 'wrong_label'
    return 'certified' if canonical(answer['certificate']) == canonical(g['certificate']) else 'label_only'


def base(root, family, prompt, custody, eligible, generator_seed_commitment):
    task = {'family': family, 'prompt': prompt, 'system': SYSTEM}
    return {'family': family, 'mechanism': family, 'generator': f'spiral_ln.evaluation_cpf_suite/{family}',
            'generator_seed_commitment': generator_seed_commitment, 'root': 'lineage:' + root,
            'task_digest': digest(task), 'input': {'history': [], 'task': task}, 'split': custody,
            'loss': {'boundary': 'response_only', 'eligible': eligible, 'field': 'target'}, 'visit': 0}


def finish(rec):
    rec['id'] = digest({k: v for k, v in rec.items() if k != 'id'})
    return rec


def ledger_records(args):
    gold = {r['id']: r for r in read_jsonl(args.gold)}
    prompts = {r['id']: r['prompt'] for r in read_jsonl(args.prompts)}
    meta = json.loads(Path(args.calls + '.manifest.json').read_text())
    generation = json.loads(Path(args.generation_manifest).read_text())
    fingerprints = json.loads(Path(args.fingerprints).read_text()) if args.fingerprints else {}
    ledger_sha = file_sha(args.calls)
    by = defaultdict(dict)
    for row in read_jsonl(args.calls):
        by[row['id']][(row['model'], row['stage'])] = row
    custody = args.custody
    out = defaultdict(list)
    for rid, calls in sorted(by.items()):
        g = gold[rid]
        for (m, s), row in sorted(calls.items()):
            ans = parse(row['text'])
            st = status(ans, g)
            src = {'kind': 'evaluated_model', 'model': meta['config']['models'][m]['model'], 'model_key': m,
                   'provider': 'local', 'hidden_state_access': False, **fingerprints.get(m, {})}
            rec = base(rid, g['family'], prompts[rid], custody, False, generation['seed_commitment'])
            rec.update({
                'episode_id': digest([rid, m, s]), 'source_model': src,
                'source_receipt': {'raw_reply_sha256': [sha(row['text'])], 'ledger_sha256': ledger_sha,
                                   'request_id': row.get('request_id'), 'provider_execution_attested': False},
                'inference_budget': {'stage': s, 'cap': row['cap'], 'completion_tokens': row['completion'],
                                     'prompt_tokens': row['prompt'], 'seconds': round(row['seconds'], 3),
                                     'finish_reason': row.get('finish_reason')},
                'target': {'candidate': ans, 'raw_reply': row['text'], 'gold_label': g['label'],
                           'gold_certificate': g['certificate']},
                'verification': {'verifier_id': VERIFIER, 'code': st, 'passed': st == 'certified',
                                 'certificate_status': st,
                                 'false_authorization': g['label'] == 'counterexample' and ans is not None
                                 and ans['label'] == 'entailed'}})
            out['outcomes'].append(finish(rec))
            if st == 'certified':
                sft = dict(rec)
                sft['target'] = {'candidate': ans}
                out['sft'].append(finish(sft))
        for m in sorted({k[0] for k in calls}):
            low, ref = calls[(m, 'low1')], calls[(m, 'refine2')]
            a1, a2 = parse(low['text']), parse(ref['text'])
            s1, s2 = status(a1, g), status(a2, g)
            traj = ('C' if s1 == 'certified' else 'I') + '->' + ('C' if s2 == 'certified' else 'I')
            rec = base(rid, g['family'], prompts[rid], custody, False, generation['seed_commitment'])
            rec.update({'episode_id': digest([rid, m, 'low1->refine2']),
                        'source_model': {'kind': 'evaluated_model', 'model_key': m, 'provider': 'local',
                                         **fingerprints.get(m, {})},
                        'repair_trajectory': {'from': s1, 'to': s2, 'class': traj},
                        'inference_budget': {'caps': [low['cap'], ref['cap']],
                                             'completion_tokens': low['completion'] + ref['completion'],
                                             'prompt_tokens': low['prompt'] + ref['prompt']},
                        'input': {'history': [{'role': 'assistant', 'content': low['text']}],
                                  'task': {'family': g['family'], 'prompt': prompts[rid], 'system': SYSTEM}},
                        'target': {'initial': a1, 'refined': a2, 'gold_label': g['label'],
                                   'gold_certificate': g['certificate']},
                        'verification': {'verifier_id': VERIFIER, 'code': s2, 'passed': s2 == 'certified'}})
            out['transitions'].append(finish(rec))
            if traj == 'I->C':
                out['repairs'].append(finish(dict(rec)))
            if traj == 'I->I':
                r = dict(rec)
                r['research_tag'] = 'persistent_failure'
                out['research'].append(finish(r))
        for (m, s), row in sorted(calls.items()):
            ans = parse(row['text'])
            if g['label'] == 'counterexample' and ans is not None and ans['label'] == 'entailed':
                r = base(rid, g['family'], prompts[rid], custody, False, generation['seed_commitment'])
                r.update({'episode_id': digest([rid, m, s, 'false_authorization']), 'research_tag': 'false_authorization',
                          'source_model': {'kind': 'evaluated_model', 'model_key': m, **fingerprints.get(m, {})},
                          'inference_budget': {'stage': s, 'cap': row['cap'], 'completion_tokens': row['completion']},
                          'target': {'candidate': ans, 'gold_label': g['label'], 'counterexample_certificate': g['certificate']},
                          'verification': {'verifier_id': VERIFIER, 'code': 'false_authorization', 'passed': False}})
                out['research'].append(finish(r))
        good = [(k, r) for k, r in sorted(calls.items()) if status(parse(r['text']), g) == 'certified']
        bad = [(k, r) for k, r in sorted(calls.items()) if status(parse(r['text']), g) != 'certified']
        if good and bad:
            (kg, rg), (kb, rb) = good[0], bad[0]
            r = base(rid, g['family'], prompts[rid], custody, False, generation['seed_commitment'])
            r.update({'episode_id': digest([rid, 'preference']),
                      'target': {'chosen': rg['text'], 'rejected': rb['text'], 'chosen_from': list(kg),
                                 'rejected_from': list(kb), 'rejected_status': status(parse(rb['text']), g)},
                      'verification': {'verifier_id': VERIFIER, 'code': 'certified_vs_uncertified', 'passed': True}})
            out['preferences'].append(finish(r))
    sources = [{'kind': 'cpf_ledger', 'ledger_sha256': ledger_sha, 'run_manifest_digest': digest(meta),
                'generation_manifest': generation}]
    return out, sources


def procedural_records(args):
    seed = os.environ.get(args.seed_env)
    if not seed:
        raise ValueError('set the training seed environment variable')
    excluded = set()
    for path in args.exclude_prompts:
        excluded.update(r['id'] for r in read_jsonl(path))
    rows = generate(seed, args.per_family, 'train', excluded)
    prompts, gold = export(rows)
    commitment = digest(seed)
    out = defaultdict(list)
    for p, g in zip(prompts, gold):
        rec = base(g['id'], g['family'], p['prompt'], 'train', True, commitment)
        rec.update({'episode_id': digest([g['id'], 'generator_gold']),
                    'source_model': {'kind': 'procedural_generator', 'model': 'spiral_ln.evaluation_cpf_suite',
                                     'provider': 'local', 'hidden_state_access': False},
                    'target': {'candidate': {'label': g['label'], 'certificate': g['certificate']}},
                    'verification': {'verifier_id': VERIFIER, 'code': 'generator_exact', 'passed': True}})
        out['sft'].append(finish(rec))
    sources = [{'kind': 'procedural_generator', 'seed_commitment': commitment, 'per_family': args.per_family,
                'families': sorted(f for f, s in FAMILIES.items() if s == 'train'),
                'excluded_ids_digest': digest(sorted(excluded)), 'prompt_digest': digest(prompts),
                'gold_digest': digest(gold)}]
    return out, sources


def write(out_dir, records, sources, split):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=False)
    streams = {}
    custody = Counter()
    roots_seen = defaultdict(set)
    for name in STREAMS:
        rows = records.get(name, [])
        text = ''.join(json.dumps(r, sort_keys=True, ensure_ascii=False) + '\n' for r in rows)
        (out / f'{name}.jsonl').write_bytes(text.encode('utf-8'))
        for r in rows:
            roots_seen[r['split']].add(r['root'])
        streams[name] = {'bytes': len(text.encode()), 'sha256': sha(text), 'unique_examples': len(rows),
                         'roots': len({r['root'] for r in rows}),
                         'families': dict(Counter(r['family'] for r in rows))}
    custody.update({k: len(v) for k, v in roots_seen.items()})
    manifest = {'schema_version': SCHEMA, 'split': split, 'roots_by_custody': dict(custody), 'sources': sources,
                'streams': streams, 'quarantine': 'calibration and sealed_eval records carry loss.eligible=false'}
    (out / 'manifest.json').write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode('utf-8'))
    print(json.dumps({k: v['unique_examples'] for k, v in streams.items()}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    q = sub.add_parser('ledger')
    for k in ('prompts', 'gold', 'generation-manifest', 'calls', 'out'):
        q.add_argument('--' + k, required=True)
    q.add_argument('--custody', choices=['calibration', 'sealed_eval'], required=True)
    q.add_argument('--fingerprints', help='JSON {model_key: {checkpoint_sha256, quantization, backend, ...}}')
    q = sub.add_parser('procedural')
    q.add_argument('--seed-env', default='CPF_TRAIN_SEED')
    q.add_argument('--per-family', type=int, default=256)
    q.add_argument('--exclude-prompts', action='append', default=[])
    q.add_argument('--out', required=True)
    args = p.parse_args()
    if args.mode == 'ledger':
        records, sources = ledger_records(args)
        write(args.out, records, sources, args.custody)
    else:
        records, sources = procedural_records(args)
        write(args.out, records, sources, 'train')


if __name__ == '__main__':
    main()

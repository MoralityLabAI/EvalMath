"""Constructed ledger only; checks the CPF-06 analysis bookkeeping, not any model."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

from spiral_ln.evaluation_cpf_suite import STAGES, digest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'scripts/{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


runner = load('run_cpf_suite')
analysis = load('analyze_cpf_suite')


def build(tmp_path, monkeypatch):
    monkeypatch.setenv('CPF_SEED', 'analysis-fixture-v1')
    case = tmp_path / 'case'
    runner.prepare(argparse.Namespace(seed_env='CPF_SEED', per_family=4, split='test', out=case))
    prompts = runner.read_jsonl(case / 'prompts.jsonl')
    gold = {r['id']: r for r in runner.read_jsonl(case / 'gold.jsonl')}
    config = {'budget': 64, 'sampling_seed': 'x', 'temperature': .3,
              'models': {'B': {'url': 'u', 'model': 'B'}, 'I': {'url': 'u', 'model': 'I'}}}
    manifest = {'schema': 'CPF-run.1', 'prompt_digest': digest(prompts), 'config': config,
                'system': runner.SYSTEM, 'protocol': 'four-shared-stages.1'}
    calls = tmp_path / 'calls.jsonl'
    (tmp_path / 'calls.jsonl.manifest.json').write_text(json.dumps(manifest))
    rows = []
    for p in prompts:
        g = gold[p['id']]
        good = json.dumps({'label': g['label'], 'certificate': g['certificate']})
        bad = json.dumps({'label': 'entailed', 'certificate': None})
        for m in ('B', 'I'):
            for s in STAGES:
                text = good
                # Both models' low1 authorize every false root; B's refinement repairs them.
                if s == 'low1' and g['label'] == 'counterexample':
                    text = bad
                if m == 'I' and s == 'refine2' and g['label'] == 'counterexample':
                    text = bad
                if m == 'B' and s == 'low2':
                    text = '```json\n' + good + '\n```'
                rows.append({'id': p['id'], 'model': m, 'stage': s, 'text': text, 'completion': 10,
                             'prompt': 20, 'seconds': 1.0, 'cap': 64 if s == 'direct' else 32,
                             'finish_reason': 'stop'})
    calls.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    return case, calls, gold


def test_analysis_transitions_joint_and_contrasts(tmp_path, monkeypatch):
    case, calls, gold = build(tmp_path, monkeypatch)
    out = tmp_path / 'analysis.json'
    monkeypatch.setattr(sys, 'argv', ['x', '--prompts', str(case / 'prompts.jsonl'), '--gold', str(case / 'gold.jsonl'),
                                      '--generation-manifest', str(case / 'manifest.json'), '--calls', str(calls),
                                      '--out', str(out)])
    analysis.main()
    rep = json.loads(out.read_text())
    reg = rep['registered']
    n = rep['roots']
    false_n = sum(g['label'] == 'counterexample' for g in gold.values())
    assert n == 24 and false_n == 10
    tb = reg['refinement_transitions']['B']['certified_2x2']
    assert tb == {'I->C': false_n, 'C->C': n - false_n}
    ti = reg['refinement_transitions']['I']['certified_2x2']
    assert ti == {'I->I': false_n, 'C->C': n - false_n}
    j = reg['joint_false_acceptance']['B/low|I/low']
    assert (j['a_false'], j['b_false'], j['joint_false']) == (false_n, false_n, false_n)
    assert j['delta_pooled'] == 0.0  # both always wrong on the null fibre: no excess over product
    assert reg['arms']['B/low2']['certified_accuracy'] == 1.0
    assert rep['exploratory_strict_parse']['arms']['B/low2']['coverage'] == 0.0
    c = reg['primary_contrasts']['B/direct|B/refine']
    assert c['a_only'] == 0 and c['b_only'] == 0 and c['mcnemar_exact'] == 1.0
    assert rep['ledger_health']['B/low2']['strict_parse_fail'] == n
    assert reg['arms']['cross/agree']['coverage'] == round((n - false_n) / n + false_n / n, 4)


exporter = load('export_cpf_datagoblin')


def test_datagoblin_export_quarantine_and_streams(tmp_path, monkeypatch):
    case, calls, gold = build(tmp_path, monkeypatch)
    out = tmp_path / 'goblin'
    monkeypatch.setattr(sys, 'argv', ['x', 'ledger', '--prompts', str(case / 'prompts.jsonl'), '--gold',
                                      str(case / 'gold.jsonl'), '--generation-manifest', str(case / 'manifest.json'),
                                      '--calls', str(calls), '--custody', 'sealed_eval', '--out', str(out)])
    exporter.main()
    man = json.loads((out / 'manifest.json').read_text())
    assert man['schema_version'] == 'rlt_gym.aleph_corpus.v1'
    rows = {k: runner.read_jsonl(out / f'{k}.jsonl') for k in exporter.STREAMS}
    assert len(rows['outcomes']) == 24 * 8
    assert all(not r['loss']['eligible'] and r['split'] == 'sealed_eval' for v in rows.values() for r in v)
    assert len(rows['repairs']) == 10  # B repairs each false root
    assert sum(r.get('research_tag') == 'persistent_failure' for r in rows['research']) == 10  # I persists
    monkeypatch.setenv('CPF_TRAIN_SEED', 'train-fixture')
    tout = tmp_path / 'train'
    monkeypatch.setattr(sys, 'argv', ['x', 'procedural', '--per-family', '4', '--exclude-prompts',
                                      str(case / 'prompts.jsonl'), '--out', str(tout)])
    exporter.main()
    sft = runner.read_jsonl(tout / 'sft.jsonl')
    assert len(sft) == 12 and all(r['loss']['eligible'] and r['family'] in ('gate', 'degree', 'determinant') for r in sft)
    assert not {r['root'] for r in sft} & {'lineage:' + i for i in gold}

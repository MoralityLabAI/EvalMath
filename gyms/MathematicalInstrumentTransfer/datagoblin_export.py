"""MIT-14: export instrument-transfer training records in DataGoblin's collection-record format.

Each JSONL row is {"record": DataCollectionRecord (DataGoblin schema 1.0), "payload": training record}.
DataGoblin's pipeline reads row["record"]; the payload is the math content, hashed into
record.content_sha256. The payload schema `evalmath.mit.training_record.v1` is an extension
(DataGoblin has no math-training schema); see DATAGOBLIN_EXPORT.md.

Files (kept apart):
  synthetic_oracle.jsonl  exact teacher traces: proof fixtures with symbolic verifier receipts,
                          exact action values with rejected actions, precision-refinement traces,
                          counterexample witnesses. model_generated = false.
  model_traces.jsonl      final responses of local models on MIT-13 development rows with
                          independent verifier outcomes. model_generated = true. Reasoning text is
                          not exported (only its length).
No confirmation data exists; rows marked sealed are refused. MIT-13 development roots are
evaluation material and carry allowed_uses = ["EVALUATION"].

    python datagoblin_export.py --output export [--mit13 DIR ...] [--validate ../../../DataGoblin]
"""
import argparse, hashlib, json, sys
from fractions import Fraction as F
from pathlib import Path

GYM = Path(__file__).resolve().parent
ROOT = GYM.parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(GYM))
import proof_pilot as pp
import certified_precision as cp
import decision_certificates as dc
from spiral_ln.evaluation_adaptive_precision import Solver, run_controller, LEVELS
from spiral_ln.evaluation_decision_certificate import policy_certificate

PAYLOAD_SCHEMA = 'evalmath.mit.training_record.v1'
SOURCES = ('gyms/MathematicalInstrumentTransfer/datagoblin_export.py', 'gyms/MathematicalInstrumentTransfer/proof_pilot.py',
           'gyms/MathematicalInstrumentTransfer/certified_precision.py',
           'src/spiral_ln/evaluation_adaptive_precision.py', 'src/spiral_ln/evaluation_decision_certificate.py')


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()


def fr(x):
    return f'{x.numerator}/{x.denominator}' if isinstance(x, F) else x


def split_of(root_id):
    """Deterministic train/dev split by root (never by row)."""
    return 'train' if int(hashlib.sha256(root_id.encode()).hexdigest(), 16) % 10 < 8 else 'dev'


def record(item_id, payload, *, kind, split, model_generated, generator_id, evidence, verified_by,
           receipt_sha, evaluation, meta):
    if split in ('confirmation', 'sealed'):
        raise ValueError('confirmation data cannot be exported')
    return dict(
        item_id=item_id, schema_version='1.0', content_sha256=sha(payload), source_kind=kind,
        purpose_id='evalmath-mit-instrument-transfer', lawful_basis='own_synthetic_research_data',
        allowed_uses=['EVALUATION'] if evaluation else ['TRAINING', 'EVALUATION'],
        data_residency_region='unrestricted', sensitivity_class='public_synthetic', license_status='ALLOWED',
        consent_status='NOT_REQUIRED', personal_data_status='NONE', redacted=False, contains_secret=False,
        contains_hidden_reasoning=False, contains_model_weight=False, evaluation_material=evaluation,
        sealed_evaluation=False, model_generated=model_generated, generator_id=generator_id, evidence_type=evidence,
        asserted_by='evalmath-mit-export', verified_by=verified_by, verification_receipt_sha256=receipt_sha,
        verification_subject_sha256=sha(payload), verification_custody='ENVIRONMENT_OWNED' if verified_by else 'NONE',
        provenance_refs=['github.com/MoralityLabAI/EvalMath', f'payload_schema:{PAYLOAD_SCHEMA}'],
        dedup_group=payload['root_id'], intended_split=split, retention_days=3650, deletion_requested=False,
        public_metadata=dict(payload_schema=PAYLOAD_SCHEMA, **meta))


def fixture_records(source_hashes):
    out = []
    for pub, sec in pp.fixtures():
        t = sec['target']
        resp, checks = pp.solve(t)
        if sec['candidate'] is not None:
            resp['mapping_valid'] = pp.mapping_valid(t, sec['candidate'])
        verified = pp.verify(t, resp)
        assert verified
        f = sec['family']
        payload = dict(
            schema=PAYLOAD_SCHEMA, kind='proof_fixture', root_id=sec['root_id'], family=f, variant=sec['variant'],
            arm=sec['arm'], source_theorem=pp.SOURCE[f], instrument=pp.INSTRUMENT[f],
            prerequisites='certificate family must match the target structure; see instrument text',
            target_theorem=pub['prompt'], target_instance=t, applicability_label=sec['expected_mapping_valid'],
            candidate_mapping=sec['candidate'],
            counterexample=resp.get('witness') if resp['verdict'] == 'counterexample' else None,
            teacher_response=resp, rejected_candidates=[sec['candidate']] if sec['expected_mapping_valid'] is False else [],
            certificate=resp.get('certificate'), verifier_receipt=dict(verifier='proof_pilot.verify', verified=verified),
            compute_cost=dict(symbolic_checks=checks), provenance=dict(generator='proof_pilot.fixtures', sources=source_hashes))
        out.append(record(f"mit06-{pub['row_id']}", payload, kind='synthetic_exact_fixture', split=split_of(sec['root_id']),
                          model_generated=False, generator_id='evalmath-proof-pilot', evidence='ENVIRONMENT_VERIFIED',
                          verified_by='proof_pilot.verify', receipt_sha=sha(payload['verifier_receipt']), evaluation=False,
                          meta=dict(family=f, variant=sec['variant'], arm=sec['arm'], origin='synthetic_oracle')))
        out[-1] = dict(record=out[-1], payload=payload)
    return out


def action_value_records(source_hashes, roots=4):
    out = []
    for fi, fam in enumerate(cp.FAMILIES):
        for i in range(roots):
            seed = 910000 + 1000 * fi + i
            env = cp.make(fam, seed)
            s = Solver(env)
            root_id = f'mit09-{fam}-{seed}'
            states = []

            def walk(m, guessed, avail, b, depth):
                acts = s.actions(guessed, avail, b)
                if not acts or sum(m) == 0:
                    return
                q = s.qvalues(m, guessed, avail, b)
                best = max(q.values())
                star = next(a for a in acts if q[a] == best)
                states.append(dict(posterior=[fr(x / sum(m)) for x in m], guessed=guessed, available=avail, budget=b,
                                   action_values={f'{a[0]}{a[1]}': fr(v) for a, v in q.items()},
                                   teacher_action=f'{star[0]}{star[1]}',
                                   rejected=[f'{a[0]}{a[1]}' for a in acts if q[a] < best],
                                   regret={f'{a[0]}{a[1]}': fr(best - v) for a, v in q.items()}))
                kind, k = star
                if kind == 'g':
                    walk(m[:k] + (F(0),) + m[k + 1:], guessed | 1 << k, avail, b - 1, depth + 1)
                else:
                    for row in env.qs[k][1]:
                        walk(tuple(x * r for x, r in zip(m, row)), guessed, avail & ~(1 << k), b - env.qs[k][0], depth + 1)
            walk(env.w, 0, (1 << len(env.qs)) - 1, env.budget, 0)
            trace = run_controller(env, F(1, 20), 'uniform')
            refine = [dict(profile=[str(x) for x in p], certificate=fr(c)) for p, c in trace['trace']]
            pc = policy_certificate(env, trace['profile'])
            payload = dict(schema=PAYLOAD_SCHEMA, kind='teacher_action_values', root_id=root_id, family=f'mit09-{fam}',
                           environment=dict(weights=[fr(x) for x in env.w], budget=env.budget,
                                            queries=[dict(cost=c, rows=[[fr(x) for x in r] for r in rows]) for c, rows in env.qs]),
                           states=states, optimum=fr(s.optimum()), precision_refinement_trace=refine,
                           certificate=dict(eta='1/20', global_bound=fr(trace['certificate']), decision_bound=fr(pc['certificate'])),
                           compute_cost=dict(refinement_cost=trace['cost'], memory_bits=trace['memory_bits'],
                                             solver_states=len(s.memo)),
                           verifier_receipt=dict(verifier='Solver exact Bellman; cross-checked by Quotient in tests'),
                           provenance=dict(generator='certified_precision.make', seed=seed, sources=source_hashes))
            rec = record(f'{root_id}-teacher', payload, kind='synthetic_exact_oracle', split=split_of(root_id),
                         model_generated=False, generator_id='evalmath-mit09-generator', evidence='ENVIRONMENT_VERIFIED',
                         verified_by='spiral_ln.evaluation_adaptive_precision.Solver', receipt_sha=sha(payload['certificate']),
                         evaluation=False, meta=dict(family=f'mit09-{fam}', states=len(states), origin='synthetic_oracle'))
            out.append(dict(record=rec, payload=payload))
    return out


def witness_records(source_hashes):
    out = []
    for name, w in (('drift', dc.drift_witness()), ('equal_accuracy', dc.equal_accuracy_witness())):
        root_id = f'mit10-{name}'
        payload = dict(schema=PAYLOAD_SCHEMA, kind='counterexample', root_id=root_id, family='mit10-certification',
                       counterexample=w, applicability_label=False,
                       rejected_candidates=['plugin', 'local', 'rootonly'] if name == 'drift' else ['scalar accuracy rule'],
                       verifier_receipt=dict(verifier='exact deployed regret (Fractions)'),
                       provenance=dict(generator='decision_certificates', sources=source_hashes))
        rec = record(root_id, payload, kind='synthetic_exact_counterexample', split='train', model_generated=False,
                     generator_id='evalmath-mit10', evidence='ENVIRONMENT_VERIFIED', verified_by='decision_certificates',
                     receipt_sha=sha(w), evaluation=False, meta=dict(family='mit10-certification', origin='synthetic_oracle'))
        out.append(dict(record=rec, payload=payload))
    return out


def model_records(mit13_dirs):
    """Real model responses on MIT-13 development rows (evaluation material, never training)."""
    out = []
    for d in mit13_dirs:
        d = Path(d)
        scores = json.loads((d / 'scores.json').read_text())
        priv = {r['dispatch_id']: r for r in map(json.loads, (d / 'private.jsonl').read_text().splitlines()) if r}
        resp = {r['row_id']: r for r in map(json.loads, (d / 'responses.jsonl').read_text().splitlines()) if r}
        ck = scores.get('checkpoint', 'unknown')
        for row in scores['rows']:
            p = priv[row['row_id']]
            r = resp.get(row['row_id'], {})
            payload = dict(schema=PAYLOAD_SCHEMA, kind='model_trace', root_id=p['root_id'], family=p['family'],
                           variant=p['variant'], arm=p['arm'], target_prompt_sha256=p.get('prompt_sha256'),
                           final_response=r.get('response'), attempts=len(r.get('attempts', [])),
                           reasoning_chars=r.get('reasoning_len'), closure=row.get('verified'),
                           applicability_correct=row.get('applicability_correct'), status=row.get('status'),
                           compute_cost=dict(tokens_in=r.get('tokens_in'), tokens_out=r.get('tokens_out'),
                                             wall_ms=r.get('wall_ms')),
                           verifier_receipt=dict(verifier='mit13_score', verified=row.get('verified')),
                           provenance=dict(checkpoint=ck, responses_sha256=scores.get('responses_sha256')))
            rec = record(f"mit13-{ck[:12]}-{row['row_id']}", payload, kind='local_model_development_trace',
                         split='evaluation_dev', model_generated=True, generator_id=ck, evidence='INDEPENDENT_HARNESS',
                         verified_by='mit13_score', receipt_sha=sha(payload['verifier_receipt']), evaluation=True,
                         meta=dict(family=p['family'], arm=p['arm'], origin='model_trace'))
            out.append(dict(record=rec, payload=payload))
    return out


def validate(rows, datagoblin):
    sys.path.insert(0, str(Path(datagoblin) / 'src'))
    from datagoblin.data_etiquette.records import DataCollectionRecord
    for row in rows:
        DataCollectionRecord.from_jsonable(row['record'])
        assert row['record']['content_sha256'] == sha(row['payload'])
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--mit13', nargs='*', default=[])
    ap.add_argument('--validate', type=Path)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    synth = fixture_records(hashes) + action_value_records(hashes) + witness_records(hashes)
    model = model_records(a.mit13)
    assert not any(r['record']['model_generated'] for r in synth) and all(r['record']['model_generated'] for r in model)
    assert not any(r['record']['sealed_evaluation'] for r in synth + model)
    for name, rows in (('synthetic_oracle.jsonl', synth), ('model_traces.jsonl', model)):
        (a.output / name).write_text(''.join(json.dumps(r, sort_keys=True, default=str) + '\n' for r in rows))
    n_valid = validate(synth + model, a.validate) if a.validate else None
    manifest = dict(payload_schema=PAYLOAD_SCHEMA, datagoblin_record_schema='1.0', synthetic_rows=len(synth),
                    model_rows=len(model), splits={s: sum(r['record']['intended_split'] == s for r in synth + model)
                                                    for s in ('train', 'dev', 'evaluation_dev')},
                    validated_with_datagoblin=n_valid, sources=hashes,
                    files={n: hashlib.sha256((a.output / n).read_bytes()).hexdigest()
                           for n in ('synthetic_oracle.jsonl', 'model_traces.jsonl')})
    (a.output / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')
    print(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()

"""MIT-13 scorer: closure and applicability scored separately; failures stay explicit; pilot spec for preflight.

Joins prompts-side dispatch ids to private rows only here."""
import argparse, json, hashlib
from pathlib import Path
from collections import defaultdict, Counter
import mit13_fixtures as fx
import mit13_lean_check as lean


def read(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def row_status(r, budget):
    if r is None:
        return 'missing'
    if not isinstance(r.get('response'), dict):
        return 'malformed'
    ni, no = r.get('tokens_in'), r.get('tokens_out')
    if type(ni) is not int or type(no) is not int or ni < 0 or no < 0 or ni + no > budget or r.get('over_budget'):
        return 'over_budget'
    return 'ok'


def score_row(g, r, budget, lean_fn=lean.check):
    status = row_status(r, budget)
    resp = r['response'] if status == 'ok' else None
    closed = False
    lean_reason = None
    if resp is not None:
        if g['family'] == 'lean':
            item = g['target']
            res = lean_fn(item['name'], item['statement'], resp.get('proof'))
            closed, lean_reason = res['ok'], res['reason']
        else:
            closed = bool(fx.verify(g['target'], resp))
    out = dict(row_id=g['row_id'], dispatch_id=g['dispatch_id'], root_id=g['root_id'], family=g['family'],
               variant=g['variant'], arm=g['arm'], status=status, closed=closed, lean_reason=lean_reason,
               tokens_in=r.get('tokens_in') if r else None, tokens_out=r.get('tokens_out') if r else None,
               wall_ms=r.get('wall_ms') if r else None, attempts=len(r.get('attempts', [])) if r else 0,
               applicability_correct=None, false_accept=None, selected_correct=None, selected_family=None)
    gold = g['expected_mapping_valid']
    if gold is not None:
        rep = resp.get('mapping_valid') if resp else None
        out['applicability_correct'] = type(rep) is bool and rep == gold
        out['false_accept'] = rep is True and gold is False
    if g['arm'] == 'adaptive':
        sel = resp.get('selected_instrument') if resp else None
        sel = sel.strip().upper() if isinstance(sel, str) else None
        out['selected_family'] = g['menu'].get(sel)
        out['selected_correct'] = sel == g['selected_gold']
    return out


def tables(rows):
    groups = defaultdict(list)
    for v in rows:
        groups[(v['family'], v['variant'], v['arm'])].append(v)
    res = []
    for (f, var, arm), v in sorted(groups.items()):
        n = len(v)
        scored = [z for z in v if z['applicability_correct'] is not None]
        sel = [z for z in v if z['selected_correct'] is not None]
        res.append(dict(family=f, variant=var, arm=arm, rows=n, closed=sum(z['closed'] for z in v), closure_rate=sum(z['closed'] for z in v) / n,
                        status=dict(Counter(z['status'] for z in v)),
                        applicability_scored=len(scored), applicability_correct=sum(z['applicability_correct'] for z in scored),
                        false_accepts=sum(bool(z['false_accept']) for z in scored),
                        selection_scored=len(sel), selection_correct=sum(z['selected_correct'] for z in sel),
                        mean_tokens=(lambda t: sum(t) / len(t) if t else None)([z['tokens_in'] + z['tokens_out'] for z in v if z['status'] == 'ok'])))
    return res


def root_effects(rows, effect_arm='instrument', families=None):
    """Per root: closure(effect_arm) - closure(sham); matched sham observation closure(sham) - closure(unaided)."""
    by = defaultdict(dict)
    for v in rows:
        if v['variant'] == 'true' and v['family'] != 'lean' and (families is None or v['family'] in families):
            by[v['root_id']][v['arm']] = int(v['closed'])
    out = []
    for rid, a in sorted(by.items()):
        if {effect_arm, 'sham', 'unaided'} <= a.keys():
            out.append(dict(unit_id=rid, paired_effect=str(a[effect_arm] - a['sham']), sham_effects=[str(a['sham'] - a['unaided'])]))
    return out


def pilot_spec(effects, experiment_id='MIT-13-pilot', **kw):
    """Schema of skills/evalmath-mechinterp-power/scripts/preflight.py --pilot."""
    spec = dict(schema_version=1, experiment_id=experiment_id, independent_unit='generated source-target root',
                alpha='0.05', scientific_min_effect='0.1', target_effect='0.2', measurement_resolution='0.05',
                sham_quantile='0.95', sham_confidence='0.95', planned_comparisons=4, confirm_units_planned=64,
                pilot_from_development_only=True, heldout_sealed=False, units_independent=False, pilot=effects)
    spec.update(kw)
    return spec


def main(private, responses, out, budget, checkpoint, effect_arm='instrument', pilot_out=None, families=None, lean_fn=lean.check):
    gold = read(private)
    by = {}
    for r in read(responses):
        if r['row_id'] in by:
            raise ValueError('duplicate response id')
        by[r['row_id']] = r
    unknown = set(by) - {g['dispatch_id'] for g in gold}
    if unknown:
        raise ValueError(f'unknown dispatch ids: {len(unknown)}')
    rows = [score_row(g, by.get(g['dispatch_id']), budget, lean_fn) for g in gold]
    effects = root_effects(rows, effect_arm, families)
    result = dict(schema='mit13-model-open-dev-v1', checkpoint=checkpoint, total_token_budget=budget, rows=rows, groups=tables(rows),
                  root_effects=effects, effect_arm=effect_arm, missing_rows=sum(v['status'] == 'missing' for v in rows),
                  responses_sha256=hashlib.sha256(Path(responses).read_bytes()).hexdigest(),
                  limits='Open development roots; one sample per row; token counts are server-reported usage; no sealed confirmation.')
    Path(out).write_text(json.dumps(result, indent=2) + '\n')
    if pilot_out:
        Path(pilot_out).write_text(json.dumps(pilot_spec(effects), indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--private', type=Path, required=True)
    p.add_argument('--responses', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--budget', type=int, required=True)
    p.add_argument('--checkpoint', required=True)
    p.add_argument('--effect-arm', default='instrument', choices=('instrument', 'source', 'adaptive', 'oracle', 'near_miss'))
    p.add_argument('--pilot-out', type=Path)
    p.add_argument('--families', nargs='*')
    a = p.parse_args()
    main(a.private, a.responses, a.output, a.budget, a.checkpoint, a.effect_arm, a.pilot_out, a.families)

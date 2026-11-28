#!/usr/bin/env python3
"""CPF-06 analysis of a completed call ledger: registered contrasts plus labelled exploratory tables.

Validates the ledger exactly as `run_cpf_suite.py score`, then reports per arm and per family:
certified and label accuracy, coverage, abstention, false authorization, Wilson intervals, token
and latency cost; paired bootstrap intervals and exact McNemar tests for the registered primary
contrasts (Holm-adjusted); conditional joint false acceptance with pooled, family-stratified and
within-family permutation views; refinement transition matrices; malformed/truncation ledger.
"""
import argparse
import json
import random
from collections import Counter, defaultdict
from fractions import Fraction
from math import comb, sqrt
from pathlib import Path

from spiral_ln.evaluation_cpf_suite import STAGES, arms, canonical, digest, parse
from run_cpf_suite import read_jsonl

BOOT = 10000
PERM = 10000
SEED = 20261125


def wilson(k, n, z=1.959964):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return float(min(Fraction(1), 2 * Fraction(sum(comb(n, k) for k in range(min(b, c) + 1)), 2 ** n)))


def holm(pvals):
    order = sorted(pvals, key=lambda k: pvals[k])
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * pvals[k]))
        out[k] = running
    return out


def status(answer, g):
    if answer is None:
        return 'abstain'
    if answer['label'] != g['label']:
        return 'wrong_label'
    return 'certified' if canonical(answer['certificate']) == canonical(g['certificate']) else 'label_only'


def load(args):
    gold = read_jsonl(args.gold)
    prompts = read_jsonl(args.prompts)
    meta = json.loads(Path(args.calls + '.manifest.json').read_text())
    generation = json.loads(Path(args.generation_manifest).read_text())
    if digest(gold) != generation['gold_digest'] or digest(prompts) != generation['prompt_digest']:
        raise ValueError('generation manifest mismatch')
    if digest(prompts) != meta['prompt_digest']:
        raise ValueError('prompt mismatch')
    models = list(meta['config']['models'])
    if args.only_model:
        models = [args.only_model]
    budget = meta['config']['budget']
    by = defaultdict(dict)
    for row in read_jsonl(args.calls):
        if row['model'] not in models:
            continue
        k = (row['model'], row['stage'])
        if k in by[row['id']]:
            raise ValueError('duplicate calls')
        cap = budget if row['stage'] == 'direct' else budget // 2
        if row['cap'] != cap or not 0 <= row['completion'] <= cap:
            raise ValueError('invalid measured cap')
        by[row['id']][k] = row
    want = {(m, s) for m in models for s in STAGES}
    if set(by) != {p['id'] for p in prompts} or any(set(r) != want for r in by.values()):
        raise ValueError('incomplete call panel')
    return gold, by, models, meta, generation


def analyze(gold, by, models, strict=False):
    g = {r['id']: r for r in gold}
    ids = sorted(g)
    fam = defaultdict(list)
    for i in ids:
        fam[g[i]['family']].append(i)
    if strict:
        import spiral_ln.evaluation_cpf_suite as S
        orig = S.parse
        S.parse = lambda t: orig(t, strict=True)
    try:
        pred = {i: arms(by[i], models) for i in ids}
    finally:
        if strict:
            S.parse = orig
    names = sorted(next(iter(pred.values())))

    def metric(sub, arm):
        c = Counter()
        cost = Counter()
        for i in sub:
            p = pred[i][arm]
            st = status(p['answer'], g[i])
            c['n'] += 1
            c[st] += 1
            c['covered'] += st != 'abstain'
            c['label_correct'] += st in ('certified', 'label_only')
            if g[i]['label'] == 'counterexample':
                c['false_roots'] += 1
                c['false_authorized'] += p['answer'] is not None and p['answer']['label'] == 'entailed'
            if g[i]['label'] == 'unresolved':
                c['unresolved_roots'] += 1
                c['unresolved_authorized'] += p['answer'] is not None and p['answer']['label'] == 'entailed'
            cost.update({k: p[k] for k in ('completion', 'prompt', 'seconds')})
        n = c['n']
        out = {'counts': dict(c),
               'certified_accuracy': round(c['certified'] / n, 4), 'certified_ci': wilson(c['certified'], n),
               'label_accuracy': round(c['label_correct'] / n, 4), 'label_ci': wilson(c['label_correct'], n),
               'coverage': round(c['covered'] / n, 4), 'abstention': round(c['abstain'] / n, 4),
               'completion_tokens': cost['completion'], 'prompt_tokens': cost['prompt'],
               'total_tokens': cost['completion'] + cost['prompt'], 'latency_seconds': round(cost['seconds'], 1),
               'certified_per_1k_completion': round(1000 * c['certified'] / cost['completion'], 3) if cost['completion'] else None,
               'certified_per_1k_total': round(1000 * c['certified'] / (cost['completion'] + cost['prompt']), 3)}
        if c['false_roots']:
            out['false_authorization'] = round(c['false_authorized'] / c['false_roots'], 4)
            out['false_authorization_ci'] = wilson(c['false_authorized'], c['false_roots'])
            out['selective_false_authorization'] = (round(c['false_authorized'] / c['covered'], 4)
                                                    if c['covered'] else None)
        if c['unresolved_roots']:
            out['unresolved_authorization'] = round(c['unresolved_authorized'] / c['unresolved_roots'], 4)
        return out

    report = {'arms': {a: metric(ids, a) for a in names},
              'families': {f: {a: metric(sub, a) for a in names} for f, sub in sorted(fam.items())}}

    def correct(i, a):
        return status(pred[i][a]['answer'], g[i]) == 'certified'

    def contrast(a, b):
        wins = sum(correct(i, a) and not correct(i, b) for i in ids)
        losses = sum(correct(i, b) and not correct(i, a) for i in ids)
        rng = random.Random(SEED)
        d = [correct(i, a) - correct(i, b) for i in ids]
        # Family-stratified paired bootstrap over roots.
        idx = {f: [ids.index(i) for i in sub] for f, sub in fam.items()}
        boots = []
        for _ in range(BOOT):
            s = 0
            for f, pos in idx.items():
                s += sum(d[pos[rng.randrange(len(pos))]] for _ in pos)
            boots.append(s / len(ids))
        boots.sort()
        return {'a': a, 'b': b, 'a_only': wins, 'b_only': losses, 'delta': round((wins - losses) / len(ids), 4),
                'bootstrap95': [round(boots[int(0.025 * BOOT)], 4), round(boots[int(0.975 * BOOT) - 1], 4)],
                'mcnemar_exact': mcnemar(wins, losses)}

    primary = []
    for m in models:
        primary.append((m + '/direct', m + '/refine'))
        primary.append((m + '/independent', m + '/serial_agree'))
    if len(models) == 2:
        for m in models:
            primary.append(('cross/agree', m + '/independent'))
    contrasts = {f'{a}|{b}': contrast(a, b) for a, b in primary}
    adj = holm({k: v['mcnemar_exact'] for k, v in contrasts.items()})
    for k in contrasts:
        contrasts[k]['holm'] = round(adj[k], 6)
    report['primary_contrasts'] = contrasts

    def fa(i, a):
        x = pred[i][a]['answer']
        return x is not None and x['label'] == 'entailed'

    def joint(a, b):
        null = [i for i in ids if g[i]['label'] == 'counterexample']
        n = len(null)
        pa = sum(fa(i, a) for i in null)
        pb = sum(fa(i, b) for i in null)
        j = sum(fa(i, a) and fa(i, b) for i in null)
        by_f, strat, w = {}, 0.0, 0
        groups = defaultdict(list)
        for i in null:
            groups[g[i]['family']].append(i)
        for f, sub in sorted(groups.items()):
            k = len(sub)
            fa_ = sum(fa(i, a) for i in sub)
            fb_ = sum(fa(i, b) for i in sub)
            fj = sum(fa(i, a) and fa(i, b) for i in sub)
            dlt = fj / k - fa_ * fb_ / k / k
            by_f[f] = {'n': k, 'a': fa_, 'b': fb_, 'joint': fj, 'delta': round(dlt, 4)}
            strat += k * dlt
            w += k
        rng = random.Random(SEED + 1)
        ge = 0
        for _ in range(PERM):  # permute b's indicators within family: difficulty-matched null
            jj = 0
            for f, sub in groups.items():
                bs = [fa(i, b) for i in sub]
                rng.shuffle(bs)
                jj += sum(fa(i, a) and v for i, v in zip(sub, bs))
            ge += jj >= j
        return {'a': a, 'b': b, 'null_n': n, 'a_false': pa, 'b_false': pb, 'joint_false': j,
                'p_joint': round(j / n, 4) if n else None,
                'delta_pooled': round(j / n - pa * pb / n / n, 4) if n else None,
                'delta_family_stratified': round(strat / w, 4) if w else None,
                'within_family_permutation_p_ge': round((ge + 1) / (PERM + 1), 4),
                'by_family': by_f}

    pairs = []
    for m in models:
        pairs += [(m + '/low', m + '/low2'), (m + '/low', m + '/refine'), (m + '/direct', m + '/low')]
    if len(models) == 2:
        pairs += [(models[0] + '/low', models[1] + '/low'), (models[0] + '/direct', models[1] + '/direct')]
    report['joint_false_acceptance'] = {f'{a}|{b}': joint(a, b) for a, b in pairs}

    trans = {}
    for m in models:
        mat = Counter()
        bin2 = Counter()
        copied = 0
        for i in ids:
            s1 = status(pred[i][m + '/low']['answer'], g[i])
            s2 = status(pred[i][m + '/refine']['answer'], g[i])
            mat[s1 + '->' + s2] += 1
            bin2[('C' if s1 == 'certified' else 'I') + '->' + ('C' if s2 == 'certified' else 'I')] += 1
            copied += canonical(pred[i][m + '/low']['answer']) == canonical(pred[i][m + '/refine']['answer'])
        trans[m] = {'certified_2x2': dict(bin2), 'four_state': dict(mat), 'refine_identical_to_low1': copied,
                    'repair_rate_given_incorrect': round(bin2['I->C'] / (bin2['I->C'] + bin2['I->I']), 4)
                    if bin2['I->C'] + bin2['I->I'] else None,
                    'corruption_rate_given_correct': round(bin2['C->I'] / (bin2['C->C'] + bin2['C->I']), 4)
                    if bin2['C->C'] + bin2['C->I'] else None}
    report['refinement_transitions'] = trans
    return report


def ledger_health(by, models):
    out = {}
    for m in models:
        for s in STAGES:
            rows = [r[(m, s)] for r in by.values()]
            out[f'{m}/{s}'] = {
                'calls': len(rows),
                'finish_length': sum(r.get('finish_reason') == 'length' for r in rows),
                'empty_content': sum(not (r['text'] or '').strip() for r in rows),
                'parse_fail': sum(parse(r['text']) is None for r in rows),
                'strict_parse_fail': sum(parse(r['text'], strict=True) is None for r in rows),
                'completion_tokens': sum(r['completion'] for r in rows),
                'prompt_tokens': sum(r['prompt'] for r in rows),
                'cap_hits': sum(r['completion'] >= r['cap'] for r in rows),
                'mean_latency_s': round(sum(r['seconds'] for r in rows) / len(rows), 2),
                'reported_models': sorted({str(r.get('reported_model')) for r in rows})}
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ('prompts', 'gold', 'generation-manifest', 'calls', 'out'):
        p.add_argument('--' + k, required=True)
    p.add_argument('--only-model')
    p.add_argument('--label', default='primary', help='primary (registered) or exploratory')
    args = p.parse_args()
    gold, by, models, meta, generation = load(args)
    report = {'schema': 'CPF-analysis.1', 'status': args.label, 'models': models, 'roots': len(gold),
              'generation_manifest': generation, 'run_manifest_digest': digest(meta),
              'registered': analyze(gold, by, models),
              'exploratory_strict_parse': {'arms': analyze(gold, by, models, strict=True)['arms']},
              'ledger_health': ledger_health(by, models)}
    Path(args.out).write_bytes((json.dumps(report, indent=2, sort_keys=True) + '\n').encode('utf-8'))
    for a, v in report['registered']['arms'].items():
        print(f"{a:22s} cert {v['certified_accuracy']:.3f} label {v['label_accuracy']:.3f} cov {v['coverage']:.3f} "
              f"FA {v.get('false_authorization')} tok {v['completion_tokens']}")


if __name__ == '__main__':
    main()

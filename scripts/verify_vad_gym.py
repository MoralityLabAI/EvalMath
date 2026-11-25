"""VAD-11 verifier: kernel-checks the proof gym under both Lean toolchains and writes the receipt.

    python scripts/verify_vad_gym.py [--per-family 6] [--full] [--work DIR] [--out FILE]
                                     [--workers 4] [--repeats 1] [--families F1 F2 ..] [--no-lean]

What it does (all counts are integers, all times are aggregated with exact Fractions):
  1. frozen split manifest (calibration seeds 81000-81199, test seeds 82000-82399 per family):
     sha256 of every generated statement, template / moduli sets, disjointness checks;
  2. statement fidelity for EVERY generated statement (not only the Lean slice): the template
     renderer and the re-printer driven by the parsed Lean text agree byte-for-byte, and the
     parsed statement is true by brute force in Python (no Lean involved);
  3. for a slice (default 6 evenly spaced seeds per family per split, `--full` = all seeds) every
     applicable strategy file is checked with `lean file.lean` in a fresh process under 4.35.0
     (primary) and 4.19.0 (CI pin): ok, wall seconds, child CPU seconds, profiler work_ms
     (elaboration + type checking, excludes process start-up), peak RSS, axiom report class
     ('none' or 'standard' = subset of propext / Classical.choice / Quot.sound; anything else fails);
  4. library lemmas used by the slice are built once per toolchain to .olean (each a fresh process,
     each with its own statement and cost);
  5. abstraction invention: structural anti-unification over calibration instances -> candidate
     lemmas -> kernel check -> use on calibration and test targets; the same machinery run on test
     instances is the leak control and must be rejected by the transitive dependency auditor;
  6. dependency audit of every library unit, invented unit and test target (all 400 per family),
     plus mutation controls.
Wall times are measured with up to 4 concurrent lean processes on a possibly loaded machine; use
`work_ms` (and the CPU column) for cost comparisons, and compare medians rather than single files.
A failed or timed-out file stays in the receipt as a failure; nothing is retried or relaxed.
"""
import argparse
import hashlib
import json
import statistics
import sys
import tempfile
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vad_gym as G          # noqa: E402
import vad_lean_runner as R  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / 'output' / 'verified_abstraction' / 'vad_11_gym.json'


def file_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def frac_median(xs):
    xs = sorted(Fraction(int(round(x * 1000000)), 1000000) for x in xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def fnum(x, nd=4):
    return None if x is None else round(float(x), nd)


def size_key(spec):
    f = spec['family']
    if f == 'F1': return spec['nvars']
    if f == 'F2': return spec['m']
    if f == 'F3': return spec['m']
    if f == 'F4': return spec['n']
    return spec['k']


def aggregate(rows):
    """rows: per-(instance, strategy, version) result dicts -> medians (exact Fractions, printed as floats)."""
    ok = [r for r in rows if r['ok']]
    out = {'n': len(rows), 'n_ok': len(ok), 'n_timeout': sum(1 for r in rows if r.get('timed_out'))}
    for key in ('seconds', 'cpu_seconds', 'work_ms', 'peak_rss_mb'):
        vals = [r[key] for r in ok if r.get(key) is not None]
        m = frac_median(vals)
        out['median_' + key] = fnum(m)
        out['median_' + key + '_exact'] = None if m is None else f'{m.numerator}/{m.denominator}'
    return out


def run_items(ws, items, repeats):
    """Check items [(label, body, target)] `repeats` times; keep the per-version minimum of the cost fields."""
    best = {}
    for rep in range(repeats):
        res = ws.check_many(items)
        for label, per_v in res.items():
            for v, r in per_v.items():
                cur = best.setdefault(label, {}).get(v)
                if cur is None:
                    r['runs'] = 1
                    r['all_ok'] = r['ok']
                    best[label][v] = r
                else:
                    cur['runs'] += 1
                    cur['all_ok'] = cur['all_ok'] and r['ok']
                    cur['verifier_calls'] += 1
                    for k in ('seconds', 'cpu_seconds', 'work_ms'):
                        if r.get(k) is not None and (cur.get(k) is None or r[k] < cur[k]):
                            cur[k] = r[k]
                    cur['peak_rss_mb'] = max(cur['peak_rss_mb'], r['peak_rss_mb'])
                    cur['ok'] = cur['ok'] and r['ok']
    return best


def slim(r):
    return {'ok': r['ok'], 'seconds': r['seconds'], 'cpu_seconds': r['cpu_seconds'], 'work_ms': r['work_ms'],
            'peak_rss_mb': r['peak_rss_mb'], 'axiom_class': r['axiom_class'], 'axioms': r['axioms'],
            'rc': r['rc'], 'timed_out': r['timed_out'], 'runs': r.get('runs', 1), 'source_sha256': r.get('source_sha256'),
            'imports': r.get('imports'), 'error': None if r['ok'] else (r['stdout'] + r['stderr'])[-600:]}


def mutation_controls():
    """Auditor controls independent of the gym: clean / direct / transitive / provenance / header-only."""
    held = {'vad_t_F1_82001', 'vad_t_F1_82002'}
    d = {
        'clean': {'text': 'theorem vadl_c : True := trivial', 'owns': ['vadl_c'], 'origin': []},
        'cites_cal': {'text': 'theorem vadl_cc : True := by\n  have := vad_t_F1_81001\n  trivial', 'owns': ['vadl_cc'], 'origin': []},
        'cites_test': {'text': 'theorem vadl_ct : True := by\n  have := vad_t_F1_82001\n  trivial', 'owns': ['vadl_ct'], 'origin': []},
        'cites_lemma_citing_test': {'text': 'theorem vadl_cl : True := vadl_ct', 'owns': ['vadl_cl'], 'origin': []},
        'dotted_ref': {'text': 'theorem vadl_cd : True := by\n  exact (vad_t_F1_82001.symm).elim', 'owns': ['vadl_cd'], 'origin': []},
        'comment_only': {'text': '-- vad_t_F1_82001 is not used\ntheorem vadl_cm : True := trivial', 'owns': ['vadl_cm'], 'origin': []},
        'prefix_name': {'text': 'theorem vadl_cp : True := by\n  have := vad_t_F1_820010\n  trivial', 'owns': ['vadl_cp'], 'origin': []},
        'provenance': {'text': 'theorem vadl_cv : True := trivial', 'owns': ['vadl_cv'], 'origin': ['vad_t_F1_82001']},
        'target_self': {'text': 'theorem vad_t_F1_82001 : True := by\n  exact vad_t_F1_82001', 'owns': ['vad_t_F1_82001'], 'origin': []},
        'target_header_only': {'text': 'theorem vad_t_F1_82002 : True := trivial', 'owns': ['vad_t_F1_82002'], 'origin': []},
    }
    res = G.audit_decls(d, held)
    expected_ok = {'clean', 'cites_cal', 'comment_only', 'prefix_name', 'target_header_only'}
    return {k: {'ok': v['ok'], 'reason': v['reason'], 'path': v['path'], 'as_expected': (k in expected_ok) == v['ok']}
            for k, v in res.items()}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--per-family', type=int, default=6)
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--work', type=Path, default=Path(tempfile.gettempdir()) / 'vad11_work')
    ap.add_argument('--out', type=Path, default=DEFAULT_OUT)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--repeats', type=int, default=1)
    ap.add_argument('--families', nargs='+', default=list(G.FAMILIES))
    ap.add_argument('--invent-max', type=int, default=6)
    ap.add_argument('--no-lean', action='store_true')
    args = ap.parse_args(argv)
    t0 = time.perf_counter()
    per = None if args.full else args.per_family
    fams = args.families
    R.CALLS.clear()

    receipt = {'protocol': 'VAD-11', 'primary_toolchain': R.PRIMARY, 'toolchains': list(R.VERSIONS),
               'lean_versions': R.versions_info(), 'parallelism': min(args.workers, R.MAX_WORKERS),
               'mode': {'full': args.full, 'per_family_per_split': per, 'repeats': args.repeats, 'families': fams,
                        'timeout_seconds': R.TIMEOUT},
               'source_sha256': {n: file_sha(Path(__file__).resolve().parent / n)
                                 for n in ('vad_gym.py', 'vad_lean_runner.py', 'verify_vad_gym.py')}}

    # 1 manifest ---------------------------------------------------------------------------
    manifest = G.split_manifest(None)
    receipt['manifest'] = manifest
    receipt['split_checks'] = {f: manifest[f]['checks'] for f in G.FAMILIES}

    # 2 fidelity on every generated statement -------------------------------------------------
    fid = {}
    for fam in fams:
        for sp in ('cal', 'test'):
            n = agree = true = 0
            fails = []
            for seed in G.split_seeds(sp):
                f = G.fidelity(G.gen(fam, seed, sp))
                n += 1
                agree += f['renderers_agree']
                true += f['python_true']
                if not (f['renderers_agree'] and f['python_true']):
                    fails.append(seed)
            fid[f'{fam}/{sp}'] = {'n': n, 'renderers_agree': agree, 'python_true': true, 'failures': fails}
    receipt['fidelity'] = fid

    # 3 slice -----------------------------------------------------------------------------------
    slice_specs = {(fam, sp): [G.gen(fam, s, sp) for s in G.split_seeds(sp, per)] for fam in fams for sp in ('cal', 'test')}
    instances = []
    failures = []
    if not args.no_lean:
        ws = G.Workspace(args.work, workers=args.workers)
        items, meta = [], {}
        for (fam, sp), specs in slice_specs.items():
            for spec in specs:
                for strat in G.STRATEGIES[fam]:
                    body, nm = G.build(spec, strat)
                    label = f'{nm}__{strat}'
                    items.append((label, body, nm))
                    meta[label] = (spec, strat)
        # build the library closure first so that targets measure only themselves
        deps = sorted({d for _, b, _ in items for d in G.imports_for(b)})
        if args.full:
            deps = sorted(set(deps) | {n for n, u in G.LIB.items() if u.tier != 'invented'})
        ws.build_units(deps)
        res = run_items(ws, items, args.repeats)
        by_inst = defaultdict(dict)
        for label, per_v in res.items():
            spec, strat = meta[label]
            by_inst[(spec['family'], spec['split'], spec['seed'])][strat] = {v: slim(r) for v, r in per_v.items()}
            for v, r in per_v.items():
                if not r['ok']:
                    failures.append({'file': label, 'version': v, 'timed_out': r['timed_out'],
                                     'error': (r['stdout'] + r['stderr'])[-500:]})
        for (fam, sp), specs in slice_specs.items():
            for spec in specs:
                fd = G.fidelity(spec)
                instances.append({'id': G.spec_id(spec), 'family': fam, 'split': sp, 'seed': spec['seed'],
                                  'templates': spec['templates'], 'size': size_key(spec), 'cost_hint': G.cost_hint(spec),
                                  'statement_sha256': fd['statement_sha256'], 'fidelity': {k: fd[k] for k in ('renderers_agree', 'python_true')},
                                  'strategies': by_inst[(fam, sp, spec['seed'])]})
        receipt['instances'] = instances

        # library costs
        lib = {}
        for (n, v), r in sorted(ws.unit_results.items()):
            u = G.LIB[n]
            ent = lib.setdefault(n, {'family': u.family, 'tier': u.tier, 'declarations': list(u.decls), 'theorems': list(u.theorems),
                                     'imports': G.unit_deps(u), 'origin': list(u.origin), 'results': {}})
            ent['results'][v] = slim(r)
            if not r['ok']:
                failures.append({'file': n, 'version': v, 'error': (r['stdout'] + r['stderr'])[-500:]})
        receipt['library'] = lib

        # summary -----------------------------------------------------------------------------
        summary = {}
        for fam in fams:
            summary[fam] = {}
            for strat in G.STRATEGIES[fam]:
                for v in R.VERSIONS:
                    rows = [i['strategies'][strat][v] for i in instances if i['family'] == fam and strat in i['strategies']]
                    entry = aggregate(rows)
                    bysize = defaultdict(list)
                    for i in instances:
                        if i['family'] == fam and strat in i['strategies'] and i['strategies'][strat][v]['ok']:
                            bysize[i['size']].append(i['strategies'][strat][v]['work_ms'])
                    entry['median_work_ms_by_size'] = {str(k): fnum(frac_median([x for x in xs if x is not None]), 3) for k, xs in sorted(bysize.items())}
                    summary[fam].setdefault(strat, {})[v] = entry
        receipt['summary'] = summary
        ax = Counter()
        for i in instances:
            for strat, per_v in i['strategies'].items():
                for v, r in per_v.items():
                    ax[f"{r['axiom_class']}:{','.join(sorted({a for t in r['axioms'].values() for a in t[1]}))}"] += 1
        receipt['axiom_summary'] = dict(ax)

    # 5/6 invention + dependency audit -----------------------------------------------------------
    held = G.held_out_names()
    inv = {}
    all_cal = {fam: [G.gen(fam, s, 'cal') for s in G.split_seeds('cal')] for fam in ('F1', 'F2', 'F5') if fam in fams}
    all_test = {fam: [G.gen(fam, s, 'test') for s in G.split_seeds('test')] for fam in ('F1', 'F2', 'F5') if fam in fams}
    for fam in all_cal:
        honest = G.invent(fam, all_cal[fam], max_pairs=args.invent_max)
        leaky = G.invent(fam, all_test[fam], max_pairs=args.invent_max)
        base = {**G.library_decls()}
        decls = {k: v for k, v in base.items()}
        verdicts = G.audit_decls(decls, held)
        rec = {'honest': [], 'leaky_control': []}
        for kind, cands in (('honest', honest), ('leaky_control', leaky)):
            for c in cands:
                v = verdicts[f"unit:{c['unit']}"]
                rec[kind].append({'unit': c['unit'], 'statement': c['stmt'], 'origin': c['origin'], 'audit': v})
        rec['honest_all_accepted'] = all(x['audit']['ok'] for x in rec['honest'])
        rec['leaky_all_rejected'] = all(not x['audit']['ok'] for x in rec['leaky_control'])
        accepted = [c for c in honest if verdicts[f"unit:{c['unit']}"]['ok']]
        # use of invented lemmas on calibration vs test slices
        if fam == 'F5':
            names = sorted(G.F5_SHAPES) + [c['shape'] for c in accepted]
            hit = lambda sp: [x for x in sp if G.f5_shape_hits(x, names) and set(G.f5_shape_hits(x, names)) & {c['shape'] for c in accepted}]
        else:
            hit = lambda sp: [x for x in sp if any(G.apply_candidate(x, c) for c in accepted)]
        rec['hits_cal_all_200'] = len(hit(all_cal[fam]))
        rec['hits_test_all_400'] = len(hit(all_test[fam]))
        leaky_acc = leaky
        rec['leaky_hits_test_all_400'] = (sum(1 for x in all_test[fam] if any(G.apply_candidate(x, c) for c in leaky_acc))
                                          if fam != 'F5' else None)
        if not args.no_lean and accepted:
            ws.build_units([c['unit'] for c in accepted])
            rec['kernel'] = {c['unit']: {v: slim(ws.unit_results[(c['unit'], v)]) for v in R.VERSIONS} for c in accepted}
            todo = []
            for sp, pool in (('cal', slice_specs.get((fam, 'cal'), []) + all_cal[fam][:40]), ('test', slice_specs.get((fam, 'test'), []))):
                got = 0
                for x in pool:
                    if got >= 4:
                        break
                    if fam == 'F5':
                        names = sorted(G.F5_SHAPES) + [c['shape'] for c in accepted]
                        if not (set(G.f5_shape_hits(x, names)) & {c['shape'] for c in accepted}):
                            continue
                        body, nm = G.f5_apply_with(x, names)
                    elif fam == 'F1':
                        r = [G.f1_build_with(x, accepted)]
                        if not r[0][2]:
                            continue
                        body, nm = r[0][0], r[0][1]
                    else:
                        r = next((G.apply_candidate(x, c) for c in accepted if G.apply_candidate(x, c)), None)
                        if r is None:
                            continue
                        body, nm = r
                    todo.append((f'{nm}__invented', body, nm, sp))
                    got += 1
            if todo:
                out = run_items(ws, [(a, b, c) for a, b, c, _ in todo], args.repeats)
                rec['applied_kernel_checks'] = [{'target': a, 'split_of_target': sp, 'results': {v: slim(r) for v, r in out[a].items()}}
                                                for a, _, _, sp in todo]
                for a, per_v in out.items():
                    for v, r in per_v.items():
                        if not r['ok']:
                            failures.append({'file': a, 'version': v, 'error': (r['stdout'] + r['stderr'])[-500:]})
        inv[fam] = rec
    receipt['invention'] = inv

    specs_test_all = [G.gen(f, s, 'test') for f in fams for s in G.split_seeds('test')]
    decls = {**G.library_decls(), **G.target_decls(specs_test_all)}
    verdict = G.audit_decls(decls, held)
    bad = {k: v for k, v in verdict.items() if not v['ok']}
    leak_units = {f"unit:{x['unit']}" for rec in inv.values() for x in rec['leaky_control']}
    unexpected = {k: v for k, v in bad.items() if k not in leak_units}
    receipt['dependency_audit'] = {'declarations_audited': len(verdict), 'held_out_targets': len(held),
                                   'rejected': len(bad), 'rejected_are_exactly_leak_controls': set(bad) == leak_units,
                                   'unexpected_rejections': unexpected, 'mutation_controls': mutation_controls()}
    receipt['failures'] = failures
    receipt['verifier_calls'] = dict(R.CALLS)
    receipt['wall_seconds'] = round(time.perf_counter() - t0, 1)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=1, sort_keys=True, default=list) + '\n', encoding='utf-8')

    # console summary -------------------------------------------------------------------------
    print(f"VAD-11 receipt -> {args.out}  ({receipt['wall_seconds']} s, verifier calls {receipt['verifier_calls']})")
    print('fidelity:', {k: f"{v['renderers_agree']}/{v['python_true']}/{v['n']}" for k, v in fid.items()})
    print('split checks:', receipt['split_checks'])
    if 'summary' in receipt:
        for fam, per_s in receipt['summary'].items():
            for strat, per_v in per_s.items():
                print(fam, strat, {v: (e['n_ok'], e['n'], e['median_work_ms'], e['median_seconds'], e['median_peak_rss_mb']) for v, e in per_v.items()})
    print('invention:', {f: (len(r['honest']), r['honest_all_accepted'], len(r['leaky_control']), r['leaky_all_rejected'],
                             r['hits_cal_all_200'], r['hits_test_all_400']) for f, r in inv.items()})
    print('audit:', {k: v for k, v in receipt['dependency_audit'].items() if k != 'mutation_controls'})
    print('failures:', len(failures))
    ok = (not failures and all(v['renderers_agree'] == v['n'] == v['python_true'] for v in fid.values())
          and receipt['dependency_audit']['rejected_are_exactly_leak_controls'])
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

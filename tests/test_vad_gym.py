"""Fast tests for the VAD-11 proof gym (python-only checks + 2 kernel-checked instances per family).

Kernel tests use the primary toolchain only and a persistent module cache under the system temp
directory (`vad11_test_work`), keyed by source sha256, so repeated runs only re-check what changed.
"""
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import vad_gym as G              # noqa: E402
import vad_lean_runner as R      # noqa: E402
import verify_vad_gym as V       # noqa: E402

HAVE_LEAN = R.lean_exe(R.PRIMARY).exists()


def specs(fam, split, n):
    base = 81000 if split == 'cal' else 82000
    return [G.gen(fam, base + i, split) for i in range(n)]


# --- statement fidelity -----------------------------------------------------------------------
@pytest.mark.parametrize('fam', G.FAMILIES)
def test_renderers_agree_and_python_truth(fam):
    for split in ('cal', 'test'):
        for spec in specs(fam, split, 25):
            r = G.render_spec(spec)
            p = G.parse_spec(fam, r)
            assert G.reprint_spec(fam, p) == r, (fam, spec['seed'])      # two code paths, byte for byte
            assert G.truth_spec(fam, p), (fam, spec['seed'], r)          # parsed text is true (brute force, no Lean)
            assert G.fidelity(spec)['python_true']


def test_python_truth_rejects_false_statements():
    s1 = G.gen('F1', 81000, 'cal')
    p = G.parse_spec('F1', G.render_spec(s1))
    p['rhs'] = ('n', p['rhs'])
    assert not G.f1_truth(p)
    s2 = G.gen('F2', 81000, 'cal')
    r = G.render_spec(s2)
    p2 = G.f2_parse_stmt(r['stmt'].replace(' = 0', ' = 1'))
    assert not G.f2_truth(p2)
    s3 = G.gen('F3', 81001, 'cal')
    p3 = G.parse_spec('F3', G.render_spec(s3))
    p3['table'] = [row[:] for row in p3['table']]
    p3['table'][0][0] = (p3['table'][0][0] + 1) % p3['m']
    assert not G.f3_truth(p3) or p3['law'] == 'lid' and p3['e'] != 0
    p4 = None
    for sd in range(81000, 81100):
        s4 = G.gen('F4', sd, 'cal')
        if s4['claim'] == 'compl_deg':
            p4 = G.parse_spec('F4', G.render_spec(s4))
            break
    assert G.f4_truth(p4)
    p4['matrix'][0][0] = True                                           # a loop breaks deg G + deg Gc = n-1
    assert not G.f4_truth(p4)
    s5 = G.gen('F5', 81000, 'cal')
    p5 = G.parse_spec('F5', G.render_spec(s5))
    p5['lhs'], p5['rhs'] = p5['rhs'], p5['lhs']
    assert not G.f5_truth(p5)


def test_generation_is_deterministic_and_templates_fresh():
    for fam in G.FAMILIES:
        a = [G.gen(fam, 82000 + i, 'test') for i in range(8)]
        b = [G.gen(fam, 82000 + i, 'test') for i in range(8)]
        assert a == b
    assert G.split_manifest(5)['manifest_sha256'] == G.split_manifest(5)['manifest_sha256']


# --- splits -----------------------------------------------------------------------------------
def test_split_disjointness_and_hashes():
    man = G.split_manifest(None)
    for fam in G.FAMILIES:
        ck = man[fam]['checks']
        assert ck['templates_disjoint'] and ck['observed_within_declared'] and ck['statements_disjoint'], (fam, ck)
        assert man[fam]['cal']['seeds'] == [81000, 81199] and man[fam]['cal']['count'] == 200
        assert man[fam]['test']['seeds'] == [82000, 82399] and man[fam]['test']['count'] == 400
        assert len(man[fam]['test']['statement_sha256']) == 400 and len(man[fam]['test']['split_sha256']) == 64
        assert set(man[fam]['cal']['templates_observed']).isdisjoint(man[fam]['test']['templates_observed'])
    assert man['F2']['checks']['moduli_disjoint']
    assert set(G.F2_MODULI['cal']).isdisjoint(G.F2_MODULI['test']) and all(3 <= m <= 12 for sp in G.F2_MODULI.values() for m in sp)
    assert set(G.F3_M['cal']).isdisjoint(G.F3_M['test']) and all(3 <= m <= 7 for sp in G.F3_M.values() for m in sp)
    assert all(5 <= n <= 7 for sp in G.F4_N.values() for n in sp)
    assert len(man['manifest_sha256']) == 64


# --- anti-unification ---------------------------------------------------------------------------
def test_lgg_structure_and_variable_sharing():
    a, b, c, d = G.V('a'), G.V('b'), G.V('c'), G.V('d')
    p = G.lgg(('a', a, a), ('a', b, b))
    assert p[1] == p[2] and p[1][0] == 'm'                                # repeated difference pair -> one variable
    q = G.lgg(('x', a, b), ('x', c, d))
    assert q[1] != q[2] and G.match(q, ('x', a, b)) == {q[1][1]: a, q[2][1]: b}
    assert G.lgg(('x', a, b), ('x', a, b)) == ('x', a, b)
    assert G.lgg(('x', a, ('n', b)), ('x', a, ('a', b, c))) == ('x', a, G.lgg(('n', b), ('a', b, c)))
    with pytest.raises(G.Incompatible):
        G.lgg(('^', a, 2), ('^', a, 3))                                   # exponents are not generalisable
    # the lgg is an instance-generalisation: both inputs are instances of the pattern
    t1, t2 = ('a', ('x', a, b), c), ('a', ('x', c, d), c)
    pat = G.lgg(t1, t2)
    assert G.match(pat, t1) is not None and G.match(pat, t2) is not None


def test_invented_candidates_are_true_and_come_from_calibration():
    cal = {f: [G.gen(f, s, 'cal') for s in range(81000, 81060)] for f in ('F1', 'F2', 'F5')}
    got = {}
    for fam in cal:
        cands = G.invent(fam, cal[fam], max_pairs=12)
        assert cands, fam
        got[fam] = cands
        for c in cands:
            assert all(o.startswith(f'vad_t_{fam}_81') for o in c['origin'])
    for c in got['F1']:                                                   # semantics re-decided from the printed statement
        p = G.f1_parse_stmt(c['stmt'])
        assert G.f1_truth(p)
    for c in got['F2']:
        assert G.f2_truth(G.f2_parse_stmt(c['stmt']))
    for c in got['F5']:
        xs = G.metas(c['pattern'])
        assert len(xs) >= 2 and G.size(c['pattern']) >= 5
    # a recovered rule lemma is reused on calibration instances but never matches fresh test templates
    f1_hits = [s for s in cal['F1'] if any(G.apply_candidate(s, c) for c in got['F1'])]
    test_hits = [s for s in specs('F1', 'test', 60) if any(G.apply_candidate(s, c) for c in got['F1'])]
    assert f1_hits and not test_hits
    recovered = {G.f1_render(G._canon_metas(('eq',) + G.F1_RULES[n][:2])[1]) for n in ('xor_comm', 'and_comm', 'and_assoc', 'xor_assoc', 'dist_l')}
    assert any(G.f1_render(G._canon_metas(c['pattern'])[1]) in recovered for c in got['F1'])   # lemma re-discovered from instances


# --- dependency auditor ---------------------------------------------------------------------------
def test_dependency_auditor_mutations():
    ctl = V.mutation_controls()
    for name, r in ctl.items():
        assert r['as_expected'], (name, r)
    assert ctl['cites_test']['reason'] == 'reaches_held_out' and ctl['cites_test']['path'] == ['cites_test', 'target_self']
    assert ctl['cites_lemma_citing_test']['path'] == ['cites_lemma_citing_test', 'cites_test', 'target_self']
    assert ctl['provenance']['reason'] == 'provenance_held_out'
    assert ctl['target_self']['reason'] == 'self_reference'
    held = {'vad_t_F1_82001', 'vad_t_F1_82002'}
    d = {'L1': {'text': 'theorem l1 : True := trivial', 'owns': ['l1'], 'origin': []},
         'L2': {'text': 'theorem l2 : True := l1', 'owns': ['l2'], 'origin': []},
         'L3': {'text': 'theorem l3 : True := by\n  have := vad_t_F1_82002\n  exact l2', 'owns': ['l3'], 'origin': []},
         'L4': {'text': 'theorem l4 : True := l3', 'owns': ['l4'], 'origin': []},
         'L5': {'text': 'theorem l5 : True := l4.elim', 'owns': ['l5'], 'origin': []},
         'T1': {'text': 'theorem vad_t_F1_82001 : True := l2', 'owns': ['vad_t_F1_82001'], 'origin': []},
         'T2': {'text': 'theorem vad_t_F1_82002 : True := l1', 'owns': ['vad_t_F1_82002'], 'origin': []},
         'T3': {'text': 'theorem vad_t_F1_82001 : True := l4', 'owns': ['vad_t_F1_82001'], 'origin': []}}
    r = G.audit_decls({k: v for k, v in d.items() if k != 'T3'}, held)
    assert [k for k, v in r.items() if not v['ok']] == ['L3', 'L4', 'L5']          # descendants, transitively
    assert r['L5']['path'] == ['L5', 'L4', 'L3', 'T2']
    r = G.audit_decls({k: v for k, v in d.items() if k not in ('T1', 'T2')}, held | {'vad_t_F1_82001'})
    assert not r['T3']['ok']                                                        # a test target citing a tainted lemma


def test_real_library_and_test_targets_are_not_tainted_and_leaks_are_rejected():
    held = G.held_out_names()
    test_specs = [s for f in G.FAMILIES for s in specs(f, 'test', 12)]
    base = {**G.library_decls(), **G.target_decls(test_specs)}
    assert all(v['ok'] for v in G.audit_decls(base, held).values())
    ts = [G.gen('F1', 82000 + i, 'test') for i in range(40)]
    leaky = G.invent('F1', ts, max_pairs=3)
    assert leaky
    verdict = G.audit_decls({**G.library_decls()}, held)
    for c in leaky:
        assert not verdict[f"unit:{c['unit']}"]['ok'] and verdict[f"unit:{c['unit']}"]['reason'] == 'provenance_held_out'
    # a lemma whose *proof text* cites a test target is rejected even with clean provenance
    sneaky = {'unit:sneaky': {'text': 'theorem vadl_sneaky : True := by\n  have := vad_t_F1_82003\n  trivial', 'owns': ['vadl_sneaky'], 'origin': []}}
    assert not G.audit_decls({**G.library_decls(), **sneaky}, held)['unit:sneaky']['ok']


# --- runner helpers ---------------------------------------------------------------------------------
def test_axiom_report_parser():
    out = ("'a' does not depend on any axioms\n'b' depends on axioms: [propext]\n"
           "'c' depends on axioms: [propext, Classical.choice, Quot.sound]\n'd' depends on axioms: [propext, sorryAx]\n"
           "'e' depends on axioms: [Lean.ofReduceBool]\nwarning: x\n")
    ax = R.parse_axioms(out)
    assert ax['a'] == ('none', []) and ax['b'] == ('standard', ['propext'])
    assert ax['c'][0] == 'standard' and ax['d'][0] == 'bad' and ax['e'][0] == 'bad'
    assert 'f' not in ax


def test_forbidden_token_scan_and_generated_sources_are_clean():
    assert R.forbidden_tokens('theorem t : True := by sorry') == ['sorry']
    assert 'native_decide' in R.forbidden_tokens('example : 1 = 1 := by native_decide')
    assert R.forbidden_tokens('axiom foo : False\nunsafe def x := 1') == ['axiom', 'unsafe']
    assert R.forbidden_tokens('-- sorry in a comment\ntheorem t : True := trivial') == []
    assert R.forbidden_tokens('theorem t : True := trivial /- admit -/') == []
    for fam in G.FAMILIES:
        for sp in ('cal', 'test'):
            for spec in specs(fam, sp, 6):
                for strat in G.STRATEGIES[fam]:
                    body, nm = G.build(spec, strat)
                    src = G.target_source(body, nm)
                    assert R.forbidden_tokens(src) == [] and f'#print axioms {nm}' in src
        assert all(R.forbidden_tokens(G.unit_source(u)) == [] for u in G.LIB.values())


def test_strategies_cite_library_only_for_lemma_strategy():
    for fam in G.FAMILIES:
        for spec in specs(fam, 'cal', 6):
            body_l, _ = G.build(spec, 'S_lemma')
            assert G.imports_for(body_l), (fam, spec['seed'])                 # genuinely reuses a library lemma
    body_d, _ = G.build(specs('F1', 'cal', 1)[0], 'S_decide')
    assert not G.imports_for(body_d) and body_d.endswith('by decide')


# --- kernel: two instances (one per strategy) per family under the primary toolchain -----------------
@pytest.fixture(scope='module')
def ws():
    return G.Workspace(Path(tempfile.gettempdir()) / 'vad11_test_work', versions=[R.PRIMARY], workers=4)


def cheap_spec(fam):
    best = None
    for spec in specs(fam, 'cal', 40):
        if fam == 'F3' and spec['law'] in ('medial',):
            continue
        h = G.cost_hint(spec)
        if best is None or h < best[0]:
            best = (h, spec)
    return best[1]


@pytest.mark.skipif(not HAVE_LEAN, reason='primary Lean toolchain not installed')
@pytest.mark.parametrize('fam', G.FAMILIES)
def test_kernel_two_strategies_per_family(ws, fam):
    spec = cheap_spec(fam)
    strats = [G.STRATEGIES[fam][0], 'S_lemma']
    items = []
    for strat in strats:
        body, nm = G.build(spec, strat)
        items.append((f'{nm}__{strat}', body, nm))
    res = ws.check_many(items)
    for label, per_v in res.items():
        r = per_v[R.PRIMARY]
        assert r['ok'], (label, r['stdout'], r['stderr'])
        assert r['axiom_class'] in ('none', 'standard') and r['verifier_calls'] == 1
        assert r['seconds'] > 0 and r['peak_rss_mb'] > 0 and not r['timed_out']


@pytest.mark.skipif(not HAVE_LEAN, reason='primary Lean toolchain not installed')
def test_runner_rejects_false_theorems_and_sorry(tmp_path):
    f1 = tmp_path / 'neg1.lean'
    f1.write_text('theorem vad_neg : (2 : Nat) = 3 := by decide\n#print axioms vad_neg\n', encoding='utf-8')
    r1 = R.run_lean(f1, R.PRIMARY, targets=('vad_neg',))
    assert not r1['ok'] and r1['rc'] != 0
    f2 = tmp_path / 'neg2.lean'
    f2.write_text('theorem vad_neg2 : (2 : Nat) = 3 := sorry\n#print axioms vad_neg2\n', encoding='utf-8')
    r2 = R.run_lean(f2, R.PRIMARY, targets=('vad_neg2',))
    assert not r2['ok'] and r2['forbidden'] == ['sorry'] and r2['axiom_class'] == 'bad'

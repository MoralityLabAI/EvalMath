"""MIT-13 pilot: fixtures, blindness, token matching, verifier agreement, scorer, Lean filter, dispatcher parsing."""
import sys, json, re, hashlib, importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
GYM = ROOT / 'gyms' / 'MathematicalInstrumentTransfer'
sys.path.insert(0, str(GYM))
import proof_pilot as pp
import mit13_fixtures as fx
import mit13_lean_check as lc
import mit13_dispatch as dp
import mit13_score as sc

N = 3
count = fx.whitespace_count


@pytest.fixture(scope='module')
def built():
    return fx.build(N, count, budget=4096, seed=13)


def test_determinism(built):
    assert fx.build(N, count, budget=4096, seed=13) == built
    assert fx.build(N, count, budget=4096, seed=14)[0] != built[0]


def test_row_counts_and_seeds(built):
    prompts, private = built
    for f in fx.FAMILIES:
        rows = [r for r in private if r['family'] == f]
        assert len(rows) == N * (7 + 3)
        assert {r['arm'] for r in rows if r['variant'] == 'false'} == {'unaided', 'instrument', 'adaptive'}
    assert len([r for r in private if r['family'] == 'lean']) == 16
    assert fx.SEED_BASE > 86031
    assert all(s >= fx.SEED_BASE for _, s, *_ in fx.roots(N))


def test_blindness(built):
    prompts, private = built
    assert all(set(p) == {'id', 'prompt', 'max_tokens'} for p in prompts)
    ids = [p['id'] for p in prompts]
    assert len(set(ids)) == len(ids) and all(re.fullmatch(r'd[0-9a-f]{16}', i) for i in ids)
    bad = re.compile(r'm13|-true|-false|near_miss|oracle|sham|adaptive|root_id|row_id|variant|family|transfer', re.I)
    for p in prompts:
        assert not bad.search(p['prompt']), p['prompt'][:200]
    by_id = {r['dispatch_id']: r for r in private}
    assert all(by_id[p['id']]['prompt_sha256'] == hashlib.sha256(p['prompt'].encode()).hexdigest() for p in prompts)


def test_transfer_contract_does_not_name_family(built):
    prompts, private = built
    by_id = {p['id']: p['prompt'] for p in prompts}
    for r in private:
        if r['family'] == 'transfer' and r['arm'] == 'unaided':
            text = by_id[r['dispatch_id']]
            assert 'cover' not in text.lower() and 'dual' not in text.lower()
            assert 'verdict' in text and 'certificate' in text and 'witness' in text


def test_unaided_matches_mit06():
    mit06 = {s['family']: s['target'] for _, s in pp.fixtures() if s['arm'] == 'unaided' and s['variant'] == 'true'}
    for f in pp.FAMILIES:
        assert fx.prompt(mit06[f], 'unaided') == pp.prompt(mit06[f], 'unaided')
        assert fx.prompt(mit06[f], 'instrument') == pp.prompt(mit06[f], 'instrument')


def test_token_matching_fake_tokenizer(built):
    _, private = built
    shams = [r for r in private if r['arm'] == 'sham']
    assert len(shams) == N * 5
    src = {r['root_id']: r['prompt_tokens'] for r in private if r['arm'] == 'source'}
    for r in shams:
        assert abs(r['sham_prompt_tokens'] - r['source_prompt_tokens']) <= 2
        assert r['prompt_tokens'] == r['sham_prompt_tokens']
        assert src[r['root_id']] == r['source_prompt_tokens']


def test_token_matching_skewed_tokenizer():
    skew = lambda t: len(t.split()) + t.count(',') * 2
    t, *_ = fx.transfer_instance(95000)
    prefix = fx.base_prompt(t)
    target = skew(fx.prompt(t, 'source'))
    text, c = fx.match_sham(prefix, target, *fx.sham_parts(t), skew)
    assert abs(c - target) <= 2 and c == skew(prefix + '\nRelated source: ' + text)
    jumpy = lambda s: 10 * len(s.split())
    with pytest.raises(ValueError):
        fx.match_sham('p', 55, 'a b c d', ['e f.'], jumpy, tol=2)


def test_token_cache(tmp_path):
    calls = []
    inner = lambda s: calls.append(s) or len(s.split())
    c = fx.CachedTokenizer(inner, tmp_path / 'c.json', 'm1')
    assert c('a b c') == 3 and c('a b c') == 3 and len(calls) == 1
    c.flush()
    c2 = fx.CachedTokenizer(inner, tmp_path / 'c.json', 'm1')
    assert c2('a b c') == 3 and len(calls) == 1
    fx.CachedTokenizer(inner, tmp_path / 'c.json', 'm2')('a b c')
    assert len(calls) == 2


def test_http_tokenizer_mock():
    tok = fx.HttpTokenizer('http://x', post=lambda path, payload: {'tokens': list(range(len(payload['content'].split())))})
    assert tok('one two three') == 3


def test_verify_bruteforce_agreement():
    for rid, seed, t, neg, good, bad, x in fx.roots(8):
        f = t['family']
        assert fx.independent(t) == (False if f == 'congruence' else t['bound'])
        assert fx.independent(neg) == (True if f == 'congruence' else t['bound'])
        assert fx.verify(t, dict(verdict='proved', certificate=good, witness=x))
        assert not fx.verify(t, dict(verdict='proved', certificate=bad, witness=x))
        assert fx.verify(neg, dict(verdict='counterexample', certificate=None, witness=x))
        assert fx.verify(t, fx.solve(t)[0]) and fx.verify(neg, fx.solve(neg)[0])


def test_transfer_instance():
    t, neg, good, bad, x = fx.transfer_instance(95001)
    assert t['family'] == neg['family'] == 'transfer' and fx.mapping_valid(t, good) and not fx.mapping_valid(t, bad)


def test_adaptive_menu(built):
    _, private = built
    for r in private:
        if r['arm'] == 'adaptive':
            assert sorted(r['menu']) == list('ABCD') and sorted(r['menu'].values()) == sorted(pp.FAMILIES)
            assert r['menu'][r['selected_gold']] == r['applicable_family']
    assert len({tuple(r['menu'].values()) for r in private if r['arm'] == 'adaptive'}) > 1


def test_lean_targets_shape():
    items = fx.lean_targets()
    assert len(items) == 8
    for it in items:
        assert it['statement'].startswith('theorem ' + it['name']) and lc.filter_proof(it['name'], it['reference']) is None
        assert ':= by' not in it['statement']


@pytest.mark.parametrize('proof,reason', [
    ('sorry', 'sorry'), ('exact sorryAx _ true', 'sorry'), ('admit', 'admit'), ('native_decide', 'native_decide'),
    ('omega\naxiom foo : False', 'axiom'), ('simp [implemented_by]', 'implemented_by'), ('@[simp] def', 'attribute'),
    ('unsafe', 'unsafe'), ('import Mathlib', 'import'), ('open Nat in omega', 'open'), ('set_option maxRecDepth 9 in decide', 'set_option'),
    ('exact mit13_lean_00 x y hx hy h1 h2', 'self-citation'), ('', 'empty'), ('omega\n#eval 1', 'command'),
    ('omega\ntheorem foo : True := trivial', 'top-level'), ('macro "x" : tactic => `(tactic| omega)', 'metaprogramming'),
    ('extern', 'extern')])
def test_lean_filter_rejects(proof, reason):
    r = lc.filter_proof('mit13_lean_00', proof)
    assert r and reason in r


def test_lean_filter_accepts_and_builds():
    assert lc.filter_proof('mit13_lean_00', 'intro x y\nomega') is None
    assert lc.filter_proof('mit13_lean_00', 'exact mit13_lean_000_helper') is None
    assert lc.build_file('t', 'theorem t : 1 = 1', 'rfl') == 'theorem t : 1 = 1 := by\n  rfl\n\n#print axioms t\n'


def test_lean_axiom_audit_with_fake_runner():
    ok = lambda s: (0, "'t' depends on axioms: [propext, Classical.choice]\n")
    assert lc.check('t', 'theorem t : 1 = 1', 'rfl', ok)['ok']
    bad = lambda s: (0, "'t' depends on axioms: [propext, sorryAx]\n")
    assert lc.check('t', 'theorem t : 1 = 1', 'rfl', bad)['reason'] == 'disallowed_axioms'
    assert lc.check('t', 'theorem t : 1 = 1', 'rfl', lambda s: (0, ''))['reason'] == 'axiom_output_missing'
    assert lc.check('t', 'theorem t : 1 = 1', 'rfl', lambda s: (1, 'x.lean:2:2: error: unsolved goals'))['reason'] == 'lean_error'
    assert lc.parse_axioms("'t' does not depend on any axioms") == []


# ---- dispatcher ----------------------------------------------------------------
@pytest.mark.parametrize('reply,expected', [
    ('{"verdict": "proved", "certificate": [1,2], "witness": [3,4]}', {'verdict': 'proved', 'certificate': [1, 2], 'witness': [3, 4]}),
    ('<think>{"verdict": "x"}</think>\n```json\n{"verdict": "counterexample", "witness": [1]}\n```', {'verdict': 'counterexample', 'witness': [1]}),
    ('Here you go: {"a": {"b": 1}} trailing {"c": 2}', {'a': {'b': 1}}),
    ('{bad json} then {"ok": true}', {'ok': True}),
])
def test_extract_json(reply, expected):
    assert dp.extract_json(reply) == (expected, None)


@pytest.mark.parametrize('reply', ['no json here', '', '<think>{"a":1}', '[1,2,3]', '{"a": '])
def test_extract_json_failures(reply):
    assert dp.extract_json(reply) == (None, 'no_json_object')


def fake_post(replies, usage=(100, 50), calls=None):
    it = iter(replies)

    def post(path, payload):
        if path == '/tokenize':
            return {'tokens': list(range(len(payload['content'].split())))}
        if calls is not None:
            calls.append(payload)
        u = {'prompt_tokens': usage[0], 'completion_tokens': usage[1]} if usage else {}
        return {'choices': [{'message': {'content': next(it), 'reasoning_content': 'think'}, 'finish_reason': 'stop'}], 'usage': u}
    return post


def test_run_row_retry_counts_all_attempts():
    calls = []
    row = dict(id='dabc', prompt='solve this', max_tokens=1000)
    r = dp.run_row(fake_post(['garbage', '{"verdict":"proved"}'], calls=calls), row, retries=1)
    assert r['response'] == {'verdict': 'proved'} and len(r['attempts']) == 2
    assert r['tokens_in'] == 200 and r['tokens_out'] == 100 and not r['over_budget']
    assert r['raw'] == ['garbage', '{"verdict":"proved"}'] and r['reasoning_len'] == 10
    assert calls[1]['max_tokens'] < calls[0]['max_tokens'] - 100
    assert calls[0]['messages'][1]['content'] == 'solve this' and calls[0]['messages'][0] == calls[1]['messages'][0]
    assert all(len(c['messages']) == 2 for c in calls)


def test_run_row_budget_stops_retry_and_flags_failure():
    row = dict(id='dabc', prompt='solve this', max_tokens=250)
    r = dp.run_row(fake_post(['garbage', '{"a":1}']), row, retries=1)
    assert r['response'] is None and len(r['attempts']) == 1 and r['parse_error'] == 'budget_exhausted'
    assert dp.run_row(fake_post(['{"a":1}'], usage=(250, 100)), row, retries=0)['over_budget']
    r = dp.run_row(fake_post([]), dict(id='x', prompt='p ' * 400, max_tokens=300), retries=1)
    assert r['parse_error'] == 'prompt_exceeds_budget' and r['attempts'] == []


def test_run_row_without_usage_and_request_error():
    row = dict(id='dabc', prompt='solve this', max_tokens=1000)
    r = dp.run_row(fake_post(['{"a":1}'], usage=None), row, retries=0)
    assert r['attempts'][0]['usage_reported'] is False and r['tokens_out'] > 0

    def boom(path, payload):
        if path == '/tokenize':
            return {'tokens': [1]}
        raise OSError('down')
    r = dp.run_row(boom, row, retries=1)
    assert r['response'] is None and r['parse_error'] == 'request_error' and len(r['attempts']) == 2


def test_dispatch_resumable_and_blind(tmp_path):
    prompts = tmp_path / 'p.jsonl'
    prompts.write_text(''.join(json.dumps(dict(id=f'd{i}', prompt=f'q{i}', max_tokens=1000)) + '\n' for i in range(5)))
    out = tmp_path / 'r.jsonl'
    seen = []

    def post(path, payload):
        if path == '/tokenize':
            return {'tokens': [1]}
        seen.append(payload['messages'])
        return {'choices': [{'message': {'content': '{"k": 1}'}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 10, 'completion_tokens': 5}}
    assert dp.dispatch('http://x', prompts, out, 7, 1, 0.0, post=post, limit=2) == 2
    assert dp.dispatch('http://x', prompts, out, 7, 1, 0.0, post=post) == 3
    assert dp.dispatch('http://x', prompts, out, 7, 1, 0.0, post=post) == 0
    ids = [json.loads(l)['row_id'] for l in out.read_text().splitlines()]
    assert sorted(ids) == [f'd{i}' for i in range(5)]
    assert all(len(m) == 2 and m[0]['role'] == 'system' and m[1]['role'] == 'user' for m in seen)
    assert len({m[0]['content'] for m in seen}) == 1


# ---- scorer ---------------------------------------------------------------------
def make_responses(private):
    resp = []
    for g in private:
        if g['family'] == 'lean':
            body = dict(proof=g['target']['reference'])
        else:
            body, _ = fx.solve(g['target'])
            if g['candidate'] is not None:
                body['mapping_valid'] = fx.mapping_valid(g['target'], g['candidate'])
            if g['arm'] == 'adaptive':
                body['selected_instrument'] = g['selected_gold']
        resp.append(dict(row_id=g['dispatch_id'], tokens_in=100, tokens_out=50, response=body, attempts=[{}], wall_ms=5))
    return resp


def fake_lean(name, statement, proof):
    return dict(ok=proof in ('omega', 'decide'), reason='ok', axioms=[], output='')


def run_score(tmp_path, private, resp, budget=1000):
    (tmp_path / 'private.jsonl').write_text(''.join(json.dumps(g) + '\n' for g in private))
    (tmp_path / 'resp.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in resp))
    return sc.main(tmp_path / 'private.jsonl', tmp_path / 'resp.jsonl', tmp_path / 's.json', budget, 'ck',
                   pilot_out=tmp_path / 'pilot.json', lean_fn=fake_lean)


def test_scorer_perfect(built, tmp_path):
    _, private = built
    res = run_score(tmp_path, private, make_responses(private))
    assert all(r['closed'] and r['status'] == 'ok' for r in res['rows'])
    assert all(r['applicability_correct'] for r in res['rows'] if r['applicability_correct'] is not None)
    assert all(r['selected_correct'] for r in res['rows'] if r['arm'] == 'adaptive')
    assert res['missing_rows'] == 0 and res['groups']


def test_scorer_failures_explicit(built, tmp_path):
    _, private = built
    resp = make_responses(private)
    by = {g['dispatch_id']: g for g in private}
    cands = [r for r in resp if by[r['row_id']]['arm'] == 'unaided' and by[r['row_id']]['variant'] == 'true'
             and by[r['row_id']]['family'] in ('lp', 'cover')]
    drop, bad, over, wrong = cands[:4]
    resp = [r for r in resp if r is not drop]
    bad['response'] = None
    over['tokens_out'] = 5000
    wrong['response'] = dict(verdict='proved', certificate=[0, 0], witness=[0, 0])
    orc = next(r for r in resp if by[r['row_id']]['arm'] == 'oracle')
    orc['response']['mapping_valid'] = 'yes'
    nm = next(r for r in resp if by[r['row_id']]['arm'] == 'near_miss')
    nm['response']['mapping_valid'] = True
    res = run_score(tmp_path, private, resp)
    rows = {r['dispatch_id']: r for r in res['rows']}
    for r, status in ((drop, 'missing'), (bad, 'malformed'), (over, 'over_budget'), (wrong, 'ok')):
        assert rows[r['row_id']]['status'] == status and not rows[r['row_id']]['closed']
    assert res['missing_rows'] == 1
    o, n = rows[orc['row_id']], rows[nm['row_id']]
    assert o['closed'] and o['applicability_correct'] is False
    assert n['closed'] and n['applicability_correct'] is False and n['false_accept'] is True


def test_scorer_selection_independent_of_closure(built, tmp_path):
    _, private = built
    resp = make_responses(private)
    by = {g['dispatch_id']: g for g in private}
    r = next(r for r in resp if by[r['row_id']]['arm'] == 'adaptive' and by[r['row_id']]['variant'] == 'true')
    g = by[r['row_id']]
    wrong = next(k for k in 'ABCD' if k != g['selected_gold'])
    r['response']['selected_instrument'] = wrong
    row = {x['dispatch_id']: x for x in run_score(tmp_path, private, resp)['rows']}[r['row_id']]
    assert row['closed'] and row['selected_correct'] is False and row['selected_family'] == g['menu'][wrong]


def test_scorer_rejects_unknown_ids(built, tmp_path):
    _, private = built
    resp = make_responses(private) + [dict(row_id='dfeedface', tokens_in=1, tokens_out=1, response={})]
    with pytest.raises(ValueError):
        run_score(tmp_path, private, resp)


def test_pilot_spec_runs_through_preflight(built, tmp_path):
    _, private = built
    run_score(tmp_path, private, make_responses(private))
    spec = json.loads((tmp_path / 'pilot.json').read_text())
    assert len(spec['pilot']) == N * 5 and all(set(u) == {'unit_id', 'paired_effect', 'sham_effects'} for u in spec['pilot'])
    path = ROOT / 'skills' / 'evalmath-mechinterp-power' / 'scripts' / 'preflight.py'
    s = importlib.util.spec_from_file_location('preflight', path)
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    out = mod.preflight(spec)
    assert out['pilot_worlds'] == N * 5 and out['decision'] == 'REDESIGN_OR_PILOT_ONLY'


def test_manifest(tmp_path):
    fx.main(['--output', str(tmp_path), '--roots-per-family', '2', '--tokenizer', 'whitespace'])
    m = json.loads((tmp_path / 'manifest.json').read_text())
    assert set(m['files']) == {'prompts.jsonl', 'private.jsonl'} and 'mit13_fixtures.py' in m['sources']
    assert m['files']['prompts.jsonl'] == fx.sha(tmp_path / 'prompts.jsonl')


def test_lean_reference_proofs_through_wsl():
    """CPU-only WSL Lean run; rejects a wrong proof."""
    for it in fx.lean_targets():
        res = lc.check(it['name'], it['statement'], it['reference'])
        assert res['ok'], res
        assert set(res['axioms']) <= lc.ALLOWED_AXIOMS
    it = fx.lean_targets()[0]
    assert not lc.check(it['name'], it['statement'], 'simp')['ok']

"""MIT-13 real-model proof pilot fixtures: seven arms, token-matched sham, transfer family, Lean targets.

Development roots only (seeds 91000+, disjoint from MIT-06's 83000-86031). No sealed split."""
import argparse, json, hashlib, subprocess, ast, sys
from pathlib import Path
from random import Random
from urllib import request
import development as d
import proof_pilot as pp

HERE = Path(__file__).parent
ARMS7 = pp.ARMS + ('adaptive',)
FAMILIES = pp.FAMILIES + ('transfer',)
SEED_BASE = 91000
TRANSFER_SEED = 95000
LLAMA_TOKENIZE = r'C:\Users\patri\tools\llama-b12686\bin\llama-tokenize.exe'
SOURCE_OF = {'lp': 'lp', 'path': 'path', 'cover': 'cover', 'congruence': 'congruence', 'transfer': 'lp'}
APPLICABLE = {'lp': 'lp', 'path': 'path', 'cover': 'cover', 'congruence': 'congruence', 'transfer': 'cover'}
LEAN_INSTRUMENT = {'omega': 'Hypotheses and goal are linear integer arithmetic over bounded naturals; a decision procedure for linear integer arithmetic closes them.',
                   'decide': 'The statement quantifies over small finite types with a decidable body; exhaustive evaluation closes it.'}


# ---- tokenizer backends -------------------------------------------------
class CliTokenizer:
    """llama-tokenize.exe on the model GGUF, CPU only (-ngl 0); the tool loads only the vocabulary."""
    def __init__(self, gguf, exe=LLAMA_TOKENIZE):
        self.gguf, self.exe = str(gguf), exe

    def __call__(self, text):
        p = subprocess.run([self.exe, '-m', self.gguf, '--stdin', '--ids', '--no-bos', '-ngl', '0', '--log-disable'],
                           input=text.encode(), capture_output=True, check=True)
        line = [l for l in p.stdout.decode('utf-8', 'replace').splitlines() if l.startswith('[')][-1]
        return len(ast.literal_eval(line))


class HttpTokenizer:
    """Counts through a running llama-server's /tokenize endpoint."""
    def __init__(self, base_url, post=None):
        self.base_url, self.post = base_url.rstrip('/'), post or self._post

    def _post(self, path, payload):
        req = request.Request(self.base_url + path, json.dumps(payload).encode(), {'Content-Type': 'application/json'})
        with request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())

    def __call__(self, text):
        return len(self.post('/tokenize', {'content': text, 'add_special': False})['tokens'])


class CachedTokenizer:
    """Counts cached in a JSON file keyed by sha256(text) + model key."""
    def __init__(self, inner, path, model_key):
        self.inner, self.path, self.model_key = inner, Path(path), model_key
        self.cache = json.loads(self.path.read_text()) if self.path.exists() else {}

    def __call__(self, text):
        key = hashlib.sha256(text.encode()).hexdigest() + ':' + self.model_key
        if key not in self.cache:
            self.cache[key] = self.inner(text)
        return self.cache[key]

    def flush(self):
        self.path.write_text(json.dumps(self.cache, sort_keys=True))


def model_key(gguf):
    """Cheap stable model identity: size plus sha256 of the first 64 MiB."""
    p = Path(gguf)
    with p.open('rb') as f:
        head = f.read(1 << 26)
    return f'{p.stat().st_size}-{hashlib.sha256(head).hexdigest()[:16]}'


def whitespace_count(text):
    return len(text.split())


# ---- token-matched sham ---------------------------------------------------
def _fit(words, n):
    text = ' '.join(words[:n])
    return text if text.endswith('.') else text.rstrip(',;:') + '.'


def match_sham(prefix, target_count, base_text, filler, count, tol=2):
    """Sham source whose full prompt token count is within tol of target_count.

    prefix: prompt text before the source line. base_text: the irrelevant source. filler: neutral sentences
    appended after it. Returns (sham_text, sham_prompt_count)."""
    words = base_text.split()
    sents = [s for s in filler if s]
    while True:
        full = prefix + '\nRelated source: ' + _fit(words, len(words))
        if count(full) >= target_count - tol or len(words) > 20000:
            break
        for s in sents:
            words += s.split()
    line = lambda n: prefix + '\nRelated source: ' + _fit(words, n)
    lo, hi = 1, len(words)
    while lo < hi:
        mid = (lo + hi) // 2
        if count(line(mid)) >= target_count:
            hi = mid
        else:
            lo = mid + 1
    best = min(range(max(1, lo - 3), min(len(words), lo + 3) + 1), key=lambda n: abs(count(line(n)) - target_count))
    c = count(line(best))
    if abs(c - target_count) > tol:
        raise ValueError(f'sham token match failed: {c} vs {target_count}')
    return _fit(words, best), c


# ---- targets ----------------------------------------------------------------
def base(t):
    return dict(t, family='cover') if t['family'] == 'transfer' else t


def mapping_valid(t, m):
    return pp.mapping_valid(base(t), m)


def verify(t, r):
    return pp.verify(base(t), r)


def independent(t):
    return pp.independent(base(t))


def solve(t):
    return pp.solve(base(t))


def transfer_instance(seed):
    t, good, bad, x = pp.cover(seed)
    t = dict(t, family='transfer')
    neg = dict(pp.false_variant(base(t), x), family='transfer')
    return t, neg, good, bad, x


CONTRACT = ('\nReturn one JSON object: verdict (proved or counterexample), certificate (integer list or null), witness '
            '(integer list or null). A proved result requires a checkable certificate; supply an attaining witness for a '
            'sharp bound. A counterexample requires a witness refuting the claim.')


def transfer_base(t):
    data = {k: v for k, v in t.items() if k != 'family'}
    return ('A staffing office schedules two crew types, counted in whole people x[0] and x[1], each between 0 and box. '
            'Task i needs at least b[i] work units, and one person of crew type j supplies A[i][j] units on task i. '
            'One person of crew type j costs c[j]. The office claims that the lowest possible total cost, c dot x, '
            'equals bound.\nData: ' + json.dumps(data, sort_keys=True) + CONTRACT)


def base_prompt(t):
    return transfer_base(t) if t['family'] == 'transfer' else pp.prompt(t, 'unaided')


def menu_for(root_id, seed):
    """Seeded letter -> family menu over the four family instruments."""
    order = list(pp.FAMILIES)
    Random(f'menu-{seed}-{root_id}').shuffle(order)
    return {chr(65 + i): f for i, f in enumerate(order)}


def prompt(t, arm, candidate=None, sham_text=None, menu=None):
    f = t['family']
    if arm == 'unaided':
        return base_prompt(t)
    if f != 'transfer' and arm in ('source', 'instrument', 'near_miss', 'oracle'):
        return pp.prompt(t, arm, candidate)
    text = base_prompt(t)
    if arm == 'source':
        return text + '\nRelated source: ' + pp.SOURCE[SOURCE_OF[f]]
    if arm == 'instrument':
        return text + '\nSuggested technique: ' + pp.INSTRUMENT[SOURCE_OF[f]]
    if arm in ('near_miss', 'oracle'):
        return (text + '\nSuggested technique: ' + pp.INSTRUMENT['cover'] + ' Candidate certificate: ' + json.dumps(candidate) +
                '. Also return mapping_valid (boolean) for the candidate, even if replacing it.')
    if arm == 'sham':
        return text + '\nRelated source: ' + sham_text
    if arm == 'adaptive':
        lines = ''.join(f'\n{k}: {pp.INSTRUMENT[v]}' for k, v in menu.items())
        return (text + '\nChoose exactly one of these techniques and apply it:' + lines +
                '\nAlso return selected_instrument: the letter of the technique you chose.')
    raise ValueError('unknown arm')


def sham_parts(t):
    f = t['family']
    irrelevant = 'path' if f == 'congruence' else 'congruence'
    skip = {SOURCE_OF[f], irrelevant}
    filler = [s.strip() + '.' for k in pp.FAMILIES if k not in skip for s in pp.SOURCE[k].split('. ') if s.strip().strip('.')]
    return pp.SOURCE[irrelevant], [s.replace('..', '.') for s in filler]


# ---- Lean targets -----------------------------------------------------------
def lean_targets():
    """Eight finite-integer Lean 4 theorems with reference proofs: 6 omega (LP-style), 2 decide (congruence-style)."""
    out = []
    for i in range(6):
        t, _, _, _ = d.lp(93000 + i)
        a, b, c = t['A'], t['b'], t['c']
        hyp = ' '.join(f'(h{k + 1} : {a[k][0]} * x + {a[k][1]} * y ≤ {b[k]})' for k in range(2))
        st = (f'theorem mit13_lean_{i:02d} (x y : Nat) (hx : x ≤ 8) (hy : y ≤ 8) {hyp} :\n'
              f'    {c[0]} * x + {c[1]} * y ≤ {t["bound"]}')
        out.append(dict(name=f'mit13_lean_{i:02d}', statement=st, reference='omega', kind='omega'))
    seed = 93100
    while len(out) < 8:
        t, _, _, _ = pp.congruence(seed)
        seed += 1
        if t['p'] > 7:
            continue
        p, a, b = t['p'], t['A'], t['b']
        i = len(out)
        st = (f'theorem mit13_lean_{i:02d} : ∀ x y : Fin {p},\n    ¬ (({a[0][0]} * x.val + {a[0][1]} * y.val) % {p} = {b[0]} ∧ '
              f'({a[1][0]} * x.val + {a[1][1]} * y.val) % {p} = {b[1]})')
        out.append(dict(name=f'mit13_lean_{i:02d}', statement=st, reference='decide', kind='decide'))
    return out


def lean_prompt(item, arm):
    text = ('Prove the following Lean 4 theorem using core Lean only (no Mathlib, no imports, no sorry). Return one JSON '
            'object with key proof whose value is only the tactic block that follows `:= by`.\n\n' + item['statement'])
    return text + ('\nSuggested technique: ' + LEAN_INSTRUMENT[item['kind']] if arm == 'instrument' else '')


# ---- build ----------------------------------------------------------------------
def roots(n):
    makers = dict(lp=d.lp, path=d.path, cover=pp.cover, congruence=pp.congruence)
    for fi, f in enumerate(pp.FAMILIES):
        for i in range(n):
            seed = SEED_BASE + i + 1000 * fi
            t, good, bad, x = makers[f](seed)
            yield f'{f}-m13-{i:02d}', seed, t, pp.false_variant(t, x), good, bad, x
    for i in range(n):
        seed = TRANSFER_SEED + i
        t, neg, good, bad, x = transfer_instance(seed)
        yield f'transfer-m13-{i:02d}', seed, t, neg, good, bad, x


def build(n, count, budget=4096, seed=13):
    """Return (prompt_rows, private_rows). count: text -> token count."""
    rows = []
    for rid, rseed, t, neg, good, bad, x in roots(n):
        f = t['family']
        assert rseed >= SEED_BASE
        assert mapping_valid(t, good) and not mapping_valid(t, bad)
        assert independent(t) == (False if f == 'congruence' else t['bound'])
        assert independent(neg) == (True if f == 'congruence' else t['bound'])
        assert verify(t, dict(verdict='proved', certificate=good, witness=x))
        assert verify(neg, dict(verdict='counterexample', certificate=None, witness=x))
        menu = menu_for(rid, seed)
        letter = next(k for k, v in menu.items() if v == APPLICABLE[f])
        for variant, target, arms in (('true', t, ARMS7), ('false', neg, ('unaided', 'instrument', 'adaptive'))):
            src_count = count(prompt(target, 'source')) if variant == 'true' else None
            for arm in arms:
                cand = good if arm == 'oracle' else bad if arm == 'near_miss' else None
                sham_text = None
                info = {}
                if arm == 'sham':
                    prefix = base_prompt(target)
                    sham_text, c = match_sham(prefix, src_count, *sham_parts(target), count)
                    info = dict(source_prompt_tokens=src_count, sham_prompt_tokens=c)
                text = prompt(target, arm, cand, sham_text, menu)
                rows.append(dict(
                    row_id=f'{rid}-{variant}-{arm}', root_id=rid, family=f, variant=variant, arm=arm, target=target,
                    candidate=cand, expected_mapping_valid=mapping_valid(target, cand) if cand is not None else None,
                    selected_gold=letter if arm == 'adaptive' else None, menu=menu if arm == 'adaptive' else None,
                    applicable_family=APPLICABLE[f], prompt=text, prompt_tokens=count(text), **info))
    for item in lean_targets():
        for arm in ('unaided', 'instrument'):
            text = lean_prompt(item, arm)
            rows.append(dict(row_id=f'{item["name"]}-true-{arm}', root_id=item['name'], family='lean', variant='true',
                             arm=arm, target=item, candidate=None, expected_mapping_valid=None, selected_gold=None,
                             menu=None, applicable_family='lean', prompt=text, prompt_tokens=count(text)))
    rng = Random(f'dispatch-{seed}')
    ids = set()
    prompts, private = [], []
    for r in rows:
        did = f'd{rng.getrandbits(64):016x}'
        assert did not in ids
        ids.add(did)
        r['dispatch_id'] = did
        r['prompt_sha256'] = hashlib.sha256(r['prompt'].encode()).hexdigest()
        r['token_budget'] = budget
        prompts.append(dict(id=did, prompt=r.pop('prompt'), max_tokens=budget))
        private.append(r)
    order = sorted(range(len(rows)), key=lambda i: prompts[i]['id'])
    return [prompts[i] for i in order], [private[i] for i in order]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(out, prompts, private, meta):
    out.mkdir(parents=True, exist_ok=True)
    for name, entries in (('prompts.jsonl', prompts), ('private.jsonl', private)):
        (out / name).write_text(''.join(json.dumps(e, sort_keys=True) + '\n' for e in entries))
    manifest = dict(schema='mit13-pilot-fixtures-v1', rows=len(private), roots=len({r['root_id'] for r in private}),
                    seed_range=[SEED_BASE, TRANSFER_SEED + 1000], **meta,
                    files={n: sha(out / n) for n in ('prompts.jsonl', 'private.jsonl')},
                    sources={n: sha(HERE / n) for n in ('proof_pilot.py', 'development.py', 'mit13_fixtures.py', 'mit13_lean_check.py')})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--roots-per-family', type=int, default=8)
    p.add_argument('--budget', type=int, default=4096, help='total tokens per row: prompt + all attempts')
    p.add_argument('--seed', type=int, default=13, help='dispatch-id and menu seed')
    p.add_argument('--tokenizer', choices=('whitespace', 'cli', 'http'), default='cli')
    p.add_argument('--gguf', help='model GGUF for the cli tokenizer')
    p.add_argument('--base-url', help='llama-server URL for the http tokenizer')
    p.add_argument('--model-id', default='', help='model identity for the http tokenizer cache key')
    p.add_argument('--cache', type=Path, default=None)
    a = p.parse_args(argv)
    if a.tokenizer == 'cli':
        inner, key = CliTokenizer(a.gguf), model_key(a.gguf)
    elif a.tokenizer == 'http':
        inner, key = HttpTokenizer(a.base_url), a.model_id
    else:
        inner, key = whitespace_count, 'whitespace'
    count = CachedTokenizer(inner, a.cache or a.output / 'token_cache.json', key)
    a.output.mkdir(parents=True, exist_ok=True)
    prompts, private = build(a.roots_per_family, count, a.budget, a.seed)
    count.flush()
    m = write(a.output, prompts, private, dict(tokenizer=a.tokenizer, model_key=key, budget=a.budget, seed=a.seed,
                                               roots_per_family=a.roots_per_family))
    print(json.dumps(m, indent=2))


if __name__ == '__main__':
    main()

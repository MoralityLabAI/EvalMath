"""VAD-11: a harder, kernel-checked core-Lean proof gym with competing proof strategies.

Everything is deterministic: instance (family, split, seed) -> spec is a pure function.
No Mathlib, no lake. Every generated file is checked by `lean file.lean` in a fresh
process (see vad_lean_runner) under two toolchains; library lemmas are separate
modules compiled once per toolchain to .olean and imported by the files that cite them.

Families (each: seeded generator, template renderer, independent parser, re-printer,
Python semantic evaluator, >= 2 proof strategies):
  F1 Boolean polynomial identities, 4-7 variables, 1-3 chained rewrite steps with
     rules over xor/and/not.  S_decide = `decide` (cost ~ 2^n x term size).
     S_lemma = chain of instantiated library rule lemmas (congrArg + Eq.trans).
  F2 modular arithmetic over Nat, degree 2-4, moduli 3-12.  S_decide = structural
     reduction to n % m via modeq lemmas, then `decide` on all residues.
     S_lemma = base lemma (itself an F2 instance) + composition lemma.
  F3 finite algebra on Fin m, m = 3..7 (assoc / comm / medial / identity / inverse).
     S_decide = `decide` (m^3, m^4, ...).  S_lemma = base-operation lemma (per
     operation and m, proved once) transported along a relabeling (homomorphism)
     lemma; the relabeling hypothesis costs only m^2.
  F4 graph invariants on Nat-indexed Bool adjacency matrices, n = 5..7:
     bipartite colouring + triangle-freeness, proper 3-colouring + K4-freeness,
     complement degree identity, degree-sum evenness, complement regularity.
     S_decide = `decide`; S_lemma = general lemma (colouring => no K3/K4, loopless =>
     deg G v + deg Gc v = n-1, symmetric+loopless => handshake) with O(n^2) side checks.
  F5 monotone product/sum inequalities over Nat from x_i <= y_i.  S_direct = explicit
     Nat.mul_le_mul / Nat.add_le_add term; S_omega = per-product `have` + omega with
     the products as atoms; S_lemma = library shape lemmas (prod3, sum of products,
     ...) matched structurally.

Statement fidelity: render(spec) is the template renderer; parse(text) is a separate
recursive-descent/regex parser of the *Lean text*; reprint(parsed) is a second printer.
`fidelity(spec)` checks render == reprint byte-for-byte and then decides truth of the
PARSED statement by brute force (all assignments for Bool, n in 0..2m for Nat claims,
the whole finite domain for Fin/graph claims, x<=y in 0..2 for F5) without Lean.

Splits: calibration seeds 81000-81199, test seeds 82000-82399 per family.  Test
templates (rule sets, polynomial bases, operation templates, graph templates, product
shapes) and moduli sets are disjoint from calibration templates; `split_manifest`
records every statement sha256, the template sets and the disjointness checks.

Abstraction invention: `lgg` is structural anti-unification (least general
generalisation, repeated difference pairs share one variable) over the statement ASTs
(F1 equations, F2 residue claims, F5 shapes); `invent_*` turn an lgg into a candidate
lemma, filter it by Python semantics, then it is proved by the family strategy at small
size and kernel-checked/cached as an `inv_` unit.  The strict-exclusion auditor
(`audit_decls`) parses identifiers of all generated sources against the library and
rejects any lemma that reaches, transitively, a held-out (test) target or any
descendant of one; provenance (the instances a lemma was generalised from) is audited
too.  Test targets themselves may not cite any test target.

Library lemmas are tiered: 'base' (generic), 'cal' (templates of the calibration
split), 'test_ref' (reference lemmas for test templates; independent of any target:
they are the oracle "intermediate lemma" that an inventing agent must rediscover).

Cost notes: wall seconds include ~0.4 s (4.19) / ~0.55 s (4.35) process start-up and
import; compare strategies by the difference or by the medians of the same family.
"""
import hashlib
import itertools
import json
import random
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

SEEDS = {'cal': range(81000, 81200), 'test': range(82000, 82400)}
FAMILIES = ('F1', 'F2', 'F3', 'F4', 'F5')
STRATEGIES = {'F1': ('S_decide', 'S_lemma'), 'F2': ('S_decide', 'S_lemma'),
              'F3': ('S_decide', 'S_lemma'), 'F4': ('S_decide', 'S_lemma'),
              'F5': ('S_direct', 'S_omega', 'S_lemma')}
HEADER = ("set_option autoImplicit false\nset_option linter.unusedVariables false\nset_option profiler true\n"
          "set_option synthInstance.maxSize 100000\nset_option synthInstance.maxHeartbeats 200000\n"
          "set_option maxRecDepth 100000\n")


def sha(x):
    return hashlib.sha256(x.encode('utf-8') if isinstance(x, str) else x).hexdigest()


def rng_for(fam, split, seed, attempt=0):
    return random.Random(f'vad11/{fam}/{split}/{seed}/{attempt}')


# ---------------------------------------------------------------------------
# Lean source utilities, library registry, dependency auditor
# ---------------------------------------------------------------------------

def strip_comments(text):
    text = re.sub(r'/-.*?-/', ' ', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_'.!?]*")
_DECL = re.compile(r"^(?:theorem|def|lemma|abbrev|instance)\s+([A-Za-z_][A-Za-z0-9_'.]*)", re.M)


def declared_names(text):
    return _DECL.findall(strip_comments(text))


def referenced_names(text, universe):
    """Identifiers of the comment-stripped source that name something in `universe`
    (whole identifier, or a dotted prefix such as `vad_x.symm` -> `vad_x`)."""
    out = set()
    for ident in _IDENT.findall(strip_comments(text)):
        parts = ident.split('.')
        for i in range(1, len(parts) + 1):
            cand = '.'.join(parts[:i])
            if cand in universe:
                out.add(cand)
    return out


class Unit:
    """A library module: one or more declarations compiled to M_<name>.olean."""

    def __init__(self, name, family, tier, body, origin=()):
        self.name, self.family, self.tier, self.body = name, family, tier, body
        self.origin = tuple(origin)

    module = property(lambda s: 'M_' + s.name)
    decls = property(lambda s: tuple(declared_names(s.body)))
    theorems = property(lambda s: tuple(re.findall(r"^theorem\s+([A-Za-z_][A-Za-z0-9_'.]*)", strip_comments(s.body), re.M)))


LIB = {}          # unit name -> Unit
DECL2UNIT = {}    # declaration name -> unit name


def add_unit(name, family, tier, body, origin=()):
    u = Unit(name, family, tier, body.strip('\n') + '\n', origin)
    if name in LIB:
        assert LIB[name].body == u.body, name
        return LIB[name]
    LIB[name] = u
    for d in u.decls:
        assert d not in DECL2UNIT, (d, name)
        DECL2UNIT[d] = name
    return u


def unit_deps(u):
    refs = referenced_names(u.body, set(DECL2UNIT))
    return sorted({DECL2UNIT[r] for r in refs} - {u.name})


def imports_for(text, exclude=()):
    refs = referenced_names(text, set(DECL2UNIT))
    return sorted({DECL2UNIT[r] for r in refs} - set(exclude))


def unit_source(u):
    imp = ''.join(f'import {LIB[d].module}\n' for d in unit_deps(u))
    prints = ''.join(f'#print axioms {t}\n' for t in u.theorems)
    return imp + HEADER + u.body + prints


def target_source(body, target):
    imp = ''.join(f'import {LIB[d].module}\n' for d in imports_for(body))
    return imp + HEADER + body.strip('\n') + f'\n#print axioms {target}\n'


def closure(unit_names):
    """Topologically ordered unit closure."""
    order, seen = [], set()

    def visit(n):
        if n in seen:
            return
        seen.add(n)
        for d in unit_deps(LIB[n]):
            visit(d)
        order.append(n)
    for n in unit_names:
        visit(n)
    return order


# --- strict-exclusion dependency auditor ---------------------------------

def audit_decls(decls, held_out):
    """decls: {name: {'text': lean source of the declaration(s), 'origin': [ids], 'owns': [declared names]}}
    held_out: set of declaration names that are held-out test targets.
    Returns {name: {'ok': bool, 'reason': str|None, 'path': [...]}}.
    A decl is rejected when its reference graph reaches (transitively) a held-out target,
    when it is itself tainted (a descendant of one), or when its provenance (`origin`)
    names a held-out instance id.  Held-out targets may not cite held-out targets
    (including themselves)."""
    owner = {}
    for k, d in decls.items():
        for n in d.get('owns', [k]):
            owner[n] = k
    edges = {}
    for k, d in decls.items():
        text = d['text']
        for n in d.get('owns', [k]):   # the declaration header itself is not a reference
            text = re.sub(r'^(theorem|def|lemma|abbrev|instance)\s+' + re.escape(n) + r"(?![A-Za-z0-9_'.])", r'\1 _', text, flags=re.M)
        edges[k] = {owner.get(r, 'held:' + r) for r in referenced_names(text, set(owner) | set(held_out))}
    held_keys = {owner.get(h, 'held:' + h) for h in held_out}
    res = {}
    for k, d in decls.items():
        # DFS for the shortest path to a held-out key (excluding the start unless it cites itself via an edge)
        path, seen, stack = None, {k}, [(k, [k])]
        while stack and path is None:
            cur, p = stack.pop()
            for nxt in sorted(edges.get(cur, ())):
                if nxt in held_keys:
                    path = p + [nxt]
                    break
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append((nxt, p + [nxt]))
        origin_hit = [o for o in d.get('origin', []) if o in held_out]
        if path is not None:
            kind = 'self_reference' if k in held_keys and path == [k, k] else 'reaches_held_out'
            res[k] = {'ok': False, 'reason': kind, 'path': path}
        elif origin_hit:
            res[k] = {'ok': False, 'reason': 'provenance_held_out', 'path': origin_hit}
        else:
            res[k] = {'ok': True, 'reason': None, 'path': []}
    return res


# ---------------------------------------------------------------------------
# Generic AST helpers: first-order matching and anti-unification (lgg)
# ---------------------------------------------------------------------------
LEAF_TAGS = {'v', 'c', 'T', 'F', 'm', 'hole'}


class Incompatible(Exception):
    pass


def is_leaf(t):
    return not isinstance(t, tuple) or t[0] in LEAF_TAGS


def match(pat, term, sub=None):
    """First-order match of pattern (with ('m', name) metavariables) against a term."""
    sub = {} if sub is None else sub
    if isinstance(pat, tuple) and pat and pat[0] == 'm':
        if pat[1] in sub:
            return sub if sub[pat[1]] == term else None
        sub[pat[1]] = term
        return sub
    if not isinstance(pat, tuple) or not isinstance(term, tuple):
        return sub if pat == term else None
    if pat[0] != term[0] or len(pat) != len(term):
        return None
    for p, t in zip(pat[1:], term[1:]):
        if match(p, t, sub) is None:
            return None
    return sub


def subst(pat, sub):
    if isinstance(pat, tuple) and pat and pat[0] == 'm':
        return sub[pat[1]]
    if isinstance(pat, tuple):
        return (pat[0],) + tuple(subst(p, sub) for p in pat[1:])
    return pat


def metas(pat, acc=None):
    acc = [] if acc is None else acc
    if isinstance(pat, tuple) and pat and pat[0] == 'm':
        if pat[1] not in acc:
            acc.append(pat[1])
    elif isinstance(pat, tuple):
        for p in pat[1:]:
            metas(p, acc)
    return acc


def lgg(t1, t2, table=None, prefix='X'):
    """Structural anti-unification: least general generalisation of two ASTs.
    Differing leaves/subtrees become metavariables; the same pair of differing subterms
    shares one variable.  Differing non-AST atoms (e.g. exponents) are Incompatible."""
    table = {} if table is None else table
    if t1 == t2:
        return t1
    if isinstance(t1, tuple) and isinstance(t2, tuple) and not is_leaf(t1) and not is_leaf(t2) \
            and t1[0] == t2[0] and len(t1) == len(t2):
        return (t1[0],) + tuple(lgg(a, b, table, prefix) for a, b in zip(t1[1:], t2[1:]))
    if not isinstance(t1, tuple) or not isinstance(t2, tuple):
        raise Incompatible((t1, t2))
    key = (t1, t2)
    if key not in table:
        table[key] = ('m', f'{prefix}{len(table)}')
    return table[key]


def size(t):
    return 1 + sum(size(c) for c in t[1:]) if isinstance(t, tuple) and not is_leaf(t) else 1


def tokens_join(tokens):
    """Second printer path: join tokens with a space except after '(' / '!' and before ')'."""
    out = ''
    prev = ''
    for tk in tokens:
        if out and prev not in ('(', '!') and tk not in (')', ','):
            out += ' '
        out += tk
        prev = tk
    return out


def split_top(s, sep):
    """Split s at the first top-level (paren depth 0) occurrence of sep."""
    depth = 0
    for i in range(len(s) - len(sep) + 1):
        c = s[i]
        depth += (c == '(') - (c == ')')
        if depth == 0 and s.startswith(sep, i):
            return s[:i], s[i + len(sep):]
    raise ValueError(f'no top-level {sep!r} in {s!r}')


def tokenize(s, extra=()):
    pat = r"\(|\)|&&|!|\+|\*|\^|%|=|≤|→|∀|:|,|[A-Za-z_][A-Za-z0-9_']*|\d+"
    toks = re.findall(pat, s)
    assert ''.join(toks) == re.sub(r'\s+', '', s), (toks, s)
    return toks


VARS = 'abcdefg'
T_, F_ = ('T',), ('F',)


def V(n):
    return ('v', n)


def M(n):
    return ('m', n)


# ---------------------------------------------------------------------------
# F1  Boolean polynomial identities
# ---------------------------------------------------------------------------
def bx(a, b): return ('x', a, b)
def ba(a, b): return ('a', a, b)
def bn(a): return ('n', a)


A_, B_, C_ = M('A'), M('B'), M('C')
# name: (lhs, rhs, split)    -- all are Bool identities, checked by decide in the library
F1_RULES = {
    'dist_l': (ba(A_, bx(B_, C_)), bx(ba(A_, B_), ba(A_, C_)), 'cal'),
    'dist_r': (ba(bx(B_, C_), A_), bx(ba(B_, A_), ba(C_, A_)), 'cal'),
    'and_idem': (ba(A_, A_), A_, 'cal'),
    'xor_self': (bx(A_, A_), F_, 'cal'),
    'xor_false': (bx(A_, F_), A_, 'cal'),
    'and_true': (ba(A_, T_), A_, 'cal'),
    'and_false': (ba(A_, F_), F_, 'cal'),
    'xor_comm': (bx(A_, B_), bx(B_, A_), 'cal'),
    'and_comm': (ba(A_, B_), ba(B_, A_), 'cal'),
    'xor_assoc': (bx(bx(A_, B_), C_), bx(A_, bx(B_, C_)), 'cal'),
    'and_assoc': (ba(ba(A_, B_), C_), ba(A_, ba(B_, C_)), 'cal'),
    'absorb': (ba(A_, bx(bx(A_, B_), ba(A_, B_))), A_, 'test'),
    'demorgan': (bn(ba(A_, B_)), bx(bx(bn(A_), bn(B_)), ba(bn(A_), bn(B_))), 'test'),
    'not_xor': (bn(bx(A_, B_)), bx(bn(A_), B_), 'test'),
    'xor_cancel': (bx(A_, bx(A_, B_)), B_, 'test'),
    'and_xor_self': (ba(A_, bx(A_, B_)), bx(A_, ba(A_, B_)), 'test'),
    'not_not': (bn(bn(A_)), A_, 'test'),
}


def f1_render(e):
    t = e[0]
    if t == 'v': return e[1]
    if t == 'T': return 'true'
    if t == 'F': return 'false'
    if t == 'x': return f'(xor {f1_render(e[1])} {f1_render(e[2])})'
    if t == 'a': return f'({f1_render(e[1])} && {f1_render(e[2])})'
    if t == 'n': return f'(!{f1_render(e[1])})'
    if t == 'm': return e[1].lower()
    if t == 'hole': return 'z'
    raise ValueError(e)


def f1_toks(e):
    t = e[0]
    if t == 'v': return [e[1]]
    if t == 'T': return ['true']
    if t == 'F': return ['false']
    if t == 'm': return [e[1].lower()]
    if t == 'x': return ['(', 'xor'] + f1_toks(e[1]) + f1_toks(e[2]) + [')']
    if t == 'a': return ['('] + f1_toks(e[1]) + ['&&'] + f1_toks(e[2]) + [')']
    if t == 'n': return ['(', '!'] + f1_toks(e[1]) + [')']
    raise ValueError(e)


def f1_parse_expr(s):
    toks = tokenize(s)
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def nxt():
        nonlocal pos
        pos += 1
        return toks[pos - 1]

    def expr():
        t = nxt()
        if t == '(':
            if peek() == 'xor':
                nxt(); a = expr(); b = expr(); assert nxt() == ')'
                return ('x', a, b)
            if peek() == '!':
                nxt(); a = expr(); assert nxt() == ')'
                return ('n', a)
            a = expr(); assert nxt() == '&&'; b = expr(); assert nxt() == ')'
            return ('a', a, b)
        if t == 'true': return T_
        if t == 'false': return F_
        assert re.fullmatch(r'[a-g]|x\d+', t), t
        return ('v', t)
    e = expr()
    assert pos == len(toks), (s, pos)
    return e


def f1_eval(e, env):
    t = e[0]
    if t == 'v': return env[e[1]]
    if t == 'm': return env[e[1].lower()]
    if t == 'T': return True
    if t == 'F': return False
    if t == 'x': return f1_eval(e[1], env) != f1_eval(e[2], env)
    if t == 'a': return f1_eval(e[1], env) and f1_eval(e[2], env)
    if t == 'n': return not f1_eval(e[1], env)
    raise ValueError(e)


def f1_vars(e, acc=None):
    acc = set() if acc is None else acc
    if e[0] == 'v': acc.add(e[1])
    elif e[0] == 'm': acc.add(e[1].lower())
    elif e[0] not in ('T', 'F'):
        for c in e[1:]: f1_vars(c, acc)
    return acc


def f1_stmt(vs, l, r):
    return f'∀ {" ".join(vs)} : Bool, {f1_render(l)} = {f1_render(r)}'


def f1_parse_stmt(text):
    m = re.fullmatch(r'∀ ((?:(?:[a-g]|x\d+) )*(?:[a-g]|x\d+)) : Bool, (.+)', text)
    assert m, text
    l, r = split_top(m.group(2), ' = ')
    return {'vars': m.group(1).split(), 'lhs': f1_parse_expr(l), 'rhs': f1_parse_expr(r)}


def f1_reprint(p):
    return tokens_join(['∀'] + p['vars'] + [':', 'Bool', ','] + f1_toks(p['lhs']) + ['='] + f1_toks(p['rhs']))


def f1_truth(p):
    vs = p['vars']
    if not f1_vars(p['lhs']) | f1_vars(p['rhs']) <= set(vs):
        return False
    for bits in itertools.product((False, True), repeat=len(vs)):
        env = dict(zip(vs, bits))
        if f1_eval(p['lhs'], env) != f1_eval(p['rhs'], env):
            return False
    return True


def f1_lemma_stmt(name):
    lhs, rhs, _ = F1_RULES[name]
    ms = sorted(set(metas(lhs) + metas(rhs)))
    return f'∀ {" ".join(m.lower() for m in ms)} : Bool, {f1_render(lhs)} = {f1_render(rhs)}', ms


for _name, (_l, _r, _sp) in F1_RULES.items():
    _st, _ms = f1_lemma_stmt(_name)
    add_unit(f'f1_{_name}', 'F1', _sp if _sp == 'cal' else 'test_ref',
             f'theorem vadl_b_{_name} : {_st} := by decide')


def f1_sub_positions(e, path=()):
    yield path, e
    if e[0] in ('x', 'a', 'n'):
        for i, c in enumerate(e[1:], 1):
            yield from f1_sub_positions(c, path + (i,))


def f1_replace(e, path, new):
    if not path:
        return new
    i = path[0]
    return e[:i] + (f1_replace(e[i], path[1:], new),) + e[i + 1:]


def f1_rand(rng, pool, depth):
    if depth <= 0 or rng.random() < 0.12:
        r = rng.random()
        if r < 0.04: return T_
        if r < 0.08: return F_
        return ('v', rng.choice(pool))
    k = rng.random()
    if k < 0.15: return ('n', f1_rand(rng, pool, depth - 1))
    return ('x' if k < 0.6 else 'a', f1_rand(rng, pool, depth - 1), f1_rand(rng, pool, depth - 1))


def f1_rand_ctx(rng, pool, depth):
    """A context (expression with a single ('hole',)) of the given maximal depth."""
    if depth <= 0 or rng.random() < 0.2:
        return ('hole',)
    k = rng.random()
    if k < 0.15: return ('n', f1_rand_ctx(rng, pool, depth - 1))
    op = 'x' if k < 0.6 else 'a'
    if rng.random() < 0.5:
        return (op, f1_rand_ctx(rng, pool, depth - 1), f1_rand(rng, pool, 3))
    return (op, f1_rand(rng, pool, 3), f1_rand_ctx(rng, pool, depth - 1))


def f1_plug(ctx, term):
    if ctx[0] == 'hole': return term
    return (ctx[0],) + tuple(f1_plug(c, term) if isinstance(c, tuple) else c for c in ctx[1:])


def f1_ctx_at(e, path):
    if not path: return ('hole',)
    i = path[0]
    return e[:i] + (f1_ctx_at(e[i], path[1:]),) + e[i + 1:]


def f1_hole_path(ctx):
    if ctx[0] == 'hole':
        return ()
    for i, c in enumerate(ctx[1:], 1):
        if isinstance(c, tuple) and 'hole' in json.dumps(c):
            return (i,) + f1_hole_path(c)
    raise ValueError(ctx)


def f1_directions(name):
    lhs, rhs, _ = F1_RULES[name]
    yield False, lhs, rhs
    if rhs[0] != 'm':
        yield True, rhs, lhs


def f1_gen(seed, split):
    rules = [k for k, v in F1_RULES.items() if v[2] == split]
    for attempt in range(400):
        rng = rng_for('F1', split, seed, attempt)
        nv = rng.choice((5, 6, 7, 7))
        pool = list(VARS[:nv])
        steps_wanted = rng.choice((1, 2, 3))
        name = rng.choice(rules)
        rev, lhs, rhs = rng.choice(list(f1_directions(name)))
        allm = sorted(set(metas(F1_RULES[name][0]) + metas(F1_RULES[name][1])))
        sub = {m: f1_rand(rng, pool, rng.choice((3, 4, 5))) for m in allm}
        redex = subst(lhs, sub)
        ctx0 = f1_rand_ctx(rng, pool, rng.choice((3, 4, 5)))
        pth = f1_hole_path(ctx0)
        e0 = f1_plug(ctx0, redex)
        steps, cur = [], e0
        after = f1_replace(cur, pth, subst(rhs, sub))
        steps.append({'rule': name, 'rev': rev, 'path': list(pth), 'args': [sub[m] for m in allm],
                      'before': cur, 'after': after})
        cur = after
        while len(steps) < steps_wanted:
            cands = []
            for pth, sx in f1_sub_positions(cur):
                for nm in rules:
                    for rv, l, r in f1_directions(nm):
                        s2 = match(l, sx)
                        if s2 is not None and nm != steps[-1]['rule'] and set(metas(r)) <= set(metas(l)):
                            new = subst(r, s2)
                            if new != sx and size(f1_replace(cur, pth, new)) <= 450:
                                cands.append((nm, rv, pth, s2, new))
            if not cands:
                break
            nm, rv, pth, s2, new = cands[rng.randrange(len(cands))]
            mn = sorted(set(metas(F1_RULES[nm][0]) + metas(F1_RULES[nm][1])))
            nxt = f1_replace(cur, pth, new)
            steps.append({'rule': nm, 'rev': rv, 'path': list(pth), 'args': [s2[m] for m in mn if m in s2],
                          'before': cur, 'after': nxt})
            cur = nxt
        used = sorted(f1_vars(e0) | f1_vars(cur))
        if e0 == cur or not (4 <= len(used) <= 7) or size(e0) > 450 or size(cur) > 450:
            continue
        if len(used) != nv and attempt < 150:
            continue
        return {'family': 'F1', 'split': split, 'seed': seed, 'vars': used, 'lhs': e0, 'rhs': cur,
                'steps': steps, 'templates': sorted({s['rule'] for s in steps}), 'nvars': len(used)}
    raise RuntimeError(f'F1 generation failed for seed {seed}')


def f1_unit_name(rule):
    return f'vadl_b_{rule}'


def f1_build(spec, strat):
    nm = f"vad_t_F1_{spec['seed']}"
    vs = ' '.join(spec['vars'])
    stmt = f1_stmt(spec['vars'], spec['lhs'], spec['rhs'])
    if strat == 'S_decide':
        return f'theorem {nm} : {stmt} := by decide', nm
    lines = [f'theorem {nm} : {stmt} := by', f'  intro {vs}']
    for i, s in enumerate(spec['steps'], 1):
        ctx = f1_render(f1_ctx_at(s['before'], tuple(s['path'])))
        args = ' '.join(f1_render(a) for a in s['args'])
        lem = f"{f1_unit_name(s['rule'])} {args}"
        if s['rev']:
            lem = f'({lem}).symm'
        else:
            lem = f'({lem})'
        lines.append(f"  have h{i} : {f1_render(s['before'])} = {f1_render(s['after'])} := "
                     f'congrArg (fun z : Bool => {ctx}) {lem}')
    k = len(spec['steps'])
    chain = f'h{k}'
    for i in range(k - 1, 0, -1):
        chain = f'h{i}.trans ({chain})'
    lines.append(f'  exact {chain}')
    return '\n'.join(lines), nm


# ---------------------------------------------------------------------------
# Workspace: builds library units to .olean per toolchain and checks target files
# ---------------------------------------------------------------------------
class Workspace:
    def __init__(self, root, versions=None, workers=4):
        import vad_lean_runner as R
        self.R = R
        self.root = Path(root)
        self.versions = tuple(versions or R.VERSIONS)
        self.workers = workers
        self.src = self.root / 'src'
        self.src.mkdir(parents=True, exist_ok=True)
        self.unit_results = {}
        for v in self.versions:
            (self.root / 'cache' / v).mkdir(parents=True, exist_ok=True)

    def cache_dir(self, v):
        return self.root / 'cache' / v

    def _unit_job(self, name, v):
        u = LIB[name]
        text = unit_source(u)
        f = self.src / (u.module + '.lean')
        f.write_text(text, encoding='utf-8', newline='\n')
        return {'path': f, 'version': v, 'lean_path': self.cache_dir(v), 'targets': u.theorems,
                'olean_out': self.cache_dir(v) / (u.module + '.olean')}, sha(text)

    def build_units(self, names):
        """Build the closure of `names` (topological levels, <=4 parallel). Returns {(unit, ver): result}."""
        order = closure(names)
        depth = {}
        for n in order:
            depth[n] = 1 + max([depth[d] for d in unit_deps(LIB[n])] + [0])
        for lvl in sorted(set(depth.values())):
            jobs, keys = [], []
            for n in order:
                if depth[n] != lvl:
                    continue
                for v in self.versions:
                    if (n, v) in self.unit_results:
                        continue
                    meta = self.cache_dir(v) / (LIB[n].module + '.json')
                    job, h = self._unit_job(n, v)
                    if meta.exists():
                        rec = json.loads(meta.read_text(encoding='utf-8'))
                        if rec.get('sha') == h and job['olean_out'].exists() and rec['result']['ok']:
                            self.unit_results[(n, v)] = rec['result']
                            continue
                    jobs.append(job)
                    keys.append((n, v, h, meta))
            for (n, v, h, meta), res in zip(keys, self.R.run_many(jobs, self.workers)):
                res['unit'] = n
                if not res['ok']:
                    raise RuntimeError(f'library unit {n} failed under {v}: {res["stdout"]} {res["stderr"]}')
                meta.write_text(json.dumps({'sha': h, 'result': res}), encoding='utf-8')
                self.unit_results[(n, v)] = res
        return {k: v for k, v in self.unit_results.items() if k[0] in set(order)}

    def check(self, label, body, target, versions=None):
        """Check one generated target source under every toolchain; builds needed units first."""
        text = target_source(body, target)
        deps = imports_for(body)
        self.build_units(deps)
        f = self.src / f'{label}.lean'
        f.write_text(text, encoding='utf-8', newline='\n')
        jobs = [{'path': f, 'version': v, 'lean_path': self.cache_dir(v), 'targets': (target,)}
                for v in (versions or self.versions)]
        out = {}
        for j, r in zip(jobs, self.R.run_many(jobs, 1)):
            r['source_sha256'] = sha(text)
            r['imports'] = deps
            out[j['version']] = r
        return out

    def check_many(self, items, versions=None):
        """items: [(label, body, target)] -> {label: {version: result}} with <=workers parallel."""
        all_deps = sorted({d for _, b, _ in items for d in imports_for(b)})
        self.build_units(all_deps)
        jobs, keys = [], []
        for label, body, target in items:
            text = target_source(body, target)
            f = self.src / f'{label}.lean'
            f.write_text(text, encoding='utf-8', newline='\n')
            for v in (versions or self.versions):
                jobs.append({'path': f, 'version': v, 'lean_path': self.cache_dir(v), 'targets': (target,)})
                keys.append((label, v, sha(text), imports_for(body)))
        out = defaultdict(dict)
        for (label, v, h, deps), r in zip(keys, self.R.run_many(jobs, self.workers)):
            r['source_sha256'] = h
            r['imports'] = deps
            out[label][v] = r
        return dict(out)


# ---------------------------------------------------------------------------
# F2  Modular arithmetic over Nat
# ---------------------------------------------------------------------------
NV = V('n')


def c_(k): return ('c', k)
def padd(a, b): return ('+', a, b)
def pmul(a, b): return ('*', a, b)
def ppow(a, k): return ('^', a, k)


F2_MODULI = {'cal': (3, 4, 6, 8, 10, 12), 'test': (5, 7, 9, 11)}


def poly_render(e):
    t = e[0]
    if t == 'v': return e[1]
    if t == 'm': return e[1].lower()
    if t == 'c': return str(e[1])
    if t == '+': return f'({poly_render(e[1])} + {poly_render(e[2])})'
    if t == '*': return f'({poly_render(e[1])} * {poly_render(e[2])})'
    if t == '^': return f'({poly_render(e[1])} ^ {e[2]})'
    if t == '%': return f'({poly_render(e[1])} % {e[2]})'
    raise ValueError(e)


def poly_toks(e):
    t = e[0]
    if t == 'v': return [e[1]]
    if t == 'm': return [e[1].lower()]
    if t == 'c': return [str(e[1])]
    if t in '+*': return ['('] + poly_toks(e[1]) + [t] + poly_toks(e[2]) + [')']
    if t == '^': return ['('] + poly_toks(e[1]) + ['^', str(e[2]), ')']
    if t == '%': return ['('] + poly_toks(e[1]) + ['%', str(e[2]), ')']
    raise ValueError(e)


def poly_parse(s):
    toks = tokenize(s)
    pos = 0

    def nxt():
        nonlocal pos
        pos += 1
        return toks[pos - 1]

    def expr():
        t = nxt()
        if t == '(':
            a = expr()
            op = nxt()
            if op in ('+', '*'):
                b = expr()
                assert nxt() == ')'
                return (op, a, b)
            assert op == '^'
            k = int(nxt())
            assert nxt() == ')'
            return ('^', a, k)
        if re.fullmatch(r'\d+', t): return ('c', int(t))
        assert re.fullmatch(r"[A-Za-z_][A-Za-z0-9_']*", t), t
        return ('v', t)
    e = expr()
    assert pos == len(toks), s
    return e


def poly_eval(e, env):
    t = e[0]
    if t == 'v': return env[e[1]]
    if t == 'c': return e[1]
    if t == '+': return poly_eval(e[1], env) + poly_eval(e[2], env)
    if t == '*': return poly_eval(e[1], env) * poly_eval(e[2], env)
    if t == '^': return poly_eval(e[1], env) ** e[2]
    if t == '%': return poly_eval(e[1], env) % e[2]
    raise ValueError(e)


def poly_vars(e, acc=None):
    acc = [] if acc is None else acc
    if e[0] == 'v':
        if e[1] not in acc: acc.append(e[1])
    elif e[0] in '+*^%':
        poly_vars(e[1], acc)
        if e[0] in '+*': poly_vars(e[2], acc)
    return acc


def poly_deg(e):
    t = e[0]
    if t == 'v': return 1
    if t == 'c': return 0
    if t == '+': return max(poly_deg(e[1]), poly_deg(e[2]))
    if t == '*': return poly_deg(e[1]) + poly_deg(e[2])
    if t == '^': return poly_deg(e[1]) * e[2]
    raise ValueError(e)


def poly_sub(e, mp):
    """Substitute variables by ASTs."""
    if e[0] == 'v': return mp.get(e[1], e)
    if e[0] in ('c', 'm'): return e
    if e[0] in '+*': return (e[0], poly_sub(e[1], mp), poly_sub(e[2], mp))
    return (e[0], poly_sub(e[1], mp), e[2])


def f2_stmt(vs, lhs, m, rhs):
    r = str(rhs[1]) if rhs[0] == 'const' else f'{poly_render(rhs[1])} % {m}'
    return f'∀ {" ".join(vs)} : Nat, {poly_render(lhs)} % {m} = {r}'


def f2_parse_stmt(text):
    mt = re.fullmatch(r'∀ ((?:[A-Za-z_][A-Za-z0-9_\']* )*[A-Za-z_][A-Za-z0-9_\']*) : Nat, (.+)', text)
    assert mt, text
    l, r = split_top(mt.group(2), ' = ')
    lp, lm = l.rsplit(' % ', 1)
    if re.fullmatch(r'\d+', r):
        rhs = ('const', int(r))
    else:
        rp, rm = r.rsplit(' % ', 1)
        assert int(rm) == int(lm)
        rhs = ('mod', poly_parse(rp))
    return {'vars': mt.group(1).split(), 'lhs': poly_parse(lp), 'm': int(lm), 'rhs': rhs}


def f2_reprint(p):
    toks = ['∀'] + p['vars'] + [':', 'Nat', ','] + _plain(poly_toks(p['lhs'])) + ['%', str(p['m']), '=']
    if p['rhs'][0] == 'const':
        toks.append(str(p['rhs'][1]))
    else:
        toks += _plain(poly_toks(p['rhs'][1])) + ['%', str(p['m'])]
    return tokens_join(toks)


def _plain(toks):
    return toks


def f2_truth(p):
    m, vs = p['m'], p['vars']
    if not set(poly_vars(p['lhs'])) | (set(poly_vars(p['rhs'][1])) if p['rhs'][0] == 'mod' else set()) <= set(vs):
        return False
    for vals in itertools.product(range(2 * m + 1), repeat=len(vs)):
        env = dict(zip(vs, vals))
        lhs = poly_eval(p['lhs'], env) % m
        rhs = p['rhs'][1] if p['rhs'][0] == 'const' else poly_eval(p['rhs'][1], env) % m
        if lhs != rhs:
            return False
    return True


def f2_red_term(e, m, v_mod):
    """Proof term for `e % m = e[v := v % m] % m` assembled from the modeq lemmas."""
    t = e[0]
    if t == 'v': return f'(Nat.mod_mod {e[1]} {m}).symm'
    if t == 'c': return 'rfl'
    if t == '+': return f'(vadl_modeq_add {f2_red_term(e[1], m, v_mod)} {f2_red_term(e[2], m, v_mod)})'
    if t == '*': return f'(vadl_modeq_mul {f2_red_term(e[1], m, v_mod)} {f2_red_term(e[2], m, v_mod)})'
    if t == '^': return f'(vadl_modeq_pow {e[2]} {f2_red_term(e[1], m, v_mod)})'
    raise ValueError(e)


def f2_decide_body(name, vs, lhs, m, rhs):
    """S_decide: structural reduction to residues + `decide` over all residues."""
    ks = {v: ('v', f'k_{v}') for v in vs}
    ms = {v: ('%', ('v', v), m) for v in vs}
    kb = ' '.join(f'∀ k_{v} : Nat, k_{v} < {m} →' for v in vs)
    rk = str(rhs[1]) if rhs[0] == 'const' else f'{poly_render(poly_sub(rhs[1], ks))} % {m}'
    lines = [f'theorem {name} : {f2_stmt(vs, lhs, m, rhs)} := by', f'  intro {" ".join(vs)}',
             f'  have key : {kb} {poly_render(poly_sub(lhs, ks))} % {m} = {rk} := by decide',
             f'  have red : {poly_render(lhs)} % {m} = {poly_render(poly_sub(lhs, ms))} % {m} := {f2_red_term(lhs, m, None)}']
    kargs = ' '.join(f'({v} % {m}) (Nat.mod_lt {v} (by decide))' for v in vs)
    if rhs[0] == 'const':
        lines.append(f'  exact red.trans (key {kargs})')
    else:
        lines.append(f'  have redq : {poly_render(rhs[1])} % {m} = {poly_render(poly_sub(rhs[1], ms))} % {m} := {f2_red_term(rhs[1], m, None)}')
        lines.append(f'  exact red.trans ((key {kargs}).trans redq.symm)')
    return '\n'.join(lines)


add_unit('f2_modeq', 'F2', 'base', '''
theorem vadl_modeq_add {m a b c d : Nat} (h1 : a % m = b % m) (h2 : c % m = d % m) : (a + c) % m = (b + d) % m := by
  rw [Nat.add_mod a c m, h1, h2, ← Nat.add_mod]
theorem vadl_modeq_mul {m a b c d : Nat} (h1 : a % m = b % m) (h2 : c % m = d % m) : (a * c) % m = (b * d) % m := by
  rw [Nat.mul_mod a c m, h1, h2, ← Nat.mul_mod]
theorem vadl_modeq_pow {m a b : Nat} (k : Nat) (h : a % m = b % m) : (a ^ k) % m = (b ^ k) % m := by
  induction k with
  | zero => rfl
  | succ k ih => rw [Nat.pow_succ, Nat.pow_succ]; exact vadl_modeq_mul ih h''')
add_unit('f2_comp', 'F2', 'base', '''
theorem vadl_mod_comp (a c d m q : Nat) (h : a % d = 0) (hm : (c * d) % m = 0) : (c * a + m * q) % m = 0 := by
  have h1 : d ∣ a := Nat.dvd_of_mod_eq_zero h
  have h2 : m ∣ c * d := Nat.dvd_of_mod_eq_zero hm
  have h3 : m ∣ c * a := Nat.dvd_trans h2 (Nat.mul_dvd_mul_left c h1)
  have h4 : m ∣ c * a + m * q := Nat.dvd_add h3 (Nat.dvd_mul_right m q)
  exact Nat.mod_eq_zero_of_dvd h4''')
add_unit('f2_lin', 'F2', 'test_ref', '''
theorem vadl_lin_pow (m r d n : Nat) : ((m * n + r) ^ d) % m = (r ^ d) % m :=
  vadl_modeq_pow d (Nat.mul_add_mod m n r)''')
add_unit('f2_mulzero', 'F2', 'test_ref', '''
theorem vadl_mulzero (m q b : Nat) : (m * q * b) % m = 0 := by
  rw [Nat.mul_assoc]; exact Nat.mul_mod_right m (q * b)
theorem vadl_mulzero_r (m q b : Nat) : (b * (m * q)) % m = 0 := by
  rw [Nat.mul_comm b]; exact vadl_mulzero m q b''')
add_unit('f2_shift', 'F2', 'test_ref', '''
theorem vadl_shift_pow (m k d n : Nat) : ((n + k * m) ^ d) % m = (n ^ d) % m :=
  vadl_modeq_pow d (Nat.add_mul_mod_self_right n k m)''')

# base polynomials B with B(n) % F = 0 (verified again by Python and by the kernel)
F2_BASES = {
    'consec2': (pmul(NV, padd(NV, c_(1))), 2, 'cal'),
    'consec3': (pmul(pmul(NV, padd(NV, c_(1))), padd(NV, c_(2))), 6, 'cal'),
    'consec4': (pmul(pmul(pmul(NV, padd(NV, c_(1))), padd(NV, c_(2))), padd(NV, c_(3))), 24, 'cal'),
    'cubic5': (padd(ppow(NV, 3), pmul(c_(5), NV)), 6, 'cal'),
    'quartic11': (padd(ppow(NV, 4), pmul(c_(11), ppow(NV, 2))), 12, 'cal'),
    'cubic2': (padd(ppow(NV, 3), pmul(c_(2), NV)), 3, 'test'),
    'shiftprod': (pmul(pmul(pmul(padd(NV, c_(1)), padd(NV, c_(1))), NV), padd(NV, c_(2))), 12, 'test'),
}
for _k, (_b, _F, _sp) in F2_BASES.items():
    add_unit(f'f2_base_{_k}', 'F2', _sp if _sp == 'cal' else 'test_ref',
             f2_decide_body(f'vadl_base_{_k}', ['n'], _b, _F, ('const', 0)))
F2_TEMPLATES = {'cal': ('consec2', 'consec3', 'consec4', 'cubic5', 'quartic11'),
                'test': ('cubic2', 'shiftprod', 'lin', 'mulzero_l', 'mulzero_r', 'shiftpow')}


def f2_rand_poly(rng, maxdeg, mindeg=0):
    for _ in range(50):
        terms = []
        for _ in range(rng.choice((1, 2, 3))):
            j, co = rng.randint(0, maxdeg), rng.randint(1, 5)
            x = c_(co) if j == 0 else pmul(c_(co), NV if j == 1 else ppow(NV, j))
            terms.append(x)
        e = terms[0]
        for x in terms[1:]:
            e = padd(e, x)
        if mindeg <= poly_deg(e) <= maxdeg:
            return e
    return NV


def f2_gen(seed, split):
    rng = rng_for('F2', split, seed)
    kind = rng.choice(F2_TEMPLATES[split])
    m = rng.choice(F2_MODULI[split])
    if kind in F2_BASES:
        B, F, _ = F2_BASES[kind]
        cs = [c for c in range(1, 13) if (c * F) % m == 0]
        c = rng.choice(cs)
        Q = f2_rand_poly(rng, poly_deg(B))
        lhs, rhs, par = padd(pmul(c_(c), B), pmul(c_(m), Q)), ('const', 0), {'base': kind, 'c': c, 'F': F, 'q': Q}
    elif kind == 'lin':
        d = rng.randint(2, 4)
        r = rng.randint(1, m - 1)
        inner = f2_rand_poly(rng, 4 // d, 1)
        lhs, rhs, par = ppow(padd(pmul(c_(m), inner), c_(r)), d), ('const', (r ** d) % m), {'r': r, 'd': d, 'inner': inner}
    elif kind in ('mulzero_l', 'mulzero_r'):
        Q, R = f2_rand_poly(rng, 2, 1), f2_rand_poly(rng, 2, 1)
        mq = pmul(c_(m), Q)
        lhs, rhs, par = (pmul(mq, R) if kind == 'mulzero_l' else pmul(R, mq)), ('const', 0), {'q': Q, 'r': R}
    else:
        k, d = rng.randint(1, 9), rng.randint(2, 4)
        inner = f2_rand_poly(rng, 4 // d, 1)
        lhs, rhs, par = ppow(padd(inner, pmul(c_(k), c_(m))), d), ('mod', ppow(inner, d)), {'k': k, 'd': d, 'inner': inner}
    return {'family': 'F2', 'split': split, 'seed': seed, 'kind': kind, 'm': m, 'vars': ['n'], 'lhs': lhs,
            'rhs': rhs, 'params': par, 'templates': [kind], 'moduli': [m], 'degree': poly_deg(lhs)}


def f2_build(spec, strat):
    nm = f"vad_t_F2_{spec['seed']}"
    vs, lhs, m, rhs = spec['vars'], spec['lhs'], spec['m'], spec['rhs']
    if strat == 'S_decide':
        return f2_decide_body(nm, vs, lhs, m, rhs), nm
    k, p, stmt = spec['kind'], spec['params'], f2_stmt(vs, lhs, m, rhs)
    if k in F2_BASES:
        term = f"fun n => vadl_mod_comp {poly_render(F2_BASES[k][0])} {p['c']} {p['F']} {m} {poly_render(p['q'])} (vadl_base_{k} n) (by decide)"
    elif k == 'lin':
        term = f"fun n => (vadl_lin_pow {m} {p['r']} {p['d']} {poly_render(p['inner'])}).trans (by decide)"
    elif k == 'mulzero_l':
        term = f"fun n => vadl_mulzero {m} {poly_render(p['q'])} {poly_render(p['r'])}"
    elif k == 'mulzero_r':
        term = f"fun n => vadl_mulzero_r {m} {poly_render(p['q'])} {poly_render(p['r'])}"
    else:
        term = f"fun n => vadl_shift_pow {m} {p['k']} {p['d']} {poly_render(p['inner'])}"
    return f'theorem {nm} : {stmt} :=\n  {term}', nm


# ---------------------------------------------------------------------------
# dispatch
# ---------------------------------------------------------------------------
def gen(fam, seed, split):
    return globals()[f'{fam.lower()}_gen'](seed, split)


def build(spec, strat):
    return globals()[f"{spec['family'].lower()}_build"](spec, strat)


# ---------------------------------------------------------------------------
# F5  monotone product/sum inequalities over Nat
# ---------------------------------------------------------------------------
def _xv(i): return ('v', f'x{i}')


def f5_prime(e, primed):
    """Meta/var AST -> variable AST; primed variables get a `y` name (x3 -> y3) or a prime (metas)."""
    t = e[0]
    if t == 'm':
        return ('v', e[1].lower() + ("'" if primed else ''))
    if t == 'v':
        return ('v', 'y' + e[1][1:]) if primed else e
    if t == 'c':
        return e
    return (t, f5_prime(e[1], primed), f5_prime(e[2], primed))


def f5_stmt_text(k, expr):
    binders = ' '.join(f'x{i} y{i}' for i in range(1, k + 1))
    hyps = ' → '.join(f'x{i} ≤ y{i}' for i in range(1, k + 1))
    return f'∀ {binders} : Nat, {hyps} → {poly_render(expr)} ≤ {poly_render(f5_prime(expr, True))}'


def f5_parse_stmt(text):
    mt = re.fullmatch(r'∀ ((?:[xy]\d+ )*[xy]\d+) : Nat, (.+)', text)
    assert mt, text
    parts, rest, depth, cur = [], mt.group(2), 0, ''
    i = 0
    while i < len(rest):
        if rest.startswith(' → ', i) and depth == 0:
            parts.append(cur)
            cur = ''
            i += 3
            continue
        depth += (rest[i] == '(') - (rest[i] == ')')
        cur += rest[i]
        i += 1
    goal = cur
    l, r = split_top(goal, ' ≤ ')
    hyps = [tuple(h.split(' ≤ ')) for h in parts]
    return {'binders': mt.group(1).split(), 'hyps': hyps, 'lhs': poly_parse(l), 'rhs': poly_parse(r)}


def f5_reprint(p):
    toks = ['∀'] + p['binders'] + [':', 'Nat', ',']
    for a, b in p['hyps']:
        toks += [a, '≤', b, '→']
    toks += poly_toks(p['lhs']) + ['≤'] + poly_toks(p['rhs'])
    return tokens_join(toks)


def f5_truth(p):
    """x_i <= y_i over {0,1,2}^2 for every hypothesis pair; the goal must hold on all of them."""
    xs = [a for a, _ in p['hyps']]
    ys = [b for _, b in p['hyps']]
    if sorted(p['binders']) != sorted(xs + ys):
        return False
    pairs = [(a, b) for a in range(3) for b in range(a, 3)]
    for combo in itertools.product(pairs, repeat=len(xs)):
        env = {}
        for x, y, (a, b) in zip(xs, ys, combo):
            env[x], env[y] = a, b
        if poly_eval(p['lhs'], env) > poly_eval(p['rhs'], env):
            return False
    return True


def f5_term(e, hyp):
    """S_direct: explicit Nat.add_le_add / Nat.mul_le_mul term."""
    t = e[0]
    if t == 'v': return hyp[e[1]]
    if t == '+': return f'(Nat.add_le_add {f5_term(e[1], hyp)} {f5_term(e[2], hyp)})'
    if t == '*': return f'(Nat.mul_le_mul {f5_term(e[1], hyp)} {f5_term(e[2], hyp)})'
    raise ValueError(e)


def f5_shape_stmt(pat):
    ms = metas(pat)
    binders = ' '.join(f'{m.lower()} {m.lower()}\'' for m in ms)
    hyps = ' → '.join(f'{m.lower()} ≤ {m.lower()}\'' for m in ms)
    return f'∀ {binders} : Nat, {hyps} → {poly_render(f5_prime(pat, False))} ≤ {poly_render(f5_prime(pat, True))}', ms


F5_SHAPES = {}     # static library shapes: unit short name -> (pattern, tier)
F5_INVENTED = {}   # invented shapes (never used unless passed explicitly)


def f5_register_shape(name, pat, tier, origin=()):
    st, ms = f5_shape_stmt(pat)
    hyp = {m.lower(): f'h{i}' for i, m in enumerate(ms)}
    term = f5_term(f5_prime(pat, False), hyp)
    intro = ' '.join(f"{m.lower()} {m.lower()}'" for m in ms) + ' ' + ' '.join(f'h{i}' for i in range(len(ms)))
    add_unit(f'f5_{name}', 'F5', tier, f'theorem vadl_f5_{name} : {st} := by\n  intro {intro}\n  exact {term}', origin)
    (F5_INVENTED if tier == 'invented' else F5_SHAPES)[name] = (pat, tier)


def _P(*names):
    e = M(names[0])
    for n in names[1:]:
        e = pmul(e, M(n))
    return e


f5_register_shape('prod2', _P('A', 'B'), 'cal')
f5_register_shape('prod3', _P('A', 'B', 'C'), 'cal')
f5_register_shape('prod4', _P('A', 'B', 'C', 'D'), 'cal')
f5_register_shape('prod5', _P('A', 'B', 'C', 'D', 'E'), 'cal')
f5_register_shape('sp2', padd(_P('A', 'B'), _P('C', 'D')), 'cal')
f5_register_shape('sp3', padd(_P('A', 'B', 'C'), _P('D', 'E', 'F')), 'cal')
f5_register_shape('sq', pmul(padd(M('A'), M('B')), padd(M('A'), M('B'))), 'test_ref')
f5_register_shape('sumfac', pmul(padd(M('A'), M('B')), padd(M('C'), M('D'))), 'test_ref')
f5_register_shape('sumfac3', pmul(pmul(padd(M('A'), M('B')), padd(M('C'), M('D'))), padd(M('E'), M('F'))), 'test_ref')
f5_register_shape('horner', pmul(M('A'), padd(M('B'), pmul(M('C'), M('D')))), 'test_ref')

F5_TEMPLATES = {'cal': ('prod', 'sumprod', 'sumprod_lin'), 'test': ('sq', 'sumfac', 'sumfac3', 'horner')}


def _fold(op, xs):
    e = xs[0]
    for x in xs[1:]:
        e = (op, e, x)
    return e


def _f5_relabel(e, used):
    mp = {u: f'x{i}' for i, u in enumerate(sorted(used), 1)}
    return poly_sub(e, {u: ('v', v) for u, v in mp.items()})


def f5_gen(seed, split):
    for attempt in range(300):
        rng = rng_for('F5', split, seed, attempt)
        kind = rng.choice(F5_TEMPLATES[split])
        pool = [_xv(i) for i in range(1, 6)]
        pick = lambda: rng.choice(pool[:rng.randint(2, 5)])
        term = lambda: pick() if rng.random() < 0.6 else pmul(pick(), pick())
        if kind == 'prod':
            e = _fold('*', [pick() for _ in range(rng.randint(3, 5))])
        elif kind in ('sumprod', 'sumprod_lin'):
            mons = [_fold('*', [pick() for _ in range(rng.randint(2, 3))]) for _ in range(rng.randint(2, 4))]
            if kind == 'sumprod_lin':
                mons.append(pick())
            e = _fold('+', mons)
        elif kind == 'sq':
            inner = _fold('+', [term() for _ in range(rng.randint(2, 3))])
            e = pmul(inner, inner)
        elif kind == 'sumfac':
            e = pmul(_fold('+', [term() for _ in range(2)]), _fold('+', [term() for _ in range(rng.randint(2, 3))]))
        elif kind == 'sumfac3':
            e = pmul(pmul(padd(pick(), pick()), padd(pick(), pick())), padd(pick(), pick()))
        else:
            x = [pick() for _ in range(5)]
            e = pmul(x[0], padd(x[1], pmul(x[2], padd(x[3], x[4]) if rng.random() < 0.5 else x[3])))
        used = set(poly_vars(e))
        if not (2 <= len(used) <= 5) or not (5 <= size(e) <= 70):
            continue
        e = _f5_relabel(e, used)
        k = len(used)
        return {'family': 'F5', 'split': split, 'seed': seed, 'kind': kind, 'k': k, 'expr': e,
                'templates': [kind], 'vars': [f'x{i}' for i in range(1, k + 1)]}
    raise RuntimeError('F5 generation failed')


def f5_lemma_term(e, hyp, shape_names=None):
    """S_lemma: largest library shape that matches at each node; core lemmas as the fallback."""
    t = e[0]
    if t == 'v':
        return hyp[e[1]]
    allshapes = {**F5_SHAPES, **F5_INVENTED}
    names = shape_names if shape_names is not None else sorted(F5_SHAPES, key=lambda n: (-size(F5_SHAPES[n][0]), n))
    for n in names:
        pat = allshapes[n][0]
        sub = match(pat, e)
        if sub is not None:
            ms = metas(pat)
            args = ' '.join(f5_lemma_term(sub[m], hyp, shape_names) for m in ms)
            return f'(vadl_f5_{n} {" ".join(["_"] * (2 * len(ms)))} {args})'
    head = 'Nat.add_le_add' if t == '+' else 'Nat.mul_le_mul'
    return f'({head} {f5_lemma_term(e[1], hyp, shape_names)} {f5_lemma_term(e[2], hyp, shape_names)})'


def f5_mul_atoms(e):
    """Maximal product nodes under the top-level sum tree (atoms for omega)."""
    if e[0] == '*':
        return [e]
    if e[0] == '+':
        return f5_mul_atoms(e[1]) + f5_mul_atoms(e[2])
    return []


def f5_build(spec, strat):
    nm = f"vad_t_F5_{spec['seed']}"
    k, e = spec['k'], spec['expr']
    hyp = {f'x{i}': f'h{i}' for i in range(1, k + 1)}
    stmt = f5_stmt_text(k, e)
    intro = ' '.join(f'x{i} y{i}' for i in range(1, k + 1)) + ' ' + ' '.join(f'h{i}' for i in range(1, k + 1))
    hyp_y = {f'x{i}': f'h{i}' for i in range(1, k + 1)}
    if strat == 'S_direct':
        return f'theorem {nm} : {stmt} := by\n  intro {intro}\n  exact {f5_term(e, hyp)}', nm
    if strat == 'S_lemma':
        return f'theorem {nm} : {stmt} := by\n  intro {intro}\n  exact {f5_lemma_term(e, hyp)}', nm
    lines = [f'theorem {nm} : {stmt} := by', f'  intro {intro}']
    for i, a in enumerate(f5_mul_atoms(e), 1):
        lines.append(f'  have p{i} : {poly_render(a)} ≤ {poly_render(f5_prime(a, True))} := {f5_term(a, hyp)}')
    lines.append('  omega')
    return '\n'.join(lines), nm


# ---------------------------------------------------------------------------
# F3  finite algebra on Fin m
# ---------------------------------------------------------------------------
F3_OPS = {'cal': ('add', 'muladd', 'shift1', 'shift2', 'shift3', 'shift4'), 'test': ('mul', 'dbl', 'conj2', 'conj3', 'conj4', 'conj5')}
F3_M = {'cal': (3, 4, 5), 'test': (6, 7)}
F3_LAWS = ('assoc', 'comm', 'medial', 'lid', 'inv')


def f3_pyop(key, m):
    mt = re.fullmatch(r'(add|muladd|mul|dbl|shift|conj)(\d*)', key)
    base, K = mt.group(1), (int(mt.group(2)) if mt.group(2) else None)
    if base == 'add': f = lambda a, b: (a + b) % m
    elif base == 'muladd': f = lambda a, b: (a * b + a + b) % m
    elif base == 'mul': f = lambda a, b: (a * b) % m
    elif base == 'dbl': f = lambda a, b: (a + b + 2 * a * b) % m
    elif base == 'shift': f = lambda a, b: (a + b + K) % m
    else: f = lambda a, b: (a * b + K * a + K * b + K * K - K) % m
    return [[f(a, b) for b in range(m)] for a in range(m)]


def f3_lean_body(key):
    mt = re.fullmatch(r'(add|muladd|mul|dbl|shift|conj)(\d*)', key)
    base, K = mt.group(1), mt.group(2)
    return {'add': 'a + b', 'muladd': 'a * b + a + b', 'mul': 'a * b', 'dbl': 'a + b + 2 * a * b',
            'shift': f'a + b + {K}', 'conj': f'a * b + {K} * a + {K} * b + {int(K) * int(K) - int(K)}' if K else ''}[base]


def f3_law_true(T, m, law, e=None):
    r = range(m)
    if law == 'assoc': return all(T[T[a][b]][c] == T[a][T[b][c]] for a in r for b in r for c in r)
    if law == 'comm': return all(T[a][b] == T[b][a] for a in r for b in r)
    if law == 'medial': return all(T[T[a][b]][T[c][d]] == T[T[a][c]][T[b][d]] for a in r for b in r for c in r for d in r)
    if law == 'lid': return e is not None and all(T[e][a] == a for a in r)
    if law == 'inv': return e is not None and all(any(T[a][b] == e for b in r) for a in r)
    raise ValueError(law)


def f3_identity(T, m):
    for e in range(m):
        if all(T[e][a] == a for a in range(m)):
            return e
    return None


def f3_law_stmt(op, m, law, e=None):
    F = f'Fin {m}'
    if law == 'assoc': return f'∀ a b c : {F}, {op} ({op} a b) c = {op} a ({op} b c)'
    if law == 'comm': return f'∀ a b : {F}, {op} a b = {op} b a'
    if law == 'medial': return f'∀ a b c d : {F}, {op} ({op} a b) ({op} c d) = {op} ({op} a c) ({op} b d)'
    if law == 'lid': return f'∀ a : {F}, {op} ({e} : {F}) a = a'
    return f'∀ a : {F}, ∃ b : Nat, b < {m} ∧ {op} a (vad_fin {m} b) = ({e} : {F})'


def f3_true_laws(T, m):
    e = f3_identity(T, m)
    return [(l, e) for l in F3_LAWS if f3_law_true(T, m, l, e)]


def f3_op_name(key, m):
    return f'vad_f3_{key}_{m}'


F3_BASE_LAWS = {}
for _sp in ('cal', 'test'):
    for _key in F3_OPS[_sp]:
        for _m in F3_M[_sp]:
            if (mt := re.fullmatch(r'(?:shift|conj)(\d+)', _key)) and int(mt.group(1)) >= _m:
                continue
            _T = f3_pyop(_key, _m)
            _laws = f3_true_laws(_T, _m)
            F3_BASE_LAWS[(_key, _m)] = (_laws, _sp)
            _op = f3_op_name(_key, _m)
            _body = f'def {_op} (a b : Fin {_m}) : Fin {_m} := {f3_lean_body(_key)}\n'
            for _l, _e in _laws:
                _body += f'theorem vadl_f3_{_key}_{_m}_{_l} : {f3_law_stmt(_op, _m, _l, _e)} := by decide\n'
            add_unit(f'f3_{_key}_{_m}', 'F3', _sp if _sp == 'cal' else 'test_ref', _body)

add_unit('f3_hom', 'F3', 'base', '''
theorem vad_hom_assoc {α : Type} (f g : α → α) (B op : α → α → α) (hfg : ∀ y, f (g y) = y)
    (hB : ∀ a b c, B (B a b) c = B a (B b c)) (hop : ∀ a b, op a b = g (B (f a) (f b))) :
    ∀ a b c, op (op a b) c = op a (op b c) := by
  intro a b c
  rw [hop (op a b) c, hop a b, hop b c, hop a (g (B (f b) (f c))), hfg, hfg, hB]
theorem vad_hom_comm {α : Type} (f g : α → α) (B op : α → α → α)
    (hB : ∀ a b, B a b = B b a) (hop : ∀ a b, op a b = g (B (f a) (f b))) :
    ∀ a b, op a b = op b a := by
  intro a b
  rw [hop a b, hop b a, hB]
theorem vad_hom_medial {α : Type} (f g : α → α) (B op : α → α → α) (hfg : ∀ y, f (g y) = y)
    (hB : ∀ a b c d, B (B a b) (B c d) = B (B a c) (B b d)) (hop : ∀ a b, op a b = g (B (f a) (f b))) :
    ∀ a b c d, op (op a b) (op c d) = op (op a c) (op b d) := by
  intro a b c d
  have e : ∀ x y, f (op x y) = B (f x) (f y) := fun x y => by rw [hop, hfg]
  rw [hop (op a b) (op c d), hop (op a c) (op b d)]
  simp only [e]
  rw [hB]
theorem vad_hom_lid {α : Type} (f g : α → α) (B op : α → α → α) (e0 e1 : α) (hgf : ∀ x, g (f x) = x)
    (hfg : ∀ y, f (g y) = y) (hB : ∀ a, B e0 a = a) (he : g e0 = e1)
    (hop : ∀ a b, op a b = g (B (f a) (f b))) : ∀ a, op e1 a = a := by
  intro a
  rw [← he, hop, hfg, hB, hgf]
def vad_fin (m : Nat) [NeZero m] (b : Nat) : Fin m := ⟨b % m, Nat.mod_lt _ (Nat.pos_of_ne_zero (NeZero.ne m))⟩
theorem vad_fin_val {m : Nat} [NeZero m] (x : Fin m) : vad_fin m x.val = x := Fin.ext (Nat.mod_eq_of_lt x.isLt)
theorem vad_hom_inv {m : Nat} [NeZero m] (f g : Fin m → Fin m) (B op : Fin m → Fin m → Fin m) (e0 e1 : Fin m)
    (hfg : ∀ y, f (g y) = y) (hB : ∀ a : Fin m, ∃ b : Nat, b < m ∧ B a (vad_fin m b) = e0) (he : g e0 = e1)
    (hop : ∀ a b, op a b = g (B (f a) (f b))) : ∀ a : Fin m, ∃ b : Nat, b < m ∧ op a (vad_fin m b) = e1 := by
  intro a
  obtain ⟨b, hb, h⟩ := hB (f a)
  refine ⟨(g (vad_fin m b)).val, (g (vad_fin m b)).isLt, ?_⟩
  rw [vad_fin_val, hop, hfg, h, he]''')


def f3_table_def(name, m, tbl):
    flat = ','.join(str(x) for row in tbl for x in row)
    return f'def {name} (a b : Fin {m}) : Fin {m} := ⟨[{flat}].getD (a.val * {m} + b.val) 0 % {m}, Nat.mod_lt _ (by decide)⟩'


def f3_perm_def(name, m, lst):
    return f'def {name} (a : Fin {m}) : Fin {m} := ⟨[{",".join(str(x) for x in lst)}].getD a.val 0 % {m}, Nat.mod_lt _ (by decide)⟩'


def f3_gen(seed, split):
    rng = rng_for('F3', split, seed)
    while True:
        key, m = rng.choice(F3_OPS[split]), rng.choice(F3_M[split])
        if (key, m) in F3_BASE_LAWS:
            break
    laws, _ = F3_BASE_LAWS[(key, m)]
    law, e0 = laws[rng.randrange(len(laws))]
    base = f3_pyop(key, m)
    if rng.random() < 1 / 3:
        perm = None
        tbl, e1 = None, e0
    else:
        f = list(range(m))
        while f == list(range(m)):
            rng.shuffle(f)
        g = [f.index(i) for i in range(m)]
        perm = f
        tbl = [[g[base[f[a]][f[b]]] for b in range(m)] for a in range(m)]
        e1 = g[e0] if e0 is not None else None
    return {'family': 'F3', 'split': split, 'seed': seed, 'key': key, 'm': m, 'law': law, 'e0': e0, 'e': e1,
            'perm': perm, 'table': tbl, 'templates': [key], 'size': m}


def f3_render(spec):
    m, key = spec['m'], spec['key']
    op = 'vad_op' if spec['table'] is not None else f3_op_name(key, m)
    defs = f3_table_def('vad_op', m, spec['table']) if spec['table'] is not None else ''
    return {'defs': defs, 'stmt': f3_law_stmt(op, m, spec['law'], spec['e'] if spec['law'] in ('lid', 'inv') else None)}


_F3_STMT = [
    ('assoc', r'∀ a b c : Fin (\d+), (\S+) \(\2 a b\) c = \2 a \(\2 b c\)'),
    ('comm', r'∀ a b : Fin (\d+), (\S+) a b = \2 b a'),
    ('medial', r'∀ a b c d : Fin (\d+), (\S+) \(\2 a b\) \(\2 c d\) = \2 \(\2 a c\) \(\2 b d\)'),
    ('lid', r'∀ a : Fin (\d+), (\S+) \((\d+) : Fin \1\) a = a'),
    ('inv', r'∀ a : Fin (\d+), ∃ b : Nat, b < \1 ∧ (\S+) a \(vad_fin \1 b\) = \((\d+) : Fin \1\)'),
]


def f3_parse(r):
    for law, rx in _F3_STMT:
        mt = re.fullmatch(rx, r['stmt'])
        if mt:
            m, op = int(mt.group(1)), mt.group(2)
            e = int(mt.group(3)) if law in ('lid', 'inv') else None
            break
    else:
        raise ValueError(r['stmt'])
    if op == 'vad_op':
        dm = re.fullmatch(r'def vad_op \(a b : Fin (\d+)\) : Fin \1 := ⟨\[([\d,]*)\]\.getD \(a\.val \* \1 \+ b\.val\) 0 % \1, Nat\.mod_lt _ \(by decide\)⟩', r['defs'])
        assert dm and int(dm.group(1)) == m, r['defs']
        flat = [int(x) for x in dm.group(2).split(',')]
        assert len(flat) == m * m
        table = [flat[i * m:(i + 1) * m] for i in range(m)]
        return {'m': m, 'law': law, 'e': e, 'op': op, 'table': table, 'key': None}
    om = re.fullmatch(r'vad_f3_([a-z]+\d*)_(\d+)', op)
    assert om and int(om.group(2)) == m, op
    return {'m': m, 'law': law, 'e': e, 'op': op, 'table': f3_pyop(om.group(1), m), 'key': om.group(1)}


def f3_reprint(p):
    stmt = {'assoc': 'a b c', 'comm': 'a b', 'medial': 'a b c d', 'lid': 'a', 'inv': 'a'}
    m, op, e = p['m'], p['op'], p['e']
    body = {'assoc': f'{op} ({op} a b) c = {op} a ({op} b c)', 'comm': f'{op} a b = {op} b a',
            'medial': f'{op} ({op} a b) ({op} c d) = {op} ({op} a c) ({op} b d)',
            'lid': f'{op} ({e} : Fin {m}) a = a', 'inv': None}[p['law']]
    if p['law'] == 'inv':
        s = f'∀ a : Fin {m}, ∃ b : Nat, b < {m} ∧ {op} a (vad_fin {m} b) = ({e} : Fin {m})'
    else:
        s = f'∀ {stmt[p["law"]]} : Fin {m}, {body}'
    defs = f3_table_def('vad_op', m, p['table']) if p['key'] is None else ''
    return {'defs': defs, 'stmt': s}


def f3_truth(p):
    return f3_law_true(p['table'], p['m'], p['law'], p['e'])


def f3_build(spec, strat):
    nm = f"vad_t_F3_{spec['seed']}"
    r = f3_render(spec)
    m, key, law = spec['m'], spec['key'], spec['law']
    defs = r['defs'] + '\n' if r['defs'] else ''
    if strat == 'S_decide':
        return f"{defs}theorem {nm} : {r['stmt']} := by decide", nm
    B = f3_op_name(key, m)
    lem = f'vadl_f3_{key}_{m}_{law}'
    if spec['table'] is None:
        return f"theorem {nm} : {r['stmt']} := {lem}", nm
    f, g = spec['perm'], [spec['perm'].index(i) for i in range(m)]
    helper = f3_perm_def('vad_f', m, f) + '\n' + f3_perm_def('vad_g', m, g) + '\n'
    args = {'assoc': f'vad_f vad_g {B} vad_op (by decide) {lem} (by decide)',
            'comm': f'vad_f vad_g {B} vad_op {lem} (by decide)',
            'medial': f'vad_f vad_g {B} vad_op (by decide) {lem} (by decide)',
            'lid': f"vad_f vad_g {B} vad_op ({spec['e0']} : Fin {m}) ({spec['e']} : Fin {m}) (by decide) (by decide) {lem} (by decide) (by decide)",
            'inv': f"vad_f vad_g {B} vad_op ({spec['e0']} : Fin {m}) ({spec['e']} : Fin {m}) (by decide) {lem} (by decide) (by decide)"}[law]
    return f"{defs}{helper}theorem {nm} : {r['stmt']} :=\n  vad_hom_{law} {args}", nm


# ---------------------------------------------------------------------------
# F4  graph invariants on Nat-indexed Bool adjacency matrices
# ---------------------------------------------------------------------------
F4_N = {'cal': (5, 6), 'test': (7,)}
F4_TEMPLATES = {'cal': ('bip_random', 'cycle', 'tripartite'), 'test': ('circulant', 'multipartite', 'tree')}
F4_CLAIMS = ('bip_tf', 'col3_k4', 'compl_deg', 'degsum', 'compl_reg')

add_unit('f4_defs', 'F4', 'base', '''
def vad_deg (G : Nat → Nat → Bool) (v : Nat) : Nat → Nat
  | 0 => 0
  | k+1 => vad_deg G v k + (if G v k then 1 else 0)
def vad_compl (G : Nat → Nat → Bool) (i j : Nat) : Bool := (i != j) && !(G i j)
def vad_dsum (G : Nat → Nat → Bool) (n : Nat) : Nat → Nat
  | 0 => 0
  | v+1 => vad_dsum G n v + vad_deg G v n''')
add_unit('f4_compl', 'F4', 'base', '''
theorem vadl_compl_deg (G : Nat → Nat → Bool) (n v : Nat) (hv : v < n) (hl : G v v = false) :
    vad_deg G v n + vad_deg (vad_compl G) v n = n - 1 := by
  have key : ∀ k, vad_deg G v k + vad_deg (vad_compl G) v k + (if v < k then 1 else 0) = k := by
    intro k
    induction k with
    | zero => simp [vad_deg]
    | succ k ih =>
      simp only [vad_deg, vad_compl]
      by_cases h1 : v < k
      · have h1' : v < k + 1 := by omega
        have h2 : v ≠ k := by omega
        by_cases hg : G v k = true
        · simp [h1, h1', h2, hg] at *
          omega
        · have hg' : G v k = false := by simpa using hg
          simp [h1, h1', h2, hg'] at *
          omega
      · by_cases h2 : v = k
        · subst h2
          simp [hl] at *
          omega
        · have h1' : ¬ v < k + 1 := by omega
          by_cases hg : G v k = true
          · simp [h1, h1', h2, hg] at *
            omega
          · have hg' : G v k = false := by simpa using hg
            simp [h1, h1', h2, hg'] at *
            omega
  have := key n
  simp [hv] at this
  omega''')
add_unit('f4_colour', 'F4', 'base', '''
theorem vadl_prop2_tf (G : Nat → Nat → Bool) (n : Nat) (col : Nat → Nat)
    (hc : ∀ i, i < n → col i < 2)
    (h : ∀ i, i < n → ∀ j, j < n → G i j = true → col i ≠ col j) :
    ∀ i, i < n → ∀ j, j < n → ∀ k, k < n → G i j = true → G j k = true → G i k = true → False := by
  intro i hi j hj k hk g1 g2 g3
  have := h i hi j hj g1
  have := h j hj k hk g2
  have := h i hi k hk g3
  have := hc i hi
  have := hc j hj
  have := hc k hk
  omega
theorem vadl_prop3_k4 (G : Nat → Nat → Bool) (n : Nat) (col : Nat → Nat)
    (hc : ∀ i, i < n → col i < 3)
    (h : ∀ i, i < n → ∀ j, j < n → G i j = true → col i ≠ col j) :
    ∀ i, i < n → ∀ j, j < n → ∀ k, k < n → ∀ l, l < n → G i j = true → G j k = true → G i k = true → G i l = true → G j l = true → G k l = true → False := by
  intro i hi j hj k hk l hl g1 g2 g3 g4 g5 g6
  have := h i hi j hj g1
  have := h j hj k hk g2
  have := h i hi k hk g3
  have := h i hi l hl g4
  have := h j hj l hl g5
  have := h k hk l hl g6
  have := hc i hi
  have := hc j hj
  have := hc k hk
  have := hc l hl
  omega''')
add_unit('f4_handshake', 'F4', 'base', '''
def vad_csum (G : Nat → Nat → Bool) (j : Nat) : Nat → Nat
  | 0 => 0
  | k+1 => vad_csum G j k + (if G k j then 1 else 0)
def vad_dsum2 (G : Nat → Nat → Bool) (j : Nat) : Nat → Nat
  | 0 => 0
  | v+1 => vad_dsum2 G j v + vad_deg G v j
theorem vadl_dsum_step (G : Nat → Nat → Bool) (j : Nat) : ∀ k, vad_dsum2 G (j+1) k = vad_dsum2 G j k + vad_csum G j k := by
  intro k
  induction k with
  | zero => rfl
  | succ k ih =>
    simp only [vad_dsum2, vad_csum, vad_deg]
    omega
theorem vadl_csum_eq_deg (G : Nat → Nat → Bool) (m : Nat) (hs : ∀ i, i < m → G i m = G m i) : ∀ k, k ≤ m → vad_csum G m k = vad_deg G m k := by
  intro k
  induction k with
  | zero => intro _; rfl
  | succ k ih =>
    intro hk
    simp only [vad_csum, vad_deg]
    rw [ih (by omega), hs k (by omega)]
theorem vadl_handshake (G : Nat → Nat → Bool) (n : Nat)
    (hs : ∀ i, i < n → ∀ j, j < n → G i j = G j i) (hl : ∀ i, i < n → G i i = false) :
    vad_dsum G n n % 2 = 0 := by
  have key : ∀ m, m ≤ n → vad_dsum2 G m m % 2 = 0 := by
    intro m
    induction m with
    | zero => intro _; rfl
    | succ m ih =>
      intro hm
      have ih' := ih (by omega)
      have e1 := vadl_dsum_step G m (m+1)
      have e3 : vad_csum G m (m+1) = vad_csum G m m + (if G m m then 1 else 0) := rfl
      have e4 : vad_deg G m (m+1) = vad_deg G m m + (if G m m then 1 else 0) := rfl
      have e5 : vad_dsum2 G (m+1) (m+1) = vad_dsum2 G (m+1) m + vad_deg G m (m+1) := rfl
      have e6 := vadl_csum_eq_deg G m (fun i hi => hs i (by omega) m (by omega)) m (Nat.le_refl m)
      have e7 := hl m (by omega)
      simp [e7] at e3 e4
      have e8 := vadl_dsum_step G m m
      omega
  have := key n (Nat.le_refl n)
  have h2 : vad_dsum2 G n n = vad_dsum G n n := by
    have : ∀ k, vad_dsum2 G n k = vad_dsum G n k := by
      intro k
      induction k with
      | zero => rfl
      | succ k ih => simp only [vad_dsum2, vad_dsum]; omega
    exact this n
  omega''')


def f4_edges_to_matrix(n, edges):
    G = [[False] * n for _ in range(n)]
    for i, j in edges:
        G[i][j] = G[j][i] = True
    return G


def f4_gen(seed, split):
    for attempt in range(200):
        rng = rng_for('F4', split, seed, attempt)
        kind = rng.choice(F4_TEMPLATES[split])
        n = rng.choice(F4_N[split])
        col, claims, k_reg = None, ['compl_deg', 'degsum'], None
        if kind == 'bip_random':
            col = [rng.randint(0, 1) for _ in range(n)]
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if col[i] != col[j] and rng.random() < 0.7]
            claims += ['bip_tf', 'col3_k4']
        elif kind == 'cycle':
            edges = [(i, (i + 1) % n) for i in range(n)]
            col = [i % 2 for i in range(n)] if n % 2 == 0 else [0, 1] * (n // 2) + [2]
            claims += ['compl_reg', 'col3_k4'] + (['bip_tf'] if n % 2 == 0 else [])
        elif kind == 'tripartite':
            col = [rng.randint(0, 2) for _ in range(n)]
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if col[i] != col[j] and rng.random() < 0.75]
            claims += ['col3_k4']
        elif kind == 'circulant':
            S = sorted(rng.sample(range(1, n // 2 + 1), rng.randint(1, 2)))
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if min((i - j) % n, (j - i) % n) in S]
            claims += ['compl_reg']
            if n % 2 == 0 and all(s % 2 == 1 for s in S):
                col = [i % 2 for i in range(n)]
                claims += ['bip_tf', 'col3_k4']
        elif kind == 'multipartite':
            parts = rng.choice([[4, 3], [3, 2, 2], [5, 2], [3, 3, 1], [4, 2, 1], [2, 2, 3], [6, 1], [2, 5]])
            col = [p for p, sz in enumerate(parts) for _ in range(sz)]
            edges = [(i, j) for i in range(n) for j in range(i + 1, n) if col[i] != col[j]]
            claims += ['col3_k4'] + (['bip_tf'] if len(parts) == 2 else [])
            if len(set(parts)) == 1:
                claims += ['compl_reg']
        else:
            parent = [None] + [rng.randrange(i) for i in range(1, n)]
            depth = [0]
            for i in range(1, n):
                depth.append(depth[parent[i]] + 1)
            col = [d % 2 for d in depth]
            edges = [(parent[i], i) for i in range(1, n)]
            claims += ['bip_tf', 'col3_k4']
        pi = list(range(n))
        rng.shuffle(pi)                       # random vertex relabelling: same graph, many distinct statements
        edges = [(pi[i], pi[j]) for i, j in edges]
        if col is not None:
            col = [col[pi.index(v)] for v in range(n)]
        G = f4_edges_to_matrix(n, edges)
        deg = [sum(r) for r in G]
        if 'compl_reg' in claims and len(set(deg)) != 1:
            claims.remove('compl_reg')
        if len(edges) == 0 or (kind in ('bip_random', 'tripartite') and (len(set(col)) < (2 if kind == 'bip_random' else 3))):
            continue
        claim = rng.choice(claims)
        spec = {'family': 'F4', 'split': split, 'seed': seed, 'kind': kind, 'n': n, 'matrix': G, 'col': col,
                'claim': claim, 'templates': [kind], 'size': n}
        if claim == 'compl_reg':
            spec['k'] = deg[0]
        return spec
    raise RuntimeError('F4 generation failed')


def f4_defs_text(n, G, col):
    flat = ','.join('true' if G[i][j] else 'false' for i in range(n) for j in range(n))
    out = f'def vad_g : Nat → Nat → Bool := fun i j => [{flat}].getD (i * {n} + j) false'
    if col is not None:
        out += f'\ndef vad_c : Nat → Nat := fun i => [{",".join(str(c) for c in col)}].getD i 0'
    return out


def f4_claim_stmt(claim, n, k=None):
    bip = f'∀ i, i < {n} → ∀ j, j < {n} → vad_g i j = true → vad_c i ≠ vad_c j'
    tf = f'∀ i, i < {n} → ∀ j, j < {n} → ∀ k, k < {n} → vad_g i j = true → vad_g j k = true → vad_g i k = true → False'
    k4 = (f'∀ i, i < {n} → ∀ j, j < {n} → ∀ k, k < {n} → ∀ l, l < {n} → vad_g i j = true → vad_g j k = true → '
          'vad_g i k = true → vad_g i l = true → vad_g j l = true → vad_g k l = true → False')
    if claim == 'bip_tf': return f'(∀ i, i < {n} → vad_c i < 2) ∧ ({bip}) ∧ ({tf})'
    if claim == 'col3_k4': return f'(∀ i, i < {n} → vad_c i < 3) ∧ ({bip}) ∧ ({k4})'
    if claim == 'compl_deg': return f'∀ v, v < {n} → vad_deg vad_g v {n} + vad_deg (vad_compl vad_g) v {n} = {n} - 1'
    if claim == 'degsum': return f'vad_dsum vad_g {n} {n} % 2 = 0'
    return f'∀ v, v < {n} → vad_deg (vad_compl vad_g) v {n} = {n - 1 - k}'


def f4_render(spec):
    needs_col = spec['claim'] in ('bip_tf', 'col3_k4')
    return {'defs': f4_defs_text(spec['n'], spec['matrix'], spec['col'] if needs_col else None),
            'stmt': f4_claim_stmt(spec['claim'], spec['n'], spec.get('k'))}


def f4_parse(r):
    dm = re.fullmatch(r'def vad_g : Nat → Nat → Bool := fun i j => \[([a-z,]*)\]\.getD \(i \* (\d+) \+ j\) false'
                      r'(?:\ndef vad_c : Nat → Nat := fun i => \[([\d,]*)\]\.getD i 0)?', r['defs'])
    assert dm, r['defs']
    n = int(dm.group(2))
    flat = [x == 'true' for x in dm.group(1).split(',')]
    assert len(flat) == n * n
    G = [flat[i * n:(i + 1) * n] for i in range(n)]
    col = [int(x) for x in dm.group(3).split(',')] if dm.group(3) else None
    st = r['stmt']
    for claim in F4_CLAIMS:
        for kk in (range(0, n) if claim == 'compl_reg' else (None,)):
            if f4_claim_stmt(claim, n, kk) == st:
                return {'n': n, 'matrix': G, 'col': col, 'claim': claim, 'k': kk, 'stmt': st}
    raise ValueError(st)


def f4_reprint(p):
    # re-print from the parsed statement kind, not from the original spec
    return {'defs': f4_defs_text(p['n'], p['matrix'], p['col']), 'stmt': f4_claim_stmt(p['claim'], p['n'], p['k'])}


def f4_deg(G, v, n):
    return sum(1 for w in range(n) if G[v][w])


def f4_truth(p):
    n, G, col, claim = p['n'], p['matrix'], p['col'], p['claim']
    R = range(n)
    if claim in ('bip_tf', 'col3_k4'):
        lim = 2 if claim == 'bip_tf' else 3
        if not (all(col[i] < lim for i in R) and all(not G[i][j] or col[i] != col[j] for i in R for j in R)):
            return False
        if claim == 'bip_tf':
            return all(not (G[i][j] and G[j][k] and G[i][k]) for i in R for j in R for k in R)
        return all(not (G[i][j] and G[j][k] and G[i][k] and G[i][l] and G[j][l] and G[k][l])
                   for i in R for j in R for k in R for l in R)
    Gc = [[(i != j) and not G[i][j] for j in R] for i in R]
    if claim == 'compl_deg':
        return all(f4_deg(G, v, n) + f4_deg(Gc, v, n) == n - 1 for v in R)
    if claim == 'degsum':
        return sum(f4_deg(G, v, n) for v in R) % 2 == 0
    return all(f4_deg(Gc, v, n) == n - 1 - p['k'] for v in R)


def f4_build(spec, strat):
    nm = f"vad_t_F4_{spec['seed']}"
    r = f4_render(spec)
    n, claim = spec['n'], spec['claim']
    defs = r['defs'] + '\n'
    if strat == 'S_decide':
        return f"{defs}theorem {nm} : {r['stmt']} := by decide", nm
    hl = f'  have hl : ∀ v, v < {n} → vad_g v v = false := by decide'
    bip = f'∀ i, i < {n} → ∀ j, j < {n} → vad_g i j = true → vad_c i ≠ vad_c j'
    if claim in ('bip_tf', 'col3_k4'):
        lim, lem = (2, 'vadl_prop2_tf') if claim == 'bip_tf' else (3, 'vadl_prop3_k4')
        body = (f'  have hc : ∀ i, i < {n} → vad_c i < {lim} := by decide\n  have hb : {bip} := by decide\n'
                f'  exact ⟨hc, hb, {lem} vad_g {n} vad_c hc hb⟩')
    elif claim == 'compl_deg':
        body = f'{hl}\n  exact fun v hv => vadl_compl_deg vad_g {n} v hv (hl v hv)'
    elif claim == 'degsum':
        body = (f'{hl}\n  have hs : ∀ i, i < {n} → ∀ j, j < {n} → vad_g i j = vad_g j i := by decide\n'
                f'  exact vadl_handshake vad_g {n} hs hl')
    else:
        body = (f'{hl}\n  have hr : ∀ v, v < {n} → vad_deg vad_g v {n} = {spec["k"]} := by decide\n'
                f'  intro v hv\n  have h1 := vadl_compl_deg vad_g {n} v hv (hl v hv)\n  have h2 := hr v hv\n  omega')
    return f"{defs}theorem {nm} : {r['stmt']} := by\n{body}", nm


# ---------------------------------------------------------------------------
# statement fidelity: template renderer vs parser + second printer + semantic evaluator
# ---------------------------------------------------------------------------
def render_spec(spec):
    """Template renderer: {'defs': context definitions, 'stmt': the theorem statement}."""
    f = spec['family']
    if f == 'F1': return {'defs': '', 'stmt': f1_stmt(spec['vars'], spec['lhs'], spec['rhs'])}
    if f == 'F2': return {'defs': '', 'stmt': f2_stmt(spec['vars'], spec['lhs'], spec['m'], spec['rhs'])}
    if f == 'F3': return f3_render(spec)
    if f == 'F4': return f4_render(spec)
    return {'defs': '', 'stmt': f5_stmt_text(spec['k'], spec['expr'])}


def parse_spec(fam, r):
    """Independent parser of the rendered Lean text (never looks at the generating spec)."""
    if fam == 'F1': return f1_parse_stmt(r['stmt'])
    if fam == 'F2': return f2_parse_stmt(r['stmt'])
    if fam == 'F3': return f3_parse(r)
    if fam == 'F4': return f4_parse(r)
    return f5_parse_stmt(r['stmt'])


def reprint_spec(fam, p):
    """Second printer, driven only by the parsed object."""
    if fam == 'F1': return {'defs': '', 'stmt': f1_reprint(p)}
    if fam == 'F2': return {'defs': '', 'stmt': f2_reprint(p)}
    if fam == 'F3': return f3_reprint(p)
    if fam == 'F4': return f4_reprint(p)
    return {'defs': '', 'stmt': f5_reprint(p)}


def truth_spec(fam, p):
    return {'F1': f1_truth, 'F2': f2_truth, 'F3': f3_truth, 'F4': f4_truth, 'F5': f5_truth}[fam](p)


def statement_text(r):
    return (r['defs'] + '\n' if r['defs'] else '') + r['stmt']


def fidelity(spec):
    fam = spec['family']
    r = render_spec(spec)
    p = parse_spec(fam, r)
    rp = reprint_spec(fam, p)
    return {'renderers_agree': rp == r, 'python_true': bool(truth_spec(fam, p)), 'statement_sha256': sha(statement_text(r))}


# ---------------------------------------------------------------------------
# Abstraction invention: structural anti-unification -> candidate lemma -> kernel check
# ---------------------------------------------------------------------------
def spec_id(spec):
    return f"vad_t_{spec['family']}_{spec['seed']}"


def _canon_metas(pat):
    order = metas(pat)
    return subst(pat, {m: ('m', f'C{i}') for i, m in enumerate(order)})


def f1_at(e, path):
    for i in path:
        e = e[i]
    return e


def f1_redex_eq(spec, i):
    st = spec['steps'][i]
    p = tuple(st['path'])
    return ('eq', f1_at(st['before'], p), f1_at(st['after'], p))


def f1_candidate(a, b):
    """lgg of the redex equations of same-rule rewrite steps of two F1 specs (the instances the
    library lemma was applied to); kept only if the generalisation is a true Boolean identity."""
    out = []
    for i, sa in enumerate(a['steps']):
        for j, sb in enumerate(b['steps']):
            if (sa['rule'], sa['rev']) != (sb['rule'], sb['rev']):
                continue
            try:
                pat = lgg(f1_redex_eq(a, i), f1_redex_eq(b, j))
            except Incompatible:
                continue
            if not metas(pat) or pat[1] == pat[2]:
                continue
            vs = sorted(f1_vars(pat[1]) | f1_vars(pat[2]))
            if len(vs) > 10:
                continue
            if any(f1_eval(pat[1], dict(zip(vs, bits))) != f1_eval(pat[2], dict(zip(vs, bits)))
                   for bits in itertools.product((False, True), repeat=len(vs))):
                continue
            stmt = f'∀ {" ".join(vs)} : Bool, {f1_render(pat[1])} = {f1_render(pat[2])}'
            h = sha(stmt + '|' + spec_id(a) + '|' + spec_id(b))[:10]
            out.append({'family': 'F1', 'pattern': pat, 'vars': vs, 'stmt': stmt, 'unit': f'inv_f1_{h}',
                        'decl': f'vadl_inv_f1_{h}', 'origin': [spec_id(a), spec_id(b)],
                        'body': f'theorem vadl_inv_f1_{h} : {stmt} := by decide'})
    return out


def _poly_meta_to_var(e):
    if e[0] == 'm': return ('v', e[1].lower())
    if e[0] in ('v', 'c'): return e
    if e[0] in '+*': return (e[0], _poly_meta_to_var(e[1]), _poly_meta_to_var(e[2]))
    return (e[0], _poly_meta_to_var(e[1]), e[2])


def f2_candidate(a, b):
    if a['m'] != b['m'] or a['rhs'] != b['rhs'] or a['rhs'][0] != 'const':
        return []
    try:
        pat = lgg(a['lhs'], b['lhs'])
    except Incompatible:
        return []
    ms = sorted(m.lower() for m in metas(pat))
    if not ms or len(ms) > 2:
        return []
    vs = ['n'] + ms
    lhs = _poly_meta_to_var(pat)
    if not f2_truth({'vars': vs, 'lhs': lhs, 'm': a['m'], 'rhs': a['rhs']}):
        return []
    st = f2_stmt(vs, lhs, a['m'], a['rhs'])
    h = sha(st + '|' + spec_id(a) + '|' + spec_id(b))[:10]
    return [{'family': 'F2', 'pattern': pat, 'vars': vs, 'stmt': st, 'unit': f'inv_f2_{h}', 'decl': f'vadl_inv_f2_{h}',
             'origin': [spec_id(a), spec_id(b)], 'm': a['m'], 'rhs': a['rhs'],
             'body': f2_decide_body(f'vadl_inv_f2_{h}', vs, lhs, a['m'], a['rhs'])}]


def f5_pat_eval(e, env):
    t = e[0]
    if t == 'm': return env[e[1]]
    if t == 'v': return env[e[1]]
    if t == 'c': return e[1]
    a, b = f5_pat_eval(e[1], env), f5_pat_eval(e[2], env)
    return a + b if t == '+' else a * b


def f5_candidate(a, b):
    try:
        pat = lgg(a['expr'], b['expr'])
    except Incompatible:
        return []
    pat = _vars_to_metas(pat)
    ms = metas(pat)
    if not (2 <= len(ms) <= 5) or size(pat) < 5:
        return []
    canon = _canon_metas(pat)
    if any(_canon_metas(p) == canon for p, _ in F5_SHAPES.values()):
        return []
    pairs = [(x, y) for x in range(3) for y in range(x, 3)]
    for combo in itertools.product(pairs, repeat=len(ms)):
        lo = {m: c[0] for m, c in zip(ms, combo)}
        hi = {m: c[1] for m, c in zip(ms, combo)}
        if f5_pat_eval(pat, lo) > f5_pat_eval(pat, hi):
            return []
    h = sha(poly_render(canon) + '|' + spec_id(a) + '|' + spec_id(b))[:10]
    return [{'family': 'F5', 'pattern': pat, 'unit': f'f5_inv_{h}', 'shape': f'inv_{h}', 'origin': [spec_id(a), spec_id(b)],
             'stmt': f5_shape_stmt(pat)[0]}]


def _vars_to_metas(e):
    if e[0] == 'v': return ('m', 'V' + e[1])
    if e[0] in ('c', 'm'): return e
    return (e[0],) + tuple(_vars_to_metas(c) for c in e[1:])


def _leaves(e):
    if e[0] in ('v', 'c', 'm'):
        return [e]
    return [x for c in e[1:] if isinstance(c, tuple) for x in _leaves(c)]


def register_candidate(c):
    """Add a candidate to the library as an `invented` unit (statement + proof by the family strategy)."""
    if c['family'] == 'F5':
        f5_register_shape(c['shape'], c['pattern'], 'invented', c['origin'])
    else:
        add_unit(c['unit'], c['family'], 'invented', c['body'], c['origin'])
    return c


def invent(fam, specs, max_pairs=60):
    """Pairwise anti-unification over specs of one family; same-template pairs first. Returns registered candidates."""
    fn = {'F1': f1_candidate, 'F2': f2_candidate, 'F5': f5_candidate}.get(fam)
    if fn is None:
        return []      # F3/F4 statements are parameter records over a fixed operation; their lgg is not a lemma
    specs = sorted(specs, key=lambda s: s['seed'])
    pairs = [(a, b) for i, a in enumerate(specs) for b in specs[i + 1:] if a['templates'] == b['templates']]
    out, seen = [], set()
    for a, b in pairs[:max_pairs * 20]:
        for c in fn(a, b):
            if c['stmt'] in seen:
                continue
            seen.add(c['stmt'])
            out.append(register_candidate(c))
        if len(out) >= max_pairs:
            break
    return out


def candidate_decl(c):
    """The declaration record the dependency auditor consumes."""
    u = LIB[c['unit']]
    return {'text': u.body, 'origin': list(c['origin']), 'owns': list(u.decls)}


def apply_candidate(spec, c):
    """Proof body of `spec` through the invented lemma `c` (None when the lemma does not match)."""
    nm = f"vad_t_{spec['family']}_{spec['seed']}"
    if c['family'] != spec['family']:
        return None
    if c['family'] == 'F1':
        body, name, used = f1_build_with(spec, [c])
        return (body, name) if used else None
    if c['family'] == 'F2':
        sub = match(c['pattern'], spec['lhs'])
        if sub is None or spec['m'] != c['m'] or spec['rhs'] != c['rhs']:
            return None
        low = {k.lower(): v for k, v in sub.items()}
        args = ' '.join(poly_render(low[v]) if v in low else v for v in c['vars'])
        return f"theorem {nm} : {f2_stmt(spec['vars'], spec['lhs'], spec['m'], spec['rhs'])} :=\n  fun n => {c['decl']} {args}", nm
    return None


def f5_apply_with(spec, shape_names):
    """S_lemma proof of an F5 spec using an explicit shape-name list (static + invented)."""
    k, e = spec['k'], spec['expr']
    hyp = {f'x{i}': f'h{i}' for i in range(1, k + 1)}
    nm = f"vad_t_F5_{spec['seed']}"
    intro = ' '.join(f'x{i} y{i}' for i in range(1, k + 1)) + ' ' + ' '.join(f'h{i}' for i in range(1, k + 1))
    return f"theorem {nm} : {f5_stmt_text(k, e)} := by\n  intro {intro}\n  exact {f5_lemma_term(e, hyp, shape_names)}", nm


def f5_shape_hits(spec, shape_names):
    """Names of the shapes from `shape_names` that the S_lemma proof actually uses on this spec."""
    body, _ = f5_apply_with(spec, shape_names)
    return sorted({n for n in shape_names if f'vadl_f5_{n} ' in body})


def f1_build_with(spec, cands):
    """S_lemma proof of an F1 spec in which every rewrite step whose redex equation is an instance of an
    invented candidate uses that lemma (otherwise the static library rule). -> (body, name, #invented uses)"""
    nm = f"vad_t_F1_{spec['seed']}"
    stmt = f1_stmt(spec['vars'], spec['lhs'], spec['rhs'])
    lines = [f'theorem {nm} : {stmt} := by', f"  intro {' '.join(spec['vars'])}"]
    used = 0
    for i, st in enumerate(spec['steps'], 1):
        ctx = f1_render(f1_ctx_at(st['before'], tuple(st['path'])))
        redex = f1_redex_eq(spec, i - 1)
        term = None
        for c in cands:
            sub = match(c['pattern'], redex)
            if sub is not None:
                low = {k.lower(): v for k, v in sub.items()}
                term = f"({c['decl']} {' '.join(f1_render(low[v]) if v in low else v for v in c['vars'])})"
                used += 1
                break
        if term is None:
            args = ' '.join(f1_render(a) for a in st['args'])
            term = f"({f1_unit_name(st['rule'])} {args})"
            if st['rev']:
                term += '.symm'
        lines.append(f"  have h{i} : {f1_render(st['before'])} = {f1_render(st['after'])} := congrArg (fun z : Bool => {ctx}) {term}")
    k = len(spec['steps'])
    chain = f'h{k}'
    for i in range(k - 1, 0, -1):
        chain = f'h{i}.trans ({chain})'
    lines.append(f'  exact {chain}')
    return '\n'.join(lines), nm, used


# ---------------------------------------------------------------------------
# splits, manifest, cost hints, audit inputs
# ---------------------------------------------------------------------------
def split_seeds(split, per=None):
    seeds = list(SEEDS[split])
    if per is None or per >= len(seeds):
        return seeds
    step = len(seeds) / per
    return [seeds[int(i * step)] for i in range(per)]


def cost_hint(spec):
    """Rough integer size of the S_decide search space (used only to pick cheap instances)."""
    f = spec['family']
    if f == 'F1': return (2 ** spec['nvars']) * (size(spec['lhs']) + size(spec['rhs']))
    if f == 'F2': return spec['m'] ** len(spec['vars']) * size(spec['lhs'])
    if f == 'F3': return spec['m'] ** {'assoc': 3, 'comm': 2, 'medial': 4, 'lid': 1, 'inv': 2}[spec['law']]
    if f == 'F4': return spec['n'] ** {'bip_tf': 3, 'col3_k4': 4, 'compl_deg': 2, 'degsum': 2, 'compl_reg': 2}[spec['claim']]
    return size(spec['expr'])


DECLARED_TEMPLATES = {
    'F1': {sp: sorted(k for k, v in F1_RULES.items() if v[2] == sp) for sp in ('cal', 'test')},
    'F2': {sp: sorted(F2_TEMPLATES[sp]) for sp in ('cal', 'test')},
    'F3': {sp: sorted(F3_OPS[sp]) for sp in ('cal', 'test')},
    'F4': {sp: sorted(F4_TEMPLATES[sp]) for sp in ('cal', 'test')},
    'F5': {sp: sorted(F5_TEMPLATES[sp]) for sp in ('cal', 'test')},
}


def split_manifest(per=None):
    """Frozen-split manifest: seeds, sha256 of every generated statement, template/moduli sets, disjointness."""
    man, shas = {}, {}
    for fam in FAMILIES:
        man[fam] = {}
        for sp in ('cal', 'test'):
            rows, templates = {}, set()
            for seed in split_seeds(sp, per):
                spec = gen(fam, seed, sp)
                rows[seed] = sha(statement_text(render_spec(spec)))
                templates.update(spec['templates'])
            shas[(fam, sp)] = rows
            canon = json.dumps(sorted(rows.items()), separators=(',', ':'))
            man[fam][sp] = {'seeds': [min(rows), max(rows)], 'count': len(rows), 'statement_sha256': {str(k): v for k, v in rows.items()},
                            'split_sha256': sha(canon), 'templates_observed': sorted(templates),
                            'templates_declared': DECLARED_TEMPLATES[fam][sp],
                            'duplicate_statements': len(rows) - len(set(rows.values()))}
        c, t = man[fam]['cal'], man[fam]['test']
        man[fam]['checks'] = {
            'templates_disjoint': not (set(DECLARED_TEMPLATES[fam]['cal']) & set(DECLARED_TEMPLATES[fam]['test'])),
            'observed_within_declared': set(c['templates_observed']) <= set(c['templates_declared']) and set(t['templates_observed']) <= set(t['templates_declared']),
            'statements_disjoint': not (set(shas[(fam, 'cal')].values()) & set(shas[(fam, 'test')].values())),
            'moduli_disjoint': (not (set(F2_MODULI['cal']) & set(F2_MODULI['test']))) if fam == 'F2' else None,
        }
    man['manifest_sha256'] = sha(json.dumps({f: {sp: man[f][sp]['split_sha256'] for sp in ('cal', 'test')} for f in FAMILIES}, sort_keys=True))
    return man


def library_decls():
    return {f'unit:{u.name}': {'text': u.body, 'origin': list(u.origin), 'owns': list(u.decls)} for u in LIB.values()}


def target_decls(specs, strat='S_lemma'):
    out = {}
    for sp in specs:
        body, nm = build(sp, strat)
        out[f'target:{nm}'] = {'text': body, 'origin': [], 'owns': [nm]}
    return out


def held_out_names(per=None):
    return {f'vad_t_{fam}_{seed}' for fam in FAMILIES for seed in split_seeds('test', per)}

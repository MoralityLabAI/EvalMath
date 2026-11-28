"""VAD-05: isolated core-Lean conjunction proof gym; no model or tactics."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import tempfile
import time

REGIMES = ('shared', 'renamed', 'shifted', 'null')
ARMS = ('direct', 'concrete', 'shape', 'global_shape')
H = 8


def leaves(t):
    return [t] if isinstance(t, int) else leaves(t[0]) + leaves(t[1])


def shape(t):
    return 'x' if isinstance(t, int) else '(' + shape(t[0]) + shape(t[1]) + ')'


def subtrees(t):
    if not isinstance(t, int):
        yield t
        yield from subtrees(t[0])
        yield from subtrees(t[1])


def tree(r, xs):
    if len(xs) == 1:
        return xs[0]
    i = r.randrange(1, len(xs))
    return tree(r, xs[:i]), tree(r, xs[i:])


def replace(t, xs):
    it = iter(xs)
    def rec(u):
        return next(it) if isinstance(u, int) else (rec(u[0]), rec(u[1]))
    return rec(t)


def family(seed, regime):
    r = random.Random(seed)
    k = r.choice((4, 5, 6))
    motif = tree(r, list(range(k)))
    alternate = tree(r, list(range(k)))
    while shape(alternate) == shape(motif):
        alternate = tree(r, list(range(k)))
    seen = set()
    def root(dev):
        while True:
            m = motif if dev or regime != 'shifted' else alternate
            if regime == 'null':
                t = tree(r, r.sample(range(32), k + r.randrange(3, 7)))
            else:
                ids = list(range(k)) if regime == 'shared' else r.sample(range(32), k)
                a = replace(m, ids)
                b = tree(r, r.sample([i for i in range(32) if i not in ids], r.randrange(3, 7)))
                t = (a, b) if r.randrange(2) else (b, a)
            if t not in seen:
                seen.add(t)
                return t
    return tuple(root(True) for _ in range(4)), tuple(root(False) for _ in range(H))


def key(t, kind):
    return shape(t) if kind == 'shape' else t


def discover(roots, kind, horizon):
    counts, reps, visits = Counter(), {}, 0
    for t in roots:
        for u in subtrees(t):
            visits += 1
            if len(leaves(u)) >= 3:
                k = key(u, kind)
                counts[k] += 1
                reps[k] = u
    # For one fixed candidate, all exact matches are disjoint (equal leaf count).
    def value(k):
        n = len(leaves(reps[k]))
        return horizon * counts[k] * (n - 2) - len(roots) * (2*n - 1)
    best = min(counts, key=lambda k: (-value(k), len(leaves(reps[k])), repr(k)), default=None)
    return (reps[best] if best is not None and value(best)>0 else None), visits + len(counts)


def render(t, prop=False):
    if isinstance(t, int):
        return ('p' if prop else 'h') + str(t)
    return '(' + ('And' if prop else 'And.intro') + ' ' + render(t[0], prop) + ' ' + render(t[1], prop) + ')'


def proof(t, cache, kind):
    if cache is not None and key(t, kind) == key(cache, kind):
        return '(vad_cache ' + ' '.join('h'+str(x) for x in leaves(t)) + ')', len(leaves(t))+1, 1
    if isinstance(t, int):
        return 'h'+str(t), 1, 0
    a, ac, an = proof(t[0], cache, kind)
    b, bc, bn = proof(t[1], cache, kind)
    return '(And.intro '+a+' '+b+')', 1+ac+bc, an+bn


def decl(name, t, body):
    ids = sorted(leaves(t))
    assert len(set(ids)) == len(ids)
    return 'theorem '+name+' {'+' '.join('p'+str(x) for x in ids)+' : Prop} '+ ' '.join('(h'+str(x)+' : p'+str(x)+')' for x in ids)+' : '+render(t, True)+' := '+body+'\n'


def source(t, cache, kind):
    # Generic cache leaf binders are numbered in traversal order, independent of target names.
    c = None if cache is None else replace(cache, range(len(leaves(cache))))
    text = 'import Init\nset_option autoImplicit false\n'
    if c is not None:
        text += decl('vad_cache', c, render(c))
    body, refs, uses = proof(t, cache, kind)
    text += decl('vad_target', t, body)
    if c is not None:
        text += '#print axioms vad_cache\n'
    text += '#print axioms vad_target\n'
    return text, refs, uses


def audit(text, t, cache):
    """Parse the generated, restricted term grammar independently of proof()."""
    c = None
    seen = []
    for line in text.splitlines():
        if not line.startswith('theorem '):
            assert line in ('import Init','set_option autoImplicit false','#print axioms vad_cache','#print axioms vad_target')
            continue
        m = re.fullmatch(r'theorem (vad_cache|vad_target) \{((?:p\d+ ?)+) : Prop\} ((?:\(h\d+ : p\d+\) ?)+) : (.+) := (.+)', line)
        assert m, line
        name, ps, hs, typ, term = m.groups()
        ids = [int(x[1:]) for x in ps.split()]
        pairs = [(int(a),int(b)) for a,b in re.findall(r'\(h(\d+) : p(\d+)\)',hs)]
        assert pairs == [(i,i) for i in ids] and len(ids)==len(set(ids))
        def parse(expr, typemode):
            tokens=iter(re.findall(r'\(|\)|[A-Za-z_.][A-Za-z_.0-9]*',expr))
            assert re.sub(r'\s+','',expr)==''.join(re.findall(r'\(|\)|[A-Za-z_.][A-Za-z_.0-9]*',expr))
            def rec():
                token=next(tokens)
                if token!='(':
                    assert re.fullmatch(('p' if typemode else 'h')+r'\d+',token)
                    v=int(token[1:]); assert v in ids; return v
                op=next(tokens)
                if op==('And' if typemode else 'And.intro'):
                    out=(rec(),rec())
                else:
                    assert not typemode and op=='vad_cache' and c is not None and name=='vad_target'
                    args=[rec() for _ in leaves(c)]
                    out=replace(c,args)
                assert next(tokens)==')'
                return out
            out=rec(); assert next(tokens,None) is None; return out
        expected=replace(cache,range(len(leaves(cache)))) if name=='vad_cache' else t
        assert ids == sorted(leaves(expected))
        assert parse(typ,True)==expected==parse(term,False)
        seen.append(name)
        if name=='vad_cache': c=expected
    assert seen==(['vad_cache','vad_target'] if cache is not None else ['vad_target'])


def run(out, lean=None):
    out.mkdir(parents=True,exist_ok=True)
    cal=[family(10000+i,REGIMES[i%4])[0] for i in range(16)]
    g,gw=discover(tuple(t for f in cal for t in f),'shape',32*H)
    rows=[]; manifest=[]
    for i in range(32):
        regime=REGIMES[i%4]; dev,held=family(20000+i,regime)
        assert not set(dev)&set(held)
        for arm in ARMS:
            kind='concrete' if arm=='concrete' else 'shape'
            cache,work=(None,0) if arm=='direct' else (g,0) if arm=='global_shape' else discover(dev,kind,H)
            build=0 if cache is None else 2*len(leaves(cache))-1
            refs=uses=byte_count=0
            for j,t in enumerate(held):
                s,n,u=source(t,cache,kind); audit(s,t,cache)
                p=out/f'f{i:02d}_t{j:02d}_{arm}.lean'; p.write_text(s)
                manifest.append({'file':p.name,'sha256':hashlib.sha256(s.encode()).hexdigest(),'goal':t,'family':i,'arm':arm})
                refs+=n; uses+=u; byte_count+=len(s.encode())
            rows.append(dict(family=i,regime=regime,arm=arm,refs=refs,uses=uses,source_bytes=byte_count,construction=0 if arm=='global_shape' else build,work=work))
    # Global discovery/build is charged once, across all held-out families.
    gb=0 if g is None else 2*len(leaves(g))-1
    summary={}
    for arm in ARMS:
        rr=[r for r in rows if r['arm']==arm]
        sums={k:sum(r[k] for r in rr) for k in ('refs','uses','source_bytes','construction','work')}
        if arm=='global_shape': sums['construction']+=gb; sums['work']+=gw
        sums['total']=sums['refs']+sums['construction']+sums['work']
        summary[arm]=sums
    (out/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    receipt={'protocol':'VAD-05A','evidence':'restricted source-term grammar; kernel status separate','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'roots':256,'files':len(manifest),'summary':summary,'rows':rows,'kernel':'NOT_RUN'}
    if lean:
        # Each file gets a fresh process and can only access Init and its own cache.
        verified=[]
        for item in manifest:
            start=time.monotonic(); p=out/item['file']
            result=subprocess.run(lean+[str(p.resolve())],capture_output=True,text=True,timeout=60)
            required=['vad_target']+(['vad_cache'] if 'theorem vad_cache ' in p.read_text() else [])
            ok=result.returncode==0 and all(f"'{name}' does not depend on any axioms" in result.stdout for name in required)
            verified.append(dict(file=p.name,ok=ok,seconds=time.monotonic()-start,stdout=result.stdout,stderr=result.stderr))
            if not ok:
                (out/'kernel.json').write_text(json.dumps(verified,indent=2)+'\n')
                raise RuntimeError(p.name+': '+result.stdout+result.stderr)
        (out/'kernel.json').write_text(json.dumps(verified,indent=2)+'\n')
        receipt['kernel']='PASS'
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='rows'},indent=2))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,required=True); parser.add_argument('--lean',nargs='+'); args=parser.parse_args()
    run(args.out,args.lean)

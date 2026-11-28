"""VAD-06A: exact acyclic Horn proof costs and isolated Lean batches."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import re
import subprocess
import time

REGIMES = ('shared', 'shifted', 'mixed', 'null')
ARMS = ('direct', 'frequency', 'top4', 'exhaustive', 'support', 'support_exact', 'oracle')
HORIZONS = (8, 32, 128, 256)


def family(seed, regime):
    rng = Random(seed); facts = tuple(range(6)); rules = []; n = 6
    def rule(args, head=None):
        nonlocal n
        if head is None: head = n; n += 1
        assert all(a < head for a in args)
        rules.append((tuple(args), head)); return head
    def chain(start, length):
        for _ in range(length): start = rule((start, rng.choice(facts)))
        return start
    hubs = [chain(facts[i], rng.randrange(4, 7)) for i in range(2)]
    targets = []
    for j in range(8 + max(HORIZONS)):
        hub = (hubs[0] if j < 8 or regime == 'shared' else hubs[1] if regime == 'shifted'
               else hubs[j % 2] if regime == 'mixed' else None)
        if regime == 'null': hub = None
        private = chain(rng.choice(facts), rng.randrange(2, 8))
        goal = rule((private,))
        if hub is not None: rule((hub, rng.choice(facts)), goal)
        targets.append(goal)
    return facts, tuple(rules), tuple(targets[:8]), tuple(targets[8:]), n


def index(rules):
    by = defaultdict(list)
    for i, (_, h) in enumerate(rules): by[h].append(i)
    return by


def cone(rules, by, roots):
    todo = list(roots); nodes = set(todo); selected = set(); work = 0
    while todo:
        h = todo.pop(); work += 1
        for i in by[h]:
            selected.add(i); work += 1+len(rules[i][0])
            for a in rules[i][0]:
                if a not in nodes: nodes.add(a); todo.append(a)
    return tuple(sorted(selected)), nodes, work


def solve(facts, rules, indices, cached=()):
    d = {a: 1 for a in facts}; p = {a: ('f', a) for a in facts}; work = 0
    for a in cached: d[a] = 1; p[a] = ('c', a)
    for i in indices:
        args, h = rules[i]; work += 1 + len(args)
        if all(a in d for a in args):
            v = 1 + sum(d[a] for a in args)
            if v < d.get(h, float('inf')): d[h] = v; p[h] = ('r', i)
    return d, p, work


def independent(facts, rules, cached=()):
    d = dict.fromkeys(facts + tuple(cached), 1)
    while True:
        old = dict(d)
        for args, h in reversed(rules):
            if all(a in old for a in args):
                d[h] = min(d.get(h, float('inf')), 1+sum(old[a] for a in args))
        if old == d: return d


def occurrences(g, p, rules):
    kind, i = p[g]; out = Counter({g: 1}); work = 1
    if kind == 'r':
        for a in rules[i][0]:
            c, w = occurrences(a, p, rules); out.update(c); work += w
    return out, work


def choose(facts, rules, by, dev, held, method, horizon):
    if method == 'direct': return (), 0
    ix, nodes, work = cone(rules, by, dev)
    if method in ('support', 'support_exact'):
        # Each bit denotes a distinct development goal, propagated backward
        # along every available rule, rather than only the chosen proof tree.
        supports = {g: 1 << i for i,g in enumerate(dev)}
        for j in reversed(ix):
            args,h = rules[j]; bits = supports.get(h,0); work += 1+len(args)
            for a in args: supports[a] = supports.get(a,0) | bits
        cand = sorted(a for a in nodes-set(facts)-set(dev)-set(held)
                      if supports.get(a,0).bit_count() >= 2)
        work += len(nodes)
        if not cand: return (),work
        d,_,w=solve(facts,rules,ix); work+=w
        cand=[a for a in cand if a in d]
        scores={a:horizon*supports[a].bit_count()*(d[a]-1)-len(dev)*d[a] for a in cand}
        work+=len(cand)*(1+max(1,len(cand).bit_length()))
        ranked=sorted(cand,key=lambda a:(-scores[a],a))
        if method=='support':
            return ((ranked[0],) if ranked and scores[ranked[0]]>0 else ()),work
        best,value=(),0
        for a in ranked:
            dd,_,w=solve(facts,rules,ix,(a,)); work+=w+len(dev)
            v=horizon*sum(d[g]-dd[g] for g in dev)-len(dev)*d[a]
            if v>value or (v==value and best and a<best[0]): best,value=(a,),v
        return best,work
    d, p, w = solve(facts, rules, ix); work += w
    cand = sorted(a for a in nodes-set(facts)-set(dev)-set(held) if a in d)
    counts = Counter()
    for g in dev:
        c,w = occurrences(g,p,rules); counts.update(c); work += w
    scores = {a: horizon*counts[a]*(d[a]-1)-len(dev)*d[a] for a in cand}
    work += len(cand)*(1+max(1,len(cand).bit_length()))
    ranked = sorted(cand, key=lambda a: (-scores[a], a))
    if method == 'frequency':
        return ((ranked[0],) if ranked and scores[ranked[0]] > 0 else ()), work
    roots = held if method == 'oracle' else dev
    if method == 'oracle':
        # Privileged selection sees held-out costs, but uses the same dev menu.
        ix,_,w = cone(rules, by, roots+tuple(cand)); work += w
        d,_,w = solve(facts,rules,ix); work += w
    best, value = (), 0
    for a in (ranked[:4] if method == 'top4' else ranked):
        dd, _, w = solve(facts, rules, ix, (a,)); work += w + len(roots)
        v = horizon*sum(d[g]-dd[g] for g in roots)-len(roots)*d[a]
        if v > value or (v == value and best and a < best[0]): best,value=(a,),v
    return best, work


def term(g, p, rules):
    k,i = p[g]
    if k != 'r': return k+str(i)
    return '(r'+str(i)+' '+' '.join(term(a,p,rules) for a in rules[i][0])+')'


def conjunction(xs, op):
    if len(xs)==1: return xs[0]
    return '('+op+' '+xs[0]+' '+conjunction(xs[1:],op)+')'


def header(facts,rules,ix,roots):
    nodes=sorted(set(facts)|set(roots)|{a for i in ix for a in (*rules[i][0],rules[i][1])})
    binders=['('+' '.join('p'+str(a) for a in nodes)+' : Prop)']
    binders += [f'(f{a} : p{a})' for a in facts]
    binders += ['(r'+str(i)+' : '+' → '.join('p'+str(a) for a in (*rules[i][0],rules[i][1]))+')' for i in ix]
    return 'import Init\nset_option autoImplicit false\nset_option maxRecDepth 4096\ntheorem vad_batch '+' '.join(binders)+' : '+conjunction(['p'+str(a) for a in roots],'And')+' :=\n'


def emit(facts,rules,ix,roots,cached):
    _,p,_=solve(facts,rules,ix); _,pp,_=solve(facts,rules,ix,cached)
    s=header(facts,rules,ix,roots)
    for a in cached: s+=f'  let c{a} : p{a} := '+term(a,p,rules)+'\n'
    return s+'  '+conjunction([term(g,pp,rules) for g in roots],'And.intro')+'\n#print axioms vad_batch\n'


def audit(s,facts,rules,roots,cached,ix):
    h=header(facts,rules,ix,roots); assert s.startswith(h)
    lines=s[len(h):].splitlines(); assert len(lines)==len(cached)+2
    assert lines[-1]=='#print axioms vad_batch'
    legal={f'f{a}':a for a in facts}; allowed={f'r{i}':rules[i] for i in ix}
    def parse(x):
        tokens=re.findall(r'\(|\)|[A-Za-z_.][A-Za-z_.0-9]*',x)
        assert ''.join(tokens)==re.sub(r'\s+','',x); it=iter(tokens); refs=0
        def rec():
            nonlocal refs
            refs+=1; v=next(it)
            if v!='(': return legal[v]
            op=next(it)
            if op=='And.intro': out=(rec(),rec())
            else:
                args,out=allowed[op]; assert tuple(rec() for _ in args)==args
            assert next(it)==')'; return out
        out=rec(); assert next(it,None) is None; return out,refs
    construction=0
    for a,line in zip(cached,lines):
        prefix=f'  let c{a} : p{a} := '; assert line.startswith(prefix)
        got,refs=parse(line[len(prefix):]); assert got==a; construction+=refs; legal[f'c{a}']=a
    expect=roots[-1]
    for a in reversed(roots[:-1]): expect=(a,expect)
    got,refs=parse(lines[-2]); assert got==expect
    return construction,refs


def run(out, lean=None, count=48, seed_base=67000):
    out.mkdir(parents=True,exist_ok=True); rows=[]; files=[]; checks=0
    for i in range(count):
        regime=REGIMES[i%4]; facts,rules,dev,held,missing=family(seed_base+i,regime); by=index(rules)
        assert not set(dev)&set(held) and not any(a in dev+held for args,h in rules for a in args)
        allix=tuple(range(len(rules))); base,_,_=solve(facts,rules,allix)
        assert base==independent(facts,rules) and missing not in base; checks+=len(base)+1
        libs={m:choose(facts,rules,by,dev,held,m,max(HORIZONS)) for m in ARMS}
        for method,(lib,search) in libs.items():
            dd,_,_=solve(facts,rules,allix,lib)
            assert dd==independent(facts,rules,lib); checks+=len(dd)
            assert not set(lib)&set(dev+held)
            construction=sum(base[a] for a in lib)
            for n in HORIZONS:
                roots=held[:n]; ix0,_,w0=cone(rules,by,roots)
                # Every arm receives identical legal premises: union of the
                # target cone and all caches selected without deployment data.
                common=tuple(sorted(set(ix0)|set(cone(rules,by,tuple(a for m,(l,_) in libs.items() if m!='oracle' for a in l))[0])))
                ix=tuple(sorted(set(common)|set(cone(rules,by,lib)[0])))
                direct=sum(base[g] for g in roots)+n-1; refs=sum(dd[g] for g in roots)+n-1
                dp=sum(1+len(rules[j][0]) for j in ix)
                total=refs+construction+search
                rows.append(dict(family=i,regime=regime,method=method,horizon=n,baseline=direct,refs=refs,construction=construction,selection=search,total=total,dp=dp,baseline_dp=sum(1+len(rules[j][0]) for j in common),cache=lib,closure=n))
                if n==8 and method!='oracle':
                    s=emit(facts,rules,ix,roots,lib)
                    assert audit(s,facts,rules,roots,lib,ix)==(construction,refs)
                    path=out/f'f{i:02d}_{method}.lean'; path.write_text(s)
                    files.append(dict(file=path.name,sha256=sha256(s.encode()).hexdigest(),roots=roots,cache=lib))
    summary=[]
    for regime in REGIMES+('all',):
        for method in ARMS:
            for n in HORIZONS:
                rr=[r for r in rows if r['method']==method and r['horizon']==n and (regime=='all' or r['regime']==regime)]
                b=sum(r['baseline'] for r in rr); t=sum(r['total'] for r in rr)
                bd=b+sum(r['baseline_dp'] for r in rr); td=t+sum(r['dp'] for r in rr)
                summary.append(dict(regime=regime,method=method,horizon=n,baseline=b,total=t,gain=b/t,gain_with_dp=bd/td,profitable=sum(r['total']<r['baseline'] for r in rr),selected=sum(bool(r['cache']) for r in rr),refs=sum(r['refs'] for r in rr),selection=sum(r['selection'] for r in rr)))
    receipt=dict(protocol='VAD-06A',evidence='exact Horn DAG and restricted source audit',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),families=count,seed_base=seed_base,checks=checks,files=len(files),kernel='NOT_RUN',summary=summary,records=rows)
    (out/'manifest.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
    if lean:
        verified=[]
        for f in files:
            start=time.monotonic(); p=subprocess.run(lean+[str((out/f['file']).resolve())],capture_output=True,text=True,timeout=60)
            ok=p.returncode==0 and "'vad_batch' does not depend on any axioms" in p.stdout
            verified.append(dict(file=f['file'],ok=ok,seconds=time.monotonic()-start,stdout=p.stdout,stderr=p.stderr))
            (out/'kernel.json').write_text(json.dumps(verified,indent=2)+'\n')
            if not ok: raise RuntimeError(f['file']+p.stdout+p.stderr)
        receipt['kernel']='PASS'
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--lean',nargs='+'); ap.add_argument('--count',type=int,default=48); ap.add_argument('--seed-base',type=int,default=67000); a=ap.parse_args()
    r=run(a.out,a.lean,a.count,a.seed_base)
    print(json.dumps([s for s in r['summary'] if s['regime']=='all'],indent=2))

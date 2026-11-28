"""CPF-04/05/06: fresh paired semantic audits, exact certificates and matched-call arms."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import comb
import json
import random

FAMILIES = {
    'gate': 'train', 'degree': 'train', 'determinant': 'train',
    'threshold': 'dev', 'witness': 'test', 'polynomial': 'test',
    'quantifier': 'test', 'implication': 'test', 'scope': 'test', 'joint': 'test',
}
LABELS = ('entailed', 'counterexample', 'unresolved')
STAGES = ('direct', 'low1', 'low2', 'refine2')


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(x):
    return sha256(canonical(x).encode()).hexdigest()


def seed_rng(seed, family, i):
    return random.Random(int(digest([seed, family, i]), 16))


def parameters(f, r, positive):
    if f == 'gate':
        o = r.randrange(1, 100000); t = o-r.randrange(0,o+1) if positive else o+r.randrange(1,10000)
        return [o,t]
    if f == 'degree':
        a = r.randrange(1,100); powers = [r.randrange(2,6) for _ in range(r.randrange(2,8))]
        d = a
        for p in powers: d *= p
        return [a,powers,d+r.randrange(0,1000) if positive else d-r.randrange(1,d+1)]
    if f == 'determinant':
        p = r.choice([3,5,7,11,13,17,19,23,29,31,37]); a,b,c,d = [r.randrange(p) for _ in range(4)]
        if positive: b=0; c=r.randrange(p)
        else: b,c = r.randrange(1,p),r.randrange(1,p)
        return [p,a,b,c,d]
    if f == 'threshold':
        ns = [r.randrange(1,10000) for _ in range(r.randrange(3,10))]; m=max(ns)
        return [ns,m+r.randrange(0,1000) if positive else m-r.randrange(1,m+1)]
    if f == 'witness':
        n=r.randrange(8,18); a=sorted(r.sample(range(n),r.randrange(2,n))); e=sorted(r.sample(a,r.randrange(1,len(a))))
        g=set(r.sample(range(n),r.randrange(1,n))); g.update(e)
        if positive: g.update(a)
        else: g.discard(r.choice(sorted(set(a)-set(e))))
        return [n,e,a,sorted(g)]
    if f == 'polynomial':
        p=r.choice([2,3,5,7,11]); n=r.randrange(p+2,p+10); a=[r.randrange(p) for _ in range(n)]
        b=a.copy(); formal=r.choice([False,True]); k=r.randrange(n-p)
        if not formal or not positive:
            v=r.randrange(1,p); b[k+p]=(b[k+p]+v)%p; b[k+1]=(b[k+1]-v)%p
        if not formal and not positive: b[0]=(b[0]+1)%p
        return [p,a,b,formal]
    if f == 'quantifier':
        n,m=r.randrange(4,9),r.randrange(4,9); rows=[[r.randrange(2) for _ in range(m)] for _ in range(n)]
        j=r.randrange(m)
        if positive:
            for row in rows: row[j]=1
        else:
            for col in range(m): rows[r.randrange(n)][col]=0
            # guarantee premise forall rows exists a witness; each row can use a distinct column
            for i,row in enumerate(rows):
                if not any(row): row[i % m]=1
            # if fixing empty rows made a common column, clear it in a row with another one
            for col in range(m):
                if all(row[col] for row in rows):
                    choices=[row for row in rows if sum(row)>1]
                    if not choices: return None
                    choices[0][col]=0
        return [rows]
    if f == 'implication':
        n=r.randrange(5,10); s,t=r.sample(range(n),2)
        if positive:
            edges={(i,j) for i in range(n) for j in range(n) if i!=j and r.randrange(5)==0}
            middle=r.sample([i for i in range(n) if i not in (s,t)],r.randrange(1,min(4,n-1)))
            chain=[s,*middle,t]; edges.update(zip(chain,chain[1:])); edges.discard((s,t))
        else:
            side={s}|set(r.sample([i for i in range(n) if i not in (s,t)],r.randrange(n-1)))
            edges={(i,j) for i in range(n) for j in range(n) if i!=j and not(i in side and j not in side) and r.randrange(3)==0}
        return [n,s,t,sorted(map(list,edges))]
    if f == 'scope':
        n=r.randrange(10,23); required=sorted(r.sample(range(n),r.randrange(2,n-1))); passed=set(r.sample(range(n),r.randrange(1,n)))
        if positive: passed.update(required)
        else: passed.discard(r.choice(required))
        return [n,required,sorted(passed)]
    if f == 'joint':
        # Four disjoint null atoms: both, A only, B only, neither.
        a=[r.randrange(1,10000) for _ in range(4)]; t=a[0]+r.randrange(0,1000) if positive else a[0]-r.randrange(1,a[0]+1)
        return [a,t]
    raise ValueError(f)


def derive(f, x):
    """Exact gold; certificate shape is specified publicly, answer values are not."""
    if f=='gate':
        o,t=x; return o>=t,[o,4*o+2]
    if f=='degree':
        a,powers,t=x
        for p in powers: a*=p
        return a<=t,a
    if f=='determinant':
        p,a,b,c,d=x; v=[(a*d+b*c)%p,(a*d-b*c)%p]; return v[0]==v[1],v
    if f=='threshold':
        ns,t=x; m=max(ns); return m<=t,m
    if f=='witness':
        _,e,a,g=x; v=sorted(set(a)-set(g)); return not v,v
    if f=='polynomial':
        p,a,b,formal=x; c=[i for i in range(len(a)) if a[i]!=b[i]]
        def ev(co,z):
            v=0
            for k in reversed(co): v=(v*z+k)%p
            return v
        d=[z for z in range(p) if ev(a,z)!=ev(b,z)]
        return not (c if formal else d),[c,d]
    if f=='quantifier':
        rows=x[0]; cols=[j for j in range(len(rows[0])) if all(row[j] for row in rows)]; return bool(cols),cols
    if f=='implication':
        n,s,t,edges=x; seen={s}
        while True:
            nxt=seen|{j for i,j in edges if i in seen}
            if nxt==seen: break
            seen=nxt
        return t in seen,sorted(seen)
    if f=='scope':
        _,required,passed=x; v=sorted(set(required)-set(passed)); return not v,v
    if f=='joint':
        a,t=x; return a[0]<=t,[a[0],sum(a)]
    raise ValueError(f)


def question(f,x):
    if f=='gate':
        o,t=x; return f'Only the abstract integer constraints O={o}, O<=A<=4O+2 are given. Is A>={t} forced in every compatible model? Certificate: [minimum A, maximum A].'
    if f=='degree':
        a,p,t=x; return f'Over a field start from x^{a}. Successively raise the result to powers {p}. Is the formal degree <= {t}? Certificate: exact degree.'
    if f=='determinant':
        p,a,b,c,d=x; return f'Over F_{p} take matrix [[{a},{b}],[{c},{d}]]. Are its permanent and determinant equal? Certificate: [permanent, determinant] as least nonnegative residues.'
    if f=='threshold':
        ns,t=x; return f'Each index i has R(i,n) iff n >= threshold[i], with thresholds {ns}. Does N={t} work uniformly? Certificate: least uniform N.'
    if f=='witness':
        n,e,a,g=x; return f'In abstract universe 0..{n-1}, exact witnesses E={e}, approximate witnesses A={a}, good witnesses G={g}. E is contained in A and in G. Is A contained in G? Certificate: sorted list of elements of A outside G. This is a finite model, not an assertion about circuit classes.'
    if f=='polynomial':
        p,a,b,formal=x; mode='formal polynomials' if formal else 'functions on the field'; return f'Over F_{p}, two polynomials have ascending coefficient arrays {a} and {b}. Are they equal as {mode}? Certificate: [sorted indices of differing coefficients, sorted field elements with differing evaluations].'
    if f=='quantifier':
        return f'Rows of the relation R (1 means true) are {x[0]}. Is there a single column j with R(i,j) for every row i? Certificate: sorted list of such zero-based columns.'
    if f=='implication':
        n,s,t,edges=x; return f'Boolean variables are 0..{n-1}. Each directed edge i->j in {edges} asserts i implies j. Does setting {s} true force {t} true in every satisfying assignment? Certificate: sorted vertices reachable from {s}, including itself.'
    if f=='scope':
        n,req,passed=x; return f'Claim authorization under this evidence contract requires every obligation in {req}; the packet supplies certificates only for {passed}, from IDs 0..{n-1}. Is authorization established by the packet? If missing evidence, use unresolved, never infer falsity. Certificate: sorted missing required IDs.'
    if f=='joint':
        a,t=x; return f'Conditional on a false claim, four atom weights for both accept, only A, only B, neither are {a}. Normalize by total weight. Is joint acceptance at most {t}/sum(weights)? Certificate: [both-accept weight, total weight] (unreduced).'
    raise ValueError(f)


def generate(seed, per_family, split=None, exclude=()):
    if per_family < 2 or per_family % 2: raise ValueError('per-family count must be positive even')
    rows=[]; seen=set(exclude)
    for f,group in FAMILIES.items():
        if split is not None and group!=split: continue
        i=0; made=0
        while made<per_family:
            if i>=1000*per_family: raise ValueError('generator exhausted unique roots')
            positive=made%2==0; x=parameters(f,seed_rng(seed,f,i),positive); i+=1
            if x is None: continue
            ident=digest([f,x]);
            if ident in seen: continue
            ok,cert=derive(f,x)
            if ok!=positive: continue
            seen.add(ident); made+=1
            rows.append({'id':ident,'family':f,'split':group,'prompt':question(f,x),'parameters':x,
                         'label':'entailed' if ok else ('unresolved' if f=='scope' else 'counterexample'), 'certificate':cert})
    random.Random(int(digest([seed,'order']),16)).shuffle(rows)
    return rows


def export(rows):
    return ([{k:r[k] for k in ('id','prompt')} for r in rows],
            [{k:r[k] for k in ('id','family','split','label','certificate','parameters')} for r in rows])


def strip_fence(text):
    """Remove surrounding whitespace and at most one Markdown code fence around the whole reply."""
    t=(text or '').strip()
    if t.startswith('```') and t.endswith('```') and len(t)>=6:
        body=t[3:-3]
        first,_,rest=body.partition('\n')
        t=(rest if first.strip().lower() in ('','json') else body).strip()
    return t


def parse(text, strict=False):
    """Registered parse (amended before the dev preflight): the whole reply, optionally inside one
    code fence, must be a JSON object with exactly label and certificate. strict=True disallows the
    fence; both are reported."""
    try:
        r=json.loads(text if strict else strip_fence(text))
        if not isinstance(r,dict) or set(r)!= {'label','certificate'} or r['label'] not in LABELS: return None
        return r
    except (ValueError,TypeError): return None


def agree(a,b):
    return a if a is not None and b is not None and canonical(a)==canonical(b) else None


def arms(calls, models):
    """Input keyed by (model,stage); parsed answers and measured call usage."""
    def ans(m,s): return parse(calls[m,s]['text'])
    def result(answer, members):
        records=[calls[k] for k in members]
        return {'answer':answer,'completion':sum(r['completion'] for r in records),
                'prompt':sum(r['prompt'] for r in records),'seconds':sum(r['seconds'] for r in records)}
    out={}
    for m in models:
        d,l1,l2,r= [(m,s) for s in STAGES]
        a,b,c,e=[ans(*k) for k in (d,l1,l2,r)]
        for name,answer,members in [('direct',a,[d]),('low',b,[l1]),('low2',c,[l2]),
           ('independent',agree(b,c),[l1,l2]),('refine',e,[l1,r]),('serial_agree',agree(b,e),[l1,r])]:
            out[m+'/'+name]=result(answer,members)
    if len(models)==2:
        a,b=models; out['cross/agree']=result(agree(ans(a,'low1'),ans(b,'low1')),[(a,'low1'),(b,'low1')])
    return out


def score(gold, predictions):
    """Exact root-paired metrics; require complete predictions for every compared arm."""
    by_id={r['id']:r for r in gold};
    if not gold or len(by_id)!=len(gold) or set(by_id)!=set(predictions): raise ValueError('incomplete or duplicate roots')
    names=sorted(next(iter(predictions.values())))
    if not names or any(set(p)!=set(names) for p in predictions.values()): raise ValueError('incomplete arm panel')
    def metric(ids,arm):
        n=len(ids); counts=Counter(); cost=Counter()
        for i in ids:
            g=by_id[i]; p=predictions[i][arm]; a=p['answer']; counts['n']+=1
            counts['covered']+=a is not None
            counts['label_correct']+=a is not None and a['label']==g['label']
            counts['certified_correct']+=a is not None and a['label']==g['label'] and canonical(a['certificate'])==canonical(g['certificate'])
            counts['false_roots']+=g['label']=='counterexample'
            counts['false_authorized']+=g['label']=='counterexample' and a is not None and a['label']=='entailed'
            counts['unresolved_roots']+=g['label']=='unresolved'
            counts['unresolved_authorized']+=g['label']=='unresolved' and a is not None and a['label']=='entailed'
            cost.update({k:p[k] for k in ('completion','prompt','seconds')})
        return {'counts':dict(counts),'cost':dict(cost)}
    groups=defaultdict(list)
    for r in gold: groups[r['family']].append(r['id'])
    def pair(ids,a,b):
        pa,pb,j,n=0,0,0,0; wins=losses=0
        for i in ids:
            g=by_id[i]
            x,y=(predictions[i][k]['answer'] for k in (a,b))
            def correct(v): return v is not None and v['label']==g['label'] and canonical(v['certificate'])==canonical(g['certificate'])
            wins+=correct(x) and not correct(y); losses+=correct(y) and not correct(x)
            if g['label']!='counterexample': continue
            u=x is not None and x['label']=='entailed'; v=y is not None and y['label']=='entailed'
            pa+=u; pb+=v; j+=u and v; n+=1
        discordant=wins+losses
        p=min(Fraction(1),2*Fraction(sum(comb(discordant,k) for k in range(min(wins,losses)+1)),2**discordant))
        return {'certified_a_only':wins,'certified_b_only':losses,'certified_delta':str(Fraction(wins-losses,len(ids))),
                'mcnemar_exact_two_sided':str(p),'null_n':n,'a_false':pa,'b_false':pb,'joint_false':j,
                'joint_minus_product':str(Fraction(j,n)-Fraction(pa*pb,n*n)) if n else None}
    pairs={}
    for a,b in product(names,names):
        if a>=b: continue
        pairs[a+'|'+b]={**pair(list(by_id),a,b),'by_family':{f:pair(ids,a,b) for f,ids in sorted(groups.items())}}
    return {'roots':len(gold),'arms':{a:metric(list(by_id),a) for a in names},
            'families':{f:{a:metric(ids,a) for a in names} for f,ids in sorted(groups.items())},'paired':pairs}

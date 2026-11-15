"""BPD-LG-02: source-first, reachable-obligation, finite-model curriculum.

Four tactic witnesses are generated independently of their withheld labels.
A row is labelled by reachability/equality connectivity of its actual source
hypotheses, not by a generator toggle. The negative certificate is a finite
semantic interpretation checked independently by evaluating every hypothesis.
No generated model has been trained or run here.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random

SCHEMA = 'BPD-LG-02-v1'
SEED = 2026111518
FAMILIES = ('exact', 'rw', 'rcases', 'induction')
DEPTHS = (3, 4, 5, 6)
SHAPES = tuple(range(6))
SPLITS = ('train', 'dev', 'test')


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def digest(value) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def node(kind: str, i: int) -> str:
    return ('X' if kind == 'rw' else 'P') + str(i)


def directed_path(start: str, target: str, edges: list[tuple[str,str]]) -> list[tuple[str,str]] | None:
    """Independent shortest-path witness search for explicit proof terms."""
    pending=deque([start]); predecessor={start:None}
    while pending:
        cur=pending.popleft()
        if cur==target:
            path=[]
            while predecessor[cur] is not None:
                prev=predecessor[cur]
                path.append((prev,cur));cur=prev
            return path[::-1]
        for a,b in edges:
            if a==cur and b not in predecessor:
                predecessor[b]=cur;pending.append(b)
    return None


def graph_spec(family: str, depth: int, shape: int, nuisance: int, variant: int) -> dict:
    """Return graph with binder roles independent of theorem/variable names.

    The first `depth` edges form a potential source-to-goal chain. A changed
    *interior* edge is redirected to a fresh decoy node, preserving the number
    and type of premises. Distractors also include reachable and dead-end
    implications/equalities. Only traversal determines the label.
    """
    if family not in FAMILIES or depth not in DEPTHS or shape not in SHAPES or nuisance not in (0,1) or variant not in (0,1):
        raise ValueError('unsupported family/depth/shape/nuisance/variant')
    rng = random.Random(SEED + 100003*FAMILIES.index(family) + 1009*depth + 137*shape + 17*nuisance)
    # Different decoy graph sizes make each structural shape distinct, including
    # between train and held-out shape families.
    n_decoys = 4 + shape*2
    main = [node(family, i) for i in range(depth+1)]
    aux = ['D'+str(i) for i in range(n_decoys)]
    cut = 1 + ((shape+depth) % (depth-2))  # strictly interior edge
    # Shuffle the polarity of the counterfactual variant, so variant=0 is not
    # uniformly positive (and the variant is never model-visible anyway).
    intact_variant = (shape + depth + FAMILIES.index(family)) % 2
    intact = (variant == intact_variant)
    use_detour = (shape + depth) % 2 == 1
    core = []
    for i in range(depth):
        # Half the structural roots need an alternate bridge; the main chain
        # is absent for positive as well as negative examples in that stratum.
        dst = aux[-1] if i == cut and (use_detour or not intact) else main[i+1]
        core.append((main[i], dst))
    # The dead-end branch into the goal has no incoming path from the start.
    distractors = [(main[0], aux[0]), (main[0], aux[1])]
    distractors += [(aux[j], aux[j+1]) for j in range(1, n_decoys-3)]
    distractors.append((aux[-2], main[-1]))
    # A detour requires a distinct bridge rule, but only on the positive.
    # Replacing that rule by a dead-end premise is a one-edge counterfactual.
    distractors.append((aux[-1], main[cut+1]) if (use_detour and intact)
                       else (aux[-1], aux[0]))
    # Nuisance is a real typed rule that can fire, but it does not bridge the
    # missing source-to-goal cut. No dummy unreferenced binder is introduced.
    distractors.append((main[0], aux[1]) if nuisance else (aux[-3], aux[0]))
    all_edges = core + distractors
    order = list(range(len(all_edges)))
    rng.shuffle(order)
    edges = [all_edges[i] for i in order]
    edge_ids = ['h'+str(i) for i in range(len(edges))]
    # Kernel witnesses use actual dependency paths, including detours.
    walk = directed_path(main[0], main[-1], edges) if intact else None
    witness_indices = [next(j for j,e in enumerate(edges) if e==link) for link in walk] if walk is not None else None
    public_names={role:'v'+format(rng.randrange(1<<44),'011x') for role in main+aux}
    assert len(set(public_names.values()))==len(public_names)
    sig = {'family': family, 'depth': depth, 'main_count': len(main),
           'decoy_count': n_decoys, 'edges': sorted(edges),
           'source': main[0], 'target': main[-1],
           'loop': family == 'induction'}
    return {'family':family,'depth':depth,'shape':shape,'nuisance':nuisance,
            'variant':variant, 'main':main,'aux':aux,'cut':cut,'public_names':public_names,
            'edges':edges,'edge_ids':edge_ids,'witness_indices':witness_indices,'use_detour':use_detour,
            'signature':sig, 'alpha_hash':digest(sig)}


def reachability(start: str, edges: list[tuple[str,str]]) -> set[str]:
    todo = [start]
    visited = {start}
    out: dict[str,list[str]] = defaultdict(list)
    for src,dst in edges:
        out[src].append(dst)
    while todo:
        cur = todo.pop()
        for nxt in out[cur]:
            if nxt not in visited:
                visited.add(nxt)
                todo.append(nxt)
    return visited


def connectivity(start: str, edges: list[tuple[str,str]]) -> set[str]:
    undirected = edges + [(b,a) for a,b in edges]
    return reachability(start, undirected)


def semantic_label(spec: dict) -> bool:
    edges=spec['edges']
    reachable = (connectivity(spec['main'][0],edges) if spec['family']=='rw'
                 else reachability(spec['main'][0],edges))
    return spec['main'][-1] in reachable


def model(spec: dict) -> dict:
    fam=spec['family']
    nodes = spec['main']+spec['aux']
    reachable = (connectivity(spec['main'][0],spec['edges']) if fam=='rw'
                 else reachability(spec['main'][0],spec['edges']))
    if fam=='rw':
        # Union-connectivity components are given distinct Nat values; source
        # and goal are in different components exactly for negative cases.
        comps = {}
        values={}
        for x in nodes:
            c=frozenset(connectivity(x,spec['edges']))
            if c not in comps: comps[c]=len(comps)
            values[x]=comps[c]
        result={'domain':'Nat','assignments':values,'goal_false':values[nodes[0]]!=values[spec['main'][-1]]}
    else:
        # Induction predicates are constant across Nat: P_i(n) is either True
        # or False. The recurrence is satisfied because its head Pd is False.
        values={x:x in reachable for x in nodes}
        result={'domain':'Nat -> Prop' if fam=='induction' else 'Prop',
                'assignments':values,'goal_false':not values[spec['main'][-1]]}
    if not result['goal_false']:
        return {}
    return result


def verify_model(spec: dict, witness: dict) -> bool:
    if semantic_label(spec):
        return witness == {}
    assignments=witness.get('assignments',{})
    if set(assignments) != set(spec['main']+spec['aux']):
        return False
    if spec['family']=='rw':
        ok=all(assignments[a]==assignments[b] for a,b in spec['edges'])
        return ok and assignments[spec['main'][0]]!=assignments[spec['main'][-1]]
    ok=bool(assignments[spec['main'][0]])
    ok=ok and all(not assignments[a] or assignments[b] for a,b in spec['edges'])
    if spec['family']=='induction':
        # For every Nat n, Pd(n) implies P0(n+1). Both are constant predicates.
        ok=ok and (not assignments[spec['main'][-1]] or assignments[spec['main'][0]])
    return ok and not assignments[spec['main'][-1]]


def edge_expr(fam: str, a: str, b: str) -> str:
    if fam=='rw': return f'{a} = {b}'
    if fam=='induction': return f'∀ n : Nat, {a} n → {b} n'
    return f'{a} → {b}'


def chain_term(spec: dict, start_term: str, index_term: str='') -> str:
    inner=start_term
    for step in spec['witness_indices']:
        h=spec['edge_ids'][step]
        inner = f'({h} {index_term} {inner})' if spec['family']=='induction' else f'({h} {inner})'
    return inner


def right_conj(parts: list[str]) -> str:
    if len(parts)==1: return '('+parts[0]+')'
    return '(('+parts[0]+') ∧ '+right_conj(parts[1:])+')'


def source(spec: dict, name: str) -> tuple[str, str|None]:
    family=spec['family']; nodes=spec['main']+spec['aux']; edges=spec['edges']
    render=lambda n:spec.get('public_names',{}).get(n,n)
    names=' '.join(render(n) for n in nodes)
    if family=='rw':
        header=f'theorem {name} ({names} : Nat)'
    elif family=='induction':
        header=f'theorem {name} ({names} : Nat → Prop)'
    else:
        header=f'theorem {name} ({names} : Prop)'
    if family=='rcases':
        # Bundle contains shuffled real and decoy edges so deconstruction
        # must recover the actual dependency order.
        bundle=right_conj([edge_expr(family,render(a),render(b)) for a,b in edges])
        header+=f' (hs : {render(spec["main"][0])}) (bundle : {bundle})'
    else:
        if family!='rw': header+=f' (hs : {render(spec["main"][0])}' + (' 0)' if family=='induction' else ')')
        for h,(a,b) in zip(spec['edge_ids'],edges):
            header+=f' ({h} : {edge_expr(family,render(a),render(b))})'
    if family=='induction':
        header+=f' (hloop : ∀ n : Nat, {render(spec["main"][-1])} n → {render(spec["main"][0])} (Nat.succ n))'
        goal=f'∀ n : Nat, {render(spec["main"][-1])} n'
    elif family=='rw':
        goal=f'{render(spec["main"][0])} = {render(spec["main"][-1])}'
    else:
        goal=render(spec['main'][-1])
    declaration=header+' : '+goal+' := by'
    if not semantic_label(spec):
        return declaration, None
    if family=='exact':
        script='  exact '+chain_term(spec,'hs')
    elif family=='rw':
        # The chain is the unique witness despite shuffled decoys.
        path=directed_path(spec['main'][0],spec['main'][-1],spec['edges'])
        assert path is not None
        index_by_edge={e:i for i,e in enumerate(spec['edges'])}
        lines=['  calc']
        for i,(a,b) in enumerate(path):
            lines.append(f'    {render(a) if i==0 else "_"} = {render(b)} := by rw [{spec["edge_ids"][index_by_edge[a,b]]}]')
        script='\n'.join(lines)
    elif family=='rcases':
        n=len(edges)
        # Each rcases step peels one piece of the nested conjunction. The last
        # binder is a rule itself, with no further destructuring.
        lines=[]
        rest='bundle'
        for i in range(n-1):
            tail=f'tail{i}'
            lines.append(f'  rcases {rest} with ⟨{spec["edge_ids"][i]}, {tail}⟩')
            rest=tail
        lines.append(f'  have {spec["edge_ids"][-1]} := {rest}')
        lines.append('  exact '+chain_term(spec,'hs'))
        script='\n'.join(lines)
    else:
        base=chain_term(spec,'hs','0')
        step=chain_term(spec,'(hloop n ih)','(Nat.succ n)')
        script=('  intro n\n  induction n with\n'
                f'  | zero =>\n      exact {base}\n'
                f'  | succ n ih =>\n      exact {step}')
    return declaration, script


def refutation_certificate(spec: dict, name: str) -> str | None:
    """A constructively checked closed refutation of an invalid statement.

    Premises are built from True.intro, False.elim, And.intro and rfl, so the
    negative witnesses do not require Classical.choice or propext.
    """
    if semantic_label(spec): return None
    declaration,_=source(spec,name)
    statement=declaration.removesuffix(' := by')
    fam=spec['family']
    if fam=='induction':
        head,tail=statement.rsplit(' : ∀ n : Nat, ',1)
        goal='∀ n : Nat, '+tail
    else:
        head,goal=statement.rsplit(' : ',1)
    binders=head.removeprefix('theorem '+name+' ')
    assignments=model(spec)['assignments']
    nodes=spec['main']+spec['aux']
    if fam=='rw':
        vals=[str(assignments[n]) for n in nodes]
    elif fam=='induction':
        vals=[f'(fun _ : Nat => {"True" if assignments[n] else "False"})' for n in nodes]
    else:
        vals=['True' if assignments[n] else 'False' for n in nodes]

    def term_for_arrow(a: str, b: str) -> str:
        if fam=='rw':
            assert assignments[a]==assignments[b]
            return 'rfl'
        if assignments[b]:
            return '(fun _ _ => True.intro)' if fam=='induction' else '(fun _ => True.intro)'
        assert not assignments[a]
        return '(fun _ h => False.elim h)' if fam=='induction' else '(False.elim)'

    terms=[term_for_arrow(a,b) for a,b in spec['edges']]
    if fam=='rcases':
        def and_term(parts: list[str]) -> str:
            if len(parts)==1: return parts[0]
            return '(And.intro '+parts[0]+' '+and_term(parts[1:])+')'
        assumptions=['True.intro', and_term(terms)]
    elif fam=='rw':
        assumptions=terms
    else:
        assumptions=['True.intro']+terms
    if fam=='induction':
        # The constant interpretation makes P0 true and Pd false.
        assumptions+=['(fun _ _ => True.intro)']
    app='hall '+' '.join(vals+assumptions)
    if fam=='induction': app='('+app+') 0'
    if fam=='rw':
        pair=f'{assignments[spec["main"][0]]} = {assignments[spec["main"][-1]]}'
        body=f'  intro hall\n  have absurd_eq : {pair} := {app}\n  cases absurd_eq'
    else:
        body=f'  intro hall\n  have hFalse : False := {app}\n  exact hFalse'
    return f'theorem neg_{name} : ¬ (∀ {binders}, {goal}) := by\n{body}'


def group_signature(family: str, depth: int, shape: int) -> dict:
    # Ignore labels/nuisance while grouping all intervention variants of one
    # structural recipe. Contains no root index or theorem names.
    s=graph_spec(family,depth,shape,0,0)
    return {'family':family,'depth':depth, 'decoy_count':len(s['aux']),
            'edge_count':len(s['edges']), 'loop':family=='induction'}


def assign_groups() -> dict[tuple[str,int,int],str]:
    output={}
    for family in FAMILIES:
        for depth in DEPTHS:
            scored=sorted((digest(group_signature(family,depth,shape)),shape) for shape in SHAPES)
            assert len({h for h,_ in scored}) == len(SHAPES)
            for i,(_,shape) in enumerate(scored):
                output[family,depth,shape]='train' if i<4 else ('dev' if i==4 else 'test')
    return output


def roster() -> list[dict]:
    groups=assign_groups()
    rows=[]
    for family in FAMILIES:
      for depth in DEPTHS:
       for shape in SHAPES:
        for nuisance in (0,1):
         for variant in (0,1):
          spec=graph_spec(family,depth,shape,nuisance,variant)
          label=semantic_label(spec)
          cm=model(spec)
          assert label or verify_model(spec,cm)
          assert label == (spec['witness_indices'] is not None)
          group_hash=digest(group_signature(family,depth,shape))
          cid='bpd2_'+digest((family,depth,shape,nuisance,variant))[:16]
          decl,proof=source(spec,'thm_'+cid)
          if label: assert proof is not None
          rows.append({
              'schema':SCHEMA,'case_id':cid,'split':groups[family,depth,shape],
              'root_group':group_hash, 'alpha_hash':spec['alpha_hash'],
              'family':family,'structural_depth':depth,
              'public':{'case_id':cid,'lean_statement':decl.removesuffix(' := by')},
              'host_only':{'solvable':label,'countermodel':cm if not label else None,
                           'proof_witness':proof,'source_edges':spec['edges'],
                           'source_node':spec['main'][0],'target_node':spec['main'][-1],
                           'cut_edge':spec['cut'] if not label else None,
                           'model_signature':spec['signature'], 'public_names':spec['public_names']},
              'kernel_status':'pending_independent_lean',
          })
    return rows


def audit(rows: list[dict]) -> dict:
    if len(rows)!=384 or len({r['case_id'] for r in rows})!=len(rows):
        raise AssertionError('roster cardinality or duplicated case ID')
    by_split={s:[r for r in rows if r['split']==s] for s in SPLITS}
    if {s:len(rows) for s,rows in by_split.items()}!={'train':256,'dev':64,'test':64}:
        raise AssertionError('split mismatch')
    group_splits=defaultdict(set)
    alpha_splits=defaultdict(set)
    labels=defaultdict(int)
    for row in rows:
        group_splits[row['root_group']].add(row['split'])
        alpha_splits[row['alpha_hash']].add(row['split'])
        labels[row['split'],row['host_only']['solvable']]+=1
        # The learner never receives the label or generator toggle in public.
        assert set(row['public'])=={'case_id','lean_statement'}
        assert not any(key in row['public'] for key in ('critical','nuisance','solvable','variant'))
    if any(len(v)>1 for v in group_splits.values()):
        raise AssertionError('structural groups leak between splits')
    if any(len(v)>1 for v in alpha_splits.values()):
        raise AssertionError('alpha-normalized statements leak between splits')
    # Each root/group is two positive and two negative matched observations.
    for group in group_splits:
        r=[x for x in rows if x['root_group']==group]
        if len(r)!=4 or sum(x['host_only']['solvable'] for x in r)!=2:
            raise AssertionError('root matched contrasts missing')
    return {'cases':len(rows),'split_counts':{s:len(by_split[s]) for s in SPLITS},
            'positive_cases':sum(r['host_only']['solvable'] for r in rows),
            'negative_finite_models':sum(not r['host_only']['solvable'] for r in rows),
            'distinct_alpha_hashes':len(alpha_splits),
            'distinct_root_groups':len(group_splits),
            'cross_split_alpha_collisions':sum(len(v)>1 for v in alpha_splits.values()),
            'cross_split_group_collisions':sum(len(v)>1 for v in group_splits.values()),
            'labels':{s:{'positive':labels[s,True],'negative':labels[s,False]} for s in SPLITS},
            'claim_boundary':'source-first synthetic Horn/equality curriculum, no neural training; kernel separately audited'}


def export(out: Path) -> dict:
    rows=roster()
    report=audit(rows)
    out.mkdir(parents=True,exist_ok=True)
    for s in SPLITS:
        subset=[r for r in rows if r['split']==s]
        # Publish model inputs without scorer labels or generator mechanics.
        (out/f'{s}_public.jsonl').write_text(
            ''.join(canonical(r['public'])+'\n' for r in subset))
        # Host-only evidence is a separate file; only trusted scoring code
        # may load this label/countermodel/proof manifest.
        (out/f'{s}_host.jsonl').write_text(
            ''.join(canonical({k:v for k,v in r.items() if k!='public'})+'\n' for r in subset))
        proofs=[]
        negative_certs=[]
        for r in subset:
            if r['host_only']['solvable']:
                proof=r['host_only']['proof_witness']
                proofs.append(r['public']['lean_statement']+' := by\n'+proof)
            else:
                spec=r['host_only']['model_signature']
                # The graph can be reconstructed from the host-only structure
                # without the generator's hidden polarity flag.
                edges=[tuple(e) for e in r['host_only']['source_edges']]
                role_nodes=[f'X{i}' if r['family']=='rw' else f'P{i}' for i in range(r['structural_depth']+1)]
                decoys=[f'D{i}' for i in range(spec['decoy_count'])]
                complete={'family':r['family'],'main':role_nodes,'aux':decoys,'edges':edges,
                          'edge_ids':['h'+str(i) for i in range(len(edges))],
                          'witness_indices':None,'public_names':r['host_only']['public_names']}
                neg=refutation_certificate(complete,'thm_'+r['case_id'])
                if neg is None: raise AssertionError('missing negative proof witness')
                negative_certs.append(neg)
        (out/f'{s}_positives.lean').write_text(
            '/- BPD-LG-02 generated positive proof candidates; Lean 4.19.0 -/\n\n'+
            '\n\n'.join(proofs)+'\n')
        (out/f'{s}_refutations.lean').write_text(
            '/- BPD-LG-02 closed negative certificates; Lean 4.19.0 -/\n\n'+
            '\n\n'.join(negative_certs)+'\n')
    report.update({'schema':SCHEMA,'seed':SEED,
                   'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(out.glob('*.jsonl'))+sorted(out.glob('*.lean'))}})
    (out/'manifest.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(export(a.out),sort_keys=True))


if __name__=='__main__': main()

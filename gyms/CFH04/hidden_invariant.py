"""CFH-04: exact finite identification of hidden graph-invariant routes.
Public development only. Python 3.10+, NetworkX. No trained model.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from itertools import combinations
from math import comb, log2
import hashlib
import json
from pathlib import Path
import random
import networkx as nx

INVARIANTS = ('independence', 'clique', 'matching', 'chromatic', 'domination')
TRANSFORMS = ('identity', 'complement', 'delete0')
ROUTES = tuple((t, i) for t in TRANSFORMS for i in INVARIANTS)
# Complement exchanges independence and clique exactly, for every graph.
ALIASES = {('complement','independence'): ('identity','clique'),
           ('complement','clique'): ('identity','independence')}
CLASSES = tuple(r for r in ROUTES if r not in ALIASES)
N = len(CLASSES)
ALL = (1 << N) - 1
BUDGETS = (1, 2, 3, 4)
POLICIES = ('random', 'static_entropy', 'optimal_static', 'adaptive_entropy', 'adaptive_minimax', 'optimal_adaptive')


def graph_tuple(g):
    return len(g), tuple(sorted(tuple(sorted(e)) for e in g.edges()))


def transform(g, t):
    n, edges = g
    if t == 'identity':
        return g
    if t == 'complement':
        return n, tuple(sorted(set(combinations(range(n), 2)) - set(edges)))
    if t == 'delete0':
        return n-1, tuple((i-1,j-1) for i,j in edges if i and j)
    raise ValueError(t)


@cache
def coefficients(g, inv):
    n, edges = g
    adj = [0]*n
    for i,j in edges:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    full = (1 << n)-1
    if inv == 'clique':
        adj = [full ^ (1 << i) ^ a for i,a in enumerate(adj)]
    independent = [True] + [False]*full
    for s in range(1,full+1):
        bit = s & -s
        i = bit.bit_length()-1
        rest = s ^ bit
        independent[s] = independent[rest] and not (adj[i] & rest)
    out = [0]*(n+1)
    if inv in ('independence','clique'):
        for s,ok in enumerate(independent):
            if ok: out[s.bit_count()] += 1
    elif inv == 'domination':
        for s in range(full+1):
            cover = s
            for i in range(n):
                if s >> i & 1: cover |= adj[i]
            if cover == full: out[s.bit_count()] += 1
    elif inv == 'matching':
        @cache
        def rec(s):
            if not s: return (1,)
            bit = s & -s
            i = bit.bit_length()-1
            rest = s ^ bit
            a = list(rec(rest)) + [0]
            for j in range(n):
                if rest & adj[i] & (1 << j):
                    for k,c in enumerate(rec(rest ^ (1 << j))):
                        a[k+1] += c
            return tuple(a[:s.bit_count()//2+1])
        a = rec(full)
        out[:len(a)] = a
    elif inv == 'chromatic':
        @cache
        def partitions(s):
            if not s: return (1,)
            a = [0]*(s.bit_count()+1)
            v = s & -s
            u = s
            while u:
                if u & v and independent[u]:
                    for k,c in enumerate(partitions(s ^ u)): a[k+1] += c
                u = (u-1) & s
            return tuple(a)
        fall = [1]
        for k,c in enumerate(partitions(full)):
            for j,a in enumerate(fall): out[j] += a*c
            nxt = [0]*(len(fall)+1)
            for j,a in enumerate(fall):
                nxt[j] -= k*a
                nxt[j+1] += a
            fall = nxt
    else:
        raise ValueError(inv)
    return tuple(out)


def prediction(g, route):
    # Pad deleted-vertex polynomial to the original order + 1.
    t, inv = route
    a = coefficients(transform(g,t), inv)
    return a + (0,)*(g[0]+1-len(a))


def independent_check(g):
    n, edges = g
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
    for inv in INVARIANTS:
        a = coefficients(g, inv)
        assert len(a) == n+1
        if inv == 'independence':
            assert a[0] == 1 and a[1] == n and a[2] == comb(n,2)-len(edges)
        elif inv == 'clique':
            assert a[0] == 1 and a[1] == n and a[2] == len(edges)
            assert sum(a) == 1+sum(1 for _ in nx.enumerate_all_cliques(G))
        elif inv == 'matching':
            assert a[0] == 1 and a[1] == len(edges)
            assert a[2] == sum(len(set(e+f)) == 4 for e,f in combinations(edges,2))
        elif inv == 'chromatic':
            assert a[n] == 1 and a[n-1] == -len(edges)
            # Independent direct enumeration of proper 3-color assignments.
            from itertools import product
            assert sum(c*3**k for k,c in enumerate(a)) == sum(
                all(colors[i] != colors[j] for i,j in edges)
                for colors in product(range(3), repeat=n))
        else:
            assert a[n] == 1
            assert sum(a) == sum(nx.is_dominating_set(G, s)
                for k in range(n+1) for s in combinations(range(n),k))



@cache
def direct_coefficients(g):
    """Independent enumeration: subsets, edge subsets and set partitions."""
    n, edges = g
    E = set(edges)
    ans = {inv:[0]*(n+1) for inv in INVARIANTS}
    vertices = set(range(n))
    for k in range(n+1):
        for S in combinations(range(n),k):
            pairs = list(combinations(S,2))
            ans['independence'][k] += not any(e in E for e in pairs)
            ans['clique'][k] += all(e in E for e in pairs)
            selected = set(S)
            cover = selected | {j for i,j in E if i in selected} | {i for i,j in E if j in selected}
            ans['domination'][k] += cover == vertices
    for k in range(n//2+1):
        for es in combinations(edges,k):
            ans['matching'][k] += len({v for e in es for v in e}) == 2*k
    # Enumerate partitions by assigning the next vertex to an existing block
    # or a new final block. Count only independent blocks (proper color classes).
    counts = [0]*(n+1)
    def visit(v, blocks):
        if v == n:
            counts[len(blocks)] += 1
            return
        for k,block in enumerate(blocks):
            if all((u,v) not in E for u in block):
                visit(v+1,blocks[:k]+(block+(v,),)+blocks[k+1:])
        visit(v+1,blocks+((v,),))
    visit(0,())
    # Convert counts of partitions into ordinary coefficients using direct
    # elementary symmetric sums of 0..k-1, not the iterative falling recurrence.
    for k,count in enumerate(counts):
        for j in range(k+1):
            import math
            elementary = sum(math.prod(S) for S in combinations(range(k),k-j))
            ans['chromatic'][j] += count*(-1)**(k-j)*elementary
    return {inv:tuple(a) for inv,a in ans.items()}

def make_graph(kind,n,rng):
    seed = rng.randrange(2**31)
    if kind == 'er': return nx.gnp_random_graph(n,rng.uniform(.1,.9),seed=seed)
    if kind == 'tree': return nx.from_prufer_sequence([rng.randrange(n) for _ in range(n-2)])
    if kind == 'bipartite': return nx.bipartite.random_graph(n//2,n-n//2,rng.uniform(.2,.9),seed=seed)
    if kind == 'cycle': return nx.cycle_graph(n)
    if kind == 'complete': return nx.complete_graph(n)
    if kind == 'empty': return nx.empty_graph(n)
    if kind == 'star': return nx.star_graph(n-1)
    if kind == 'path': return nx.path_graph(n)
    raise ValueError(kind)


def decks():
    rng = random.Random(20261125)
    for group,count in (('mixed',32), ('sparse',16), ('restricted',16)):
        for index in range(count):
            if group == 'mixed':
                kinds = ('er','tree','bipartite','cycle','complete','star')
            elif group == 'sparse':
                kinds = ('tree','path','star','cycle','empty','er')
            else:
                # A single small observation graph, useful for explicit ambiguity.
                kinds = (('complete','empty','cycle','path')[index%4],)
            cards = []
            for k in kinds:
                n = rng.randrange(4,8)
                G = make_graph(k,n,rng)
                labels = list(range(n)); rng.shuffle(labels)
                cards.append(graph_tuple(nx.relabel_nodes(G,dict(enumerate(labels)))))
            yield group,index,tuple(cards)


def bits(s):
    while s:
        bit = s & -s
        yield bit.bit_length()-1
        s ^= bit


def partition(values):
    masks = defaultdict(int)
    for i,v in enumerate(values): masks[v] |= 1 << i
    return tuple(sorted(masks.values()))


def refine(cells, parts):
    return tuple(sorted(c & p for c in cells for p in parts if c & p))


def entropy(cells):
    n = sum(c.bit_count() for c in cells)
    return log2(n)-sum(c.bit_count()*log2(c.bit_count()) for c in cells)/n


def singleton_count(cells):
    return sum(c.bit_count()==1 for c in cells)


def solve_deck(cards,seed):
    # All hypothesis-side evaluations are charged separately as a shared setup.
    predictions = [[prediction(g,r) for r in CLASSES] for g in cards]
    for g in cards:
        for alias,canon in ALIASES.items(): assert prediction(g,alias)==prediction(g,canon)
    actions = {}
    for j,g in enumerate(cards):
        for k in range(g[0]+1):
            for mod in (2,3):
                values = tuple(a[k]%mod for a in predictions[j])
                p = partition(values)
                if len(p)>1: actions.setdefault(p,(j,k,mod,values))
    parts = tuple(actions)
    assert parts
    full = (ALL,)
    for p in parts: full = refine(full,p)
    exact_full = partition(tuple(tuple(predictions[j][i] for j in range(len(cards))) for i in range(N)))
    assert all(any(c & e == e for c in full) for e in exact_full)
    @cache
    def splits(s):
        # Multiple probes may induce the same partition on the current version set.
        found={}
        for p in parts:
            sub=tuple(sorted(s & t for t in p if s & t))
            if len(sub)>1: found.setdefault(sub,p)
        return tuple(found.items())
    @cache
    def optimal(s,b):
        if s.bit_count()==1: return 1,0,None
        if not b: return 0,0,None
        opts=splits(s)
        if not opts: return 0,0,None
        # Maximize singleton hits, then minimize summed calls over uniform routes.
        best=(-1,0);best_p=None
        for sub,p in opts:
            values=[optimal(t,b-1) for t in sub]
            candidate=(sum(v[0] for v in values), -s.bit_count()+sum(v[1] for v in values))
            if candidate>best: best,best_p=candidate,p
        return *best,best_p
    # Exact nonadaptive optimum: enumerate fixed query subsets, independent of replies.
    # Early exit is valid only when the full-interface identifiability ceiling is reached.
    static_opt={}; prior_best=();prior_hits=0
    for budget in BUDGETS:
        best_seq=prior_best; best_hits=prior_hits
        if best_hits<singleton_count(full):
            for seq in combinations(parts,budget):
                cells_=(ALL,)
                for p in seq: cells_=refine(cells_,p)
                score=singleton_count(cells_)
                if score>best_hits:
                    best_hits,best_seq=score,seq
                    if best_hits==singleton_count(full):break
        static_opt[budget]=(best_hits,best_seq)
        prior_best,prior_hits=best_seq,best_hits
    # Nonadaptive sequence: maximize entropy of the partition jointly, no answer feedback.
    cells=(ALL,);static=[]
    for _ in BUDGETS:
        p=max(parts,key=lambda p:(entropy(refine(cells,p)), singleton_count(refine(cells,p))))
        static.append(p);cells=refine(cells,p)
    rng=random.Random(seed);random_order=list(parts);rng.shuffle(random_order)
    rows=[];traces=[]
    for budget in BUDGETS:
        for policy in POLICIES:
            hits=0;calls=0;wrong=0;ambiguity=0
            for hidden in range(N):
                s=ALL;trace=[];h=1 << hidden
                for t in range(budget):
                    if s.bit_count()==1 or not splits(s):break
                    if policy=='random':
                        if t>=len(random_order): break
                        p=random_order[t]
                    elif policy=='static_entropy': p=static[t]
                    elif policy=='optimal_static':
                        seq=static_opt[budget][1]
                        if t>=len(seq): break
                        p=seq[t]
                    elif policy=='optimal_adaptive':p=optimal(s,budget-t)[2]
                    elif policy=='adaptive_entropy':p=max(splits(s),key=lambda a:(entropy(a[0]),singleton_count(a[0])))[1]
                    else:p=min(splits(s),key=lambda a:(max(c.bit_count() for c in a[0]),-entropy(a[0])))[1]
                    assert p is not None
                    j,k,mod,values=actions[p]
                    ans=values[hidden]
                    s &= sum(1 << i for i,v in enumerate(values) if v==ans)
                    assert s & h
                    trace.append((j,k,mod,ans))
                hit=s==h
                hits+=hit;calls+=len(trace);wrong+=s.bit_count()==1 and not hit;ambiguity+=s.bit_count()
                traces.append(dict(budget=budget,policy=policy,hidden=hidden,queries=trace,remaining=list(bits(s)),hit=hit))
            if policy=='optimal_adaptive':
                assert hits==optimal(ALL,budget)[0] and calls==-optimal(ALL,budget)[1]
            if policy=='optimal_static': assert hits==static_opt[budget][0]
            assert wrong==0 and hits<=singleton_count(full)
            rows.append(dict(budget=budget,policy=policy,hits=hits,calls=calls,wrong=wrong,remaining=ambiguity))
    return dict(rows=rows,traces=traces,mod_ceiling=singleton_count(full),exact_ceiling=singleton_count(exact_full),mod_classes=len(full),exact_classes=len(exact_full),unique_probes=len(parts),prediction_calls=len(cards)*N,full_vector_best=max(singleton_count(partition(a)) for a in predictions))


def main():
    # Reference controls use direct combinatorial identities, independently of probes.
    for n in range(4,7):
        for G in (nx.path_graph(n),nx.complete_graph(n),nx.empty_graph(n),nx.cycle_graph(n)):
            independent_check(graph_tuple(G))
    records=[];all_traces=[];meta=[];aggregate_signatures=[[] for _ in CLASSES]
    verified=set();comparisons=0
    for i,(group,index,cards) in enumerate(decks()):
        r=solve_deck(cards,70000+i)
        for g in cards:
            for t in TRANSFORMS:
                h=transform(g,t)
                if h not in verified:
                    for inv,a in direct_coefficients(h).items():
                        assert a==coefficients(h,inv)
                        comparisons+=1
                    verified.add(h)
            for j,route in enumerate(CLASSES):aggregate_signatures[j].append(prediction(g,route))
        for row in r.pop('rows'): records.append(dict(group=group,deck=index,**row))
        for trace in r.pop('traces'): all_traces.append(dict(group=group,deck=index,**trace))
        meta.append(dict(group=group,deck=index,cards=cards,**r))
    # Constructive witnesses of distinctness for every pair of canonical routes.
    assert len({tuple(s) for s in aggregate_signatures})==N
    summary=[]
    for group in ('all','mixed','sparse','restricted'):
        for budget in BUDGETS:
            for policy in POLICIES:
                rr=[r for r in records if (group=='all' or r['group']==group) and r['budget']==budget and r['policy']==policy]
                summary.append(dict(group=group,budget=budget,policy=policy,tasks=len(rr)*N,hits=sum(r['hits'] for r in rr),calls=sum(r['calls'] for r in rr),wrong=sum(r['wrong'] for r in rr),mean_remaining=str(Fraction(sum(r['remaining'] for r in rr),len(rr)*N))))
    return dict(evidence='public finite identification over a supplied hypothesis library',independent_coefficient_comparisons=comparisons,distinct_transformed_graphs=len(verified),routes=ROUTES,classes=CLASSES,aliases=[(a,b) for a,b in ALIASES.items()],decks=meta,summary=summary,records=records,traces=all_traces,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

if __name__=='__main__': print(json.dumps(main(),indent=2))

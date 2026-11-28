"""Stronger bounded exact-search controls and permutation-invariant oracle checks."""
from run import *
from statistics import mean

def clique_bound(d,s):
    # A disjoint partition into conflict cliques bounds independent-set weight.
    adj=[0]*len(d.w)
    for i,j in d.edges:adj[i]|=1<<j;adj[j]|=1<<i
    groups=[]
    for i in sorted((i for i in range(len(d.w)) if s>>i&1),key=lambda i:(-d.w[i],-adj[i].bit_count(),i)):
        for k,g in enumerate(groups):
            if g&adj[i]==g:groups[k]|=1<<i;break
        else:groups.append(1<<i)
    return sum(max(d.w[i] for i in range(len(d.w)) if g>>i&1) for g in groups)

def strong(d,budget=32,seconds=None):
    t=perf_counter();deadline=t+seconds if seconds is not None else float('inf')
    g=greedy(d,'degree',budget=budget);best=g['mask'];calls=g['calls'];checks=g['support_checks']
    if calls>=budget:return {**g,'certified_optimal':False}
    s,c=closure(d,(1<<len(d.w))-1);calls+=1;checks+=c
    heap=[(-clique_bound(d,s),s)];seen={s}
    while heap and -heap[0][0]>val(d,best) and calls+2<=budget and perf_counter()<deadline:
        _,s=heapq.heappop(heap);e=conflict(d,s)
        if e is None:
            if val(d,s)>val(d,best):best=s
            continue
        for i in e:
            q,c=closure(d,s&~(1<<i));calls+=1;checks+=c
            if q in seen:continue
            seen.add(q)
            if valid(d,q):
                if val(d,q)>val(d,best):best=q
            else:
                ub=clique_bound(d,q)
                if ub>val(d,best):heapq.heappush(heap,(-ub,q))
    assert valid(d,best)
    return dict(value=val(d,best),mask=best,calls=calls,support_checks=checks,ms=(perf_counter()-t)*1000,certified_optimal=not heap or -heap[0][0]<=val(d,best))

def audit():
    x=json.loads(Path(__file__).with_name('results.json').read_text());rows=[]
    for r in x['rows']:
        d=root(r['family'],r['seed'],r['n']);target=mean(r['arms'][f'dynamic_{s}']['ms'] for s in SEEDS)
        arms={f'strong{k}':strong(d,k) for k in (32,64,128,256)}
        arms['time_matched']=strong(d,100000,seconds=target/1000)
        assert all(valid(d,a['mask']) and a['value']<=r['gold'] and (not a['certified_optimal'] or a['value']==r['gold']) for a in arms.values())
        rows.append(dict(family=r['family'],n=r['n'],seed=r['seed'],gold=r['gold'],target_ms=target,arms=arms))
    return dict(schema='MIC-07/audit/v1',rows=rows,scope='retrospective; time limit checked between branch expansions; soft deadline may overshoot; no oracle information used in search')
if __name__=='__main__':print(json.dumps(audit(),indent=2,sort_keys=True))

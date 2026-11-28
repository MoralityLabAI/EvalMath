"""Retrospective forced include/exclude control; same incumbent and clique bounds."""
from run import *

def include_search(d,cap=CAP,seconds=None):
    t=perf_counter();deadline=t+seconds if seconds is not None else math.inf
    e=Engine(d);s=e.close(e.full);best=e.initializer(s);assert valid(d,best)
    init=e.calls;start=bestval=e.value(best);front=[(-e.upper(s),s,0)];seen={(s,0)};steps=0
    while front:
        if e.calls-init+2>cap or perf_counter()>=deadline:break
        neg,s,forced=front.pop()
        if -neg<=bestval:continue
        deg=e.degrees(s);edge=e.edge(s,deg)
        if edge is None:
            v=e.value(s)
            if v>bestval:best,bestval=s,v
            continue
        i=edge[0];assert not forced>>i&1;steps+=1;children=[]
        for active,req in ((s&~(1<<i),forced),(s&~e.adj[i],forced|1<<i)):
            q=e.close(active)
            if req&~q or (q,req) in seen:continue
            seen.add((q,req));v=e.value(q)
            if not any(e.degrees(q).values()):
                assert valid(d,q)
                if v>bestval:best,bestval=q,v
                continue
            b=e.upper(q)
            if b>bestval:children.append((-b,q,req))
        # Stack visits larger admissible upper bound first.
        front.extend(sorted(children,reverse=True))
    upper=max([bestval]+[-u for u,_,_ in front]);assert valid(d,best)
    return dict(value=bestval,mask=hex(best),upper=upper,certified=upper==bestval,
                init_value=start,init_calls=init,closure_calls=e.calls-init,bound_calls=e.bound_calls,
                support_checks=e.support_checks,expansions=steps,model_calls=0,ms=(perf_counter()-t)*1000)

def audit(raw):
    out=[]
    for r in raw['rows']:
        d=root(r['family'],r['seed'],r['n'])
        a={'include512':include_search(d),'timed_include':include_search(d,cap=8192,seconds=r['learned_time_ms']/1000)}
        lo=max([r['pooled_lower']]+[x['value'] for x in a.values()]);hi=min([r['pooled_upper']]+[x['upper'] for x in a.values()]);assert lo<=hi
        out.append(dict(n=r['n'],family=r['family'],seed=r['seed'],arms=a,pooled_lower=lo,pooled_upper=hi))
    return dict(schema='MIC-08/retrospective-include-exclude/v1',rows=out,scope='soft deadline checked between complete expansions; no exact optimum claim when interval remains open')
if __name__=='__main__':print(json.dumps(audit(json.loads(Path(__file__).with_name('results.json').read_text())),sort_keys=True,indent=2))

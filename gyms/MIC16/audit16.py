"""Independent explicit-world oracle and nonanticipation/receipt audit."""
from mic16 import *
from collections import defaultdict
from statistics import mean


def oracle(d):
    # Alternate representation: posterior is a tuple of world IDs, acquisition
    # is a frozenset, and the Bellman recurrence groups complete outcomes.
    def cost(i):return sum(len(row) for j,row in enumerate(d.entries) if d.supports[i]>>j&1)
    @lru_cache(None)
    def opt(acquired,worlds,budget,allow_probe=True):
        if not budget:return 0
        actions=[('direct',i) for i in range(7) if i not in acquired]+[('cached',i) for i in range(7) if i not in acquired]
        actions += [('compose',i) for i in range(3,7) if i not in acquired and all(j in acquired for j in range(3) if d.supports[i]>>j&1)]
        if allow_probe:actions += [('probe',i) for i in range(3)]
        best=0
        for k,i in actions:
            groups=defaultdict(list)
            for w in worlds:
                if k=='direct':o=(True,cost(i),-1)
                elif k=='compose':o=(True,1+d.supports[i].bit_count()//2,-1)
                elif k=='cached':o=(*d.catalog[i][w],-1)
                else:o=(False,1,(w//(2**i))%2)
                groups[o].append(w)
            if any(c>budget for _,c,_ in groups):continue
            if len(groups)==1 and not next(iter(groups))[0]:continue
            score=0
            for (ok,c,signal),sub in groups.items():
                new=acquired|{i} if ok else acquired
                reward=d.reward[i] if ok else 0
                score+=sum(d.weights[w] for w in sub)*reward+opt(new,tuple(sub),budget-c,allow_probe)
            best=max(best,score)
        return best
    return opt


def reset_rollout(p,w,b):
    """Retrospective ablation: retain acquired set and budget, reset belief at decisions."""
    s=0;m=FULL;reward=0;path=[]
    while b:
        a=p.policy('bayes',s,FULL,b)
        if a<0:break
        k,i=p.actions[a];ok,c,sig=p.observation(k,i,w);o=(ok,c,sig)
        assert max(p.observation(k,i,z)[1] for z in bits(m))<=b
        q=sum(1<<z for z in bits(m) if p.observation(k,i,z)==o)
        path.append([k,i,list(o),m,q]);m=q;b-=c
        if ok:s|=1<<i;reward+=p.d.reward[i]
    return dict(reward=reward,remaining=b,acquired=s,posterior=m,path=path)


def nonanticipation(worlds,b,mode):
    # Same observable acquired set, belief and budget must imply the same
    # selected action (including stop). The reset control is allowed less state.
    choices={}
    for w,r in enumerate(worlds):
        s=0;m=1<<w if mode=='clairvoyant' else FULL;remaining=b
        for k,i,o,prior,post in r['path']:
            state=(s,m,remaining)
            assert choices.setdefault(state,(k,i))==(k,i)
            assert prior==m
            if o[0]:s|=1<<i
            remaining-=o[1];m=post
        state=(s,m,remaining);assert choices.setdefault(state,None) is None
    return len(choices)


def audit(raw):
    t=time.perf_counter();rows=[];paths=states=0;independent=0
    for f in FAMILIES:
        for seed in SEEDS:
            d=make(f,seed);p=Planner(d);alt=oracle(d)
            for r in [r for r in raw['rows'] if r['family']==f and r['seed']==seed]:
                b=r['budget'];arms=r['arms'];assert list(d.weights)==r['prior']
                for mode,a in arms.items():
                    assert sum(d.weights[w]*check(d,w,b,mode,x) for w,x in enumerate(a['worlds']))==a['weighted_reward']
                    paths+=len(a['worlds']);states+=nonanticipation(a['worlds'],b,mode)
                # Full independent solver on one root per family and every budget,
                # plus all primary-budget roots. Compare both probe regimes.
                if b==12 or seed==SEEDS.start:
                    for mode,allow in [('bayes',True),('bayes_no_probe',False)]:
                        assert alt(frozenset(),tuple(range(WORLD)),b,allow)==arms[mode]['weighted_reward'];independent+=1
                worlds=[reset_rollout(p,w,b) for w in range(WORLD)]
                value=sum(d.weights[w]*check(d,w,b,'posterior_reset',x) for w,x in enumerate(worlds))
                assert value<=arms['bayes']['weighted_reward'];states+=nonanticipation(worlds,b,'posterior_reset');paths+=len(worlds)
                rows.append(dict(family=f,seed=seed,budget=b,reset_weighted_reward=value,reset_worlds=worlds))
            alt.cache_clear();p.choice.cache_clear()
        print('audit',f,flush=True,file=__import__('sys').stderr)
    primary=[r for r in raw['rows'] if r['budget']==12]
    controls=('greedy_1','lookahead_2','lookahead_3','lookahead_4')
    regret={k:[F(r['arms']['bayes']['weighted_reward']-r['arms'][k]['weighted_reward'],max(1,r['arms']['bayes']['weighted_reward'])) for r in primary] for k in controls}
    best=min(controls,key=lambda k:mean(regret[k]));gap=mean(regret[best]);hard=sum(x>=F(1,10) for x in regret[best]);gate=gap>=F(1,20) and F(hard,len(primary))>=F(1,5)
    pilot=[]
    for f in FAMILIES:
        rr=[g for r,g in zip(primary,regret[best]) if r['family']==f]
        pilot.append(dict(unit_id=f,paired_effect=str(mean(rr)),sham_effects=['0']))
    spec=dict(schema_version=1,experiment_id='MIC-16-public-headroom',independent_unit='generator lineage (independence unverified)',alpha='1/20',scientific_min_effect='1/20',target_effect='1/10',measurement_resolution='0',sham_quantile='19/20',sham_confidence='19/20',planned_comparisons=1,confirm_units_planned=128,pilot_from_development_only=True,heldout_sealed=False,units_independent=False,pilot=pilot)
    return dict(schema='MIC-16/independent-belief-replay/v1',verified_paths=paths,nonanticipation_state_checks=states,independent_optimum_checks=independent,strongest_fixed=best,mean_relative_regret=str(gap),hard_primary_roots=hard,headroom_gate='PASS_FUTURE_DESIGN_ONLY' if gate else 'FAIL_NO_FITS',rows=rows,elapsed_s=time.perf_counter()-t),spec

if __name__=='__main__':
    p=Path(__file__).parent;out,spec=audit(json.loads((p/'results.json').read_text()))
    (p/'audit_results.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    (p/'preflight_input.json').write_text(json.dumps(spec,sort_keys=True,indent=2)+'\n')
    print({k:v for k,v in out.items() if k!='rows'})

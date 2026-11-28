"""VAD-06B: charged transfer validation for one frozen Horn cache."""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random

import verify_vad_horn as v

REGIMES = ('shared', 'mix75', 'mix50', 'mix25', 'shifted', 'null', 'dominated', 'late_shift')
P, H = 32, 256
SPLITS = {'cal': (78000, 12), 'test': (88000, 24)}
FIXED = ('direct', 'support', 'support_exact')
POLICIES = tuple(('fixed', k, m) for k, m in product((4, 8, 16, 32), (0, 1, 2))) + tuple(('sequential', k, m) for k, m in product((8, 16, 32), (0, 1, 2)))


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
    for j in range(8 + P + H):
        if regime == 'null': hub = None
        elif j < 8 or regime == 'shared' or (regime == 'late_shift' and j < 8+P): hub = hubs[0]
        elif regime in ('shifted', 'late_shift'): hub = hubs[1]
        elif regime.startswith('mix'): hub = hubs[0] if rng.randrange(100) < int(regime[3:]) else hubs[1]
        else: hub = hubs[0]
        private = rng.choice(facts) if regime == 'dominated' else chain(rng.choice(facts), rng.randrange(2, 8))
        goal = rule((private,))
        if hub is not None: rule((hub, rng.choice(facts)), goal)
        targets.append(goal)
    return facts, tuple(rules), tuple(targets[:8]), tuple(targets[8:8+P]), tuple(targets[8+P:])


def probe_prefix(facts, rules, by, probe, cache, base):
    """Counterfactual shortest costs with shared memo; no held queries."""
    memo = dict.fromkeys(facts + cache, 1); work = 0; out = []
    def rec(a):
        nonlocal work
        work += 1
        if a in memo: return memo[a]
        best = float('inf')
        for i in by[a]:
            args, _ = rules[i]; work += 1 + len(args)
            best = min(best, 1 + sum(rec(x) for x in args))
        memo[a] = best; return best
    saving = 0
    for g in probe:
        saving += base[g] - rec(g); work += 1
        out.append((saving, work))
    return out


def gate(policy, cache, selection, build, prefix):
    """Frozen empirical thresholds, not confidence bounds."""
    if not cache: return False, 0, 0
    mode, cap, margin = policy
    sizes = (cap,) if mode == 'fixed' else tuple(k for k in (4, 8, 16, 32) if k <= cap)
    for j, k in enumerate(sizes, 1):
        save, work = prefix[k-1]; work += j  # decision charge
        accept = H*save > k*(selection+build+work+H*margin)
        if accept or k == cap or (mode == 'sequential' and k >= 8 and save == 0):
            return accept, k, work
    raise AssertionError('no decision')


def evaluate(split):
    start, count = SPLITS[split]; rows=[]; checks=0
    for ri, regime in enumerate(REGIMES):
        for i in range(count):
            seed=start+ri*1000+i; facts,rules,dev,probe,held=family(seed,regime); by=v.index(rules)
            assert len(set(dev+probe+held))==8+P+H
            assert not any(a in dev+probe+held for args,_ in rules for a in args)
            ix=tuple(range(len(rules))); base,_,_=v.solve(facts,rules,ix)
            assert base==v.independent(facts,rules); checks+=len(base)
            # Pilot proof workload is identical for every arm. Counterfactual probes are extra.
            baseline=sum(base[g] for g in probe+held)+P+H-2
            direct_held=sum(base[g] for g in held)
            choices={m:v.choose(facts,rules,by,dev,(),m,H) for m in FIXED}
            # Selected caches must be reachable in development cone and never targets.
            devix, nodes,_=v.cone(rules,by,dev)
            for m,(cache,selection) in choices.items():
                assert set(cache)<=nodes-set(facts)-set(dev)
                d,_,_=v.solve(facts,rules,ix,cache)
                assert d==v.independent(facts,rules,cache); checks+=len(d)
                build=sum(base[a] for a in cache); future=direct_held-sum(d[g] for g in held)
                prefix=probe_prefix(facts,rules,by,probe,cache,base) if cache else []
                for k,(s,_) in enumerate(prefix,1):
                    assert s==sum(base[g]-d[g] for g in probe[:k]); checks+=1
                tests=[(m,bool(cache),0,0)]
                if m=='support':
                    tests += [(f'{p[0]}_{p[1]}_{p[2]}',*gate(p,cache,selection,build,prefix)) for p in POLICIES]
                for name,use,k,validation in tests:
                    total=baseline+selection+validation+(build-future if use else 0)
                    rows.append(dict(seed=seed,regime=regime,method=name,baseline=baseline,total=total,selected=use,probe_count=k,validation=validation,selection=selection,construction=build if use else 0,held_savings=future if use else 0,candidate_savings=future,cache=list(cache) if use else [],candidate=list(cache)))
    return rows,checks


def summary(rows):
    out=[]
    for regime in REGIMES+('all',):
        for m in sorted({r['method'] for r in rows}):
            rr=[r for r in rows if r['method']==m and (r['regime']==regime or regime=='all')]
            b,t=[sum(r[k] for r in rr) for k in ('baseline','total')]
            out.append(dict(regime=regime,method=m,n=len(rr),baseline=b,total=t,gain=str(Fraction(b,t)),profitable=sum(r['total']<r['baseline'] for r in rr),selected=sum(r['selected'] for r in rr),zero_savings_selected=sum(r['selected'] and not r['held_savings'] for r in rr),validation=sum(r['validation'] for r in rr),probes=sum(r['probe_count'] for r in rr)))
    return out


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    cal,c=evaluate('cal'); cal_summary=summary(cal)
    eligible=[r for r in cal_summary if r['regime']=='all' and r['method'].startswith(('fixed_','sequential_'))]
    choice=min(eligible,key=lambda r:(r['total'],r['method']))['method']
    freeze=dict(protocol='VAD-06B',splits=SPLITS,chosen_validation=choice,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),parent_sha256=sha256(Path(v.__file__).read_bytes()).hexdigest(),calibration=cal_summary)
    (out/'freeze.json').write_text(json.dumps(freeze,indent=2,sort_keys=True)+'\n')
    test,t=evaluate('test'); report=dict(**freeze,checks=c+t,test_checks=t,test=summary(test),records=test,evidence='exact synthetic reference costs; no new kernel replay')
    (out/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    r=run(a.out); print('chosen',r['chosen_validation'],'checks',r['checks'],'records',len(r['records']))
    for row in r['test']:
        if row['method'] in ('direct','support','support_exact',r['chosen_validation']): print(row)

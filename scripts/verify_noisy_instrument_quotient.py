"""MIT-07 exact receipts and optional non-receipt timing diagnostic."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import runpy
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spiral_ln.evaluation_noisy_instrument_quotient import Quotient, perturbation_bound, approximate_policy_value
from spiral_ln.evaluation_instrument_transfer import optimal_search


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=ROOT/'output/evaluation_instrument_transfer/mit07_v0_1.json')
    p.add_argument('--timing',type=Path)
    a=p.parse_args()
    test='tests/test_noisy_instrument_quotient.py';mod='src/spiral_ln/evaluation_noisy_instrument_quotient.py';oracle='src/spiral_ln/evaluation_instrument_transfer.py';this='scripts/verify_noisy_instrument_quotient.py'
    t=runpy.run_path(str(ROOT/test));checks={}
    for name in sorted(t):
        if name.startswith('test_'):
            t[name]();checks[name]=True
    rows=[];timings=[]
    for i in range(10):
        w,q,b=t['repeated'](9100+i);x=Quotient(w,q,b);y=Quotient(w,q,b,dynamic=False)
        start=time.perf_counter_ns();v=x.solve();dynamic_ns=time.perf_counter_ns()-start
        start=time.perf_counter_ns();u=y.solve();static_ns=time.perf_counter_ns()-start
        start=time.perf_counter_ns();e=optimal_search(w,q,b);expanded_ns=time.perf_counter_ns()-start
        assert v==u==e
        rows.append(dict(seed=9100+i,value=str(v),initial_classes=len(x.start[0]),dynamic_states=x.value.cache_info().currsize,static_states=y.value.cache_info().currsize))
        timings.append(dict(seed=9100+i,dynamic_ms=dynamic_ns/1e6,static_ms=static_ns/1e6,expanded_ms=expanded_ns/1e6))
    pert=[]
    for i in range(32):
        w,q,b=t['noisy'](8500+i);z,r=t['approximate'](w,q);truth=Quotient(w,q,b).solve();approx=Quotient(z,r,b).solve();actual,estimated=approximate_policy_value(w,q,z,r,b);bound,regret=perturbation_bound(w,q,z,r,b)
        pert.append(dict(seed=8500+i,budget=b,truth=str(truth),approx=str(approx),deployed=str(actual),bound=str(bound),regret_bound=str(regret)))
    stress=[]
    for i in range(16):
        w,q,r,b=t['channel_flip'](9900+i);truth=Quotient(w,q,b).solve();actual,estimated=approximate_policy_value(w,q,w,r,b);bound,regret=perturbation_bound(w,q,w,r,b)
        stress.append(dict(seed=9900+i,truth=str(truth),approx=str(estimated),deployed=str(actual),bound=str(bound),regret_bound=str(regret)))
    def regret_of(row):return F(row['truth'])-F(row['deployed'])
    receipt=dict(schema='mit07-v0.1',evidence='algebraic argument plus exact finite synthetic checks',checks=checks,source_sha256={k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest() for k in (test,mod,oracle,this)},noisy_random_roots=48,repeated_roots=10,perturbation_roots=32,dynamic_states=sum(x['dynamic_states'] for x in rows),static_states=sum(x['static_states'] for x in rows),random_perturbation_positive_regrets=sum(regret_of(x)>0 for x in pert),stress_roots=len(stress),stress_positive_regrets=sum(regret_of(x)>0 for x in stress),stress_max_regret=str(max(map(regret_of,stress))),stress_mean_regret=str(sum(map(regret_of,stress))/len(stress)),row_manifest_sha256=hashlib.sha256(json.dumps([rows,pert,stress],sort_keys=True,separators=(',',':')).encode()).hexdigest())
    if a.timing:
        a.timing.with_name('exact_rows.json').write_text(json.dumps(dict(repeated=rows,perturbation=pert,stress=stress),indent=2)+'\n')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    if a.timing:
        a.timing.write_text(json.dumps(dict(rows=timings,median_ms={k:statistics.median(x[k] for x in timings) for k in ('dynamic_ms','static_ms','expanded_ms')},scope='single run CPU; quotient construction excluded; original oracle includes its own input preparation'),indent=2)+'\n')
    print(f'{len(checks)} checks; 58 exact oracle roots, 48 policy perturbation roots (32 random, 16 designed)')

if __name__=='__main__':main()

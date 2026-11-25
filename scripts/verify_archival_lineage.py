"""ADG-06 exact development receipt, with separate post-hoc diagnostic family."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import runpy
from spiral_ln.evaluation_archival_lineage import Oracle, profiles, boundary_profiles, utility, revocation_witness, threshold_witness

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('src/spiral_ln/evaluation_archival_lineage.py','tests/test_archival_lineage.py','scripts/verify_archival_lineage.py','skills/evalmath-mechinterp-power/scripts/preflight.py')
MODES=('stop','independent','map','one','two','macro','no_lineage','full','known')
METRICS=('correct','false','abstain','spent','lineage_queries','exact_lineage_queries','graph_map_correct')


def serial(r):return {**dict(zip(METRICS,map(str,r))),'utility':str(utility(r))}


def family(gen,name,checks):
    rows=[]; sums={m:[F(0)]*len(METRICS) for m in MODES}; pilot=[]; gains={m:[] for m in MODES if m not in ('known','full')}
    for i,p in enumerate(gen()):
        o=Oracle(p); r={m:o.run(m) for m in MODES}; sham=Oracle(p,reverse=True); s=sham.run('full')
        checks['mass_and_budget'] &= all(sum(x[:3])==1 and x[3]<=p.budget for x in r.values())
        checks['full_dominance'] &= all(utility(r['full'])>=utility(x) for m,x in r.items() if m!='known')
        checks['known_graph_upper_bound'] &= utility(r['known'])>=utility(r['full'])
        checks['calibrated_risk_bound'] &= all(x[1]<=F(1,5)*(x[0]+x[1]) for m,x in r.items() if m not in ('independent','map'))
        checks['action_order_utility_invariant'] &= utility(s)==utility(r['full'])
        checks['no_lineage_ablation'] &= r['no_lineage'][4]==0
        checks['known_graph_recovery'] &= r['known'][-1]==1
        for m,x in r.items():sums[m]=[a+b for a,b in zip(sums[m],x)]
        for m in gains:gains[m].append(utility(r['full'])-utility(r[m]))
        pilot.append({'unit_id':f'{name}-{i}','paired_effect':str(utility(r['full'])-utility(r['macro'])),
                      'sham_effects':[str(utility(s)-utility(r['full']))]})
        rows.append({'cell':i,'profile':{k:str(v) for k,v in vars(p).items()},'initial_graph_posterior':list(map(str,o.graph_posterior(o.root))),
                     'scores':{m:serial(x) for m,x in r.items()},'order_sham':serial(s)})
        o.clear();sham.clear()
    n=len(rows)
    spec={'schema_version':1,'experiment_id':f'ADG-06-{name}','independent_unit':'finite parameter cell, not independent sampled world',
          'alpha':'1/20','scientific_min_effect':'1/20','target_effect':'3/20','measurement_resolution':'0',
          'sham_quantile':'19/20','sham_confidence':'19/20','planned_comparisons':7,'confirm_units_planned':240,
          'pilot_from_development_only':True,'heldout_sealed':False,'units_independent':False,'pilot':pilot}
    plan=runpy.run_path(str(ROOT/SOURCES[-1]))['preflight'](spec)
    return {'n_cells':n,'overall':{m:serial([x/n for x in a]) for m,a in sums.items()},
            'full_vs':{m:{'mean_gain':str(sum(ds)/n),'max_gain':str(max(ds)),'strict_wins':sum(x>0 for x in ds)} for m,ds in gains.items()},
            'preflight':plan,'preflight_spec':spec,'rows':rows}


def run():
    checks={k:True for k in ('mass_and_budget','full_dominance','known_graph_upper_bound','calibrated_risk_bound','action_order_utility_invariant','no_lineage_ablation','known_graph_recovery')}
    out={name:family(gen,name,checks) for name,gen in [('ordinary',profiles),('posthoc_boundary',boundary_profiles)]}
    return {'schema':'ADG-06/v1','evidence':'exact finite synthetic development; second grid designed after first result',
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},'checks':checks,
            'revocation_witness':{k:str(v) for k,v in revocation_witness().items()},'threshold_witness':{k:str(v) for k,v in threshold_witness().items()},'families':out}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--output',type=Path,default=ROOT/'output/evaluation_adg/adg_06.json')
    a.add_argument('--compact',action='store_true');p=a.parse_args();result=run()
    if p.compact:
        digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        result['schema']='ADG-06/compact/v1'
        result['families']={name:{'n_cells':f['n_cells'],'rows_sha256':digest(f['rows']),
            'overall_sha256':digest(f['overall']),'preflight':{'decision':f['preflight']['decision']},
            'overall':{k:{'utility':v['utility']} for k,v in f['overall'].items()}} for name,f in result['families'].items()}
    p.output.parent.mkdir(parents=True,exist_ok=True)
    p.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({name:{'n_cells':f['n_cells'],'preflight':f['preflight']['decision'],'overall_utility':{k:float(F(v['utility'])) for k,v in f['overall'].items()}} for name,f in result['families'].items()},indent=2))
    if not all(result['checks'].values()):raise SystemExit(1)


if __name__=='__main__':main()

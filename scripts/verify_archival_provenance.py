"""Regenerate exact ADG-05 development receipt; no learned or sealed evaluation."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import runpy
from spiral_ln.evaluation_archival_provenance import Planner, Result, profiles, revocation_witness, brute_value, likelihood, exhaustive_likelihood

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('src/spiral_ln/evaluation_archival_provenance.py','tests/test_archival_provenance.py','scripts/verify_archival_provenance.py','skills/evalmath-mechinterp-power/scripts/preflight.py')
MODES=('copies','stop','one','two','macro','full')


def serialize(r):
    return {**{k:str(v) for k,v in vars(r).items()},'utility':str(r.utility)}


def run():
    rows=[]; pilot=[]; wins=0; totals={m:Result() for m in MODES}; witnesses=[]
    checks={'probability_conservation':True,'budgets':True,'optimal_dominance':True,'order_sham_utility':True,
            'bayesian_assertion_risk_bound':True,'independent_brute_tree':True,'revocation_witness':True}
    for i,(sources,budget) in enumerate(profiles()):
        p=Planner(sources); scores={m:p.run(budget,m) for m in MODES}
        rev=Planner(sources,order=reversed(range(len(sources))))
        sham=rev.run(budget,'full'); effect=scores['full'].utility-scores['macro'].utility
        checks['probability_conservation'] &= all(r.correct+r.false+r.abstain==1 for r in scores.values())
        checks['budgets'] &= all(r.spent<=budget for r in scores.values())
        checks['optimal_dominance'] &= all(scores['full'].utility>=r.utility for r in scores.values())
        checks['order_sham_utility'] &= sham.utility==scores['full'].utility
        checks['bayesian_assertion_risk_bound'] &= all(scores[m].false<=F(1,5)*(scores[m].correct+scores[m].false) for m in MODES if m!='copies')
        if i in (0,24,40,61): checks['independent_brute_tree'] &= p.run(3,'full').utility==brute_value(sources,3)
        if effect>0:
            wins+=1; witnesses.append({'cell':i,'budget':budget,'utility_gain':str(effect),'full_first':p.value(p.initial,budget,budget)[1],'macro_first':p.macro_value(p.initial,budget)[1]})
        rows.append({'cell':i,'budget':budget,'sources':[{k:str(v) for k,v in vars(s).items()} for s in sources],
                     'scores':{m:serialize(r) for m,r in scores.items()},'order_sham':serialize(sham)})
        pilot.append({'unit_id':f'cell-{i}','paired_effect':str(effect),'sham_effects':[str(sham.utility-scores['full'].utility)]})
        for m,r in scores.items(): totals[m]+=r
        p.clear(); rev.clear()
    n=len(rows)
    w=revocation_witness()
    checks['revocation_witness'] &= w['left_before']==w['right_before']==F(1,2) and w['left_after']==F(1,6) and w['right_after']==F(5,6) and w['left_after_naive_copies']==F(5,6)
    spec={'schema_version':1,'experiment_id':'ADG-05','independent_unit':'synthetic parameter cell (not independent sampled world)',
          'alpha':'1/20','scientific_min_effect':'1/20','target_effect':'3/20','measurement_resolution':'0',
          'sham_quantile':'19/20','sham_confidence':'19/20','planned_comparisons':5,'confirm_units_planned':240,
          'pilot_from_development_only':True,'heldout_sealed':False,'units_independent':False,'pilot':pilot}
    plan=runpy.run_path(str(ROOT/SOURCES[-1]))['preflight'](spec)
    return {'schema':'ADG-05/v1','evidence':'exact finite synthetic parameter census; no model inference or confirmation',
            'n_cells':n,'checks':checks,'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'overall':{m:serialize(r.weighted(F(1,n))) for m,r in totals.items()},'full_strict_wins_over_macro':wins,
            'strict_win_cells':witnesses,'revocation_witness':{k:str(v) for k,v in w.items()},'preflight':plan,'preflight_spec':spec,'rows':rows}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--output',type=Path,default=ROOT/'output/evaluation_adg/adg_05.json')
    a.add_argument('--compact',action='store_true',help='Omit raw rows; retain their canonical SHA-256')
    p=a.parse_args(); result=run(); p.output.parent.mkdir(parents=True,exist_ok=True)
    if p.compact:
        result['rows_sha256']=hashlib.sha256(json.dumps(result.pop('rows'),sort_keys=True,separators=(',',':')).encode()).hexdigest()
        result.pop('preflight_spec')
    p.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('overall','checks','full_strict_wins_over_macro','revocation_witness','preflight')},indent=2))
    if not all(result['checks'].values()): raise SystemExit(1)


if __name__=='__main__': main()

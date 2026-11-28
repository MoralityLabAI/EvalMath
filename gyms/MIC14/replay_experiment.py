"""Run extraction and fitting as separate bounded steps, and emit exact paired pilot inputs."""
import mic14
from mic14 import *
from cost14 import CostReplay,BUDGET
from itertools import combinations


def train_cached(rows,cost=False):
    result=run(rows);dev=[x for x in rows if x['split']=='dev']
    if cost:
        controls={
            'cheapest':[min(range(len(x['obligations'])),key=lambda i:(x['obligations'][i]['bytes'],i)) for x in dev],
            'cap_then_cheap':[min(range(len(x['obligations'])),key=lambda i:(-x['obligations'][i]['cap'],x['obligations'][i]['bytes'],i)) for x in dev],
            'gap_per_byte':[max(range(len(x['obligations'])),key=lambda i:(F(x['obligations'][i]['cap']-x['lower'],x['obligations'][i]['bytes']),-i)) for x in dev],
        }
        for k,v in controls.items():result['predictions'][k]=v;result['metrics'][k]=metrics(dev,v)
    return result


def preflight_input(rows,result):
    # Informative binary accuracy, root-weighted within each generator lineage.
    dev=[r for r in rows if r['split']=='dev'];pred=result['predictions'];groups=[]
    for fam in DEV:
        roots=defaultdict(list)
        for j,r in enumerate(dev):
            if r['root'][0]==fam and r['informative']:roots[tuple(r['root'])].append(j)
        effects=[];shams=[]
        for ids in roots.values():
            def acc(k):return F(sum(dev[j]['gains'][pred[k][j]]==dev[j]['oracle_gain'] for j in ids),len(ids))
            a=[acc(f'ordered_{s}') for s in SEEDS];b=[acc(f'shuffle_{s}') for s in SEEDS]
            effects.append(mean(a)-mean(b));shams.extend(abs(x-y) for arm in (a,b) for x,y in combinations(arm,2))
        if effects:groups.append(dict(unit_id=fam,paired_effect=str(mean(effects)),sham_effects=[str(max(shams))]))
    return dict(schema_version=1,experiment_id='MIC-14-public-replay',independent_unit='generator lineage (independence unverified)',alpha='1/20',scientific_min_effect='1/20',target_effect='1/10',measurement_resolution='0',sham_quantile='19/20',sham_confidence='19/20',planned_comparisons=1,confirm_units_planned=128,pilot_from_development_only=True,heldout_sealed=False,units_independent=False,pilot=groups)


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=('extract','fit','audit'),required=True);p.add_argument('--cost',action='store_true');p.add_argument('--archive',type=Path);p.add_argument('--source-dir',type=Path);p.add_argument('--out',type=Path,default=Path(__file__).parent);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    prefix='cost_' if a.cost else '';data=a.out/(prefix+'obligations.jsonl.gz');res=a.out/(prefix+'results.json');t=time.perf_counter()
    if a.stage=='extract':
        if a.archive is None or a.source_dir is None:p.error('extract requires archive and source-dir')
        mic14.Replay=CostReplay if a.cost else Replay
        rows,summary=mic14.extract(a.archive,a.source_dir)
        with gzip.open(data,'wt',encoding='utf-8') as f:
            for r in rows:f.write(json.dumps(r,separators=(',',':'))+'\n')
        (a.out/(prefix+'extraction.json')).write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print({k:v for k,v in summary.items() if k!='summaries'});return
    rows=[json.loads(x) for x in gzip.open(data,'rt',encoding='utf-8')]
    if a.stage=='fit':
        r=train_cached(rows,a.cost);r['fit_eval_elapsed_s']=time.perf_counter()-t;res.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else:
        r=json.loads(res.read_text());dev=[x for x in rows if x['split']=='dev'];assert len(dev)==r['dev_rows']
        for k,v in r['predictions'].items():assert len(v)==len(dev) and metrics(dev,v)==r['metrics'][k]
        (a.out/(prefix+'preflight_input.json')).write_text(json.dumps(preflight_input(rows,r),sort_keys=True,indent=2)+'\n')
        print('all stored prediction metrics replayed:',len(r['metrics']))
if __name__=='__main__':main()

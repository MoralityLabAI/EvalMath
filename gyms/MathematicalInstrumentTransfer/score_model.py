"""Offline scorer for local-model MIT-06 development transcripts; no network or model calls."""
import argparse,json,hashlib
from pathlib import Path
from collections import defaultdict
from proof_pilot import score


def read(path):
    with path.open() as f:return [json.loads(line) for line in f if line.strip()]

def main(private,responses,out,budget,checkpoint):
    gold=read(private);raw=read(responses);by={};ids={r['row_id'] for r in gold}
    for r in raw:
        rid=r['row_id']
        if rid in by or rid not in ids:raise ValueError('duplicate or unknown response row')
        by[rid]=r
    rows=[];groups=defaultdict(list)
    for g in gold:
        r=by.get(g['row_id'],{});ni=r.get('tokens_in');no=r.get('tokens_out');valid_budget=type(ni) is int and type(no) is int and ni>=0 and no>=0 and ni+no<=budget
        response=r.get('response');res=score(g,response if valid_budget else None)
        v={'row_id':g['row_id'],'root_id':g['root_id'],'family':g['family'],'variant':g['variant'],'arm':g['arm'],'within_budget':valid_budget,'tokens_in':ni,'tokens_out':no,'present':bool(r),**res};rows.append(v);groups[(v['family'],v['variant'],v['arm'])].append(v)
    result={'schema':'mit06-model-open-dev-v1','checkpoint':checkpoint,'total_token_budget':budget,'rows':rows,'groups':[{'family':k[0],'variant':k[1],'arm':k[2],'rows':len(v),'verified':sum(z['verified'] for z in v),'within_budget':sum(z['within_budget'] for z in v),'applicability_correct':sum(z['applicability_correct'] is True for z in v),'applicability_scored':sum(z['applicability_correct'] is not None for z in v)} for k,v in sorted(groups.items())],'missing_rows':len(gold)-len(by),'responses_sha256':hashlib.sha256(responses.read_bytes()).hexdigest(),'limits':'Open development; token counts are adapter-reported, not independently authenticated; no proof of token-matched sham; no sealed confirmation.'}
    out.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private',type=Path,required=True);p.add_argument('--responses',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--budget',type=int,required=True);p.add_argument('--checkpoint',required=True);a=p.parse_args()
    if a.budget<=0:raise ValueError('budget must be positive')
    main(a.private,a.responses,a.output,a.budget,a.checkpoint)

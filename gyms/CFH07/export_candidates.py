"""Project evaluator receipts into public-development candidates; no corpus admission."""
import gzip
import hashlib
import json
import sys
from pathlib import Path
from collections import Counter


def project(receipt):
    assert receipt['schema']=='cfh07/public-development/v1' and receipt['training_ready'] is False
    decks={d['seed']:d for d in receipt['decks']}
    episodes={};counts=Counter()
    for trace in receipt['traces']:
        seed,cap=trace['seed'],trace['cap'];assert seed in decks
        events=[]
        for e in trace['events']:
            state=hex(e['remaining'])
            if e['kind']=='buy':
                events.append({'proposal':{'action':'buy','groups':e['groups']},'verified':{'version_set':state}})
            elif e['kind']=='observe':
                events.append({'proposal':{'action':'observe','probe':e['probe']},'environment':{'reply':e['reply']},'verified':{'version_set':state}})
            elif e['kind']=='finish':
                events.append({'proposal':{'action':'finish','claim':e['claim']},'verified':{'version_set':state}})
            else:raise ValueError('event kind')
        episode={'schema':'cfh07/candidate/v1','source_family':'CFH-public-graph-route-grammar','deck':seed,'base_cap':cap,'query_cap':4,'split':'public_development','training_ready':False,'policy_optimality':'unknown','events':events}
        raw=json.dumps(episode,sort_keys=True,separators=(',',':'))
        key=hashlib.sha256(raw.encode()).hexdigest()
        if key in episodes:counts['duplicates_removed']+=1;continue
        episodes[key]=episode;counts['unique_episodes']+=1;counts['events']+=len(events)
        counts['identifications']+=events[-1]['proposal']['claim'] is not None
    out={'schema':'cfh07/candidate-pack/v1','split':'public_development','training_ready':False,'family':'CFH-public-graph-route-grammar','source_receipt_sha256':None,'counts':dict(counts),'decks':list(decks.values()),'episodes':[dict(id=k,**v) for k,v in episodes.items()]}
    return out


def main():
    source=Path(sys.argv[1]);raw=source.read_bytes()
    d=json.loads(gzip.decompress(raw) if source.suffix=='.gz' else raw)
    out=project(d);out['source_receipt_sha256']=hashlib.sha256(raw).hexdigest()
    text=json.dumps(out,sort_keys=True,separators=(',',':'))
    assert 'hidden_evaluator_only' not in text and 'truth' not in text
    print(text)

if __name__=='__main__':main()

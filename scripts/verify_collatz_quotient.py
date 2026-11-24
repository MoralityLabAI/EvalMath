"""Regenerate exact CLQ-01 receipt (Python stdlib only)."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import gcd
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spiral_ln.evaluation_collatz_quotient import atlas, basin, collision, feedback, full_oracle, quotient


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'output/collatz_quotient/clq01.json');args=p.parse_args()
    census=Counter(); checked=0; examples={}; witnesses=[]
    exact=(13,73,97,265,577,601,7081)
    for d in sorted(set(range(1,2002,4))|set(exact)):
        if gcd(d,6)!=1: continue
        labels, periods=atlas(d);q=quotient(d);result=feedback(d)
        for n in range(1,2*d,2):
            c=basin(n,d,labels)
            assert full_oracle(n,d)==(c,periods[c])
            assert q[n%d]==q[c%d]
            checked+=1
        assert set(q.values())=={q[c%d] for c in periods}
        if d<=2001:
            census['moduli']+=1
            census['quotient_sufficient']+=result['collision_classes']==0
            census['quotient_insufficient']+=result['collision_classes']>0
        if d in exact:
            examples[str(d)]={**result,'periods':periods}
            groups=defaultdict(list)
            for c in sorted(periods): groups[q[c%d]].append(c)
            for cs in groups.values():
                if len(cs)<2: continue
                for m in (1,2,4,8,13,24,73,2*d,3*d):
                    x,y=collision(d,*cs[:2],m)
                    assert x%m==y%m and full_oracle(x,d)[0]==cs[0] and full_oracle(y,d)[0]==cs[1]
                    witnesses.append({'d':d,'cycles':cs[:2],'modulus':m,'residue':x%m,'bit_lengths':[x.bit_length(),y.bit_length()], 'sha256':[hashlib.sha256(z.to_bytes((z.bit_length()+7)//8,'big')).hexdigest() for z in (x,y)]})
    rng=random.Random(2601);long_count=0
    for d in exact:
        labels,periods=atlas(d);q=quotient(d)
        for bits in (64,256,1024):
            for _ in range(16):
                n=(1<<(bits-1))|rng.getrandbits(bits-1)
                c=basin(n,d,labels)
                assert full_oracle(n,d)==(c,periods[c]) and q[n%d]==q[c%d]
                long_count+=1
    sources=['src/spiral_ln/evaluation_collatz_quotient.py','tests/test_collatz_quotient.py','scripts/verify_collatz_quotient.py','paper/collatz_quotient_sufficiency.md']
    receipt={'experiment':'CLQ-01','evidence':'finite verified example','population':'uniform odd representatives 1..2d-1','checks':{'independent_full_oracle_agrees':True,'all_quotient_classes_occupied':True,'quotient_invariant':True,'constructive_witnesses_replay':True,'long_inputs_agree':True},'finite_roots_checked':checked,'long_inputs_checked':long_count,'census':dict(census),'examples':examples,'collision_witness_count':len(witnesses),'collision_witness_sha256':hashlib.sha256(json.dumps(witnesses,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'source_sha256':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources}}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('census','finite_roots_checked','long_inputs_checked')},indent=2));print('collision witnesses:',len(witnesses))

if __name__=='__main__': main()

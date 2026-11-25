"""Source-hashed exact receipt: belief recursion versus alpha-vector oracle."""
import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spiral_ln.evaluation_math_controller import bayes, blind, alpha_oracle, fixture


def build():
    n=0
    for strength,prior,cost,b in product((F(1,2),F(3,4),F(1)),(F(0),F(1,4),F(1,2),F(3,4),F(1)),(1,2,3),range(5)):
        a=(strength,1-strength); z=a[::-1]; t=(F(3,4),)*2
        r=((a,z,t),(a,z,t)); c=((1,1,cost),(1,1,cost+1)); p=(prior,1-prior)
        v=bayes(r,c,p,b)[0]
        assert v==alpha_oracle(r,c,p,b)
        assert v>=blind(r,c,p,b)
        if prior in (0,1):
            assert v==blind(r,c,p,b)
        n+=1
    r,c,p=fixture(2); v,solve=bayes(r,c,p,4); u=blind(r,c,p,4)
    assert v-u==F(3,128)
    assert solve(0,4,p)[1]==0 and solve(0,3,(F(1,8),F(3,8)))[1]==1
    assert solve(1,2,(F(3,32),F(3,32)))[1]==0 and solve(1,2,(F(1,32),F(9,32)))[1]==1
    rc,cc,pc=fixture(1); cheap=bayes(rc,cc,pc,4)[0]
    assert cheap==F(219,256)
    paths=['src/spiral_ln/evaluation_math_controller.py','tests/test_evaluation_math_controller.py','scripts/verify_math_controller.py']
    return {'schema':'em-mpt-03-v0.1','evidence':'exact finite synthetic mechanism','grid_cases':n,
            'values':{'bayes':str(v),'blind':str(u),'gap':str(v-u),'cheap_retrieval':str(cheap)},
            'checks':{'alpha_oracle_agrees':True,'optimal_blind_dominated':True,'known_type_equality':True,'history_collision_witness':True,'retrieval_cost_witness':True},
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'output/evaluation_math_controller/em_mpt_03_v0_1.json')
    out=parser.parse_args().output; out.parent.mkdir(parents=True,exist_ok=True)
    result=build(); out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2,sort_keys=True))

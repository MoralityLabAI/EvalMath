"""Exact finite audits of the sharp fixed-product theorem."""
import argparse,hashlib,json,sys
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spiral_ln.evaluation_math_loss_envelope import completion,pair_exchange,concentrated_lower
from spiral_ln.evaluation_math_persistence import persistent,homogeneous


def build():
    counts=dict(dp=0,lower=0,upper=0,exchange=0,stress=0)
    for d in range(1,5):
        for exps in product(range(5),repeat=d):
            ps=tuple(F(1,2)**e for e in exps); q=prod(ps)
            for b in range(d+7):
                v=completion(ps,b)
                assert v==persistent(ps,b); counts['dp']+=1
                assert concentrated_lower(d,b,q)==completion((q,)+(F(1),)*(d-1),b)<=v
                counts['lower']+=1
                if sum(exps)%d==0:
                    p=F(1,2)**(sum(exps)//d)
                    assert v<=homogeneous(d,b,p)==completion((p,)*d,b)
                    counts['upper']+=1
    for e1,e2,e3 in product(range(5),repeat=3):
        ps=tuple(F(1,2)**e for e in (e1,e2,e3))
        for e4 in range(e1+e2+1):
            rep=(F(1,2)**e4,F(1,2)**(e1+e2-e4))
            for b in range(3,10):
                gap=completion((*rep,ps[2]),b)-completion(ps,b)
                assert gap==pair_exchange(ps,rep,b)
                assert gap*(sum(ps[:2])-sum(rep))>=0
                counts['exchange']+=1
    for d,b in ((5,12),(8,16),(10,20),(16,32)):
        p=F(1,2); q=p**d
        a=completion((q,)+(F(1),)*(d-1),b); z=completion((p,)*d,b)
        assert a==concentrated_lower(d,b,q) and z==homogeneous(d,b,p) and a<z
        counts['stress']+=1
    ps=(F(1,2),)*4; q=prod(ps); b=8
    paths=['src/spiral_ln/evaluation_math_loss_envelope.py','src/spiral_ln/evaluation_math_persistence.py','scripts/verify_math_loss_envelope.py','tests/test_evaluation_math_loss_envelope.py']
    return {'schema':'em-mpt-07-v0.1','evidence':'algebraic theorem with exact finite checks','counts':counts,
            'values':{'product':str(q),'budget':b,'lower':str(concentrated_lower(4,b,q)),
                      'upper':str(completion(ps,b))},
            'checks':{'dp_oracle':True,'lower_attainment':True,'upper_when_rational':True,'pair_identity':True,'larger_cases':True},
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'output/evaluation_math_loss_envelope/em_mpt_07_v0_1.json')
    out=p.parse_args().output; out.parent.mkdir(parents=True,exist_ok=True)
    r=build(); out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(r,indent=2,sort_keys=True))

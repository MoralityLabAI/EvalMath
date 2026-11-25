"""Independent finite checks for EM-MPT-04--06; exact fractions and hashes."""
import argparse,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from math import comb
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from spiral_ln.evaluation_math_controller import fixture,blind
from spiral_ln.evaluation_math_memory import (optimal_tree,evaluate,compile_tree,decode,quantized_tree,
    posterior_regret_certificate,frontier,robust_two,coupling_bound,interval,envelope)


def build():
    counts=dict(compression=0,quantization=0,minimax=0,coupling=0,coverage=0,envelope=0,stress=0)
    for strength,prior,cost,b in product((F(1,2),F(3,4),F(1)),(F(0),F(1,4),F(1,2),F(3,4),F(1)),(1,2,3),range(5)):
        a=(strength,1-strength); z=a[::-1]; q=(F(3,4),)*2
        r=((a,z,q),(a,z,q)); c=((1,1,cost),(1,1,cost+1)); p=(prior,1-prior)
        v,t=optimal_tree(r,c,p,b); start,table,w,bits=compile_tree(t,c,b)
        assert decode(start,table,c,b)==t and 2**bits>=w and (bits==0 or 2**(bits-1)<w)
        assert sum(x*y for x,y in zip(p,evaluate(t,r,c,b,2)))==v
        counts['compression']+=1
        for g in (1,2,3,8):
            tq=quantized_tree(r,c,p,b,g); qv=sum(x*y for x,y in zip(p,evaluate(tq,r,c,b,2)))
            assert qv<=v and posterior_regret_certificate(tq,r,c,p,b)==v-qv
            counts['quantization']+=1
        f=frontier(r,c,b,2); rv,(u,w,m)=robust_two(f)
        assert min(m*x+(1-m)*y for x,y in zip(u,w))==rv
        # Independently use a uniform-prior grid as a weak-duality upper bound;
        # candidate prior breakpoints from intersections of payoff lines are also included.
        candidates={F(0),F(1)}
        for x,y in product(f,repeat=2):
            slope=x[0]-x[1]-y[0]+y[1]
            if slope:
                k=(y[1]-x[1])/slope
                if 0<=k<=1: candidates.add(k)
        assert rv==min(max(k*x+(1-k)*y for x,y in f) for k in candidates)
        counts['minimax']+=1
    # True/nominal worlds: homogeneous two-action probabilities, two latent types, two stages.
    vals=(F(1,4),F(1,2),F(3,4))
    for s,t,p,q in product(vals,vals,vals,vals):
        r=(((s,1-s),(1-s,s)),)*2; rr=(((t,1-t),(1-t,t)),)*2; c=((1,1),)*2
        pi=(p,1-p); qq=(q,1-q)
        v,tr=optimal_tree(r,c,pi,3); vv,_=optimal_tree(rr,c,qq,3)
        tv=sum(x*y for x,y in zip(qq,evaluate(tr,rr,c,3,2)))
        gamma=coupling_bound(abs(p-q),abs(s-t),3)
        assert abs(v-tv)<=gamma and 0<=vv-tv<=min(F(1),2*gamma)
        counts['coupling']+=1
    for n,p in product(range(1,13),[F(i,40) for i in range(41)]):
        cover=sum((comb(n,k)*p**k*(1-p)**(n-k) for k in range(n+1)
                   if (lambda z:z[0]<=p<=z[1])(interval(n,k,F(1,20),20))),F(0))
        assert cover>=F(19,20)
        counts['coverage']+=1
    tree=(0,(0,None,None),(0,None,None)); c=((1,),(1,)); keys=(((),0),(((0,1),),0),(((0,0),),0))
    options=((F(0),F(1)),(F(1,4),F(3,4)),(F(1,2),F(1,2)))
    for ints in product(options,repeat=3):
        e=envelope(tree,dict(zip(keys,ints)),c,2)
        oracle=[a*b for a,b,_ in product(*ints)]
        assert e==(min(oracle),max(oracle)); counts['envelope']+=1
    # Stress beyond the small exhaustive clock/progress grid. Width is for this fixed policy.
    stress=[]
    for d,b in ((2,6),(3,6),(3,8),(4,8),(4,10)):
        a=(F(3,4),F(1,4)); r=((a,a[::-1],(F(3,4),)*2),)*d
        c=tuple((1,1,2+i) for i in range(d)); p=(F(1,2),)*2
        v,t=optimal_tree(r,c,p,b); start,table,w,bits=compile_tree(t,c,b)
        assert decode(start,table,c,b)==t and sum(x*y for x,y in zip(p,evaluate(t,r,c,b,2)))==v
        stress.append({'d':d,'budget':b,'closure':str(v),'width':w,'bits':bits,'table_rows':len(table)})
        counts['stress']+=1
    r,c,p=fixture(2); v,t=optimal_tree(r,c,p,4); f=frontier(r,c,4,2); rv,witness=robust_two(f)
    qvals={str(g):str(sum(x*y for x,y in zip(p,evaluate(quantized_tree(r,c,p,4,g),r,c,4,2)))) for g in (1,2,3,8,16)}
    paths=['src/spiral_ln/evaluation_math_controller.py','src/spiral_ln/evaluation_math_memory.py','tests/test_evaluation_math_memory.py','scripts/verify_math_memory.py']
    return {'schema':'em-mpt-04-06-v0.1','evidence':'exact finite synthetic mechanism and confidence-grid checks',
            'counts':counts,'stress':stress,'checks':{'all_grid_checks':True,'policy_reconstruction':True,'regret_telescope':True,
             'minimax_dual':True,'coupling_bound':True,'confidence_coverage':True,'rectangular_corner_oracle':True},
            'values':{'optimal':str(v),'blind':str(blind(r,c,p,4)),'compiled_bits':compile_tree(t,c,4)[3],
                      'quantized':qvals,'deterministic_minimax':str(max(map(min,f))),'randomized_minimax':str(rv),
                      'mixture':[[str(x) for x in w] for w in witness[:2]]+[str(witness[2])]},
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'output/evaluation_math_memory/em_mpt_04_06_v0_1.json')
    out=parser.parse_args().output; out.parent.mkdir(parents=True,exist_ok=True)
    r=build(); out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(r,indent=2,sort_keys=True))

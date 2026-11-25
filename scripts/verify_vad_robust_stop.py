"""VAD-07B: exact latent cue-reliability mixture and worst-case policy menu."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse,json
import verify_vad_stopping as a

REVERSE=(F(1,4),)*4+(F(3,4),)
WEAK=(F(11,20),)*4+(F(9,20),)
BLIND=(F(1,2),)*5


def run():
    w=a.prior(a.WEIGHTS['base']); scenarios={'base':(w,a.P),'reversed':(w,REVERSE),'weak':(w,WEAK),'blind':(w,BLIND)}
    for s in ('null_heavy','early_heavy','late_heavy'): scenarios[s]=a.model(a.WEIGHTS[s])
    menu={}; checks=0
    # Reliability mixture is chosen before a family, and can be inferred from cue history.
    for k in range(11):
        alpha=F(k,10); times=a.TIMES*2; weights=tuple((1-alpha)*x for x in w)+tuple(alpha*x for x in w)
        v=a.bellman(weights,a.P+REVERSE,times=times); act=lambda n,j,v=v:v(n,j)[1]
        assert a.evaluate(weights,a.P+REVERSE,act,times)['net']==v(0,0)[0]; checks+=1
        menu[f'mix_{k}']=act
    for k in (0,2,8,16,24): menu[f'cut_{k}']=lambda n,j,k=k:n<k
    results={m:{s:a.evaluate(wq,q,act)['net'] for s,(wq,q) in scenarios.items()} for m,act in menu.items()}
    # Protect across base/reversed/weak/blind, holding the latent-time prior fixed.
    protected=('base','reversed','weak','blind')
    pure=max(menu,key=lambda m:(min(results[m][s] for s in protected),results[m]['base'],m))
    # Enumerate all pair mixtures on a predeclared 1/20 grid; no claims about global minimax.
    best=None
    for m in menu:
        for n in menu:
            for j in range(21):
                alpha=F(j,20); v={s:alpha*results[m][s]+(1-alpha)*results[n][s] for s in scenarios}
                key=(min(v[s] for s in protected),v['base'],m,n,j)
                if best is None or key>best[0]: best=(key,v)
    key,values=best
    rows=[dict(policy=m,**{s:str(v) for s,v in rr.items()}) for m,rr in results.items()]
    return dict(protocol='VAD-07B',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),dependency_sha256=sha256(Path(a.__file__).read_bytes()).hexdigest(),checks=checks,protected=list(protected),pure=pure,pure_worst=str(min(results[pure][s] for s in protected)),pair_mix=dict(first=key[2],second=key[3],first_probability=str(F(key[4],20)),worst=str(key[0]),values={s:str(x) for s,x in values.items()}),rows=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); args=p.parse_args(); r=run(); args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('pure',r['pure'],float(F(r['pure_worst'])), 'pair',r['pair_mix']['first'],r['pair_mix']['second'],r['pair_mix']['first_probability'],float(F(r['pair_mix']['worst'])))
    for row in r['rows']:
        if row['policy'] in ('mix_0','mix_5','mix_10','cut_2',r['pure'],r['pair_mix']['first'],r['pair_mix']['second']): print(row['policy'],{s:round(float(F(x)),4) for s,x in row.items() if s!='policy'})
    print('pair mix', {s:round(float(F(x)),4) for s,x in r['pair_mix']['values'].items()})

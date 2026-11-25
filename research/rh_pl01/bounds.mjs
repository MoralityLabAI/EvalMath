// RH-PL-02: stronger full-calculus last-rule bounds and independent bounded MP control.
import {kernel} from './kernel.mjs';
function buildBounds(k){
  const {E,M,I,Q,encode,axiom,verify,lower}=k;
  const minShape=f=>{
    switch(f[0]){
      case'e':case'm':return 5;
      case'n':return 1+minShape(f[1]);
      case'i':return 1+minShape(f[1])+minShape(f[2]);
      case'a':return 3+minShape(f[2]);
      default:throw Error('invalid formula');
    }
  };
  function strengthened(f){
    const n=encode(f).length;
    if(axiom(f))return n+1;
    if(f[0]!=='a')return 2*n+14;
    const axMP=2*n+2*minShape(f)+10;
    const nonaxMP=3*n+27;
    const gen=n+1+strengthened(f[2]);
    return Math.min(axMP,nonaxMP,gen);
  }
  function formulae(max){
    const bySize=Array.from({length:max+1},()=>[]);
    for(let n=1;n<=max;n++){
      const out=bySize[n];
      for(let x=0;x<=n-5;x++){const y=n-5-x;out.push(['e',x,y],['m',x,y])}
      for(const a of bySize[n-1])out.push(['n',a]);
      for(let j=1;j<n-1;j++)for(const a of bySize[j])for(const b of bySize[n-1-j])out.push(['i',a,b]);
      for(let x=0;x<=n-3;x++)for(const a of bySize[n-3-x])out.push(['a',x,a]);
    }
    return bySize.flat();
  }
  function orders(xs){
    if(!xs.length)return [[]];
    return xs.flatMap((x,i)=>orders(xs.slice(0,i).concat(xs.slice(i+1))).map(rest=>[x,...rest]));
  }
  // Exact last-MP search at budgets allowing at most one additional line.
  // The generalization branch must separately be ruled out.
  function oneExtraMP(f,B){
    const n=encode(f).length, maxA=Math.floor((B-2*n-4)/2);
    if(maxA<5)return {antecedents:0,additional_candidates:0,checked_orders:0,witness:null};
    if(B-(2*n+14)>=12)throw Error('more than one additional line possible');
    const all=formulae(maxA);
    let antecedents=0,additional_candidates=0,checked_orders=0;
    for(const a of all){
      antecedents++;
      const aText=encode(a), fText=encode(f), imp=encode(I(a,f));
      if(aText===fText)continue;
      const slack=B-(aText.length+imp.length+fText.length+3);
      if(slack<0)throw Error('bad antecedent budget');
      const extras=[null,...(slack>=6?formulae(slack-1).map(encode):[])];
      for(const extra of extras){
        if(extra!==null){additional_candidates++;if([aText,imp,fText].includes(extra))continue}
        for(const lines of orders(extra===null?[aText,imp]:[aText,imp,extra])){
          if(lines.indexOf(aText)<0||lines.indexOf(imp)<0)throw Error('bad order');
          checked_orders++;
          const proof=lines.concat(fText).join('\n')+'\n';
          if(proof.length>B)throw Error('budget');
          if(verify(proof,fText))return {antecedents,additional_candidates,checked_orders,witness:proof};
        }
      }
    }
    return {antecedents,additional_candidates,checked_orders,witness:null};
  }
  function run(){
    const assert=(b,m)=>{if(!b)throw Error(m)};
    const p=M(0,0), r=E(0,0), id=I(p,p), target=Q(0,id);
    const witness=[r,I(r,id),id,target].map(encode).join('\n')+'\n';
    assert(verify(witness,encode(target)),'upper witness');
    assert(witness.length===51&&strengthened(target)===51&&lower(target)===42,'exact bound');
    const search=oneExtraMP(target,50);
    assert(search.witness===null,'MP counterexample');
    assert(lower(id)+encode(target).length+1===51,'generalization bound');
    const examples=[];
    for(let n=1;n<=5;n++){
      let f=r;
      for(let x=0;x<n;x++)f=Q(x,f);
      examples.push({binders:n,length:encode(f).length,baseline:lower(f),strengthened:strengthened(f)});
    }
    return {target:encode(target),target_bytes:encode(target).length,baseline:lower(target),strengthened:strengthened(target),upper:witness.length,mp_budget:50,mp_search:search,examples};
  }
  return {minShape,strengthened,formulae,oneExtraMP,run};
}
export const bounds=buildBounds(kernel);
if (typeof process!=='undefined' && process.argv[1]?.endsWith('/bounds.mjs')) console.log(JSON.stringify(bounds.run(),null,2));

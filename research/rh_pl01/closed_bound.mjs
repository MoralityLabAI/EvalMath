// RH-PL-03: free-occurrence-aware refinement of the last-rule bound.
import {kernel} from './kernel.mjs';
import {bounds} from './bounds.mjs';
function buildClosedBound(k,bounds){
  const {encode,decode,axiom,subst,Q,I}=k;
  function freeCounts(f){
    const counts=new Map(), bound=new Map();
    const add=x=>{if(!bound.get(x))counts.set(x,(counts.get(x)||0)+1)};
    function walk(g){
      switch(g[0]){
        case'e':case'm':add(g[1]);add(g[2]);break;
        case'n':walk(g[1]);break;
        case'i':walk(g[1]);walk(g[2]);break;
        case'a':{const x=g[1];bound.set(x,(bound.get(x)||0)+1);walk(g[2]);bound.set(x,bound.get(x)-1);break;}
      }
    }
    walk(f);return counts;
  }
  function instantiationPredecessorFloor(f){
    const n=encode(f).length;
    let saving=0;
    for(const [v,c] of freeCounts(f))saving=Math.max(saving,v*c);
    return 3+Math.max(bounds.minShape(f),n-saving);
  }
  function cases(f){
    const n=encode(f).length;
    if(axiom(f))return {axiom:n+1};
    if(f[0]!=='a')return {mp:2*n+14};
    return {axiom_mp:2*n+2*instantiationPredecessorFloor(f)+4,derived_mp:3*n+27,generalization:n+1+bound(f[2])};
  }
  function bound(f){return Math.min(...Object.values(cases(f)))}
  function controls(){
    let substitutions=0,closed=0,open=0;
    for(const g of bounds.formulae(11))for(let x=0;x<4;x++)for(let y=0;y<4;y++){
      let f;try{f=subst(g,x,y)}catch{continue}
      const a=Q(x,g), imp=I(a,f);
      if(axiom(imp)!=='forall-elimination')throw Error('unexpected universal axiom');
      if(encode(a).length<instantiationPredecessorFloor(f))throw Error('invalid floor');
      if(freeCounts(f).size===0)closed++;else open++;
      substitutions++;
    }
    return {substitutions,closed,open};
  }
  return {freeCounts,instantiationPredecessorFloor,cases,bound,controls};
}
export const closedBound=buildClosedBound(kernel,bounds);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/closed_bound.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 const f=kernel.decode(raw.slice(0,-1));
 if(kernel.encode(f)+'\n'!==raw)throw Error('target roundtrip');
 console.log(JSON.stringify({bytes:raw.length,free_variables:closedBound.freeCounts(f).size,previous:bounds.strengthened(f),new_lower:closedBound.bound(f),last_rule_cases:closedBound.cases(f),controls:closedBound.controls()},null,2));
}

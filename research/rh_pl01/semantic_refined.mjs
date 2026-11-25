// RH-PL-05: exact cheapest false-axiom cost in the well-founded countermodel.
import {kernel} from './kernel.mjs';
import {bounds} from './bounds.mjs';
import {spine} from './spine.mjs';
import {semantic} from './semantic.mjs';
function buildRefined(k,b,sp,sem){
  const {E,M,N,I,Q,X,A,F,encode,decode,free,axiom}=k;
  const sep=phi=>X(2,Q(0,F(M(0,2),A(M(0,1),phi))));
  function run(raw){
    const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
    const short=b.formulae(7).filter(f=>!free(f).has(2));
    let controls=0;
    // For x in a in a well-founded membership structure, x!=a,
    // no loops, no reverse edge, and x in a. The possible atoms
    // below size 8 use only x=v0 and a=v1.
    const truth=f=>{
      if(f[0]==='n')return !truth(f[1]);
      if(!['e','m'].includes(f[0])||f[1]>1||f[2]>1)throw Error('unexpected short formula');
      return f[0]==='e'?f[1]===f[2]:f[1]===0&&f[2]===1;
    };
    const rows=short.map(phi=>{
      const s=sep(phi),u=encode(s).length+1,c=sp.compact(s).length+1;
      assert(axiom(s)==='separation','schema recognition');
      assert(u===58+2*(encode(phi).length-5),'unary byte accounting');
      assert(u<64,'short threshold');
      const uniform=truth(phi);
      controls++;return {phi:encode(phi),unary_line:u,compact_line:c,separation_result:uniform?'source':'empty'};
    });
    const witness=sep(M(3,0));
    assert(axiom(witness)==='separation','false witness schema');
    const costs={unary:encode(witness).length+1,compact:sp.compact(witness).length+1};
    assert(costs.unary===64&&costs.compact===36,'exact false separation costs');
    const f=decode(raw.slice(0,-1));assert(encode(f)+'\n'===raw,'target');
    const bounds=Object.entries(sp.encodings).map(([encoding,enc])=>{
      const minFalse=costs[encoding];
      return {encoding,minimum_false_axiom_line:minFalse,...sem.semanticFloor(f,enc,minFalse)};
    });
    return {short_schema_instances:controls,short_schema_panel:rows,witness_phi:encode(M(3,0)),witness_separation_costs:costs,bounds};
  }
  return {run};
}
export const refined=buildRefined(kernel,bounds,spine,semantic);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/semantic_refined.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(refined.run(raw),null,2));
}

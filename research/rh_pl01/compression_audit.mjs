// RH-PL-09: independent structural-recognizer and serialized-cost audit.
import {kernel} from './kernel.mjs';
import {bounds} from './bounds.mjs';
import {spine} from './spine.mjs';
import {compression} from './compression.mjs';
function audit(k,b,sp,c,raw){
 const {E,M,N,I,Q,encode,axiom}=k;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const {ar,build,clauses}=c.prepare(raw);
 const allowed=new Set(['K','S','classical']);let census=0,censusPos=0,generated=0,generatedPos=0,negative=0;
 function check(f,group){const id=ar.intern(f),p=ar.prop(id),q=allowed.has(axiom(f));assert(p===q,'propositional recognition disagreement');assert(ar.nodes[id].u===encode(f).length&&ar.nodes[id].c===sp.compact(f).length,'serialized cost');if(group==='census'){census++;censusPos+=Number(p)}else{generated++;generatedPos+=Number(p);negative+=Number(!p)}}
 for(const f of b.formulae(18))check(f,'census');
 const pool=[M(0,0),M(1,1),E(0,0),N(M(0,0)),Q(0,M(0,1)),I(M(0,1),M(1,0)),M(36,1296),Q(3,E(3,3))];
 for(const p of pool)for(const q of pool){
  check(I(p,I(q,p)),'generated');check(I(I(N(q),N(p)),I(p,q)),'generated');
  check(I(p,I(q,N(p))),'generated');check(I(I(N(q),N(p)),I(q,p)),'generated');
  for(const r of pool){
    check(I(I(p,I(q,r)),I(I(p,q),I(p,r))),'generated');
    check(I(I(p,I(q,r)),I(I(p,q),I(p,N(r)))),'generated');
  }
 }
 // A further deep-interface check in the original checker with compact
 // serialization (and conversion back to unary through verifyCompact).
 // Use one moderate-depth root to avoid materializing the full library.
 const index=4,p=build('unary',[index]),asts=p.ids.map(id=>ar.ast(id)),target=ar.ast(p.roots[0]);
 const compactProof=asts.map(sp.compact).join('\n')+'\n';
 assert(sp.verifyCompact(compactProof,sp.compact(target)),'depth-five compact proof rejected');
 assert(compactProof.length===p.cost.compact,'compact expanded cost');
 return {census,census_propositional_positive:censusPos,generated,generated_positive:generatedPos,generated_negative:negative,depth_five_interface:{index,...p.cost,compact_kernel_replay:true},actual_rh_proof:false};
}
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/compression_audit.mjs')){
 const {readFileSync}=await import('node:fs');const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');console.log(JSON.stringify(audit(kernel,bounds,spine,compression,raw),null,2));
}

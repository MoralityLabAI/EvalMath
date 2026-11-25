// RH-PL-16: the normalized denominator contract is equivalent to its
// exact frozen clauses under Omega and a designated natural empty set.
import {pairs} from './pairs.mjs';
import {denominatorBridge} from './denominator_bridge.mjs';
import {denominatorNormalize} from './denominator_normalize.mjs';
import {kernel} from './kernel.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??pairs.prepare(raw),{p,t,ar,ns,pack}=ctx;
 const {nest,empty}=t,{F,hyp,mp,abs,left,right,conj}=p.logic;
 const forward=denominatorBridge.prepare(raw,ctx),backward=denominatorNormalize.prepare(raw,ctx);
 const d=forward.predicates,{G,Z,nat}=d;
 const normalized=d.normalized(G),exact=d.exact(G),goal=F(normalized,exact);
 const premises=[d.omega,nat(Z),empty(Z)];
 const [totalProof,baseProof,updateProof]=forward.components.map(c=>c.result);
 const result=pack(premises,(omega,mz,ez)=>{
   const hn=hyp(normalized),total=left(hn),functional=left(right(hn));
   const base=left(right(right(hn))),update=right(right(right(hn)));
   const exactTotal=mp(nest(total,functional),totalProof);
   const exactBase=mp(nest(mz,ez,total,base),baseProof);
   const exactUpdate=mp(nest(omega,total,update),updateProof);
   const toExact=abs(hn,nest(exactTotal,exactBase,exactUpdate));
   const he=hyp(exact),sourceTotal=left(he),sourceBase=left(right(he)),sourceUpdate=right(right(he));
   const toNormalized=abs(he,mp(nest(mz,ez,sourceTotal,sourceBase,sourceUpdate),backward.result));
   return conj(toExact,toNormalized)
 });
 if(ns[result.f].y!==goal||result.deps.size)throw Error('denominator equivalence target');
 function run(){
   const row=ctx.get('normalized_denominator_equivalent_to_exact_frozen_clauses',result);
   Object.assign(row.receipt,{source_clauses:[14,19,21],source_slots:d.slots,
     initial_value_naturalness_premise_required:false,both_directions_derived:true,actual_rh_proof:false});
   return [row]
 }
 return {ctx,predicates:d,result,premises,goal,run,source_slots:d.slots,
   exact_source:kernel.encode(ar.ast(exact)),normalized_source:kernel.encode(ar.ast(normalized))};
}
export const denominatorEquivalence={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/denominator_equivalence.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(denominatorEquivalence.prepare(raw).run().map(x=>x.receipt),null,2));
}

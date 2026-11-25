// RH-PL-16: exact frozen denominator clauses imply the PL-15 normal form.
import {pairs} from './pairs.mjs';
import {makeDenominatorPredicates} from './denominator_predicates.mjs';
import {kernel} from './kernel.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??pairs.prepare(raw),{p,t,ar,ns,pack,witness,allP}=ctx;
 const {apply,inst,nest,move,symmetric,trans,replace,emptyUnique,succUnique,empty,succ}=t;
 const {E,A,hyp,mp,abs,left,right,conj}=p.logic;
 const d=makeDenominatorPredicates(ctx,raw),{nat,at,mul,clause,G,Z,C0}=d;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const [x,y,a,b,mark]=[70,71,72,73,99];
 const premises=[nat(Z),empty(Z),clause(14),clause(19),clause(21)];
 const goal=d.normalized(G);
 function functionalAt(total,x,u,v,mx,mu,mv,gu,gv){
   const consequence=mp(nest(mx,mu,mv),inst(right(total),x,u,v));
   const [l,r]=p.logic.split(ns[consequence.f].x);
   return mp(conj(move(gu,l),move(gv,r)),consequence)
 }
 function withNat(exists,v,fn){return witness(exists,v,h=>fn(left(h),right(h)))}
 const result=pack(premises,(mz,ez,total,initial,recurrence)=>{
   const normalizedTotal=move(left(total),d.total(G));

   const fh=[nat(x),nat(a),nat(b),at(G,x,a),at(G,x,b)].map(hyp);
   const feq=functionalAt(total,x,a,b,...fh);
   const normalizedFunctional=move(allP([x,a,b],fh.reduceRight((q,h)=>abs(h,q),feq)),d.functional(G));

   // Empty-set uniqueness moves an arbitrary empty natural input to the
   // designated zero. Exact functionality identifies its chosen value.
   const bh=[empty(x),nat(x),nat(a),at(G,x,a)].map(hyp);
   const xz=emptyUnique(x,Z,bh[0],ez,98);
   const atZero=replace(bh[3],xz,at(G,mark,a),mark);
   const beq=withNat(initial,80,(mi,body)=>{
     const same=functionalAt(total,Z,a,80,mz,bh[2],mi,atZero,left(body));
     return trans(same,right(body))
   });
   assert(beq.f===E(a,C0),'normalized initial value');
   const normalizedBase=move(allP([x,a],bh.reduceRight((q,h)=>abs(h,q),beq)),d.base(G));

   // The frozen recurrence introduces two successor witnesses and three
   // value witnesses. Successor uniqueness and graph functionality move
   // the resulting multiplication relation to the requested arguments.
   const sh=[nat(x),nat(y),nat(a),nat(b),succ(x,y),at(G,x,a),at(G,y,b)].map(hyp);
   const [mx,my,ma,mb,sy,gxa,gyb]=sh;
   const recurrenceAt=mp(mx,inst(recurrence,x));
   const step=withNat(recurrenceAt,80,(mk,kbody)=>
     withNat(right(kbody),81,(mu,ubody)=>
       withNat(right(ubody),82,(ml,lbody)=>
         withNat(right(lbody),83,(mv,vbody)=>
           withNat(right(vbody),84,(mw,wbody)=>{
             const sk=left(kbody),gku=left(ubody),sl=left(lbody),gxv=left(vbody);
             const product=left(wbody),equalOutput=right(wbody);
             assert(equalOutput.f===E(81,84),'frozen recurrence final equality');
             const ky=succUnique(x,80,y,sk,sy,98),ly=succUnique(x,82,y,sl,sy,98);
             const gyu=replace(move(gku,at(G,80,81)),ky,at(G,mark,81),mark);
             const ub=functionalAt(total,y,81,b,my,mu,mb,gyu,gyb);
             const va=functionalAt(total,x,83,a,mx,mv,ma,gxv,gxa);
             const wb=trans(symmetric(equalOutput),ub);
             let out=move(product,mul(82,83,84));
             out=replace(out,ly,mul(mark,83,84),mark);
             out=replace(out,va,mul(y,mark,84),mark);
             out=replace(out,wb,mul(y,a,mark),mark);
             assert(out.f===mul(y,a,b),'normalized successor equation');
             return out
           })))))
   ;
   const normalizedUpdate=move(allP([x,y,a,b],sh.reduceRight((q,h)=>abs(h,q),step)),d.update(G));
   return nest(normalizedTotal,normalizedFunctional,normalizedBase,normalizedUpdate)
 });
 assert(ns[result.f].y===goal&&result.deps.size===0,'denominator normalization target');
 function run(){
   const row=ctx.get('exact_denominator_clauses_imply_normalized_recurrence',result);
   Object.assign(row.receipt,{source_clauses:[14,19,21],source_slots:d.slots,
     empty_input_normalization:true,successor_witnesses_normalized:true,
     omega_premise_required:false,multiplication_totality_premise_required:false,
     actual_rh_proof:false});
   return [row]
 }
 return {ctx,predicates:d,result,premises,goal,run,source_slots:d.slots,
   exact_source:kernel.encode(ar.ast(d.exact(G))),normalized_goal:kernel.encode(ar.ast(goal))};
}
export const denominatorNormalize={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/denominator_normalize.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(denominatorNormalize.prepare(raw).run().map(x=>x.receipt),null,2));
}

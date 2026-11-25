// RH-PL-15: every natural index is the endpoint of a bounded Good prefix.
import {ordinals} from './ordinals.mjs';
import {prefixBase} from './prefix_base.mjs';
import {prefixExtension} from './prefix_extension.mjs';
import {makePrefixPredicates} from './prefix_predicates.mjs';
import {kernel} from './kernel.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??ordinals.prepare(raw),{p,t,ar,ns,allP,and,pack,witness,orRight,refl}=ctx;
 const {apply,inst,nest,move,empty,succ}=t,{gen}=ar;
 const {E,M,A,X,sub,hyp,mp,generalize,abs,left,right,conj,ui,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const defs=makePrefixPredicates(ctx,raw,{W:1}),{nat,at,domain,mul}=defs;
 const P=50,Q=51,K=53;
 function unpack(h,count){const out=[];for(let i=1;i<count;i++){out.push(left(h));h=right(h)}out.push(h);return out}
 const exactCover=n=>X(46,A(M(46,K),A(domain(46,n),X(47,A(nat(47),at(46,n,47))))));
 const phi=exactCover(0),induction=p.prove(phi);
 const base=prefixBase.prepare(raw,ctx),extension=prefixExtension.prepare(raw,ctx);
 const baseAll=allP([37,60],base.strongResult);
 const extensionAll=allP([37,60,61,62,63,64],extension.result);
 const premises=[p.omegaW,nat(defs.C0),defs.mt,defs.power(1,P),defs.power(P,Q),defs.famSpec(Q,K)];
 const inductionResult=pack(premises,(omega,mc,mt,pw,pq,family)=>{
   const z=20,bh=hyp(A(empty(z),nat(z)));
   const initial=mp(nest(right(bh),left(bh),mc,pw,pq,family),inst(baseAll,1,z));
   assert(initial.f===exactCover(z),'strong singleton base target');
   const baseProof=generalize(z,abs(bh,initial));
   assert(baseProof.f===induction.base,'endpoint coverage base');

   const x=21,y=22,sh=hyp(and([nat(x),nat(y),succ(x,y),exactCover(x)]));
   const [mx,my,sy,cov]=unpack(sh,4);
   const next=witness(cov,80,hg=>{
     const [inFamily,oldDomain,oldValue]=unpack(hg,3);
     const properties=mp(inFamily,left(ui(family,80)));
     const bounded=left(properties),good=right(properties);
     return witness(oldValue,81,ha=>{
       const ma=left(ha),app=right(ha);
       const multiplication=mp(conj(my,ma),inst(left(mt),y,81));
       return witness(multiplication,82,hb=>{
         const mb=left(hb),product=move(right(hb),mul(y,81,82));
         const extended=mp(nest(omega,mx,my,sy,ma,app,mb,product,pw,pq,bounded,good,oldDomain),inst(extensionAll,1,y,82,80,x,81));
         return witness(extended,84,hu=>{
           const [newBound,newGood,newDomain,relation]=unpack(hu,4);
           const member=mp(conj(newBound,newGood),right(ui(family,84)));
           const relAt=inst(relation,y,82);
           const newValue=mp(orRight(at(80,y,82),conj(refl(y),refl(82))),right(relAt));
           const valueExists=exIntro(X(47,A(nat(47),at(84,y,47))),82,conj(mb,newValue));
           return exIntro(exactCover(y),84,nest(member,newDomain,valueExists))
         })
       })
     })
   });
   const stepProof=allP([x,y],abs(sh,next));
   assert(stepProof.f===induction.step,'endpoint coverage step');
   const goal=apply(induction.result,omega,baseProof,stepProof);
   assert(goal.f===induction.goal,'endpoint coverage induction goal');
   return goal
 });
 assert(inductionResult.deps.size===0,'endpoint coverage assumptions escaped');

 const result=ui(generalize(1,inductionResult),37);
 const source=makePrefixPredicates(ctx,raw,{W:37});
 const sourcePremises=[source.omega,source.nat(source.C0),source.mt,source.power(37,P),source.power(P,Q),source.famSpec(Q,K)];
 const sourceExactCover=n=>X(46,A(M(46,K),A(source.domain(46,n),X(47,A(source.nat(47),at(46,n,47))))));
 const goal=gen(27,ar.imp(source.nat(27),sourceExactCover(27)));
 assert(ns[result.f].x===and(sourcePremises)&&ns[result.f].y===goal,'source endpoint coverage target');
 const quantified=allP([37,50,51,53],result);
 function covered(proofs,n,natProof){return mp(natProof,ui(mp(nest(...proofs),result),n))}
 function run(){
   const out=ctx.get('bounded_good_prefix_family_endpoint_coverage',result);
   Object.assign(out.receipt,{exact_endpoint_domain_covered:true,base_constructed_by_singleton:true,successor_constructed_by_good_extension:true,multiplication_premise:'exact_frozen_clause_6',actual_rh_proof:false});
   return [out]
 }
 return {ctx,defs:source,inductionDefs:defs,result,inductionResult,quantified,premises:sourcePremises,exactCover:sourceExactCover,goal,covered,run,good_source:kernel.encode(ar.ast(source.good(0))),family_source:kernel.encode(ar.ast(source.famSpec(Q,K))),good_instances:[{graph:0,omega:37}]};
}
export const prefixTotal={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/prefix_total.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(prefixTotal.prepare(raw).run().map(x=>x.receipt),null,2));
}

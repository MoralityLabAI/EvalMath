// RH-PL-15: overlap agreement of exact finite Good prefixes.
import {ordinals} from './ordinals.mjs';
import {makePrefixPredicates} from './prefix_predicates.mjs';
import {kernel} from './kernel.mjs';

function buildPrefixOverlap(ord,k){
 function prepare(raw,context=null){
 const ctx=context??ord.prepare(raw),{p,t,ar,ns,pack,witness,allP,all,chain,and,orRight}=ctx;
 const {apply,inst,nest,move,symmetric,trans,replace,empty,succ}=t;
 const {imp,gen,neg}=ar;
 const {E,M,A,sub,split,qAt,hyp,mp,generalize,abs,left,right,conj,ui,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const defs=makePrefixPredicates(ctx,raw,{W:1}),{nat,at,mul,dom,good,mt}=defs;
 const G=60,H=61,aa=70,bb=71,mark=99;
 function unpack(h,count){const out=[];for(let i=1;i<count;i++){out.push(left(h));h=right(h)}out.push(h);return out}
 const mulFunctional=split(mt)[1];
 const phi=all([aa,bb],imp(and([nat(aa),nat(bb),at(G,0,aa),at(H,0,bb)]),E(aa,bb)));
 const induction=p.prove(phi),P=n=>sub(phi,0,n);
 const premises=[p.omegaW,mulFunctional,good(G),good(H)];

 // A successor index in a prefix forces its predecessor into the
 // domain. Transitivity of the endpoint is obtained from Omega.
 function predecessorDomain(omega,domain,graph,x,y,mx,my,sy,v,mv,app,endpoint){
   return witness(domain,endpoint,hd=>{
     const lastNat=left(hd),exact=right(hd);
     const value=exIntro(dom(graph,y),v,conj(mv,app));
     const order=mp(value,left(mp(my,ui(exact,y))));
     const below=ctx.down(omega,endpoint,lastNat,x,y,sy,order);
     return mp(orRight(E(x,endpoint),below),right(mp(mx,ui(exact,x))))
   })
 }
 function outputs(n){
   const target=ns[qAt(qAt(P(n),aa),bb)],h=hyp(target.x);
   const [ma,mb,ga,hb]=unpack(h,4);
   return {ma,mb,ga,hb,finish:q=>allP([aa,bb],abs(h,q))}
 }
 function multiplicationEquality(functional,x,y,u,v,mx,my,mu,mv,gu,gv){
   const implication=mp(nest(mx,my,mu,mv),inst(functional,x,y,u,v));
   const [l,r]=split(ns[implication.f].x);
   return mp(conj(move(gu,l),move(gv,r)),implication)
 }

 const result=pack(premises,(omega,mf,gg,hh)=>{
   const [gd,gf,gb,gs]=unpack(gg,4),[hd,hf,hb,hs]=unpack(hh,4);
   // Empty inputs in both prefixes have the same designated value.
   const z=20,bh=hyp(A(empty(z),nat(z))),ob=outputs(z);
   const ga=apply(inst(gb,z,aa),left(bh),right(bh),ob.ma,ob.ga);
   const ha=apply(inst(hb,z,bb),left(bh),right(bh),ob.mb,ob.hb);
   const baseProof=generalize(z,abs(bh,ob.finish(trans(ga,symmetric(ha)))));
   assert(baseProof.f===induction.base,'prefix overlap base');

   const x=21,y=22,sh=hyp(and([nat(x),nat(y),succ(x,y),P(x)]));
   const [mx,my,sy,prev]=unpack(sh,4),oy=outputs(y);
   const dg=predecessorDomain(omega,gd,G,x,y,mx,my,sy,aa,oy.ma,oy.ga,80);
   const dh=predecessorDomain(omega,hd,H,x,y,mx,my,sy,bb,oy.mb,oy.hb,81);
   const stepEquality=witness(dg,82,gv=>witness(dh,83,hv=>{
     const mg=left(gv),mh=left(hv),ag=right(gv),ah=right(hv);
     const same=mp(nest(mg,mh,ag,ah),inst(prev,82,83));
     const pg=apply(inst(gs,x,y,82,aa),mx,my,mg,oy.ma,sy,ag,oy.ga);
     const ph=apply(inst(hs,x,y,83,bb),mx,my,mh,oy.mb,sy,ah,oy.hb);
     const phSame=replace(ph,symmetric(same),mul(y,mark,bb),mark);
     return multiplicationEquality(mf,y,82,aa,bb,my,mg,oy.ma,oy.mb,pg,phSame)
   }));
   const stepProof=allP([x,y],abs(sh,oy.finish(stepEquality)));
   assert(stepProof.f===induction.step,'prefix overlap step');
   const conclusion=apply(induction.result,omega,baseProof,stepProof);
   assert(conclusion.f===induction.goal,'prefix overlap conclusion');
   return conclusion
 });
 assert(result.deps.size===0,'prefix overlap assumptions escaped');
 const quantified=allP([1,G,H],result);

 // Project Good from membership in the literal bounded family and
 // obtain the compatibility interface used by union gluing.
 const source=makePrefixPredicates(ctx,raw,{W:37}),Q=51,K=53;
 const family=source.famSpec(Q,K),sourceMulFunctional=split(source.mt)[1];
 const inFamily=g=>M(g,K),[i,a,b]=[72,73,74];
 const compat=all([G,H,i,a,b],chain([inFamily(G),inFamily(H),source.nat(i),source.nat(a),source.nat(b),at(G,i,a),at(H,i,b)],E(a,b)));
 const familyPremises=[source.omega,sourceMulFunctional,family];
 const familyResult=pack(familyPremises,(omega,mf,fam)=>{
   const hyps=[inFamily(G),inFamily(H),source.nat(i),source.nat(a),source.nat(b),at(G,i,a),at(H,i,b)].map(hyp);
   const [mg,mh,mi,ma,mb,ga,hb]=hyps;
   const gg=right(mp(mg,left(ui(fam,G)))),hh=right(mp(mh,left(ui(fam,H))));
   const agreement=mp(nest(omega,mf,gg,hh),inst(quantified,37,G,H));
   const atIndex=mp(mi,ui(agreement,i));
   const eq=mp(nest(ma,mb,ga,hb),inst(atIndex,a,b));
   return allP([G,H,i,a,b],hyps.reduceRight((q,h)=>abs(h,q),eq))
 });
 assert(ns[familyResult.f].y===compat,'literal family compatibility');

 function run(){
   const rows=[ctx.get('good_prefix_overlap_agreement',result),ctx.get('bounded_good_prefix_family_compatibility',familyResult)];
   for(const row of rows)Object.assign(row.receipt,{ordinal_facts_derived_from_omega:true,multiplication_premise:'exact_functionality_half_of_frozen_clause_6',prefix_base_discharged:true,prefix_overlap_step_discharged:true,actual_rh_proof:false});
   return rows
 }
 return {ctx,defs,source,result,quantified,agreement:induction.goal,premises,familyResult,familyPremises,compat,predecessorDomain,run,good_source:k.encode(ar.ast(source.good(0))),family_source:k.encode(ar.ast(family))};
 }
 return {prepare};
}
export const prefixOverlap=buildPrefixOverlap(ordinals,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/prefix_overlap.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(prefixOverlap.prepare(raw).run().map(x=>x.receipt),null,2));
}

// RH-PL-15: discharge every prefix-family construction condition in the
// normalized denominator-recursion theorem. Multiplication remains an
// arbitrary total functional natural operation in the exact frozen encoding.
import {ordinals} from './ordinals.mjs';
import {prefixTotal} from './prefix_total.mjs';
import {prefixOverlap} from './prefix_overlap.mjs';
import {prefixFamily} from './prefix_family.mjs';
import {recursionExistence} from './recursion_existence.mjs';
import {makePrefixPredicates} from './prefix_predicates.mjs';
import {kernel} from './kernel.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??ordinals.prepare(raw),{p,t,ar,ns,pack,witness,allP,and,orRight}=ctx;
 const {apply,inst,nest,move,empty,succ}=t,{gen}=ar;
 const {E,M,A,X,split,exAt,hyp,mp,generalize,abs,left,right,conj,ui,exIntro,sub}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const d=makePrefixPredicates(ctx,raw,{W:1}),{nat,at,mul,domain}=d;
 const total=prefixTotal.prepare(raw,ctx),overlap=prefixOverlap.prepare(raw,ctx);
 const recursion=recursionExistence.prepare(raw,ctx),gl=recursion.ctx;
 const familyExistence=prefixFamily.prepare(raw,ctx);
 const P=50,Q=51,K=4,C0=6;
 const family=d.famSpec(Q,K);
 const totalFor=inst(allP([1,53],total.inductionResult),1,K);
 const compatibleFor=inst(allP([37,53],overlap.familyResult),1,K);
 const premises=[p.omegaW,nat(C0),d.mt,d.power(1,P),d.power(P,Q),family];

 const withFamily=pack(premises,(omega,mc,mt,pw,pq,fam)=>{
   const covered=mp(nest(omega,mc,mt,pw,pq,fam),totalFor);
   function cover(n,mn){
     return witness(mp(mn,ui(covered,n)),80,hg=>{
       return exIntro(gl.cover(n),80,conj(left(hg),right(right(hg))))
     });
   }
   const hb=hyp(A(empty(20),nat(20)));
   const base=generalize(20,abs(hb,cover(20,right(hb))));
   assert(base.f===gl.base,'covered zero interface');
   const compat=move(mp(nest(omega,right(mt),fam),compatibleFor),gl.compat);

   // The family's exact Good predicate supplies the common base equation.
   // Fresh names avoid the value binders 41--44 inside literal Good.
   const [g,bx,a]=[85,86,87];
   const bh=[M(g,K),empty(bx),nat(bx),nat(a),at(g,bx,a)].map(hyp);
   const good=right(mp(bh[0],left(ui(fam,g))));
   const gb=left(right(right(good)));
   const val=apply(inst(gb,bx,a),...bh.slice(1));
   const bLocal=move(allP([g,bx,a],bh.reduceRight((r,h)=>abs(h,r),val)),recursion.bLocal);
   assert(bLocal.f===recursion.bLocal,'family base interface');

   // Choose a prefix whose endpoint is y. The given successor x belongs
   // to y, so the exact domain supplies both values in one Good prefix.
   // This discharges the old extension premise even when its cover(x)
   // hypothesis came from an unrelated, longer prefix.
   const x=40,y=49,eh=[nat(x),nat(y),succ(x,y),gl.cover(x)].map(hyp);
   const [mx,my,sy]=eh;
   const loc=witness(mp(my,ui(covered,y)),80,hg=>{
     const inFamily=left(hg),exact=left(right(hg)),endpoint=right(right(hg));
     const good=right(mp(inFamily,left(ui(fam,80)))),step=right(right(right(good)));
     const xy=ctx.successorMember(sy,x);
     const dx=mp(orRight(E(x,y),xy),right(mp(mx,ui(exact,x))));
     return witness(endpoint,81,hy=>witness(dx,82,hx=>{
       const ma=left(hx),mb=left(hy),ax=right(hx),ay=right(hy);
       const product=apply(inst(step,x,y,82,81),mx,my,ma,mb,sy,ax,ay);
       const goal=recursion.localWitness(x,y),aExists=split(exAt(goal,80))[1];
       const bExists=split(exAt(aExists,82))[1];
       const bProof=exIntro(bExists,81,nest(mb,ax,ay,product));
       const aProof=exIntro(aExists,82,conj(ma,bProof));
       return exIntro(goal,80,conj(inFamily,aProof));
     }));
   });
   const ext=allP([x,y],eh.reduceRight((r,h)=>abs(h,r),loc));
   assert(ext.f===recursion.ext,'family local extension interface');
   return mp(nest(omega,base,compat,bLocal,ext),recursion.result);
 });
 assert(ns[withFamily.f].y===recursion.goal,'normalized family recursion goal');

 // Power and Separation construct the family. Eliminate all three set
 // witnesses, leaving only Omega, the initial natural value, and the
 // exact total/functionality clause of the chosen multiplication graph.
 const familyEx=ui(generalize(37,familyExistence.result),1);
 const corePremises=[p.omegaW,nat(C0),d.mt];
 const result=pack(corePremises,(omega,mc,mt)=>{
   return witness(familyEx,P,hp=>witness(hp,Q,hq=>witness(hq,K,hf=>{
     const pw=left(hf),pq=left(right(hf)),fam=right(right(hf));
     return mp(nest(omega,mc,mt,pw,pq,fam),withFamily);
   })));
 });
 assert(ns[result.f].y===recursion.goal&&result.deps.size===0,'closed prefix recursion construction');
 const source=makePrefixPredicates(ctx,raw,{W:37});
 const sourceResult=ui(generalize(1,result),37),sourceGoal=sub(recursion.goal,1,37);
 const sourcePremises=[source.omega,source.nat(C0),source.mt];
 assert(ns[sourceResult.f].x===and(sourcePremises)&&ns[sourceResult.f].y===sourceGoal,'source normalized recurrence target');
 function run(){
   const row=ctx.get('normalized_denominator_recursion_from_omega_and_multiplication',sourceResult);
   Object.assign(row.receipt,{family_construction_discharged:true,base_coverage_discharged:true,
     family_compatibility_discharged:true,local_extension_discharged:true,
     remaining_premises:['exact_least_inductive_omega','natural_initial_value','exact_total_functional_multiplication_clause_6'],
     normalized_recurrence:true,exact_clause_21_bridge:false,actual_rh_proof:false});
   return [row];
 }
 return {ctx,result:sourceResult,inductionResult:result,withFamily,premises:sourcePremises,goal:sourceGoal,run,
   normalized_goal:kernel.encode(ar.ast(sourceGoal)),omega_variable:37,
   good_source:kernel.encode(ar.ast(source.good(0))),family_source:kernel.encode(ar.ast(source.famSpec(51,53)))};
}
export const prefixRecursion={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/prefix_recursion.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(prefixRecursion.prepare(raw).run().map(x=>x.receipt),null,2));
}

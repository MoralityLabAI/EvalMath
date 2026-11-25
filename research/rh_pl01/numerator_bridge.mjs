// RH-PL-17: reconstruct frozen numerator clauses 13, 18 and 20 from
// normalized graph properties and the exact denominator totality clause.
import {pairs} from './pairs.mjs';
import {makeNumeratorPredicates} from './numerator_predicates.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??pairs.prepare(raw),{p,t,ar,ns,pack,witness,allP,and,refl}=ctx;
 const {apply,inst,nest,move,empty,succ}=t;
 const {E,split,qAt,exAt,hyp,mp,generalize,abs,left,right,conj,ui,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const d=makeNumeratorPredicates(ctx,raw),{Z,G,B,nat,at,total,functional,base,update,normalized,exact,clause}=d;
 const [exactTotal,exactBase,exactUpdate]=[clause(13),clause(18),clause(20)],denTotal=clause(14);

 const totalPremises=[total(G),functional(G)];
 const totalResult=pack(totalPremises,(tot,fun)=>{
   const [tgtTotal,tgtFun]=split(exactTotal),[x,a,b]=[71,72,73];
   const body=d.qform(tgtFun,x,a,b),hNat=hyp(ns[body].x),hApp=hyp(ns[ns[body].y].x);
   const mx=left(hNat),ma=left(right(hNat)),mb=right(right(hNat));
   const ga=move(left(hApp),at(G,x,a)),gb=move(right(hApp),at(G,x,b));
   const eq=apply(inst(fun,x,a,b),mx,ma,mb,ga,gb);
   const funProof=move(allP([x,a,b],abs(hNat,abs(hApp,eq))),tgtFun);
   return conj(move(tot,tgtTotal),funProof)
 });
 assert(ns[totalResult.f].y===exactTotal,'exact numerator totality');

 const basePremises=[nat(Z),empty(Z),total(G),base(G)];
 const baseResult=pack(basePremises,(mz,ez,tot,bs)=>{
   return witness(mp(mz,ui(tot,Z)),71,hv=>{
     const mv=left(hv),app=right(hv),eq=apply(inst(bs,Z,71),ez,mz,mv,app);
     const [,tail]=split(exAt(exactBase,71)),[tgtApp,tgtEq]=split(tail);
     assert(eq.f===tgtEq,'exact numerator initial equality');
     return exIntro(exactBase,71,nest(mv,move(app,tgtApp),eq))
   })
 });
 assert(ns[baseResult.f].y===exactBase,'exact numerator base');

 // The normalized update already supplies a natural product witness
 // together with the sum relation. The forward bridge therefore needs
 // no additional arithmetic totality assumption.
 const updatePremises=[d.omega,total(G),denTotal,update(G,B)];
 const updateResult=pack(updatePremises,(omega,tot,dt,step)=>{
   const [x,y,a,b,den,c]=[71,72,73,74,75,76],mx=hyp(nat(x));
   const target=ns[qAt(exactUpdate,x)].y;
   const next=mp(mx,ui(right(left(omega)),x));
   const out=witness(next,y,hy=>{
     const my=left(hy),sy=move(right(hy),succ(x,y));
     return witness(mp(mx,ui(tot,x)),a,ha=>witness(mp(my,ui(tot,y)),b,hb=>witness(mp(mx,ui(left(dt),x)),den,hd=>{
       const ma=left(ha),mb=left(hb),md=left(hd),gx=right(ha),gy=right(hb),dx=move(right(hd),at(B,x,den));
       const operation=apply(inst(step,x,y,a,b,den),mx,my,ma,mb,md,sy,gx,gy,dx);
       return witness(operation,c,hc=>{
         const mc=left(hc),product=left(right(hc)),sum=right(right(hc));
         // Instantiate the seven exact natural witnesses in the frozen
         // nesting order: successor, new value, successor, old value,
         // product, denominator value, sum value.
         const [,kTail]=split(exAt(target,y)),[sk,aExists]=split(kTail);
         const [,aTail]=split(exAt(aExists,b)),[appY,lExists]=split(aTail);
         const [,lTail]=split(exAt(lExists,y)),[sl,bExists]=split(lTail);
         const [,bTail]=split(exAt(bExists,a)),[appX,cExists]=split(bTail);
         const [,cTail]=split(exAt(cExists,c)),[prod,dExists]=split(cTail);
         const [,dTail]=split(exAt(dExists,den)),[appD,eExists]=split(dTail);
         const [,eTail]=split(exAt(eExists,b)),[plus,equal]=split(eTail);
         assert(equal===E(b,b),'same numerator/sum witness');
         const eProof=exIntro(eExists,b,nest(mb,move(sum,plus),refl(b)));
         const dProof=exIntro(dExists,den,nest(md,move(dx,appD),eProof));
         const cProof=exIntro(cExists,c,nest(mc,move(product,prod),dProof));
         const bProof=exIntro(bExists,a,nest(ma,move(gx,appX),cProof));
         const lProof=exIntro(lExists,y,nest(my,move(sy,sl),bProof));
         const aProof=exIntro(aExists,b,nest(mb,move(gy,appY),lProof));
         return exIntro(target,y,nest(my,move(sy,sk),aProof))
       })
     })))
   });
   return move(generalize(x,abs(mx,out)),exactUpdate)
 });
 assert(ns[updateResult.f].y===exactUpdate,'exact numerator recurrence');

 const premises=[d.omega,nat(Z),empty(Z),denTotal,normalized(G,B)];
 const result=pack(premises,(omega,mz,ez,dt,norm)=>{
   const tot=left(norm),fn=left(right(norm)),bs=left(right(right(norm))),st=right(right(right(norm)));
   return nest(mp(nest(tot,fn),totalResult),mp(nest(mz,ez,tot,bs),baseResult),mp(nest(omega,tot,dt,st),updateResult))
 });
 const goal=exact(G,B);
 assert(ns[result.f].x===and(premises)&&ns[result.f].y===goal,'aggregate exact numerator bridge');
 // Instantiate all free parameters together in the original frozen slots.
 // Multiplication's new slot 8 is consumed before denominator slot 8 is
 // introduced, and addition's new slot 7 before numerator slot 7.
 const sourcePredicates=makeNumeratorPredicates(ctx,raw,{W:0,Z:1,C0:2,ADD:3,MUL:4,G:7,B:8});
 const sourceResult=inst(allP([37,60,7,8,62,61],result),0,1,3,4,7,8);
 const sourcePremises=[sourcePredicates.omega,sourcePredicates.nat(1),empty(1),sourcePredicates.clause(14),sourcePredicates.normalized(7,8)];
 const sourceGoal=sourcePredicates.exact(7,8);
 assert(ns[sourceResult.f].x===and(sourcePremises)&&ns[sourceResult.f].y===sourceGoal,'original-slot numerator bridge');
 const components=[
   {name:'normalized_numerator_totality_to_exact_clause_13',result:totalResult,premises:totalPremises,goal:exactTotal,source_clauses:[13]},
   {name:'normalized_numerator_base_to_exact_clause_18',result:baseResult,premises:basePremises,goal:exactBase,source_clauses:[18]},
   {name:'normalized_numerator_update_to_exact_clause_20',result:updateResult,premises:updatePremises,goal:exactUpdate,source_clauses:[20]}
 ];
 function run(cap=48000000){
   return [...components,{name:'normalized_numerator_to_exact_frozen_clauses',result,premises,goal,source_clauses:[13,18,20]},
     {name:'normalized_numerator_to_original_frozen_slots',result:sourceResult,premises:sourcePremises,goal:sourceGoal,source_clauses:[13,18,20],slots:sourcePredicates.slots}].map(c=>{
     const row=ctx.get(c.name,c.result,cap);
     Object.assign(row.receipt,{source_clauses:c.source_clauses,source_slot_mapping:c.slots||d.slots,exact_frozen_consequent:true,normalized_update_supplies_operation_witness:true,denominator_totality_is_explicit:c.source_clauses.includes(20),joint_recurrence_existence:false,actual_rh_proof:false});
     return row
   })
 }
 return {ctx,predicates:d,result,premises,goal,clauses:d.clauses,sourceClauses:d.sourceClauses,slots:d.slots,normalized,exact,components,sourcePredicates,sourceResult,sourcePremises,sourceGoal,run};
}
export const numeratorBridge={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/numerator_bridge.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(numeratorBridge.prepare(raw).run().map(x=>x.receipt),null,2));
}
